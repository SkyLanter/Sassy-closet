"""A fixture sell price of 0 is flagged and left in place. Blank is not this flag."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from held_policy import load_held_policy
from zero_sell_price import CatalogRow, flag_zero_sell_prices, load_catalog, main, report_json

ROOT = Path(__file__).resolve().parents[2]
FIXTURES = Path(__file__).resolve().parent / "fixtures"
GAPS = FIXTURES / "zero_sell_price.json"
CLEAN = FIXTURES / "zero_sell_price_clean.json"
HELD = ROOT / "data" / "held.json"
CATALOG = ROOT / "sassy-closet-shop" / "data" / "products.json"
EXTRAS = ROOT / "sassy-closet-shop" / "data" / "intake-extras.json"
HELD_CODES = frozenset(load_held_policy().held)
SCRIPT = ROOT / "scripts" / "zero_sell_price.py"

EXPECTED = [
    ("K06", 0, True),
    ("A02", "0", False),
    ("P04", "  0  ", False),
]


def test_fixture_flags_zero_and_leaves_the_price() -> None:
    assert {"K06", "V05", "K02"} <= HELD_CODES
    assert "S06" not in HELD_CODES
    original = GAPS.read_text(encoding="utf-8")
    rows = load_catalog(GAPS)
    before = [(row.ma, row.price_usd, row.price_set) for row in rows]
    flags = flag_zero_sell_prices(rows, HELD_CODES)
    assert [(row.ma, row.price_usd, row.price_set) for row in rows] == before
    assert GAPS.read_text(encoding="utf-8") == original
    assert '"priceUsd": 0' in original
    assert len(rows) == 9
    found = [(flag.ma, flag.stored, flag.held) for flag in flags]
    assert found == EXPECTED
    assert rows[1].ma == "k06"
    assert rows[1].price_usd == 0
    assert rows[7].price_usd == "0"
    assert rows[8].price_usd == "  0  "
    assert all(flag.ma != "S06" for flag in flags)
    body = json.dumps(report_json(rows, flags, HELD_CODES), ensure_ascii=False)
    assert '"s06": "stays $25"' in body
    assert '"heldMas": "stay held"' in body
    assert '"readOnly": true' in body
    assert '"writes": []' in body
    assert "corrected" not in body
    assert "suggested" not in body
    assert "replacement" not in body
    parsed = json.loads(body)
    assert parsed["rows"][1] == {"ma": "K06", "held": True, "priceUsd": 0}
    assert parsed["rows"][7] == {"ma": "A02", "held": False, "priceUsd": "0"}
    assert parsed["rows"][8] == {"ma": "P04", "held": False, "priceUsd": "  0  "}
    assert parsed["flags"][0]["kind"] == "zero_sell_price"
    assert parsed["flags"][0]["field"] == "priceUsd"
    assert parsed["flags"][0]["stored"] == 0
    assert parsed["writes"] == []
    assert not any(key in parsed["flags"][0] for key in ("filled", "replacement", "price"))


def test_s06_stays_25_and_stays_clean() -> None:
    for path in (GAPS, CLEAN):
        original = path.read_text(encoding="utf-8")
        rows = load_catalog(path)
        flags = flag_zero_sell_prices(rows, HELD_CODES)
        assert path.read_text(encoding="utf-8") == original
        s06 = next(row for row in rows if row.ma.strip().upper() == "S06")
        assert s06.price_usd == 25
        assert s06.price_set is True
        assert all(flag.ma != "S06" for flag in flags)
        report = report_json(rows, flags, HELD_CODES)
        s06_row = next(row for row in report["rows"] if row["ma"] == "S06")
        assert s06_row == {"ma": "S06", "held": False, "priceUsd": 25}
        assert report["s06"] == "stays $25"


def test_blank_price_is_not_this_flag() -> None:
    rows = [
        CatalogRow("S06", 25, True),
        CatalogRow("V05", None, False),
        CatalogRow("K02", "", True),
        CatalogRow("H01", "   ", True),
        CatalogRow("P03", None, True),
        CatalogRow("A01", 27, True),
        CatalogRow("D05", False, True),
        CatalogRow("P01", "0.5", True),
        CatalogRow("K01", 10, True),
    ]
    before = [(row.ma, row.price_usd, row.price_set) for row in rows]
    flags = flag_zero_sell_prices(rows, HELD_CODES)
    assert [(row.ma, row.price_usd, row.price_set) for row in rows] == before
    assert flags == []
    gap_rows = load_catalog(GAPS)
    gap_flags = flag_zero_sell_prices(gap_rows, HELD_CODES)
    quiet = {"S06", "A01", "V05", "H01", "K02", "P03"}
    assert quiet.isdisjoint(flag.ma for flag in gap_flags)
    by_ma = {row.ma.strip().upper(): row for row in gap_rows}
    assert by_ma["V05"].price_set is False
    assert by_ma["K02"].price_usd == ""
    assert by_ma["H01"].price_usd == "   "
    assert by_ma["P03"].price_usd is None
    parsed = json.loads(json.dumps(report_json(gap_rows, gap_flags, HELD_CODES), ensure_ascii=False))
    v05 = next(row for row in parsed["rows"] if row["ma"] == "V05")
    assert v05 == {"ma": "V05", "held": True}
    assert "priceUsd" not in v05


def test_string_and_float_zero_are_flagged_not_rewritten() -> None:
    rows = [
        CatalogRow("S06", 25, True),
        CatalogRow("A07", 0.0, True),
        CatalogRow("P02", "0.00", True),
        CatalogRow("K01", 0, True),
        CatalogRow("Z02", 0, True),
        CatalogRow("Z02", 12, True),
    ]
    before = [(row.ma, row.price_usd, row.price_set) for row in rows]
    flags = flag_zero_sell_prices(rows, HELD_CODES)
    assert [(row.ma, row.price_usd, row.price_set) for row in rows] == before
    assert [(flag.ma, flag.stored, flag.held) for flag in flags] == [
        ("A07", 0.0, False),
        ("P02", "0.00", False),
        ("K01", 0, False),
        ("Z02", 0, False),
    ]
    assert rows[4].price_usd == 0
    assert rows[5].price_usd == 12


def test_clean_fixture_has_no_flags() -> None:
    original = CLEAN.read_text(encoding="utf-8")
    rows = load_catalog(CLEAN)
    flags = flag_zero_sell_prices(rows, HELD_CODES)
    assert flags == []
    assert CLEAN.read_text(encoding="utf-8") == original
    assert [row.ma for row in rows] == ["S06", "A01", "H01", "V05", "K02", "P03"]
    assert rows[0].price_usd == 25
    assert rows[1].price_usd == 27
    assert rows[2].price_usd == 8
    assert rows[4].price_usd == ""
    assert rows[5].price_usd is None
    report = report_json(rows, flags, HELD_CODES)
    assert report["flagCount"] == 0
    assert report["flags"] == []
    assert report["writes"] == []
    assert report["rows"][0] == {"ma": "S06", "held": False, "priceUsd": 25}
    assert report["rows"][3] == {"ma": "V05", "held": True}
    assert report["rows"][4] == {"ma": "K02", "held": True, "priceUsd": ""}


def test_cli_prints_the_flag_and_writes_nothing(tmp_path: Path) -> None:
    held_bytes = HELD.read_bytes()
    catalog_bytes = CATALOG.read_bytes()
    extras_bytes = EXTRAS.read_bytes()
    gaps_bytes = GAPS.read_bytes()
    clean_bytes = CLEAN.read_bytes()
    gaps = subprocess.run(
        [sys.executable, str(SCRIPT), "--catalog", str(GAPS)],
        cwd=tmp_path,
        check=False,
        capture_output=True,
        text=True,
    )
    assert gaps.returncode == 1, gaps.stderr
    assert gaps.stderr == ""
    report = json.loads(gaps.stdout)
    assert report["readOnly"] is True
    assert report["s06"] == "stays $25"
    assert report["flagCount"] == len(EXPECTED)
    assert report["writes"] == []
    found = [(flag["ma"], flag["stored"], flag["held"]) for flag in report["flags"]]
    assert found == EXPECTED
    assert all(flag["ma"] != "S06" for flag in report["flags"])
    assert report["rows"][0] == {"ma": "S06", "held": False, "priceUsd": 25}
    assert report["rows"][1] == {"ma": "K06", "held": True, "priceUsd": 0}
    assert "priceUsd" not in report["rows"][3]
    assert report["rows"][4]["priceUsd"] == "   "
    assert report["rows"][5]["priceUsd"] == ""
    assert report["rows"][6]["priceUsd"] is None
    assert "Washed distressed overalls" not in gaps.stdout
    assert "suggested" not in gaps.stdout
    assert "replacement" not in gaps.stdout
    assert list(tmp_path.iterdir()) == []
    assert HELD.read_bytes() == held_bytes
    assert CATALOG.read_bytes() == catalog_bytes
    assert EXTRAS.read_bytes() == extras_bytes
    assert GAPS.read_bytes() == gaps_bytes
    assert '"priceUsd": 0' in GAPS.read_text(encoding="utf-8")
    assert "K06" in HELD.read_text(encoding="utf-8")
    assert "V05" in HELD.read_text(encoding="utf-8")

    clean = subprocess.run(
        [sys.executable, str(SCRIPT), "--catalog", str(CLEAN)],
        cwd=tmp_path,
        check=False,
        capture_output=True,
        text=True,
    )
    assert clean.returncode == 0, clean.stderr
    clean_report = json.loads(clean.stdout)
    assert clean_report["flagCount"] == 0
    assert clean_report["flags"] == []
    assert clean_report["rows"][0] == {"ma": "S06", "held": False, "priceUsd": 25}
    assert all(row["ma"] != "S06" or row["priceUsd"] == 25 for row in clean_report["rows"])
    assert HELD.read_bytes() == held_bytes
    assert CATALOG.read_bytes() == catalog_bytes
    assert EXTRAS.read_bytes() == extras_bytes
    assert CLEAN.read_bytes() == clean_bytes


def test_cli_refuses_live_and_bad_fixtures(tmp_path: Path) -> None:
    held_bytes = HELD.read_bytes()
    catalog_bytes = CATALOG.read_bytes()
    refused = subprocess.run(
        [sys.executable, str(SCRIPT), "--catalog", "https://example.invalid/catalog.json"],
        cwd=tmp_path,
        check=False,
        capture_output=True,
        text=True,
    )
    assert refused.returncode == 2
    assert "Catalog fixtures only." in refused.stderr
    assert list(tmp_path.iterdir()) == []

    shop = subprocess.run(
        [sys.executable, str(SCRIPT), "--catalog", str(CATALOG)],
        cwd=tmp_path,
        check=False,
        capture_output=True,
        text=True,
    )
    assert shop.returncode == 2
    assert "Shop catalog files are not read." in shop.stderr
    assert CATALOG.read_bytes() == catalog_bytes
    assert HELD.read_bytes() == held_bytes

    named = tmp_path / "products.json"
    named.write_text(json.dumps([{"ma": "S06", "priceUsd": 25}, {"ma": "K06", "priceUsd": 0}]), encoding="utf-8")
    named_raw = named.read_text(encoding="utf-8")
    assert main(["--catalog", str(named)]) == 2
    assert named.read_text(encoding="utf-8") == named_raw
    assert '"priceUsd": 0' in named_raw

    held_as_catalog = main(["--catalog", str(HELD)])
    assert held_as_catalog == 2
    assert HELD.read_bytes() == held_bytes

    held_refused = main(["--catalog", str(CLEAN), "--held", "https://example.invalid/held.json"])
    assert held_refused == 2
    assert CLEAN.read_bytes()
    assert HELD.read_bytes() == held_bytes

    missing = main(["--catalog", str(tmp_path / "missing.json")])
    assert missing == 2
    broken = tmp_path / "broken.json"
    broken.write_text("{", encoding="utf-8")
    assert main(["--catalog", str(broken)]) == 2
    assert broken.read_text(encoding="utf-8") == "{"

    listed = tmp_path / "rows.json"
    listed.write_text(
        json.dumps(
            [
                {"ma": "S06", "priceUsd": 25},
                {"ma": "K06", "priceUsd": 0},
                {"ma": "H01", "priceUsd": "   "},
            ]
        ),
        encoding="utf-8",
    )
    raw = listed.read_text(encoding="utf-8")
    assert main(["--catalog", str(listed)]) == 1
    assert listed.read_text(encoding="utf-8") == raw

    blank_only = tmp_path / "blanks.json"
    blank_only.write_text(
        json.dumps(
            [
                {"ma": "S06", "priceUsd": 25},
                {"ma": "V05"},
                {"ma": "K02", "priceUsd": ""},
                {"ma": "P03", "priceUsd": None},
            ]
        ),
        encoding="utf-8",
    )
    blank_raw = blank_only.read_text(encoding="utf-8")
    assert main(["--catalog", str(blank_only)]) == 0
    assert blank_only.read_text(encoding="utf-8") == blank_raw

    priced = tmp_path / "priced.json"
    priced.write_text(json.dumps([{"ma": "S06", "priceUsd": 25}]), encoding="utf-8")
    priced_raw = priced.read_text(encoding="utf-8")
    assert main(["--catalog", str(priced)]) == 0
    assert priced.read_text(encoding="utf-8") == priced_raw
    assert HELD.read_bytes() == held_bytes
    assert CATALOG.read_bytes() == catalog_bytes


def test_script_has_no_write_or_network_calls() -> None:
    text = SCRIPT.read_text(encoding="utf-8")
    assert ".write_text" not in text
    assert "write_bytes" not in text
    assert "urlopen" not in text
    assert "requests" not in text
    assert "suggestedPrice" not in text
    assert "filledPrice" not in text
    assert "missing_sell_price" not in text
