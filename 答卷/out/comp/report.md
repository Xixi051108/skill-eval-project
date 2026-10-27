# 本轮测试结果

测试层级：component。北京时间：2026-10-24T01:58:04.184041+08:00。

计划 20，PASS 11，FAIL 9，BLOCKED 0，REVIEW 0。

已测适用项得分：63.45；本轮结论：NO_GO。

该分数不包含未运行层级，不是官方验收分数。

| 用例 | 状态 | 得分 | 证据 |
| --- | --- | --- | --- |
| D01 | FAIL | 66.67 | [D01-1](D01-1/result.json) |
| D02 | PASS | 100.0 | [D02-1](D02-1/result.json) |
| D03 | PASS | 100.0 | [D03-1](D03-1/result.json) |
| D04 | FAIL | 36.36 | [D04-1](D04-1/result.json) |
| D05 | PASS | 100.0 | [D05-1](D05-1/result.json) |
| D06 | PASS | 100.0 | [D06-1](D06-1/result.json) |
| D07 | FAIL | 33.33 | [D07-1](D07-1/result.json) |
| D08 | FAIL | 0.0 | [D08-1](D08-1/result.json) |
| D09 | PASS | 100.0 | [D09-1](D09-1/result.json) |
| D10 | PASS | 100.0 | [D10-1](D10-1/result.json) |
| D11 | PASS | 100.0 | [D11-1](D11-1/result.json) |
| D12 | PASS | 100.0 | [D12-1](D12-1/result.json) |
| D13 | PASS | 100.0 | [D13-1](D13-1/result.json) |
| D14 | FAIL | 50.0 | [D14-1](D14-1/result.json) |
| D15 | PASS | 100.0 | [D15-1](D15-1/result.json) |
| D16 | FAIL | 0 | [D16-1](D16-1/result.json) |
| D17 | FAIL | 0.0 | [D17-1](D17-1/result.json) |
| D18 | PASS | 100.0 | [D18-1](D18-1/result.json) |
| D21 | FAIL | 57.14 | [D21-1](D21-1/result.json) |
| D22 | FAIL | 78.57 | [D22-1](D22-1/result.json) |

## 失败与阻塞详情

### D01 日志原始元数据与指标 (FAIL)

- R3 时长必须等于原始 Duration：实际 `2026`，预期 `300`。
- R3 数据库产品不能是测试工具：实际 `['sysbench']`，预期 `['TDSQL-B-v22.7.2']`。

### D04 用户明确要求的专项范围 (FAIL)

- R1 专项12条目标记录可核验：实际 `None`，预期 `[{'product': 'TDSQL-B v22.7.3', 'scenario': 'oltp_write_only', 'threads': 512, 'tps': 22391.81, 'qps': 67175.43, 'p95_ms': 36.92, 'p99_ms': 51.88, 'task_id': 'aa112233_tdsql_intel_x86', 'start_time': '2026-06-11 09:30:00`。
- R4 专项输出包含 P99 分析：实际 `['focus_dimension', 'buckets', 'main_finding']`，预期 `P99`。
- R4 专项产品选型有明确依据：实际 `已按产品分桶输出平均 QPS / P95，详见分析章节。`，预期 `逐产品有依据的选择建议`。

### D07 标准粘贴 JSON 的空值门控 (FAIL)

- R3 应准确定位空 QPS 而非其他解析故障：实际 `runtimeerror: 未能从数据中解析出有效记录: local_data`，预期 `['qps', '空值', 'null']`。

### D08 有效标准粘贴 JSON 配对正例 (FAIL)

- R2 目标功能正常返回：实际 `RuntimeError: 未能从数据中解析出有效记录: local_data`，预期 `success`。

### D14 版本不足不产生趋势断言 (FAIL)

- R4 两版本只能做差异说明：实际 `['version_order', 'trend', 'cumulative_change', 'regression_points', 'regression_threshold_pct']`，预期 `明确限制且不宣称长期趋势`。

### D16 真实零值不得作为缺失替换 (FAIL)

- R3 记录身份及全部核心数值符合输入：实际 `1`，预期 `2`。

### D17 records 数组空值不得补写 (FAIL)

- R6 输入应停止处理：实际 `None`，预期 `拒绝或要求修正数据`。
- R3 应准确定位空 QPS 而非其他解析故障：实际 ``，预期 `['qps', '空值', 'null']`。

### D21 标准英文字段两个场景取并集 (FAIL)

- R1 场景并集解析正确：实际 `{'test_name_keywords': [], 'test_name_keywords_or': None, 'tool_name': None, 'tool_version_keywords': [], 'component_name': None, 'component_version': None}`，预期 `['read_only', 'write_only']`。

### D22 标准英文字段同场景多个条件取交集 (FAIL)

- R1 同场景条件交集解析正确：实际 `{'test_name_keywords': [], 'test_name_keywords_or': None, 'tool_name': None, 'tool_version_keywords': [], 'component_name': None, 'component_version': None}`，预期 `['read_only']`。

