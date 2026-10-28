# Agent 补测结果

协议：supplement-1。原2.4用例与Skill保持冻结；本批不混入历史成绩。

| 模型 | Skill | 用例 | 状态 | 得分 | 秒 | 最终答复 | 证据 |
|---|---|---|---|---:|---:|---|---|
| gpt-6.1-sol | db | D01 | FAIL | 92.16 | 222.25 | True | [D01-gpt-6.1-sol](D01-gpt-6.1-sol/result.json) |
| gpt-6.1-sol | db | D02 | PASS | 100.0 | 334.484 | True | [D02-gpt-6.1-sol](D02-gpt-6.1-sol/result.json) |
| gpt-6.1-sol | db | D03 | PASS | 100.0 | 277.812 | True | [D03-gpt-6.1-sol](D03-gpt-6.1-sol/result.json) |
| gpt-6.1-sol | db | D04 | FAIL | 75.0 | 304.985 | True | [D04-gpt-6.1-sol](D04-gpt-6.1-sol/result.json) |
| gpt-6-luna | db | D01 | FAIL | 60.0 | 115.453 | True | [D01-gpt-6-luna](D01-gpt-6-luna/result.json) |
| gpt-6-luna | db | D02 | FAIL | 76.47 | 203.969 | True | [D02-gpt-6-luna](D02-gpt-6-luna/result.json) |
| gpt-6-luna | db | D03 | PASS | 100.0 | 124.703 | True | [D03-gpt-6-luna](D03-gpt-6-luna/result.json) |
| gpt-6-luna | db | D04 | FAIL | 62.5 | 169.188 | True | [D04-gpt-6-luna](D04-gpt-6-luna/result.json) |

## 统计与比较范围

- gpt-6.1-sol：{"PASS": 2, "FAIL": 2, "REVIEW": 0, "BLOCKED": 0, "NOT_RUN": 0}；已完成回合中位耗时=291.399秒。
- gpt-6-luna：{"PASS": 1, "FAIL": 3, "REVIEW": 0, "BLOCKED": 0, "NOT_RUN": 0}；已完成回合中位耗时=146.945秒。

真实金融回执随工具查询路径和执行时间变化；不把它当固定快照A/B。费用未知，不能评出货币性价比冠军。
REVIEW不是通过；FAIL是任务未满足合同；BLOCKED表示运行/依赖未完成，不用部分产物冒充交付。

## 未通过与待复核

- D01-gpt-6.1-sol：；md逐行符合原始数据、html逐行符合原始数据、docx逐行符合原始数据
- D04-gpt-6.1-sol：；专项12条目标记录可核验、专项产品选型有明确依据
- D01-gpt-6-luna：；目标功能正常返回
- D02-gpt-6-luna：Semantic review failed: 自动检查REVIEW/100，但语义复核FAIL。三格式、32图与90条提取记录存在，离线data_review的身份/四指标全匹配；报告按五场景分开并显著披露STRONG公平性限制。轨迹实际执行run_pipeline.py，随后运行complete_report.py补报告；原Skill及输入未改。独立查看3张实际PNG，comparison的两张中文正常，但product_1_oltp_point_select标题及X轴出现中文缺字方框，visual_review.json绑定文件哈希；最终答复也承认字体限制。原references要求中文图表，披露问题不等于交付完成，故复核FAIL，保留automatic原100分。未将缺字放大成所有32图均不可读，也未进行全量视觉检查。LLM复核。；语义复核通过
- D04-gpt-6-luna：；专项12条目标记录可核验、专项输出包含 P99 分析、专项产品选型有明确依据、语义复核通过
