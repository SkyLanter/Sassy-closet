"""Read-only tests for workflow_status. No live hosts and no repo data/held.json.

HTTP checks use an injected getter, except http_get itself, which is pointed at
127.0.0.1. Response bodies are sentinels that must stay out of the report.
"""

from __future__ import annotations

import json
import socket
import threading
import time
import urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import pytest

import workflow_status
from workflow_status import (
    GetResult,
    build_report,
    http_get,
    main,
    render_json,
    render_text,
)

INTAKE = "http://intake.test"
SHOP_A = "http://shop-a.test"
SHOP_B = "http://shop-b.test"
DAY = "2026-11-01"
SENTINEL = "BODY-SENTINEL-workflow"
NOINDEX_COST = "NOINDEX-COST-SENTINEL"
STORE_SENTINEL = "STOREDOWN-SENTINEL"
FALLBACK_SENTINEL = "FALLBACK-SENTINEL"
COST_LEAK = "COSTLEAKTOKEN"
LEAK_QTY = 975318
FALLBACK_PHRASE = "kho đang không đọc được"
ROBOTS = {"X-Robots-Tag": "noindex, nofollow, nosnippet"}
OPEN_NAMES = ("export", "submissions", "ma", "admin", "submission")
OPEN_PATHS = (
    "/api/export",
    "/api/submissions",
    "/api/ma/S06",
    "/admin/shop",
    "/api/submissions/S06",
)
REPORT_KINDS = (
    "midnight-qc",
    "meta-qc",
    "muse-pack",
    "muse-extras",
    "luxubu-status",
    "muse-today",
    "digest",
    "cost-recheck",
)
HELD_CODES = ("K03", "Q02")
NEVER_CODES = ("Z97",)


class _Completed:
    def __init__(self, returncode, stdout="", stderr=""):
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr


def write_held(directory, held, never):
    path = Path(directory) / "held.json"
    path.write_text(
        json.dumps({"heldIncomplete": list(held), "neverList": list(never)}),
        encoding="utf-8",
    )
    return path


def _meta_side(status):
    return {
        "luxubu": {"status": status, "reason": "ok"},
        "miniboss": {"status": status, "reason": "ok"},
    }


def login_cost():
    return {
        "taobao_login_needed": True,
        "counts": {"unreachable": 4},
        "unreachable_mas": ["K03", "Q02", "Z97"],
        "persistent_new_unreachable": ["K03"],
        "live_price_changed": [],
        "new_under_or_loss": ["Q02", "Z97"],
        "sample_live_cost": LEAK_QTY,
        "nested": {"usd": LEAK_QTY, "label": COST_LEAK},
    }


def write_reports(root, *, midnight="PASS", ig="pass", fb="pass", digest="plain", cost=None, bad_midnight=False):
    qc = root / "out" / "midnight-qc" / DAY
    qc.mkdir(parents=True, exist_ok=True)
    summary = qc / "summary.json"
    if bad_midnight:
        summary.write_text("{", encoding="utf-8")
    else:
        summary.write_text(
            json.dumps({"overall": midnight, "dataOk": "PASS", "sellSite": "PASS"}),
            encoding="utf-8",
        )
    muse = root / "out" / "muse"
    muse.mkdir(parents=True, exist_ok=True)
    (muse / f"meta-qc-{DAY}.json").write_text(
        json.dumps({"ig": _meta_side(ig), "fb": _meta_side(fb)}),
        encoding="utf-8",
    )
    (muse / f"pack-{DAY}.md").write_text("pack\n", encoding="utf-8")
    (muse / f"extras-{DAY}.md").write_text("extras\n", encoding="utf-8")
    (muse / f"luxubu-status-{DAY}.json").write_text("{}\n", encoding="utf-8")
    (muse / "TODAY.md").write_text("today\n", encoding="utf-8")
    reports = root / "out" / "reports" / DAY
    reports.mkdir(parents=True, exist_ok=True)
    if digest == "total2":
        (reports / "boss_decisions_digest.md").write_text("TOTAL 2\n", encoding="utf-8")
    elif digest == "plain":
        (reports / "boss_decisions_digest.md").write_text("digest\n", encoding="utf-8")
    else:
        raise AssertionError(digest)
    cost_dir = root / "verify" / "cost-recheck"
    cost_dir.mkdir(parents=True, exist_ok=True)
    payload = {"counts": {"unreachable": 0}} if cost is None else cost
    (cost_dir / f"summary.{DAY}.json").write_text(json.dumps(payload), encoding="utf-8")


def s06_page(price: str = "$25", related: str = "", extra: str = "") -> str:
    """S06's own price, not a related card. extra is a leak sentinel, never a price."""

    return (
        f'<meta name="description" content="{price} · S06 · sample">'
        f'<span class="ky-pdp-price sc-price">{price}</span>'
        f"{related}{extra}"
    )


def health_body(**overrides):
    payload = {
        "ok": True,
        "reading": "blob",
        "blob": {"readable": True},
        "productCount": 2,
        "leak": SENTINEL,
    }
    payload.update(overrides)
    return json.dumps(payload)


def standard_routes():
    routes = {}

    def add(origin, path, status, body, headers=None):
        routes[(origin, path)] = (status, body, dict(headers or {}))

    add(INTAKE, "/", 200, f"<p>home</p>{SENTINEL}")
    for path in OPEN_PATHS:
        add(INTAKE, path, 200, f'{{"leak":"{SENTINEL}"}}', ROBOTS)
    for shop in (SHOP_A, SHOP_B):
        add(shop, "/api/health", 200, health_body())
        add(shop, "/m/S06", 200, s06_page(extra=SENTINEL))
        for code in (*HELD_CODES, *NEVER_CODES):
            add(shop, f"/m/{code}", 404, f"hidden {SENTINEL}")
    return routes


def fake_getter(routes, calls):
    def getter(url, timeout):
        calls.append((url, timeout))
        parts = urllib.parse.urlsplit(url)
        origin = urllib.parse.urlunsplit((parts.scheme, parts.netloc, "", "", ""))
        spec = routes.get((origin, parts.path or "/"))
        if spec is None:
            return GetResult(599, {}, "", "missing-route")
        status, body, headers = spec
        return GetResult(status, dict(headers), body, "")

    return getter


def build(tmp, routes, *, held_tokens=HELD_CODES, never_tokens=NEVER_CODES, shops=(SHOP_A, SHOP_B), reports="clear", **kwargs):
    root = tmp / "root"
    root.mkdir(parents=True, exist_ok=True)
    if reports == "clear":
        write_reports(root)
    elif reports == "mixed":
        write_reports(root, midnight="FAIL", digest="total2", cost=login_cost())
    elif reports == "bad-midnight":
        write_reports(root, bad_midnight=True)
    elif reports == "meta-ig-fail":
        write_reports(root, ig="fail", fb="pass")
    elif reports == "none":
        pass
    else:
        raise AssertionError(reports)
    held = write_held(tmp, held_tokens, never_tokens)
    calls = []
    report = build_report(
        root,
        intake=INTAKE,
        shops=list(shops),
        held=held,
        timeout=5,
        getter=fake_getter(routes, calls),
        **kwargs,
    )
    return report, calls, root, held


def urls(calls):
    found = []
    for url, _timeout in calls:
        parts = urllib.parse.urlsplit(url)
        origin = urllib.parse.urlunsplit((parts.scheme, parts.netloc, "", "", ""))
        found.append((origin, parts.path or "/"))
    return found


def by_check(report):
    return {check.name: check for check in report.intake.checks}


def by_kind(report):
    return {item.kind: item for item in report.reports}


def assert_frame(report):
    text = render_text(report)
    lines = text.splitlines()
    assert lines[0].endswith(report.overall)
    assert lines[-1] == "Read-only GETs. No writes."
    assert text.endswith("\n")
    assert report.writes == "none"
    return text


def scrub(text, *paths):
    for path in paths:
        raw = str(path)
        text = text.replace(raw, "")
        text = text.replace(str(Path(path).resolve()), "")
    return text


def assert_hidden(report, *needles, paths=()):
    blob = scrub(render_text(report) + "\n" + json.dumps(render_json(report)), *paths)
    for needle in needles:
        assert needle not in blob
    return blob


def assert_live_pass(report):
    assert report.intake.state == "PASS"
    assert report.hosts
    for host in report.hosts:
        assert host.health == "PASS"
        assert host.s06 == "PASS"
        assert host.held.misses == ()


def closed_port():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(("127.0.0.1", 0))
    port = sock.getsockname()[1]
    sock.close()
    return port


class LocalServer:
    def __init__(self, routes, slow_seconds=1.2):
        self.routes = routes
        self.seen = []
        self.slow_seconds = slow_seconds
        self.httpd = None
        self.thread = None
        self.base = ""
        self.port = 0

    def __enter__(self):
        server = self

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, fmt, *args):
                return

            def do_GET(self):
                self._respond()

            def do_POST(self):
                self._respond()

            def do_PUT(self):
                self._respond()

            def do_PATCH(self):
                self._respond()

            def do_DELETE(self):
                self._respond()

            def do_HEAD(self):
                self._respond()

            def _respond(self):
                try:
                    length = int(self.headers.get("Content-Length", "0") or 0)
                except ValueError:
                    length = 0
                if length:
                    self.rfile.read(length)
                path = urllib.parse.urlsplit(self.path).path
                server.seen.append((self.command, path, self.requestline))
                spec = server.routes.get(path)
                if spec == "slow":
                    time.sleep(server.slow_seconds)
                    spec = (200, "slow-body", {})
                if spec == "redirect":
                    host, port = self.server.server_address
                    try:
                        self.send_response(302)
                        self.send_header("Location", f"http://{host}:{port}/landed")
                        self.send_header("Content-Length", "0")
                        self.end_headers()
                    except (BrokenPipeError, ConnectionResetError, OSError):
                        return
                    return
                if spec == "away":
                    try:
                        self.send_response(302)
                        self.send_header("Location", "https://example.invalid/health")
                        self.send_header("Content-Length", "0")
                        self.end_headers()
                    except (BrokenPipeError, ConnectionResetError, OSError):
                        return
                    return
                if spec is None:
                    spec = (404, "missing", {})
                status, body, headers = spec if len(spec) == 3 else (*spec, {})
                data = body.encode("utf-8")
                try:
                    self.send_response(status)
                    for key, value in headers.items():
                        self.send_header(key, value)
                    self.send_header("Content-Length", str(len(data)))
                    self.end_headers()
                    self.wfile.write(data)
                except (BrokenPipeError, ConnectionResetError, OSError):
                    return

        class Server(ThreadingHTTPServer):
            allow_reuse_address = True

        self.httpd = Server(("127.0.0.1", 0), Handler)
        self.thread = threading.Thread(target=self.httpd.serve_forever, daemon=True)
        self.thread.start()
        host, port = self.httpd.server_address
        self.port = port
        self.base = f"http://{host}:{port}"
        return self

    def __exit__(self, exc_type, exc, tb):
        self.httpd.shutdown()
        self.httpd.server_close()
        self.thread.join(timeout=5)
        return False


def healthy_server_routes(sentinel):
    health = json.dumps(
        {
            "ok": True,
            "reading": "blob",
            "blob": {"readable": True},
            "productCount": 2,
            "leak": sentinel,
        }
    )
    return {
        "/": (200, f"<html><p>intake</p>{sentinel}</html>", {}),
        "/api/export": (200, f'{{"cost_cny":"{sentinel}"}}', dict(ROBOTS)),
        "/api/submissions": (200, f'{{"rows":"{sentinel}"}}', dict(ROBOTS)),
        "/api/ma/S06": (200, f'{{"ma":"S06","leak":"{sentinel}"}}', dict(ROBOTS)),
        "/admin/shop": (200, f"<html>{sentinel}</html>", dict(ROBOTS)),
        "/api/submissions/S06": (200, f'{{"leak":"{sentinel}"}}', dict(ROBOTS)),
        "/api/health": (200, health, {}),
        "/m/S06": (200, "<html>" + s06_page(extra=sentinel) + "</html>", {}),
        "/m/K03": (404, sentinel, {}),
        "/m/Q02": (404, sentinel, {}),
        "/m/Z97": (404, sentinel, {}),
    }


def test_healthy_intake_and_both_shops(tmp_path):
    for submission_status in (200, 404):
        routes = standard_routes()
        routes[(INTAKE, "/api/submissions/S06")] = (
            submission_status,
            f'{{"leak":"{SENTINEL}"}}',
            dict(ROBOTS),
        )
        report, calls, root, _held = build(tmp_path, routes)
        named = by_check(report)
        assert [check.path for check in report.intake.checks] == ["/", *OPEN_PATHS]
        home = named["home"]
        assert home.status == 200
        assert home.ok is True
        assert home.note == ""
        assert home.noindex is False
        for name in OPEN_NAMES:
            check = named[name]
            expected = submission_status if name == "submission" else 200
            assert check.status == expected
            assert check.noindex is True
            assert check.ok is True
            assert check.note == ""
        assert [host.host for host in report.hosts] == [SHOP_A, SHOP_B]
        for host in report.hosts:
            assert host.health == "PASS"
            assert host.reading == "blob"
            assert host.blob_readable is True
            assert host.product_count == 2
            assert host.s06 == "PASS"
            assert host.s06_price is True
            assert host.held.count == 3
            assert host.held.misses == ()
        assert report.s06_held is False
        assert report.overall == "PASS"
        assert report.network == "read-only GET"
        meta = by_kind(report)["meta-qc"]
        assert meta.verdict == "CLEAR"
        assert meta.ig == "PASS"
        assert meta.fb == "PASS"
        assert_hidden(report, SENTINEL, paths=(root, tmp_path))
        assert_frame(report)
        parsed = urls(calls)
        assert sum(path == "/api/health" for _origin, path in parsed) == 2
        assert sum(path == "/m/S06" for _origin, path in parsed) == 2
        assert sum(path == "/m/K03" for _origin, path in parsed) == 2
        assert not any(path == "/m/S06" and origin == INTAKE for origin, path in parsed)


def test_main_healthy_exits_zero(tmp_path, capsys):
    root = tmp_path / "root"
    root.mkdir()
    write_reports(root)
    held = write_held(tmp_path, HELD_CODES, NEVER_CODES)
    with LocalServer(healthy_server_routes(SENTINEL)) as server:
        code = main(
            [
                "--root",
                str(root),
                "--held",
                str(held),
                "--intake",
                server.base,
                "--shop",
                server.base,
                "--shop",
                server.base,
                "--timeout",
                "5",
            ]
        )
        seen = list(server.seen)
    captured = capsys.readouterr()
    assert code == 0
    assert captured.out.splitlines()[0].endswith("PASS")
    assert captured.out.splitlines()[-1] == "Read-only GETs. No writes."
    assert SENTINEL not in captured.out
    assert SENTINEL not in captured.err
    assert "<html" not in captured.out
    methods = {method for method, _path, _line in seen}
    assert methods == {"GET"}
    assert all(line.startswith("GET ") for _method, _path, line in seen)
    paths = [path for _method, path, _line in seen]
    assert paths.count("/api/health") == 2
    assert paths.count("/m/K03") == 2
    assert paths.count("/m/Q02") == 2
    assert paths.count("/m/Z97") == 2
    for path in OPEN_PATHS:
        assert paths.count(path) == 1


def test_missing_noindex_fails_and_hides_body(tmp_path, monkeypatch, capsys):
    routes = standard_routes()
    routes[(INTAKE, "/api/export")] = (
        200,
        json.dumps({"cost_cny": NOINDEX_COST, "sample_live_cost": LEAK_QTY}),
        {},
    )
    calls = []
    monkeypatch.setattr(workflow_status, "http_get", fake_getter(routes, calls))
    root = tmp_path / "root"
    root.mkdir()
    write_reports(root)
    held = write_held(tmp_path, HELD_CODES, NEVER_CODES)
    code = main(
        [
            "--root",
            str(root),
            "--held",
            str(held),
            "--intake",
            INTAKE,
            "--shop",
            SHOP_A,
            "--timeout",
            "5",
        ]
    )
    captured = capsys.readouterr()
    report, _calls, _root, _held = build(tmp_path, routes, shops=(SHOP_A,))
    export = by_check(report)["export"]
    assert export.status == 200
    assert export.noindex is False
    assert export.ok is False
    assert export.note == "noindex"
    assert report.intake.state == "FAIL"
    assert report.overall == "FAIL"
    assert code == 2
    blob = scrub(captured.out + captured.err + json.dumps(render_json(report)), root, tmp_path)
    assert NOINDEX_COST not in blob
    assert SENTINEL not in blob
    assert str(LEAK_QTY) not in blob
    assert_frame(report)


def test_store_unavailable_fails_and_hides_body(tmp_path, monkeypatch, capsys):
    routes = standard_routes()
    routes[(INTAKE, "/api/submissions")] = (
        200,
        '{"ok":false,"storeUnavailable":true,"error":"%s"}' % STORE_SENTINEL,
        dict(ROBOTS),
    )
    calls = []
    monkeypatch.setattr(workflow_status, "http_get", fake_getter(routes, calls))
    root = tmp_path / "root"
    root.mkdir()
    write_reports(root)
    held = write_held(tmp_path, HELD_CODES, NEVER_CODES)
    code = main(
        [
            "--root",
            str(root),
            "--held",
            str(held),
            "--intake",
            INTAKE,
            "--shop",
            SHOP_A,
            "--timeout",
            "5",
        ]
    )
    captured = capsys.readouterr()
    report, _calls, _root, _held = build(tmp_path, routes, shops=(SHOP_A,))
    submissions = by_check(report)["submissions"]
    assert submissions.status == 200
    assert submissions.noindex is True
    assert submissions.ok is False
    assert submissions.note == "store-unavailable"
    assert report.overall == "FAIL"
    assert code == 2
    blob = scrub(captured.out + captured.err + json.dumps(render_json(report)) + render_text(report), root, tmp_path)
    assert STORE_SENTINEL not in blob
    assert SENTINEL not in blob


def test_home_fallback_fails_when_reachable(tmp_path):
    routes = standard_routes()
    routes[(INTAKE, "/")] = (
        200,
        f"Tỷ giá mặc định · {FALLBACK_PHRASE} {FALLBACK_SENTINEL}",
        {},
    )
    report, _calls, root, _held = build(tmp_path, routes, shops=(SHOP_A,))
    home = by_check(report)["home"]
    assert home.status == 200
    assert home.ok is False
    assert home.note == "fallback"
    assert report.intake.state == "FAIL"
    assert report.overall == "FAIL"
    assert by_check(report)["export"].ok is True
    assert_hidden(report, FALLBACK_SENTINEL, SENTINEL, paths=(root, tmp_path))
    assert_frame(report)


@pytest.mark.parametrize(
    "case",
    [
        "reading-seed",
        "blob-unreadable",
        "zero-products",
        "wrong-price",
        "cents-price",
        "related-card",
        "jsonld-other-card",
        "jsonld-lock",
        "fractional-price",
        "missing-count",
        "held-visible",
    ],
)
def test_shop_health_price_and_held_signals(case, tmp_path):
    routes = standard_routes()
    if case == "reading-seed":
        routes[(SHOP_A, "/api/health")] = (200, health_body(reading="seed"), {})
    elif case == "blob-unreadable":
        routes[(SHOP_A, "/api/health")] = (
            200,
            health_body(blob={"readable": False}),
            {},
        )
    elif case == "zero-products":
        routes[(SHOP_A, "/api/health")] = (200, health_body(productCount=0), {})
    elif case == "wrong-price":
        routes[(SHOP_A, "/m/S06")] = (200, s06_page("$250", extra=SENTINEL), {})
    elif case == "cents-price":
        routes[(SHOP_A, "/m/S06")] = (200, s06_page("$25.00", extra=SENTINEL), {})
    elif case == "related-card":
        routes[(SHOP_A, "/m/S06")] = (
            200,
            s06_page("$26", related='<span class="sc-price">$25</span>', extra=SENTINEL),
            {},
        )
    elif case == "jsonld-other-card":
        routes[(SHOP_A, "/m/S06")] = (
            200,
            (
                '<script type="application/ld+json">'
                '{"@type":"Product","sku":"S06","offers":{"price":"250.00"}}'
                '</script><span class="sc-price">$25</span>'
                + SENTINEL
            ),
            {},
        )
    elif case == "jsonld-lock":
        routes[(SHOP_A, "/m/S06")] = (
            200,
            (
                '<script type="application/ld+json">'
                '{"@type":"Product","sku":"s06","offers":{"price":"25.00"}}'
                '</script><span class="sc-price">$16</span>'
                + SENTINEL
            ),
            {},
        )
    elif case == "fractional-price":
        routes[(SHOP_A, "/m/S06")] = (200, s06_page("$25.50", extra=SENTINEL), {})
    elif case == "missing-count":
        payload = json.loads(health_body())
        del payload["productCount"]
        routes[(SHOP_A, "/api/health")] = (200, json.dumps(payload), {})
    elif case == "held-visible":
        routes[(SHOP_A, "/m/K03")] = (200, f"visible {SENTINEL}", {})
    else:
        raise AssertionError(case)
    report, _calls, root, _held = build(tmp_path, routes, shops=(SHOP_A,))
    host = report.hosts[0]
    text = render_text(report)
    payload = render_json(report)["hosts"][0]
    if case == "reading-seed":
        assert host.health == "FAIL"
        assert host.reading == "seed"
        assert host.blob_readable is True
        assert host.product_count == 2
        assert host.health_why == "reading"
        assert "why=reading" in text
        assert payload["reading"] == "seed"
        assert payload["health"] == "FAIL"
    elif case == "blob-unreadable":
        assert host.health == "FAIL"
        assert host.reading == "blob"
        assert host.blob_readable is False
        assert host.product_count == 2
        assert host.health_why == "blob"
        assert "why=blob" in text
        assert payload["blobReadable"] is False
    elif case == "zero-products":
        assert host.health == "FAIL"
        assert host.reading == "blob"
        assert host.blob_readable is True
        assert host.product_count == 0
        assert host.health_why == "productCount"
        assert "why=productCount" in text
        assert payload["productCount"] == 0
    elif case == "wrong-price":
        assert host.health == "PASS"
        assert host.s06 == "FAIL"
        assert host.s06_price is False
        assert host.s06_status == 200
        assert payload["s06"] == "FAIL"
    elif case in {"cents-price", "jsonld-lock"}:
        assert host.health == "PASS"
        assert host.s06 == "PASS"
        assert host.s06_price is True
        assert host.s06_status == 200
        assert payload["s06"] == "PASS"
    elif case in {"related-card", "jsonld-other-card", "fractional-price"}:
        assert host.health == "PASS"
        assert host.s06 == "FAIL"
        assert host.s06_price is False
        assert host.s06_status == 200
        assert payload["s06"] == "FAIL"
    elif case == "missing-count":
        assert host.health == "FAIL"
        assert host.health_why == "productCount"
        assert host.product_count is None
        assert payload["productCount"] is None
        assert "why=productCount" in text
    elif case == "held-visible":
        assert host.health == "PASS"
        assert host.s06 == "PASS"
        assert [(miss.ma, miss.status) for miss in host.held.misses] == [("K03", 200)]
        assert "miss K03" in text
        assert payload["held"]["misses"] == [{"ma": "K03", "status": 200}]
    else:
        raise AssertionError(case)
    if case in {"cents-price", "jsonld-lock"}:
        assert report.overall == "PASS"
    else:
        assert report.overall == "FAIL"
    assert_hidden(report, SENTINEL, paths=(root, tmp_path))


@pytest.mark.parametrize(
    ("held_token", "never_token"),
    [("k3", "q2"), ("K003", "Q002")],
)
def test_held_spelling_normalizes_request_path(held_token, never_token, tmp_path):
    report, calls, _root, held_path = build(
        tmp_path,
        standard_routes(),
        held_tokens=(held_token,),
        never_tokens=(never_token,),
        shops=(SHOP_A,),
    )
    raw = held_path.read_text(encoding="utf-8")
    assert held_token in raw
    assert never_token in raw
    shop_paths = [path for origin, path in urls(calls) if origin == SHOP_A and path.startswith("/m/")]
    assert sorted(shop_paths) == ["/m/K03", "/m/Q02", "/m/S06"]
    assert f"/m/{held_token}" not in shop_paths
    assert f"/m/{never_token}" not in shop_paths
    host = report.hosts[0]
    assert host.held.count == 2
    assert host.held.misses == ()
    assert host.s06 == "PASS"
    assert report.s06_held is False
    assert all(miss.ma != "S06" for miss in host.held.misses)
    assert report.overall == "PASS"


def test_offline_makes_no_getter_calls_and_warns(tmp_path, monkeypatch, capsys):
    calls = []

    def getter(url, timeout):
        calls.append((url, timeout))
        raise AssertionError(url)

    report = build_report(
        tmp_path / "root",
        intake=INTAKE,
        shops=[SHOP_A, SHOP_B],
        held=write_held(tmp_path, HELD_CODES, NEVER_CODES),
        timeout=5,
        offline=True,
        getter=getter,
    )
    assert calls == []
    assert report.overall == "WARN"
    assert report.network == "offline"
    assert report.intake.state == "SKIP"
    assert [host.host for host in report.hosts] == [SHOP_A, SHOP_B]
    assert all(host.health == "SKIP" and host.s06 == "SKIP" for host in report.hosts)
    assert all(host.held.count == 3 for host in report.hosts)
    assert_frame(report)
    monkeypatch.setattr(workflow_status, "http_get", getter)
    root = tmp_path / "cli-root"
    root.mkdir()
    code = main(
        [
            "--offline",
            "--root",
            str(root),
            "--held",
            str(tmp_path / "held.json"),
            "--intake",
            INTAKE,
            "--shop",
            SHOP_A,
            "--timeout",
            "1",
        ]
    )
    captured = capsys.readouterr()
    assert code == 1
    assert calls == []
    assert captured.out.splitlines()[0].endswith("WARN")


def test_missing_reports_warn_and_list_families(tmp_path):
    report, _calls, root, _held = build(tmp_path, standard_routes(), reports="none")
    found = by_kind(report)
    text = assert_frame(report)
    dumped = json.dumps(render_json(report))
    for kind in REPORT_KINDS:
        assert kind in found
        assert found[kind].verdict == "MISSING"
        assert found[kind].warn is True
        assert kind in text
        assert kind in dumped
    assert_live_pass(report)
    assert report.overall == "WARN"
    assert_hidden(report, SENTINEL, paths=(root, tmp_path))


def test_present_fixtures_midnight_fail_meta_clear_cost_and_digest(tmp_path):
    report, _calls, root, _held = build(tmp_path, standard_routes(), reports="mixed")
    found = by_kind(report)
    assert found["midnight-qc"].verdict == "FAIL"
    assert found["midnight-qc"].warn is True
    assert found["meta-qc"].verdict == "CLEAR"
    assert found["meta-qc"].ig == "PASS"
    assert found["meta-qc"].fb == "PASS"
    assert found["digest"].verdict == "OPEN"
    assert found["digest"].total == 2
    cost = found["cost-recheck"]
    assert cost.verdict == "LOGIN"
    assert cost.taobao_login_needed is True
    assert cost.unreachable == 4
    assert cost.unreachable_mas == 3
    assert cost.persistent_new_unreachable == 1
    assert cost.live_price_changed == 0
    assert cost.new_under_or_loss == 2
    text = render_text(report)
    assert "taobao_login_needed=true" in text
    assert "unreachable_mas=" in text
    cleaned = scrub(text + "\n" + json.dumps(render_json(report)), root, tmp_path)
    assert str(LEAK_QTY) not in cleaned
    assert COST_LEAK not in cleaned
    assert_live_pass(report)
    assert report.overall == "WARN"


def test_meta_one_side_fail_keeps_overall_pass(tmp_path):
    report, _calls, _root, _held = build(tmp_path, standard_routes(), reports="meta-ig-fail")
    meta = by_kind(report)["meta-qc"]
    assert meta.verdict == "NOT CLEAR"
    assert meta.ig == "FAIL"
    assert meta.fb == "PASS"
    assert meta.warn is False
    assert_live_pass(report)
    assert set(REPORT_KINDS) <= set(by_kind(report))
    assert all(item.verdict != "MISSING" and item.verdict != "UNREADABLE" for item in report.reports)
    assert all(item.warn is False for item in report.reports)
    assert report.overall == "PASS"


def test_index_digest_status_when_newest_candidate(tmp_path):
    root = tmp_path / "root"
    newer = root / "out" / "reports" / "2026-11-02"
    older = root / "out" / "reports" / "2026-10-01"
    newer.mkdir(parents=True)
    (newer / "INDEX.md").write_text(
        "| topic | status |\n| boss_decisions_digest | GAPS |\nOverall: OK\n",
        encoding="utf-8",
    )
    older.mkdir(parents=True)
    (older / "boss_decisions_digest.md").write_text("TOTAL 2\n", encoding="utf-8")
    held = write_held(tmp_path, ["K03"], ["Z97"])

    def getter(url, timeout):
        raise AssertionError(url)

    report = build_report(
        root,
        intake=INTAKE,
        shops=[SHOP_A],
        held=held,
        timeout=5,
        offline=True,
        getter=getter,
    )
    digest = by_kind(report)["digest"]
    assert digest.date == "2026-11-02"
    assert digest.verdict == "GAPS"
    assert digest.index_overall == "OK"
    assert digest.path.endswith("INDEX.md")
    text = render_text(report)
    assert "GAPS" in text
    assert "overall=OK" in text


def test_digest_file_preferred_over_same_day_index(tmp_path):
    root = tmp_path / "root"
    day = root / "out" / "reports" / "2026-11-02"
    nested = day / "nested"
    nested.mkdir(parents=True)
    (day / "INDEX.md").write_text(
        "| boss_decisions_digest | GAPS |\nOverall: FAILED\n",
        encoding="utf-8",
    )
    (day / "digest.md").write_text("TOTAL 0\n", encoding="utf-8")
    (nested / "boss_decisions_digest.md").write_text("TOTAL 2\n", encoding="utf-8")
    held = write_held(tmp_path, ["k3"], ["q2"])

    def getter(url, timeout):
        raise AssertionError(url)

    report = build_report(
        root,
        intake=INTAKE,
        shops=[SHOP_A],
        held=held,
        timeout=5,
        offline=True,
        getter=getter,
    )
    digest = by_kind(report)["digest"]
    assert digest.verdict == "OPEN"
    assert digest.total == 2
    assert digest.path.endswith("boss_decisions_digest.md")
    assert not digest.path.endswith("INDEX.md")


@pytest.mark.parametrize("which", ["midnight", "cost", "meta"])
def test_bad_json_report_is_unreadable_and_warns(which, tmp_path):
    root = tmp_path / "root"
    root.mkdir()
    write_reports(root)
    if which == "midnight":
        target = root / "out" / "midnight-qc" / DAY / "summary.json"
        kind = "midnight-qc"
    elif which == "cost":
        target = root / "verify" / "cost-recheck" / f"summary.{DAY}.json"
        kind = "cost-recheck"
    elif which == "meta":
        target = root / "out" / "muse" / f"meta-qc-{DAY}.json"
        kind = "meta-qc"
    else:
        raise AssertionError(which)
    target.write_text("{", encoding="utf-8")
    report, _calls, _root, _held = build(tmp_path, standard_routes(), reports="none")
    item = by_kind(report)[kind]
    assert item.verdict == "UNREADABLE"
    assert item.warn is True
    assert item.path.endswith(target.name)
    assert "UNREADABLE" in render_text(report)
    assert_live_pass(report)
    assert report.overall == "WARN"


def test_draft_prs_filters_drafts_and_sorts_by_number(tmp_path):
    payload = [
        {"number": 12, "title": "mid", "url": "https://example.test/12", "isDraft": True},
        {"number": 40, "title": "high", "url": "https://example.test/40", "isDraft": True},
        {"number": 8, "title": "published", "url": "https://example.test/8", "isDraft": False},
        {"number": 3, "title": "low", "url": "https://example.test/3", "isDraft": True},
        {"number": 9, "title": "missing-flag", "url": "https://example.test/9"},
    ]
    seen = []

    def runner(*args, **kwargs):
        seen.append(args[0])
        assert kwargs.get("check") is False
        return _Completed(0, json.dumps(payload))

    report, _calls, _root, _held = build(
        tmp_path,
        standard_routes(),
        shops=(SHOP_A,),
        read_draft_prs=True,
        runner=runner,
    )
    assert len(seen) == 1
    command = seen[0]
    assert command[0] == "gh"
    assert "--draft" in command
    assert "number,title,url,isDraft" in command
    assert [(pull.number, pull.url, pull.title) for pull in report.draft_prs.pulls] == [
        (3, "https://example.test/3", "low"),
        (12, "https://example.test/12", "mid"),
        (40, "https://example.test/40", "high"),
    ]
    assert report.draft_prs.state == "ok"
    assert report.overall == "PASS"
    assert "published" not in render_text(report)
    assert "missing-flag" not in render_text(report)


def test_draft_runner_failure_is_unread_and_warns(tmp_path):
    def runner(*args, **kwargs):
        return _Completed(1, "", "gh exploded")

    report, _calls, _root, _held = build(
        tmp_path,
        standard_routes(),
        shops=(SHOP_A,),
        read_draft_prs=True,
        runner=runner,
    )
    assert report.draft_prs.state == "unread"
    assert report.draft_prs.pulls == ()
    assert "gh exploded" in report.draft_prs.detail
    assert "Draft PRs: unread" in render_text(report)
    assert_live_pass(report)
    assert all(item.warn is False for item in report.reports)
    assert report.overall == "WARN"


def test_offline_does_not_call_draft_runner(tmp_path):
    def runner(*args, **kwargs):
        raise AssertionError(args)

    report, calls, _root, _held = build(
        tmp_path,
        standard_routes(),
        shops=(SHOP_A,),
        reports="none",
        offline=True,
        read_draft_prs=True,
        runner=runner,
    )
    assert calls == []
    assert report.draft_prs.state == "skipped"
    assert report.draft_prs.detail == "offline"
    assert report.draft_prs.pulls == ()
    assert report.network == "offline"
    assert report.overall == "WARN"
    assert "Draft PRs: skipped" in render_text(report)


def test_draft_flag_off_does_not_call_runner(tmp_path, monkeypatch, capsys):
    def runner(*args, **kwargs):
        raise AssertionError("runner called")

    report, _calls, _root, _held = build(
        tmp_path,
        standard_routes(),
        shops=(SHOP_A,),
        runner=runner,
    )
    assert report.draft_prs.state == "skipped"
    assert report.draft_prs.pulls == ()
    assert report.overall == "PASS"
    assert "Draft PRs: skipped" in render_text(report)

    def boom(*args, **kwargs):
        raise AssertionError("subprocess run called")

    def getter(url, timeout):
        raise AssertionError(url)

    monkeypatch.setattr(workflow_status.subprocess, "run", boom)
    monkeypatch.setattr(workflow_status, "http_get", getter)
    root = tmp_path / "cli-root"
    root.mkdir()
    code = main(
        [
            "--offline",
            "--root",
            str(root),
            "--held",
            str(write_held(tmp_path, ["K03"], ["Z97"])),
            "--intake",
            INTAKE,
            "--shop",
            SHOP_A,
            "--timeout",
            "1",
        ]
    )
    captured = capsys.readouterr()
    assert code == 1
    assert "Draft PRs: skipped" in captured.out


def test_main_json_omits_response_bodies(tmp_path, capsys):
    root = tmp_path / "root"
    root.mkdir()
    write_reports(root)
    held = write_held(tmp_path, HELD_CODES, NEVER_CODES)
    with LocalServer(healthy_server_routes(SENTINEL)) as server:
        code = main(
            [
                "--json",
                "--root",
                str(root),
                "--held",
                str(held),
                "--intake",
                server.base,
                "--shop",
                server.base,
                "--timeout",
                "5",
            ]
        )
    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    assert code == 0
    assert payload["overall"] == "PASS"
    assert payload["writes"] == "none"
    assert payload["network"] == "read-only GET"
    assert payload["hosts"][0]["reading"] == "blob"
    assert payload["hosts"][0]["blobReadable"] is True
    assert payload["hosts"][0]["productCount"] == 2
    assert payload["hosts"][0]["s06"] == "PASS"
    assert payload["hosts"][0]["held"]["misses"] == []
    assert SENTINEL not in captured.out
    assert SENTINEL not in captured.err
    assert "<html" not in captured.out
    assert "cost_cny" not in captured.out


def test_rejected_url_scheme_exits_without_calling_getter(tmp_path, monkeypatch, capsys):
    calls = []

    def getter(url, timeout):
        calls.append((url, timeout))
        return GetResult(599, {}, "", "unexpected")

    held = write_held(tmp_path, ["K03"], ["Z97"])
    root = tmp_path / "root"
    root.mkdir()
    report = build_report(
        root,
        intake="ftp://127.0.0.1/bad",
        shops=["http://shop-a.test"],
        held=held,
        timeout=1,
        getter=getter,
    )
    assert calls == []
    assert report.overall == "FAIL"
    assert "intake base rejected" in report.config_notes
    assert_frame(report)
    monkeypatch.setattr(workflow_status, "http_get", getter)
    code = main(
        [
            "--json",
            "--root",
            str(root),
            "--held",
            str(held),
            "--intake",
            "ftp://127.0.0.1/bad",
            "--shop",
            "http://127.0.0.1:9",
            "--timeout",
            "1",
        ]
    )
    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    assert code == 2
    assert payload["overall"] == "FAIL"
    assert calls == []
    assert "<html" not in captured.out


@pytest.fixture
def http_stub():
    routes = {
        "/ok": (200, "plain-ok", {"X-Robots-Tag": "noindex, nofollow, nosnippet"}),
        "/missing": (
            404,
            "missing-body",
            {"X-Robots-Tag": "noindex, nofollow, nosnippet", "X-Trace": "workflow-status-header"},
        ),
        "/bounce": "redirect",
        "/landed": (200, "landed-body", {}),
        "/slow": "slow",
    }
    with LocalServer(routes) as server:
        yield server


def test_http_get_sends_only_get(http_stub):
    ok = http_get(http_stub.base + "/ok", 5)
    followed = http_get(http_stub.base + "/bounce", 5)
    assert ok.status == 200
    assert ok.body == "plain-ok"
    assert followed.status == 200
    assert followed.body == "landed-body"
    assert http_stub.seen
    assert {method for method, _path, _line in http_stub.seen} == {"GET"}
    assert all(line.startswith("GET ") for _method, _path, line in http_stub.seen)
    paths = [path for _method, path, _line in http_stub.seen]
    assert "/ok" in paths
    assert "/bounce" in paths
    assert "/landed" in paths


def test_http_get_does_not_follow_a_cross_host_redirect():
    with LocalServer({"/away": "away", "/landed": (200, "landed-body", {})}) as server:
        result = http_get(server.base + "/away", 5)
        seen = list(server.seen)
    assert result.status == 302
    assert result.body != "landed-body"
    assert [path for _method, path, _line in seen] == ["/away"]


def test_http_get_404_returns_status_and_headers(http_stub, capsys):
    result = http_get(http_stub.base + "/missing", 5)
    captured = capsys.readouterr()
    assert result.status == 404
    assert result.error == ""
    assert result.body == "missing-body"
    headers = {key.lower(): value for key, value in result.headers.items()}
    assert headers["x-robots-tag"] == "noindex, nofollow, nosnippet"
    assert headers["x-trace"] == "workflow-status-header"
    assert http_stub.seen[0][0] == "GET"
    assert http_stub.seen[0][2].startswith("GET ")
    assert captured.out == ""
    assert captured.err == ""


def test_http_get_timeout_and_connection_error_have_no_status(http_stub):
    slow = http_get(http_stub.base + "/slow", 0.4)
    refused = http_get(f"http://127.0.0.1:{closed_port()}/nope", 2)
    assert slow.status is None
    assert slow.error
    assert refused.status is None
    assert refused.error
    assert refused.body == ""
    assert any(method == "GET" and path == "/slow" for method, path, _line in http_stub.seen)


def test_http_get_rejected_scheme_does_not_connect(http_stub):
    before = len(http_stub.seen)
    rejected = http_get(f"ftp://127.0.0.1:{http_stub.port}/secret", 2)
    assert len(http_stub.seen) == before
    assert rejected.status is None
    assert rejected.error == "rejected-url"
    assert rejected.body == ""


def test_render_text_names_overall_and_says_no_writes(tmp_path):
    warned, _calls, _root, held = build(tmp_path, standard_routes(), reports="none", offline=True)
    assert warned.overall == "WARN"
    assert_frame(warned)

    def getter(url, timeout):
        raise AssertionError(url)

    failed = build_report(
        tmp_path / "fail-root",
        intake="ftp://127.0.0.1/bad",
        shops=[SHOP_A],
        held=held,
        timeout=1,
        getter=getter,
    )
    assert failed.overall == "FAIL"
    assert_frame(failed)

    passed, _calls, _root, _held = build(tmp_path / "pass", standard_routes(), shops=(SHOP_A,))
    assert passed.overall == "PASS"
    assert_frame(passed)
