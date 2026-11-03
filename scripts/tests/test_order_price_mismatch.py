"""Order-line prices vs fixture catalog prices. Neither amount is rewritten."""

from __future__ import annotations

import json
import subprocess
import sys
from decimal import Decimal
from pathlib import Path

import pytest

from order_price_mismatch import (
    KINDS,
    MISMATCH,
    NO_CATALOG,
    NO_PRICE,
    CompareResult,
    Finding,
    OmittedLine,
    flag_fixture,
    main,
    render_report,
    write_outputs,
)

ROOT = Path(__file__).resolve().parents[2]
FIXTURE = Path(__file__).resolve().parent / "fixtures" / "order_price_mismatch.json"
HELD = ROOT / "data" / "held.json"
PRODUCTS = ROOT / "sassy-closet-shop" / "data" / "products.json"
SCRIPT = ROOT / "scripts" / "order_price_mismatch.py"

OTHER_DOLLARS = (
    (0, "0"),
    (1, "1"),
    (10, "10"),
    (24, "24"),
    (26, "26"),
    (30, "30"),
    (40, "40"),
    (99, "99"),
    ("0", "0"),
    ("24", "24"),
    ("26", "26"),
    ("30", "30"),
    ("24.00", "24.00"),
    ("26.00", "26.00"),
    ("25.01", "25.01"),
    ("25.50", "25.50"),
    (24.5, "24.5"),
)

CLEAN_DOLLARS = (25, "25", "25.00", "25.0", "$25", "25.000", 25.0)


def _s06_payload(price: object) -> dict[str, object]:
    return {
        "catalog": [{"ma": "S06", "priceUsd": "25"}],
        "lines": [{"ma": "S06", "title": "Satin skirt", "priceUsd": price}],
    }


def test_fixture_flags_only_the_line_whose_price_differs() -> None:
    payload = json.loads(FIXTURE.read_text(encoding="utf-8"))
    before = json.dumps(payload)
    result = flag_fixture(payload)
    assert json.dumps(payload) == before
    assert [(item.ma, item.kind, item.order_usd, item.catalog_usd) for item in result.findings] == [
        ("A02", MISMATCH, "20", "23"),
    ]
    assert [(item.ma, item.reason) for item in result.omitted] == [
        ("A01", NO_PRICE),
        ("Z99", NO_CATALOG),
    ]
    assert payload["catalog"][0]["priceUsd"] == "25"
    assert payload["lines"][0]["priceUsd"] == 25
    assert payload["lines"][1]["priceUsd"] == "28.00"
    assert payload["lines"][2]["priceUsd"] == 20
    assert "priceUsd" not in payload["lines"][3]
    assert payload["lines"][4]["priceUsd"] == 40


def test_s06_at_25_stays_clean_and_file_stays(tmp_path: Path) -> None:
    for price in CLEAN_DOLLARS:
        payload = _s06_payload(price)
        raw = json.dumps(payload)
        path = tmp_path / f"clean-{price}.json"
        path.write_text(raw, encoding="utf-8")
        before = path.read_bytes()
        held_before = HELD.read_bytes()
        products_before = PRODUCTS.read_bytes()
        result = flag_fixture(json.loads(raw))
        assert result.findings == ()
        assert result.omitted == ()
        assert path.read_bytes() == before
        assert HELD.read_bytes() == held_before
        assert PRODUCTS.read_bytes() == products_before
        stored = json.loads(path.read_text(encoding="utf-8"))
        assert stored["catalog"][0]["priceUsd"] == "25"
        assert stored["lines"][0]["priceUsd"] == price


@pytest.mark.parametrize(("price", "shown"), OTHER_DOLLARS)
def test_s06_other_dollar_is_flagged_and_file_stays(tmp_path: Path, price: object, shown: str) -> None:
    payload = _s06_payload(price)
    raw = json.dumps(payload)
    path = tmp_path / "order.json"
    path.write_text(raw, encoding="utf-8")
    before = path.read_bytes()
    held_before = HELD.read_bytes()
    products_before = PRODUCTS.read_bytes()
    out = tmp_path / "out"
    completed = subprocess.run(
        [sys.executable, str(SCRIPT), "--fixture", str(path), "--out", str(out)],
        check=False,
        capture_output=True,
        text=True,
    )
    assert completed.returncode == 1, completed.stderr
    assert path.read_bytes() == before
    assert HELD.read_bytes() == held_before
    assert PRODUCTS.read_bytes() == products_before
    stored = json.loads(path.read_text(encoding="utf-8"))
    assert stored["catalog"][0]["priceUsd"] == "25"
    assert stored["lines"][0]["priceUsd"] == price
    flags = json.loads((out / "flags.json").read_text(encoding="utf-8"))
    assert flags["flags"] == [
        {"ma": "S06", "kind": MISMATCH, "orderUsd": shown, "catalogUsd": "25"},
    ]
    assert flags["omitted"] == []
    body = json.dumps(flags)
    assert "corrected" not in body
    assert "fixedUsd" not in body
    report = (out / "report.md").read_text(encoding="utf-8")
    assert f"Mã S06 order `${shown}` catalog `$25`. Neither price was changed." in report
    assert Decimal(shown) != Decimal("25")


def test_each_line_uses_that_mas_catalog_price() -> None:
    payload = {
        "catalog": [
            {"ma": "S06", "priceUsd": "25"},
            {"ma": "A07", "priceUsd": "28"},
            {"ma": "D06", "priceUsd": "40"},
        ],
        "lines": [
            {"ma": "S06", "priceUsd": 25},
            {"ma": "A07", "priceUsd": 30},
            {"ma": "d06", "priceUsd": "40.00"},
        ],
    }
    before = json.dumps(payload)
    result = flag_fixture(payload)
    assert json.dumps(payload) == before
    assert [(item.ma, item.order_usd, item.catalog_usd) for item in result.findings] == [
        ("A07", "30", "28"),
    ]
    assert payload["catalog"][0]["priceUsd"] == "25"
    assert payload["catalog"][1]["priceUsd"] == "28"
    assert payload["catalog"][2]["priceUsd"] == "40"
    assert payload["lines"][1]["priceUsd"] == 30


def test_same_dollars_in_another_shape_stay_clean() -> None:
    payload = {
        "catalog": [{"ma": "A08", "priceUsd": 24.5}],
        "lines": [
            {"ma": "A08", "priceUsd": "24.50"},
            {"ma": "A08", "priceUsd": "24.5"},
        ],
    }
    originals = [line["priceUsd"] for line in payload["lines"]]
    result = flag_fixture(payload)
    assert result.findings == ()
    assert [line["priceUsd"] for line in payload["lines"]] == originals
    assert payload["catalog"][0]["priceUsd"] == 24.5


def test_missing_price_and_missing_catalog_add_nothing() -> None:
    payload = {
        "catalog": [{"ma": "A01", "priceUsd": "27"}],
        "lines": [
            {"ma": "A01", "title": "Puppy cardigan"},
            {"ma": "A01", "priceUsd": None},
            {"ma": "A01", "priceUsd": "  "},
            {"ma": "Z99", "priceUsd": 40},
        ],
    }
    before = json.dumps(payload)
    result = flag_fixture(payload)
    assert json.dumps(payload) == before
    assert result.findings == ()
    assert [(item.ma, item.reason) for item in result.omitted] == [
        ("A01", NO_PRICE),
        ("A01", NO_PRICE),
        ("A01", NO_PRICE),
        ("Z99", NO_CATALOG),
    ]
    assert "Z99" not in {row["ma"] for row in payload["catalog"]}
    assert payload["lines"][3]["priceUsd"] == 40


def test_report_names_both_amounts_and_leaves_them() -> None:
    payload = json.loads(FIXTURE.read_text(encoding="utf-8"))
    result = flag_fixture(payload)
    report = render_report(result)
    assert "Read-only" in report
    assert "Neither price was changed." in report
    assert "The fixture file was not rewritten." in report
    assert "Mã A02 order `$20` catalog `$23`. Neither price was changed." in report
    assert "A01 has no order price. No price was added." in report
    assert "Z99 has no catalog price. No price was added." in report
    assert "S06" not in report
    assert "corrected" not in report
    for item in result.findings:
        assert item.kind in KINDS
        body = json.dumps(item.as_json())
        assert "corrected" not in body
        assert "fixedUsd" not in body


def test_unknown_kind_and_reason_are_rejected() -> None:
    with pytest.raises(ValueError, match="unknown finding kind"):
        render_report(CompareResult((Finding("A02", "nope", "20", "23"),), ()))
    with pytest.raises(ValueError, match="unknown omit reason"):
        render_report(CompareResult((), (OmittedLine("A01", "held"),)))


def test_duplicate_catalog_ma_is_rejected() -> None:
    payload = {
        "catalog": [
            {"ma": "S06", "priceUsd": "25"},
            {"ma": "S06", "priceUsd": "30"},
        ],
        "lines": [],
    }
    with pytest.raises(ValueError, match="lists S06 twice"):
        flag_fixture(payload)
    assert payload["catalog"][0]["priceUsd"] == "25"
    assert payload["catalog"][1]["priceUsd"] == "30"


def test_bad_price_is_rejected_without_rewriting(tmp_path: Path) -> None:
    payload = {
        "catalog": [{"ma": "S06", "priceUsd": "25"}],
        "lines": [{"ma": "S06", "priceUsd": "thirty"}],
    }
    path = tmp_path / "bad-price.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    before = path.read_bytes()
    with pytest.raises(ValueError, match="price must be a number"):
        flag_fixture(json.loads(path.read_text(encoding="utf-8")))
    assert path.read_bytes() == before


def test_compare_leaves_fixture_held_json_and_products_unchanged() -> None:
    before_held = HELD.read_bytes()
    before_products = PRODUCTS.read_bytes()
    raw = FIXTURE.read_text(encoding="utf-8")
    payload = json.loads(raw)
    flag_fixture(payload)
    assert FIXTURE.read_text(encoding="utf-8") == raw
    assert HELD.read_bytes() == before_held
    assert PRODUCTS.read_bytes() == before_products
    assert payload["lines"][0]["priceUsd"] == 25
    assert payload["catalog"][0]["priceUsd"] == "25"


def test_outputs_are_the_report_files(tmp_path: Path) -> None:
    result = flag_fixture(json.loads(FIXTURE.read_text(encoding="utf-8")))
    write_outputs(result, tmp_path)
    assert sorted(path.name for path in tmp_path.iterdir()) == ["flags.json", "report.md"]
    payload = json.loads((tmp_path / "flags.json").read_text(encoding="utf-8"))
    assert payload["flags"] == [
        {"ma": "A02", "kind": MISMATCH, "orderUsd": "20", "catalogUsd": "23"},
    ]
    assert "S06" not in (tmp_path / "report.md").read_text(encoding="utf-8")


def test_cli_flags_the_fixture_and_leaves_the_file(tmp_path: Path) -> None:
    before_held = HELD.read_bytes()
    before_products = PRODUCTS.read_bytes()
    before_fixture = FIXTURE.read_bytes()
    out = tmp_path / "mismatch"
    completed = subprocess.run(
        [sys.executable, str(SCRIPT), "--fixture", str(FIXTURE), "--out", str(out)],
        check=False,
        capture_output=True,
        text=True,
    )
    assert completed.returncode == 1, completed.stderr
    report = (out / "report.md").read_text(encoding="utf-8")
    payload = json.loads((out / "flags.json").read_text(encoding="utf-8"))
    assert "Mã A02 order `$20` catalog `$23`. Neither price was changed." in report
    assert "S06" not in report
    assert payload["flags"][0]["orderUsd"] == "20"
    assert payload["flags"][0]["catalogUsd"] == "23"
    assert HELD.read_bytes() == before_held
    assert PRODUCTS.read_bytes() == before_products
    assert FIXTURE.read_bytes() == before_fixture


def test_cli_clean_s06_fixture_exits_zero(tmp_path: Path) -> None:
    fixture = tmp_path / "clean.json"
    original = json.dumps(_s06_payload(25))
    fixture.write_text(original, encoding="utf-8")
    out = tmp_path / "out"
    completed = subprocess.run(
        [sys.executable, str(SCRIPT), "--fixture", str(fixture), "--out", str(out)],
        check=False,
        capture_output=True,
        text=True,
    )
    assert completed.returncode == 0, completed.stderr
    report = (out / "report.md").read_text(encoding="utf-8")
    assert "Flags: 0" in report
    assert "No flags." in report
    assert "S06" not in report
    assert fixture.read_text(encoding="utf-8") == original
    stored = json.loads(fixture.read_text(encoding="utf-8"))
    assert stored["catalog"][0]["priceUsd"] == "25"
    assert stored["lines"][0]["priceUsd"] == 25


def test_cli_without_fixture_does_not_write(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    code = main(["--out", str(tmp_path / "unused")])
    assert code == 2
    assert not (tmp_path / "unused").exists()
    message = capsys.readouterr().out
    assert "fixture" in message
    assert "does not change an order price or a catalog price" in message


def test_cli_rejects_a_bad_fixture(tmp_path: Path) -> None:
    bad = tmp_path / "bad.json"
    bad.write_text("{", encoding="utf-8")
    code = main(["--fixture", str(bad), "--out", str(tmp_path / "out")])
    assert code == 2
    assert not (tmp_path / "out").exists()


def test_cli_refuses_shop_and_held_targets(tmp_path: Path) -> None:
    fixture = tmp_path / "order.json"
    fixture.write_text(json.dumps(_s06_payload(30)), encoding="utf-8")
    before = fixture.read_bytes()
    held_before = HELD.read_bytes()
    targets = (
        ROOT / "data" / "order-price-out",
        ROOT / "sassy-closet-shop" / "order-price-out",
        ROOT / "sassy-closet" / "order-price-out",
        HELD,
    )
    for target in targets:
        code = main(["--fixture", str(fixture), "--out", str(target)])
        assert code == 2
        assert not (ROOT / "data" / "order-price-out").exists()
        assert not (ROOT / "sassy-closet-shop" / "order-price-out").exists()
        assert not (ROOT / "sassy-closet" / "order-price-out").exists()
    assert fixture.read_bytes() == before
    assert HELD.read_bytes() == held_before
    code = main(["--fixture", str(fixture), "--out", str(fixture)])
    assert code == 2
    assert fixture.read_bytes() == before


def test_source_stays_fixture_only() -> None:
    source = SCRIPT.read_text(encoding="utf-8").lower()
    for banned in (
        "urllib",
        "requests",
        "httpx",
        "http.client",
        "held.json",
        "products.json",
        "vercel",
        "facebook",
        "instagram",
        "tesla",
        "packing_slip",
        "order_line_flags",
        "s06",
    ):
        assert banned not in source
