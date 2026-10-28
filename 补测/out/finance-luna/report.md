# Agent 补测结果

协议：supplement-1。原2.4用例与Skill保持冻结；本批不混入历史成绩。

| 模型 | Skill | 用例 | 状态 | 得分 | 秒 | 最终答复 | 证据 |
|---|---|---|---|---:|---:|---|---|
| gpt-6-luna | finance | F01 | PASS | 100.0 | 103.641 | True | [F01-gpt-6-luna](F01-gpt-6-luna/result.json) |
| gpt-6-luna | finance | F02 | FAIL | 68.63 | 67.688 | True | [F02-gpt-6-luna](F02-gpt-6-luna/result.json) |
| gpt-6-luna | finance | F15 | FAIL | 70.59 | 88.672 | True | [F15-gpt-6-luna](F15-gpt-6-luna/result.json) |

## 统计与比较范围

- gpt-6-luna：{"PASS": 1, "FAIL": 2, "REVIEW": 0, "BLOCKED": 0, "NOT_RUN": 0}；已完成回合中位耗时=88.672秒。

真实金融回执随工具查询路径和执行时间变化；不把它当固定快照A/B。费用未知，不能评出货币性价比冠军。
REVIEW不是通过；FAIL是任务未满足合同；BLOCKED表示运行/依赖未完成，不用部分产物冒充交付。

## 未通过与待复核

- F02-gpt-6-luna：；事实名称不重复、独立官方真值 revenue_yi、独立官方真值 revenue_yoy_pct、独立官方真值 currency、语义复核通过
- F15-gpt-6-luna：；事实名称不重复、独立官方真值 revenue_yi、独立官方真值 currency、语义复核通过
