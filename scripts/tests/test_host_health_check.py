"""Offline tests for host_health_check (all network mocked)."""
import socket
import ssl
from types import SimpleNamespace

import pytest

import daily_shop_check as dsc
import host_health_check as hh

S06_PAGE = "<h1>S06</h1><span>$25</span>"


@pytest.fixture(autouse=True)
def no_network(monkeypatch):
    def boom(*a, **k):
        raise AssertionError("live network call in test")
    monkeypatch.setattr(socket, "create_connection", boom)
    monkeypatch.setattr(socket, "getaddrinfo", boom)
    monkeypatch.setattr(hh.urllib.request, "urlopen", boom)


def fake(monkeypatch, dns=None, tls=None, pages=None):
    dns, tls, pages = dns or {}, tls or {}, pages or {}
    monkeypatch.setattr(hh, "check_dns", lambda h: dns.get(h, (True, "ok")))
    monkeypatch.setattr(hh, "check_tls", lambda h, timeout=0: tls.get(h, (True, "ok (TLSv1.3)")))

    def f(url, timeout=0):
        path = "/" + url.split("/", 3)[3] if url.count("/") >= 3 else "/"
        return pages.get(url, {"/": (200, "home", ""), "/m/S19": (404, "", ""),
                               "/m/S06": (200, S06_PAGE, "")}.get(path, (404, "", "")))
    monkeypatch.setattr(hh, "fetch", f)


EOF_TLS = (False, "SSLError: [SSL: UNEXPECTED_EOF_WHILE_READING] unexpected eof while reading")


def test_all_healthy_pass(monkeypatch):
    fake(monkeypatch)
    s = hh.run()
    assert s["overall"] == "PASS" and len(s["hosts"]) == 2 and not s["warn"]
    assert {r["host"] for r in s["hosts"]} == set(hh.VERCEL_HOSTS)
    assert all(r["s06_pdp"]["shows_25"] for r in s["hosts"])


def test_no_custom_domain_hosts():
    assert not hasattr(hh, "CUSTOM_HOSTS")
    assert all(h.endswith(".vercel.app") for h in hh.VERCEL_HOSTS)


def test_vercel_tls_failure_is_fail(monkeypatch):
    fake(monkeypatch, tls={"sassycloset.vercel.app": EOF_TLS})
    assert hh.run()["overall"] == "FAIL"


def test_vercel_dns_failure_is_fail(monkeypatch):
    fake(monkeypatch, dns={"sassy-closet-shop.vercel.app": (False, "gaierror: no host")})
    s = hh.run()
    assert s["overall"] == "FAIL" and "DNS" in s["fail"][0]


def test_held_pdp_live_is_fail(monkeypatch):
    fake(monkeypatch, pages={"https://sassycloset.vercel.app/m/S19": (200, "S19", "")})
    s = hh.run()
    assert s["overall"] == "FAIL" and "held S19" in s["fail"][0]


def test_s06_off_25_is_fail(monkeypatch):
    fake(monkeypatch, pages={"https://sassycloset.vercel.app/m/S06": (200, "$26 $250", "")})
    s = hh.run()
    assert s["overall"] == "FAIL" and "S06" in s["fail"][0]


def test_vercel_home_500_is_fail(monkeypatch):
    fake(monkeypatch, pages={"https://sassy-closet-shop.vercel.app/": (500, "", "")})
    assert hh.run()["overall"] == "FAIL"


@pytest.mark.parametrize("body,ok", [("$25", True), ("$ 25.00", True), ("$250", False), ("$2", False), ("$125", False)])
def test_shows_price(body, ok):
    assert hh.shows_price(body, 25) is ok


def test_check_tls_reports_error_text(monkeypatch):
    def conn(*a, **k):
        raise ssl.SSLError("unexpected eof while reading")
    monkeypatch.setattr(socket, "create_connection", conn)
    ok, txt = hh.check_tls("sassycloset.vercel.app")
    assert not ok and "unexpected eof" in txt


def test_check_dns_error(monkeypatch):
    def gai(*a, **k):
        raise socket.gaierror("Name or service not known")
    monkeypatch.setattr(socket, "getaddrinfo", gai)
    assert hh.check_dns("nope.invalid")[0] is False


def test_fetch_http_error_returns_code(monkeypatch):
    def uo(*a, **k):
        raise hh.urllib.error.HTTPError("u", 404, "nf", {}, None)
    monkeypatch.setattr(hh.urllib.request, "urlopen", uo)
    assert hh.fetch("https://x/m/S19")[0] == 404


def test_main_exit_and_markdown(monkeypatch, tmp_path, capsys):
    fake(monkeypatch, tls={"sassycloset.vercel.app": EOF_TLS})
    rc = hh.main(["--out-json", str(tmp_path / "h.json")])
    assert rc == 2 and "Host health: FAIL" in capsys.readouterr().out
    assert (tmp_path / "h.json").exists()


def test_daily_hosts_section_mapping(monkeypatch):
    fake(monkeypatch)
    sec = dsc.hosts_section(True)
    assert sec["name"] == "hosts" and sec["status"] == "PASS"
    fake(monkeypatch, tls={"sassycloset.vercel.app": EOF_TLS})
    assert dsc.hosts_section(True)["status"] == "FAIL"
    assert dsc.hosts_section(False)["status"] == "SKIP"


def test_daily_hosts_runner_error_is_fail():
    def bad():
        raise RuntimeError("x")
    assert dsc.hosts_section(True, runner=bad)["status"] == "FAIL"


def test_daily_reduced_with_hosts_flag(monkeypatch, tmp_path, capsys):
    fake(monkeypatch, tls={"sassycloset.vercel.app": EOF_TLS})
    snap = tmp_path / "s.json"
    snap.write_text('{"schema":"daily-inputs/v1","date":"x","items":[{"ma":"S06","live":true,"sellUsd":25}]}')
    rc = dsc.main(["--reduced", "--snapshot", str(snap), "--hosts"])
    out = capsys.readouterr().out
    assert rc == 2 and "| hosts | FAIL |" in out
    fake(monkeypatch)
    rc = dsc.main(["--reduced", "--snapshot", str(snap), "--hosts"])
    assert rc == 0 and "| hosts | PASS |" in capsys.readouterr().out


def test_daily_without_hosts_has_no_hosts_section(tmp_path, capsys):
    snap = tmp_path / "s.json"
    snap.write_text('{"schema":"daily-inputs/v1","date":"x","items":[]}')
    assert dsc.main(["--reduced", "--snapshot", str(snap)]) == 0
    assert "hosts" not in capsys.readouterr().out
