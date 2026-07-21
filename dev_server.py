#!/usr/bin/env python3
"""
Lightweight local development server for the portfolio SPA.

Serves the `portfolio/` directory as the document root with:
  - static file serving (stdlib http.server)
  - live reload via SSE when HTML/CSS/JS/JSON/images change
  - friendly 404 pages for missing assets

No third-party dependencies. Python 3.9+ recommended.
"""

from __future__ import annotations

import argparse
import json
import mimetypes
import os
import sys
import threading
import time
import webbrowser
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Iterable
from urllib.parse import unquote, urlparse

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parent
DEFAULT_ROOT = REPO_ROOT / "portfolio"
DEFAULT_PORT = 5500
DEFAULT_HOST = "127.0.0.1"
POLL_INTERVAL = 0.5  # seconds between filesystem polls
WATCH_EXTENSIONS = {
    ".html",
    ".css",
    ".js",
    ".json",
    ".svg",
    ".png",
    ".jpg",
    ".jpeg",
    ".webp",
    ".gif",
    ".ico",
    ".pdf",
    ".woff",
    ".woff2",
    ".ttf",
    ".otf",
    ".map",
}
IGNORE_DIR_NAMES = {".git", "__pycache__", ".venv", "venv", "node_modules", ".cursor"}

LIVERELOAD_PATH = "/__livereload"
LIVERELOAD_SCRIPT = f"""
<script>
(function () {{
  if (window.__portfolioLiveReload) return;
  window.__portfolioLiveReload = true;
  var es;
  function connect() {{
    try {{
      es = new EventSource({LIVERELOAD_PATH!r});
      es.onmessage = function (ev) {{
        if (ev.data === "reload") location.reload();
      }};
      es.onerror = function () {{
        try {{ es.close(); }} catch (e) {{}}
        setTimeout(connect, 1500);
      }};
    }} catch (e) {{
      setTimeout(connect, 1500);
    }}
  }}
  connect();
}})();
</script>
""".strip()


# ---------------------------------------------------------------------------
# File watcher (stdlib polling — no watchdog dependency)
# ---------------------------------------------------------------------------


class FileWatcher:
    """Poll the document root for changes and notify waiters via a condition."""

    def __init__(
        self,
        root: Path,
        extensions: Iterable[str] = WATCH_EXTENSIONS,
        interval: float = POLL_INTERVAL,
    ) -> None:
        self.root = root.resolve()
        self.extensions = {ext.lower() for ext in extensions}
        self.interval = interval
        self.generation = 0
        self._snapshot: dict[str, float] = {}
        self._cond = threading.Condition()
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None

    def start(self) -> None:
        self._snapshot = self._scan()
        self._thread = threading.Thread(target=self._run, name="FileWatcher", daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop.set()
        with self._cond:
            self._cond.notify_all()
        if self._thread is not None:
            self._thread.join(timeout=2.0)

    def wait_for_change(self, since: int, timeout: float = 25.0) -> int:
        """Block until generation advances past `since`, or timeout. Returns current gen."""
        deadline = time.monotonic() + timeout
        with self._cond:
            while self.generation <= since and not self._stop.is_set():
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    break
                self._cond.wait(timeout=remaining)
            return self.generation

    def _run(self) -> None:
        while not self._stop.wait(self.interval):
            current = self._scan()
            if current != self._snapshot:
                self._snapshot = current
                with self._cond:
                    self.generation += 1
                    self._cond.notify_all()

    def _scan(self) -> dict[str, float]:
        result: dict[str, float] = {}
        root = self.root
        if not root.is_dir():
            return result
        for dirpath, dirnames, filenames in os.walk(root):
            dirnames[:] = [d for d in dirnames if d not in IGNORE_DIR_NAMES and not d.startswith(".")]
            for name in filenames:
                path = Path(dirpath) / name
                if path.suffix.lower() not in self.extensions:
                    continue
                try:
                    result[str(path)] = path.stat().st_mtime_ns
                except OSError:
                    continue
        return result


# ---------------------------------------------------------------------------
# HTTP handler
# ---------------------------------------------------------------------------


class PortfolioHandler(SimpleHTTPRequestHandler):
    """Serve portfolio/ as root with live-reload injection and friendly 404s."""

    protocol_version = "HTTP/1.1"

    # Set by main() before serving
    watcher: FileWatcher | None = None
    document_root: Path = DEFAULT_ROOT

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, directory=str(self.document_root), **kwargs)

    def log_message(self, format: str, *args) -> None:  # noqa: A003
        # Quieter logs: skip noisy SSE reconnects
        if args and isinstance(args[0], str) and LIVERELOAD_PATH in args[0]:
            return
        sys.stderr.write("[%s] %s\n" % (self.log_date_time_string(), format % args))

    def do_GET(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        if parsed.path == LIVERELOAD_PATH:
            self._handle_livereload(parsed)
            return
        super().do_GET()

    def do_HEAD(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        if parsed.path == LIVERELOAD_PATH:
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "text/event-stream")
            self.send_header("Cache-Control", "no-cache")
            self.end_headers()
            return
        super().do_HEAD()

    def _handle_livereload(self, parsed) -> None:
        watcher = self.watcher
        if watcher is None:
            self.send_error(HTTPStatus.SERVICE_UNAVAILABLE, "Live reload unavailable")
            return

        query = parsed.query or ""
        since = 0
        for part in query.split("&"):
            if part.startswith("since="):
                try:
                    since = int(part.split("=", 1)[1])
                except ValueError:
                    since = 0

        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "text/event-stream; charset=utf-8")
        self.send_header("Cache-Control", "no-cache, no-store")
        self.send_header("Connection", "keep-alive")
        self.send_header("X-Accel-Buffering", "no")
        self.end_headers()

        # Initial hello so the client knows the stream is alive
        try:
            self.wfile.write(f"data: {json.dumps({'generation': watcher.generation})}\n\n".encode())
            self.wfile.flush()
        except (BrokenPipeError, ConnectionResetError, OSError):
            return

        while True:
            new_gen = watcher.wait_for_change(since, timeout=20.0)
            if new_gen > since:
                try:
                    self.wfile.write(b"data: reload\n\n")
                    self.wfile.flush()
                except (BrokenPipeError, ConnectionResetError, OSError):
                    return
                since = new_gen
            else:
                # Heartbeat to keep the connection open through proxies/browsers
                try:
                    self.wfile.write(b": ping\n\n")
                    self.wfile.flush()
                except (BrokenPipeError, ConnectionResetError, OSError):
                    return

    def send_head(self):
        """Override to inject live-reload into HTML and improve 404s."""
        path = self.translate_path(self.path)
        parsed = urlparse(self.path)

        # Directory → index.html
        if os.path.isdir(path):
            parts = urllib_path_parts(parsed.path)
            if not parts or not parts[-1]:
                index = os.path.join(path, "index.html")
                if os.path.isfile(index):
                    path = index
                else:
                    return self._send_404(parsed.path)
            else:
                # Trailing-slash directories without index fall through to listing — block it
                index = os.path.join(path, "index.html")
                if os.path.isfile(index):
                    path = index
                else:
                    return self._send_404(parsed.path)

        if not os.path.isfile(path):
            return self._send_404(parsed.path)

        ctype = self.guess_type(path)
        try:
            f = open(path, "rb")
        except OSError:
            return self._send_404(parsed.path)

        try:
            fs = os.fstat(f.fileno())
            raw = f.read()
            f.close()

            # Inject live-reload script into HTML responses
            if ctype.startswith("text/html"):
                try:
                    text = raw.decode("utf-8")
                except UnicodeDecodeError:
                    text = raw.decode("utf-8", errors="replace")
                if "</body>" in text.lower():
                    # Case-insensitive replace of closing body tag
                    idx = text.lower().rfind("</body>")
                    text = text[:idx] + LIVERELOAD_SCRIPT + "\n" + text[idx:]
                else:
                    text = text + "\n" + LIVERELOAD_SCRIPT + "\n"
                raw = text.encode("utf-8")

            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(raw)))
            self.send_header("Last-Modified", self.date_time_string(fs.st_mtime))
            # Avoid sticky caches during local development
            self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
            self.end_headers()
            return _BytesReader(raw)
        except Exception:
            try:
                f.close()
            except Exception:
                pass
            raise

    def _send_404(self, request_path: str):
        body = (
            "<!DOCTYPE html>\n"
            "<html lang=\"en\">\n"
            "<head>\n"
            "  <meta charset=\"UTF-8\" />\n"
            "  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\" />\n"
            "  <title>404 — Not Found</title>\n"
            "  <style>\n"
            "    body { font-family: system-ui, sans-serif; background: #0f172a; color: #e2e8f0;\n"
            "           display: grid; place-items: center; min-height: 100vh; margin: 0; }\n"
            "    main { text-align: center; max-width: 36rem; padding: 2rem; }\n"
            "    h1 { color: #38bdf8; font-size: 3rem; margin: 0 0 0.5rem; }\n"
            "    code { background: #1e293b; padding: 0.15rem 0.4rem; border-radius: 4px; }\n"
            "    a { color: #7dd3fc; }\n"
            "  </style>\n"
            f"  {LIVERELOAD_SCRIPT}\n"
            "</head>\n"
            "<body>\n"
            "  <main>\n"
            "    <h1>404</h1>\n"
            "    <p>Asset not found during local development:</p>\n"
            f"    <p><code>{_escape(unquote(request_path))}</code></p>\n"
            "    <p><a href=\"/\">← Back to portfolio home</a></p>\n"
            "  </main>\n"
            "</body>\n"
            "</html>\n"
        ).encode("utf-8")
        self.send_response(HTTPStatus.NOT_FOUND)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-cache")
        self.end_headers()
        return _BytesReader(body)

    def guess_type(self, path: str) -> str:
        # Ensure modern types are recognized even on older Windows MIME DBs
        extra = {
            ".webp": "image/webp",
            ".svg": "image/svg+xml",
            ".woff": "font/woff",
            ".woff2": "font/woff2",
            ".json": "application/json",
            ".js": "text/javascript",
            ".mjs": "text/javascript",
            ".css": "text/css",
            ".html": "text/html; charset=utf-8",
            ".htm": "text/html; charset=utf-8",
        }
        ext = Path(path).suffix.lower()
        if ext in extra:
            return extra[ext]
        ctype, _ = mimetypes.guess_type(path)
        return ctype or "application/octet-stream"


class _BytesReader:
    """Minimal file-like object so SimpleHTTPRequestHandler can copyfile() it."""

    def __init__(self, data: bytes) -> None:
        self._data = data
        self._offset = 0

    def read(self, n: int = -1) -> bytes:
        if n is None or n < 0:
            chunk = self._data[self._offset :]
            self._offset = len(self._data)
            return chunk
        chunk = self._data[self._offset : self._offset + n]
        self._offset += len(chunk)
        return chunk

    def close(self) -> None:
        return None


def urllib_path_parts(path: str) -> list[str]:
    return [p for p in path.split("/")]


def _escape(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Serve portfolio/ with live reload (stdlib only).",
    )
    parser.add_argument(
        "--host",
        default=DEFAULT_HOST,
        help=f"Bind address (default: {DEFAULT_HOST})",
    )
    parser.add_argument(
        "--port",
        "-p",
        type=int,
        default=DEFAULT_PORT,
        help=f"Port (default: {DEFAULT_PORT})",
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=DEFAULT_ROOT,
        help=f"Document root (default: {DEFAULT_ROOT})",
    )
    parser.add_argument(
        "--no-browser",
        action="store_true",
        help="Do not open a browser tab on start",
    )
    parser.add_argument(
        "--poll",
        type=float,
        default=POLL_INTERVAL,
        help=f"Filesystem poll interval in seconds (default: {POLL_INTERVAL})",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    root = args.root.resolve()
    if not root.is_dir():
        print(f"Error: document root does not exist: {root}", file=sys.stderr, flush=True)
        return 1
    index = root / "index.html"
    if not index.is_file():
        print(f"Error: index.html not found in {root}", file=sys.stderr, flush=True)
        return 1

    watcher = FileWatcher(root, interval=args.poll)
    watcher.start()

    PortfolioHandler.watcher = watcher
    PortfolioHandler.document_root = root

    server = ThreadingHTTPServer((args.host, args.port), PortfolioHandler)
    url = f"http://{args.host}:{args.port}/"

    def say(msg: str = "") -> None:
        print(msg, flush=True)

    say("=" * 56)
    say("  Portfolio local development server")
    say("=" * 56)
    say(f"  Root:        {root}")
    say(f"  URL:         {url}")
    say(f"  Live reload: polling every {args.poll}s (stdlib, no deps)")
    say("  Stop:        Ctrl+C")
    say("=" * 56)

    if not args.no_browser:
        threading.Timer(0.6, lambda: webbrowser.open(url)).start()

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down...", flush=True)
    finally:
        watcher.stop()
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
