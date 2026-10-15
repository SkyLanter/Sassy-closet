"""Fractional sell prices from fixtures. 25.50 stays 25.50. S06 at 25 stays clean."""

from __future__ import annotations

import json
import subprocess
import sys
from decimal import Decimal
from pathlib import Path

from held_policy import load_held_policy
from non_whole_dollar import CatalogRow, flag_non_whole_dollars, load_catalog, main, report_json

ROOT = Path(__file__).resolve().parents[2]
FIXTURES = Path(__file__).resolve().parent / "fixtures"
CENTS = FIXTURES / "non_whole_dollar.json"
CLEAN = FIXTURES / "non_whole_dollar_clean.json"
HELD = ROOT / "data" / "held.json"
CATALOG = ROOT / "sassy-closet-shop" / "data" / "products.json"
EXTRAS = ROOT / "sassy-closet-shop" / "data" / "intake-extras.json"
HELD_CODES = frozenset(load_held_policy().held)

EXPECTED = [
    ("A01", "25.50", False),
    ("K06", "  7.25", True),
]


def test_cents_fixture_flags_25_50_and_leaves_rows() -> None:
    assert {"K06", "K02", "V05"} <= HELD_CODES
    assert "S06" not in HELD_CODES
    assert "A01" not in HELD_CODES
    original = CENTS.read_text(encoding="utf-8")
    assert "25.50" in original
    rows = load_catalog(CENTS)
    before = [(row.ma, row.price_usd, row.price_set) for row in rows]
    flags = flag_non_whole_dollars(rows, HELD_CODES)
    assert [(row.ma, row.price_usd, row.price_set) for row in rows] == before
    assert CENTS.read_text(encoding="utf-8") == original
    assert len(rows) == 6
    found = [(flag.ma, flag.stored, flag.held) for flag in flags]
    assert found == EXPECTED
    assert all(flag.ma != "S06" for flag in flags)
    s06 = rows[0]
    assert s06.ma == "S06"
    assert s06.price_usd == 25
    assert s06.price_set is True
    assert rows[1].ma == "A01"
    assert rows[1].price_usd == "25.50"
    assert Decimal(rows[1].price_usd) == Decimal("25.50")
    assert rows[1].price_usd not in {25, 26, "25", "26", "26.00"}
    assert rows[2].ma == "k06"
    assert rows[2].price_usd == "  7.25"
    assert rows[4].price_usd == "12.00"
    assert rows[5].ma == "K02"
    assert rows[5].price_set is False
    assert rows[5].price_usd is None
    body = json.dumps(report_json(rows, flags, HELD_CODES), ensure_ascii=False)
    assert '"s06": "stays $25"' in body
    assert '"heldMas": "stay held"' in body
    assert '"readOnly": true' in body
    assert "rounded" not in body
    assert "suggested" not in body
    parsed = json.loads(body)
    assert parsed["rows"][0] == {"ma": "S06", "held": False, "priceUsd": 25}
    assert parsed["rows"][1] == {"ma": "A01", "held": False, "priceUsd": "25.50"}
    assert parsed["rows"][4] == {"ma": "V05", "held": True, "priceUsd": "12.00"}
    assert parsed["rows"][5] == {"ma": "K02", "held": True}
    assert "priceUsd" not in parsed["rows"][5]
    assert parsed["flags"][0]["kind"] == "non_whole_dollar"
    assert parsed["flags"][0]["field"] == "priceUsd"
    assert parsed["flags"][0]["stored"] == "25.50"
    assert Decimal(parsed["flags"][0]["stored"]) == Decimal("25.50")
    assert not any(key in parsed["flags"][0] for key in ("rounded", "replacement", "whole"))


def test_clean_fixture_has_no_flags_and_s06_stays_25() -> None:
    rows = load_catalog(CLEAN)
    flags = flag_non_whole_dollars(rows, HELD_CODES)
    assert flags == []
    assert [row.ma for row in rows] == ["S06", "A01", "H01"]
    assert rows[0].price_usd == 25
    assert rows[1].price_usd == 27
    assert rows[2].price_usd == 8
    report = report_json(rows, flags, HELD_CODES)
    assert report["flagCount"] == 0
    assert report["rows"][0] == {"ma": "S06", "held": False, "priceUsd": 25}
    assert all(flag_row["ma"] != "S06" or flag_row.get("priceUsd") == 25 for flag_row in report["rows"])


def test_whole_dollars_stay_and_cents_are_not_rounded() -> None:
    rows = [
        CatalogRow("S06", 25, True),
        CatalogRow("A01", "25.50", True),
        CatalogRow("H01", "25.00", True),
        CatalogRow("P03", "25.501", True),
        CatalogRow("A07", 25.5, True),
        CatalogRow("P02", Decimal("10.10"), True),
        CatalogRow("V05", None, True),
        CatalogRow("K02", "", True),
        CatalogRow("Z01", "   ", True),
        CatalogRow("Z02", True, True),
    ]
    before = [row.price_usd for row in rows]
    flags = flag_non_whole_dollars(rows, HELD_CODES)
    assert [row.price_usd for row in rows] == before
    assert rows[0].price_usd == 25
    assert rows[1].price_usd == "25.50"
    found = [(flag.ma, flag.stored) for flag in flags]
    assert found == [
        ("A01", "25.50"),
        ("P03", "25.501"),
        ("A07", "25.5"),
        ("P02", "10.10"),
    ]
    assert all(flag.stored not in {"25", "26", "10", "11"} for flag in flags)
    assert Decimal("25.50") == Decimal(flags[0].stored)
    assert flags[0].stored != "26"
    assert flags[0].stored != "25"


def test_same_ma_whole_and_cents_stay_separate() -> None:
    rows = [
        CatalogRow("Z02", "25.50", True),
        CatalogRow("Z02", 25, True),
    ]
    flags = flag_non_whole_dollars(rows, HELD_CODES)
    assert [row.price_usd for row in rows] == ["25.50", 25]
    assert [(flag.ma, flag.stored) for flag in flags] == [("Z02", "25.50")]
    assert rows[1].price_usd == 25


def test_cli_reports_fixture_and_does_not_write(tmp_path: Path) -> None:
    held_bytes = HELD.read_bytes()
    catalog_bytes = CATALOG.read_bytes()
    extras_bytes = EXTRAS.read_bytes()
    cents_bytes = CENTS.read_bytes()
    clean_bytes = CLEAN.read_bytes()
    cents = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "non_whole_dollar.py"), "--catalog", str(CENTS)],
        cwd=tmp_path,
        check=False,
        capture_output=True,
        text=True,
    )
    assert cents.returncode == 1, cents.stderr
    assert cents.stderr == ""
    report = json.loads(cents.stdout)
    assert report["readOnly"] is True
    assert report["s06"] == "stays $25"
    assert report["flagCount"] == len(EXPECTED)
    found = [(flag["ma"], flag["stored"], flag["held"]) for flag in report["flags"]]
    assert found == EXPECTED
    assert all(flag["ma"] != "S06" for flag in report["flags"])
    assert report["flags"][0]["stored"] == "25.50"
    assert Decimal(report["flags"][0]["stored"]) == Decimal("25.50")
    assert report["rows"][0] == {"ma": "S06", "held": False, "priceUsd": 25}
    assert report["rows"][1]["priceUsd"] == "25.50"
    assert report["rows"][2]["held"] is True
    assert report["rows"][2]["priceUsd"] == "  7.25"
    assert report["rows"][4]["priceUsd"] == "12.00"
    assert "priceUsd" not in report["rows"][5]
    assert "Washed distressed overalls" not in cents.stdout
    assert "rounded" not in cents.stdout
    assert "suggested" not in cents.stdout
    assert list(tmp_path.iterdir()) == []
    assert HELD.read_bytes() == held_bytes
    assert CATALOG.read_bytes() == catalog_bytes
    assert EXTRAS.read_bytes() == extras_bytes
    assert CENTS.read_bytes() == cents_bytes
    assert b"25.50" in CENTS.read_bytes()
    assert "K06" in HELD.read_text(encoding="utf-8")
    assert "V05" in HELD.read_text(encoding="utf-8")

    clean = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "non_whole_dollar.py"), "--catalog", str(CLEAN)],
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
            str(ROOT / "scripts" / "non_whole_dollar.py"),
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
        json.dumps([{"ma": "S06", "priceUsd": 25}, {"ma": "A01", "priceUsd": "25.50"}]),
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


def test_script_does_not_write_round_or_fetch() -> None:
    text = (ROOT / "scripts" / "non_whole_dollar.py").read_text(encoding="utf-8")
    assert "round(" not in text
    assert ".write_text" not in text
    assert "write_bytes" not in text
    assert "urlopen" not in text
    assert "requests" not in text
    assert "missing_sell_price" not in text
    assert "suggestedPrice" not in text
