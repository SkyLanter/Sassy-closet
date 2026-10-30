"""Catalog fixture diff. No Blob write, no live catalog write, no held.json write."""

from __future__ import annotations

import json
import subprocess
import sys
from decimal import Decimal
from pathlib import Path

from catalog_diff import (
    CatalogRow,
    HeldRow,
    PriceChange,
    diff_catalog_files,
    diff_catalogs,
    load_catalog,
    main,
    parse_catalog,
)
from held_policy import HeldPolicy, default_held_path, load_held_policy

ROOT = Path(__file__).resolve().parents[2]
BEFORE = ROOT / "scripts" / "fixtures" / "catalog-diff" / "before.json"
AFTER = ROOT / "scripts" / "fixtures" / "catalog-diff" / "after.json"
HELD = ROOT / "data" / "held.json"
PRODUCTS = ROOT / "sassy-closet-shop" / "data" / "products.json"


def test_fixture_diff_reports_add_remove_and_one_price_change() -> None:
    policy = load_held_policy()
    before = load_catalog(BEFORE)
    after = load_catalog(AFTER)
    report = diff_catalogs(before, after, policy)
    assert report.added == ("Z02",)
    assert report.removed == ("Z01",)
    assert report.price_changes == (PriceChange("Z03", "20", "24"),)
    assert report.s06_before == "25"
    assert report.s06_after == "25"
    assert before["S06"].price_usd == after["S06"].price_usd == Decimal("25")
    assert before["D05"].price_usd == after["D05"].price_usd == Decimal("26")
    assert before["S10"].price_usd == after["S10"].price_usd == Decimal("37")
    assert [row.ma for row in report.held] == sorted(policy.held)
    assert all(row.before_status == "hold" and row.after_status == "hold" for row in report.held)
    assert all(row.stays_held for row in report.held)
    changed = {change.ma for change in report.price_changes}
    for code in policy.held:
        assert code not in report.added
        assert code not in report.removed
        assert code not in changed
        assert before[code].status == after[code].status == "hold"
        assert before[code].price_usd is None
        assert after[code].price_usd is None


def test_fixture_files_keep_s06_at_25_and_held_rows_on_hold() -> None:
    policy = load_held_policy()
    for path in (BEFORE, AFTER):
        payload = json.loads(path.read_text(encoding="utf-8"))
        assert payload["schema"] == "catalog.v1"
        assert payload["siteId"] == "fixture"
        rows = {item["ma"]: item for item in payload["products"]}
        assert rows["S06"]["priceUsd"] == 25
        assert rows["S06"]["status"] == "available"
        for code in policy.held:
            assert rows[code]["status"] == "hold"
            assert rows[code]["priceUsd"] is None


def test_cli_prints_the_diff_and_writes_nothing() -> None:
    held_before = HELD.read_bytes()
    products_before = PRODUCTS.read_bytes()
    before_bytes = BEFORE.read_bytes()
    after_bytes = AFTER.read_bytes()
    completed = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "catalog_diff.py"),
            "--before",
            str(BEFORE),
            "--after",
            str(AFTER),
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert completed.returncode == 0, completed.stderr
    body = json.loads(completed.stdout)
    assert body["added"] == ["Z02"]
    assert body["removed"] == ["Z01"]
    assert body["priceChanges"] == [{"ma": "Z03", "before": "20", "after": "24"}]
    assert body["s06"] == {"before": "25", "after": "25"}
    assert body["held"]
    assert all(row["staysHeld"] is True and row["beforeStatus"] == "hold" for row in body["held"])
    assert HELD.read_bytes() == held_before
    assert PRODUCTS.read_bytes() == products_before
    assert BEFORE.read_bytes() == before_bytes
    assert AFTER.read_bytes() == after_bytes
    assert not (ROOT / "sassy-closet-shop" / "catalog.v1.json").exists()
    assert default_held_path() == HELD


def test_identical_fixtures_report_no_changes() -> None:
    before_bytes = BEFORE.read_bytes()
    report = diff_catalog_files(BEFORE, BEFORE)
    assert report.added == ()
    assert report.removed == ()
    assert report.price_changes == ()
    assert report.s06_before == report.s06_after == "25"
    assert all(row.stays_held for row in report.held)
    assert BEFORE.read_bytes() == before_bytes


def test_same_dollar_is_not_a_price_change() -> None:
    before = {
        "S06": CatalogRow("S06", Decimal("25"), "available"),
        "A01": CatalogRow("A01", Decimal("27.0"), "available"),
    }
    after = {
        "S06": CatalogRow("S06", Decimal("25.00"), "available"),
        "A01": CatalogRow("A01", Decimal("27"), "available"),
    }
    report = diff_catalogs(before, after, HeldPolicy(held=(), never_list=()))
    assert report.added == ()
    assert report.removed == ()
    assert report.price_changes == ()
    assert report.s06_before == report.s06_after == "25"
    assert before["S06"].price_usd == Decimal("25")
    assert after["A01"].price_usd == Decimal("27")


def test_null_to_number_is_reported_and_rows_are_not_rewritten() -> None:
    before_row = CatalogRow("A01", None, "hold")
    after_row = CatalogRow("A01", Decimal("27"), "available")
    report = diff_catalogs(
        {"A01": before_row},
        {"A01": after_row},
        HeldPolicy(held=(), never_list=()),
    )
    assert report.price_changes == (PriceChange("A01", None, "27"),)
    assert before_row.price_usd is None
    assert before_row.status == "hold"
    assert after_row.price_usd == Decimal("27")
    assert after_row.status == "available"


def test_held_status_is_observed_and_not_rewritten() -> None:
    before = {"V05": CatalogRow("V05", None, "hold")}
    after = {"V05": CatalogRow("V05", None, "available")}
    report = diff_catalogs(before, after, HeldPolicy(held=("V05",), never_list=()))
    assert report.added == ()
    assert report.removed == ()
    assert report.price_changes == ()
    assert report.held == (HeldRow("V05", "hold", "available", False),)
    assert before["V05"].status == "hold"
    assert after["V05"].status == "available"
    assert before["V05"].price_usd is None


def test_a_different_s06_dollar_is_reported_and_the_file_stays(tmp_path: Path) -> None:
    before = tmp_path / "before.json"
    after = tmp_path / "after.json"
    before.write_text(_document([_product("S06", 25, "available")]), encoding="utf-8")
    after.write_text(_document([_product("S06", 30, "available")]), encoding="utf-8")
    after_bytes = after.read_bytes()
    held_before = HELD.read_bytes()
    report = diff_catalog_files(before, after)
    assert report.price_changes == (PriceChange("S06", "25", "30"),)
    assert report.s06_before == "25"
    assert report.s06_after == "30"
    assert after.read_bytes() == after_bytes
    assert json.loads(after.read_text(encoding="utf-8"))["products"][0]["priceUsd"] == 30
    assert HELD.read_bytes() == held_before


def test_whole_dollar_float_matches_an_int() -> None:
    before = parse_catalog(_payload([_product("S06", 25, "available")]))
    after = parse_catalog(_payload([_product("S06", 25.0, "available")]))
    report = diff_catalogs(before, after, HeldPolicy(held=(), never_list=()))
    assert report.price_changes == ()
    assert report.s06_before == report.s06_after == "25"


def test_duplicate_and_invalid_catalogs_are_refused() -> None:
    try:
        parse_catalog(_payload([_product("S06", 25, "available"), _product("s06", 25, "available")]))
    except ValueError as error:
        assert "S06" in str(error)
    else:
        raise AssertionError("duplicate mã was accepted")
    try:
        parse_catalog({"schema": "catalog.v2", "products": []})
    except ValueError as error:
        assert "catalog.v1" in str(error)
    else:
        raise AssertionError("wrong schema was accepted")
    try:
        parse_catalog(_payload([_product("S06", True, "available")]))
    except ValueError as error:
        assert "priceUsd" in str(error)
    else:
        raise AssertionError("boolean price was accepted")
    try:
        parse_catalog(_payload([_product("S06", -1, "available")]))
    except ValueError as error:
        assert "negative" in str(error)
    else:
        raise AssertionError("negative price was accepted")


def test_main_refuses_held_json_a_url_and_a_missing_file(capsys) -> None:
    held_before = HELD.read_bytes()
    refused = main(["--before", str(HELD), "--after", str(AFTER)])
    assert refused == 2
    assert "held.json" in capsys.readouterr().err
    remote = main(["--before", "https://example.com/catalog.v1.json", "--after", str(AFTER)])
    assert remote == 2
    assert "local JSON fixtures" in capsys.readouterr().err
    missing = main(["--before", "scripts/fixtures/catalog-diff/missing.json", "--after", str(AFTER)])
    assert missing == 2
    assert "missing catalog fixture" in capsys.readouterr().err
    assert HELD.read_bytes() == held_before


def test_lowercase_ma_matches_the_same_code() -> None:
    before = parse_catalog(_payload([_product("z01", 18, "available")]))
    after = parse_catalog(
        _payload([_product("Z02", 22, "available"), _product("z01", 18, "available")])
    )
    report = diff_catalogs(before, after, HeldPolicy(held=(), never_list=()))
    assert report.added == ("Z02",)
    assert report.removed == ()
    assert report.price_changes == ()
    assert before["Z01"].price_usd == Decimal("18")


def test_script_has_no_write_or_network_calls() -> None:
    source = (ROOT / "scripts" / "catalog_diff.py").read_text(encoding="utf-8")
    for token in (
        "write_text",
        "write_bytes",
        "urlopen",
        "urllib",
        "urlretrieve",
        "mkdir",
        "@vercel/blob",
        "put(",
        "requests",
        "open(",
    ):
        assert token not in source


def _product(ma: str, price: object, status: str) -> dict[str, object]:
    return {"ma": ma, "priceUsd": price, "status": status}


def _payload(products: list[dict[str, object]]) -> dict[str, object]:
    return {
        "schema": "catalog.v1",
        "version": 1,
        "siteId": "fixture",
        "products": products,
    }


def _document(products: list[dict[str, object]]) -> str:
    return json.dumps(_payload(products))
