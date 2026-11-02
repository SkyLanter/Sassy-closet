"""Blank catalog status stays live, and a boolean price is not a dollar."""
import json

import export_daily_inputs as e


def catalog(tmp_path, products):
    path = tmp_path / "live.json"
    path.write_text(json.dumps({"products": products}), encoding="utf-8")
    return path


def test_blank_status_stays_live(tmp_path):
    live = e.load_live(catalog(tmp_path, [
        {"ma": "S06", "priceUsd": 30, "status": " "},
        {"ma": "A02", "priceUsd": 22, "status": None},
        {"ma": "A03", "priceUsd": 23, "status": "\n"},
        {"ma": "A04", "priceUsd": 24, "status": " Available "},
        {"ma": "A07", "priceUsd": 11},
        {"ma": "Z03", "priceUsd": 19, "status": " sold "},
        {"ma": "S14", "priceUsd": 28, "status": "hold"},
        {"ma": "A05", "priceUsd": 10, "status": True},
    ]))
    assert live["S06"] == 30
    assert live["A02"] == 22
    assert live["A03"] == 23
    assert live["A04"] == 24
    assert live["A07"] == 11
    assert "Z03" not in live and "S14" not in live and "A05" not in live


def test_bool_price_is_not_one_dollar():
    assert e._price(True) is None
    assert e._price(False) is None
    assert e._price(25.0) == 25
    assert e._price("25") == 25


def test_non_object_row_is_skipped(tmp_path):
    live = e.load_live(catalog(tmp_path, [
        "nope",
        None,
        {"ma": "A01", "priceUsd": 22, "status": "available"},
    ]))
    assert live == {"A01": 22}


def test_only_non_object_rows_fail_the_export(tmp_path):
    cat = catalog(tmp_path, ["nope", None])
    held = tmp_path / "held.json"
    held.write_text(json.dumps({"heldIncomplete": [], "neverList": []}), encoding="utf-8")
    assert e.main([
        "--live", str(cat), "--held", str(held), "--date", "2026-01-02",
        "--out-dir", str(tmp_path / "daily-inputs"),
    ]) == 2
    assert not (tmp_path / "daily-inputs").exists()


def test_all_sold_rows_still_export(tmp_path):
    live = e.load_live(catalog(tmp_path, [
        {"ma": "Z03", "priceUsd": 19, "status": "sold"},
    ]))
    assert live == {}


def test_bad_ma_still_fails_the_export(tmp_path):
    cat = catalog(tmp_path, [{"ma": "../etc", "priceUsd": 1}, "nope"])
    held = tmp_path / "held.json"
    held.write_text(json.dumps({"heldIncomplete": [], "neverList": []}), encoding="utf-8")
    assert e.main([
        "--live", str(cat), "--held", str(held), "--date", "2026-01-02",
        "--out-dir", str(tmp_path / "daily-inputs"),
    ]) == 2
    assert not (tmp_path / "daily-inputs").exists()
