"""The post-deploy gates must check every held mã in data/held.json, not a stale copy.

data/held.json is the one held source. A held mã that is publicly live on the
shop makes the gate FAIL; before this, the gate carried its own nine-mã list
and S14, V05 and the other held mãs were never fetched, so a live held mã
still printed PASS.
"""

from __future__ import annotations

import json
import os
import subprocess
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import held_mas

ROOT = Path(__file__).resolve().parents[2]
HELD_JSON = ROOT / "data" / "held.json"
POST_DEPLOY = ROOT / "scripts" / "post_deploy_privacy_check.sh"
SMOKE = ROOT / "scripts" / "live_shop_smoke.sh"
ROBOTS = {"X-Robots-Tag": "noindex, nofollow, nosnippet"}


def _held_codes() -> list[str]:
    data = json.loads(HELD_JSON.read_text(encoding="utf-8"))
    return list(data["heldIncomplete"]) + list(data["neverList"]) + ["Q02"]


def _serve(routes):
    class H(BaseHTTPRequestHandler):
        def do_GET(self):
            spec = routes.get(self.path, (404, "nf"))
            code, body = spec[0], spec[1]
            headers = spec[2] if len(spec) == 3 else {}
            self.send_response(code)
            for key, value in headers.items():
                self.send_header(key, value)
            self.end_headers()
            self.wfile.write(body.encode())

        def log_message(self, *a):
            pass

    srv = ThreadingHTTPServer(("127.0.0.1", 0), H)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv


def _healthy(held: list[str]):
    routes = {
        path: (200, '{"ok":true}', ROBOTS)
        for path in ("/api/export", "/api/submissions", "/api/submissions/S06", "/api/ma/S06", "/admin/shop")
    }
    routes["/api/health"] = (200, '{"reading":"blob","blob":{"readable":true}}')
    routes["/m/S06"] = (200, "<p>$25</p>")
    for ma in held:
        routes[f"/m/{ma}"] = (404, "nf")
    return routes


def _run(script: Path, routes, held: list[str] | None):
    srv = _serve(routes)
    base = f"http://127.0.0.1:{srv.server_address[1]}"
    env = {"PATH": "/usr/bin:/bin", "INTAKE_BASE": base, "SHOP_BASE": base,
           "SHOP_HOSTS": base, "CHECK_TIMEOUT": "5"}
    if held is not None:
        env["HELD_MAS"] = " ".join(held)
    try:
        return subprocess.run(["bash", str(script)], env=env, capture_output=True, text=True, timeout=90)
    finally:
        srv.shutdown()


def test_helper_reads_the_whole_held_list_and_q02() -> None:
    codes = held_mas.held_mas()
    assert codes == list(dict.fromkeys(held_mas.norm_ma(code) for code in _held_codes()))
    assert len(codes) == len(_held_codes())
    for code in ("S14", "V05", "A24", "Q02"):
        assert code in codes


def test_helper_canonicalises_an_override() -> None:
    assert held_mas.held_mas(" k3 s14 S006 q02 k03 ") == ["K03", "S14", "S06", "Q02"]


def test_cli_prints_the_list() -> None:
    r = subprocess.run(["python3", str(ROOT / "scripts" / "held_mas.py")],
                       capture_output=True, text=True, env={"PATH": "/usr/bin:/bin"})
    assert r.returncode == 0, r.stderr
    assert r.stdout.split() == held_mas.held_mas()


def test_post_deploy_gate_checks_every_held_ma_in_dry_run() -> None:
    r = subprocess.run(["bash", str(POST_DEPLOY), "--dry-run", "--with-privacy"],
                       capture_output=True, text=True,
                       env={"PATH": "/usr/bin:/bin", "HELD_MAS": ""})
    assert r.returncode == 0, r.stdout + r.stderr
    for code in held_mas.held_mas():
        assert f"/m/{code} -> 404" in r.stdout, code


def test_post_deploy_gate_fails_when_a_held_ma_outside_the_old_nine_is_live() -> None:
    """S14 is held in data/held.json and was missing from the gate's own list."""
    held = held_mas.held_mas()
    assert "S14" in held
    routes = _healthy(held)
    routes["/m/S14"] = (200, "held mã S14 is publicly live")
    r = _run(POST_DEPLOY, routes, held)
    assert r.returncode == 1, r.stdout
    assert "FAIL  shop /m/S14 held" in r.stdout
    assert "HELD MÃ VISIBLE" in r.stdout


def test_post_deploy_gate_fails_on_the_default_held_list() -> None:
    """No HELD_MAS override: the gate must still read data/held.json itself."""
    held = held_mas.held_mas()
    routes = _healthy(held)
    routes["/m/V05"] = (200, "held mã V05 is publicly live")
    r = _run(POST_DEPLOY, routes, None)
    assert r.returncode == 1, r.stdout
    assert "FAIL  shop /m/V05 held" in r.stdout
    assert "HELD MÃ VISIBLE" in r.stdout


def test_post_deploy_gate_passes_when_every_held_ma_is_404() -> None:
    held = held_mas.held_mas()
    r = _run(POST_DEPLOY, _healthy(held), held)
    assert r.returncode == 0, r.stdout
    assert "POST-DEPLOY PRIVACY CHECK: PASS" in r.stdout


def test_live_smoke_checks_the_same_held_list() -> None:
    r = subprocess.run(["bash", str(SMOKE), "--dry-run"], capture_output=True, text=True,
                       env={"PATH": "/usr/bin:/bin", "SHOP_HOSTS": "http://127.0.0.1:9", "HELD_MAS": ""})
    assert r.returncode == 0, r.stdout + r.stderr
    for code in held_mas.held_mas():
        assert f"/m/{code} -> 404" in r.stdout, code
