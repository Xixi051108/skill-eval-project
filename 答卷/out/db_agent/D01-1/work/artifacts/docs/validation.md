# 最小交付核查

固定时间：2026-06-19T16:00:00+08:00。

- ✅ A JSON intent：存在且 JSON 合法
- ✅ A JSON extracted_data：存在且 JSON 合法
- ✅ A JSON analysis_results：存在且 JSON 合法
- ✅ A JSON insights：存在且 JSON 合法
- ✅ A data/block_map.md：文件存在
- ✅ A docs/analysis_proposal.md：文件存在
- ✅ A report.md：16,745 字节，达到基线
- ✅ A report.docx：781,413 字节，达到基线
- ✅ A report.html：21,302 字节，达到基线
- ✅ A Todo：执行清单全 ✅
- ✅ B 产品、时长及记录覆盖：TDSQL-B-v22.7.2；300s；30 条
- ✅ B 指标空值率：四项指标空值率均为 0%
- ✅ B 来源与并发：来源字段完整，全部场景全并发覆盖
- ✅ B 全量数据表：第3章包含全部记录与 TPS/QPS/P95/P99
- ✅ B/F 全量指标与三格式一致性：30 条 × 4 项指标逐项与原日志一致，且全部数值在三格式中存在；超过6条抽检要求
- ✅ F 元数据与占位符：产品、300s、固定报告日期在三格式一致；无未替换占位符
- ✅ A/C 图表完整性：12 张：全部场景 QPS/P95、峰值汇总和单产品曲线；排名图 N/A
- ✅ C 中文标题与文字重叠：12张均有中文标题；check_text_overlap 实际执行且全部返回空
- ✅ E 图片路径与Word嵌入：三格式均引用 12 张图，路径正确，Word嵌入完整
- ✅ E Word字体：全部 391 处文字 run 显式设置微软雅黑
- ✅ E Word表头底色：全部 7 张表的表头为 D9E2F3
- ✅ E HTML结构：完整 head、内联CSS、目录及中文字体回退
- ✅ E Markdown层级与表格：章 #、节 ##，GFM表格含分隔行
- ✅ D 核心结论：第1章共5条核心结论，每场景1条
- ✅ D 洞察分级与来源：所有洞察含level/source/scenario，无L3推测
- ✅ D 场景分离与公平性：5场景独立、无合并均值；环境缺失已披露，无STRONG未披露项
- ✅ F 建议数值依据：移除默认参数建议；并发建议仅引用实测峰值并要求验证
- ✅ 输入与源码变更检查：skill/ 与 data/ 文件清单及 SHA-256 均未变化；所有新增产物仅位于 artifacts/

图表文字检查记录：data/chart_checks.json。完整记录逐项对源核对，三格式数字核查通过。
