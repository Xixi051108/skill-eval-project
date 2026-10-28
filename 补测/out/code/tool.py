"""Agent-side client. The real finance credential stays in the host process."""
from pathlib import Path
import json
import sys
from urllib.request import Request, urlopen


def main():
    config = json.loads(Path('endpoint.json').read_text(encoding='utf-8'))
    tool, *arguments = sys.argv[1:]
    request = Request(config['url'], data=json.dumps({'tool': tool, 'arguments': arguments}).encode(),
                      headers={'Content-Type': 'application/json', 'Authorization': 'Bearer ' + config['capability']})
    with urlopen(request, timeout=70) as response:
        print(response.read().decode('utf-8'))


if __name__ == '__main__':
    main()
