# README 提纲草稿

## 1. 项目目标
- 说明本项目是 Skill 评估任务，不是 Skill 开发任务。
- 说明评估对象为 `db_report` 与 `tracingclaw_finance` 两个 Skill。

## 2. 提交目录结构
```text
submission.zip
├── db_report_eval.yaml
├── tracingclaw_finance_eval.yaml
└── README.md
```

## 3. 两个 YAML 的统一结构
- `meta`
- `logic_chain`
- `ideal_state`
- `rubrics`
- `testcases`
- `meta_testcases`
- `coverage_matrix`

## 4. 每个模块是什么意思
- `meta`：评估对象、版本、范围、命名规范。
- `logic_chain`：Skill 从输入到输出的关键链路。
- `ideal_state`：满分 Skill 应该表现出的能力边界与质量上限。
- `rubrics`：评分维度、权重、扣分规则和零分触发条件。
- `testcases`：实际拿来测 Skill 的输入和判定条件。
- `meta_testcases`：检查测试集本身是否完整、清晰、可判定。
- `coverage_matrix`：证明测试覆盖到了哪些任务类型、风险和路径。

## 5. 统一命名规范
- testcase id：`DB-XX` / `FIN-XX`
- meta-testcase id：`META-DB-XX` / `META-FIN-XX`
- tags：统一使用小写 `snake_case`
- judge：统一使用 `pass_if_all` 与 `fail_if_any`

## 6. 评估设计原则
- 先定义能力边界，再写评分规则。
- judge 必须可执行、可观察、可复核。
- 红线场景必须既写进 rubrics，也写进 testcase。
- failure path 和 edge case 不能少于 happy path 的重要性。

## 7. Skill 级别概览
### db_report
- 核心是本地数据接入、报告类型识别、质量门控、三格式交付。

### tracingclaw_finance
- 核心是金融事实拆解、工具路由、口径一致性、0/1/2 评分与修正答案。

## 8. coverage_matrix 如何阅读
- `task_types`：测了哪些任务类型。
- `data_sources`：测了哪些数据源或工具来源。
- `risk_types`：测了哪些高风险错误。
- `path_types`：测了正常、失败、边界、红线哪些路径。
- `fatal_error_types`：测了哪些一票否决问题。

## 9. 本周推进节奏
- Day 1：搭统一框架与命名规范。
- Day 2-3：完成 `db_report`。
- Day 4-6：完成 `tracingclaw_finance`。
- Day 7：做 meta-testcases、coverage_matrix、README 和最终打包。
