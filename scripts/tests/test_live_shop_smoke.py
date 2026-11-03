"""live_shop_smoke.sh against a local stub server (no real network)."""
import os
import subprocess
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "live_shop_smoke.sh"
SENTINEL = "SENTINEL-VALUE-777"


def _serve(routes, seen):
    class H(BaseHTTPRequestHandler):
        def _go(self):
            seen.append((self.command, self.path))
            code, body = routes.get(self.path, (404, "nf"))
            self.send_response(code)
            self.end_headers()
            self.wfile.write(body.encode())

        do_GET = do_POST = do_PATCH = _go

        def log_message(self, *a):
            pass

    srv = ThreadingHTTPServer(("127.0.0.1", 0), H)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv


def _run(routes, *args, held="k3 Q02"):
    seen = []
    srv = _serve(routes, seen)
    base = f"http://127.0.0.1:{srv.server_address[1]}"
    env = dict(os.environ, SHOP_HOSTS=base, INTAKE_BASE=base, HELD_MAS=held, CHECK_TIMEOUT="5")
    p = subprocess.run(["bash", str(SCRIPT), *args], capture_output=True, text=True, env=env)
    srv.shutdown()
    return p, seen


GOOD = {
    "/api/health": (200, '{"reading":"blob","productCount":62}'),
    "/m/S06": (200, "<p>$25</p>"),
    "/": (200, "<h1>intake</h1>"),
}


def test_pass_and_get_only_and_norm():
    p, seen = _run(GOOD)
    assert p.returncode == 0, p.stdout
    assert "LIVE SHOP SMOKE: PASS" in p.stdout
    assert "/m/K03 404" in p.stdout  # k3 normalised
    assert {m for m, _ in seen} == {"GET"}


def test_s06_wrong_price_fails():
    r = dict(GOOD, **{"/m/S06": (200, "<p>$16</p>")})
    p, _ = _run(r)
    assert p.returncode == 1 and "S06 MUST BE $25" in p.stdout


def test_held_visible_and_not_blob_fail():
    r = dict(GOOD, **{"/m/Q02": (200, "x"), "/api/health": (200, '{"reading":"seed","productCount":62}')})
    p, _ = _run(r)
    assert p.returncode == 1 and "HELD MÃ VISIBLE" in p.stdout and "reading=seed" in p.stdout


def test_intake_leak_names_only():
    r = dict(GOOD, **{"/": (200, '{"cost_cny":"' + SENTINEL + '"}')})
    p, _ = _run(r)
    assert p.returncode == 1 and "cost_cny" in p.stdout and SENTINEL not in p.stdout + p.stderr


def test_dry_run_no_network():
    p = subprocess.run(["bash", str(SCRIPT), "--dry-run", "--with-privacy"], capture_output=True, text=True,
                       env=dict(os.environ, SHOP_HOSTS="http://127.0.0.1:9", HELD_MAS="S006"))
    assert p.returncode == 0 and "/m/S06 -> 404" in p.stdout and "DRY RUN" in p.stdout
