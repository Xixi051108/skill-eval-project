import json, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT.parent/'skill'/'scripts'))
from render_core import render_md,render_html,render_docx
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
d=json.loads((ROOT/'data/extracted_data.json').read_text(encoding='utf-8'))
a=json.loads((ROOT/'data/analysis_results.json').read_text(encoding='utf-8'))
ins=json.loads((ROOT/'data/insights.json').read_text(encoding='utf-8'))
m,rs=d['meta'],d['records']; ps,ss=m['products'],m['scenarios']; ts=sorted(m['concurrencies'])
cn={'oltp_point_select':'点查','oltp_read_only':'只读','oltp_read_write':'读写','oltp_write_only':'写入','oltp_update_index':'更新索引'}
def rows(p,s): return sorted([r for r in rs if r['product']==p and r['scenario']==s],key=lambda r:r['threads'])
def peak(p,s): return max(rows(p,s),key=lambda r:r['qps'])
def f(x,n=2): return f'{x:,.{n}f}' if x is not None else '-'
def tbl(h,r): return {'type':'table','headers':h,'rows':r}
def para(t): return {'type':'paragraph','text':t}
def img(path,cap): return {'type':'image','path':'charts/'+path,'caption':cap}
lm=m.get('log_meta',[])
issues=['测试分别在 09:30、13:30、17:30 开始，且 task_id 不同，非同步同批次交叉测试',
'元数据仅有共享硬件声明，未提供逐产品主机及资源分配核验',
'未提供逐产品数据库配置和资源配额，无法确认除产品外变量完全相同',
'每个产品只有一轮结果，缺少重复运行、预热和波动范围']
fair={'passed':False,'severity':'STRONG','issues':issues,'concurrencies':ts,'scenarios':ss}
a['product_compare']['fairness']=fair
a['fairness_warnings']=[{'severity':'STRONG','text':x} for x in issues]
peakq={s:{p:peak(p,s)['qps'] for p in ps} for s in ss}
ratio={s:{p:peakq[s][p]/peakq[s][ps[0]] for p in ps} for s in ss}
a['product_compare']['peak_qps']=peakq
a['product_compare']['ratio_matrix']=ratio
(ROOT/'data/analysis_results.json').write_text(json.dumps(a,ensure_ascii=False,indent=2),encoding='utf-8')
charts=ROOT/'charts'; matplotlib.rcParams['axes.unicode_minus']=False
for pi,p in enumerate(ps,1):
 for s in ss:
  rr=rows(p,s); fig,ax=plt.subplots(figsize=(8.5,5))
  ax.plot([r['threads'] for r in rr],[r['qps'] for r in rr],marker='o',linewidth=2)
  ax.set_xscale('log',base=2); ax.set_xticks(ts); ax.set_xticklabels(list(map(str,ts)))
  ax.set_title(f'{p}｜{cn[s]} 并发-QPS曲线'); ax.set_xlabel('并发数（threads）'); ax.set_ylabel('QPS')
  ax.grid(True,alpha=.3); fig.tight_layout(); fig.savefig(charts/f'product_{pi}_{s}.png'); plt.close(fig)
ch1=[para(f'本报告对比 {len(ps)} 个产品、{len(ss)} 个场景及 {len(rs)} 条记录。数据集配置、测试时长、场景和并发档对齐；公平性存在 STRONG 限制，结论仅为描述性比较。')]
key=[]
for s in ss:
 order=sorted(ps,key=lambda p:peakq[s][p],reverse=True); lead=(peakq[s][order[0]]/peakq[s][order[1]]-1)*100
 key.append([cn[s],order[0],f(peakq[s][order[0]],0),peak(order[0],s)['threads'],order[1],f(peakq[s][order[1]],0),order[2]])
 ch1.append({'type':'insight','level':'L1','source':f'records.{s}.qps','text':f'{cn[s]}峰值QPS排序：{" > ".join(order)}；第一名较第二名高{lead:.1f}%。'})
ch1.insert(1,tbl(['场景','第一名','峰值QPS','峰值并发','第二名','第二名QPS','第三名'],key))
envrows=[[x.get(k,'-') for k in ('product','engine','start_time','duration_sec','data_config','task_id')] for x in lm]
env=[{'id':'ch2a','title':'2.1 测试批次与数据集','blocks':[tbl(['产品','引擎','开始时间','时长秒','数据配置','任务ID'],envrows),para('三产品均为 tables=16、table_size=1,000,000，运行 300 秒；覆盖同五场景及 32、64、128、256、512、1000 并发。')]},
{'id':'ch2b','title':'2.2 硬件与公平性限制','blocks':[tbl(['环境项','声明'],[[k,v] for k,v in m.get('test_env',{}).items()]),para('公平性限制（STRONG）：'+ '；'.join(issues)),{'type':'bullet','items':issues}]},
{'id':'ch2c','title':'2.3 数据质量','blocks':[para(f'来源 {m.get("source_info",{}).get("value","-")}；{len(rs)} 条记录，TPS/QPS/P95/P99 均有值。输入为汇总数据，不含原始 sysbench 日志。')]}]
ch3=[]
for i,p in enumerate(ps,1):
 rr=[]
 for s in ss:
  for r in rows(p,s): rr.append([cn[s],r['threads'],f(r['tps']),f(r['qps']),f(r['p95_ms']),f(r['p99_ms'])])
 ch3.append({'id':f'ch3{i}','title':f'3.{i} {p}','blocks':[tbl(['场景','并发','TPS','QPS','P95 ms','P99 ms'],rr)]})
ch4=[]
for i,s in enumerate(ss,1):
 pr=[[p,peak(p,s)['threads'],f(peak(p,s)['qps'],0),f(peak(p,s)['p95_ms']),f(peak(p,s)['p99_ms'])] for p in ps]
 fixed=[]
 for t in ts:
  vals=[next(r for r in rows(p,s) if r['threads']==t) for p in ps]
  fixed.append([t]+[f(r['qps'],0) for r in vals]+[f(r['p95_ms']) for r in vals])
 ch4.append({'id':f'ch4{i}','title':f'4.{i} {cn[s]}（{s}）','blocks':[para('本场景独立比较；峰值取每产品六档并发中的最大 QPS。'),tbl(['产品','峰值并发','峰值QPS','峰值P95','峰值P99'],pr),tbl(['并发']+[p+' QPS' for p in ps]+[p+' P95(ms)' for p in ps],fixed),img(f'comparison_peak_{s}.png',cn[s]+'峰值QPS'),img(f'comparison_qps_{s}.png',cn[s]+'并发-QPS'),img(f'comparison_p95_{s}.png',cn[s]+'并发-P95')]})
ch4.append({'id':'ch4ratio','title':'4.6 峰值QPS比值矩阵','blocks':[para(f'以 {ps[0]} 为 1.00 基线，各产品取自身峰值。'),tbl(['场景']+ps,[[cn[s]]+[f'{ratio[s][p]:.3f}x' for p in ps] for s in ss]),img('comparison_radar.png','峰值QPS场景雷达图'),img('comparison_ladder.png','各场景峰值QPS天梯图')]})
ch4.append({'id':'ch4single','title':'4.7 单产品并发曲线','blocks':[para('各产品各场景的独立 QPS 曲线：')]+[img(f'product_{i}_{s}.png',p+'｜'+cn[s]) for i,p in enumerate(ps,1) for s in ss]})
rd={'cover':{'title':'数据库性能对比报告','subtitle':'TDSQL-B v22.7.3 vs MySQL 8.0.32 vs OceanBase 4.2','date':'2026-06-19','version':'v1.0'},'sections':[
{'id':'ch1','title':'第 1 章 测试结论','blocks':ch1},
{'id':'ch2','title':'第 2 章 环境与公平性','subsections':env},
{'id':'ch3','title':'第 3 章 全量性能数据','subsections':ch3},
{'id':'ch4','title':'第 4 章 按场景横向对比','subsections':ch4},
{'id':'ch5','title':'第 5 章 选型建议与边界','subsections':[{'id':'ch5a','title':'5.1 选型建议','blocks':[{'type':'bullet','items':['按目标业务场景和并发查看各节，不将五个场景合并成单一总分。','形成生产选型前，建议同环境、同配置进行多轮交叉运行并报告中位数及波动范围。','[待确认] 补充业务场景占比、延迟 SLA 和成本权重后再做加权决策；当前数据不足以指定综合胜者。']}]},{'id':'ch5b','title':'5.2 测试边界','blocks':[para('结果仅描述本次 sysbench 汇总数据，受测试时间、批次及运行次数限制，不能直接外推到所有生产负载。')]}]},
{'id':'ch6','title':'第 6 章 附录','subsections':[{'id':'ch6a','title':'6.1 数据来源','blocks':[para(m.get('source_info',{}).get('value','-'))]}]}]}
(ROOT/'report.md').write_text(render_md(rd),encoding='utf-8')
render_docx(rd,str(ROOT/'report.docx'),charts_abs_dir=str(charts))
(ROOT/'report.html').write_text(render_html(rd),encoding='utf-8')
ins['product_compare_insights']=[{'level':'L1','text':f'{cn[s]}峰值QPS排序：{" > ".join(sorted(ps,key=lambda p:peakq[s][p],reverse=True))}','source':f'records.{s}.qps','scenario':s} for s in ss]
ins['fairness_warnings']=[{'level':'L2','text':x,'source':'meta.log_meta','scenario':'all'} for x in issues]
(ROOT/'data/insights.json').write_text(json.dumps(ins,ensure_ascii=False,indent=2),encoding='utf-8')
print('完成：',len(list(charts.glob('*.png'))),'张图')

