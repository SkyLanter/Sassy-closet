"""Missing sell prices from fixtures. Rows stay as stored. held.json stays put."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from held_policy import load_held_policy
from missing_sell_price import CatalogRow, flag_missing_sell_prices, load_catalog, main, report_json

ROOT = Path(__file__).resolve().parents[2]
FIXTURES = Path(__file__).resolve().parent / "fixtures"
GAPS = FIXTURES / "missing_sell_price.json"
CLEAN = FIXTURES / "missing_sell_price_clean.json"
HELD = ROOT / "data" / "held.json"
CATALOG = ROOT / "sassy-closet-shop" / "data" / "products.json"
EXTRAS = ROOT / "sassy-closet-shop" / "data" / "intake-extras.json"
HELD_CODES = frozenset(load_held_policy().held)

EXPECTED = [
    ("K06", "null", "null", True),
    ("V05", "missing", "", True),
    ("H01", "blank", "   ", False),
    ("K02", "blank", "", True),
]


def test_gap_fixture_flags_missing_prices_and_leaves_rows() -> None:
    assert {"K06", "V05", "K02"} <= HELD_CODES
    assert "S06" not in HELD_CODES
    original = GAPS.read_text(encoding="utf-8")
    rows = load_catalog(GAPS)
    before = [(row.ma, row.price_usd, row.price_set) for row in rows]
    flags = flag_missing_sell_prices(rows, HELD_CODES)
    assert [(row.ma, row.price_usd, row.price_set) for row in rows] == before
    assert GAPS.read_text(encoding="utf-8") == original
    assert len(rows) == 6
    found = [(flag.ma, flag.reason, flag.stored, flag.held) for flag in flags]
    assert found == EXPECTED
    assert all(flag.ma != "S06" for flag in flags)
    s06 = rows[0]
    assert s06.ma == "S06"
    assert s06.price_usd == 25
    assert s06.price_set is True
    assert rows[1].ma == "k06"
    assert rows[1].price_usd is None
    assert rows[3].ma == "V05"
    assert rows[3].price_set is False
    assert rows[3].price_usd is None
    assert rows[4].price_usd == "   "
    body = json.dumps(report_json(rows, flags, HELD_CODES), ensure_ascii=False)
    assert '"s06": "stays $25"' in body
    assert '"heldMas": "stay held"' in body
    assert '"readOnly": true' in body
    assert "corrected" not in body
    assert "suggested" not in body
    parsed = json.loads(body)
    assert parsed["rows"][0] == {"ma": "S06", "held": False, "priceUsd": 25}
    assert parsed["rows"][1] == {"ma": "K06", "held": True, "priceUsd": None}
    assert parsed["rows"][3] == {"ma": "V05", "held": True}
    assert "priceUsd" not in parsed["rows"][3]
    assert parsed["flags"][0]["kind"] == "missing_sell_price"
    assert parsed["flags"][0]["field"] == "priceUsd"
    assert parsed["flags"][0]["stored"] == "null"
    assert not any(key in parsed["flags"][0] for key in ("filled", "replacement", "price"))


def test_clean_fixture_has_no_flags_and_s06_stays_25() -> None:
    rows = load_catalog(CLEAN)
    flags = flag_missing_sell_prices(rows, HELD_CODES)
    assert flags == []
    assert [row.ma for row in rows] == ["S06", "A01", "H01"]
    assert rows[0].price_usd == 25
    assert rows[1].price_usd == 27
    assert rows[2].price_usd == 8
    report = report_json(rows, flags, HELD_CODES)
    assert report["flagCount"] == 0
    assert report["rows"][0] == {"ma": "S06", "held": False, "priceUsd": 25}
    assert all(flag_row["ma"] != "S06" or flag_row.get("priceUsd") == 25 for flag_row in report["rows"])


def test_present_prices_stay_and_are_not_flagged() -> None:
    rows = [
        CatalogRow("S06", 25, True),
        CatalogRow("A01", 27, True),
        CatalogRow("H01", 0, True),
        CatalogRow("P03", "11", True),
        CatalogRow("A07", " 26 ", True),
    ]
    before = [row.price_usd for row in rows]
    flags = flag_missing_sell_prices(rows, HELD_CODES)
    assert flags == []
    assert [row.price_usd for row in rows] == before
    assert rows[0].price_usd == 25


def test_same_ma_missing_and_priced_rows_stay_separate() -> None:
    rows = [
        CatalogRow("Z02", None, True),
        CatalogRow("Z02", 12, True),
    ]
    flags = flag_missing_sell_prices(rows, HELD_CODES)
    assert [row.price_usd for row in rows] == [None, 12]
    assert [(flag.ma, flag.reason, flag.stored) for flag in flags] == [("Z02", "null", "null")]


def test_cli_reports_fixture_and_does_not_write(tmp_path: Path) -> None:
    held_bytes = HELD.read_bytes()
    catalog_bytes = CATALOG.read_bytes()
    extras_bytes = EXTRAS.read_bytes()
    gaps_bytes = GAPS.read_bytes()
    clean_bytes = CLEAN.read_bytes()
    gaps = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "missing_sell_price.py"), "--catalog", str(GAPS)],
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
    found = [(flag["ma"], flag["reason"], flag["stored"], flag["held"]) for flag in report["flags"]]
    assert found == EXPECTED
    assert all(flag["ma"] != "S06" for flag in report["flags"])
    assert report["rows"][0] == {"ma": "S06", "held": False, "priceUsd": 25}
    assert report["rows"][1]["held"] is True
    assert report["rows"][1]["priceUsd"] is None
    assert "priceUsd" not in report["rows"][3]
    assert "Washed distressed overalls" not in gaps.stdout
    assert "suggested" not in gaps.stdout
    assert list(tmp_path.iterdir()) == []
    assert HELD.read_bytes() == held_bytes
    assert CATALOG.read_bytes() == catalog_bytes
    assert EXTRAS.read_bytes() == extras_bytes
    assert GAPS.read_bytes() == gaps_bytes
    assert "K06" in HELD.read_text(encoding="utf-8")
    assert "V05" in HELD.read_text(encoding="utf-8")

    clean = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "missing_sell_price.py"), "--catalog", str(CLEAN)],
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


def test_cli_rejects_live_and_bad_catalogs(tmp_path: Path) -> None:
    refused = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "missing_sell_price.py"),
            "--catalog",
            "https://example.invalid/catalog.json",
        ],
        cwd=tmp_path,
        check=False,
        capture_output=True,
        text=True,
    )
    assert refused.returncode == 2
    assert "Catalog fixtures only." in refused.stderr
    assert list(tmp_path.iterdir()) == []

    held_refused = main(["--catalog", str(CLEAN), "--held", "https://example.invalid/held.json"])
    assert held_refused == 2
    assert CLEAN.is_file()

    missing = main(["--catalog", str(tmp_path / "missing.json")])
    assert missing == 2
    broken = tmp_path / "broken.json"
    broken.write_text("{", encoding="utf-8")
    assert main(["--catalog", str(broken)]) == 2
    assert broken.read_text(encoding="utf-8") == "{"
    listed = tmp_path / "rows.json"
    listed.write_text(
        json.dumps([{"ma": "S06", "priceUsd": 25}, {"ma": "K06", "priceUsd": None}]),
        encoding="utf-8",
    )
    raw = listed.read_text(encoding="utf-8")
    assert main(["--catalog", str(listed)]) == 1
    assert listed.read_text(encoding="utf-8") == raw
    priced = tmp_path / "priced.json"
    priced.write_text(json.dumps([{"ma": "S06", "priceUsd": 25}]), encoding="utf-8")
    priced_raw = priced.read_text(encoding="utf-8")
    assert main(["--catalog", str(priced)]) == 0
    assert priced.read_text(encoding="utf-8") == priced_raw


def test_script_does_not_write_or_fetch() -> None:
    text = (ROOT / "scripts" / "missing_sell_price.py").read_text(encoding="utf-8")
    assert ".write_text" not in text
    assert "write_bytes" not in text
    assert "urlopen" not in text
    assert "requests" not in text
    assert "suggestedPrice" not in text
    assert "filledPrice" not in text
