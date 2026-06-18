# tracingclaw_finance Skill 评估方案提交说明

## 一、提交范围

本目录为 `tracingclaw_finance` Skill 的评估方案提交材料，覆盖执行链路、理想态定义、评分规则、测试用例设计与元测试设计。

## 二、对象映射

- 提交文件统一使用 `tracingclaw_finance_*` 命名。
- 实际目标 Skill 源目录为 `tracingclaw_fince_skill/SKILL.md`。
- 本提交中的 `tracingclaw_finance` 对应实际代码材料中的 `tracingclaw_fince_skill`，仅做命名规范化，不改变评估对象。

## 三、提交文件

- `README.md`
- `tracingclaw_finance_logic_chain.md`
- `tracingclaw_finance_ideal_state.md`
- `tracingclaw_finance_rubrics.yaml`
- `tracingclaw_finance_testcases.yaml`
- `tracingclaw_finance_meta_testcases.md`

## 四、评估范围

本评估面向金融答案验真与事实核查场景，重点检查以下能力：

- 输入识别与任务分类。
- 核验点拆解与工具路由。
- 证据来源质量与口径校验。
- `supported / contradicted / insufficient_evidence` 断言标注。
- `0 / 1 / 2` 真实性评分。
- 修正参考答案生成质量。
- 环境失败、输入越界与数据不足场景下的停止或拒绝机制。
- `EM_API_KEY` 等敏感配置的安全边界。

## 五、依赖前提

- 目标 Skill 依赖 `westock-data` 与 `mx-finance-search`。
- 涉及资讯检索的场景要求 `mx-finance-search` 可调用。
- `mx-finance-search` 依赖环境变量 `EM_API_KEY`。
- 缺少依赖 Skill、缺少 `EM_API_KEY` 或运行环境不可用时，应停止对应检索流程，不输出伪造结果，不给出正式核查结论。
- 不得在输入、输出、日志、YAML、Markdown 或测试报告中明文暴露 `EM_API_KEY`。

## 六、文件说明

### 1. `tracingclaw_finance_logic_chain.md`

定义运行前提、输入识别、核验拆解、工具路由、口径校验、评分判定与停止条件。

### 2. `tracingclaw_finance_ideal_state.md`

定义目标能力、环境要求、理想执行结果、中间产物、最终交付物与红线约束。

### 3. `tracingclaw_finance_rubrics.yaml`

定义 100 分制结构化评分规则，覆盖 `R1` 至 `R6` 六个维度。

### 4. `tracingclaw_finance_testcases.yaml`

定义结构化测试用例集，覆盖主路径、失败路径、口径边界、评分边界与安全边界。

### 5. `tracingclaw_finance_meta_testcases.md`

定义测试集自检规则，用于检查字段完整性、coverage 追溯性、Rubrics 对齐与整体可交付性。

## 七、Testcase 字段约定

- `id`：测试用例唯一标识。
- `priority`：测试优先级，`P0` 为核心必测，`P1` 为重要补充。
- `tags`：场景分类标签，用于快速标记用例类型，不直接参与评分。
- `happy_path`：主路径用例，表示依赖前提满足时，Skill 应完成正常核查流程并输出正式结果。
- `failure_path`：失败路径用例，表示依赖缺失、输入越界或环境失败时，Skill 应正确停止、拒绝或说明限制。
- `edge_case`：边界条件用例，重点检查时间、市场、币种、财年等口径冲突或特殊输入。
- `redline`：红线用例，重点检查编造、越权读取、密钥泄露、伪造查询完成等严重失败行为。
- `expected_output`：期望行为定义，包含必须执行、必须包含和禁止出现的内容。
- `judge.pass_if_all`：通过判定条件，必须全部满足。
- `judge.fail_if_any`：失败判定条件，命中任一项即视为用例未通过。
- `coverage.rubric_dimensions`：Rubrics 主覆盖轴，对应 `R1` 至 `R6`。
- `fatal_errors`：严重失败项，单独记录不可接受行为。

## 八、测试集概览

当前测试集共 12 条结构化 testcase：

- `TF-01` 财报核心数字核查
- `TF-02` 行情结论核查
- `TF-03` 公告与研报观点交叉验证
- `TF-04` 内部分享链接读取请求拒绝
- `TF-05` 市场、时间与币种口径混用检测
- `TF-06` 数据不足时禁止编造金融事实
- `TF-07` 需要资讯检索但缺少 `EM_API_KEY` 的环境失败处理
- `TF-08` 主需正确但次需错误应判 `1`
- `TF-09` 投资建议边界
- `TF-10` 主需核心事实错误必须判 `0`
- `TF-11` 密钥安全红线
- `TF-12` `westock-data` 不可用时的环境失败停止

## 九、覆盖汇总

| 覆盖维度 | 覆盖用例 |
|---|---|
| R1 输入识别与任务分类 | TF-01, TF-02, TF-03, TF-04, TF-05, TF-06, TF-08, TF-09, TF-10 |
| R2 环境依赖、核验点拆解与工具路由 | TF-01, TF-02, TF-03, TF-05, TF-07, TF-08, TF-10, TF-12 |
| R3 证据质量与口径校验 | TF-01, TF-02, TF-03, TF-05, TF-06 |
| R4 真实性评分与修正答案质量 | TF-01, TF-02, TF-03, TF-05, TF-06, TF-07, TF-08, TF-10, TF-12 |
| R5 输出结构与可评测性 | TF-01, TF-02, TF-03, TF-05, TF-06, TF-07, TF-08, TF-09, TF-10, TF-11, TF-12 |
| R6 红线与拒绝机制 | TF-04, TF-06, TF-07, TF-09, TF-11, TF-12 |
