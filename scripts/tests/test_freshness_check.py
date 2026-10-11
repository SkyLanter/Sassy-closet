"""Freshness guards on fixtures. No live Taobao or Blob call."""

from __future__ import annotations

import json
import subprocess
import sys
from decimal import Decimal
from pathlib import Path

from openpyxl import Workbook

from freshness_check import (
    ALIAS_ORIGIN,
    PRIMARY_ORIGIN,
    SELL_ORIGINS,
    classify_taobao,
    evaluate,
    parse_pdp_price,
    read_hub_official,
    render_markdown,
    report_json,
    snapshot_from_json,
    taobao_blocked,
    write_report,
)
from held_policy import load_held_policy

ROOT = Path(__file__).resolve().parents[2]


def _passing_payload() -> dict:
    policy = load_held_policy()
    origins = list(SELL_ORIGINS)
    pdp: dict = {}
    for code in list(policy.held) + list(policy.never_list):
        pdp[code] = {origin: {"status": 404} for origin in origins}
    pdp["S06"] = {origin: {"status": 200, "price_usd": "25"} for origin in origins}
    pdp["A07"] = {origin: {"status": 200, "price_usd": "26"} for origin in origins}
    pdp["S10"] = {origin: {"status": 200, "price_usd": "37"} for origin in origins}
    return {
        "day": "2026-10-11",
        "origins": origins,
        "intakeState": {"state": "ok"},
        "intake": [
            {"ma": "K01", "cost_cny": "", "sell_usd": "37"},
            {"ma": "H01", "cost_cny": "  ", "sell_usd": "8"},
            {"ma": "O04", "cost_cny": "", "sell_usd": ""},
            {"ma": "S07", "cost_cny": "127;145", "sell_usd": ""},
            {"ma": "S09", "cost_cny": "134", "sell_usd": ""},
            {"ma": "S11", "cost_cny": "221.43", "sell_usd": ""},
            {"ma": "S06", "cost_cny": "80", "sell_usd": ""},
            {"ma": "A07", "cost_cny": "87.23", "sell_usd": ""},
            {"ma": "S10", "cost_cny": "90", "sell_usd": ""},
        ],
        "blob": {
            "state": "ok",
            "rows": [
                {"ma": "S06", "price_usd": "25"},
                {"ma": "A07", "price_usd": "26"},
                {"ma": "S10", "price_usd": "37"},
            ],
        },
        "hub": {
            "state": "ok",
            "rows": [
                {"ma": "S06", "price_usd": "25"},
                {"ma": "A07", "price_usd": "26"},
                {"ma": "S10", "price_usd": "37"},
            ],
        },
        "pdp": pdp,
        "taobao": [
            {"ma": "S09", "state": "ok", "public_cny": "100", "detail": "fixture comparator"},
            {"ma": "S11", "state": "ok", "public_cny": "200", "detail": "fixture comparator"},
            {"ma": "A07", "state": "skip", "detail": "login-walled"},
        ],
    }


def test_default_origins_are_primary_and_alias() -> None:
    assert PRIMARY_ORIGIN in SELL_ORIGINS
    assert ALIAS_ORIGIN in SELL_ORIGINS
    assert len(SELL_ORIGINS) == 2


def test_passing_fixture_flags_yen_without_failing_guards() -> None:
    report = evaluate(snapshot_from_json(_passing_payload()))
    assert report.guards_pass
    found = {(flag.ma, flag.kind, flag.stored) for flag in report.flags}
    assert ("K01", "blank_cny", "") in found
    assert ("H01", "blank_cny", "  ") in found
    assert ("O04", "blank_cny", "") in found
    assert ("S07", "garbled_cny", "127;145") in found
    assert ("S09", "above_public", "134") in found
    assert ("S11", "above_public", "221.43") in found
    body = json.dumps(report_json(report))
    assert "127;145" in body
    assert "corrected" not in body
    assert "fixedCny" not in body
    text = render_markdown(report)
    assert "127;145" in text
    assert "Guards: PASS" in text
    assert "SKIP (login-walled)" in text


def test_blob_skip_is_not_a_guard_failure() -> None:
    payload = _passing_payload()
    payload["blob"] = {"state": "skip", "detail": "unreachable"}
    report = evaluate(snapshot_from_json(payload))
    assert report.guards_pass
    assert report.sources["blob"].state == "skip"


def test_held_pdp_200_fails() -> None:
    payload = _passing_payload()
    payload["pdp"]["K06"][PRIMARY_ORIGIN] = {"status": 200, "price_usd": "48"}
    report = evaluate(snapshot_from_json(payload))
    assert report.guards_pass is False
    assert any(not guard.ok and "K06" in guard.name for guard in report.guards)


def test_q02_pdp_200_fails() -> None:
    payload = _passing_payload()
    payload["pdp"]["Q02"][ALIAS_ORIGIN] = {"status": 200, "price_usd": "20"}
    assert evaluate(snapshot_from_json(payload)).guards_pass is False


def test_s06_not_25_fails_on_blob_and_pdp() -> None:
    blob_bad = _passing_payload()
    for row in blob_bad["blob"]["rows"]:
        if row["ma"] == "S06":
            row["price_usd"] = "24"
    assert evaluate(snapshot_from_json(blob_bad)).guards_pass is False
    pdp_bad = _passing_payload()
    pdp_bad["pdp"]["S06"][ALIAS_ORIGIN] = {"status": 200, "price_usd": "26"}
    assert evaluate(snapshot_from_json(pdp_bad)).guards_pass is False


def test_held_on_blob_fails_even_when_pdp_is_404() -> None:
    payload = _passing_payload()
    payload["blob"]["rows"].append({"ma": "V05", "price_usd": "27"})
    report = evaluate(snapshot_from_json(payload))
    assert report.guards_pass is False
    assert any(guard.name == "off-catalog:V05:blob" and not guard.ok for guard in report.guards)


def test_cli_writes_sibling_reports_and_exit_codes(tmp_path: Path) -> None:
    fixture = tmp_path / "pass.json"
    fixture.write_text(json.dumps(_passing_payload()), encoding="utf-8")
    out = tmp_path / "out"
    passed = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "freshness_check.py"),
            "--fixture",
            str(fixture),
            "--out",
            str(out),
            "--date",
            "2026-10-11",
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert passed.returncode == 0, passed.stderr
    markdown = out / "dataset-freshness-2026-10-11.md"
    sibling = out / "dataset-freshness-2026-10-11.json"
    assert markdown.is_file()
    assert sibling.is_file()
    assert "127;145" in markdown.read_text(encoding="utf-8")
    saved = json.loads(sibling.read_text(encoding="utf-8"))
    assert saved["guardsPass"] is True
    assert "corrected" not in sibling.read_text(encoding="utf-8")

    fail_payload = _passing_payload()
    fail_payload["pdp"]["V05"][PRIMARY_ORIGIN] = {"status": 200, "price_usd": "27"}
    fail_file = tmp_path / "fail.json"
    fail_file.write_text(json.dumps(fail_payload), encoding="utf-8")
    failed = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "freshness_check.py"),
            "--fixture",
            str(fail_file),
            "--out",
            str(out),
            "--date",
            "2026-10-11",
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert failed.returncode == 1
    assert json.loads(sibling.read_text(encoding="utf-8"))["guardsPass"] is False


def test_taobao_login_wall_is_skip_and_public_price_parses() -> None:
    assert taobao_blocked("login") is True
    wall = classify_taobao(200, "passport.taobao.com")
    assert wall.state == "skip"
    page = '{"priceText":"99"}' + (" " * 2100)
    assert taobao_blocked(page) is False
    parsed = classify_taobao(200, page)
    assert parsed.state == "ok"
    assert parsed.public_cny == Decimal("99")


def test_pdp_jsonld_price() -> None:
    html = (
        '<script type="application/ld+json">'
        '{"@type":"Product","offers":{"price":"25.00","priceCurrency":"USD"}}'
        "</script>"
    )
    assert parse_pdp_price(html) == Decimal("25")


def test_hub_official_reader(tmp_path: Path) -> None:
    book = Workbook()
    sheet = book.active
    sheet.title = "Official"
    sheet.cell(4, 1, "ma")
    sheet.cell(4, 2, "list_price")
    sheet.cell(5, 1, "S06")
    sheet.cell(5, 2, 25)
    sheet.cell(6, 1, "A07")
    sheet.cell(6, 2, 26)
    path = tmp_path / "hub.xlsx"
    book.save(path)
    rows = {row.ma: row.price_usd for row in read_hub_official(path)}
    assert rows["S06"] == Decimal("25")
    assert rows["A07"] == Decimal("26")
    assert "K06" not in rows
    assert "V05" not in rows
    assert "Q02" not in rows


def test_write_report_names(tmp_path: Path) -> None:
    report = evaluate(snapshot_from_json(_passing_payload()))
    markdown, sibling = write_report(report, tmp_path)
    assert markdown.name == "dataset-freshness-2026-10-11.md"
    assert sibling.name == "dataset-freshness-2026-10-11.json"
