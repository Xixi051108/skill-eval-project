"""Offline report/data audits; annotate frozen Judge results without overriding them."""
from pathlib import Path
import argparse
import hashlib
import json
import sys
import zipfile
import xml.etree.ElementTree as ET

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / '答卷'))
from judge import HTMLText, METRICS, SCENARIO_DISPLAY, log_truth, reported_rows_match, rows_equal


def raw_rows(path, fmt):
    if fmt == 'md':
        return [[c.strip() for c in line.strip().strip('|').split('|')]
                for line in path.read_text(encoding='utf-8-sig').splitlines()
                if line.strip().startswith('|')]
    if fmt == 'html':
        parser = HTMLText()
        parser.feed(path.read_text(encoding='utf-8-sig'))
        return parser.rows
    with zipfile.ZipFile(path) as archive:
        root = ET.fromstring(archive.read('word/document.xml'))
    ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
    return [[''.join(t.text or '' for t in cell.findall('.//w:t', ns))
             for cell in row.findall('w:tc', ns)] for row in root.findall('.//w:tr', ns)]


def mapped_rows(rows):
    # Only explicit headers identify columns; extra columns cannot shift metrics.
    aliases = {'场景': 'scenario', 'scenario': 'scenario', '并发': 'threads',
               '线程数': 'threads', 'threads': 'threads', 'tps': 'tps', 'qps': 'qps',
               'p95(ms)': 'p95_ms', 'p95_ms': 'p95_ms', 'p99(ms)': 'p99_ms', 'p99_ms': 'p99_ms'}
    required = {'scenario', 'threads', *METRICS}
    mapping, result = None, []
    for cells in rows:
        names = [aliases.get(''.join(c.lower().split())) for c in cells]
        if required <= set(names):
            if all(names.count(name) == 1 for name in required):
                mapping = {name: names.index(name) for name in required}
            else:
                mapping = None
            continue
        if mapping is None or len(cells) <= max(mapping.values()):
            continue
        scenario = cells[mapping['scenario']]
        scenario = SCENARIO_DISPLAY.get(scenario, scenario)
        if not scenario.startswith('oltp_'):
            continue
        try:
            values = {key: float(cells[mapping[key]].replace(',', '')) for key in required - {'scenario'}}
        except ValueError:
            continue
        result.append({'scenario': scenario, **values})
    return result


def audit(artifacts, source):
    expected = log_truth(source)['records']
    results = {}
    for fmt in ('md', 'html', 'docx'):
        path = artifacts / ('report.' + fmt)
        if not path.is_file():
            results[fmt] = {'matched': False, 'reason': 'missing report'}
            continue
        rows = mapped_rows(raw_rows(path, fmt))
        results[fmt] = {'matched': reported_rows_match(rows, expected),
                        'actual_rows': len(rows), 'expected_rows': len(expected)}
    return {'method': 'deterministic_header_mapping', 'source': str(source),
            'sha256': {str(path): hashlib.sha256(path.read_bytes()).hexdigest()
                       for path in [Path(__file__), source, *[artifacts / ('report.' + fmt)
                                    for fmt in ('md', 'html', 'docx')]] if path.is_file()},
            'scope': 'D01三格式的场景、并发、TPS、QPS、P95、P99逐行核验；不代表全部交付规范通过',
            'formats': results, 'all_matched': all(r['matched'] for r in results.values()),
            'note': '独立补充审计，不覆盖automatic.json/result.json；冻结裁判只接受六列，可能漏读额外列。'}


def data_audit(artifacts, source):
    expected = log_truth(source)['records'] if source.suffix == '.log' else json.loads(source.read_text(encoding='utf-8'))['records']
    extracted = artifacts / 'data/extracted_data.json'
    actual = json.loads(extracted.read_text(encoding='utf-8')).get('records') if extracted.is_file() else None
    return {'method': 'independent_source_record_comparison', 'matched': rows_equal(actual, expected),
            'actual_rows': len(actual) if isinstance(actual, list) else None, 'expected_rows': len(expected),
            'scope': '按product/scenario/threads比较全部TPS/QPS/P95/P99；专项筛选集合另由原Judge检查',
            'sha256': {str(p): hashlib.sha256(p.read_bytes()).hexdigest()
                       for p in (Path(__file__), source, extracted) if p.is_file()}}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--artifacts', type=Path, required=True)
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--data-only', action='store_true')
    args = parser.parse_args()
    result = (data_audit if args.data_only else audit)(args.artifacts, args.source)
    args.out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
