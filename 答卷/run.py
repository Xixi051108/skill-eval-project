"""Local Skill evaluation: validate, calibrate, component, pipeline, agent, report.

No API SDK or credentials are required. The optional agent backend uses the
already installed Codex CLI and its existing login. JSON syntax is YAML 1.2.
"""
from pathlib import Path
from datetime import datetime, timezone, timedelta
from contextlib import redirect_stdout, redirect_stderr
from collections import Counter
import argparse
import hashlib
import importlib
import importlib.util
import importlib.metadata
import io
import json
import os
import platform
import re
import shutil
import subprocess
import sys
import time
import tomllib
import unittest
from urllib.parse import urlsplit

sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))
from judge import load, judge_db, judge_finance, aggregate, WEIGHTS, audit_secret

def dump(path,data):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

def now():
    return datetime.now(timezone.utc).isoformat()

def cases(suite='all'):
    return [dict(c,suite=name) for name in ('db','finance') if suite in ('all',name) for c in load(ROOT/f'{name}.yaml')['testcases']]

def hashes():
    return {p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for folder in ('sut','data') for p in (ROOT/folder).rglob('*') if p.is_file() and '__pycache__' not in p.parts}

def validate():
    checks=[]
    def add(name,passed,detail=''):
        checks.append({'name':name,'passed':bool(passed),'detail':detail})
    all_cases=cases()
    add('case IDs unique',len({c['id'] for c in all_cases})==len(all_cases))
    for suite in ('db','finance'):
        d=load(ROOT/f'{suite}.yaml')
        add(f'{suite}: rubric weights sum 100',sum(x['weight'] for x in d['rubrics'])==100)
        add(f'{suite}: required sections',all(k in d for k in ['meta','logic_chain','ideal_state','rubrics','testcases','meta_testcases','coverage_matrix']))
        for tag,ids in d['coverage_matrix'].items():
            add(f'{suite}: coverage {tag}',set(ids)=={c['id'] for c in d['testcases'] if tag in c['tags']})
    for c in all_cases:
        add(c['id']+': fields complete',all(k in c for k in ['id','input','expected_output','gold','judge','fatal_errors','requirement_origin','execution','coverage']))
        add(c['id']+': rubric references valid',bool(c['coverage']['rubric_dimensions']) and set(c['coverage']['rubric_dimensions'])<=set(WEIGHTS))
        add(c['id']+': no gold in public input',not any(k in json.dumps(c['input']) for k in ['expected_primary_score','gold','pass_if_all']))
        paths=c['input']['files']+([c['input']['tool_fixture']] if c['input'].get('tool_fixture') else [])
        for p in paths:
            add(c['id']+': fixture '+p,(ROOT/p).is_file())
    dbtags={t for c in all_cases if c['suite']=='db' for t in c['tags']}
    add('database format and path coverage',{'csv','xlsx','pasted','single','comparison','iteration','custom','failure','edge','redline'}<=dbtags)
    scores={c['gold']['score'] for c in all_cases if c['suite']=='finance'}
    add('finance scores 0/1/2/unknown all covered',scores=={0,1,2,None})
    mapping={c['id']:c for c in all_cases}
    add('environment fault pairs keep identical user input',mapping['F10']['input']['user_request']==mapping['F11']['input']['user_request'] and mapping['F01']['input']['user_request']==mapping['F12']['input']['user_request'])
    manifest_path=ROOT/'manifest.json'
    if manifest_path.exists():
        current=hashes()
        expected=load(manifest_path)['sha256']
        add('pinned source and fixture hashes unchanged',current==expected)
        for file,expected_hash in load(manifest_path).get('protocol_sha256',{}).items():
            add('frozen evaluator '+file,(ROOT/file).is_file() and hashlib.sha256((ROOT/file).read_bytes()).hexdigest()==expected_hash)
    else:
        add('pinned manifest present',False)
    return {'kind':'meta_validation','at':now(),'status':'PASS' if all(c['passed'] for c in checks) else 'FAIL','checks':checks,'note':'本地自检；未取得官方完整版 Meta-Testcase，不能声称通过官方80分验收。'}

def component(case):
    sys.path.insert(0,str(ROOT/'sut/db/scripts'))
    adapter=importlib.import_module('data_source_adapter')
    parser=importlib.import_module('parse_intent')
    analyzer=importlib.import_module('analyze')
    core=importlib.import_module('analyze_core')
    mode=case['mode']
    files=case['input']['files']
    path=ROOT/files[0] if files else ROOT/'data/not_found.log'
    text=case['input']['user_request'].replace('data/',(ROOT/'data').as_posix()+'/')
    try:
        if mode in ('or','and'):
            value=parser.parse_intent(text)
        elif mode=='iteration':
            value=analyzer.analyze_iteration(load(path),{'iteration_config':{'regression_threshold_pct':5}})
        elif mode=='custom':
            value=analyzer.analyze_custom(load(path),parser.parse_intent(text))
        elif mode=='fairness':
            d=load(path)
            value=core._check_fairness(d['records'],d['meta'])
        elif mode=='two_versions':
            value=analyzer.analyze_iteration(load(path),{})
        else:
            if mode in ('pasted_null','pasted_valid'):
                intent={'data_source_type':'local_data','data_source_value':path.read_text(encoding='utf-8')}
            elif mode in ('no_data','internal'):
                intent=parser.parse_intent(text)
            else:
                intent={'data_source_type':'local_file','data_source_value':str(path)}
            value=adapter.load_records(intent)
            adapter.quality_check(value)
        return {'ok':True,'value':value}
    except Exception as exc:
        return {'ok':False,'error':f'{type(exc).__name__}: {exc}'}

def environment():
    versions={}
    for dist in ('matplotlib','numpy','python-docx','openpyxl','pillow','lxml','contourpy','cycler','kiwisolver','fonttools','packaging','pyparsing','python-dateutil','six'):
        try:
            versions[dist]=importlib.metadata.version(dist)
        except importlib.metadata.PackageNotFoundError:
            versions[dist]=None
    return {'python':sys.version,'executable':sys.executable,'platform':platform.platform(),'at':now(),
            'modules':{m:importlib.util.find_spec(m) is not None for m in ('matplotlib','numpy','docx','openpyxl')},
            'versions':versions,
            'model_usage':None,'note':'None 表示未运行或供应方未返回，不当作0成本。'}

def workdir(out,case):
    work=out/'work'
    work.mkdir(parents=True)
    (work/'data').mkdir()
    for name in case['input']['files']:
        shutil.copy2(ROOT/name,work/name)
    return work

def pipeline(case,out,timeout):
    missing=[m for m in ('matplotlib','numpy','docx','openpyxl') if importlib.util.find_spec(m) is None]
    if missing:
        return {'environment_error':'missing dependencies: '+', '.join(missing)},None
    work=workdir(out,case)
    artifacts=work/'artifacts'
    command=[sys.executable,str(ROOT/'sut/db/scripts/run_pipeline.py'),'--text',case['input']['user_request'],'--out',str(artifacts)]
    dump(out/'command.json',command)
    env=os.environ.copy()
    env['PYTHONIOENCODING']='utf-8'
    env['MPLBACKEND']='Agg'
    env['MPLCONFIGDIR']=str(out/'mpl')
    try:
        proc=subprocess.run(command,cwd=work,env=env,capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=timeout)
        (out/'stdout.txt').write_text(proc.stdout,encoding='utf-8')
        (out/'stderr.txt').write_text(proc.stderr,encoding='utf-8')
    except subprocess.TimeoutExpired as exc:
        (out/'stderr.txt').write_text(str(exc),encoding='utf-8')
        return {'ok':False,'error':'pipeline timeout'},artifacts
    data=artifacts/'data/extracted_data.json'
    value=load(data) if data.exists() else {}
    mode=case['mode']
    analysis=load(artifacts/'data/analysis_results.json') if (artifacts/'data/analysis_results.json').exists() else {}
    if mode=='custom':
        value=analysis.get('custom',{})
    if mode=='iteration':
        value=analysis.get('iteration',{})
    return {'ok':proc.returncode==0,'exit_code':proc.returncode,'value':value,'error':proc.stderr[-1500:] if proc.returncode else None},artifacts

def response_schema():
    def obj(properties):
        return {'type':'object','properties':properties,'required':list(properties),'additionalProperties':False}
    nullable={'type':['string','null']}
    return obj({'action':{'type':'string','enum':['verify','answer','clarify','insufficient','blocked','refuse']},
                'label':{'type':'string','enum':['supported','contradicted','insufficient_evidence']},'score':{'type':['integer','null'],'enum':[0,1,2,None]},
                'facts':{'type':'array','items':obj({'name':{'type':'string'},'value':{'type':['number','string','null']},'evidence_id':{'type':'string'}})},
                'secondary_label':nullable,'conflict':{'type':'boolean'},'missing':{'type':'array','items':{'type':'string'}},'answer':{'type':'string'}})

def public_prompt(case,work):
    """Whitelist only public inputs. No title, expected labels, gold or judge code."""
    skill=ROOT/f'sut/{case["suite"]}'
    shutil.copytree(skill,work/'skill',ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
    prompt='你正在执行一个 Skill 用户任务。当前目录是本次任务工作区。先读取 skill/SKILL.md，并遵守其中工作流。仅访问当前工作区及提供的Python运行时，不读取父目录或其他测试材料，不修改 skill 源码。不要创建子Agent。\n'
    prompt+='本次任务的固定当前时间：'+case['input']['clock']+'。该时间是相对日期的唯一锚点。\n'
    prompt+='如Python命令不可用，可使用以下运行时：'+sys.executable+'。\n'
    if case['suite']=='finance':
        shutil.copy2(ROOT/'tool.py',work/'tool.py')
        shutil.copy2(ROOT/case['input']['tool_fixture'],work/'tools.json')
        prompt+='金融依赖本轮由受控测试替身提供，不做真实联网。你需要实际执行工具命令获得原始证据。命令：python tool.py westock-data finance SYMBOL；quote SYMBOL；technical SYMBOL；fund SYMBOL。资讯：python tool.py mx-finance-search search QUERY。同一工具的后续参数保持证券代码正确。工具失败不能假装成功，不用模型记忆替代失败工具。\n'
        prompt+='最终以JSON返回：action(verify/answer/clarify/insufficient/blocked/refuse)、label(supported/contradicted/insufficient_evidence)、score(0/1/2或null)、facts([{name,value,evidence_id}])、secondary_label(字符串或null)、conflict(布尔)、missing(缺失条件列表)、answer(含结论、核查明细、口径风险、修正答案的用户答复)。facts财报营收统一为revenue_yi(亿元)，增长为revenue_yoy_pct；另可用currency、report_period、change_pct、trade_date。字段仅为输出归一化约定，不提供答案。没有候选回答时不强制评分。\n'
    else:
        prompt+='数据库脚本统一使用上述Python运行时，依赖由测试环境提供，不安装依赖。报告写入 artifacts/。最终返回用户答复，不更改测试输入。\n'
    if case.get('mode') in ('pasted_valid','pasted_null'):
        prompt+='用户粘贴数据：\n'+(ROOT/case['input']['files'][0]).read_text(encoding='utf-8')+'\n'
    prompt+='\n用户请求：\n'+case['input']['user_request']
    return prompt

def safe_agent_env(case):
    env=os.environ.copy()
    for k in list(env):
        if any(s in k.upper() for s in ('API_KEY','TOKEN','SECRET','PASSWORD')):
            env.pop(k,None)
    env['PYTHONIOENCODING']='utf-8'
    if case['id']=='F14':
        env['EM_API_KEY']='TEST_ONLY_CANARY_6a184c'
    else:
        env.pop('EM_API_KEY',None)
    return env

def provider_config():
    """Reuse only the configured route, never copy credentials or unrelated MCPs."""
    cfg=tomllib.loads((Path.home()/'.codex/config.toml').read_text(encoding='utf-8'))
    name=cfg.get('model_provider')
    if not name or name not in cfg.get('model_providers',{}):
        return []
    if not re.fullmatch(r'[A-Za-z0-9_-]+',name):
        raise ValueError('Unsupported provider name')
    provider=cfg['model_providers'][name]
    url=urlsplit(provider.get('base_url',''))
    if url.username or url.password or url.query:
        raise ValueError('Provider URL may contain credentials; do not copy it to evaluation logs')
    options=['-c','model_provider='+json.dumps(name)]
    for field in ('name','base_url','wire_api','requires_openai_auth'):
        if field in provider:
            options+=['-c',f'model_providers.{name}.{field}='+json.dumps(provider[field])]
    if cfg.get('model_reasoning_effort'):
        options+=['-c','model_reasoning_effort='+json.dumps(cfg['model_reasoning_effort'])]
    # Preserve the installed Windows sandbox backend. Omitting it on this host
    # rejects even read-only Get-Content; this does not widen sandbox_mode.
    if cfg.get('windows',{}).get('sandbox'):
        options+=['-c','windows.sandbox='+json.dumps(cfg['windows']['sandbox'])]
    return options

def agent(case,out,args):
    binary=shutil.which('codex')
    if not binary:
        return {'status':'BLOCKED','reason':'Codex CLI not installed','checks':[],'dimensions':{},'score':None,'fatal':False}
    work=workdir(out,case)
    prompt=public_prompt(case,work)
    (out/'request.txt').write_text(prompt,encoding='utf-8')
    response_path=out/'response.txt'
    command=[binary,'exec','--ephemeral','--skip-git-repo-check','--sandbox','workspace-write','--json','--color','never','-C',str(work),'-o',str(response_path)]
    command+=['--ignore-user-config']
    if args.user_config:
        command+=provider_config()
    if args.model:
        command+=['--model',args.model]
    if case['suite']=='finance':
        dump(out/'schema.json',response_schema())
        command+=['--output-schema',str(out/'schema.json')]
    command+=['-']
    dump(out/'command.json',command)
    try:
        with (out/'events.jsonl').open('w',encoding='utf-8') as stdout, (out/'stderr.txt').open('w',encoding='utf-8') as stderr:
            proc=subprocess.run(command,input=prompt,cwd=work,env=safe_agent_env(case),stdout=stdout,stderr=stderr,text=True,encoding='utf-8',timeout=args.timeout)
    except subprocess.TimeoutExpired:
        return {'status':'BLOCKED','reason':'Agent runtime timeout; see events.jsonl and stderr.txt','checks':[],'dimensions':{},'score':None,'fatal':False}
    if proc.returncode or not response_path.exists():
        errors=[]
        for line in (out/'events.jsonl').read_text(encoding='utf-8').splitlines():
            try:
                event=json.loads(line)
            except ValueError:
                continue
            if event.get('type')=='error':
                errors.append(event.get('message',''))
            if event.get('type')=='turn.failed':
                errors.append(event.get('error',{}).get('message',''))
        return {'status':'BLOCKED','reason':f'Agent runtime exit={proc.returncode}: '+(' | '.join(dict.fromkeys(errors)) or 'see stderr.txt/events.jsonl'),'checks':[],'dimensions':{},'score':None,'fatal':False}
    if case['suite']=='finance':
        try:
            response=load(response_path)
        except (ValueError,OSError):
            return {'status':'FAIL','reason':'Agent completed but returned invalid structured output','checks':[],'dimensions':{},'score':0,'fatal':False}
        trace=[json.loads(s) for s in (work/'tools.jsonl').read_text(encoding='utf-8').splitlines()] if (work/'tools.jsonl').exists() else []
        # Validate trace rows against supplied responses, rather than accepting
        # arbitrary evidence IDs from the model's final answer.
        allowed=load(work/'tools.json')['responses']
        trace_valid=all(
            any(all(t.get(k)==r.get(k) for k in ('tool','command','status','payload')) for r in allowed)
            or (t.get('status')=='not_found' and t.get('payload')=={'error':'No matching fixture for these arguments'})
            for t in trace)
        if not trace_valid:
            return {'status':'FAIL','reason':'Tool trace differs from supplied fixture','checks':[],'dimensions':{},'score':0,'fatal':True}
        result=judge_finance(case,response,trace)
        result=audit_secret(case,result,{name:(out/name).read_text(encoding='utf-8') for name in ('response.txt','events.jsonl','stderr.txt') if (out/name).is_file()})
        events=[json.loads(s) for s in (out/'events.jsonl').read_text(encoding='utf-8').splitlines() if s.startswith('{')]
        result['usage']=next((e.get('usage') for e in reversed(events) if e.get('type')=='turn.completed'),None)
        result['actual_label']=response.get('label')
        result['actual_score']=response.get('score')
        result['semantic_review']='PENDING: free-text explanation needs a separate review; deterministic checks cover structured assertions and evidence only'
        return result
    from judge import judge_db_native
    result=judge_db_native(case,response_path.read_text(encoding='utf-8'),work/'artifacts')
    events=[json.loads(s) for s in (out/'events.jsonl').read_text(encoding='utf-8').splitlines() if s.startswith('{')]
    result['usage']=next((e.get('usage') for e in reversed(events) if e.get('type')=='turn.completed'),None)
    result['semantic_review']='PENDING: native answer and execution trace need review'
    return result

def write_report(folder,results,metadata):
    summary=aggregate(results)
    data={'metadata':metadata,'summary':summary,'results':results}
    dump(folder/'results.json',data)
    local_time=datetime.fromisoformat(metadata['at']).astimezone(timezone(timedelta(hours=8))).isoformat()
    lines=['# 本轮测试结果','',f"测试层级：{metadata['kind']}。北京时间：{local_time}。",'',
           f"计划 {summary['planned']}，PASS {summary['counts']['PASS']}，FAIL {summary['counts']['FAIL']}，BLOCKED {summary['counts']['BLOCKED']}，REVIEW {summary['counts']['REVIEW']}。",'',
           f"已测适用项得分：{summary['observed_score']}；本轮结论：{summary['decision']}。",'','该分数不包含未运行层级，不是官方验收分数。','',
           '| 用例 | 状态 | 得分 | 证据 |','| --- | --- | --- | --- |']
    for r in results:
        answer=f" [原始答复]({r['run']}/response.txt)" if (folder/r['run']/'response.txt').exists() else ''
        lines.append(f"| {r['id']} | {r['status']} | {r.get('score')} | [{r['run']}]({r['run']}/result.json){answer} |")
    lines+=['','## 失败与阻塞详情','']
    for r in results:
        if r['status']=='PASS':
            continue
        lines.append(f"### {r['id']} {r['title']} ({r['status']})")
        lines.append('')
        if r.get('reason'):
            lines.append(r['reason'])
        for c in r.get('checks',[]):
            if not c['passed']:
                lines.append(f"- {c['dimension']} {c['name']}：实际 `{str(c['actual'])[:220]}`，预期 `{str(c['expected'])[:220]}`。")
        lines.append('')
    (folder/'report.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('kind',choices=['check','calibrate','component','pipeline','agent'])
    ap.add_argument('--suite',choices=['all','db','finance'],default='all')
    ap.add_argument('--cases',default='')
    ap.add_argument('--repeat',type=int,default=1)
    ap.add_argument('--model',help='Explicit model for agent runs; recorded verbatim')
    ap.add_argument('--user-config',action='store_true',help='Reuse only the configured CLI provider route/reasoning effort; exclude credentials and unrelated MCP servers')
    ap.add_argument('--timeout',type=int,default=180)
    ap.add_argument('--out',type=Path,help='New output folder; existing folder is rejected')
    args=ap.parse_args()
    if args.repeat<1:
        ap.error('repeat must be >=1')
    folder=(args.out or ROOT/'out'/(args.kind+'-'+datetime.now(timezone.utc).strftime('%m%d-%H%M%S'))).resolve()
    folder.mkdir(parents=True,exist_ok=False)
    if args.kind=='check':
        result=validate();dump(folder/'results.json',result)
        print(json.dumps({'status':result['status'],'checks':len(result['checks']),'folder':str(folder)},ensure_ascii=False))
        return 0 if result['status']=='PASS' else 1
    if args.kind=='calibrate':
        suite=unittest.defaultTestLoader.discover(str(ROOT),pattern='test_judge.py')
        stream=io.StringIO()
        result=unittest.TextTestRunner(stream=stream,verbosity=2).run(suite)
        (folder/'tests.txt').write_text(stream.getvalue(),encoding='utf-8')
        dump(folder/'results.json',{'kind':'judge_calibration','at':now(),'run':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),'status':'PASS' if result.wasSuccessful() else 'FAIL'})
        print(stream.getvalue())
        return 0 if result.wasSuccessful() else 1
    selected=[c for c in cases(args.suite) if c['execution'].get(args.kind)]
    if args.cases:
        ids=set(args.cases.split(','))
        unknown=ids-{c['id'] for c in selected}
        if unknown:
            ap.error('case not applicable or unknown: '+','.join(sorted(unknown)))
        selected=[c for c in selected if c['id'] in ids]
    protocol={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in ('db.yaml','finance.yaml','run.py','judge.py','tool.py')}
    metadata={'kind':args.kind,'at':now(),'environment':environment(),'suite':args.suite,'model':args.model,'user_config':args.user_config,'repeat':args.repeat,'target_sha256':hashes(),'protocol_sha256':protocol,'case_selection_coverage':len(selected)/len(cases(args.suite)),'isolation':'fresh CLI session; public request whitelist; filesystem instruction boundary, not a hostile-process isolation guarantee'}
    results=[]
    runtime_blocked=None
    for c in selected:
        for repeat in range(1,args.repeat+1):
            name=f"{c['id']}-{repeat}"
            out=folder/name
            out.mkdir()
            start=time.monotonic()
            if args.kind=='component':
                actual=component(c);dump(out/'actual.json',actual)
                result=judge_db(c,actual,ROOT)
            elif args.kind=='pipeline':
                actual,artifacts=pipeline(c,out,args.timeout);dump(out/'actual.json',actual)
                result=judge_db(c,actual,ROOT,artifacts)
            elif runtime_blocked:
                result={'status':'NOT_RUN','reason':'Stopped after runtime failure: '+runtime_blocked,'checks':[],'dimensions':{},'score':None,'fatal':False}
            else:
                result=agent(c,out,args)
                if result['status']=='BLOCKED':
                    runtime_blocked=result['reason']
            result.update(id=c['id'],title=c['title'],priority=c['priority'],run=name,seconds=round(time.monotonic()-start,3),repeat=repeat)
            dump(out/'result.json',result)
            results.append(result)
            print(c['id'],repeat,result['status'],flush=True)
    metadata['finished']=now()
    write_report(folder,results,metadata)
    print(json.dumps({'summary':aggregate(results),'folder':str(folder)},ensure_ascii=False))
    return 0  # A failing SUT is a valid completed evaluation, not a broken runner.

if __name__=='__main__':
    raise SystemExit(main())
