"""Live-check scripts must GET /admin open-by-link and noindex.

No network. Response bodies are not echoed. Fixture rates only.
"""

import re
import subprocess
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
UNBLOCK = ROOT / "post_blob_unblock_check.sh"
PRIVACY = ROOT / "post_deploy_privacy_check.sh"
ROBOTS = {"X-Robots-Tag": "noindex, nofollow, nosnippet"}
SENTINEL = "SENTINEL-ADMIN-BODY"


def _routes(admin):
    routes = {
        "/": (200, "<html>rate</html>"),
        "/api/fx": (200, '{"usd_cny":6.71}', ROBOTS),
        "/api/submissions": (200, '{"submissions":[]}', ROBOTS),
        "/api/submissions/S06": (404, "{}", ROBOTS),
        "/api/ma/S06": (200, '{"code":"S06"}', ROBOTS),
        "/api/export": (200, "ma\n", ROBOTS),
        "/admin": admin,
        "/admin/shop": (200, "<main>shop tools</main>", ROBOTS),
        "/api/health": (
            200,
            '{"reading":"blob","blob":{"configured":true,"readable":true}}',
            ROBOTS,
        ),
        "/m/S06": (200, "<p>$25</p>"),
        "/m/K03": (404, "nf"),
    }
    for ma in ("A01", "A02", "S01", "P01"):
        routes[f"/m/{ma}"] = (200, "ok")
    return routes


def _serve(routes, seen):
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            seen.append(self.command)
            spec = routes.get(self.path, (404, "nf"))
            headers = {}
            if len(spec) == 3:
                code, body, headers = spec
            else:
                code, body = spec
            data = body.encode()
            try:
                self.send_response(code)
                for key, value in headers.items():
                    self.send_header(key, value)
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)
            except (BrokenPipeError, ConnectionResetError):
                pass

        def do_POST(self):
            seen.append(self.command)
            self.send_response(405)
            self.end_headers()

        def log_message(self, *_args):
            pass

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server


def _run(script, routes):
    seen = []
    server = _serve(routes, seen)
    base = f"http://127.0.0.1:{server.server_address[1]}"
    try:
        result = subprocess.run(
            ["bash", str(script)],
            env={
                "PATH": "/usr/bin:/bin",
                "INTAKE_BASE": base,
                "SHOP_BASE": base,
                "CHECK_TIMEOUT": "5",
                "HELD_MAS": "K03",
            },
            capture_output=True,
            text=True,
            timeout=60,
        )
    finally:
        server.shutdown()
    return result, seen


def _reported_status(line: str) -> int | None:
    match = re.search(r"\bhttp (\d{3})\b", line)
    if match is None:
        return None
    return int(match.group(1))


def _admin_lines(stdout: str, prefix: str) -> list[str]:
    lines = []
    for line in stdout.splitlines():
        if not line.startswith(prefix):
            continue
        head = line.split("(", 1)[0]
        if "/admin" in head and "/admin/" not in head:
            lines.append(line)
    return lines


def test_admin_open_and_noindex_passes_both_checks():
    routes = _routes((200, "<main>Kit export CSV</main>", ROBOTS))
    for script in (UNBLOCK, PRIVACY):
        result, seen = _run(script, routes)
        assert result.returncode == 0, result.stdout
        assert _admin_lines(result.stdout, "PASS"), result.stdout
        assert seen
        assert all(method == "GET" for method in seen)


def test_admin_missing_noindex_fails_without_echoing_the_body():
    routes = _routes((200, SENTINEL))
    for script in (UNBLOCK, PRIVACY):
        result, seen = _run(script, routes)
        assert result.returncode == 1, result.stdout
        failed = _admin_lines(result.stdout, "FAIL")
        assert failed, result.stdout
        assert any("X-Robots-Tag" in line for line in failed)
        assert SENTINEL not in result.stdout + result.stderr
        assert all(method == "GET" for method in seen)


def test_admin_login_wall_fails_without_echoing_the_body():
    routes = _routes((401, SENTINEL, ROBOTS))
    for script in (UNBLOCK, PRIVACY):
        result, seen = _run(script, routes)
        assert result.returncode == 1, result.stdout
        failed = _admin_lines(result.stdout, "FAIL")
        assert failed, result.stdout
        assert any(_reported_status(line) == 401 for line in failed)
        assert SENTINEL not in result.stdout + result.stderr
        assert all(method == "GET" for method in seen)
