"""A blank or whitespace-only SHOP_HOSTS must not skip every shop check.

`SHOP_HOSTS` is a space-separated list. `${SHOP_HOSTS:-default}` only replaces
an *empty* value, so `SHOP_HOSTS="   "` was kept, word-split to zero words, and
the `for s in $SHOPS` loop never ran. Every shop check — health, the S06 lock
and each held 404 — was silently skipped while the intake check still ran, so
the smoke reported `LIVE SHOP SMOKE: PASS` without fetching a single shop page.

A blank list is not a host list, so it now falls back to the two real shop
hosts and the shop checks always run. These tests read the resolved list from
`--dry-run` and drive a local stub server; there is no real network call.
"""

from __future__ import annotations

import subprocess
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "live_shop_smoke.sh"
DEFAULT_HOSTS = "https://sassy-closet-shop.vercel.app https://sassycloset.vercel.app"


def _dry_run(shop_hosts):
    env = {
        "PATH": "/usr/bin:/bin",
        "INTAKE_BASE": "http://127.0.0.1:9",
        "HELD_MAS": "K03",
        "CHECK_TIMEOUT": "2",
    }
    if shop_hosts is not None:
        env["SHOP_HOSTS"] = shop_hosts
    return subprocess.run(
        ["bash", str(SCRIPT), "--dry-run"], env=env, capture_output=True, text=True, timeout=60
    )


@pytest.mark.parametrize("blank", ["", " ", "   ", "\t", " \t \n "])
def test_blank_shop_hosts_resolves_to_the_real_hosts(blank):
    """A blank list must resolve to the two shop hosts, not to an empty list."""
    proc = _dry_run(blank)
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert f"shops=[{DEFAULT_HOSTS}]" in proc.stdout
    # Every shop check is still listed for both hosts.
    assert proc.stdout.count("/api/health -> 200") == 2
    assert proc.stdout.count("/m/S06 -> 200 shows $25") == 2
    assert proc.stdout.count("/m/K03 -> 404 (held)") == 2


def test_blank_list_is_not_printed_as_an_empty_check_list():
    """The regression printed `shops=[]`, which skipped every shop check silently."""
    proc = _dry_run("   ")
    assert "shops=[]" not in proc.stdout


def test_explicit_host_list_is_kept_verbatim():
    proc = _dry_run("http://a.example http://b.example")
    assert "shops=[http://a.example http://b.example]" in proc.stdout


def _serve(routes, seen):
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            seen.append(self.path)
            code, body = routes.get(self.path, (404, "nf"))
            data = body.encode()
            try:
                self.send_response(code)
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)
            except (BrokenPipeError, ConnectionResetError):
                pass

        def log_message(self, *args):
            pass

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server


HEALTHY = {
    "/api/health": (200, '{"reading":"blob","productCount":62}'),
    "/m/S06": (200, "<p>$25</p>"),
    "/": (200, "<h1>intake</h1>"),
}


def test_one_real_host_still_runs_every_shop_check():
    """A real single host keeps working, and every check is issued once."""
    seen: list[str] = []
    server = _serve(HEALTHY, seen)
    base = f"http://127.0.0.1:{server.server_address[1]}"
    env = {
        "PATH": "/usr/bin:/bin",
        "INTAKE_BASE": base,
        "SHOP_HOSTS": base,
        "HELD_MAS": "K03",
        "CHECK_TIMEOUT": "5",
    }
    try:
        proc = subprocess.run(["bash", str(SCRIPT)], env=env, capture_output=True, text=True, timeout=90)
    finally:
        server.shutdown()
    assert proc.returncode == 0, proc.stdout
    for path in ("/api/health", "/m/S06", "/m/K03", "/"):
        assert path in seen, f"{path} was not requested"
