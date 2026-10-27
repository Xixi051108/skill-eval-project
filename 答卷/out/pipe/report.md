# 本轮测试结果

测试层级：pipeline。北京时间：2026-10-24T01:58:05.718217+08:00。

计划 6，PASS 0，FAIL 6，BLOCKED 0，REVIEW 0。

已测适用项得分：60.8；本轮结论：NO_GO。

该分数不包含未运行层级，不是官方验收分数。

| 用例 | 状态 | 得分 | 证据 |
| --- | --- | --- | --- |
| D01 | FAIL | 75.9 | [D01-1](D01-1/result.json) |
| D02 | FAIL | 94.16 | [D02-1](D02-1/result.json) |
| D03 | FAIL | 96.1 | [D03-1](D03-1/result.json) |
| D04 | FAIL | 45.41 | [D04-1](D04-1/result.json) |
| D19 | FAIL | 77.92 | [D19-1](D19-1/result.json) |
| D20 | FAIL | 77.92 | [D20-1](D20-1/result.json) |

## 失败与阻塞详情

### D01 日志原始元数据与指标 (FAIL)

- R3 时长必须等于原始 Duration：实际 `2026`，预期 `300`。
- R3 数据库产品不能是测试工具：实际 `['sysbench']`，预期 `['TDSQL-B-v22.7.2']`。
- R5 强制交付文件 data/block_map.md：实际 `data/block_map.md`，预期 `存在`。
- R5 强制交付文件 docs/analysis_proposal.md：实际 `docs/analysis_proposal.md`，预期 `存在`。
- R3 md时长符合原始日志：实际 `None`，预期 `300秒`。
- R3 html时长符合原始日志：实际 `None`，预期 `300秒`。
- R3 docx时长符合原始日志：实际 `None`，预期 `300秒`。

### D02 三产品横向比较 (FAIL)

- R5 强制交付文件 data/block_map.md：实际 `data/block_map.md`，预期 `存在`。
- R5 强制交付文件 docs/analysis_proposal.md：实际 `docs/analysis_proposal.md`，预期 `存在`。
- R5 图表达到 reference 基线：实际 `17`，预期 `20`。

### D03 四版本趋势与回退 (FAIL)

- R5 强制交付文件 data/block_map.md：实际 `data/block_map.md`，预期 `存在`。
- R5 强制交付文件 docs/analysis_proposal.md：实际 `docs/analysis_proposal.md`，预期 `存在`。

### D04 用户明确要求的专项范围 (FAIL)

- R1 专项12条目标记录可核验：实际 `None`，预期 `[{'product': 'TDSQL-B v22.7.3', 'scenario': 'oltp_write_only', 'threads': 512, 'tps': 22391.81, 'qps': 67175.43, 'p95_ms': 36.92, 'p99_ms': 51.88, 'task_id': 'aa112233_tdsql_intel_x86', 'start_time': '2026-06-11 09:30:00`。
- R4 专项输出包含 P99 分析：实际 `['focus_dimension', 'buckets', 'main_finding']`，预期 `P99`。
- R4 专项产品选型有明确依据：实际 `已按产品分桶输出平均 QPS / P95，详见分析章节。`，预期 `逐产品有依据的选择建议`。
- R5 强制交付文件 data/block_map.md：实际 `data/block_map.md`，预期 `存在`。
- R5 强制交付文件 docs/analysis_proposal.md：实际 `docs/analysis_proposal.md`，预期 `存在`。
- R5 图表达到 reference 基线：实际 `2`，预期 `3`。
- R4 正式报告包含用户要求的P99：实际 `None`，预期 `三格式均含P99`。

### D19 严格最小交付规范 (FAIL)

- R5 强制交付文件 data/block_map.md：实际 `data/block_map.md`，预期 `存在`。
- R5 强制交付文件 docs/analysis_proposal.md：实际 `docs/analysis_proposal.md`，预期 `存在`。
- R3 md时长符合原始日志：实际 `None`，预期 `300秒`。
- R3 html时长符合原始日志：实际 `None`，预期 `300秒`。
- R3 docx时长符合原始日志：实际 `None`，预期 `300秒`。

### D20 三格式数值一致且符合原始数据 (FAIL)

- R5 强制交付文件 data/block_map.md：实际 `data/block_map.md`，预期 `存在`。
- R5 强制交付文件 docs/analysis_proposal.md：实际 `docs/analysis_proposal.md`，预期 `存在`。
- R3 md时长符合原始日志：实际 `None`，预期 `300秒`。
- R3 html时长符合原始日志：实际 `None`，预期 `300秒`。
- R3 docx时长符合原始日志：实际 `None`，预期 `300秒`。

