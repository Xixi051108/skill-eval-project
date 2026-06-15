# db_report 元测试设计

这个文档用于检查 `db_report_testcases.yaml` 这套测试集本身的质量。

换句话说，它不是在测 `db_report Skill`，而是在测“我们写出来的测试用例集是否覆盖充分、判定清晰、能稳定复现”。

## META-DB-01 happy path 覆盖检查

目的：确认测试集覆盖四类核心成功路径。

通过标准：

- 至少包含 1 条 `local log + single`
- 至少包含 1 条 `records JSON + comparison`
- 至少包含 1 条 `iteration`
- 至少包含 1 条 `custom`

失败标准：

- 缺少任一核心 happy path

## META-DB-02 failure path 覆盖检查

目的：确认测试集覆盖主要失败路径。

通过标准：

- 包含缺少数据源用例
- 包含文件不存在用例
- 包含字段缺失或空值用例
- 包含不可解析输入或无法标准化输入用例

失败标准：

- 缺少任一核心 failure path

## META-DB-03 edge case 覆盖检查

目的：确认测试集覆盖逻辑边界情况。

通过标准：

- 包含 OR 条件解析用例
- 包含 AND 条件解析用例
- 包含三格式交付一致性用例
- 包含 L1/L2/L3 洞察治理用例

失败标准：

- 缺少任一关键边界场景

## META-DB-04 redline 覆盖检查

目的：确认测试集覆盖高风险红线行为。

通过标准：

- 包含禁止 `task_id/report_id/plan_id` 查询用例
- 包含禁止内部数据库/API 查询场景
- 包含禁止编造性能指标场景
- 包含门控失败后不得继续正式交付的场景

失败标准：

- 缺少任一红线场景

## META-DB-05 judge 可执行性检查

目的：确认每条 testcase 的 judge 具体、可观察、可判定。

通过标准：

- 每条 testcase 都包含 `pass_if_all`
- 每条 testcase 都包含 `fail_if_any` 或 `fatal_errors`
- judge 使用可观察行为描述，而不是“合理”“完整”“质量高”等模糊词

失败标准：

- 存在无法落地判定的 judge

## META-DB-06 expected_output 具体性检查

目的：确认每条 testcase 的预期输出足够具体。

通过标准：

- 每条 testcase 的 expected_output 都明确写出要观察的行为或字段
- 拒绝类用例写清拒绝原因
- 交付类用例写清输出格式和一致性要求

失败标准：

- 存在“输出合理”“内容完整”等模糊描述

## META-DB-07 rubrics 权重检查

目的：确认评分规则结构正确。

通过标准：

- 所有 rubric 维度权重相加等于 100

失败标准：

- 总分不等于 100

## META-DB-08 重复与不可判定用例检查

目的：确认测试集中没有高重复和低可判定用例。

通过标准：

- 不存在仅改措辞、不改测试目标的重复用例
- 不存在缺少输入、预期输出或 judge 的不可判定用例

失败标准：

- 存在重复用例
- 存在无法执行判断的用例

## 当前建议

这个元测试文档已经足够作为第一版提交框架。下一步最值得补的是：

- 把每条 META 项补成“检查方法 + 证据来源 + 通过阈值”
- 在完成 `db_report_testcases.yaml` 后，回填每一条 META 项对应到哪些 testcase id
- 如果后续老师更强调自动化，可以把部分 META 项再转成结构化 YAML
