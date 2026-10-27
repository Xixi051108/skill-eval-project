# 本轮测试结果

测试层级：agent。北京时间：2026-10-24T01:57:30.884702+08:00。

计划 3，PASS 2，FAIL 1，BLOCKED 0，REVIEW 0。

已测适用项得分：97.71；本轮结论：NO_GO。

该分数不包含未运行层级，不是官方验收分数。

| 用例 | 状态 | 得分 | 证据 |
| --- | --- | --- | --- |
| F01 | PASS | 100.0 | [F01-1](F01-1/result.json) [原始答复](F01-1/response.txt) |
| F06 | FAIL | 0 | [F06-1](F06-1/result.json) [原始答复](F06-1/response.txt) |
| F08 | PASS | 100.0 | [F08-1](F08-1/result.json) [原始答复](F08-1/response.txt) |

## 失败与阻塞详情

### F06 涨幅超过3的阈值3.0 (FAIL)

- R3 独立真值 currency：实际 `None`，预期 `CNY`。
- R2 currency对应实际取得的证据：实际 `None`，预期 `实际工具返回中的 evidence_id`。

