# db_report Skill 评估方案

## 适用范围

本目录为 `db_report` Skill 的提交版评估材料，评估对象对齐当前新版 `db_report_skill` 主包。  
提交内容覆盖逻辑链路、理想态、评分规则、测试用例、元测试设计与实际测试报告。

## 交付物清单

| 文件 | 类型 | 说明 |
| --- | --- | --- |
| `db_report_logic_chain.md` | Markdown | Skill 执行链路、阶段输出、停止条件 |
| `db_report_ideal_state.md` | Markdown | 理想态、能力边界、禁止行为、异常处理 |
| `db_report_rubrics.yaml` | YAML | 100 分制评分规则 |
| `db_report_testcases.yaml` | YAML | 核心测试用例集 |
| `db_report_meta_testcases.md` | Markdown | 测试集自检与元测试设计 |
| `db_report_test_report.html` | HTML | 基于真实运行结果的测试报告 |

## 覆盖汇总

说明：下表展示各评测维度与测试用例之间的主覆盖关系；单条用例可能同时覆盖多个维度，最终判定以 `db_report_testcases.yaml` 中的结构化定义为准。

| 覆盖维度 | 覆盖用例 |
| --- | --- |
| R1 输入解析与意图识别 | DB-01, DB-02, DB-03, DB-04, DB-05, DB-06, DB-08, DB-09, DB-10 |
| R2 数据源接入与标准化 | DB-01, DB-02, DB-03, DB-04, DB-06, DB-07, DB-09, DB-10 |
| R3 数据质量门控 | DB-01, DB-02, DB-03, DB-07, DB-11 |
| R4 性能分析与洞察质量 | DB-01, DB-02, DB-03, DB-04, DB-09, DB-10, DB-12 |
| R5 图表生成与三格式交付 | DB-01, DB-02, DB-03, DB-04, DB-11 |
| R6 红线与拒绝机制 | DB-05, DB-06, DB-08 |
| `single` 主路径 | DB-01 |
| `comparison` 主路径 | DB-02 |
| `iteration` 主路径 | DB-03 |
| `custom` 主路径 | DB-04 |
| 缺少数据源 | DB-05 |
| 文件不存在 | DB-06 |
| 关键字段缺失/空值 | DB-07 |
| 禁止内部标识补查 | DB-08 |
| OR 条件解析 | DB-09 |
| AND 条件解析 | DB-10 |
| 三格式交付一致性 | DB-11 |
| L1/L2/L3 洞察治理 | DB-12 |

## 测试集概览

说明：`Happy Path` 表示主流程可用性验证，`Failure Path` 表示失败与拒绝路径验证，`Edge Case` 表示边界条件与解析稳定性验证，`Delivery & Governance` 表示交付一致性、洞察分级与治理要求验证。分类名称与 testcase 标签口径保持一致，因此保留英文写法。

| 类别 | 用例 |
| --- | --- |
| Happy Path | DB-01, DB-02, DB-03, DB-04 |
| Failure Path | DB-05, DB-06, DB-07, DB-08 |
| Edge Case | DB-09, DB-10 |
| Delivery & Governance | DB-11, DB-12 |

## 测试用例字段说明

| 字段 | 含义 |
| --- | --- |
| `tags` | 标记用例覆盖目标、场景类型与风险类别。常见标签包括 `Happy Path`、`Failure Path`、`Edge Case`、`three_format_delivery`、`intent_parsing` 等。 |
| `expected_output` | 定义理想输出行为、关键中间产物与最终交付物要求。 |
| `judge` | 定义用例通过条件与失败条件，是 testcase 可执行判定的核心依据。 |
| `fatal_errors` | 定义一旦出现即应直接判定失败的严重错误类型。 |
| `advanced_expected_outputs` / `advanced_checks` | 定义高标准增强项，用于评估实现完善度；缺失时优先表述为“实现不够完善”，不直接等同于核心逻辑错误。 |

## 提交说明

- 测试集共 12 条用例，覆盖主路径、失败路径、边界条件与红线场景。
- `db_report_testcases.yaml` 中区分了基线能力要求与高标准增强项，增强项缺失应优先表述为“实现不够完善”，不直接等同于核心逻辑错误。
- `db_report_test_report.html` 记录了当前新版 Skill 的真实运行结果，可用于对照 testcase 的可执行性与区分度。
