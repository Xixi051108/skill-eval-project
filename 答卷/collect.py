"""Rejudge saved finance outputs under the frozen current protocol.

Reuse only identical public requests, tool fixtures and target Skill bytes.
For repeated matching trials, preserve all observations; the baseline uses the
first eligible trial in the explicitly supplied chronological source order.
Never select the best score or replace a failed baseline with a passing repeat.
"""
from pathlib import Path
from collections import defaultdict
from datetime import datetime,timezone
import argparse
import hashlib
import json
import shutil

from judge import load,judge_finance,audit_secret
from run import ROOT,dump,write_report

def compatible(case,folder):
    request=folder/'request.txt'
    response=folder/'response.txt'
    skill=folder/'work/skill/SKILL.md'
    fixture=folder/'work/tools.json'
    if not all(p.is_file() for p in [request,response,skill,fixture]):
        return False,'missing completed response/request/fixture/skill'
    if not request.read_text(encoding='utf-8').endswith(case['input']['user_request']):
        return False,'user request differs from current version'
    if case['input']['clock'] not in request.read_text(encoding='utf-8'):
        return False,'clock differs from current version'
    result_path=folder/'result.json'
    if not result_path.is_file() or load(result_path)['status'] not in ('PASS','FAIL','REVIEW'):
        return False,'runtime did not complete a scored trial'
    if load(fixture)!=load(ROOT/case['input']['tool_fixture']):
        return False,'tool fixture differs from current version'
    if skill.read_bytes()!=(ROOT/'sut/finance/SKILL.md').read_bytes():
        return False,'target Skill differs'
    return True,''

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--source',type=Path,nargs='+',required=True)
    ap.add_argument('--out',type=Path,required=True)
    ap.add_argument('--cases',default='',help='Optional explicit subset; other IDs are outside this batch')
    args=ap.parse_args()
    models={load(source/'results.json')['metadata'].get('model') for source in args.source}
    if len(models)!=1 or None in models:
        ap.error('Sources must identify one identical model; collect other models separately')
    args.out.mkdir(parents=True,exist_ok=False)
    suite=load(ROOT/'finance.yaml')
    if args.cases:
        ids=set(args.cases.split(','))
        if ids-{c['id'] for c in suite['testcases']}:
            ap.error('Unknown case IDs')
        suite['testcases']=[c for c in suite['testcases'] if c['id'] in ids]
    observations=defaultdict(list)
    excluded=[]
    by_id={c['id']:c for c in suite['testcases']}
    for source in args.source:
        for folder in sorted(source.glob('F*-*')):
            cid=folder.name.split('-')[0]
            if cid not in by_id:
                continue
            valid,reason=compatible(by_id[cid],folder)
            if not valid:
                excluded.append({'source':str(folder),'reason':reason})
                continue
            try:
                response=load(folder/'response.txt')
                trace=[json.loads(s) for s in (folder/'work/tools.jsonl').read_text(encoding='utf-8').splitlines()] if (folder/'work/tools.jsonl').exists() else []
                allowed=load(folder/'work/tools.json')['responses']
                integrity=all(any(all(t.get(k)==r.get(k) for k in ('tool','command','status','payload')) for r in allowed) or (t.get('status')=='not_found' and t.get('payload')=={'error':'No matching fixture for these arguments'}) for t in trace)
                if not integrity:
                    raise ValueError('tool trace mismatch')
                result=judge_finance(by_id[cid],response,trace)
                result=audit_secret(by_id[cid],result,{name:(folder/name).read_text(encoding='utf-8') for name in ('response.txt','events.jsonl','stderr.txt') if (folder/name).is_file()})
            except (ValueError,OSError) as exc:
                excluded.append({'source':str(folder),'reason':'incomplete or invalid output: '+str(exc)})
                continue
            original=load(folder/'result.json')
            result.update(id=cid,title=by_id[cid]['title'],priority=by_id[cid]['priority'],seconds=original.get('seconds'),usage=original.get('usage'),
                          actual_label=response.get('label'),actual_score=response.get('score'),source_run=str(folder.resolve()),semantic_review='PENDING: independent free-text review')
            observations[cid].append((folder,result))
    baseline=[]
    repeats=[]
    for case in suite['testcases']:
        cid=case['id']
        trials=observations[cid]
        if not trials:
            result={'id':cid,'title':case['title'],'priority':case['priority'],'status':'NOT_RUN','reason':'No completed run matches the current public input and fixture','checks':[],'dimensions':{},'score':None,'fatal':False,'run':cid+'-1'}
            (args.out/result['run']).mkdir()
            dump(args.out/result['run']/'result.json',result)
            baseline.append(result)
            continue
        for index,(folder,result) in enumerate(trials,1):
            name=f'{cid}-{index}'
            result.update(run=name,repeat=index)
            shutil.copytree(folder,args.out/name)
            dump(args.out/name/'result.json',result)
            (baseline if index==1 else repeats).append(result)
    metadata={'kind':'finance_rejudged','at':datetime.now(timezone.utc).isoformat(),'case_version':suite['meta']['version'],
              'model':next(iter(models)),
              'evaluator_sha256':hashlib.sha256((ROOT/'judge.py').read_bytes()).hexdigest(),'suite_sha256':hashlib.sha256((ROOT/'finance.yaml').read_bytes()).hexdigest(),
              'source_order':[str(p.resolve()) for p in args.source],'baseline_policy':'first compatible completed trial in source order; never pick the best','note':'本步仅重判保存的真实输出，没有新调用模型。'}
    write_report(args.out,baseline,metadata)
    dump(args.out/'repeats.json',repeats)
    dump(args.out/'excluded.json',excluded)
    print(json.dumps({'baseline':len(baseline),'repeats':len(repeats),'excluded':len(excluded)},ensure_ascii=False))

if __name__=='__main__':
    main()
