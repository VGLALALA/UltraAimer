"""Local-only web dashboard for UltraAImer configuration and controls."""

import argparse
import configparser
import json
import subprocess
import sys
import threading
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

STATIC_DIR = Path(__file__).with_name("web_static")
if not STATIC_DIR.is_dir():
    STATIC_DIR = Path(sys.prefix) / "web_static"
CONFIG_PATH = Path(__file__).with_name("config") / "config.ini"
MAX_BODY = 64 * 1024
PROCESS = None
PROCESS_LOCK = threading.Lock()


def read_config(path=CONFIG_PATH):
    parser = configparser.ConfigParser()
    parser.read(path, encoding="utf-8")
    return {section: dict(parser[section]) for section in parser.sections()}


def write_config(payload, path=CONFIG_PATH):
    if not isinstance(payload, dict):
        raise ValueError("Configuration must be an object")
    parser = configparser.ConfigParser()
    parser.read(path, encoding="utf-8")
    for section, values in payload.items():
        if section not in parser or not isinstance(values, dict):
            raise ValueError(f"Unknown configuration section: {section}")
        for key, value in values.items():
            if key not in parser[section]:
                raise ValueError(f"Unknown setting: {section}.{key}")
            parser[section][key] = str(value)
    temporary = path.with_suffix(".ini.tmp")
    with temporary.open("w", encoding="utf-8") as stream:
        parser.write(stream)
    temporary.replace(path)


def runtime_status():
    global PROCESS
    with PROCESS_LOCK:
        if PROCESS is not None and PROCESS.poll() is not None:
            PROCESS = None
        return {"running": PROCESS is not None, "pid": PROCESS.pid if PROCESS else None}


def start_runtime():
    global PROCESS
    with PROCESS_LOCK:
        if PROCESS is None or PROCESS.poll() is not None:
            PROCESS = subprocess.Popen([sys.executable, "-m", "main"], cwd=Path(__file__).parent)
        return {"running": True, "pid": PROCESS.pid}


def stop_runtime():
    global PROCESS
    with PROCESS_LOCK:
        if PROCESS is not None and PROCESS.poll() is None:
            PROCESS.terminate()
            try:
                PROCESS.wait(timeout=5)
            except subprocess.TimeoutExpired:
                PROCESS.kill()
                PROCESS.wait(timeout=2)
        PROCESS = None
    return {"running": False, "pid": None}


class DashboardHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(STATIC_DIR), **kwargs)

    def _json(self, payload, status=HTTPStatus.OK):
        body = json.dumps(payload).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _read_json(self):
        length = int(self.headers.get("Content-Length", "0"))
        if length > MAX_BODY:
            raise ValueError("Request is too large")
        return json.loads(self.rfile.read(length) or b"{}")

    def do_GET(self):
        route = urlparse(self.path).path
        if route == "/api/config":
            return self._json(read_config())
        if route == "/api/status":
            return self._json(runtime_status())
        return super().do_GET()

    def do_PUT(self):
        try:
            if urlparse(self.path).path != "/api/config":
                return self._json({"error": "Not found"}, HTTPStatus.NOT_FOUND)
            write_config(self._read_json())
            return self._json({"saved": True, "config": read_config()})
        except (ValueError, json.JSONDecodeError) as error:
            return self._json({"error": str(error)}, HTTPStatus.BAD_REQUEST)

    def do_POST(self):
        route = urlparse(self.path).path
        try:
            if route == "/api/start":
                return self._json(start_runtime())
            if route == "/api/stop":
                return self._json(stop_runtime())
            return self._json({"error": "Not found"}, HTTPStatus.NOT_FOUND)
        except OSError as error:
            return self._json({"error": str(error)}, HTTPStatus.INTERNAL_SERVER_ERROR)

    def log_message(self, message, *args):
        print(f"[web] {message % args}")


def main():
    parser = argparse.ArgumentParser(description="Run the local UltraAImer dashboard")
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()
    server = ThreadingHTTPServer(("127.0.0.1", args.port), DashboardHandler)
    print(f"UltraAImer dashboard: http://127.0.0.1:{args.port}", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        stop_runtime()
        server.server_close()


if __name__ == "__main__":
    main()
