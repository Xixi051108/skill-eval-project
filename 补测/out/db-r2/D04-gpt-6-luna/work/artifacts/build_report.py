import json, os, sys
from pathlib import Path
from collections import defaultdict

ROOT=Path.cwd(); OUT=ROOT/'artifacts'; DATA=OUT/'data'; CH=OUT/'charts'
sys.path.insert(0,str(ROOT/'skill'/'scripts'))
from render_core import render_md, render_docx, render_html
src=json.loads((ROOT/'data'/'compare.json').read_text(encoding='utf-8'))
products=src['meta']['products']; scenarios=['oltp_write_only','oltp_update_index']; threads=[512,1000]
records=[r for r in src['records'] if r['scenario'] in scenarios and r['threads'] in threads]
assert len(records)==12
filtered_meta=dict(src['meta']); filtered_meta.update(scenarios=scenarios,concurrencies=threads,source_info={**src['meta']['source_info'],'value':'data/compare.json','rows_fetched':len(records)})
extracted={'meta':filtered_meta,'records':records}
intent={'data_source_type':'local_file','data_source_value':'data/compare.json','report_type':'custom','dimension_filters':{'test_name_keywords_or':[['write_only'],['update_index']]},'results_key_filters':{'threads':'512,1000'},'task_filters':{'task_id':None,'plan_id':None,'report_id':None},'iteration_config':None,'custom_config':{'focus_dimension':'自定义','dimensions':['product','scenario','threads'],'extra_questions':['仅分析三个产品在 oltp_write_only、oltp_update_index 两场景和 512、1000 并发下的 QPS、P95、P99，并逐产品逐场景给出有依据的产品选择建议。']},'other_info':'专项范围严格限制为上述 12 条记录。'}
(DATA/'intent.json').write_text(json.dumps(intent,ensure_ascii=False,indent=2),encoding='utf-8')
(DATA/'extracted_data.json').write_text(json.dumps(extracted,ensure_ascii=False,indent=2),encoding='utf-8')

# Per-scenario comparisons at the two requested concurrency levels.
by={(r['product'],r['scenario'],r['threads']):r for r in records}
chart_paths=[]
try:
 import matplotlib
 matplotlib.use('Agg')
 import matplotlib.pyplot as plt
 plt.rcParams['font.sans-serif']=['Microsoft YaHei','SimHei','Arial Unicode MS','DejaVu Sans']
 plt.rcParams['axes.unicode_minus']=False
 for s,cn in [('oltp_write_only','只写'),('oltp_update_index','索引更新')]:
  fig,axs=plt.subplots(1,3,figsize=(14,4.8))
  for ax,metric,label in zip(axs,['qps','p95_ms','p99_ms'],['QPS','P95 (ms)','P99 (ms)']):
   width=.24; x=[0,1]
   for i,p in enumerate(products):
    vals=[by[p,s,t][metric] for t in threads]
    bars=ax.bar([v+(i-1)*width for v in x],vals,width,label=p)
    for b,val in zip(bars,vals): ax.text(b.get_x()+b.get_width()/2,b.get_height(),f'{val:,.0f}' if metric=='qps' else f'{val:.2f}',ha='center',va='bottom',fontsize=7)
   ax.set_xticks(x,['512','1000']); ax.set_xlabel('并发 threads'); ax.set_title(label); ax.grid(axis='y',alpha=.2)
  axs[0].legend(fontsize=8)
  fig.suptitle(f'{cn}场景：三个产品在目标并发下的吞吐与尾延迟')
  fig.tight_layout()
  fn=f'custom_{s}.png'; fig.savefig(CH/fn,dpi=150,bbox_inches='tight'); plt.close(fig); chart_paths.append('charts/'+fn)
except Exception as e:
 raise RuntimeError(f'chart generation failed: {e}')

# Exact tables and objective findings.
sections=[]
sections.append({'id':'ch1','title':'第 1 章 分析目标','blocks':[],'subsections':[
 {'id':'ch1_1','title':'1.1 用户需求','blocks':[{'type':'paragraph','text':'限定比较 TDSQL-B v22.7.3、MySQL 8.0.32、OceanBase 4.2 在 oltp_write_only 与 oltp_update_index 场景、512 和 1000 并发下的 QPS、P95、P99；逐产品逐场景列数并据此给出选择建议。'}]},
 {'id':'ch1_2','title':'1.2 关键发现摘要','blocks':[{'type':'bullet','items':['oltp_write_only：TDSQL-B 在 512 和 1000 并发均有最高 QPS；两档尾延迟指标的最小值分属不同产品。','oltp_update_index：TDSQL-B 在两档均有最高 QPS；512 并发最低 P95 为 TDSQL-B，最低 P99 为 OceanBase；1000 并发最低 P95 为 OceanBase，最低 P99 为 TDSQL-B。','各任务的产品专属 task_id 和开始时间不同；可确认数据集配置与时长一致，但比较结果仍受独立任务运行差异影响。']}]}
]})
for si,s in enumerate(scenarios):
 cn='只写' if s=='oltp_write_only' else '索引更新'
 rows=[]
 for p in products:
  for t in threads:
   r=by[p,s,t]; rows.append([p,str(t),f"{r['qps']:,.2f}",f"{r['p95_ms']:.2f}",f"{r['p99_ms']:.2f}"])
 sections[0]['subsections'].append({'id':f'ch1_data{si}','title':f'1.{3+si} {s} 数据摘要','blocks':[{'type':'table','headers':['产品','并发','QPS','P95 (ms)','P99 (ms)'],'rows':rows}]})

analysis={'report_type':'custom','fairness_warnings':['INFO: 所有产品的 data_config 均为 tables=16, table_size=1000000，duration_sec=300；task_id 和 start_time 按产品不同，硬件为单一共享元数据，未提供逐任务核验信息。'],'custom':{'focus_dimension':'自定义','sample_size':12,'main_finding':'两个场景的两档并发中，TDSQL-B 均取得最高 QPS；尾延迟领先项随场景、并发与指标变化。'}}
insights={'items':[],'report_type':'custom'}
for s in scenarios:
 for t in threads:
  group=[by[p,s,t] for p in products]; top=max(group,key=lambda r:r['qps']); lo95=min(group,key=lambda r:r['p95_ms']); lo99=min(group,key=lambda r:r['p99_ms'])
  insights['items'].append({'level':'L1','text':f"{s}、{t} 并发：QPS 最高为 {top['product']}（{top['qps']:,.2f}）；P95 最低为 {lo95['product']}（{lo95['p95_ms']:.2f} ms）；P99 最低为 {lo99['product']}（{lo99['p99_ms']:.2f} ms）。",'source':'data/compare.json 筛选记录','scenario':s})
(DATA/'analysis_results.json').write_text(json.dumps(analysis,ensure_ascii=False,indent=2),encoding='utf-8')
(DATA/'insights.json').write_text(json.dumps(insights,ensure_ascii=False,indent=2),encoding='utf-8')

sections.append({'id':'ch2','title':'第 2 章 测试环境与数据范围','blocks':[],'subsections':[
 {'id':'ch2_1','title':'2.1 数据来源与子集','blocks':[{'type':'paragraph','text':'来源：data/compare.json（本地 JSON）。原始记录 90 条；按两个场景与两个并发值筛选后共 12 条（3 产品 × 2 场景 × 2 并发）。报告及图表仅使用该 12 条记录。产品：'+ '、'.join(products)+'。'}]},
 {'id':'ch2_2','title':'2.2 环境和比较前提','blocks':[{'type':'table','headers':['核查项','记录值','解释'],'rows':[['数据配置','tables=16, table_size=1000000','三产品记录一致'],['测试时长','300 秒','三产品记录一致'],['并发档','512、1000','本报告一致'],['任务标识/开始时间','各产品不同','独立任务，无法据此确认运行条件完全相同'],['硬件信息','源文件仅提供共享环境元数据','无逐任务硬件对照信息']]} ,{'type':'paragraph','text':'公平性说明：数据配置、时长、场景和并发档可对齐；task_id 与 start_time 各异，且没有逐任务硬件核验记录。因此下文是这批测试记录中的观测结果，不能单独证明产品差异完全由数据库软件造成。'}]},
 {'id':'ch2_3','title':'2.3 指标口径与假设','blocks':[{'type':'paragraph','text':'QPS 按源记录原值列示；P95、P99 单位为毫秒，延迟越低代表尾部响应越快。选择建议仅针对限定场景、并发和这批记录；未纳入成本、可靠性、运维能力或业务约束。'}]}
]})
for si,s in enumerate(scenarios):
 cn='只写' if s=='oltp_write_only' else '索引更新'
 table=[]
 for p in products:
  for t in threads:
   r=by[p,s,t]; table.append([p,str(t),f"{r['qps']:,.2f}",f"{r['p95_ms']:.2f}",f"{r['p99_ms']:.2f}"])
 sections.append({'id':f'ch3_{si}','title':f'第 3 章 {s} 专项分析','blocks':[],'subsections':[
 {'id':f'ch3_{si}_1','title':f'3.{si+1} 逐产品数据（{cn}）','blocks':[{'type':'table','headers':['产品','并发 threads','QPS','P95 (ms)','P99 (ms)'],'rows':table},{'type':'image','path':chart_paths[si],'caption':f'{cn}场景在 512 与 1000 并发下的 QPS、P95、P99'}]},
 {'id':f'ch3_{si}_2','title':f'3.{si+1}.1 数据解读','blocks':[{'type':'bullet','items':[f"{t} 并发：QPS 最高 {max((by[p,s,t] for p in products),key=lambda r:r['qps'])['product']}；最低 P95 {min((by[p,s,t] for p in products),key=lambda r:r['p95_ms'])['product']}；最低 P99 {min((by[p,s,t] for p in products),key=lambda r:r['p99_ms'])['product']}。" for t in threads]}]}
]})

sections.append({'id':'ch4','title':'第 4 章 结论与产品选择建议','blocks':[],'subsections':[
 {'id':'ch4_1','title':'4.1 主要发现','blocks':[{'type':'image','path':'charts/custom_overview.png','caption':'512 并发下两个目标场景的 QPS 横向总览'},{'type':'insight','level':'L1','source':'data/compare.json 筛选记录（12 条）','text':'oltp_write_only：TDSQL-B 在 512 并发 QPS 为 67,175.43、1000 并发为 62,141.15，均为三产品最高。oltp_update_index：TDSQL-B 在 512 并发 QPS 为 14,746.99、1000 并发为 13,965.57，也均为最高。'}, {'type':'insight','level':'L2','source':'对每个场景/并发的三产品记录分别比较 QPS、P95、P99','text':'吞吐优势不代表三个延迟分位也同时领先。write_only 512 最低 P95/P99 分别是 MySQL（36.16/51.07 ms）；1000 最低 P95 为 OceanBase（72.95 ms），P99 为 OceanBase（100.08 ms）。update_index 512 最低 P95 为 TDSQL-B（50.85 ms）、最低 P99 为 OceanBase（70.27 ms）；1000 最低 P95 为 OceanBase（100.69 ms）、最低 P99 为 TDSQL-B（137.41 ms）。'}]},
 {'id':'ch4_2','title':'4.2 选择建议','blocks':[{'type':'bullet','items':['若 oltp_write_only 的首要目标是这两档并发下的最高吞吐，优先考虑 TDSQL-B：相对第二名，512 并发 QPS 高约 11.0%，1000 并发高约 10.1%。依据为本报告列出的实测 QPS。','若 oltp_update_index 的首要目标是最高吞吐，优先考虑 TDSQL-B：相对第二名，512 并发高约 12.9%，1000 并发高约 13.3%。','若决策目标是尾延迟，需按 SLO 选择：write_only 在 512 下 MySQL 的 P95/P99 最低，1000 下 OceanBase 两项最低；update_index 在 512 下 TDSQL-B 的 P95 最低而 OceanBase 的 P99 最低，1000 下 TDSQL-B 的 P99 最低、OceanBase 的 P95 最低。','建议先用目标业务负载重复压测并按自身 SLO（尤其 P99）筛选，再决定上线产品；本报告未评估成本与非性能因素。']}]},
 {'id':'ch4_3','title':'4.3 不确定性与后续验证','blocks':[{'type':'paragraph','text':'结论基于每个产品/场景/并发单条记录，未提供重复运行波动或置信区间。运行开始时间和任务标识不同，硬件元数据未逐任务展开。产品推荐是限定指标范围内的条件性选择，不应外推到其他场景、并发、数据规模或生产负载。'}]}
]})

report={'cover':{'title':'数据库专项性能报告','subtitle':'oltp_write_only 与 oltp_update_index｜512、1000 并发｜3 产品','date':'2026-06-19','version':'v1.0'},'sections':sections}
(OUT/'report.md').write_text(render_md(report),encoding='utf-8')
render_docx(report,str(OUT/'report.docx'),charts_abs_dir=str(CH))
(OUT/'report.html').write_text(render_html(report),encoding='utf-8')
(OUT/'docs'/'analysis_proposal.md').write_text('# 分析方案\n\n报告类型：custom。分析范围固定为 3 产品 × 2 场景（oltp_write_only、oltp_update_index）× 2 并发（512、1000），共 12 条。指标为 QPS、P95、P99。按每个场景和并发独立比较三个产品，并根据数据配置、时长、任务标识与时间披露可比性限制。产品建议按吞吐优先或尾延迟优先分别提出。\n',encoding='utf-8')
(OUT/'data'/'block_map.md').write_text('# 报告区块映射\n\n- 第 1 章：用户需求、发现摘要及核心数据\n- 第 2 章：来源、筛选范围、环境公平性与指标口径\n- 第 3 章：两个指定场景的逐产品逐并发数据、图表和解读\n- 第 4 章：证据、条件性选型建议和不确定性\n',encoding='utf-8')
print('records',len(records),'charts',len(list(CH.glob('*.png'))),'sizes',[(p.name,p.stat().st_size) for p in [OUT/'report.md',OUT/'report.docx',OUT/'report.html']])
