"""The S06 gate must read the $25 lock as a whole amount, not a substring.

All three read-only shop gates asserted the S06 lock with `grep -q '$25'`, which
also matches `$250`, `$2,500` and `$25.99`. A shop page that lost the lock and
printed a larger or fractional price therefore printed PASS. `$25` and `$25.00`
are the same lock and keep passing; no dollar can silently pass as $25.

Every run is against a local stub server; there is no real network.
"""

from __future__ import annotations

import subprocess
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SMOKE = ROOT / "scripts" / "live_shop_smoke.sh"
POST_DEPLOY = ROOT / "scripts" / "post_deploy_privacy_check.sh"
POST_BLOB = ROOT / "scripts" / "post_blob_unblock_check.sh"
ROBOTS = {"X-Robots-Tag": "noindex, nofollow, nosnippet"}


def _serve(routes, seen):
    class Handler(BaseHTTPRequestHandler):
        def _go(self):
            seen.append((self.command, self.path))
            spec = routes.get(self.path, (404, "nf"))
            code, body = spec[0], spec[1]
            headers = spec[2] if len(spec) == 3 else {}
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

        do_GET = do_POST = do_PATCH = _go

        def log_message(self, *args):
            pass

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server


def _healthy(s06_body: str) -> dict:
    routes = {
        "/": (200, "<html>Tỷ giá: 1 USD</html>"),
        "/api/fx": (200, '{"usd_cny":6.71}'),
        "/api/health": (200, '{"reading":"blob","productCount":62,"blob":{"readable":true}}'),
        "/api/export": (200, "ma\n", ROBOTS),
        "/api/submissions": (200, '{"submissions":[]}', ROBOTS),
        "/api/submissions/S06": (200, "{}", ROBOTS),
        "/api/ma/S06": (200, '{"code":"S06"}', ROBOTS),
        "/admin/shop": (200, "<html></html>", ROBOTS),
        "/m/S06": (200, s06_body),
    }
    for ma in ("A01", "A02", "S01", "P01"):
        routes[f"/m/{ma}"] = (200, "ok")
    return routes


def _run(script: Path, routes: dict, *, held: str = "K03"):
    seen: list[tuple[str, str]] = []
    server = _serve(routes, seen)
    base = f"http://127.0.0.1:{server.server_address[1]}"
    env = {
        "PATH": "/usr/bin:/bin",
        "INTAKE_BASE": base,
        "SHOP_BASE": base,
        "SHOP_HOSTS": base,
        "HELD_MAS": held,
        "CHECK_TIMEOUT": "5",
    }
    try:
        proc = subprocess.run(["bash", str(script)], env=env, capture_output=True, text=True, timeout=90)
    finally:
        server.shutdown()
    return proc, seen


LOCKS = ("<p>$25</p>", "<p>$25.00</p>")
NOT_THE_LOCK = ("<p>$250</p>", "<p>$2,500</p>", "<p>$25.99</p>", "<p>$125</p>")


@pytest.mark.parametrize("body", LOCKS)
def test_both_lock_spellings_pass_every_gate(body):
    for script in (SMOKE, POST_DEPLOY, POST_BLOB):
        proc, _ = _run(script, _healthy(body))
        assert proc.returncode == 0, f"{script.name}\n{proc.stdout}"
        assert "PASS" in proc.stdout


@pytest.mark.parametrize("body", NOT_THE_LOCK)
def test_any_price_that_is_not_the_lock_fails_every_gate(body):
    for script in (SMOKE, POST_DEPLOY, POST_BLOB):
        proc, _ = _run(script, _healthy(body))
        assert proc.returncode == 1, f"{script.name} passed on {body}\n{proc.stdout}"
        assert "/m/S06" in proc.stdout and "FAIL" in proc.stdout


def test_smoke_names_the_lock_when_it_fails():
    proc, _ = _run(SMOKE, _healthy("<p>$250</p>"))
    assert "S06 MUST BE $25, tell Boss" in proc.stdout


def test_gates_stay_read_only():
    for script in (SMOKE, POST_DEPLOY, POST_BLOB):
        _, seen = _run(script, _healthy("<p>$25</p>"))
        assert {method for method, _ in seen} == {"GET"}, script.name
