# tracingclaw_finance 元测试设计

## 1. 文档目的

本文件用于检查 `tracingclaw_finance_testcases.yaml` 这套测试集本身的质量。

换句话说，本文件不是在测试 `tracingclaw_finance` Skill 是否会做金融核查，而是在测试：

- 测试集是否覆盖了应该覆盖的核心任务类型；
- 每条用例是否可判定、可复现、可执行；
- Rubrics 与 testcase 之间是否结构一致；
- 是否存在重复用例、空洞用例或无法落地的 judge；
- 是否已经覆盖环境依赖、评分边界、密钥安全和拒绝机制等高风险专项点。

本文件属于“**测试用例的测试用例**”，对应本专项中的元测试设计交付物。

## 2. 元测试使用范围

本元测试设计主要面向以下提交物：

- `tracingclaw_finance_testcases.yaml`
- `tracingclaw_finance_rubrics.yaml`
- `tracingclaw_finance_ideal_state.md`
- `tracingclaw_finance_logic_chain.md`

其中：

- `tracingclaw_finance_testcases.yaml` 是元测试的主要检查对象；
- `tracingclaw_finance_rubrics.yaml` 用于检查评分结构是否自洽；
- `tracingclaw_finance_ideal_state.md` 和 `tracingclaw_finance_logic_chain.md` 用于反查测试集是否与上游规范保持一致。

## 3. 元测试执行原则

元测试遵循以下原则：

- **先查覆盖，再查可判定性**：先判断测试集有没有覆盖该测的东西，再判断每条是否写得能判。
- **先查红线，再查增强项**：优先检查编造、越界读取、环境失败伪装、密钥泄露、评分边界错误等高风险场景。
- **以结构化证据为主**：优先通过 testcase 的 `id`、`tags`、`input`、`expected_output`、`judge`、`coverage`、`fatal_errors` 判断。
- **以“可复现判定”为通过标准**：凡是不能明确观察、不能明确证伪、不能稳定执行的 testcase，都视为存在质量风险。

## 4. 当前测试集概况

当前测试集共 **12 条 testcase**：

- `TF-01`：财报核心数字核查
- `TF-02`：行情结论核查
- `TF-03`：公告与研报观点交叉验证
- `TF-04`：内部分享链接读取请求拒绝
- `TF-05`：市场、时间与币种口径混用检测
- `TF-06`：数据不足时禁止编造金融事实
- `TF-07`：需要资讯检索但缺少 `EM_API_KEY` 的环境失败处理
- `TF-08`：主需正确但次需错误应判 `1`
- `TF-09`：投资建议边界
- `TF-10`：主需核心事实错误必须判 `0`
- `TF-11`：密钥安全红线
- `TF-12`：`westock-data` 不可用时的环境失败停止

## 5. 元测试条目

下面定义本次 `tracingclaw_finance` 测试集的元测试条目。

每条元测试均包含：

- 检查目标
- 检查方法
- 证据来源
- 通过标准
- 失败标准
- 当前测试集映射

## META-TF-01 主路径类型覆盖检查

**检查目标**

确认测试集覆盖金融验真 Skill 的核心 happy path，而不是只有拒绝类或失败类用例。

**检查方法**

检查 `tracingclaw_finance_testcases.yaml` 中是否至少存在：

- 财报核查主路径；
- 行情核查主路径；
- 观点/公告/研报交叉验证主路径。

**证据来源**

- `id`
- `tags`
- `input.skill_specific_input.expected_task_type`
- `objective`

**通过标准**

- 至少 1 条财报类主路径；
- 至少 1 条行情类主路径；
- 至少 1 条交叉验证主路径。

**失败标准**

- 测试集只有 failure path，没有主要 happy path；
- 标题声称覆盖某类任务，但 `input` 与 `expected_output` 不能支撑。

**当前测试集映射**

- `TF-01`
- `TF-02`
- `TF-03`

## META-TF-02 失败路径与拒绝机制覆盖检查

**检查目标**

确认测试集覆盖主要失败路径，而不是只测试“会不会查”。

**检查方法**

检查测试集中是否存在以下场景：

- 内部分享链接或内部读取请求；
- 数据不足，必须保留边界；
- 环境依赖缺失，必须停止正式评分；
- 投资建议请求，必须收束边界；
- 结构化数据依赖失败，必须停止正式核查。

**证据来源**

- `tags`
- `expected_output.required_actions`
- `judge.fail_if_any`
- `fatal_errors`

**通过标准**

- 至少 1 条内部读取请求拒绝用例；
- 至少 1 条数据不足拒绝编造用例；
- 至少 1 条 `EM_API_KEY` 环境失败停止用例；
- 至少 1 条 `westock-data` 环境失败停止用例；
- 至少 1 条投资建议边界用例。

**失败标准**

- failure path 只写标题，不写停止动作；
- 没有禁止输出、fatal error 或明确的失败判定。

**当前测试集映射**

- `TF-04`
- `TF-06`
- `TF-07`
- `TF-09`
- `TF-12`

## META-TF-03 口径边界覆盖检查

**检查目标**

确认测试集覆盖市场、时间、币种、财年/自然年、事实/推测混用等关键边界。

**检查方法**

检查是否存在专门的口径混用或复合结论场景，并在 judge 中体现具体判定逻辑。

**证据来源**

- `tags`
- `expected_output.required_content`
- `judge.pass_if_all`
- `judge.fail_if_any`

**通过标准**

- 至少 1 条专门覆盖口径混用的 testcase；
- 至少 1 条专门覆盖相对时间的 testcase；
- judge 中明确要求指出口径冲突、信息缺口或时间锚点。

**失败标准**

- 只提“口径”概念，但没有具体观察点；
- 未覆盖相对时间或市场口径问题。

**当前测试集映射**

- `TF-02`
- `TF-05`

## META-TF-04 红线覆盖检查

**检查目标**

确认测试集覆盖高风险红线行为，避免 Skill 因编造、越界、密钥泄露或把观点当事实而被误判通过。

**检查方法**

检查是否覆盖以下红线：

- 内部链路读取；
- 关键数字编造；
- 无时间锚点回答“今天/最新”；
- 把观点写成事实；
- 缺少 `EM_API_KEY` 时伪装完成资讯检索；
- 泄露或要求暴露密钥；
- `westock-data` 不可用时伪装完成结构化查询。

**证据来源**

- `prohibited_content`
- `judge.fail_if_any`
- `fatal_errors`

**通过标准**

- 多条用例明确覆盖上述红线；
- 每类红线都能在 testcase 中观察到，而不是只存在于 ideal_state/rubrics。

**失败标准**

- 红线只写在上游规范里；
- testcase 中没有对应的失败条件或 fatal error。

**当前测试集映射**

- `TF-02`
- `TF-03`
- `TF-04`
- `TF-06`
- `TF-07`
- `TF-11`
- `TF-12`

## META-TF-05 核心断言标签与评分边界覆盖检查

**检查目标**

确认测试集覆盖 `supported / contradicted / insufficient_evidence` 这组核心判断标签，以及 `0/1/2` 评分边界约束。

**检查方法**

检查 testcase 是否明确要求：

- 对核心断言逐项判断，而不是只给总评；
- 在证据不足时使用 `insufficient_evidence` 或等价表达；
- 主需错误必须判 `0 分`；
- 主需正确、次需错误或证据不足时能判 `1 分`；
- 环境未就绪或核心证据不足时不能伪装成满分通过。

**证据来源**

- `expected_output.required_actions`
- `input.skill_specific_input.expected_assertion_labels`
- `judge.pass_if_all`
- `judge.fail_if_any`

**通过标准**

- 多条用例明确要求核心断言判断标签；
- 至少 1 条用例明确覆盖“证据不足不能给 `2 分`”；
- 至少 1 条用例明确覆盖“主需正确但次需有问题应判 `1 分`”；
- 至少 1 条用例明确覆盖“主需错误必须判 `0 分`”；
- 至少 1 条用例明确覆盖“环境未就绪不能正式评分”。

**失败标准**

- testcase 只写“给分”，不写判定标签；
- `0 分 / 1 分 / 2 分` 边界有缺口；
- 看不出 `insufficient_evidence` 与 `contradicted` 的区别。

**当前测试集映射**

- `TF-01`
- `TF-02`
- `TF-03`
- `TF-05`
- `TF-06`
- `TF-07`
- `TF-08`
- `TF-10`

## META-TF-06 judge 可执行性检查

**检查目标**

确认每条 testcase 的 judge 具体、可观察、可执行，而不是全靠主观理解。

**检查方法**

逐条检查每个 testcase 是否具备：

- `pass_if_all`
- `fail_if_any`
- 可观察对象，例如时间口径、评分、修正答案、拒绝语句、来源说明、环境状态或密钥边界

**证据来源**

- `judge.pass_if_all`
- `judge.fail_if_any`
- `fatal_errors`

**通过标准**

- 每条 testcase 都包含 `pass_if_all` 和 `fail_if_any`；
- judge 落到文本结构、来源说明、边界说明、评分边界、红线行为等可观察对象；
- 不依赖“看起来像合理”这类主观描述。

**失败标准**

- 缺少 judge 主体；
- judge 只写“输出合理”“分析专业”之类主观表述。

**当前测试集映射**

- `TF-01 ~ TF-12`

## META-TF-07 Rubrics 对齐检查

**检查目标**

确认 Rubrics 的结构正确，且与测试集关注点保持一致。

**检查方法**

检查 `tracingclaw_finance_rubrics.yaml`：

- 各维度权重之和是否为 100；
- 是否覆盖任务分类、工具路由、口径校验、评分、输出结构、红线治理；
- testcase 的 `coverage.rubric_dimensions` 是否能回指到对应维度。

**证据来源**

- `tracingclaw_finance_rubrics.yaml`
- `tracingclaw_finance_testcases.yaml -> coverage.rubric_dimensions`

**通过标准**

- Rubrics 总分为 100；
- testcase 关注点能在 Rubrics 中找到对应维度；
- 不存在大面积 testcase 无 Rubrics 映射的情况。

**失败标准**

- 权重不等于 100；
- testcase 关注点与 Rubrics 严重脱节；
- 仍使用旧字段名导致元测试与 testcase 结构不一致。

**当前测试集映射**

- `R1 ~ R6`
- `TF-01 ~ TF-12`

## META-TF-08 安全与环境前提可执行性检查

**检查目标**

确认测试集不仅写了业务逻辑，还写清楚了实际跑测所需的运行前提、安全边界和环境异常处理。

**检查方法**

检查 testcase 元信息和各 case 的 `execution_preconditions` 是否明确说明：

- 是否依赖 `westock-data`
- 是否依赖 `mx-finance-search`
- 是否需要 `EM_API_KEY`
- 是否区分“环境问题”与“Skill 逻辑问题”
- 是否覆盖“不得泄露 `EM_API_KEY`”

**证据来源**

- `input.skill_specific_input.execution_preconditions`
- `expected_output.required_actions`
- `judge.fail_if_any`
- `fatal_errors`

**通过标准**

- 依赖 `mx-finance-search` 的用例写明环境变量前提；
- 存在明确的 `EM_API_KEY` 缺失停止用例；
- 存在明确的 `westock-data` 不可用停止用例；
- 存在明确的密钥泄露红线用例；
- 能据此判断某次失败是环境缺失还是 Skill 逻辑缺陷。

**失败标准**

- testcase 只写业务目标，不写运行前提；
- 依赖型用例没有说明依赖 Skill 或环境变量；
- 没有密钥安全专项用例；
- 无法区分“没配环境”和“Skill 没做好”。

**当前测试集映射**

- `TF-07`
- `TF-11`
- `TF-12`

## META-TF-09 重复与职责分工检查

**检查目标**

确认测试集中没有明显重复用例，同时每条用例都有清晰职责。

**检查方法**

逐条比较 testcase 的：

- 核心任务类型
- 主要风险点
- judge 关注对象
- fatal_errors

重点排查：

- 仅改措辞、不改测点的重复用例；
- 同一评分边界被多条用例机械重复但没有新增信息；
- 同一环境失败场景被重复堆砌。

**证据来源**

- `title`
- `tags`
- `judge`
- `fatal_errors`

**通过标准**

- 每条 testcase 承担的职责不同；
- 主路径、失败路径、评分边界、环境失败、安全红线之间分工清楚。

**失败标准**

- 多条 testcase 只是换标题，没有换测点；
- 同一风险点被重复堆砌但没有新增价值。

**当前测试集映射**

- `TF-01 ~ TF-12`

## META-TF-10 字段完整性检查

**检查目标**

确认每条 testcase 都具备可执行测试用例所需的基本字段，避免字段缺失、缩进错误或结构不一致。

**检查方法**

逐条检查 `tracingclaw_finance_testcases.yaml` 中每个 testcase 是否包含：

- `id`
- `title`
- `objective`
- `priority`
- `tags`
- `input`
- `expected_output`
- `judge.pass_if_all`
- `judge.fail_if_any`
- `coverage.rubric_dimensions`
- `coverage.process_coverage`
- `coverage.referenced_specs`
- `fatal_errors`

**证据来源**

- `tracingclaw_finance_testcases.yaml`

**通过标准**

- 每条 testcase 均包含上述必填字段。
- `judge.pass_if_all` 与 `judge.fail_if_any` 均为非空列表。
- `coverage.rubric_dimensions` 至少包含一个 `R1 ~ R6` 维度。

**失败标准**

- 任一 testcase 缺少必填字段。
- `judge.pass_if_all` 或 `judge.fail_if_any` 为空。
- `coverage` 仍使用旧字段名 `rubrics`，而不是 `rubric_dimensions`。

**当前测试集映射**

- `TF-01 ~ TF-12`

## META-TF-11 Coverage 追溯性检查

**检查目标**

确认 testcase 的 coverage 能够追溯到 Rubrics、logic_chain 和 ideal_state，且以 `rubric_dimensions` 作为主覆盖轴。

**检查方法**

检查每条 testcase 的 `coverage` 字段是否包含：

- `rubric_dimensions`
- `process_coverage`
- `referenced_specs`

同时检查 `rubric_dimensions` 是否只引用 `R1 ~ R6`，并确认整个测试集覆盖所有 Rubrics 维度。

**证据来源**

- `coverage.rubric_dimensions`
- `coverage.process_coverage`
- `coverage.referenced_specs`
- `tracingclaw_finance_rubrics.yaml`

**通过标准**

- 每条 testcase 都包含 `coverage.rubric_dimensions`。
- `rubric_dimensions` 只引用 `R1`、`R2`、`R3`、`R4`、`R5`、`R6`。
- 整个测试集覆盖全部 `R1 ~ R6`。
- 每条 testcase 都包含 `process_coverage` 作为 logic_chain 辅助过程说明。
- 每条 testcase 都包含 `referenced_specs`，能够回指到 `ideal_state`、`logic_chain` 或 `rubrics`。
- 不再使用旧字段 `coverage.rubrics`。

**失败标准**

- 存在 testcase 没有 `coverage.rubric_dimensions`。
- coverage 引用了不存在的 Rubrics 维度。
- `R1 ~ R6` 中任一维度完全没有 testcase 覆盖。
- 大量 testcase 缺少 `process_coverage` 或 `referenced_specs`。
- 仍使用旧字段 `coverage.rubrics`，导致 coverage 主轴不一致。

**当前测试集映射**

- `TF-01 ~ TF-12`
- `R1 ~ R6`

## META-TF-12 总体可交付性检查

**检查目标**

给出这套 testcase 集作为提交物的整体质量定位。

**检查方法**

综合前述 META 条目，判断当前测试集是否已经达到：

- 可提交；
- 可复查；
- 可用于测试报告复查与质量追踪。

**证据来源**

- `TF-01 ~ TF-12`
- `coverage.rubric_dimensions`
- `fatal_errors`
- `evaluation_policy`

**通过标准**

- 结构完整；
- 覆盖主路径、失败路径、评分边界、环境依赖、安全边界；
- judge 可执行；
- 与 ideal_state、rubrics、logic_chain 基本对齐。

**失败标准**

- 仍停留在空壳框架；
- 缺少高风险边界；
- judge 大量不可执行；
- 与上游规范明显脱节。

**当前测试集映射**

- `TF-01 ~ TF-12`

## 6. 当前元测试结论定位

本文件当前给出的，是 `tracingclaw_finance` 测试集的**可交付版元测试设计方案**。它当前的作用是：

- 作为 testcase 集的自检清单；
- 作为老师或同学复查 testcase 质量的统一标准；
- 作为后续实测记录和测试报告整理的上游依据。


