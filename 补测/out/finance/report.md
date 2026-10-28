# Agent 补测结果

协议：supplement-1。原2.4用例与Skill保持冻结；本批不混入历史成绩。

| 模型 | Skill | 用例 | 状态 | 得分 | 秒 | 最终答复 | 证据 |
|---|---|---|---|---:|---:|---|---|
| gpt-6.1-sol | finance | F01 | PASS | 100.0 | 131.016 | True | [F01-gpt-6.1-sol](F01-gpt-6.1-sol/result.json) |
| gpt-6.1-sol | finance | F02 | BLOCKED | None | 33.422 | False | [F02-gpt-6.1-sol](F02-gpt-6.1-sol/result.json) |
| gpt-6.1-sol | finance | F15 | NOT_RUN | None | 0 | False | [F15-gpt-6.1-sol](F15-gpt-6.1-sol/result.json) |
| gpt-6-luna | finance | F01 | NOT_RUN | None | 0 | False | [F01-gpt-6-luna](F01-gpt-6-luna/result.json) |
| gpt-6-luna | finance | F02 | NOT_RUN | None | 0 | False | [F02-gpt-6-luna](F02-gpt-6-luna/result.json) |
| gpt-6-luna | finance | F15 | NOT_RUN | None | 0 | False | [F15-gpt-6-luna](F15-gpt-6-luna/result.json) |

## 统计与比较范围

- gpt-6.1-sol：{"PASS": 1, "FAIL": 0, "REVIEW": 0, "BLOCKED": 1, "NOT_RUN": 1}；已完成回合中位耗时=131.016秒。
- gpt-6-luna：{"PASS": 0, "FAIL": 0, "REVIEW": 0, "BLOCKED": 0, "NOT_RUN": 3}；已完成回合中位耗时=None秒。

真实金融回执随工具查询路径和执行时间变化；不把它当固定快照A/B。费用未知，不能评出货币性价比冠军。
REVIEW不是通过；FAIL是任务未满足合同；BLOCKED表示运行/依赖未完成，不用部分产物冒充交付。

## 未通过与待复核

- F02-gpt-6.1-sol：Agent未完成回合，详见events/stderr: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 7:29 PM. | You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 7:29 PM.；
- F15-gpt-6.1-sol：Agent未完成回合，详见events/stderr: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 7:29 PM. | You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 7:29 PM.；
- F01-gpt-6-luna：Agent未完成回合，详见events/stderr: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 7:29 PM. | You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 7:29 PM.；
- F02-gpt-6-luna：Agent未完成回合，详见events/stderr: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 7:29 PM. | You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 7:29 PM.；
- F15-gpt-6-luna：Agent未完成回合，详见events/stderr: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 7:29 PM. | You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 7:29 PM.；
