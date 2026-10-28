# Agent 补测

本目录补充真实金融 Agent 执行、四类数据库报告的 Agent 测试及过程证据。原 `答卷` 2.4 的 Skill、用例、Judge、manifest 和结果不修改。

## 本批合同

- `runner.py` 复用原用例与 CLI 配置；默认两模型为 gpt-6.1-sol、gpt-6-luna，推理档位 medium，单任务上限420秒。与历史 high 档位分批报告。
- 数据库默认 D01—D04，沿用原 Judge，并核对工作副本的 Skill 和输入字节；生成原始产物、最终答复、命令轨迹及过程检查。
- 真实金融默认 F01/F02/F15，保留原公开问题和固定日期锚点，不加载合成工具夹具。调用课程原 westock、资讯检索脚本。
- 真实金融按独立官方财报字段核验；营收容差3亿元、同比0.5个百分点。此为独立补测合同，明确消费同比容差，不能把本批混为历史2.4同条件重判。
- 所有真实金融任务要求两个工具实际调用并取得回执；工具返回内容是否支持答案、来源冲突是否正确处理，仍需明确标注的LLM语义复核。自动检查通过先记REVIEW，不直接记PASS。
- `gateway.py` 在宿主侧保留现有 EM_API_KEY，仅向原资讯工具子进程注入；Agent环境不含真实密钥。Agent通过本地一次性会话能力调用只读工具；stdout/stderr脱敏后落盘。
- 每个金融任务最多8次工具调用；原工具单次超时50秒。Agent超时尝试终止其进程树；没有完成回合就不冒充交付。
- `process.json` 是命令观察、字节检查及待复核线索；动态读取和语义不能仅凭字符串匹配宣称通过。当前不是恶意进程强隔离或完整安全评估。
- 真实金融回执不是固定快照A/B；两模型可比较同任务观察，不对货币性价比排名。未返回费用保持null。

## 执行

使用现有Python 3.12及报告依赖。此工作区的Matplotlib在 `.evaldeps`，执行器会为子进程复用该路径；其他环境按原requirements安装依赖。

```powershell
python -B -m unittest discover -s 补测 -p 'test_*.py' -v
python -B 补测/runner.py --suite finance --out 补测/out/finance
python -B 补测/runner.py --suite db --out 补测/out/db
```

输出目录必须是新目录。执行Agent和金融工具会使用已有账户额度，不创建密钥、不购买额度、不使用重置券。额度／鉴权阻塞时保存原因并停止后续任务。

`protocol.json` 在执行前保存模型、档位、代码与原始输入哈希；每条保存request、command、events、response、process及automatic判定，真实工具另有脱敏原始回执。`report.md`／`results.json` 汇总状态。后续复核应保留automatic.json，另存带响应哈希的复核记录，不能覆盖原自动失败。

实际执行结论以本目录新生成的记录为准；本说明不预先声称任何用例通过。求职材料仅保留在本地，不随结果发布。

从 GitHub 仓库运行时，可使用本轮实际工具的字节快照，显式指定路径：

```powershell
python -B 补测/runner.py --suite finance --tools-root 补测/tools --out 补测/out/finance-new
```

本地工作区的默认路径是课程原始目录。`tools/` 保存本轮实际调用的原工具脚本和依赖文档，不含环境文件或密钥；脚本哈希与回执对应。仓库根目录的 `tracingclaw_finance/` 仍保留，其 westock 脚本与本轮快照仅换行字节不同，规范化后内容一致，故原字节哈希不同。不要把缺少路径误判为业务 Skill 失败。单元测试使用临时工具文档，不依赖课程目录布局，也不实际调用金融服务。

本批结论与样本边界见 [结果.md](结果.md)。`out/finance` 与 `out/db` 保留首次额度阻塞记录，后续批次另建目录，不覆盖失败历史。`process.json` 中的 `pipeline_request`／`finance_tool_request` 只是命令字符串命中，读取脚本或列举文件也可能命中；应以真实执行命令、退出码、工具回执及产物联合复核。

本轮 Agent 执行使用的四份 Python 源文件保存在 `out/code/`，与各批次 `protocol.json` 的哈希对应；该目录用于审计，复跑时使用本目录入口。之后新增的 `audit.py` 离线审计 D01 表格与数据库提取记录；测试工具文档改为临时构造，鉴权测试不发送无关正文。执行器和 Agent 客户端未改变；网关在运行结束后修正 Windows 落盘的换行转换，使未来回执的 stdout_sha256 直接对应文件字节，并补充混合换行回归断言。旧回执未覆盖，receipt_review.json 记录其文本哈希与落盘字节的可逆换行差异；不把此离线修正冒充新的模型实测。

离线审计可单独复跑。第一条按显式表头核对 D01 三格式的全部数据行，允许额外列；第二条核对提取记录是否忠实于独立原始输入，不接受用 Agent 自检替代：

```powershell
python -B 补测/audit.py --artifacts 补测/out/db-r2/D01-gpt-6.1-sol/work/artifacts --source 答卷/data/single.log --out table-review-new.json
python -B 补测/audit.py --data-only --artifacts 补测/out/db-r2/D03-gpt-6.1-sol/work/artifacts --source 答卷/data/iter.json --out data-review-new.json
```

`audit.py` 的结果另行记录源文件、报告或提取数据及审计代码哈希，不能把事后增加的审计混称为原协议已有的自动检查。
