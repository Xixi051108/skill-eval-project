# Skill 评估答卷

本项目评估数据库性能报告和金融事实核查两个 Skill，交付从需求、场景、样例、Agent 执行到判定与回归的完整材料。原 Skill 保持不变，失败结果保留原始证据。

新版包含 22 条数据库用例和 22 条金融用例。数据库同时提供组件测试、完整脚本流水线和 Agent 执行入口；金融同时提供受控工具快照、Agent 执行入口和真实依赖检查。各层结果分别报告，不互相替代。

先读 [结果.md](结果.md)查看实测结论；再读 [评估.md](评估.md)理解验收合同，按 [学习.md](学习.md)复跑。原提交的问题逐项见 [复盘.md](复盘.md)。

## 目录

| 文件 | 用途 |
| --- | --- |
| `db.yaml`、`finance.yaml` | 逻辑链、理想态、Rubrics、用例、元测试和覆盖矩阵 |
| `run.py` | 校验、Judge 校准、组件、脚本流水线、Agent 测试 |
| `judge.py`、`test_judge.py` | 独立判定与故意破坏输出的校准测试 |
| `tool.py` | 不联网、不接触真实密钥的金融工具替身 |
| `live.py` | 对课程原始金融依赖做只读调用检查 |
| `review.py` | 应用带响应哈希和证据的单独语义复核记录 |
| `collect.py`、`变更.md` | 同条件原输出统一重判、保留重复采样与协议修订原因 |
| `data/` | 原始日志、JSON、等价 CSV/XLSX、受控金融证据 |
| `sut/` | 课程提供的原 Skill 快照，非本项目开发的业务实现 |
| `manifest.json`、`sources.json` | 版本、来源、哈希和独立财报真值 |
| `结果.md`、`学习.md` | 实测结论、缺陷优先级、技术栈与能力练习 |
| `out/` | 真实执行的逐用例记录、产物与汇总 |

YAML 文件使用 JSON 兼容语法，是合法 YAML 1.2。这样可以直接用 Python 标准库读取，无需额外安装 PyYAML。

## 复跑

使用 Python 3.11 或以上。在本目录执行。每次运行自动创建新目录，不覆盖旧记录。

```powershell
python run.py check
python run.py calibrate
python run.py component --suite db
```

完整数据库流水线还需要原 Skill 的依赖：

```powershell
python -m pip install -r requirements.txt
python run.py pipeline --suite db
```

Agent 测试使用已安装并登录的 Codex CLI，不需要创建 OpenAI API 密钥。以下模型 ID 是本机本次实测所用值，在其他环境须改为实际可用的模型。`--user-config` 只复用模型路由、推理档位和 Windows 沙箱后端，不复制密钥或无关 MCP 配置。

```powershell
python run.py agent --suite finance --model gpt-6.1-sol --user-config
python run.py agent --suite db --cases D05,D18 --model gpt-6.1-sol --user-config
python run.py agent --suite finance --cases F06,F08,F12 --repeat 3 --model gpt-6.1-sol --user-config
```

这些运行会消耗登录账户的模型额度。只有实际返回 token usage 时才记录 token 数，费用字段未知时保持未知，不估算为零。

真实金融依赖使用课程提供的工具目录和已有金融检索环境变量：

```powershell
python live.py --tools-root ../性能工程+Skill+评估专项考题/tracingclaw_finance --out out/live-new
```

无需将密钥写进命令或提交材料。真实依赖检查不等于金融 Agent 端到端验证。

## 阅读结果

每轮 `out/<运行>/report.md` 是可读报告，`results.json` 是汇总，`<case>-<repeat>/result.json` 是逐项判定。组件测试保存 `actual.json`；流水线保存完整产物和 stdout/stderr；Agent 测试保存 `request.txt`、`command.json`、`events.jsonl`、`response.txt` 和受控工具轨迹。

`PASS` 指本层适用的自动检查通过。金融自由文本另有语义复核状态；机器检查通过不能抹掉该状态。复核文件必须注明 human 或 LLM、复核者、响应 SHA256 和证据说明；`review.py` 拒绝过期复核，也不允许把自动失败静默改成通过。

```powershell
python review.py --source out/fin3 --reviews reviews.json --out out/finance-reviewed
```

复现本次统一重判（不产生新模型调用）与跨模型抽样重判：

```powershell
python collect.py --source out/finance out/finance2 out/finance3 out/finance4 out/repeat --out out/collected-new
python collect.py --source out/cross --cases F01,F06,F08 --out out/cross-new
```

同一批只能合并相同模型。版本变更、排除原因和原始失败不删除；详见变更.md。已保存的原始答复可能含当时执行目录的绝对路径，迁移后请从每个用例目录中的work查找对应文件，不修改原答复。

本项目只报告本地自检与实际运行结果。课程的官方完整版 Meta-Testcase 未随当前材料提供，因此不能宣称获得官方验收分数。
