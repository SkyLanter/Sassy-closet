"""Offline Taobao pages. No login, no network, no price rewrite."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import urllib.request
from decimal import Decimal
from pathlib import Path

import pytest

from freshness_check import (
    classify_taobao,
    evaluate,
    main,
    money_text,
    parse_taobao_cny,
    parse_taobao_final,
    parse_taobao_promo,
    parse_taobao_sizes,
    render_markdown,
    snapshot_from_json,
    taobao_blocked,
)
from test_freshness_check import _passing_payload

ROOT = Path(__file__).resolve().parents[2]
FIXTURES = Path(__file__).resolve().parent / "fixtures" / "taobao"
HELD_BYTES = (ROOT / "data" / "held.json").read_bytes()
PAD = " " * 2100


def _page(name: str) -> str:
    return (FIXTURES / name).read_text(encoding="utf-8")


def _row(ma: str, view) -> dict[str, object]:
    row: dict[str, object] = {"ma": ma, "state": view.state, "detail": view.detail}
    if view.public_cny is not None:
        row["public_cny"] = format(view.public_cny, "f")
    if view.promo_cny is not None:
        row["promo_cny"] = format(view.promo_cny, "f")
    if view.final_cny is not None:
        row["final_cny"] = format(view.final_cny, "f")
    if view.sizes is not None:
        row["sizes"] = list(view.sizes)
    return row


@pytest.fixture(autouse=True)
def _no_network(monkeypatch) -> None:
    def boom(*_args, **_kwargs):
        raise AssertionError("offline Taobao fixture opened the network")

    monkeypatch.setattr(urllib.request, "urlopen", boom)


def test_parser_source_does_not_send_a_cookie() -> None:
    source = (ROOT / "scripts" / "freshness_check.py").read_text(encoding="utf-8")
    assert "Cookie" not in source
    assert "tb_token" not in source
    assert (ROOT / "data" / "held.json").read_bytes() == HELD_BYTES


def test_login_wall_is_skip_not_fail() -> None:
    html = _page("login-wall.html")
    assert len(html) > 2000
    assert taobao_blocked(html) is True
    assert parse_taobao_cny(html) == Decimal("59.9")
    assert parse_taobao_promo(html) == Decimal("79.00")
    assert parse_taobao_final(html) == Decimal("70.00")
    assert parse_taobao_sizes(html) == ("S", "M", "L")
    view = classify_taobao(200, html)
    assert view.state == "skip"
    assert view.public_cny is None
    assert view.promo_cny is None
    assert view.final_cny is None
    assert view.sizes is None
    assert view.detail == "login-walled or unreachable"

    payload = _passing_payload()
    payload["intake"].append({"ma": "Z70", "cost_cny": "87.23", "sell_usd": ""})
    payload["taobao"].append(_row("Z70", view))
    payload["taobaoMode"] = "login"
    original = json.dumps(payload["intake"])
    report = evaluate(snapshot_from_json(payload))
    assert json.dumps(payload["intake"]) == original
    assert report.guards_pass
    text = render_markdown(report)
    assert "Guards: PASS" in text
    assert "\n- FAIL " not in text
    assert "SKIP (login-walled or unreachable)" in text
    row = next(item for item in report.rows if item["ma"] == "Z70")
    assert row["intakeCny"] == "87.23"
    assert row["publicCny"] is None
    assert row["publicState"] == "skip"
    assert not any(
        flag.ma == "Z70" and flag.kind in {"promo_cny", "final_cny", "above_public"} for flag in report.flags
    )
    assert (ROOT / "data" / "held.json").read_bytes() == HELD_BYTES


def test_bridge_page_reads_item_url_price() -> None:
    html = _page("bridge-list.html")
    assert "e.tb.cn" in html
    assert "price=59.9" in html
    assert "defaultItemPrice" not in html
    assert "priceText" not in html
    assert "reservePrice" not in html
    assert '"price"' not in html
    assert taobao_blocked(html) is False
    assert parse_taobao_cny(html) == Decimal("59.9")
    view = classify_taobao(200, html)
    assert view.state == "ok"
    assert view.public_cny == Decimal("59.9")
    assert view.promo_cny is None
    assert view.sizes is None
    assert classify_taobao(302, html).state == "skip"

    short_only = "https://e.tb.cn/h.onlyShort?price=12" + PAD
    assert parse_taobao_cny(short_only) is None
    other = "https://example.com/item.htm?id=1&price=1.00" + PAD
    assert parse_taobao_cny(other) is None
    first = "https://item.taobao.com/item.htm?price=59.9&id=1" + PAD
    assert parse_taobao_cny(first) == Decimal("59.9")
    escaped = "https://item.taobao.com/item.htm?id=9\\u0026price=59.9" + PAD
    assert parse_taobao_cny(escaped) == Decimal("59.9")
    tmall = "https://detail.tmall.com/item.htm?id=1&amp;price=41.5" + PAD
    assert parse_taobao_cny(tmall) == Decimal("41.5")

    payload = _passing_payload()
    payload["intake"].append({"ma": "Z72", "cost_cny": "80", "sell_usd": ""})
    payload["taobao"].append(_row("Z72", view))
    original = json.dumps(payload["intake"])
    report = evaluate(snapshot_from_json(payload))
    assert json.dumps(payload["intake"]) == original
    assert report.guards_pass
    row = next(item for item in report.rows if item["ma"] == "Z72")
    assert row["intakeCny"] == "80"
    assert row["publicCny"] == "59.9"
    flagged = [flag for flag in report.flags if flag.ma == "Z72"]
    assert len(flagged) == 1
    assert flagged[0].kind == "above_public"
    assert flagged[0].stored == "80"
    assert flagged[0].public_cny == "59.9"
    s06 = next(item for item in report.rows if item["ma"] == "S06")
    assert s06["blobUsd"] == "25"
    assert (ROOT / "data" / "held.json").read_bytes() == HELD_BYTES


def test_promo_and_final_are_flags_and_do_not_replace_intake() -> None:
    html = _page("promo-final.html")
    assert "priceText" in html
    assert taobao_blocked(html) is False
    view = classify_taobao(200, html)
    assert view.state == "ok"
    assert view.public_cny == Decimal("99.00")
    assert view.promo_cny == Decimal("79.00")
    assert view.final_cny == Decimal("70.00")
    assert view.sizes is None
    assert view.public_cny != view.promo_cny
    assert view.public_cny != view.final_cny

    payload = _passing_payload()
    payload["intake"].append({"ma": "Z99", "cost_cny": "87.23", "sell_usd": ""})
    payload["taobao"].append(_row("Z99", view))
    original = json.dumps(payload["intake"])
    logged_out = evaluate(snapshot_from_json(payload))
    assert not any(flag.kind in {"promo_cny", "final_cny"} for flag in logged_out.flags)
    quiet = next(item for item in logged_out.rows if item["ma"] == "Z99")
    assert quiet["intakeCny"] == "87.23"
    assert quiet["publicCny"] == money_text(Decimal("99.00"))

    payload["taobaoMode"] = "login"
    report = evaluate(snapshot_from_json(payload))
    assert json.dumps(payload["intake"]) == original
    assert report.guards_pass
    row = next(item for item in report.rows if item["ma"] == "Z99")
    assert row["intakeCny"] == "87.23"
    assert row["publicCny"] == "99"
    promo = [flag for flag in report.flags if flag.ma == "Z99" and flag.kind == "promo_cny"]
    final = [flag for flag in report.flags if flag.ma == "Z99" and flag.kind == "final_cny"]
    assert len(promo) == 1 and promo[0].stored == "87.23" and promo[0].public_cny == "79"
    assert len(final) == 1 and final[0].stored == "87.23" and final[0].public_cny == "70"
    body = json.dumps(report.rows)
    assert "corrected" not in body
    text = render_markdown(report)
    assert "Z99 | 87.23 |" in text
    assert "promo_cny: stored `87.23` public ¥ 79" in text
    assert "final_cny: stored `87.23` public ¥ 70" in text
    assert (ROOT / "data" / "held.json").read_bytes() == HELD_BYTES


def test_sku_size_table_is_parsed_when_present() -> None:
    html = _page("sku-size-table.html")
    assert "<table" in html
    assert "skuBase" not in html
    assert taobao_blocked(html) is False
    view = classify_taobao(200, html)
    assert view.state == "ok"
    assert view.public_cny == Decimal("88.00")
    assert view.sizes == ("S", "M", "L")
    assert "84" not in view.sizes
    assert "88" not in view.sizes
    assert "92" not in view.sizes

    column = (
        "<table><tr><th>尺码</th><th>胸围</th></tr>"
        "<tr><td><span>S</span></td><td>84</td></tr>"
        "<tr><td>M</td><td>88</td></tr>"
        "<tr><td>L</td><td>92</td></tr></table>"
    )
    assert parse_taobao_sizes(column) == ("S", "M", "L")
    sku = (
        '{"pid":"1627207","name":"颜色分类","values":[{"name":"杏色"},{"name":"黑色"}]},'
        '{"pid":"20509","name":"尺码","values":[{"name":"S"},{"name":"M"},{"name":"L"}]}'
    )
    assert parse_taobao_sizes(sku) == ("S", "M", "L")
    both = sku + '<table><tr><td>尺码</td><td>XL</td></tr></table>'
    assert parse_taobao_sizes(both) == ("S", "M", "L")
    colors = "<table><tr><td>颜色</td><td>杏色</td><td>黑色</td></tr></table>"
    assert parse_taobao_sizes(colors) is None
    english = "<table><tr><td>Size</td><td>S</td><td>M</td></tr></table>"
    assert parse_taobao_sizes(english) == ("S", "M")
    assert parse_taobao_sizes(_page("bridge-list.html")) is None

    bare = "<table><tr><td>尺码</td><td>S</td><td>M</td></tr></table>" + PAD
    bare_view = classify_taobao(200, bare)
    assert bare_view.state == "skip"
    assert bare_view.public_cny is None
    assert bare_view.sizes == ("S", "M")

    payload = _passing_payload()
    payload["intake"].append(
        {"ma": "Z73", "cost_cny": "90", "sell_usd": "", "link": "https://e.tb.cn/h.fixtureSku"}
    )
    payload["taobao"].append(_row("Z73", view))
    original = json.dumps(payload["intake"])
    report = evaluate(snapshot_from_json(payload))
    assert json.dumps(payload["intake"]) == original
    assert report.guards_pass
    decision = next(item for item in report.pickup if item.ma == "Z73")
    assert decision.flags == ("missing_photos",)
    assert decision.quoted_usd is None
    assert decision.publish is False
    assert decision.held is True
    row = next(item for item in report.rows if item["ma"] == "Z73")
    assert row["intakeCny"] == "90"
    assert row["publicCny"] == "88"
    assert (ROOT / "data" / "held.json").read_bytes() == HELD_BYTES


def test_cli_login_mode_is_fixture_only(tmp_path: Path) -> None:
    html = _page("promo-final.html")
    view = classify_taobao(200, html)
    payload = _passing_payload()
    payload["intake"].append({"ma": "Z99", "cost_cny": "87.23", "sell_usd": ""})
    payload["taobao"].append(_row("Z99", view))
    fixture = tmp_path / "promo.json"
    original = json.dumps(payload)
    fixture.write_text(original, encoding="utf-8")
    out = tmp_path / "out"
    code = main(["--fixture", str(fixture), "--out", str(out), "--date", "2026-10-11", "--mode", "login"])
    assert code == 0
    assert fixture.read_text(encoding="utf-8") == original
    saved = json.loads((out / "dataset-freshness-2026-10-11.json").read_text(encoding="utf-8"))
    assert saved["guardsPass"] is True
    promo = [flag for flag in saved["flags"] if flag["kind"] == "promo_cny" and flag["ma"] == "Z99"]
    final = [flag for flag in saved["flags"] if flag["kind"] == "final_cny" and flag["ma"] == "Z99"]
    assert promo and promo[0]["stored"] == "87.23" and promo[0]["publicCny"] == "79"
    assert final and final[0]["stored"] == "87.23" and final[0]["publicCny"] == "70"
    compared = next(item for item in saved["rows"] if item["ma"] == "Z99")
    assert compared["intakeCny"] == "87.23"
    assert compared["publicCny"] == "99"
    assert "corrected" not in json.dumps(saved)
    assert (ROOT / "data" / "held.json").read_bytes() == HELD_BYTES

    env = {key: value for key, value in os.environ.items() if key != "SASSY_TAOBAO_MODE"}
    ran = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "freshness_check.py"),
            "--fixture",
            str(fixture),
            "--out",
            str(out),
            "--date",
            "2026-10-11",
            "--mode",
            "logged-out",
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
        env=env,
    )
    assert ran.returncode == 0, ran.stderr
    saved = json.loads((out / "dataset-freshness-2026-10-11.json").read_text(encoding="utf-8"))
    assert not any(flag["kind"] in {"promo_cny", "final_cny"} for flag in saved["flags"])
    assert fixture.read_text(encoding="utf-8") == original
