"""Supplementary native Agent runs; frozen 2.4 sources and results stay unchanged."""
from pathlib import Path
from types import SimpleNamespace
import argparse
import hashlib
import json
import os
import re
import shutil
import statistics
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parent
ANSWER = PROJECT / '答卷'
sys.path.insert(0, str(ANSWER))
import run as base
from judge import check, verdict, same, judge_db, judge_db_native
from gateway import Gateway, clean_env, redact, secret_values, stop

VERSION = 'supplement-1'
FINANCE_IDS = {'F01', 'F02', 'F15'}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def tree_hashes(folder):
    return {p.relative_to(folder).as_posix(): sha(p) for p in Path(folder).rglob('*')
            if p.is_file() and '__pycache__' not in p.parts and p.suffix != '.pyc'}


def prompt(case, work, tools_root):
    if case['suite'] == 'db':
        text = base.public_prompt(case, work)
    else:
        shutil.copytree(ANSWER / 'sut/finance', work / 'skill')
        shutil.copy2(HERE / 'tool.py', work / 'tool.py')
        for tool in ('westock-data', 'mx-finance-search'):
            target = work / 'dependencies' / tool
            target.mkdir(parents=True)
            shutil.copy2(tools_root / tool / 'SKILL.md', target / 'SKILL.md')
            if (tools_root / tool / 'references').is_dir():
                shutil.copytree(tools_root / tool / 'references', target / 'references')
        text = ('执行真实金融 Skill 用户任务。先读取 skill/SKILL.md。当前工作区是本次任务唯一工作区，'
                '不读取父目录、裁判、密钥或环境变量，不修改 Skill 或附件，不创建子 Agent。\n'
                '任务的固定日期锚点：' + case['input']['clock'] + '。本轮实际联网，不提供合成行情。\n'
                '已配置真实金融工具，密钥只由宿主提供给原工具子进程。读取 dependencies/ 下对应工具 Skill 与所需 references。\n'
                '逻辑命令 westock-data 对应：python tool.py westock-data COMMAND ARGUMENTS；'
                '支持只读 finance/quote/kline/search/help，finance 可用 hk00700 --num 8。'
                '资讯对应：python tool.py mx-finance-search search 查询文本。'
                '工具返回 LIVE-xxx 证据ID与原始正文，不能把原始接口返回自动当独立事实，必须校验时间、市场、币种和报告期。\n'
                '只能通过上述入口调用外部金融工具，不直接访问网络或其他金融服务。每任务最多8次真实工具调用。'
                '失败回执不得假装成功；无法核实时保留未知并说明原因。\n'
                '最终 JSON 字段：action(verify/answer/clarify/insufficient/blocked/refuse)、'
                'label(supported/contradicted/insufficient_evidence)、score(0/1/2或null)、'
                'facts([{name,value,evidence_id}])、secondary_label(字符串或null)、conflict(布尔)、missing(字符串列表)、'
                'answer(面向用户的结论、明细、口径风险和修正答案)。财报事实统一命名 revenue_yi(亿元)、'
                'revenue_yoy_pct(同比百分比)、currency(如CNY)、report_period(日期)。'
                '每个事实引用实际回执 LIVE-xxx，核对来源矛盾，不能声称未完成的交叉验证。\n'
                'Python运行时：' + sys.executable + '\n用户请求：\n' + case['input']['user_request'])
    text += ('\n执行预算内完成任务并给出最终用户答复。遵守原Skill及references，不修改原Skill源码；'
             '无法满足任务或强制交付时明确列出失败与已有产物，不伪称完成。'
             '测试只评估当前任务，不要求修改评估标准或修复原Skill。')
    return text


def process_audit(events, case, work):
    commands = [e['item'] for e in events if e.get('type') == 'item.completed'
                and e.get('item', {}).get('type') == 'command_execution']
    observed = []
    for index, item in enumerate(commands):
        command = item.get('command', '').replace('\\', '/').lower()
        if item.get('exit_code') == 0 and 'skill/skill.md' in command:
            observed.append({'step': 'read_skill', 'command_index': index, 'command': item['command']})
        if 'references/' in command and any(word in command for word in ('get-content', 'read_text', 'cat ', 'type ')):
            observed.append({'step': 'read_reference_candidate', 'command_index': index, 'command': item['command']})
        if 'tool.py' in command:
            observed.append({'step': 'finance_tool_request', 'command_index': index, 'command': item['command']})
        if 'run_pipeline.py' in command:
            observed.append({'step': 'pipeline_request', 'command_index': index, 'command': item['command']})
    source = ANSWER / 'sut' / case['suite']
    return {'command_count': len(commands), 'observations': observed,
            'skill_bytes_unchanged': tree_hashes(source) == tree_hashes(work / 'skill'),
            'input_bytes_unchanged': all(sha(ANSWER / name) == sha(work / name) for name in case['input']['files']),
            'skill_read_observed': any(o['step'] == 'read_skill' for o in observed),
            'note': '命令匹配是可观察线索，动态读取与阶段顺序另行复核；不宣称强物理隔离。'}


def finance_judge(case, response, receipts):
    checks = []
    if not isinstance(response, dict):
        check(checks, '结构化答复有效', 'R5', False)
        return verdict(checks)
    successes = {r['evidence_id']: r for r in receipts if r['status'] == 'ok'}
    called = {r['tool'] for r in receipts}
    if receipts and not successes and response.get('score') is None and response.get('missing'):
        return {'status': 'BLOCKED', 'score': None, 'checks': [], 'dimensions': {}, 'fatal': False,
                'reason': '真实依赖未成功返回有效回执；Agent保留未知，不能算完成正常核查任务'}
    gold = case['gold']
    check(checks, '核查主需断言正确', 'R4', response.get('label') == gold['label'], response.get('label'), gold['label'])
    check(checks, '候选评分或不评分符合用户请求', 'R4', same(response.get('score'), gold['score']), response.get('score'), gold['score'])
    for tool in ('westock-data', 'mx-finance-search'):
        check(checks, tool + '实际调用', 'R2', tool in called, sorted(called), tool)
        check(checks, tool + '取得成功回执', 'R2', any(r['tool'] == tool for r in successes.values()))
    facts = response.get('facts', [])
    valid = isinstance(facts, list) and all(isinstance(f, dict) for f in facts)
    check(checks, 'facts为对象列表', 'R5', valid)
    facts = facts if valid else []
    by_name = {f.get('name'): f for f in facts}
    check(checks, '事实名称不重复', 'R5', len(by_name) == len(facts))
    for name, expected in gold.get('facts', {}).items():
        fact = by_name.get(name, {})
        tolerance = 3 if name == 'revenue_yi' else 0.5 if name == 'revenue_yoy_pct' else 0.01
        check(checks, '独立官方真值 ' + name, 'R3', same(fact.get('value'), expected, tolerance), fact.get('value'), expected)
        check(checks, name + '引用本次成功回执', 'R2', fact.get('evidence_id') in successes, fact.get('evidence_id'), list(successes))
    for fact in facts:
        check(checks, '事实引用实际回执 ' + str(fact.get('name')), 'R2', fact.get('evidence_id') in successes)
    check(checks, '有面向用户的解释', 'R5', isinstance(response.get('answer'), str) and len(response['answer']) >= 30)
    result = verdict(checks)
    result['evidence_support_review'] = '原始回执未自动解释成真值；逐项引用支持、冲突处理及口径需LLM复核。'
    return result


def db_judge(case, reply, artifacts):
    if case['gold'].get('stop'):
        return judge_db_native(case, reply, artifacts)
    extracted = artifacts / 'data/extracted_data.json'
    analysis_path = artifacts / 'data/analysis_results.json'
    value = base.load(extracted) if extracted.is_file() else {}
    analysis = base.load(analysis_path) if analysis_path.is_file() else {}
    if case['mode'] in ('iteration', 'custom'):
        value = analysis.get(case['mode'], {})
    return judge_db(case, {'ok': extracted.is_file(), 'value': value, 'error': '未生成标准提取文件' if not extracted.is_file() else None}, ANSWER, artifacts)


def execute(case, model, folder, args):
    folder.mkdir()
    work = base.workdir(folder, case)
    request = prompt(case, work, args.tools_root)
    (folder / 'request.txt').write_text(request, encoding='utf-8')
    command = [shutil.which('codex') or 'codex', 'exec', '--ephemeral', '--skip-git-repo-check',
               '--sandbox', 'workspace-write', '--json', '--color', 'never', '--ignore-user-config', '-C', str(work)]
    command += base.provider_config() + ['--model', model, '-c', 'model_reasoning_effort=' + json.dumps(args.effort)]
    if case['suite'] == 'finance':
        base.dump(folder / 'schema.json', base.response_schema())
        command += ['--output-schema', str(folder / 'schema.json'), '-c', 'sandbox_workspace_write.network_access=true']
    command += ['-']
    base.dump(folder / 'command.json', command)
    env = clean_env()
    env['PYTHONPATH'] = str(PROJECT / '.evaldeps') + os.pathsep + env.get('PYTHONPATH', '')
    env['MPLCONFIGDIR'] = str(folder / 'mpl')
    values = secret_values()
    gateway = Gateway(args.tools_root, folder / 'receipts') if case['suite'] == 'finance' else None
    flags = (subprocess.CREATE_NO_WINDOW | subprocess.CREATE_NEW_PROCESS_GROUP) if os.name == 'nt' else 0
    start = time.monotonic()
    timed_out = False
    if gateway:
        gateway.__enter__()
        base.dump(work / 'endpoint.json', gateway.config())
    try:
        process = subprocess.Popen(command, cwd=work, env=env, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE, creationflags=flags, start_new_session=os.name != 'nt')
        try:
            stdout, stderr = process.communicate(request.encode('utf-8'), timeout=args.timeout)
        except subprocess.TimeoutExpired:
            timed_out = True
            stop(process)
            stdout, stderr = process.communicate()
    finally:
        if gateway:
            gateway.__exit__()
    output = redact(stdout.decode('utf-8', 'replace'), values)
    errors = redact(stderr.decode('utf-8', 'replace'), values)
    (folder / 'events.jsonl').write_text(output, encoding='utf-8')
    (folder / 'stderr.txt').write_text(errors, encoding='utf-8')
    events = []
    for line in output.splitlines():
        try:
            events.append(json.loads(line))
        except ValueError:
            pass
    completed = any(e.get('type') == 'turn.completed' for e in events)
    replies = [e['item']['text'] for e in events if e.get('type') == 'item.completed'
               and e.get('item', {}).get('type') == 'agent_message']
    reply = replies[-1] if completed and replies else ''
    if reply:
        (folder / 'response.txt').write_text(reply, encoding='utf-8')
    audit = process_audit(events, case, work)
    base.dump(folder / 'process.json', audit)
    receipts = gateway.receipts if gateway else []
    if timed_out or process.returncode or not reply:
        reason = 'Agent执行超时' if timed_out else 'Agent未完成回合，详见events/stderr'
        failed = [e.get('message') or e.get('error', {}).get('message', '') for e in events if e.get('type') in ('error', 'turn.failed')]
        result = {'status': 'BLOCKED', 'score': None, 'checks': [], 'dimensions': {}, 'fatal': False,
                  'reason': reason + ': ' + ' | '.join(str(x) for x in failed)}
    else:
        try:
            result = finance_judge(case, json.loads(reply), receipts) if gateway else db_judge(case, reply, work / 'artifacts')
        except (ValueError, OSError) as error:
            result = {'status': 'FAIL', 'score': 0, 'checks': [], 'dimensions': {}, 'fatal': False, 'reason': str(error)}
        if result['status'] not in ('BLOCKED',):
            checks = result['checks']
            check(checks, '被测Skill字节未改变', 'R6', audit['skill_bytes_unchanged'], fatal=True)
            check(checks, '公开输入字节未改变', 'R6', audit['input_bytes_unchanged'], fatal=True)
            result.update(verdict(checks))
            result['semantic_review'] = 'PENDING: 解释、来源支持、限制和过程另行复核'
            if result['status'] == 'PASS':
                result['status'] = 'REVIEW'
    usage = next((e.get('usage') for e in reversed(events) if e.get('type') == 'turn.completed'), None)
    result.update(id=case['id'], model=model, suite=case['suite'], run=folder.name,
                  seconds=round(time.monotonic() - start, 3), usage=usage, monetary_cost=None,
                  prompt_sha256=sha(folder / 'request.txt'), final_response=bool(reply),
                  tool_calls=len(receipts), skill_read_observed=audit['skill_read_observed'])
    base.dump(folder / 'automatic.json', result)
    base.dump(folder / 'result.json', result)
    return result


def write_report(folder, rows, metadata):
    base.dump(folder / 'results.json', {'metadata': metadata, 'results': rows})
    lines = ['# Agent 补测结果', '', '协议：' + VERSION + '。原2.4用例与Skill保持冻结；本批不混入历史成绩。', '',
             '| 模型 | Skill | 用例 | 状态 | 得分 | 秒 | 最终答复 | 证据 |', '|---|---|---|---|---:|---:|---|---|']
    for row in rows:
        lines.append('| {model} | {suite} | {id} | {status} | {score} | {seconds} | {final_response} | [{run}]({run}/result.json) |'.format(**row))
    lines += ['', '## 统计与比较范围', '']
    for model in metadata['models']:
        subset = [r for r in rows if r['model'] == model]
        counts = {status: sum(r['status'] == status for r in subset) for status in ('PASS', 'FAIL', 'REVIEW', 'BLOCKED', 'NOT_RUN')}
        times = [r['seconds'] for r in subset if r.get('final_response')]
        lines.append('- ' + model + '：' + json.dumps(counts, ensure_ascii=False) + '；已完成回合中位耗时=' + str(round(statistics.median(times), 3) if times else None) + '秒。')
    lines += ['', '真实金融回执随工具查询路径和执行时间变化；不把它当固定快照A/B。费用未知，不能评出货币性价比冠军。',
              'REVIEW不是通过；FAIL是任务未满足合同；BLOCKED表示运行/依赖未完成，不用部分产物冒充交付。', '', '## 未通过与待复核', '']
    for row in rows:
        if row['status'] != 'PASS':
            failures = [c['name'] for c in row.get('checks', []) if not c['passed']]
            lines.append('- ' + row['run'] + '：' + row.get('reason', '') + '；' + '、'.join(failures))
    (folder / 'report.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--suite', choices=('db', 'finance'), required=True)
    parser.add_argument('--models', default='gpt-6.1-sol,gpt-6-luna')
    parser.add_argument('--cases', default='')
    parser.add_argument('--effort', choices=('low', 'medium', 'high'), default='medium')
    parser.add_argument('--timeout', type=int, default=420)
    parser.add_argument('--tools-root', type=Path, default=PROJECT / '性能工程+Skill+评估专项考题/tracingclaw_finance')
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    args.tools_root = args.tools_root.resolve()
    args.out = args.out.resolve()
    models = args.models.split(',')
    if any(not re.fullmatch(r'[A-Za-z0-9._-]+', model) for model in models):
        parser.error('invalid model identifier')
    selected_ids = set(args.cases.split(',')) if args.cases else ({'D01', 'D02', 'D03', 'D04'} if args.suite == 'db' else FINANCE_IDS)
    selected = [c for c in base.cases(args.suite) if c['id'] in selected_ids]
    if {c['id'] for c in selected} != selected_ids or (args.suite == 'finance' and not selected_ids <= FINANCE_IDS):
        parser.error('unknown or unsupported supplementary cases')
    validation = base.validate()
    if validation['status'] != 'PASS':
        raise RuntimeError('Original 2.4 frozen inputs/evaluator differ; abort rather than change history')
    args.out.mkdir(parents=True, exist_ok=False)
    metadata = {'version': VERSION, 'at': base.now(), 'models': models, 'suite': args.suite, 'effort': args.effort,
                'timeout': args.timeout, 'cases': [c['id'] for c in selected], 'original_manifest_sha256': sha(ANSWER / 'manifest.json'),
                'supplement_sha256': {p.name: sha(p) for p in HERE.glob('*.py')},
                'data_skill_sha256': base.hashes(), 'finance_truth': base.load(ANSWER / 'sources.json'),
                'contract': '独立真实金融取证；营收绝对容差3亿元、同比0.5个百分点；双方工具必须实际调用并成功；正文支持另复核。数据库沿用原Judge并增加输入/Skill字节检查。'}
    base.dump(args.out / 'protocol.json', metadata)
    rows = []
    blocked = None
    for model in models:
        for case in selected:
            name = case['id'] + '-' + model
            if blocked:
                row = {'id': case['id'], 'model': model, 'suite': args.suite, 'run': name, 'status': 'NOT_RUN',
                       'score': None, 'seconds': 0, 'final_response': False, 'reason': blocked}
                (args.out / name).mkdir()
                base.dump(args.out / name / 'result.json', row)
            else:
                row = execute(case, model, args.out / name, args)
                if row['status'] == 'BLOCKED' and any(word in row.get('reason', '').lower() for word in ('quota', 'limit', 'credit', '额度', 'authentication', 'unauthorized')):
                    blocked = row['reason']
            rows.append(row)
            write_report(args.out, rows, metadata)
            print(model, case['id'], row['status'], row.get('seconds'), flush=True)
    assert base.validate()['status'] == 'PASS'


if __name__ == '__main__':
    main()
