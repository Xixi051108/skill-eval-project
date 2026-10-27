"""Apply separately authored semantic reviews without hiding automatic failures.

Review JSON: [{run, response_sha256, reviewer, method, decision, notes}].
method must identify human or LLM review; notes must cite evidence.
"""
from pathlib import Path
from copy import deepcopy
from datetime import datetime,timezone
import argparse
import hashlib
import json
import shutil

from judge import load,check,verdict
from run import dump,write_report

def apply(result,review,response_bytes):
    if hashlib.sha256(response_bytes).hexdigest()!=review['response_sha256']:
        raise ValueError('Review is stale: response hash differs')
    if review['decision'] not in ('PASS','FAIL') or review['method'] not in ('human','LLM'):
        raise ValueError('Review decision/method is invalid')
    if not review.get('reviewer') or len(review.get('notes',''))<15:
        raise ValueError('Reviewer and evidence notes are required')
    updated=deepcopy(result)
    updated['semantic_review']='COMPLETE: '+review['method']
    updated['review']=review
    checks=[c for c in updated.get('checks',[]) if c['name']!='语义复核通过']
    if checks:
        check(checks,'语义复核通过','R4',review['decision']=='PASS',review['notes'],'论证、边界与来源一致')
        updated.update(verdict(checks))
    if result['status']=='FAIL':
        updated['status']='FAIL'
        return updated  # A reviewer cannot silently override a failed mandatory check.
    updated['status']=review['decision']
    if review['decision']=='FAIL':
        updated['reason']='Semantic review failed: '+review['notes']
    return updated

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--source',type=Path,required=True)
    ap.add_argument('--reviews',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True)
    args=ap.parse_args()
    args.out.mkdir(parents=True,exist_ok=False)
    source=load(args.source/'results.json')
    reviews={r['run']:r for r in load(args.reviews)}
    results=[]
    repeats=[]
    repeated=load(args.source/'repeats.json') if (args.source/'repeats.json').is_file() else []
    for result,is_repeat in [(r,False) for r in source['results']]+[(r,True) for r in repeated]:
        review=reviews.get(result['run'])
        if review:
            result=apply(result,review,(args.source/result['run']/'response.txt').read_bytes())
        dest=args.out/result['run']
        shutil.copytree(args.source/result['run'],dest)
        dump(dest/'result.json',result)
        (repeats if is_repeat else results).append(result)
    metadata={**source['metadata'],'kind':'semantic_review','reviewed_at':datetime.now(timezone.utc).isoformat(),'source_run':str(args.source.resolve()),'reviews':str(args.reviews.resolve()),'warning':'复核结论保留方法与来源；LLM复核不得表述为独立人工评审。'}
    write_report(args.out,results,metadata)
    if repeated:
        dump(args.out/'repeats.json',repeats)
    print(json.dumps({'reviewed':len(reviews),'out':str(args.out)},ensure_ascii=False))

if __name__=='__main__':
    main()
