# Agent 补测结果

协议：supplement-1。原2.4用例与Skill保持冻结；本批不混入历史成绩。

| 模型 | Skill | 用例 | 状态 | 得分 | 秒 | 最终答复 | 证据 |
|---|---|---|---|---:|---:|---|---|
| gpt-6.1-sol | finance | F02 | PASS | 100.0 | 110.235 | True | [F02-gpt-6.1-sol](F02-gpt-6.1-sol/result.json) |
| gpt-6.1-sol | finance | F15 | PASS | 100.0 | 154.907 | True | [F15-gpt-6.1-sol](F15-gpt-6.1-sol/result.json) |

## 统计与比较范围

- gpt-6.1-sol：{"PASS": 2, "FAIL": 0, "REVIEW": 0, "BLOCKED": 0, "NOT_RUN": 0}；已完成回合中位耗时=132.571秒。

真实金融回执随工具查询路径和执行时间变化；不把它当固定快照A/B。费用未知，不能评出货币性价比冠军。
REVIEW不是通过；FAIL是任务未满足合同；BLOCKED表示运行/依赖未完成，不用部分产物冒充交付。

## 未通过与待复核

