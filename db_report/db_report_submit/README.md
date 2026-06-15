# db_report Skill 评估方案提交说明

## 一、提交目标

本目录用于存放 `db_report` Skill 的评估方案提交材料。提交内容围绕该 Skill 在数据库性能测试报告生成场景下的行为质量进行设计，覆盖理想态定义、评分规则、测试用例设计和元测试设计四部分。

## 二、文件清单

本目录当前包含以下文件：

- `db_report_ideal_state.md`
- `db_report_rubrics.yaml`
- `db_report_testcases.yaml`
- `db_report_meta_testcases.md`

## 三、文件说明

### 1. `db_report_ideal_state.md`

用于说明 `db_report` Skill 的目标、输入输出、支持的数据源、支持的报告类型、完整执行链路、禁止行为以及异常处理要求，并给出满分 Skill 应达到的理想状态描述。

### 2. `db_report_rubrics.yaml`

用于定义 `db_report` Skill 的结构化评分规则。内容包括评分维度、权重、满分标准、扣分点和严重违规项，总分为 100 分。

### 3. `db_report_testcases.yaml`

用于定义面向 `db_report` Skill 的测试用例集。内容覆盖正常路径、失败路径、边界条件和红线场景，是本评估方案的核心交付物之一。

### 4. `db_report_meta_testcases.md`

用于定义测试集自检方案，即“测试用例的测试用例”。内容主要用于检查测试集是否覆盖充分、判定是否清晰、结构是否完整、是否存在重复或不可判定用例。

## 四、当前编写状态

- `db_report_ideal_state.md`：已形成可提交初稿。
- `db_report_rubrics.yaml`：已形成结构化初稿。
- `db_report_testcases.yaml`：已建立统一字段框架，并预置候选用例骨架，待逐条补全。
- `db_report_meta_testcases.md`：已建立元测试检查框架，待结合最终测试集进一步细化。

## 五、提交说明

本目录采用分文件组织方式，以便与作业要求中的“理想态、Rubrics、测试用例、元测试设计分别成文”保持一致。后续完成内容细化后，可直接将本目录纳入最终压缩包作为 `db_report` 部分提交材料。
