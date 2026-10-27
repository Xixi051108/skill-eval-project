"""Controlled finance test double. No network or real credentials are used."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import sys

def main():
    tool, command, *args = sys.argv[1:]
    fixture=json.loads(Path('tools.json').read_text(encoding='utf-8'))
    match=next((r for r in fixture['responses'] if r['tool']==tool and r['command']==command and (not r.get('symbol') or command=='search' or r['symbol'] in args)),None)
    result=match or {'tool':tool,'command':command,'status':'not_found','payload':{'error':'No matching fixture for these arguments'}}
    row={**result,'arguments':args,'at':datetime.now(timezone.utc).isoformat()}
    row['response_sha256']=hashlib.sha256(json.dumps(result,sort_keys=True,ensure_ascii=False).encode()).hexdigest()
    with Path('tools.jsonl').open('a',encoding='utf-8') as f:
        f.write(json.dumps(row,ensure_ascii=False)+'\n')
    print(json.dumps(result,ensure_ascii=False))

if __name__=='__main__':
    main()
