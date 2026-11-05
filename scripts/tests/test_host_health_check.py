"""Offline tests for host_health_check (all network mocked)."""
import json
import socket
import ssl
from types import SimpleNamespace

import pytest

import daily_shop_check as dsc
import host_health_check as hh
import too_cheap_check
from held_policy import default_held_path, load_held_policy, norm_ma
from s06_offer_price import s06_offer_dollars


def script_json(body: str) -> dict:
    start = body.index(">") + 1
    end = body.index("</script>")
    return json.loads(body[start:end])


def product_html(sku="S06", price="25.00", extra="<h1>S06</h1><span>$25</span><span>$30</span>",
                 attrs='type="application/ld+json"', node=None):
    if node is None:
        node = {
            "@context": "https://schema.org",
            "@type": "Product",
            "sku": sku,
            "offers": {"@type": "Offer", "priceCurrency": "USD", "price": price},
        }
    return f"<script {attrs}>{json.dumps(node)}</script>{extra}"


def s06_pages(body, status=200):
    return {f"https://{host}/m/S06": (status, body, "") for host in hh.VERCEL_HOSTS}


S06_PAGE = product_html()


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
    assert '"25.00"' in S06_PAGE and "$25" in S06_PAGE and "$30" in S06_PAGE
    fake(monkeypatch)
    s = hh.run()
    assert s["overall"] == "PASS" and len(s["hosts"]) == 2 and not s["warn"]
    assert {r["host"] for r in s["hosts"]} == set(hh.VERCEL_HOSTS)
    assert all(r["s06_pdp"]["shows_25"] for r in s["hosts"])
    assert all(r["s06_pdp"]["offer_usd"] == "25.00" for r in s["hosts"])


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


def test_s06_offer_30_with_stray_25_is_fail(monkeypatch):
    body = product_html("S06", "30.00", extra="<h1>S06</h1><span>$25</span>")
    assert "$25" in body
    assert script_json(body)["offers"]["price"] == "30.00"
    fake(monkeypatch, pages=s06_pages(body))
    s = hh.run()
    assert s["overall"] == "FAIL"
    assert s["fail"] and all("S06" in item for item in s["fail"])
    assert all(r["s06_pdp"]["shows_25"] is False for r in s["hosts"])
    assert all(r["s06_pdp"]["offer_usd"] == "30.00" for r in s["hosts"])


def test_s06_dollar_text_without_jsonld_is_fail(monkeypatch):
    body = "<h1>S06</h1><span>$25</span>"
    fake(monkeypatch, pages=s06_pages(body))
    s = hh.run()
    assert s["overall"] == "FAIL"
    assert s["fail"] and all("S06" in item for item in s["fail"])
    assert all(r["s06_pdp"]["shows_25"] is False for r in s["hosts"])
    assert all(r["s06_pdp"]["offer_usd"] is None for r in s["hosts"])


def test_lowercase_s06_sku_at_25_passes(monkeypatch):
    body = product_html("s06", "25.00")
    assert '"sku": "s06"' in body
    assert hh.s06_shows_25(body) is True
    assert hh.s06_offer_usd(body) == "25.00"
    fake(monkeypatch, pages=s06_pages(body))
    s = hh.run()
    assert s["overall"] == "PASS"
    assert all(r["s06_pdp"]["shows_25"] is True for r in s["hosts"])
    assert all(r["s06_pdp"]["offer_usd"] == "25.00" for r in s["hosts"])


def test_price_25_000_equals_25_and_shows_25():
    page = product_html("S06", "25.000")
    assert script_json(page)["offers"]["price"] == "25.000"
    assert s06_offer_dollars(page) == 25
    assert hh.s06_shows_25(page) is True
    assert hh.s06_offer_usd(page) == "25.00"


def test_non_ld_script_with_dollar_25_and_sku_does_not_pass(monkeypatch):
    raw = json.dumps(
        {"@type": "Product", "sku": "S06", "name": "$25", "offers": {"price": "25.00"}},
        separators=(",", ":"),
    )
    body = f'<script type="application/json">{raw}</script>'
    assert '"sku":"S06"' in body and "$25" in body
    assert "application/ld+json" not in body
    assert hh.s06_shows_25(body) is False
    assert hh.s06_offer_usd(body) is None
    fake(monkeypatch, pages=s06_pages(body))
    s = hh.run()
    assert s["overall"] == "FAIL"
    assert s["fail"] and all("S06" in item for item in s["fail"])
    assert all(r["s06_pdp"]["shows_25"] is False for r in s["hosts"])
    assert all(r["s06_pdp"]["offer_usd"] is None for r in s["hosts"])


def test_s06_offer_price_null_fails(monkeypatch):
    body = product_html("S06", None, extra="<span>$25</span>")
    assert '"price": null' in body and "$25" in body
    assert hh.s06_shows_25(body) is False
    assert hh.s06_offer_usd(body) is None
    fake(monkeypatch, pages=s06_pages(body))
    s = hh.run()
    assert s["overall"] == "FAIL"
    assert s["fail"] and all("S06" in item for item in s["fail"])
    assert all(r["s06_pdp"]["shows_25"] is False for r in s["hosts"])
    assert all(r["s06_pdp"]["offer_usd"] is None for r in s["hosts"])


def test_one_host_s06_offer_30_other_25_is_fail(monkeypatch):
    bad_host, good_host = hh.VERCEL_HOSTS
    fake(monkeypatch, pages={
        f"https://{bad_host}/m/S06": (200, product_html("S06", "30.00", extra="<span>$25</span>"), ""),
        f"https://{good_host}/m/S06": (200, product_html("S06", "25.00"), ""),
    })
    s = hh.run()
    by_host = {r["host"]: r["s06_pdp"] for r in s["hosts"]}
    assert s["overall"] == "FAIL"
    assert by_host[bad_host]["shows_25"] is False
    assert by_host[bad_host]["offer_usd"] == "30.00"
    assert by_host[good_host]["shows_25"] is True
    assert by_host[good_host]["offer_usd"] == "25.00"
    assert any(bad_host in item and "S06" in item for item in s["fail"])
    assert all(good_host not in item for item in s["fail"])


def test_s06_offer_ignores_other_product_jsonld(monkeypatch):
    s06 = {
        "@type": "Product",
        "sku": "S06",
        "offers": {"@type": "Offer", "price": "25.00", "priceCurrency": "USD"},
    }
    other = {
        "@type": "Product",
        "sku": "A02",
        "offers": {"@type": "Offer", "price": "19.00", "priceCurrency": "USD"},
    }
    body = (
        f'<script type="application/ld+json">{json.dumps(s06)}</script>'
        f'<script type="application/ld+json">{json.dumps(other)}</script>'
        "<span>$19</span>"
    )
    fake(monkeypatch, pages=s06_pages(body))
    s = hh.run()
    assert s["overall"] == "PASS"
    assert all(r["s06_pdp"]["shows_25"] is True for r in s["hosts"])
    assert all(r["s06_pdp"]["offer_usd"] == "25.00" for r in s["hosts"])


def test_vercel_home_500_is_fail(monkeypatch):
    fake(monkeypatch, pages={"https://sassy-closet-shop.vercel.app/": (500, "", "")})
    assert hh.run()["overall"] == "FAIL"


def _expect_offer(body: str, dollars: int | None) -> None:
    assert s06_offer_dollars(body) == dollars
    assert hh.s06_shows_25(body) is (dollars == 25)
    if dollars is None:
        assert hh.s06_offer_usd(body) is None
    else:
        assert hh.s06_offer_usd(body) == f"{dollars:.2f}"


def test_s06_jsonld_offer_units():
    s006 = product_html("S006", "25.00")
    s6 = product_html("S6", "25.00")
    assert hh.s06_shows_25(s006) is True
    assert hh.s06_shows_25(s6) is True
    assert hh.s06_offer_usd(s006) == "25.00"
    assert s06_offer_dollars(s006) == 25
    assert s06_offer_dollars(s6) == 25
    s06b = product_html("S06B", "25.00")
    assert hh.s06_shows_25(s06b) is False
    assert hh.s06_offer_usd(s06b) is None
    assert s06_offer_dollars(s06b) is None
    assert hh.s06_shows_25(product_html("S06", True)) is False
    _expect_offer(product_html("S06", True), None)
    _expect_offer(product_html("S06", False), None)
    _expect_offer(product_html("S06", "25.50"), None)
    _expect_offer(product_html("S06", 25), 25)
    _expect_offer(product_html("S06", 25.0), 25)
    _expect_offer(product_html("S06", "25"), 25)
    _expect_offer(product_html("S06", "25.0"), 25)
    _expect_offer(product_html("S06", "25.00"), 25)
    _expect_offer(product_html("S06", "$25"), 25)
    _expect_offer(product_html("S06", "1e2"), None)
    _expect_offer(product_html("S06", "0x19"), None)
    _expect_offer(product_html("S06", "250"), 250)
    assert hh.s06_shows_25(product_html("S06", "250")) is False
    _expect_offer(product_html("S06", "1,025"), None)
    _expect_offer(product_html("S06", "25,00"), None)
    _expect_offer(product_html("S06", ""), None)
    _expect_offer(product_html("S06", "   "), None)
    _expect_offer(product_html("S06", None), None)
    _expect_offer(product_html("S06", float("nan")), None)
    _expect_offer(product_html("S06", float("inf")), None)
    _expect_offer(product_html("S06", float("-inf")), None)
    spliced = product_html("S06", "2$5", extra="<span>$25</span>")
    assert "2$5" in spliced and "$25" in spliced
    assert hh.s06_shows_25(spliced) is False
    assert hh.s06_offer_usd(spliced) is None
    assert s06_offer_dollars(spliced) is None
    kept = [
        {"@type": "Product", "sku": "S06", "offers": {"price": "25.00"}},
        {"@type": "Product", "sku": "S06B", "offers": {"price": "40.00"}},
    ]
    kept_page = product_html(node=kept, extra="<span>$40</span>")
    assert hh.s06_shows_25(kept_page) is True
    assert hh.s06_offer_usd(kept_page) == "25.00"
    assert s06_offer_dollars(kept_page) == 25
    split = [
        {"@type": "Product", "sku": "S06", "offers": {"price": "25.00"}},
        {"@type": "Product", "sku": "S006", "offers": {"price": "26"}},
    ]
    split_page = product_html(node=split, extra="<span>$25</span>")
    assert "$25" in split_page
    assert hh.s06_shows_25(split_page) is False
    assert hh.s06_offer_usd(product_html(node=split)) is None
    assert s06_offer_dollars(split_page) is None


def test_s06_jsonld_html_escaped_quotes_parse():
    raw = json.dumps({"@type": "Product", "sku": "S06", "offers": {"price": "25.00"}})
    escaped = raw.replace('"', "&quot;")
    page = f'<script type="application/ld+json">{escaped}</script><span>$30</span><span>$25</span>'
    assert "&quot;" in page and "&quot;price&quot;" in page
    assert "$30" in page and "$25" in page
    assert '"sku"' not in page
    assert hh.s06_shows_25(page) is False
    assert hh.s06_offer_usd(page) is None
    assert s06_offer_dollars(page) is None


def test_s06_jsonld_attribute_order_graph_and_offer_list():
    raw = json.dumps({"@type": "Product", "sku": "S06", "offers": {"price": "25.00"}})
    single = f"<script id='pdp' type='application/ld+json'>{raw}</script><span>$25</span>"
    assert "type='application/ld+json'" in single and "$25" in single
    assert hh.s06_shows_25(single) is False
    assert hh.s06_offer_usd(single) is None
    assert s06_offer_dollars(single) is None
    id_before = f'<script id="pdp" type="application/ld+json">{raw}</script>'
    id_after = f'<script type="application/ld+json" id="pdp">{raw}</script>'
    assert hh.s06_shows_25(id_before) is True
    assert hh.s06_shows_25(id_after) is True
    assert hh.s06_offer_usd(id_before) == "25.00"
    assert hh.s06_offer_usd(id_after) == "25.00"
    assert s06_offer_dollars(id_before) == 25
    assert s06_offer_dollars(id_after) == 25
    payload = {
        "@context": "https://schema.org",
        "@graph": [
            {"@type": "Organization", "name": "Sassy Closet"},
            {
                "@type": ["Product", "IndividualProduct"],
                "sku": "S6",
                "offers": [
                    {"@type": "Offer", "price": "25.0"},
                    {"@type": "Offer", "price": 25},
                ],
            },
        ],
    }
    page = f'<span>$19</span><script id="ld" type="application/ld+json">{json.dumps(payload)}</script>'
    assert "$19" in page and 'type="application/ld+json"' in page
    assert "type='application/ld+json'" not in page
    assert hh.s06_shows_25(page) is True
    assert hh.s06_offer_usd(page) == "25.00"
    assert s06_offer_dollars(page) == 25


def test_s06_spliced_price_does_not_pass(monkeypatch):
    s06 = {
        "@type": "Product",
        "sku": "S06",
        "offers": {"@type": "Offer", "price": "2$5", "priceCurrency": "USD"},
    }
    neighbour = {
        "@type": "Product",
        "sku": "A02",
        "offers": {"@type": "Offer", "price": "$25", "priceCurrency": "USD"},
    }
    body = (
        f'<script type="application/ld+json">{json.dumps(s06)}</script>'
        f'<script type="application/ld+json">{json.dumps(neighbour)}</script>'
        "<span>$25</span>"
    )
    assert "2$5" in body and "$25" in body
    assert s06_offer_dollars(body) is None
    assert hh.s06_shows_25(body) is False
    assert hh.s06_offer_usd(body) is None
    fake(monkeypatch, pages=s06_pages(body))
    summary = hh.run()
    assert hh.S06_LOCK == 25
    assert summary["overall"] == "FAIL"
    assert summary["fail"] and all("S06" in item for item in summary["fail"])
    assert {host for host in hh.VERCEL_HOSTS if any(host in item for item in summary["fail"])} == set(hh.VERCEL_HOSTS)
    assert all(row["s06_pdp"]["shows_25"] is False for row in summary["hosts"])
    assert all(row["s06_pdp"]["offer_usd"] is None for row in summary["hosts"])


def test_s06_lock_matches_too_cheap_and_daily():
    assert hh.S06_LOCK == 25
    assert hh.S06_LOCK == too_cheap_check.S06_LOCK_USD
    assert hh.S06_LOCK == dsc.S06_LOCK


def test_loose_dollar_regex_is_not_the_gate():
    assert not hasattr(hh, "shows_price")


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


@pytest.mark.parametrize("ma,alias", [("S19", "s019"), ("G01", "g001"), ("a024", "a024"), ("K3", "k003"), (" S19 ", "s019")])
def test_held_alias_spelling(ma, alias):
    assert hh.held_alias(ma) == alias and norm_ma(alias) == norm_ma(ma)


def test_held_alias_checked_and_404_pass(monkeypatch):
    fake(monkeypatch)
    s = hh.run()
    assert s["overall"] == "PASS"
    assert all(r["held_alias_pdp"] == {"ma": "s019", "status": 404} for r in s["hosts"])


def test_held_alias_served_is_fail(monkeypatch):
    # Canonical /m/S19 is 404 but the alias spelling serves the held piece.
    fake(monkeypatch, pages={"https://sassycloset.vercel.app/m/s019": (200, "S19", "")})
    s = hh.run()
    assert s["overall"] == "FAIL" and s["fail"] == ["sassycloset.vercel.app: held S19 alias /m/s019 -> 200 (want 404)"]
    md = hh.markdown(s)
    assert "held alias 404" in md and "s019 200" in md


def test_held_alias_network_error_is_fail(monkeypatch):
    fake(monkeypatch, pages={"https://sassy-closet-shop.vercel.app/m/s019": (None, "", "URLError: timed out")})
    s = hh.run()
    assert s["overall"] == "FAIL" and "alias /m/s019 -> URLError" in s["fail"][0]


def test_every_held_ma_from_held_json_is_404_on_both_hosts(monkeypatch):
    held_path = default_held_path()
    before = held_path.read_bytes()
    seen: list[str] = []
    fake(monkeypatch)
    inner = hh.fetch

    def record(url, timeout=0):
        seen.append(url)
        return inner(url, timeout)

    monkeypatch.setattr(hh, "fetch", record)
    summary = hh.run()
    assert summary["overall"] == "PASS"
    assert hh.VERCEL_HOSTS == ("sassycloset.vercel.app", "sassy-closet-shop.vercel.app")
    policy = load_held_policy()
    assert policy.held
    for host_name in hh.VERCEL_HOSTS:
        host_row = next(row for row in summary["hosts"] if row["host"] == host_name)
        by_ma = {row["ma"]: row for row in host_row["held_pdps"]}
        for ma in policy.held:
            alias = hh.held_alias(ma)
            assert by_ma[ma]["status"] == 404
            assert by_ma[ma]["alias"] == alias
            assert by_ma[ma]["alias_status"] == 404
            assert f"https://{host_name}/m/{ma}" in seen
            assert f"https://{host_name}/m/{alias}" in seen
    assert held_path.read_bytes() == before


def test_fixture_held_codes_one_live_fails(monkeypatch):
    bad_host, good_host = hh.VERCEL_HOSTS

    def scenario(pages, fail_line, k03_status, alias_status):
        fake(monkeypatch, pages=pages)
        summary = hh.run(codes=("K03", "S19"))
        assert summary["overall"] == "FAIL"
        assert fail_line in summary["fail"]
        assert all(good_host not in item for item in summary["fail"])
        assert all("K03" not in item for item in summary["fail"] if good_host in item)
        for host_row in summary["hosts"]:
            rows = host_row["held_pdps"]
            assert [row["ma"] for row in rows] == ["K03", "S19"]
            k03, s19 = rows
            assert k03["alias"] == "k003" and s19["alias"] == "s019"
            assert s19["status"] == 404 and s19["alias_status"] == 404
            if host_row["host"] == bad_host:
                assert k03["status"] == k03_status
                assert k03["alias_status"] == alias_status
            else:
                assert k03["status"] == 404 and k03["alias_status"] == 404
            assert host_row["s06_pdp"]["shows_25"] is True
            assert host_row["s06_pdp"]["offer_usd"] == "25.00"

    scenario(
        {f"https://{bad_host}/m/K03": (200, "live K03", "")},
        f"{bad_host}: held K03 PDP -> 200 (want 404)",
        200,
        404,
    )
    scenario(
        {f"https://{bad_host}/m/k003": (200, "live alias", "")},
        f"{bad_host}: held K03 alias /m/k003 -> 200 (want 404)",
        404,
        200,
    )
