"""Giá dollars vs fixture catalog prices. No caption rewrites and no price edits."""

from __future__ import annotations

import json
import subprocess
import sys
from decimal import Decimal
from pathlib import Path

import pytest

from caption_price_mismatch import (
    KINDS,
    MISMATCH,
    Caption,
    CatalogPrice,
    CompareResult,
    Finding,
    compare_prices,
    load_fixture,
    main,
    render_report,
    write_outputs,
)

ROOT = Path(__file__).resolve().parents[2]
FIXTURE = Path(__file__).resolve().parent / "fixtures" / "caption_price_mismatch.json"
HELD = ROOT / "data" / "held.json"
PRODUCTS = ROOT / "sassy-closet-shop" / "data" / "products.json"
SCRIPT = ROOT / "scripts" / "caption_price_mismatch.py"


def _loaded():
    fixture = load_fixture(FIXTURE)
    result = compare_prices(list(fixture.captions), fixture.catalog)
    return fixture, result


def test_fixture_flags_gia_dollars_that_differ_from_catalog() -> None:
    _fixture, result = _loaded()
    found = [
        (item.caption_id, item.ma, item.kind, item.excerpt, item.caption_usd, item.catalog_usd, item.line)
        for item in result.findings
    ]
    assert found == [
        ("a07-high", "A07", MISMATCH, "$30", "30", "26", 2),
        ("a02-low", "A02", MISMATCH, "$20", "20", "23", 2),
        ("cents-off", "A08", MISMATCH, "$24.00", "24.00", "24.50", 2),
        ("spaced-off", "S10", MISMATCH, "$ 40", "40", "37", 2),
        ("bare-off", "A07", MISMATCH, "28", "28", "26", 2),
        ("usd-off", "A08", MISMATCH, "24 USD", "24", "24.50", 2),
    ]


def test_s06_at_25_and_other_matches_stay_clean() -> None:
    fixture, result = _loaded()
    flagged = {item.caption_id for item in result.findings}
    clean_ids = (
        "s06",
        "s06-cents",
        "s06-ascii",
        "a07-match",
        "cents-match",
        "s10-match",
        "size-not-price",
        "bare-match",
        "usd-match",
        "inbox",
        "yen",
        "yen-suffix",
        "missing-gia",
        "no-ma",
        "unknown-ma",
    )
    for caption_id in clean_ids:
        assert caption_id not in flagged
    assert fixture.catalog["S06"].text == "25"
    assert fixture.catalog["S06"].amount == Decimal("25")
    s06 = next(caption for caption in fixture.captions if caption.id == "s06")
    assert s06.text.splitlines() == ["Mã S06", "Set đồ cưng xỉu", "Giá $25"]
    stored = json.loads(FIXTURE.read_text(encoding="utf-8"))
    s06_row = next(row for row in stored["captions"] if row["id"] == "s06")
    s06_price = next(row for row in stored["catalog"] if row["ma"] == "S06")
    assert s06_row["text"].endswith("Giá $25")
    assert s06_price["price_usd"] == "25"
    assert all(item.ma != "S06" for item in result.findings)


def test_ma_labels_use_the_catalog_row_for_that_code() -> None:
    catalog = {
        "A09": CatalogPrice("A09", Decimal("26"), "26"),
        "D06": CatalogPrice("D06", Decimal("40"), "40"),
        "V01": CatalogPrice("V01", Decimal("39"), "39"),
    }
    captions = [
        Caption("spaced-label", "M A09\nGiá $26"),
        Caption("ascii-label", "Ma D06\nGiá: $41"),
        Caption("bare", "V01\nGiá $39"),
    ]
    result = compare_prices(captions, catalog)
    assert [(item.caption_id, item.ma, item.excerpt, item.catalog_usd) for item in result.findings] == [
        ("ascii-label", "D06", "$41", "40"),
    ]


def test_size_line_is_not_a_price() -> None:
    _fixture, result = _loaded()
    assert all(item.caption_id != "size-not-price" for item in result.findings)
    assert all("36" not in item.excerpt for item in result.findings)


def test_same_dollars_in_another_shape_stay_clean() -> None:
    catalog = {"S06": CatalogPrice("S06", Decimal("25"), "25")}
    captions = [
        Caption("trailing", "Mã S06\nGiá: 25$"),
        Caption("spaced", "Mã S06\nGiá: $ 25"),
        Caption("double", "Mã S06\nGiá: $25$"),
        Caption("usd", "Mã S06\nGiá: 25 USD"),
        Caption("bare", "S06\nGiá: 25"),
    ]
    originals = [caption.text for caption in captions]
    result = compare_prices(captions, catalog)
    assert result.findings == ()
    assert [caption.text for caption in captions] == originals
    assert catalog["S06"].text == "25"


def test_one_line_can_flag_only_the_amount_that_differs() -> None:
    catalog = {"A07": CatalogPrice("A07", Decimal("26"), "26")}
    caption = Caption("mixed", "Mã A07\nGiá: $26 or $30")
    result = compare_prices([caption], catalog)
    assert [(item.excerpt, item.caption_usd, item.catalog_usd) for item in result.findings] == [
        ("$30", "30", "26"),
    ]
    assert caption.text == "Mã A07\nGiá: $26 or $30"


def test_s06_wrong_caption_is_flagged_without_changing_catalog_25() -> None:
    catalog = {"S06": CatalogPrice("S06", Decimal("25"), "25")}
    caption = Caption("s06-wrong", "Mã S06\nGiá: $30")
    result = compare_prices([caption], catalog)
    assert caption.text == "Mã S06\nGiá: $30"
    assert catalog["S06"].text == "25"
    assert catalog["S06"].amount == Decimal("25")
    assert [(item.ma, item.excerpt, item.caption_usd, item.catalog_usd) for item in result.findings] == [
        ("S06", "$30", "30", "25"),
    ]


def test_missing_ma_missing_dollars_and_unknown_ma_are_left_alone() -> None:
    catalog = {
        "A07": CatalogPrice("A07", Decimal("26"), "26"),
        "P02": CatalogPrice("P02", Decimal("12"), "12"),
    }
    captions = [
        Caption("no-ma", "WHITE ANGEL SET\nGiá $99"),
        Caption("inbox", "Mã K06\nGiá: Inbox giá"),
        Caption("yen", "Mã P02\nGiá: ¥100"),
        Caption("missing", "Mã A07\nSet đồ mới"),
        Caption("unknown", "Mã Q09\nGiá $40"),
    ]
    originals = [caption.text for caption in captions]
    result = compare_prices(captions, catalog)
    assert result.findings == ()
    assert [caption.text for caption in captions] == originals
    assert "Q09" not in catalog
    assert catalog["P02"].text == "12"


def test_whole_number_catalog_price_matches_s06(tmp_path: Path) -> None:
    path = tmp_path / "whole.json"
    path.write_text(
        json.dumps(
            {
                "catalog": [{"ma": "s06", "price_usd": 25}],
                "captions": [{"id": "s06", "text": "Mã S06\nGiá $25"}],
            }
        ),
        encoding="utf-8",
    )
    fixture = load_fixture(path)
    result = compare_prices(list(fixture.captions), fixture.catalog)
    assert result.findings == ()
    assert fixture.catalog["S06"].text == "25"
    assert fixture.catalog["S06"].amount == Decimal("25")
    assert path.read_text(encoding="utf-8").count("25") == 2


def test_report_names_both_amounts_and_leaves_them() -> None:
    _fixture, result = _loaded()
    report = render_report(result)
    assert "Read-only" in report
    assert "No caption was rewritten" in report
    assert "No price was changed" in report
    assert "No Facebook or Instagram post was created, edited, or deleted." in report
    assert "Giá dollars differ from the catalog price" in report
    assert "Mã A07 line 2 caption `$30` catalog `$26`. Neither amount was changed." in report
    assert "Mã A02 line 2 caption `$20` catalog `$23`. Neither amount was changed." in report
    assert "Mã A08 line 2 caption `$24.00` catalog `$24.50`. Neither amount was changed." in report
    assert "Mã S10 line 2 caption `$ 40` catalog `$37`. Neither amount was changed." in report
    assert "S06" not in report
    assert "corrected" not in report
    assert "rewrite" not in report.lower()
    for item in result.findings:
        assert item.kind in KINDS
        body = json.dumps(item.as_json())
        assert "corrected" not in body
        assert "fixedUsd" not in body


def test_unknown_kind_is_rejected() -> None:
    result = CompareResult((Finding("x", "A07", "nope", "$30", "30", "26", 2),))
    with pytest.raises(ValueError, match="unknown finding kind"):
        render_report(result)


def test_duplicate_catalog_ma_is_rejected(tmp_path: Path) -> None:
    path = tmp_path / "twice.json"
    path.write_text(
        json.dumps(
            {
                "catalog": [
                    {"ma": "S06", "price_usd": "25"},
                    {"ma": "S06", "price_usd": "30"},
                ],
                "captions": [],
            }
        ),
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="lists S06 twice"):
        load_fixture(path)


def test_bad_catalog_price_is_rejected(tmp_path: Path) -> None:
    path = tmp_path / "bad-price.json"
    path.write_text(
        json.dumps(
            {
                "catalog": [{"ma": "A07", "price_usd": "$26"}],
                "captions": [],
            }
        ),
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="not a dollar amount"):
        load_fixture(path)


def test_compare_leaves_fixture_held_json_and_products_unchanged() -> None:
    before_held = HELD.read_bytes()
    before_products = PRODUCTS.read_bytes()
    raw = FIXTURE.read_text(encoding="utf-8")
    fixture = load_fixture(FIXTURE)
    captions = list(fixture.captions)
    originals = [caption.text for caption in captions]
    prices = {code: price.text for code, price in fixture.catalog.items()}
    compare_prices(captions, fixture.catalog)
    assert [caption.text for caption in captions] == originals
    assert {code: price.text for code, price in fixture.catalog.items()} == prices
    assert prices["S06"] == "25"
    assert FIXTURE.read_text(encoding="utf-8") == raw
    assert HELD.read_bytes() == before_held
    assert PRODUCTS.read_bytes() == before_products


def test_outputs_are_the_report_files(tmp_path: Path) -> None:
    _fixture, result = _loaded()
    write_outputs(result, tmp_path)
    assert sorted(path.name for path in tmp_path.iterdir()) == ["findings.json", "report.md"]
    payload = json.loads((tmp_path / "findings.json").read_text(encoding="utf-8"))
    assert payload["findings"][0]["id"] == "a07-high"
    assert payload["findings"][0]["catalogUsd"] == "26"
    assert "S06" not in (tmp_path / "report.md").read_text(encoding="utf-8")


def test_cli_writes_report(tmp_path: Path) -> None:
    before_held = HELD.read_bytes()
    before_products = PRODUCTS.read_bytes()
    before_fixture = FIXTURE.read_bytes()
    out = tmp_path / "gia-mismatch"
    completed = subprocess.run(
        [sys.executable, str(SCRIPT), "--fixture", str(FIXTURE), "--out", str(out)],
        check=False,
        capture_output=True,
        text=True,
    )
    assert completed.returncode == 1, completed.stderr
    report = (out / "report.md").read_text(encoding="utf-8")
    payload = json.loads((out / "findings.json").read_text(encoding="utf-8"))
    assert "caption `$30` catalog `$26`" in report
    assert "caption `$20` catalog `$23`" in report
    assert "S06" not in report
    assert payload["findings"][0]["captionUsd"] == "30"
    assert HELD.read_bytes() == before_held
    assert PRODUCTS.read_bytes() == before_products
    assert FIXTURE.read_bytes() == before_fixture


def test_cli_clean_s06_fixture_exits_zero(tmp_path: Path) -> None:
    fixture = tmp_path / "clean.json"
    fixture.write_text(
        json.dumps(
            {
                "catalog": [{"ma": "S06", "price_usd": "25"}],
                "captions": [{"id": "s06", "text": "Mã S06\nGiá $25"}],
            }
        ),
        encoding="utf-8",
    )
    out = tmp_path / "out"
    completed = subprocess.run(
        [sys.executable, str(SCRIPT), "--fixture", str(fixture), "--out", str(out)],
        check=False,
        capture_output=True,
        text=True,
    )
    assert completed.returncode == 0, completed.stderr
    report = (out / "report.md").read_text(encoding="utf-8")
    assert "Findings: 0" in report
    assert "No findings." in report
    assert "S06" not in report
    stored = json.loads(fixture.read_text(encoding="utf-8"))
    assert stored["catalog"][0]["price_usd"] == "25"
    assert stored["captions"][0]["text"].endswith("Giá $25")


def test_cli_without_fixture_does_not_write(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    code = main(["--out", str(tmp_path / "unused")])
    assert code == 2
    assert not (tmp_path / "unused").exists()
    message = capsys.readouterr().out
    assert "fixture" in message
    assert "does not rewrite captions" in message
    assert "change a price" in message


def test_cli_rejects_a_bad_fixture(tmp_path: Path) -> None:
    bad = tmp_path / "bad.json"
    bad.write_text("{", encoding="utf-8")
    code = main(["--fixture", str(bad), "--out", str(tmp_path / "out")])
    assert code == 2
    assert not (tmp_path / "out").exists()


def test_source_stays_fixture_only() -> None:
    source = SCRIPT.read_text(encoding="utf-8").lower()
    for banned in (
        "urllib",
        "requests",
        "httpx",
        "http.client",
        "held.json",
        "products.json",
        "facebook.com",
        "instagram.com",
        "vercel",
        "caption_lint",
        "caption_price_format",
        "s06",
    ):
        assert banned not in source
