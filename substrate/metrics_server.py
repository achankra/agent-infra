"""Serves the Prometheus endpoint every lab ends at.

Run the path, come back to the dashboard, see what moved.
"""
from __future__ import annotations

import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

STATE = Path(__file__).resolve().parent.parent / ".state"


class _Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path.rstrip("/") not in ("/metrics", ""):
            self.send_error(404)
            return
        f = STATE / "metrics.prom"
        body = f.read_text() if f.exists() else "# no runs yet\n"
        raw = body.encode()
        self.send_response(200)
        self.send_header("Content-Type", "text/plain; version=0.0.4")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def log_message(self, *a):
        pass


class MetricsServer:
    def __init__(self, host: str = "127.0.0.1", port: int = 8080) -> None:
        self.host, self.port = host, port
        self._srv: HTTPServer | None = None

    def start(self) -> str:
        self._srv = HTTPServer((self.host, self.port), _Handler)
        threading.Thread(target=self._srv.serve_forever, daemon=True).start()
        return f"http://{self.host}:{self.port}/metrics"

    def stop(self) -> None:
        if self._srv:
            self._srv.shutdown()


if __name__ == "__main__":
    import argparse, time
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=8080)
    a = ap.parse_args()
    srv = MetricsServer(a.host, a.port)
    print("serving", srv.start())
    print("Ctrl+C to stop")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        srv.stop()
