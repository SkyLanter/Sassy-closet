"""post_deploy_privacy_check.sh against a local stub server (no real network)."""
import subprocess
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "post_deploy_privacy_check.sh"
J401 = '{"ok":false,"error":"Unauthorized."}'
HELD = ("K03", "Q02")
SENTINEL = "SENTINEL-VALUE-777"  # must never be echoed by the script


def _serve(routes, seen):
    class H(BaseHTTPRequestHandler):
        def _go(self):
            seen.append((self.command, self.path))
            spec = routes.get((self.command, self.path), routes.get(self.path, (404, "nf")))
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
                pass  # client (curl) closed early; stub must not crash the run

        do_GET = do_POST = do_PATCH = _go

        def log_message(self, *a):
            pass

    srv = ThreadingHTTPServer(("127.0.0.1", 0), H)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv


ROBOTS = {"X-Robots-Tag": "noindex, nofollow"}


def _healthy(write_body=J401):
    r = {p: (200, '{"ok":true}', ROBOTS) for p in ("/api/export", "/api/submissions", "/api/submissions/S06", "/api/ma/S06")}
    r[("POST", "/api/submissions")] = (401, write_body)
    r[("PATCH", "/api/submissions/ZZ99")] = (401, write_body)
    r["/api/health"] = (200, '{"reading":"blob","blob":{"readable":true}}')
    r["/m/S06"] = (200, "<p>$25</p>")
    return r


def _run(routes, args=(), **env):
    seen = []
    srv = _serve(routes, seen)
    base = f"http://127.0.0.1:{srv.server_address[1]}"
    e = {"PATH": "/usr/bin:/bin", "INTAKE_BASE": base, "SHOP_BASE": base, "CHECK_TIMEOUT": "5", "HELD_MAS": " ".join(HELD)}
    e.update(env)
    try:
        p = subprocess.run(["bash", str(SCRIPT), *args], env=e, capture_output=True, text=True, timeout=60)
    finally:
        srv.shutdown()
    return p, seen


def test_healthy_json_passes_without_write_probes():
    p, seen = _run(_healthy())
    assert p.returncode == 0, p.stdout
    assert "POST-DEPLOY PRIVACY CHECK: PASS" in p.stdout
    assert all(m == "GET" for m, _ in seen)


def test_empty_401_mode():
    assert _run(_healthy(""), WRITE_PROBES="1", SHOP_ADMIN_401_EMPTY="1")[0].returncode == 0
    p, _ = _run(_healthy(J401), WRITE_PROBES="1", SHOP_ADMIN_401_EMPTY="1")
    assert p.returncode == 1 and "body not empty shape" in p.stdout


def test_write_probes_run_when_gate_live():
    p, seen = _run(_healthy(), WRITE_PROBES="1")
    assert p.returncode == 0, p.stdout
    assert ("POST", "/api/submissions") in seen and ("PATCH", "/api/submissions/ZZ99") in seen


def test_missing_noindex_fails_never_echoes_values_and_blocks_writes():
    r = _healthy()
    r["/api/export"] = (200, f"ma,cost_cny,source_link\nS06,{SENTINEL},x")
    r["/api/ma/S06"] = (200, f'{{"cost_usd":"{SENTINEL}"}}')
    p, seen = _run(r, WRITE_PROBES="1")
    assert p.returncode == 1
    assert "X-Robots-Tag" in p.stdout
    assert SENTINEL not in p.stdout + p.stderr
    assert all(m == "GET" for m, _ in seen), "write probes must not run while the direct link is down"


def test_direct_link_body_passes_without_echoing_values():
    r = _healthy()
    r["/api/export"] = (200, f"ma,cost_cny,source_link\nS06,{SENTINEL},x", ROBOTS)
    r["/api/ma/S06"] = (200, f'{{"cost_usd":"{SENTINEL}"}}', ROBOTS)
    p, _ = _run(r)
    assert p.returncode == 0, p.stdout
    assert SENTINEL not in p.stdout + p.stderr


def test_shop_regressions_fail():
    r = _healthy()
    r["/api/health"] = (200, '{"reading":"seed"}')
    r["/m/S06"] = (200, "<p>$16</p>")
    r["/m/Q02"] = (200, "visible")
    p, _ = _run(r)
    assert p.returncode == 1
    for frag in ("FAIL  shop health", "FAIL  shop /m/S06", "HELD MÃ VISIBLE"):
        assert frag in p.stdout


def test_dry_run_no_network():
    p, seen = _run({}, ["--dry-run"], INTAKE_BASE="http://127.0.0.1:9", SHOP_BASE="http://127.0.0.1:9")
    assert p.returncode == 0 and "DRY RUN" in p.stdout and "/api/ma/S06" in p.stdout
    assert seen == []
