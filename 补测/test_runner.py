from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import json
import hashlib
import os
import shutil
import sys
import unittest
from urllib.error import HTTPError
from urllib.request import Request, urlopen

import runner
from gateway import Gateway, clean_env, invoke


class SupplementChecks(unittest.TestCase):
    def test_agent_environment_does_not_receive_real_key(self):
        with patch.dict(os.environ, {'EM_API_KEY': 'private-test-value', 'OTHER_TOKEN': 'private-token'}):
            env = clean_env()
            self.assertNotIn('EM_API_KEY', env)
            self.assertNotIn('OTHER_TOKEN', env)
            self.assertEqual(os.environ['EM_API_KEY'], 'private-test-value')

    def test_real_search_route_and_redaction(self):
        with TemporaryDirectory() as temp, patch.dict(os.environ, {'EM_API_KEY': 'private-test-value'}):
            root = Path(temp)
            script = root / 'mx-finance-search/scripts/get_data.py'
            script.parent.mkdir(parents=True)
            script.write_text('# original tool stand-in for routing test', encoding='utf-8')
            with patch('gateway.invoke', return_value=(0, 'receipt private-test-value\r\nnext\n', '', False)) as call:
                with Gateway(root, root / 'receipts') as gateway:
                    receipt = gateway.call('mx-finance-search', ['search', '腾讯 2024 年报'])
                self.assertEqual(call.call_args.kwargs['env']['EM_API_KEY'], 'private-test-value')
                self.assertEqual(call.call_args.args[0][1], str(script.resolve()))
                self.assertIn('--no-save', call.call_args.args[0])
                self.assertEqual(receipt['status'], 'ok')
                self.assertNotIn('private-test-value', json.dumps(receipt))
                self.assertNotIn('private-test-value', (root / 'receipts/tool-001.stdout.txt').read_text())
                self.assertEqual(hashlib.sha256((root / 'receipts/tool-001.stdout.txt').read_bytes()).hexdigest(),
                                 receipt['stdout_sha256'])

    def test_gateway_requires_session_capability(self):
        with TemporaryDirectory() as temp, Gateway(Path(temp), Path(temp) / 'receipts') as gateway:
            config = gateway.config()
            # Authentication precedes payload parsing; send no unread body on rejection.
            request = Request(config['url'], data=b'', headers={'Authorization': 'Bearer wrong'})
            with self.assertRaises(HTTPError) as error:
                urlopen(request, timeout=2)
            self.assertEqual(error.exception.code, 403)
            self.assertFalse(gateway.receipts)

    def test_gateway_rejects_unbounded_or_unsupported_operations(self):
        with TemporaryDirectory() as temp, Gateway(Path(temp), Path(temp) / 'receipts', limit=1) as gateway:
            with self.assertRaises(ValueError):
                gateway.call('westock-data', ['finance', 'x' * 1001])
            self.assertEqual(gateway.call('shell', ['delete'])['status'], 'unsupported')
            self.assertEqual(gateway.call('westock-data', ['finance', 'hk00700'])['status'], 'budget_exhausted')

    def test_finance_uses_independent_truth_and_current_receipts(self):
        case = next(c for c in runner.base.cases('finance') if c['id'] == 'F01')
        response = {'label': 'supported', 'score': 2, 'facts': [
            {'name': name, 'value': value, 'evidence_id': 'LIVE-001'} for name, value in case['gold']['facts'].items()],
            'answer': '已按两个真实工具返回核查年报的营收、报告期、人民币和同比；证据支持与来源冲突仍需复核。'}
        receipts = [{'tool': 'westock-data', 'status': 'ok', 'evidence_id': 'LIVE-001'},
                    {'tool': 'mx-finance-search', 'status': 'ok', 'evidence_id': 'LIVE-002'}]
        self.assertEqual(runner.finance_judge(case, response, receipts)['status'], 'PASS')
        response['facts'][0]['value'] = 13000
        self.assertEqual(runner.finance_judge(case, response, receipts)['status'], 'FAIL')

    def test_finance_cannot_cite_fixture_as_live_evidence(self):
        case = next(c for c in runner.base.cases('finance') if c['id'] == 'F01')
        response = {'label': 'supported', 'score': 2, 'facts': [
            {'name': name, 'value': value, 'evidence_id': 'TENCENT-2024'} for name, value in case['gold']['facts'].items()],
            'answer': '这是一份字段与数值正确但引用旧夹具ID的合成回答，应该被新的真实回执检查拒绝。'}
        receipts = [{'tool': 'westock-data', 'status': 'ok', 'evidence_id': 'LIVE-001'},
                    {'tool': 'mx-finance-search', 'status': 'ok', 'evidence_id': 'LIVE-002'}]
        self.assertEqual(runner.finance_judge(case, response, receipts)['status'], 'FAIL')

    def test_prompt_has_no_gold_and_never_copies_financial_key(self):
        case = next(c for c in runner.base.cases('finance') if c['id'] == 'F01')
        with TemporaryDirectory() as temp, patch.dict(os.environ, {'EM_API_KEY': 'private-test-value'}):
            tools, work = Path(temp) / 'tools', Path(temp) / 'work'
            for name in ('westock-data', 'mx-finance-search'):
                document = tools / name / 'SKILL.md'
                document.parent.mkdir(parents=True)
                document.write_text('Tool configuration documentation', encoding='utf-8')
            text = runner.prompt(case, work, tools)
            self.assertNotIn('6602.57', text)
            self.assertNotIn('private-test-value', text)
            self.assertFalse((work / 'tools.json').exists())
            self.assertTrue((work / 'tool.py').is_file())

    def test_process_audit_detects_skill_mutation(self):
        case = next(c for c in runner.base.cases('finance') if c['id'] == 'F01')
        event = {'type': 'item.completed', 'item': {'type': 'command_execution', 'exit_code': 0,
                                                   'command': 'Get-Content skill/SKILL.md'}}
        with TemporaryDirectory() as temp:
            work = Path(temp)
            shutil.copytree(runner.ANSWER / 'sut/finance', work / 'skill')
            self.assertTrue(runner.process_audit([event], case, work)['skill_bytes_unchanged'])
            self.assertTrue(runner.process_audit([event], case, work)['skill_read_observed'])
            (work / 'skill/SKILL.md').write_text('changed', encoding='utf-8')
            self.assertFalse(runner.process_audit([event], case, work)['skill_bytes_unchanged'])

    def test_timeout_stops_the_owned_process(self):
        with TemporaryDirectory() as temp:
            code, stdout, stderr, timed_out = invoke([sys.executable, '-c', 'import time;time.sleep(10)'],
                                                     env=clean_env(), cwd=temp, timeout=0.2)
            self.assertTrue(timed_out)
            self.assertIsNotNone(code)


if __name__ == '__main__':
    unittest.main(verbosity=2)
