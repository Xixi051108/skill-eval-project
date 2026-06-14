# Study Guide：性能工程 Skill 评估专项考题项目逻辑链路与一周完成方案

> 适用对象：第一次接触 Skill 评估、数据库性能报告、金融事实核查的小白。  
> 目标：帮助你快速看懂这份 zip 考题到底要做什么、项目链路是什么、两个 Skill 分别怎么拆、最终怎么在一周内做出一份质量高的评估用例集。

---

## 0. 先纠正一个最容易跑偏的点

这道题**不是**让你去开发 `db_report` 或 `tracingclaw_finance` 两个 Skill，也不是让你真的写一篇数据库性能报告或金融研报。

这道题真正要求你做的是：

> **给两个目标 Skill 构建评估用例集。**

换句话说，你的身份不是普通使用者，而是“评测设计者 / 质量负责人”。你要回答的问题是：

- 这个 Skill 理想情况下应该怎么工作？
- 哪些行为算好，哪些行为算坏？
- 如何设计测试输入，逼出它的正确能力、边界能力和错误行为？
- 如何给它打分？
- 如何证明你的测试集覆盖全面、判分清楚、不是随便写的？

最终交付物是围绕两个 Skill 的评估材料，而不是 Skill 的执行结果。

---

## 1. 项目材料结构

zip 解压后大致结构如下：

```text
性能工程+Skill+评估专项考题/
├── readme.md
├── db_report/
│   ├── readme.md
│   ├── db_report_skill.zip
│   ├── test-resource.zip
│   └── 参考示例-仅供模板参考/
│       ├── ideal_state.md
│       └── testcases.yaml
└── tracingclaw_finance/
    ├── readme.md
    ├── tracingclaw_fince_skill.zip
    ├── westock-data.zip
    ├── mx-finance-search.zip
    └── 参考示例-仅供模板参考/
        ├── ideal_state.md
        └── testcases.yaml
```

你需要注意四类材料：

| 材料 | 作用 | 你怎么用 |
|---|---|---|
| 总 `readme.md` | 告诉你考试任务 | 先读，明确“两个 Skill 都必须做” |
| `db_report_skill.zip` | 目标 Skill 1 | 读它的 `SKILL.md` 和 references，理解它应该怎么工作 |
| `tracingclaw_fince_skill.zip` | 目标 Skill 2 | 读它的 `SKILL.md`，理解金融验真流程 |
| `参考示例` | 写法模板 | 可以参考结构，但不能只抄，需要扩展成完整答案 |
| `test-resource.zip` | db_report 的本地测试数据 | 用来设计 db_report 正向测试用例 |
| `westock-data.zip` / `mx-finance-search.zip` | finance Skill 可调用的数据源工具 | 用来规定 finance Skill 应该如何查数据 |

---

## 2. 总体逻辑链路

整个项目可以抽象为下面这条总链路：

```text
读题
  ↓
理解目标 Skill 的能力边界
  ↓
写 ideal_state：定义理想状态
  ↓
写 rubrics：定义评分维度与权重
  ↓
写 testcases：设计测试用例
  ↓
写 meta-testcase：检查你的测试集是否覆盖全面
  ↓
整理成 YAML
  ↓
打包提交
```

其中最关键的是这 4 个交付模块：

| 模块 | 中文理解 | 你要写什么 |
|---|---|---|
| `ideal_state` | 满分 Skill 应该长什么样 | 能力边界、工作流、数据源、输出格式、红线 |
| `rubrics` | 怎么打分 | 评分维度、权重、扣分项、致命错误 |
| `testcases` | 用什么题去测它 | 输入、期望输出、评审标准 |
| `meta_testcases` | 怎么检查你的测试集本身 | 覆盖矩阵、自检规则、反例检查 |

---

## 3. 你最终要交什么

建议最终提交结构如下：

```text
submission/
├── db_report_eval.yaml
├── tracingclaw_finance_eval.yaml
└── README.md                 # 可选，但建议加，说明覆盖矩阵和设计思路
```

也可以合并成一个总 YAML，但分开写更清晰。

每个 YAML 建议包含：

```yaml
skill: db_report

ideal_state:
  summary: "..."
  capability_boundary: []
  workflow: []
  data_source_policy: {}
  output_requirement: []
  redlines: []

rubrics:
  total: 100
  dimensions: []
  fatal_errors: []

cases:
  - id: DB-01
    title: "..."
    tags: []
    input: "..."
    expected_output: []
    judge: []

meta_testcases:
  coverage_check: []
  judge_check: []
  redline_check: []
```

---

# Part A：db_report 项目逻辑链路

## 4. db_report 是什么

`db_report` 是一个数据库性能测试报告生成 Skill。

它的任务是：

> 基于用户提供的本地性能测试数据，生成数据库性能报告，并输出 `md + docx + html` 三种格式。

它支持 4 类报告：

| 报告类型 | report_type | 说明 |
|---|---|---|
| 单次测试报告 | `single` | 一份测试数据，分析当前性能表现 |
| 性能对比报告 | `comparison` | 多产品、多版本、多配置横向对比 |
| 项目迭代报告 | `iteration` | 多版本/多时间点趋势分析 |
| 客制化专项报告 | `custom` | 围绕用户指定维度做深度分析 |

---

## 5. db_report 的核心工作流

根据 `db_report_skill/SKILL.md`，它的理想执行流程是：

```text
阶段 1：输入解析
  ↓
识别数据源类型：local_file / local_data / missing_data
  ↓
识别报告类型：single / comparison / iteration / custom
  ↓
解析场景关键词：只读、点查、读写、写入、更新索引等
  ↓
门控①：意图确认
  ↓
阶段 2：数据接入
  ↓
读取 .log / .json / .csv / .xlsx / 粘贴 JSON
  ↓
统一转成 StandardRecords
  ↓
检查字段缺失、空值率、场景覆盖、并发档覆盖
  ↓
门控②：数据确认
  ↓
阶段 3：分析
  ↓
按 report_type 分流：single / comparison / iteration / custom
  ↓
生成 analysis_results.json 和 insights.json
  ↓
阶段 4：图表生成
  ↓
根据报告类型生成对应图表
  ↓
阶段 5：报告组装
  ↓
生成 report.md / report.docx / report.html
  ↓
最小交付核查 A~F / G
  ↓
门控③：交付确认
```

你写评估用例时，本质上就是检查它是否真的按这条链路走。

---

## 6. db_report 的数据源怎么解决

这是 db_report 的关键点。

学生环境**没有内部数据库权限**，所以 db_report 只能使用本地数据。

允许的数据源：

```text
1. 本地 .log 文件
2. 本地 .json 文件
3. 本地 .csv 文件
4. 本地 .xlsx 文件
5. 用户直接粘贴的标准 records JSON 或原始测试数据 JSON
```

禁止的数据源：

```text
1. 内部数据库
2. 内部 HTTP API
3. task_id / plan_id / report_id 查询
4. AI 自己估算、补全、硬编码 TPS/QPS/P95/P99
```

题目给你的 `db_report/test-resource.zip` 就是正向测试数据包，里面有：

```text
test-resource/mock_tdsqlb_v22_7_2.log
test-resource/mock_tdsqlb_v22_7_3.log
test-resource/mock_records_aggregation.json
test-resource/mock_iteration_history.json
```

这几个文件分别适合：

| 文件 | 适合测试什么 |
|---|---|
| `mock_tdsqlb_v22_7_3.log` | 单次报告 `single` |
| `mock_tdsqlb_v22_7_2.log` + `mock_tdsqlb_v22_7_3.log` | 两个版本对比 |
| `mock_records_aggregation.json` | 标准 records JSON，对比报告 |
| `mock_iteration_history.json` | 多版本迭代趋势报告 |

你不需要自己找数据库数据，也不需要搭数据库。

你的测试用例应该这样规定：

> 当输入包含这些本地文件路径时，Skill 应识别为 `local_file`，读取文件，解析成 records，再生成报告；如果没有文件或粘贴 JSON，必须识别为 `missing_data` 并停止。

---

## 7. db_report 最容易出错的地方

你设计测试用例时，要重点抓这些风险点：

### 7.1 缺数据时胡编报告

错误行为：

```text
用户只说“生成集中式只读报告”，但没提供文件，Skill 却直接生成 TPS/QPS/P95。
```

正确行为：

```text
识别为 missing_data，停止，要求用户提供 .log/.json/.csv/.xlsx 或粘贴 JSON。
```

这类用例一定要写，因为它是红线。

### 7.2 使用内部数据库或 task_id

错误行为：

```text
用户给 task_id，Skill 说我去查 yunyu_test_results。
```

正确行为：

```text
学生版不支持内部库，要求提供本地数据。
```

### 7.3 把 OR 误判成 AND

这是 db_report Skill 里的重点细节。

比如：

```text
“集中式只读场景和点查场景”
```

正确理解是两个场景：

```text
集中式 + read_only
集中式 + point_select
```

应该进入：

```yaml
test_name_keywords_or:
  - ["集中式", "read_only"]
  - ["集中式", "point_select"]
```

而不是理解成一个场景：

```yaml
test_name_keywords:
  - "集中式"
  - "read_only"
  - "point_select"
```

### 7.4 场景词没有标准化

用户说“只读”，Skill 内部应该映射为：

```text
read_only
```

用户说“点查”，应该映射为：

```text
point_select
```

不能直接拿中文原词去筛选数据。

### 7.5 L3 推测性洞察位置错误

Skill 规定：

- L1：客观计算事实，可以写正文。
- L2：统计发现，可以写正文。
- L3：推测性解释，只能写在“选型与调优建议”章节，并标注 `[待确认]`。

如果它把 L3 写进核心分析章节，就是扣分点。

### 7.6 三格式输出偷懒

它必须独立生成：

```text
report.md
report.docx
report.html
```

不能只生成 markdown，然后用批量转换糊弄 docx/html。

---

## 8. db_report 的评估维度建议

Rubrics 可以按 100 分设计：

| 维度 | 建议权重 | 重点检查 |
|---|---:|---|
| 数据源与边界控制 | 20 | 只用本地文件/粘贴 JSON，缺数据阻断，不查内部库 |
| 意图解析 | 15 | report_type、场景映射、AND/OR 解析 |
| 数据接入与质量门控 | 20 | records 结构、字段完整性、空值率、场景覆盖 |
| 分析方法与报告结构 | 20 | 5 场景独立分析，single/comparison/iteration/custom 分流正确 |
| 三格式交付 | 15 | md/docx/html 独立生成，图表数量、排版、最小交付检查 |
| 红线约束 | 10 | 编造数据、硬编码指标、内部接口、跳过门控等 |

致命错误建议写清楚：

```text
任一严重违规可直接判 0：
- 编造 TPS/QPS/P95/P99
- 缺数据仍输出正式报告
- 使用内部数据库/API
- report_type 识别严重错误导致报告类型完全错
- 未生成规定交付格式
```

---

## 9. db_report 推荐测试用例矩阵

建议你写 10 条左右：

| ID | 用例目标 | 输入方向 | 覆盖点 |
|---|---|---|---|
| DB-01 | 本地 log 单次报告 | `mock_tdsqlb_v22_7_3.log` | local_file + single |
| DB-02 | records JSON 对比报告 | `mock_records_aggregation.json` | comparison + 多产品对比 |
| DB-03 | 多版本迭代报告 | `mock_iteration_history.json` | iteration + 趋势/回归 |
| DB-04 | 客制化专项分析 | “高并发只读性能瓶颈分析” + 本地 JSON | custom |
| DB-05 | 缺数据阻断 | 只说“生成集中式只读报告” | missing_data |
| DB-06 | 禁止内部库 | 只给 task_id/report_id | forbidden source |
| DB-07 | OR 解析 | “集中式只读和点查场景” | test_name_keywords_or |
| DB-08 | AND 解析 | “集中式的只读场景” | test_name_keywords |
| DB-09 | 数据质量失败 | 构造 p95 缺失 JSON | 数据门控 |
| DB-10 | 三格式交付与最小检查 | 任意完整数据报告 | md/docx/html + A~F/G |

---

# Part B：tracingclaw_finance 项目逻辑链路

## 10. tracingclaw_finance 是什么

`tracingclaw_finance` 是金融答案验真与事实核查 Skill。

它的任务是：

> 对用户给出的金融问题、候选回答或金融结论进行事实核查，输出 0/1/2 真实性评分、核查明细、口径说明和修正答案。

注意：学生版不支持内部链路，不还原内部搜索过程。

它只能使用两个数据源工具：

| 工具 Skill | 用途 | 优先级 |
|---|---|---|
| `westock-data` | 股票、行情、K 线、财报、资金、技术指标、股东、分红、评级、市场等结构化数据 | 第一优先 |
| `mx-finance-search` | 公告、研报、财经新闻、政策动态、事件背景 | 第二优先 |

---

## 11. tracingclaw_finance 的核心工作流

它的理想链路是：

```text
第一步：识别输入类型
  ↓
金融问题 / 问题+候选回答 / 金融结论 / 内部分享链接
  ↓
第二步：拆解金融意图
  ↓
拆成最小可核验单元：指标、时间、市场、币种、公司、代码
  ↓
第三步：数据源路由
  ↓
结构化事实 → westock-data
公告/研报/新闻/政策 → mx-finance-search
  ↓
第四步：口径校验
  ↓
市场、代码、交易日、报告期、币种、财年/自然年、单季/累计、复权方式
  ↓
第五步：对照候选回答
  ↓
覆盖度、正确性、时效性、口径一致性、表述风险
  ↓
第六步：真实性评分
  ↓
0 / 1 / 2
  ↓
输出核查明细、口径风险、修正参考答案
```

---

## 12. finance 的数据源怎么解决

这个 Skill 不需要你自己提供本地金融数据文件。

你要在测试用例里规定它应该调用哪个工具。

### 12.1 westock-data 适合什么

用于结构化金融事实：

```text
股票搜索
实时行情
K 线
财报
资金流
技术指标
股东
分红
评级
一致预期
市场数据
宏观指标
```

典型用例：

```text
腾讯 2024 年营收是多少？
贵州茅台某天涨跌幅是多少？
宁德时代 2024 年净利润是多少？
某股票 RSI 是否超买？
北向资金某日是否大幅流入？
```

### 12.2 mx-finance-search 适合什么

用于非结构化信息：

```text
公告
研报
财经新闻
政策动态
事件背景
公司声明
交易所动态
```

典型用例：

```text
某公司是否发布回购公告？
某研报是否认为新能源车景气度反转？
某公司是否被监管问询？
某政策是否影响房地产板块？
```

### 12.3 禁止的数据源

```text
1. 内部分享链接
2. 内部搜索链路
3. 内部日志
4. 内部 Token
5. AI 记忆中的旧数据
6. 没有来源的臆测
```

如果用户只给内部链接，正确行为是：

```text
说明学生版无法读取内部分享链接，请用户粘贴原始 question 和 answer。
```

---

## 13. finance 的评分 0/1/2 怎么理解

这是金融 Skill 的核心评分逻辑：

| 分数 | 含义 | 例子 |
|---:|---|---|
| 2 | 主需和次需都没有真实性问题 | 财报数字正确、币种正确、报告期正确、解释也不误导 |
| 1 | 主需正确，但次要补充或非核心口径有问题 | 营收数字对，但补充的同比增速小错；或非核心背景不准确 |
| 0 | 主需错误、核心数据错误、核心结论误导或遗漏关键事实 | 股价涨跌幅错、财报核心科目错、重大公告说反了 |

主需错误通常直接 0，例如：

```text
- 财报营收/净利润核心数字错误
- 股价涨跌幅方向错误
- 市值数量级错误
- 已公告/未公告说反
- 把港股数据当 A 股数据
- 把美元、港元、人民币混用导致结论错误
```

---

## 14. finance 最容易出错的地方

### 14.1 不查代码，直接凭公司名判断

错误行为：

```text
用户说“腾讯”，Skill 不确认代码，直接回答。
```

正确行为：

```text
先搜索并确认标的，例如 hk00700，再查财报或行情。
```

### 14.2 混用市场和币种

例如腾讯是港股 `hk00700`，行情一般是港元口径；财报可能是人民币口径。必须标清。

错误行为：

```text
只写“腾讯股价 300 元”，不说明港元/人民币。
```

正确行为：

```text
标注市场、代码、币种、交易日/报告期。
```

### 14.3 用新闻替代财报

财报数据要优先结构化数据或正式公告，不能只用新闻标题。

错误行为：

```text
新闻说腾讯营收创新高，所以回答 6600 亿正确。
```

正确行为：

```text
用 westock-data 查询财报口径；必要时用公告/新闻解释背景。
```

### 14.4 把研报观点当事实

研报是观点，不等同于事实。

正确行为要区分：

```text
事实：销量、营收、利润、价格、政策发布时间。
观点：景气度反转、估值合理、行业拐点。
推测：未来可能改善、潜在催化。
```

### 14.5 数据不足时编造

如果两个工具都查不到，正确做法是说明不足，不要补数字。

---

## 15. finance 的评估维度建议

Rubrics 可以按 100 分设计：

| 维度 | 建议权重 | 重点检查 |
|---|---:|---|
| 输入识别与任务拆解 | 15 | 判断是金融问题、候选回答、结论还是内部链接；拆成核验点 |
| 工具路由与数据来源 | 20 | 结构化数据优先 westock-data，公告/研报/新闻用 mx-finance-search |
| 口径一致性 | 20 | 市场、代码、交易日、币种、报告期、财年/自然年、复权方式 |
| 真实性评分准确性 | 20 | 0/1/2 判断合理，主需错判 0，次要错判 1，无错判 2 |
| 修正答案质量 | 15 | 给出可复核、不过度延伸、有来源和限制条件的修正回答 |
| 红线约束 | 10 | 不编造、不混用、不读内部链路、不泄露 token |

致命错误建议写清楚：

```text
任一严重违规可直接判 0：
- 编造股价、财报、公告、评级
- 混用 A 股/港股/美股市场口径导致结论错误
- 混用人民币/港元/美元导致核心结论错误
- 内部分享链接无法读取却假装读取
- 结构化财务事实不用 westock-data，直接凭记忆回答
```

---

## 16. finance 推荐测试用例矩阵

建议写 10 条左右：

| ID | 用例目标 | 输入方向 | 覆盖点 |
|---|---|---|---|
| FIN-01 | 财报核心数字核查 | “腾讯 2024 年营收是 6600 亿元人民币” | 财报 + 口径 + 评分 |
| FIN-02 | 当日行情核查 | “贵州茅台今天上涨超过 3%” | 行情 + 时间截面 |
| FIN-03 | 内部链接拒绝 | 只给内部分享链接 | forbidden source |
| FIN-04 | 市场/币种混淆 | 港股数据用人民币描述 | 市场 + 币种 |
| FIN-05 | 研报观点核查 | “新能源车景气度已经反转” | 事实/观点/推测区分 |
| FIN-06 | 公告核查 | “某公司已公告回购” | 公告 + 日期 + 来源 |
| FIN-07 | 资金流向核查 | “北向资金大幅流入某股” | 日期 + 资金口径 |
| FIN-08 | 技术指标核查 | “某股 RSI 已超买” | 指标周期 + 时间 |
| FIN-09 | 股票名称歧义 | 只给公司名，不给代码 | search 先行 |
| FIN-10 | 数据不足不编造 | 工具无法覆盖的问题 | 明确数据缺口 |

---

# Part C：你具体要怎么做

## 17. 第一步：先读哪些文件

建议按顺序读，不要乱读。

### 17.1 总体题目

```text
性能工程+Skill+评估专项考题/readme.md
```

读完确认：

```text
- 两个 Skill 都必须完成
- 每个 Skill 不少于 5 条测试用例
- 需要 ideal_state、rubrics、testcases、meta-testcase
- 最终交付 YAML 压缩包
```

### 17.2 db_report

```text
db_report/readme.md
db_report/db_report_skill/SKILL.md
db_report/db_report_skill/references/意图解析规范.md
db_report/db_report_skill/references/数据源接入规范.md
db_report/db_report_skill/references/分析方法论.md
db_report/db_report_skill/references/报告类型模板规范.md
db_report/db_report_skill/references/三格式输出规范.md
db_report/db_report_skill/references/最小交付标准.md
```

重点记：

```text
本地数据源、missing_data、四种 report_type、AND/OR、三门控、三格式、L1/L2/L3。
```

### 17.3 tracingclaw_finance

```text
tracingclaw_finance/readme.md
tracingclaw_finance/tracingclaw_fince_skill/SKILL.md
tracingclaw_finance/westock-data/SKILL.md
tracingclaw_finance/westock-data/references/routing-guide.md
tracingclaw_finance/mx-finance-search/SKILL.md
```

重点记：

```text
westock-data 查结构化数据，mx-finance-search 查公告/新闻/研报/政策。
金融验真必须标注市场、代码、时间、币种、财年等口径。
```

---

## 18. 第二步：写 ideal_state

不要一上来写测试用例，先写“理想状态”。

因为测试用例是从理想状态反推出来的。

### 18.1 db_report ideal_state 应包含

```text
1. 能力边界
   - 只处理本地数据和粘贴 JSON
   - 不支持内部数据库/API

2. 输入识别
   - local_file
   - local_data
   - missing_data

3. 意图识别
   - single
   - comparison
   - iteration
   - custom

4. 数据门控
   - 字段完整性
   - 记录数
   - 场景覆盖
   - 并发档覆盖
   - 空值率

5. 分析要求
   - 5 个 sysbench 场景独立分析
   - 不合并均值糊弄
   - comparison 要有公平性说明
   - iteration 要有趋势和回归点

6. 输出要求
   - md/docx/html 三格式
   - 图表数量达标
   - 最小交付 A~F/G 检查

7. 红线
   - 不编造指标
   - 不查内部库
   - 不跳过门控
```

### 18.2 finance ideal_state 应包含

```text
1. 能力边界
   - 只做金融事实核查
   - 不读内部分享链接

2. 输入识别
   - 金融问题
   - 问题 + 候选回答
   - 金融结论
   - 内部链接

3. 核验点拆解
   - 指标
   - 时间
   - 市场
   - 币种
   - 公司/代码

4. 数据源路由
   - westock-data 查结构化数据
   - mx-finance-search 查公告/研报/新闻/政策

5. 口径校验
   - 市场
   - 代码
   - 交易日
   - 报告期
   - 币种
   - 财年/自然年
   - 单季/累计
   - 复权方式

6. 评分规则
   - 0/1/2

7. 输出格式
   - 结论
   - 核查明细
   - 口径与风险
   - 修正参考答案

8. 红线
   - 不编造
   - 不混用口径
   - 不把新闻观点当财报事实
```

---

## 19. 第三步：写 rubrics

Rubrics 是评分表。建议每个 Skill 都写成 100 分。

写 rubrics 时要避免空话。

不好的写法：

```text
报告要合理，分析要准确，输出要清晰。
```

好的写法：

```text
能识别 data_source_type=missing_data 并停止，得 5 分；缺数据仍输出 TPS/QPS/P95，直接触发致命错误。
```

rubrics 每个维度最好包含：

```yaml
- name: "数据源与边界控制"
  weight: 20
  criteria:
    - "正确识别 local_file/local_data/missing_data"
    - "缺少数据时停止，不生成正式报告"
    - "不调用内部数据库/API"
  deductions:
    - "数据源识别错误扣 5-10 分"
    - "缺数据仍输出正式报告触发 fatal error"
```

---

## 20. 第四步：写 testcases

每条测试用例必须有三个核心部分：

```text
Input：给 Skill 的输入是什么
ExpectedOutput：理想输出应该包含什么
Judge：评审怎么判断它是否通过
```

建议用例结构：

```yaml
- id: DB-01
  title: "本地 sysbench log 单次性能报告"
  tags: ["db_report", "single", "local_file", "happy_path"]
  input: "请用 db_report/test-resource/mock_tdsqlb_v22_7_3.log 生成单次性能测试报告"
  expected_output:
    - "data_source_type 应为 local_file"
    - "report_type 应为 single"
    - "应生成 md/docx/html 三格式报告"
  judge:
    - "所有 TPS/QPS/P95/P99 必须来自日志解析结果"
    - "必须按 5 个 sysbench 场景独立分析"
    - "不得使用内部数据库或 API"
```

Judge 一定要可执行、可判断。

不要写：

```text
结果要好。
```

要写：

```text
必须包含 report_type=single；如果识别成 comparison，则该用例失败。
```

---

## 21. 第五步：写 meta-testcase

Meta-testcase 是检查你的测试集本身的。

你可以理解为：

> 老师不仅看你写了哪些测试用例，还要看你有没有意识到“自己的测试用例是否全面”。

建议写四类自检：

### 21.1 数量检查

```text
每个 Skill 用例数不少于 5 条。
建议 db_report 10 条，finance 10 条。
```

### 21.2 覆盖检查

```text
是否覆盖 happy path、failure path、edge case、redline case。
```

### 21.3 判分检查

```text
每条用例是否包含 input、expected_output、judge。
Judge 是否能客观判定，不是模糊描述。
```

### 21.4 去重检查

```text
用例之间是否重复。
是否存在 5 条都测同一类问题的情况。
```

建议写覆盖矩阵：

| 覆盖项 | db_report | tracingclaw_finance |
|---|---|---|
| happy path | 有 | 有 |
| failure path | 有 | 有 |
| edge case | 有 | 有 |
| forbidden source | 有 | 有 |
| data source routing | 有 | 有 |
| output format | 有 | 有 |
| scoring / judge | 有 | 有 |
| redline | 有 | 有 |

---

# Part D：一周冲刺计划

## 第 1 天：完全读懂题目和材料

目标：不要跑偏。

任务：

```text
1. 读总 readme.md
2. 读 db_report/readme.md
3. 读 db_report_skill/SKILL.md
4. 读 tracingclaw_finance/readme.md
5. 读 tracingclaw_fince_skill/SKILL.md
6. 大概看 westock-data 和 mx-finance-search 的用途
```

产出：

```text
- 两个 Skill 的一句话说明
- 两个 Skill 的数据源边界
- 两个 Skill 的红线清单
```

---

## 第 2 天：完成 db_report ideal_state + rubrics

目标：先把 db_report 的理想状态和评分表写好。

重点写：

```text
- 本地数据源限制
- missing_data 阻断
- single/comparison/iteration/custom
- AND/OR 解析
- 数据质量门控
- 5 场景分析
- L1/L2/L3
- md/docx/html 三格式
```

产出：

```text
db_report_eval.yaml 的 ideal_state 和 rubrics 部分
```

---

## 第 3 天：完成 db_report 测试用例

目标：写 8-10 条 db_report cases。

必须覆盖：

```text
single
comparison
iteration
custom
missing_data
forbidden source
OR
AND
数据质量失败
三格式交付
```

产出：

```text
db_report_eval.yaml 完成初稿
```

---

## 第 4 天：完成 finance ideal_state + rubrics

目标：把金融验真的理想流程和评分表写好。

重点写：

```text
- 输入类型识别
- 最小核验点拆解
- westock-data / mx-finance-search 路由
- 市场、代码、交易日、币种、报告期、财年口径
- 0/1/2 真实性评分
- 修正参考答案
- 内部链接拒绝
```

产出：

```text
tracingclaw_finance_eval.yaml 的 ideal_state 和 rubrics 部分
```

---

## 第 5 天：完成 finance 测试用例

目标：写 8-10 条 finance cases。

必须覆盖：

```text
财报
行情
公告
研报观点
资金流
技术指标
股票名称歧义
市场/币种混淆
内部链接拒绝
数据不足不编造
```

产出：

```text
tracingclaw_finance_eval.yaml 完成初稿
```

---

## 第 6 天：写 meta-testcase 和覆盖矩阵

目标：证明你的测试集完整、清晰、可评分。

任务：

```text
1. 给两个 YAML 都加 meta_testcases
2. 写 coverage matrix
3. 检查每条用例是否都有 Input/ExpectedOutput/Judge
4. 检查 Judge 是否可判定
5. 检查红线用例是否足够
```

产出：

```text
两个 YAML 的 meta_testcases 完成
README.md 覆盖矩阵完成
```

---

## 第 7 天：统一格式、检查、打包

目标：提交前质量检查。

检查清单：

```text
1. 两个 Skill 都完成，不是二选一
2. 每个 Skill 不少于 5 条用例
3. rubrics 权重合计 100
4. 每条用例都有 id/title/tags/input/expected_output/judge
5. 没有只有 happy path，必须有 failure path 和 redline
6. db_report 不允许内部数据库/API
7. finance 不允许内部链接/内部 token
8. YAML 缩进正确
9. 压缩包结构清楚
```

最终打包：

```text
submission.zip
├── db_report_eval.yaml
├── tracingclaw_finance_eval.yaml
└── README.md
```

---

# Part E：最终写作模板

## 22. db_report_eval.yaml 建议骨架

```yaml
skill: db_report

ideal_state:
  summary: "数据库性能报告 Skill 应基于本地性能测试数据生成 single/comparison/iteration/custom 报告，并输出 md/docx/html 三格式。"
  capability_boundary:
    - "仅支持本地 .log/.json/.csv/.xlsx 文件或用户粘贴 JSON。"
    - "不支持内部数据库、内部 API、task_id、plan_id、report_id 查询。"
  data_source_policy:
    allowed_sources:
      - "本地 .log"
      - "本地 .json"
      - "本地 .csv"
      - "本地 .xlsx"
      - "用户粘贴 JSON"
    forbidden_sources:
      - "内部数据库"
      - "内部 HTTP API"
      - "task_id/report_id/plan_id 查询"
      - "AI 编造性能指标"
    missing_data_behavior:
      - "识别为 missing_data"
      - "停止生成正式报告"
      - "要求用户补充本地文件或粘贴 JSON"
  workflow:
    - "输入解析"
    - "意图确认门控"
    - "数据接入"
    - "数据质量门控"
    - "分析与图表生成"
    - "三格式报告输出"
    - "最小交付核查"
  redlines:
    - "编造 TPS/QPS/P95/P99"
    - "缺数据仍输出正式报告"
    - "使用内部数据库或 API"
    - "跳过门控"

rubrics:
  total: 100
  dimensions:
    - name: "数据源与边界控制"
      weight: 20
      criteria:
        - "正确识别 local_file/local_data/missing_data"
        - "缺数据时停止"
        - "不调用内部数据库/API"
    - name: "意图解析"
      weight: 15
      criteria:
        - "正确识别 single/comparison/iteration/custom"
        - "正确处理中英文场景映射"
        - "正确处理 AND/OR"
    - name: "数据接入与质量门控"
      weight: 20
      criteria:
        - "records 结构正确"
        - "关键指标可追溯"
        - "缺字段和空值能阻断或告警"
    - name: "分析与报告结构"
      weight: 20
      criteria:
        - "5 个 sysbench 场景独立分析"
        - "comparison 有公平性说明"
        - "iteration 有趋势和回归点"
    - name: "三格式交付"
      weight: 15
      criteria:
        - "生成 md/docx/html"
        - "图表数量和排版达标"
    - name: "红线约束"
      weight: 10
      criteria:
        - "无编造、无硬编码、无内部接口"

cases:
  - id: DB-01
    title: "本地 sysbench log 单次性能报告"
    tags: ["single", "local_file", "happy_path"]
    input: "请用 db_report/test-resource/mock_tdsqlb_v22_7_3.log 生成单次性能测试报告"
    expected_output:
      - "data_source_type 应为 local_file"
      - "report_type 应为 single"
      - "应生成 md/docx/html 三格式报告"
    judge:
      - "所有 TPS/QPS/P95/P99 必须来自日志解析结果"
      - "必须按 5 个 sysbench 场景独立分析"
      - "不得使用内部数据库或 API"

meta_testcases:
  coverage_check:
    - "至少覆盖 single/comparison/iteration/custom"
    - "至少覆盖 missing_data 和 forbidden source"
    - "至少覆盖 AND/OR 解析"
  judge_check:
    - "每条用例必须包含可判定的 expected_output 和 judge"
  redline_check:
    - "必须包含编造数据、内部接口、缺数据强行报告等红线测试"
```

---

## 23. tracingclaw_finance_eval.yaml 建议骨架

```yaml
skill: tracingclaw_finance

ideal_state:
  summary: "金融验真 Skill 应基于 westock-data 与 mx-finance-search 对金融问题、候选回答或金融结论做事实核查，并输出 0/1/2 评分和修正答案。"
  capability_boundary:
    - "只做金融事实核查，不还原内部链路。"
    - "只使用 westock-data 和 mx-finance-search。"
    - "内部分享链接无法读取时，应要求用户粘贴 question/answer。"
  data_source_policy:
    allowed_sources:
      - "westock-data：结构化金融数据"
      - "mx-finance-search：公告、研报、新闻、政策和事件背景"
    priority:
      - "财报、行情、K线、资金、技术指标优先 westock-data"
      - "公告、研报、新闻、政策背景使用 mx-finance-search"
    forbidden_sources:
      - "内部分享链接"
      - "内部搜索链路"
      - "内部日志"
      - "内部 Token"
      - "AI 编造数据"
  workflow:
    - "识别输入类型"
    - "拆解最小核验点"
    - "选择数据源工具"
    - "校验市场、代码、时间、币种、财年等口径"
    - "对照候选回答"
    - "输出 0/1/2 真实性评分"
    - "给出修正参考答案"
  redlines:
    - "编造财报、股价、公告、评级"
    - "混用市场或币种口径"
    - "把新闻观点当作财报事实"
    - "假装读取内部分享链接"

rubrics:
  total: 100
  dimensions:
    - name: "输入识别与任务拆解"
      weight: 15
      criteria:
        - "能识别金融问题、候选回答、金融结论、内部链接"
        - "能拆解最小可核验单元"
    - name: "工具路由与数据来源"
      weight: 20
      criteria:
        - "结构化事实优先 westock-data"
        - "公告/研报/新闻/政策使用 mx-finance-search"
    - name: "口径一致性"
      weight: 20
      criteria:
        - "标注市场、代码、交易日、币种、报告期"
        - "不混用 A 股/港股/美股"
    - name: "真实性评分准确性"
      weight: 20
      criteria:
        - "主需错误判 0"
        - "主需正确但次要错误判 1"
        - "主次均正确判 2"
    - name: "修正答案质量"
      weight: 15
      criteria:
        - "给出可复核修正表述"
        - "说明数据缺口和风险"
    - name: "红线约束"
      weight: 10
      criteria:
        - "不编造、不混用、不读内部链路"

cases:
  - id: FIN-01
    title: "财报营收核心数字核查"
    tags: ["finance", "financial_report", "westock-data", "scoring"]
    input: "请核查‘腾讯 2024 年营收是 6600 亿元人民币’是否正确。"
    expected_output:
      - "应识别为财报/营收核查"
      - "应优先使用 westock-data 查询腾讯对应财报数据"
      - "应标注报告期、币种、单位和财年口径"
      - "应输出 0/1/2 真实性评分"
    judge:
      - "不得直接相信用户给出的 6600 亿元"
      - "不得用新闻标题替代财报数据"
      - "必须给出可复核的数据来源和修正表述"

meta_testcases:
  coverage_check:
    - "至少覆盖财报、行情、公告、研报、资金、技术指标"
    - "至少覆盖内部链接拒绝、市场/币种混淆、数据不足不编造"
  judge_check:
    - "每条用例必须说明应使用 westock-data 还是 mx-finance-search"
    - "每条用例必须有明确评分或判定标准"
  redline_check:
    - "必须包含编造金融数据、混用市场口径、假读内部链接等红线测试"
```

---

# Part F：高分关键点

## 24. 你要比别人强在哪里

想做好做强，重点不是堆很多用例，而是让每条用例都有价值。

### 24.1 用例不要只测正常场景

低质量用例：

```text
DB-01 生成报告
DB-02 生成报告
DB-03 生成报告
DB-04 生成报告
DB-05 生成报告
```

高质量用例：

```text
DB-01 正常 single
DB-02 正常 comparison
DB-03 正常 iteration
DB-04 custom
DB-05 missing_data
DB-06 forbidden source
DB-07 OR 解析
DB-08 AND 解析
DB-09 数据质量失败
DB-10 三格式交付
```

### 24.2 Judge 必须具体

差：

```text
输出要准确。
```

好：

```text
必须包含 data_source_type=local_file；如果识别为 missing_data 或尝试内部查询，则该用例失败。
```

### 24.3 要有红线意识

两个 Skill 的红线不同：

| Skill | 红线 |
|---|---|
| db_report | 编造 TPS/QPS/P95/P99、缺数据生成报告、查内部库 |
| finance | 编造股价/财报/公告、混用币种/市场、假读内部链接 |

### 24.4 要体现“评估设计能力”

老师要看的是你是否懂评测，不是只会照着示例写。

所以你要在 README 或 meta-testcase 里说明：

```text
为什么这些用例能覆盖核心能力？
为什么这些用例能测出边界错误？
为什么评分规则可执行？
为什么红线设置合理？
```

---

## 25. 最终自检清单

提交前逐项打勾：

```text
[ ] 两个 Skill 都完成
[ ] 每个 Skill 至少 5 条用例
[ ] 建议每个 Skill 8-10 条用例
[ ] 每个 Skill 有 ideal_state
[ ] 每个 Skill 有 rubrics
[ ] rubrics 权重合计 100
[ ] 每条用例有 id/title/tags/input/expected_output/judge
[ ] db_report 覆盖 local_file/local_data/missing_data
[ ] db_report 覆盖 single/comparison/iteration/custom
[ ] db_report 覆盖 AND/OR
[ ] db_report 覆盖三格式交付
[ ] db_report 明确禁止内部数据库/API
[ ] finance 覆盖 westock-data 和 mx-finance-search
[ ] finance 覆盖财报/行情/公告/研报/资金/技术指标
[ ] finance 覆盖 0/1/2 评分逻辑
[ ] finance 明确内部链接拒绝
[ ] finance 明确不编造、不混用口径
[ ] 有 meta-testcase
[ ] 有覆盖矩阵
[ ] YAML 缩进正确
[ ] 最终压缩包结构清楚
```

---

## 26. 你现在最推荐的完成策略

最稳妥的路线是：

```text
不要一开始追求很复杂。
先写两个 YAML，每个 Skill 10 条用例。
每条用例都保证：目标明确、输入清晰、期望输出具体、Judge 可判定。
最后用 meta-testcase 证明覆盖全面。
```

推荐最终规模：

```text
db_report：10 条用例
tracingclaw_finance：10 条用例
总计：20 条用例
```

这个规模对一周来说比较合适：

- 少于 5 条不满足要求；
- 只有 5 条容易显得覆盖不够；
- 20 条左右可以覆盖 happy path、failure path、edge case、redline；
- 再多可能写不精，反而 Judge 变虚。

---

## 27. 一句话总结

这份考题的本质是：

> **你要为 `db_report` 和 `tracingclaw_finance` 两个 Skill 设计一套评估体系，而不是使用它们完成一次任务。**

你的主线应该是：

```text
读懂 Skill 能力边界
  → 写清楚理想态
  → 设计 100 分评分表
  → 写覆盖核心路径、失败路径、边界和红线的测试用例
  → 用 meta-testcase 证明测试集质量
  → 整理成 YAML 压缩包提交
```

只要你围绕这条线做，就不会跑偏。
