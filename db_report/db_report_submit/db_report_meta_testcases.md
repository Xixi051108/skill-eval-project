# db_report 元测试设计

## 1. 文档目的

本文件用于检查 `db_report_testcases.yaml` 这套测试集本身的质量。

换句话说，本文件不是在测试 `db_report` Skill 是否会生成报告，而是在测试：

- 测试集是否覆盖了应该覆盖的核心场景；
- 每条用例是否可判定、可复现、可执行；
- Rubrics 与 testcase 之间是否结构一致；
- 是否存在重复用例、空洞用例或不可落地的 judge。

本文件属于“**测试用例的测试用例**”，对应本专项中的元测试设计交付物。

---

## 2. 元测试使用范围

本元测试设计主要面向以下提交物：

- `db_report_testcases.yaml`
- `db_report_rubrics.yaml`
- `db_report_ideal_state.md`
- `db_report_logic_chain.md`

其中：

- `db_report_testcases.yaml` 是元测试的主要检查对象；
- `db_report_rubrics.yaml` 用于检查评分结构是否自洽；
- `db_report_ideal_state.md` 和 `db_report_logic_chain.md` 用于反查测试集是否与上游规范保持一致。

---

## 3. 元测试执行原则

元测试遵循以下原则：

- **先查覆盖，再查可判定性**：先判断测试集有没有覆盖该测的东西，再判断每条是否写得能判。
- **先查硬性要求，再查增强项**：优先检查题目明确要求和 reference 明确约束的内容。
- **以结构化证据为主**：优先通过 testcase 的 `id`、`tags`、`input`、`expected_output`、`judge`、`fatal_errors` 等字段判断，而不是依赖主观印象。
- **以“可复现判定”为通过标准**：凡是不能明确观察、不能明确证伪、不能稳定执行的 testcase，视为存在质量风险。

---

## 4. 元测试条目

下面定义本次 `db_report` 测试集的元测试条目。

每条元测试均包含：

- 检查目标
- 检查方法
- 证据来源
- 通过标准
- 失败标准
- 当前测试集映射

---

## META-DB-01 happy path 覆盖检查

**检查目标**

确认测试集覆盖 `db_report` 的四类核心成功路径，而不是只测试单一路径。

**检查方法**

检查 `db_report_testcases.yaml` 中是否至少存在 1 条 testcase，分别覆盖：

- 本地 `log` 输入的 `single` 报告；
- `records JSON` 输入的 `comparison` 报告；
- `iteration` 历史趋势报告；
- `custom` 专项分析报告。

**证据来源**

- `id`
- `tags`
- `input.skill_specific_input.expected_report_type`
- `objective`

**通过标准**

- 至少包含 1 条 `local_log + single` 主路径用例；
- 至少包含 1 条 `records_json + comparison` 主路径用例；
- 至少包含 1 条 `iteration` 主路径用例；
- 至少包含 1 条 `custom` 主路径用例。

**失败标准**

- 缺少任一核心 happy path；
- 某条用例标题声称覆盖某类报告，但 `input` 与 `expected_output` 无法支持该类报告主路径。

**当前测试集映射**

- `DB-01`：`local log + single`
- `DB-02`：`records JSON + comparison`
- `DB-03`：`iteration`
- `DB-04`：`custom`

---

## META-DB-02 failure path 覆盖检查

**检查目标**

确认测试集覆盖主要失败路径，而不是只有“成功生成报告”的用例。

**检查方法**

检查测试集中是否存在以下失败场景：

- `keyword_only` / 缺少数据源；
- 文件不存在；
- 关键字段缺失或空值；
- 越权请求或禁止输入方式。

**证据来源**

- `id`
- `tags`
- `input`
- `expected_output.refusal_conditions`
- `judge.fail_if_any`
- `fatal_errors`

**通过标准**

- 包含缺少数据源用例；
- 包含文件不存在用例；
- 包含字段缺失或空值用例；
- 包含越权数据入口或禁止补查数据用例。

**失败标准**

- 测试集只有 happy path，没有主要 failure path；
- failure path 只写标题，不写 stop_stage、拒绝条件或禁止输出。

**当前测试集映射**

- `DB-05`：`keyword_only` / 缺少数据源
- `DB-06`：文件不存在 / `E2001`
- `DB-07`：关键指标空值 / 阶段 2 数据质量检查点失败
- `DB-08`：内部标识补查请求拒绝

---

## META-DB-03 edge case 覆盖检查

**检查目标**

确认测试集覆盖关键边界条件，特别是容易在 Agent/Skill 中出现误判的解析与交付边界。

**检查方法**

检查测试集中是否包含以下边界场景：

- `OR` 条件解析；
- `AND` 条件解析；
- 三格式交付一致性；
- `L1/L2/L3` 洞察治理。

**证据来源**

- `tags`
- `expected_output.skill_specific_expectation`
- `judge.pass_if_all`
- `judge.fail_if_any`

**通过标准**

- 至少 1 条 `OR` 条件解析用例；
- 至少 1 条 `AND` 条件解析用例；
- 至少 1 条三格式交付一致性用例；
- 至少 1 条洞察分级与位置治理用例。

**失败标准**

- 缺少任一关键边界场景；
- 只提到边界词，但未在 judge 中体现具体判定逻辑。

**当前测试集映射**

- `DB-09`：`OR`
- `DB-10`：`AND`
- `DB-11`：三格式交付一致性
- `DB-12`：`L1/L2/L3`

---

## META-DB-04 redline 覆盖检查

**检查目标**

确认测试集覆盖高风险红线行为，确保 Skill 不会在越权、编造、阶段检查点失效等场景下被误判为通过。

**检查方法**

检查测试集是否覆盖以下红线：

- 禁止通过 `task_id / report_id / plan_id` 查数；
- 禁止内部数据库 / 内部 API / 线上任务系统补数据；
- 允许识别 `task_filters`，但不得把其中的 `task_id / report_id / plan_id` 当成可用数据源；
- 禁止编造性能指标；
- 阶段检查点失败后不得继续正式交付。

**证据来源**

- `forbidden_outputs`
- `judge.fail_if_any`
- `fatal_errors`

**通过标准**

- 至少 1 条用例明确覆盖禁止内部标识补查；
- 至少 1 条用例明确覆盖禁止内部数据库/API；
- 多条用例包含禁止编造 `TPS/QPS/P95/P99/duration`；
- 多条失败路径明确要求阶段检查点失败即停止。

**失败标准**

- 缺少任一红线场景；
- 红线只写在 ideal_state/rubrics 中，但 testcase 不可观察；
- 失败路径没有明确阻断后续阶段。

**当前测试集映射**

- `DB-05`：缺数据时不得继续
- `DB-06`：文件不存在时不得继续
- `DB-07`：阶段 2 数据质量检查点失败不得继续
- `DB-08`：禁止内部标识补查
- `DB-01 ~ DB-12` 多条用例包含禁止编造指标 / 禁止内部查询

---

## META-DB-05 judge 可执行性检查

**检查目标**

确认每条 testcase 的 judge 具体、可观察、可执行，而不是“看起来像要求”但无法真正判分。

**检查方法**

逐条检查每个 testcase 是否具备：

- `pass_if_all`
- `fail_if_any` 或强约束 `fatal_errors`
- 可观察的行为、字段、文件、阶段、数量、结构或拒绝动作

同时排查是否出现模糊表述，例如：

- “输出合理”
- “内容完整”
- “分析较好”
- “报告专业”

**证据来源**

- `judge.pass_if_all`
- `judge.fail_if_any`
- `fatal_errors`

**通过标准**

- 每条 testcase 都包含 `pass_if_all`；
- 每条 testcase 都包含 `fail_if_any` 或可替代的强失败约束；
- judge 中的条件能落到文件、字段、阶段、数量、字符串、路径、一致性等可观察对象。

**失败标准**

- 缺少 judge 主体；
- judge 只能靠主观理解，无法稳定执行；
- judge 与 expected_output 无法互相印证。

**当前测试集映射**

- `DB-01 ~ DB-12` 全量检查

---

## META-DB-06 expected_output 具体性检查

**检查目标**

确认每条 testcase 的 `expected_output` 足够具体，能够支持自动化或半自动化评测。

**检查方法**

逐条检查 testcase 是否明确写出：

- 应生成什么；
- 应停止在哪个阶段；
- 应拒绝什么；
- 应包含哪些关键字段、关键内容、关键约束；
- 拒绝类 / 失败类用例是否写清主因与禁止输出。

**证据来源**

- `expected_output.task_understanding`
- `expected_output.required_actions`
- `expected_output.required_content`
- `expected_output.skill_specific_expectation`
- `expected_output.refusal_conditions`

**通过标准**

- 正常路径用例明确写出阶段性产物、关键图表、报告格式和核心判断；
- 失败路径用例明确写出 stop_stage、拒绝原因和禁止输出；
- 三格式与洞察类用例明确写出一致性或位置约束；
- 不出现“输出合理”“结果完整”等模糊词作为主要判定依据。

**失败标准**

- 预期输出过于口号化；
- 缺少 stop_stage、关键产物或关键限制条件；
- 失败类用例只说“应该报错”，但没有明确错误类型或阻断范围。

**当前测试集映射**

- `DB-01 ~ DB-12` 全量检查

---

## META-DB-07 rubrics 权重与结构一致性检查

**检查目标**

确认 Rubrics 的结构正确，且与测试集关注点保持一致。

**检查方法**

检查 `db_report_rubrics.yaml`：

- 各维度权重之和是否为 100；
- 是否覆盖输入解析、数据接入、数据质量、性能分析、交付质量、红线治理；
- testcase 的 `coverage.rubrics` 是否能回指到对应 rubric 维度。

**证据来源**

- `db_report_rubrics.yaml`
- `db_report_testcases.yaml -> coverage.rubrics`

**通过标准**

- 所有 rubric 维度权重相加等于 100；
- testcase 中出现的关键风险点能在 rubrics 中找到对应评价维度；
- 不存在大范围 testcase 无 rubrics 对应关系的情况。

**失败标准**

- 总分不等于 100；
- rubrics 维度缺失关键能力；
- testcase 关注点与 rubrics 严重脱节。

**当前测试集映射**

- `R1 ~ R6`
- `DB-01 ~ DB-12` 的 `coverage.rubrics`

---

## META-DB-08 重复与不可判定用例检查

**检查目标**

确认测试集中没有明显重复用例，也没有缺少关键字段导致无法执行判断的空壳用例。

**检查方法**

逐条比较 testcase 的：

- 输入类型
- 报告类型
- 核心测点
- stop_stage
- 主要 judge

重点排查：

- 仅改措辞、不改测点的重复用例；
- 同一风险点被多条用例重复覆盖但没有新增信息；
- 缺少 `input`、`expected_output`、`judge`、`fatal_errors` 等关键结构的不可判定用例。

**证据来源**

- `id`
- `title`
- `tags`
- `input`
- `expected_output`
- `judge`

**通过标准**

- 不存在“仅改标题/措辞，不改测试目标”的高度重复用例；
- 每条 testcase 均具备最小可判定结构；
- 同类用例之间存在明确分工，而不是机械重复。

**失败标准**

- 存在高度重复 testcase；
- 存在缺少关键结构、无法执行判断的 testcase；
- 存在名义上不同、实质判同一件事的冗余 case。

**当前测试集映射**

- `DB-01 ~ DB-12` 全量检查

---

## 5. 当前测试集的元测试结论定位

本文件当前给出的，是 `db_report` 测试集的**元测试设计方案**，重点在于：

- 定义该检查什么；
- 明确如何检查；
- 说明通过与失败的判定标准；
- 给出当前测试集与元测试项之间的映射关系。

它本身不直接给出“最终执行结果打分”，但已经具备以下作用：

- 作为测试集自检清单；
- 作为后续同学或导师复查 testcase 质量的统一标准；
- 作为后续将元测试进一步结构化 YAML 化的上游文本依据。

---

## 6. 后续可增强方向

如果后续老师更强调自动化或评测资产沉淀，可以继续增强：

- 将每条 META 项转写为结构化 YAML；
- 为每条 META 项补充自动化检查脚本思路；
- 将 `当前测试集映射` 进一步细化为“对应 testcase id + 对应字段路径”；
- 在最终 testcase 集稳定后，追加“当前测试集通过/不通过状态记录”。
