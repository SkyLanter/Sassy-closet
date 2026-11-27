"""The privacy gate must check every held mã that data/held.json keeps off sell.

`post_deploy_privacy_check.sh` exists to catch a held mã that has gone live
(`HELD MÃ VISIBLE, tell Boss`). It defaulted to a hand-typed list of nine mãs
from an older held list, so 13 of the 21 mãs in `data/held.json` were never
requested at all. A live S19 / S14 / K06 therefore passed the gate.

`live_shop_smoke.sh` already resolves the same list through `held_policy.norm_ma`;
this gate runs on its own after a deploy, so it must read the shared list the
same way and only fall back to the typed list when the caller overrides it.
"""
from __future__ import annotations

import json
import re
import subprocess
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "post_deploy_privacy_check.sh"
HELD_JSON = ROOT / "data" / "held.json"
ROBOTS = {"X-Robots-Tag": "noindex, nofollow, nosnippet"}


def _held_codes() -> list[str]:
    payload = json.loads(HELD_JSON.read_text(encoding="utf-8"))
    return [*payload["heldIncomplete"], *payload["neverList"]]


def _healthy_routes(live_mas: set[str]) -> dict[str, tuple[int, str, dict[str, str]]]:
    routes: dict[str, tuple[int, str, dict[str, str]]] = {
        path: (200, '{"ok":true}', ROBOTS)
        for path in (
            "/api/export",
            "/api/submissions",
            "/api/submissions/S06",
            "/api/ma/S06",
            "/admin/shop",
        )
    }
    routes["/api/health"] = (200, '{"reading":"blob","blob":{"readable":true}}', {})
    routes["/m/S06"] = (200, "<p>$25</p>", {})
    for ma in live_mas:
        routes[f"/m/{ma}"] = (200, "visible", {})
    return routes


def _serve(routes, seen):
    class Handler(BaseHTTPRequestHandler):
        def _go(self):
            seen.append((self.command, self.path))
            code, body, headers = routes.get(self.path, (404, "nf", {}))
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

        def log_message(self, *a):
            pass

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server


def _run(routes, env_extra=None):
    seen: list[tuple[str, str]] = []
    server = _serve(routes, seen)
    base = f"http://127.0.0.1:{server.server_address[1]}"
    env = {
        "PATH": "/usr/bin:/bin:/usr/local/bin",
        "INTAKE_BASE": base,
        "SHOP_BASE": base,
        "CHECK_TIMEOUT": "5",
    }
    env.update(env_extra or {})
    try:
        done = subprocess.run(
            ["bash", str(SCRIPT)], env=env, capture_output=True, text=True, timeout=90
        )
    finally:
        server.shutdown()
    return done, seen


def test_default_held_list_is_the_shared_file():
    done, seen = _run(_healthy_routes(set()))
    assert done.returncode == 0, done.stdout + done.stderr
    probed = {path[len("/m/"):] for _, path in seen if path.startswith("/m/")}
    expected = set(_held_codes())
    assert expected <= probed, f"never requested: {sorted(expected - probed)}"
    assert "S06" in probed


def test_a_live_held_ma_outside_the_old_typed_list_fails():
    # S19 is heldIncomplete but was not in the old typed default, so this passed.
    done, seen = _run(_healthy_routes({"S19"}))
    assert done.returncode == 1, done.stdout
    assert "/m/S19" in [path for _, path in seen]
    assert "HELD MÃ VISIBLE" in done.stdout


def test_an_explicit_held_list_is_still_honoured():
    done, seen = _run(_healthy_routes(set()), {"HELD_MAS": "K03 Q02"})
    assert done.returncode == 0, done.stdout
    probed = {path for _, path in seen if path.startswith("/m/")}
    assert {"/m/K03", "/m/Q02"} <= probed


def test_dry_run_names_the_shared_held_list():
    done = subprocess.run(
        ["bash", str(SCRIPT), "--dry-run"],
        env={
            "PATH": "/usr/bin:/bin:/usr/local/bin",
            "INTAKE_BASE": "http://127.0.0.1:9",
            "SHOP_BASE": "http://127.0.0.1:9",
        },
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert done.returncode == 0
    for ma in _held_codes():
        assert re.search(rf"/m/{ma} -> 404", done.stdout), ma
