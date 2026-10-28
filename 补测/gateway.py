"""Read-only local gateway to the original finance tools, with redacted receipts."""
from pathlib import Path
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import hashlib
import json
import os
import secrets
import shutil
import subprocess
import sys
import threading
import time


def secret_values():
    return [value for key, value in os.environ.items() if len(value) >= 8 and
            any(word in key.upper() for word in ('API_KEY', 'TOKEN', 'SECRET', 'PASSWORD'))]


def redact(text, values):
    for value in values:
        text = text.replace(value, '[REDACTED]')
    return text


def clean_env():
    env = {key: value for key, value in os.environ.items() if not any(
        word in key.upper() for word in ('API_KEY', 'TOKEN', 'SECRET', 'PASSWORD'))}
    env.update(PYTHONIOENCODING='utf-8', PYTHONDONTWRITEBYTECODE='1', MPLBACKEND='Agg')
    return env


def invoke(command, *, env, cwd, timeout):
    flags = (subprocess.CREATE_NO_WINDOW | subprocess.CREATE_NEW_PROCESS_GROUP) if os.name == 'nt' else 0
    process = subprocess.Popen(command, cwd=cwd, env=env, stdin=subprocess.DEVNULL,
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE, creationflags=flags,
                               start_new_session=os.name != 'nt')
    try:
        stdout, stderr = process.communicate(timeout=timeout)
        return process.returncode, stdout.decode('utf-8', 'replace'), stderr.decode('utf-8', 'replace'), False
    except subprocess.TimeoutExpired:
        stop(process)
        stdout, stderr = process.communicate()
        return process.returncode, stdout.decode('utf-8', 'replace'), stderr.decode('utf-8', 'replace'), True


def stop(process):
    if process.poll() is not None:
        return
    if os.name == 'nt':
        subprocess.run(['taskkill', '/PID', str(process.pid), '/T', '/F'],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False,
                       creationflags=subprocess.CREATE_NO_WINDOW)
    else:
        import signal
        os.killpg(process.pid, signal.SIGKILL)
    if process.poll() is None:
        process.kill()


class Gateway:
    def __init__(self, tools_root, output, limit=8):
        self.tools_root = Path(tools_root).resolve()
        self.output = Path(output)
        self.limit = limit
        self.receipts = []
        self.lock = threading.Lock()
        self.capability = secrets.token_hex(24)
        self.secrets = secret_values()
        self.key = os.environ.get('EM_API_KEY')
        gateway = self

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *args):
                pass

            def do_POST(self):
                if self.headers.get('Authorization') != 'Bearer ' + gateway.capability:
                    self.send_error(403)
                    return
                try:
                    size = int(self.headers.get('Content-Length', 0))
                    if not 0 < size <= 8192:
                        raise ValueError('invalid request size')
                    request = json.loads(self.rfile.read(size))
                    result = gateway.call(request['tool'], request['arguments'])
                except (ValueError, KeyError, TypeError) as error:
                    self.send_error(400, str(error))
                    return
                content = json.dumps(result, ensure_ascii=False).encode('utf-8')
                self.send_response(200)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.send_header('Content-Length', str(len(content)))
                self.end_headers()
                self.wfile.write(content)

        self.server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)

    def __enter__(self):
        self.output.mkdir(parents=True, exist_ok=True)
        self.thread.start()
        return self

    def __exit__(self, *args):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=3)

    def config(self):
        return {'url': 'http://127.0.0.1:' + str(self.server.server_port), 'capability': self.capability}

    def call(self, tool, arguments):
        if not isinstance(arguments, list) or not arguments or len(arguments) > 32 or any(
                not isinstance(value, str) or len(value) > 1000 for value in arguments):
            raise ValueError('invalid arguments')
        with self.lock:
            if len(self.receipts) >= self.limit:
                return {'status': 'budget_exhausted', 'error': 'per-task real tool budget exhausted'}
            sequence = len(self.receipts) + 1
            self.receipts.append({'sequence': sequence, 'status': 'running'})
        env = clean_env()
        if tool == 'westock-data' and arguments[0] in ('finance', 'quote', 'kline', 'search', 'help'):
            script = self.tools_root / 'westock-data/scripts/index.js'
            command = [shutil.which('node') or 'node', str(script), *arguments]
        elif tool == 'mx-finance-search' and arguments[0] == 'search':
            if not self.key:
                return self.record(sequence, tool, arguments, 'missing_key', '', 'EM_API_KEY is not configured', None, 0)
            script = self.tools_root / 'mx-finance-search/scripts/get_data.py'
            command = [sys.executable, str(script), ' '.join(arguments[1:]), '--no-save']
            env['EM_API_KEY'] = self.key
        else:
            return self.record(sequence, tool, arguments, 'unsupported', '', 'read-only tool or command not supported', None, 0)
        start = time.monotonic()
        if not script.is_file():
            return self.record(sequence, tool, arguments, 'unavailable', '', 'original tool script not found', None, 0)
        try:
            code, stdout, stderr, timed_out = invoke(command, env=env, cwd=self.output, timeout=50)
            status = 'timeout' if timed_out else 'ok' if code == 0 and stdout.strip() else 'unavailable'
        except OSError as error:
            code, stdout, stderr, status = None, '', str(error), 'unavailable'
        return self.record(sequence, tool, arguments, status, stdout, stderr, code,
                           time.monotonic() - start, hashlib.sha256(script.read_bytes()).hexdigest())

    def record(self, sequence, tool, arguments, status, stdout, stderr, code, seconds, script_hash=None):
        stdout, stderr = redact(stdout, self.secrets), redact(stderr, self.secrets)
        stem = 'tool-' + str(sequence).zfill(3)
        (self.output / (stem + '.stdout.txt')).write_text(stdout, encoding='utf-8', newline='')
        (self.output / (stem + '.stderr.txt')).write_text(stderr, encoding='utf-8', newline='')
        receipt = {'sequence': sequence, 'evidence_id': 'LIVE-' + str(sequence).zfill(3),
                   'tool': tool, 'arguments': arguments, 'status': status, 'exit_code': code,
                   'seconds': round(seconds, 3), 'script_sha256': script_hash,
                   'stdout_sha256': hashlib.sha256(stdout.encode()).hexdigest(),
                   'stdout_file': stem + '.stdout.txt', 'stderr_file': stem + '.stderr.txt'}
        with self.lock:
            self.receipts[sequence - 1] = receipt
            with (self.output / 'tools.jsonl').open('a', encoding='utf-8') as stream:
                stream.write(json.dumps(receipt, ensure_ascii=False) + '\n')
        # ponytail: return the original text, not a financial interpretation; semantic support is reviewed separately.
        return {**receipt, 'content': stdout, 'error': stderr if status != 'ok' else None}
