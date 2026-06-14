# Skill 评估项目一周计划（先 db_report，后 tracingclaw_finance）

## 一、整体目标
本项目的目标不是直接开发 Skill，而是为两个 Skill 设计一套可执行、可判分、覆盖全面的评估方案。

最终需要完成：

```text
submission.zip
├── db_report_eval.yaml
├── tracingclaw_finance_eval.yaml
└── README.md
```

每个 YAML 建议包含：

```text
1. ideal_state：理想状态
2. rubrics：评分规则
3. testcases：测试用例
4. meta_testcases：自检规则
5. coverage_matrix：覆盖矩阵
```

整体推进顺序：

```text
Day 1：读题 + 建模板
Day 2：db_report 逻辑链路
Day 3：db_report rubrics + testcases
Day 4：tracingclaw_finance 逻辑链路
Day 5：tracingclaw_finance rubrics
Day 6：tracingclaw_finance testcases
Day 7：meta-testcase + coverage_matrix + README + 打包
```

---

## 二、统一约束（Day 1 必须定下来）

### 1. 统一 YAML 顶层结构
两个 Skill 的 YAML 尽量保持同构：

```yaml
meta:
logic_chain:
ideal_state:
rubrics:
testcases:
meta_testcases:
coverage_matrix:
```

### 2. 统一 testcase 字段
每条 testcase 固定使用：

```yaml
id:
title:
tags:
input:
expected_output:
judge:
fatal_errors:
```

### 3. 统一 judge 写法
建议统一成：

```yaml
judge:
  pass_if_all: []
  fail_if_any: []
```

### 4. 统一 tags 命名风格
建议只使用可复用标签：

```text
happy_path
failure_path
edge_case
redline
local_file
json
comparison
iteration
custom
routing
scoring
```

### 5. 统一 coverage_matrix 维度
建议两个 Skill 都至少覆盖：

```text
1. task_types / report_types
2. data_sources
3. risk_types
4. path_types
5. fatal_errors
```

### 6. 统一 README 提纲
最终 README 建议包含：

```text
1. 项目目标
2. 提交目录结构
3. 两个 YAML 的内容说明
4. ideal_state / rubrics / testcases / meta_testcases / coverage_matrix 的含义
5. 评估设计原则
```

---

## Day 1：读题 + 搭整体框架

### 目标
明确这个项目到底要交什么，统一结构和命名规则，先不要急着写具体测试用例。

### 要做的事情
1. 阅读总 README 和考题要求。
2. 明确本项目是做 Skill 评估，不是开发 Skill。
3. 明确两个目标 Skill：
   - `db_report`
   - `tracingclaw_finance`
4. 搭建最终提交目录。
5. 建立两个 YAML 的统一模板。
6. 确定 testcase 字段、judge 写法、tags 风格。
7. 先搭 README 提纲。
8. 建立两个 Skill 的工作清单。

### 需要理解的核心概念

```text
ideal_state：满分 Skill 应该是什么样
rubrics：怎么评分、怎么扣分
testcases：用什么输入去测试 Skill
meta_testcases：检查自己的测试集是否合格
coverage_matrix：证明测试覆盖全面
```

### 当天产出

```text
1. 项目总链路
2. YAML 基础模板
3. README 提纲
4. db_report 工作清单
5. tracingclaw_finance 工作清单
6. 统一字段命名规则
```

### 完成判定
- 两个 Skill 的 YAML 顶层结构已经统一。
- testcase 和 judge 字段写法已经固定。
- 已经明确最终提交物是两个 YAML 加一个 README。
- 不再把这项任务误解成 Skill 开发任务。

---

## Day 2：专攻 db_report 逻辑链路

### 目标
完整理解 `db_report` 是做什么的、输入输出是什么、数据源和红线是什么。

### 重点阅读

```text
db_report/readme.md
db_report/SKILL.md
db_report/references/*
db_report/test-resource/*
```

### 要梳理的问题
1. `db_report` 是什么？
2. 它的输入是什么？
3. 它的输出是什么？
4. 它支持哪些数据源？
5. 它支持哪些报告类型？
6. `single / comparison / iteration / custom` 有什么区别？
7. 缺少数据时应该怎么办？
8. 哪些行为是禁止的？
9. 数据质量门控怎么做？
10. 哪些内容适合进入 `coverage_matrix`？

### db_report 重点链路

```text
用户请求
    → 识别数据源
    → 识别报告类型
    → 解析本地 log/json/csv/xlsx/粘贴 JSON
    → 做数据质量门控
    → 生成性能分析
    → 输出 md/docx/html 报告
```

### 当天产出

```text
1. db_report 完整逻辑链路
2. db_report ideal_state 初稿
3. db_report 数据源规则
4. db_report 红线规则
5. db_report coverage_matrix 初稿
```

### 完成判定
- 能用自己的话讲清 db_report 的完整执行流程。
- 能区分四类报告类型。
- 已经列出数据源边界和关键红线。
- ideal_state 不再是空模板。

---

## Day 3：完成 db_report rubrics + testcases

### 目标
把 `db_report` 先做成一个完整样板。

### rubrics 建议结构

```text
总分：100 分
1. 数据源与边界控制：20 分
2. 报告类型识别：15 分
3. 数据解析与质量门控：20 分
4. 分析逻辑与报告结构：20 分
5. md/docx/html 三格式交付：15 分
6. 红线约束：10 分
```

### db_report 重点红线

```text
1. 不得编造 TPS/QPS/P95/P99
2. 不得调用内部数据库或内部 API
3. 不得用 task_id/report_id 查询线上数据
4. 缺数据时不能生成正式报告
5. 字段缺失或空值时必须停止或说明问题
6. 不得跳过数据质量门控
```

### 建议 testcases
至少 10 条，推荐 12 条：

```text
DB-01 本地 log 单次报告
DB-02 records JSON 对比报告
DB-03 iteration 历史趋势报告
DB-04 custom 专项分析
DB-05 缺少数据源时拒绝
DB-06 文件不存在
DB-07 字段缺失或空值
DB-08 禁止 task_id/report_id 查询
DB-09 OR 条件解析
DB-10 AND 条件解析
DB-11 md/docx/html 三格式交付
DB-12 L1/L2/L3 洞察位置检查
```

### 每条 testcase 建议字段

```yaml
id:
title:
tags:
input:
expected_output:
judge:
fatal_errors:
```

### 当天产出

```text
1. db_report_eval.yaml 初稿
2. db_report coverage_matrix
```

### 完成判定
- rubrics 权重合计 100。
- testcase 不少于 10 条，最好达到 12 条。
- 已覆盖 happy path、failure path、edge case、redline。
- judge 不出现“输出合理”“内容完整”这类模糊表述。

---

## Day 4：开始 tracingclaw_finance，先梳理链路

### 目标
完整理解 `tracingclaw_finance` 是什么，以及它和 AFC 项目的关系。

### 重点阅读

```text
tracingclaw_finance/readme.md
tracingclaw_finance/SKILL.md
westock-data/SKILL.md
mx-finance-search/SKILL.md
```

### 要梳理的问题
1. `tracingclaw_finance` 是什么？
2. 输入是什么？
3. 输出是什么？
4. 0/1/2 怎么判？
5. `westock-data` 查什么？
6. `mx-finance-search` 查什么？
7. 哪些属于核心事实错误？
8. 哪些属于次要事实错误？
9. 数据不足时应该怎么办？
10. coverage_matrix 应该怎么映射金融任务类型？

### tracingclaw_finance 重点链路

```text
用户给金融问题 / 候选回答
    → 识别金融任务类型
    → 拆解可核验事实
    → 选择数据源 / 工具
        财报、行情、资金、技术指标 → westock-data
        公告、新闻、研报、政策 → mx-finance-search
    → 核验证据
    → 判断 0/1/2
    → 输出理由和修正答案
```

### 当天产出

```text
1. tracingclaw_finance 逻辑链路
2. finance ideal_state 初稿
3. finance 数据源规则
4. 0/1/2 判分框架
5. finance coverage_matrix 初稿
```

### 完成判定
- 能清楚说明两个数据源工具各自负责什么。
- 能讲清 0/1/2 评分的基本边界。
- 能列出金融核验的核心风险类型。

---

## Day 5：完成 tracingclaw_finance rubrics

### 目标
把金融 Skill 的评分规则写细，尤其是金融口径和工具路由。

### rubrics 建议结构

```text
总分：100 分
1. 输入识别与核验点拆解：15 分
2. 工具路由与数据源使用：20 分
3. 金融口径一致性：20 分
4. 0/1/2 评分准确性：20 分
5. 修正答案质量：15 分
6. 红线约束：10 分
```

### 金融 Skill 重点红线

```text
1. 编造财报数据
2. 编造股价、涨跌幅、成交额等行情数据
3. 把新闻观点当成已发生事实
4. 混用 A 股、港股、美股市场
5. 混用人民币、港元、美元
6. 混用财年、自然年、季度、累计值
7. 工具查不到时强行给确定结论
8. 跳过 westock-data 或 mx-finance-search 的规定数据源
```

### 0/1/2 判分建议

```text
0：核心事实错误，例如财报核心数字错、行情方向错、公告是否存在判断错、股票对象错
1：主需求基本正确，但存在次要事实错误或口径不完整，例如单位、币种、来源说明有轻微问题
2：主次事实均正确，数据源、口径、时间、市场、币种说明清楚
```

### 当天产出

```text
1. tracingclaw_finance_eval.yaml 中的 ideal_state + rubrics
2. finance coverage_matrix 更新版
```

### 完成判定
- rubrics 能支持 0/1/2 的稳定判分。
- 工具路由和金融口径已经落成可判定规则。
- 红线不再只是口号，而是能写进 judge 的具体条件。

---

## Day 6：完成 tracingclaw_finance testcases

### 目标
完成金融 Skill 的测试用例，覆盖正常路径、失败路径、边界条件和红线违规。

### 建议 testcases
至少 10 条，推荐 12 条：

```text
FIN-01 财报核心数字错误
FIN-02 行情涨跌幅核查
FIN-03 公告是否存在核查
FIN-04 研报观点与事实区分
FIN-05 股票名称/代码正义
FIN-06 A 股/港股/美股市场混淆
FIN-07 人民币/港元/美元币种混淆
FIN-08 财年/自然年/季度口径混淆
FIN-09 内部链接拒绝
FIN-10 工具查不到时不得编造
FIN-11 技术指标周期口径
FIN-12 资金流日期口径
```

### 每条 testcase 建议字段

```yaml
id:
title:
tags:
input:
expected_output:
judge:
fatal_errors:
```

### 当天产出

```text
1. tracingclaw_finance_eval.yaml 初稿
2. finance coverage_matrix
```

### 完成判定
- testcase 不少于 10 条，最好达到 12 条。
- 已覆盖 happy path、failure path、edge case、redline。
- 至少有 1 组用例直接检验 0/1/2 评分边界。

---

## Day 7：统一整理 + meta-testcase + README + 打包

### 目标
把两个 Skill 的 YAML 变成最终提交版本。

### 要检查的内容

```text
1. 两个 YAML 结构是否统一
2. rubrics 权重是否都是 100
3. 每个 Skill 是否不少于 5 条 testcase
4. 是否覆盖 happy path
5. 是否覆盖 failure path
6. 是否覆盖 edge case
7. 是否覆盖 redline
8. judge 是否具体可判定
9. expected_output 是否明确
10. 是否存在重复用例
11. 是否存在“输出合理”“内容完整”这类模糊标准
12. coverage_matrix 是否能支撑你证明覆盖范围
13. README 是否能解释整个提交结构
```

### meta-testcase 要覆盖

```text
META-01 测试用例数量检查
META-02 happy path 覆盖检查
META-03 failure path 覆盖检查
META-04 edge case 覆盖检查
META-05 redline 覆盖检查
META-06 judge 可判定性检查
META-07 rubrics 权重检查
META-08 expected_output 明确性检查
META-09 重复用例检查
META-10 数据源约束覆盖检查
```

### coverage_matrix 建议覆盖

```text
1. report_types / finance_task_types
2. data_sources
3. risk_types
4. path_types
5. fatal_errors
```

### 最终提交结果

```text
submission.zip
├── db_report_eval.yaml
├── tracingclaw_finance_eval.yaml
└── README.md
```

### 完成判定
- 两个 YAML 都能独立阅读和使用。
- README 已补齐。
- meta_testcases 和 coverage_matrix 都不缺席。
- 提交目录完整可打包。

---

## 最终节奏总结

```text
Day 1：读题 + 建模板
Day 2：db_report 逻辑链路
Day 3：db_report rubrics + testcases
Day 4：finance 逻辑链路
Day 5：finance rubrics
Day 6：finance testcases
Day 7：meta-testcase + coverage_matrix + README + 打包
```

---

## 执行建议
1. 不要两个 Skill 同时写，先把 `db_report` 做成样板。
2. `db_report` 做完后，把结构复制到 `tracingclaw_finance`，再替换成金融核查内容。
3. 每条 testcase 都要具体，避免写“输出合理”“分析完整”。
4. 多设计失败路径和红线场景，这比只写正常路径更能体现评估能力。
5. `coverage_matrix` 不要等到最后一天才想，从 Day 2 开始同步记录。
6. Day 7 只做汇总、检查和打包，尽量不要在 Day 7 才重写主体内容。
