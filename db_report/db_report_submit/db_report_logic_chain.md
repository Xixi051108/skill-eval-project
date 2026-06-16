# db_report Logic Chain

## 1. Skill Goal

`db_report` Skill 的目标是：基于用户提供的本地数据库性能测试数据或用户粘贴的 JSON，完成输入解析、数据接入、性能分析、图表生成和三格式报告交付，生成可信、可追溯、可复核的数据库性能测试报告。

## 2. Input Modes

支持的输入方式包括：

- 本地 `.log` 文件
- 本地 `.json` 文件
- 本地 `.csv` 文件
- 本地 `.xlsx` 文件
- 用户粘贴的标准 `records JSON`
- 用户粘贴的原始测试行 JSON
- 未提供本地文件或可解析粘贴 JSON 的 `missing_data` 请求

## 3. Output Contract

按执行阶段，Skill 的关键输出应包括：

- 阶段 1 输出 `intent.json`
- 阶段 2 输出标准化 `extracted_data.json`（或等价的 `records.json` / `StandardRecords`）和 `data_quality_summary.json`
- 阶段 3 输出 `analysis_results.json` 和 `insights.json`
- 阶段 4 输出 `charts/*` 图表文件
- 阶段 5 输出 `report.md`、`report.docx`、`report.html` 和最小交付检查结果（或等价的门控③核查结果）

## 4. Tool Or Data Routing

在进入正式分析前，Skill 应先判断输入属于哪一类，并决定对应处理路径。

- 先识别输入属于 `local_file`、`local_data` 或 `missing_data`
- `local_file` 按文件类型分流到 `log/json/csv/xlsx` 解析流程
- `local_data` 进入粘贴 JSON 解析流程
- 缺少可用数据源时识别为 `missing_data`，在门控①处停止，不进入阶段 2 数据接入
- 根据关键词或用户需求识别 `report_type` 为 `single`、`comparison`、`iteration` 或 `custom`

## 5. Execution Stages

### 阶段1：输入解析

目的：识别用户提供的数据源、报告类型、筛选条件和输出格式。

关键输出：

- `intent.json`
- `data_source_type`
- `report_type`
- `test_name_keywords` 或 `test_name_keywords_or`

门控①：意图确认

目的：在进入数据接入前，让用户确认 Skill 对数据源、报告类型、筛选条件和输出格式的理解是否正确。

### 阶段2：数据接入

目的：读取本地 `log/json/csv/xlsx` 或用户粘贴 JSON，并转换为标准 `extracted_data.json`（或等价的 `records.json` / `StandardRecords`）。

关键输出：

- `extracted_data.json`（或等价的 `records.json` / `StandardRecords`）
- `meta`
- `records`
- `data_quality_summary`

门控②：数据确认

目的：确认数据记录数、字段完整性、空值率、抽检结果和覆盖范围是否满足分析要求。

### 阶段3：性能分析

目的：根据 `report_type` 分流执行 `single`、`comparison`、`iteration` 或 `custom` 分析。

关键输出：

- `analysis_results.json`
- `insights.json`

分支逻辑：

- `single`
  - 分析单次测试的峰值 `QPS`、扩展性和 `P95/P99` 延迟
- `comparison`
  - 进行多产品、多版本或多配置的对比分析；若存在不可比条件，可继续输出描述性分析，但不得直接给出确定性优劣结论
- `iteration`
  - 分析版本趋势、累计变化和性能回归点
- `custom`
  - 围绕用户指定问题进行专项分析

### 阶段4：图表生成

目的：根据 `report_type` 生成匹配报告类型的图表组合。

关键输出：

- `charts/*`

分支逻辑：

- `single`
  - 生成单产品性能画像图
- `comparison`
  - 生成横向对比图、峰值对比图和综合对比图
- `iteration`
  - 生成趋势图和回归点图
- `custom`
  - 生成服务于专项问题的图表

### 阶段5：报告组装与交付

目的：将文字、表格、图表和洞察组装为 `md/docx/html` 三格式报告。

关键输出：

- `report.md`
- `report.docx`
- `report.html`
- 最小交付检查结果（或等价的门控③核查结果）

门控③：交付确认

目的：检查三格式文件是否存在、内容是否一致、图表是否引用正确、报告是否满足最小交付要求。

## 6. Refusal Or Stop Conditions

在以下场景下，Skill 必须停止正式报告生成，或拒绝继续执行：

- 没有本地文件且没有可解析的粘贴 JSON 时，必须停止并要求补充数据源
- 文件路径不存在或不可访问时，必须停止
- JSON 无法解析或无法标准化为 `records` 结构时，必须停止
- `TPS / QPS / P95` 存在空值时，必须停止正式报告生成
- 用户仅提供 `task_id`、`report_id`、`plan_id` 等内部标识时，必须拒绝并说明不支持内部查数
- 任一门控未通过时，不得进入下一阶段

## 7. Logic Chain 的评估价值

将 `logic_chain` 单独整理为文档，有助于后续评估方案设计：

- 可以作为 `ideal_state` 和 `testcases` 的上游依据
- 可以帮助判断每个测试用例究竟在测哪一个阶段
- 可以辅助检查是否覆盖了意图解析、数据接入、质量门控、分析、交付五个主要阶段
- 可以帮助识别红线是否出现在某个具体门控之前或之后
