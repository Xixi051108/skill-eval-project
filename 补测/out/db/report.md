# Agent 补测结果

协议：supplement-1。原2.4用例与Skill保持冻结；本批不混入历史成绩。

| 模型 | Skill | 用例 | 状态 | 得分 | 秒 | 最终答复 | 证据 |
|---|---|---|---|---:|---:|---|---|
| gpt-6.1-sol | db | D01 | BLOCKED | None | 56.547 | False | [D01-gpt-6.1-sol](D01-gpt-6.1-sol/result.json) |
| gpt-6.1-sol | db | D02 | NOT_RUN | None | 0 | False | [D02-gpt-6.1-sol](D02-gpt-6.1-sol/result.json) |
| gpt-6.1-sol | db | D03 | NOT_RUN | None | 0 | False | [D03-gpt-6.1-sol](D03-gpt-6.1-sol/result.json) |
| gpt-6.1-sol | db | D04 | NOT_RUN | None | 0 | False | [D04-gpt-6.1-sol](D04-gpt-6.1-sol/result.json) |
| gpt-6-luna | db | D01 | NOT_RUN | None | 0 | False | [D01-gpt-6-luna](D01-gpt-6-luna/result.json) |
| gpt-6-luna | db | D02 | NOT_RUN | None | 0 | False | [D02-gpt-6-luna](D02-gpt-6-luna/result.json) |
| gpt-6-luna | db | D03 | NOT_RUN | None | 0 | False | [D03-gpt-6-luna](D03-gpt-6-luna/result.json) |
| gpt-6-luna | db | D04 | NOT_RUN | None | 0 | False | [D04-gpt-6-luna](D04-gpt-6-luna/result.json) |

## 统计与比较范围

- gpt-6.1-sol：{"PASS": 0, "FAIL": 0, "REVIEW": 0, "BLOCKED": 1, "NOT_RUN": 3}；已完成回合中位耗时=None秒。
- gpt-6-luna：{"PASS": 0, "FAIL": 0, "REVIEW": 0, "BLOCKED": 0, "NOT_RUN": 4}；已完成回合中位耗时=None秒。

真实金融回执随工具查询路径和执行时间变化；不把它当固定快照A/B。费用未知，不能评出货币性价比冠军。
REVIEW不是通过；FAIL是任务未满足合同；BLOCKED表示运行/依赖未完成，不用部分产物冒充交付。

## 未通过与待复核

- D01-gpt-6.1-sol：Agent未完成回合，详见events/stderr: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 7:29 PM. | You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 7:29 PM.；
- D02-gpt-6.1-sol：Agent未完成回合，详见events/stderr: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 7:29 PM. | You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 7:29 PM.；
- D03-gpt-6.1-sol：Agent未完成回合，详见events/stderr: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 7:29 PM. | You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 7:29 PM.；
- D04-gpt-6.1-sol：Agent未完成回合，详见events/stderr: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 7:29 PM. | You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 7:29 PM.；
- D01-gpt-6-luna：Agent未完成回合，详见events/stderr: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 7:29 PM. | You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 7:29 PM.；
- D02-gpt-6-luna：Agent未完成回合，详见events/stderr: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 7:29 PM. | You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 7:29 PM.；
- D03-gpt-6-luna：Agent未完成回合，详见events/stderr: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 7:29 PM. | You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 7:29 PM.；
- D04-gpt-6-luna：Agent未完成回合，详见events/stderr: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 7:29 PM. | You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 7:29 PM.；
