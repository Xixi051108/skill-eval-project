import unittest
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from audit import mapped_rows, data_audit


class TableAuditChecks(unittest.TestCase):
    def test_extra_column_and_reordered_metrics(self):
        rows = [['场景', '并发', '记录时间', 'QPS', 'TPS', 'P95 (ms)', 'P99 (ms)'],
                ['点查', '32', '14:00:00', '2,000.5', '1000', '3.1', '4.2']]
        actual = mapped_rows(rows)
        self.assertEqual(actual, [{'scenario': 'oltp_point_select', 'threads': 32.0,
                                  'qps': 2000.5, 'tps': 1000.0, 'p95_ms': 3.1, 'p99_ms': 4.2}])

    def test_missing_or_duplicate_metric_header_cannot_pass(self):
        for headers in [['场景', '并发', 'TPS', 'QPS', 'P95 (ms)'],
                        ['场景', '并发', 'TPS', 'QPS', 'P95 (ms)', 'P99 (ms)', 'QPS']]:
            self.assertEqual(mapped_rows([headers, ['点查', '32', '100', '200', '3', '4', '999']]), [])

    def test_intermediate_records_checked_against_source(self):
        with TemporaryDirectory() as temp:
            root = Path(temp)
            records = [{'product': 'A', 'scenario': 'oltp_point_select', 'threads': 32,
                        'tps': 0, 'qps': 0, 'p95_ms': 2, 'p99_ms': 3}]
            source = root / 'source.json'
            source.write_text(json.dumps({'records': records}), encoding='utf-8')
            (root / 'data').mkdir()
            extracted = root / 'data/extracted_data.json'
            extracted.write_text(source.read_text(), encoding='utf-8')
            self.assertTrue(data_audit(root, source)['matched'])
            records[0]['qps'] = None
            extracted.write_text(json.dumps({'records': records}), encoding='utf-8')
            self.assertFalse(data_audit(root, source)['matched'])


if __name__ == '__main__':
    unittest.main()
