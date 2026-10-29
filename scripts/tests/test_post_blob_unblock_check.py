"""post_blob_unblock_check.sh against a local stub server (no real network)."""
import subprocess
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "post_blob_unblock_check.sh"


def _serve(routes):
    class H(BaseHTTPRequestHandler):
        def do_GET(self):
            code, body = routes.get(self.path, (404, "nf"))
            self.send_response(code)
            self.end_headers()
            self.wfile.write(body.encode())

        def do_POST(self):  # the script must never POST
            routes["__posted__"] = True
            self.send_response(405)
            self.end_headers()

        def log_message(self, *a):
            pass

    srv = ThreadingHTTPServer(("127.0.0.1", 0), H)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv


def _healthy():
    r = {
        "/": (200, "<html>Tỷ giá: 1 USD</html>"),
        "/api/submissions": (401, "{}"),
        "/api/fx": (200, '{"usd_cny":6.71}'),
        "/api/submissions/S06": (401, "{}"),
        "/api/ma/S06": (401, "{}"),
        "/api/export": (401, "{}"),
        "/api/ma-index": (200, '{"items":[{"ma":"A01","kind":"A","size":"M","color":"Kem"}]}'),
        "/api/health": (200, '{"reading":"blob","blob":{"readable":true}}'),
        "/m/S06": (200, "<p>$25</p>"),
    }
    for m in ("A01", "A02", "S01", "P01"):
        r[f"/m/{m}"] = (200, "ok")
    return r


def _run(routes):
    srv = _serve(routes)
    base = f"http://127.0.0.1:{srv.server_address[1]}"
    try:
        return subprocess.run(
            ["bash", str(SCRIPT)],
            env={"PATH": "/usr/bin:/bin", "INTAKE_BASE": base, "SHOP_BASE": base, "CHECK_TIMEOUT": "5"},
            capture_output=True, text=True, timeout=60,
        )
    finally:
        srv.shutdown()


def test_all_healthy_passes_and_never_posts():
    routes = _healthy()
    p = _run(routes)
    assert p.returncode == 0, p.stdout
    assert "POST-UNBLOCK CHECK: PASS" in p.stdout
    assert "__posted__" not in routes


def test_store_down_and_seed_and_held_visible_fail():
    routes = _healthy()
    routes["/api/fx"] = (503, '{"storeUnavailable":true}')
    routes["/api/submissions"] = (200, '{"submissions":[{"cost_usd":"x"}]}')
    routes["/api/health"] = (200, '{"reading":"seed","blob":{"readable":false}}')
    routes["/m/S06"] = (200, "<p>$27</p>")
    routes["/m/K03"] = (200, "held leak")
    routes["/api/export"] = (200, "ma\nS06")
    p = _run(routes)
    assert p.returncode == 1
    for frag in ("FAIL  intake /api/fx", "FAIL  intake /api/submissions locked", "FAIL  shop health", "FAIL  shop /m/S06", "HELD MÃ VISIBLE", "costs may be public"):
        assert frag in p.stdout, p.stdout
