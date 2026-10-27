"""Probe the original finance dependencies; this is NOT an Agent evaluation.

Use existing EM_API_KEY only. Save redacted stdout/stderr and receipt metadata.
No key is requested, created, copied to a file, or included in the command.
"""
from pathlib import Path
from datetime import datetime,timezone
import argparse
import json
import os
import shutil
import subprocess
import sys
import time
import hashlib

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--tools-root',type=Path,required=True)
    ap.add_argument('--node',default=shutil.which('node'))
    ap.add_argument('--out',type=Path,required=True)
    args=ap.parse_args()
    args.out.mkdir(parents=True,exist_ok=False)
    secrets=[v for k,v in os.environ.items() if v and len(v)>=8 and any(t in k.upper() for t in ('API_KEY','TOKEN','SECRET','PASSWORD'))]
    def redact(text):
        for secret in secrets:
            text=text.replace(secret,'[REDACTED]')
        return text
    commands={
        'westock':[args.node,str((args.tools_root/'westock-data/scripts/index.js').resolve()),'finance','hk00700','--num','8'],
        'search':[sys.executable,str((args.tools_root/'mx-finance-search/scripts/get_data.py').resolve()),'腾讯控股 2024 年全年 营收 年报','--no-save']}
    receipts=[]
    for name,cmd in commands.items():
        item={'dependency':name,'command':cmd,'at':datetime.now(timezone.utc).isoformat(),'is_agent_test':False}
        if cmd[1] and Path(cmd[1]).is_file():
            item['script_sha256']=hashlib.sha256(Path(cmd[1]).read_bytes()).hexdigest()
        start=time.monotonic()
        if not cmd[0] or not Path(cmd[1]).is_file():
            item.update(status='BLOCKED',reason='required executable/script is unavailable')
        elif name=='search' and not os.environ.get('EM_API_KEY'):
            item.update(status='BLOCKED',reason='EM_API_KEY is not configured')
        else:
            env=os.environ.copy();env['PYTHONIOENCODING']='utf-8'
            try:
                p=subprocess.run(cmd,cwd=args.out,env=env,capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=40)
                (args.out/f'{name}.stdout.txt').write_text(redact(p.stdout),encoding='utf-8')
                (args.out/f'{name}.stderr.txt').write_text(redact(p.stderr),encoding='utf-8')
                item.update(status='REVIEW' if p.returncode==0 else 'BLOCKED',exit_code=p.returncode,reason='dependency returned; source/time/currency require review' if p.returncode==0 else 'dependency invocation failed')
            except subprocess.TimeoutExpired:
                item.update(status='BLOCKED',reason='dependency timeout')
        item['seconds']=round(time.monotonic()-start,3)
        receipts.append(item)
        print(name,item['status'])
    (args.out/'results.json').write_text(json.dumps({'kind':'live_dependency_probe','results':receipts,'note':'真实依赖调用可用性记录；不能替代Agent验真测试或独立真值核验。'},ensure_ascii=False,indent=2),encoding='utf-8')

if __name__=='__main__':
    main()
