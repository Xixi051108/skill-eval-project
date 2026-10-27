# 题目：为目标 Skill 构建评估用例集

## 最新版：Skill 评估答卷 2.4

最新评估代码、用例与执行证据位于 [答卷](答卷/README.md)，原题和历史提交目录继续保留。下面的原提交说明供追溯，最新结论以答卷中的实测结果为准。

- [评估合同](答卷/评估.md)：任务范围、评分规则与停止条件。
- [实测结果](答卷/结果.md)：不同层级的结果、缺陷与适用边界。

### 本地检查

使用 Python 3.11 或以上，在仓库根目录执行：

```powershell
cd 答卷
python -B -m unittest -v test_judge
python -B run.py check
```

运行数据库组件或报告流水线还需安装 `答卷/requirements.txt` 中的依赖。Agent 测试需要已登录的 Codex CLI，并会消耗模型额度，详见答卷说明。

如从本仓库运行真实金融依赖检查，在答卷目录使用本仓库已有的工具目录：

```powershell
python live.py --tools-root ../tracingclaw_finance --out out/live-new
```

### 已保存结果的范围

数据库与金融各 22 条用例；Judge 校准 38/38 通过；数据库组件 20 条中 9 条失败；金融受控基线 22/22 通过并完成 LLM 复核。它们是不同层级的结果，不能合并为整个项目的通过率，也不代表官方验收或真实金融 Agent 端到端成功。

`答卷/sut` 保存被测原 Skill 快照，新增工程主要是执行器、Judge、工具替身、用例和复核流程。必要的失败、重复与过程证据按原交付清单保留；本次不上传本地运行依赖、缓存或重复压缩包。`.gitattributes` 对新增答卷目录禁用换行自动转换，保持冻结文件字节与 SHA-256 一致。

---


本项目围绕目标 Skill 的评估方案设计展开，核心任务是为给定 Skill 构建一套结构完整、可执行、可追溯的评估交付物，包括理想态定义、逻辑链、评分规则、测试用例与元测试方案。

## 项目范围

当前目录包含两个目标 Skill 子项目：

- `db_report`
- `tracingclaw_finance`

其中：

- `db_report` 聚焦数据库性能报告生成与评估。
- `tracingclaw_finance` 聚焦金融答案验真、事实核查、口径校验与真实性评分。

## 标准交付物

每个 Skill 项目原则上应包含以下提交材料：

- `README.md`
- `*_logic_chain.md`
- `*_ideal_state.md`
- `*_rubrics.yaml`
- `*_testcases.yaml`
- `*_meta_testcases.md`
- 如进行了实际运行测试，可补充统一测试报告 `*.html`

## db_report 当前提交位置

`db_report` 项目的提交版材料位于：

- `db_report/db_report_submit`

当前目录下的核心文件包括：

- `db_report_submit/README.md`
- `db_report_submit/db_report_logic_chain.md`
- `db_report_submit/db_report_ideal_state.md`
- `db_report_submit/db_report_rubrics.yaml`
- `db_report_submit/db_report_testcases.yaml`
- `db_report_submit/db_report_meta_testcases.md`
- `db_report_submit/db_report_test_report.html`

## tracingclaw_finance 当前提交位置

`tracingclaw_finance` 项目的提交版材料位于：

- `tracingclaw_finance/tracingclaw_finance_submit`

当前目录下的核心文件包括：

- `tracingclaw_finance_submit/README.md`
- `tracingclaw_finance_submit/tracingclaw_finance_logic_chain.md`
- `tracingclaw_finance_submit/tracingclaw_finance_ideal_state.md`
- `tracingclaw_finance_submit/tracingclaw_finance_rubrics.yaml`
- `tracingclaw_finance_submit/tracingclaw_finance_testcases.yaml`
- `tracingclaw_finance_submit/tracingclaw_finance_meta_testcases.md`
- `tracingclaw_finance_submit/tracingclaw_finance_full_test_report_2026-06-19.html`

## 交付要求要点

- 以结构正确、层级统一、字段规范为前提。
- 测试用例需覆盖主路径、失败路径、边界条件与安全红线。
- Rubrics、testcases 与 meta-testcases 之间需保持可追溯关系。
- 若存在环境依赖或敏感配置，需在文档中说明依赖条件与安全边界，但不得泄露密钥或本地敏感信息。

## 备注

提交版材料应避免出现：

- 本地绝对路径
- 无关项目引用
- 敏感环境变量明文
- 未说明用途的占位空壳文件
