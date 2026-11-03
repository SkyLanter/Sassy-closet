"""Fixture-only catalog status flags. No live catalog and no row writes."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from catalog_status import flag_catalog_status, load_rows, main, report_json, render_markdown
from held_policy import load_held_policy

ROOT = Path(__file__).resolve().parents[2]
FIXTURES = Path(__file__).resolve().parent / "fixtures"
GAPS = FIXTURES / "catalog_status_gaps.json"
CLEAN = FIXTURES / "catalog_status_clean.json"
HELD = ROOT / "data" / "held.json"
CATALOG = ROOT / "sassy-closet-shop" / "data" / "products.json"
SCRIPT = ROOT / "scripts" / "catalog_status.py"

EXPECTED: dict[str, tuple[tuple[str, str, bool], ...]] = {
    "S06": (),
    "A01": (),
    "D05": (),
    "K06": (),
    "V05": (),
    "Z81": (("unknown_status", "reserved", False),),
    "Z82": (("blank_status", "null", False),),
    "Z83": (("missing_status", "", False),),
    "Z84": (("blank_status", "", False),),
    "Z85": (("blank_status", "  ", False),),
    "Z86": (("unknown_status", "Available", False),),
    "Z87": (("unknown_status", "staged", False),),
    "Z88": (("unreadable_status", "1", False),),
    "Z89": (("unreadable_status", "true", False),),
    "Z90": (("unknown_status", "sold-out", False),),
    "Z91": (("unknown_status", "live", False),),
    "Z92": (("unknown_status", "HOLD", False),),
    "Z93": (("unknown_status", "in_stock", False),),
    "K02": (("unknown_status", "draft", True),),
    "Z94": (),
    "Z95": (),
    "Z96": (("unreadable_status", '["sold"]', False),),
    "Z97": (("unknown_status", "pending", False),),
    "Z98": (("unknown_status", "archived", False),),
    "Z99": (("unknown_status", "sold ", False),),
    "Z70": (("blank_status", "n/a", False),),
    "Z71": (("unknown_status", "Sold", False),),
}

PRICES = {
    "S06": "25",
    "A01": "27",
    "D05": "26",
    "K06": None,
    "V05": None,
    "Z81": "40",
    "K02": None,
    "Z94": "36",
    "Z95": None,
}


def _rows(path: Path) -> list[dict[str, object]]:
    return load_rows(json.loads(path.read_text(encoding="utf-8")))


def test_gap_fixture_flags_unknown_statuses_and_keeps_rows() -> None:
    original = GAPS.read_text(encoding="utf-8")
    rows = _rows(GAPS)
    before = json.dumps(rows)
    report = flag_catalog_status(rows, load_held_policy())
    assert json.dumps(rows) == before
    assert GAPS.read_text(encoding="utf-8") == original
    found = {
        row.ma: tuple((flag.kind, flag.stored, flag.held) for flag in row.flags) for row in report.rows
    }
    assert found == EXPECTED
    assert report.flag_count == sum(len(flags) for flags in EXPECTED.values())
    by_ma = {row.ma: row for row in report.rows}
    assert by_ma["S06"].status == "available"
    assert by_ma["S06"].price_usd == "25"
    assert by_ma["S06"].held is False
    assert by_ma["K06"].status == "held"
    assert by_ma["K06"].held is True
    assert by_ma["V05"].status == "hold"
    assert by_ma["V05"].held is True
    assert by_ma["K02"].status == "draft"
    assert by_ma["K02"].held is True
    assert by_ma["Z81"].price_usd == "40"
    assert by_ma["Z94"].status == "held"
    assert by_ma["Z94"].held is False
    assert by_ma["Z95"].status == "hold"
    for ma, price in PRICES.items():
        assert by_ma[ma].price_usd == price
    stored = {str(row["ma"]): row for row in rows}
    assert stored["S06"]["status"] == "available"
    assert stored["S06"]["priceUsd"] == 25
    assert stored["S06"]["titleEn"] == "Washed distressed overalls"
    assert stored["Z81"]["status"] == "reserved"
    assert stored["Z81"]["priceUsd"] == 40
    assert stored["K02"]["status"] == "draft"
    assert stored["K06"]["status"] == "held"
    assert stored["V05"]["status"] == "hold"
    body = json.dumps(report_json(report))
    assert '"s06": "stays $25"' in body
    assert '"s06PriceUsd": "25"' in body
    assert '"heldMas": "stay held"' in body
    assert '"knownStatuses": ["available", "sold", "held"]' in body
    assert '"catalogHeldSpelling": "hold"' in body
    assert '"writes": []' in body
    assert "corrected" not in body
    assert "tesla" not in body.casefold()
    markdown = render_markdown(report)
    assert "Known statuses are available, sold, and held." in markdown
    assert 'The sell catalog stores held as "hold".' in markdown
    assert "S06 stays $25." in markdown
    assert "Held mãs stay held." in markdown
    assert "S06 | false | available | 25 | —" in markdown
    assert "K06 | true | held | — | —" in markdown
    assert "V05 | true | hold | — | —" in markdown
    assert "K02 unknown_status stored `draft` stays held" in markdown
    assert "Z81 unknown_status stored `reserved`" in markdown
    assert "Catalog rows, prices, and data/held.json were not written." in markdown


def test_clean_fixture_has_no_flags() -> None:
    report = flag_catalog_status(_rows(CLEAN), load_held_policy())
    assert report.flag_count == 0
    assert [row.ma for row in report.rows] == ["S06", "A01", "D05", "K06", "V05"]
    assert report.price_for("S06") == "25"
    assert next(row for row in report.rows if row.ma == "K06").held is True
    assert next(row for row in report.rows if row.ma == "V05").status == "hold"
    assert next(row for row in report.rows if row.ma == "D05").status == "sold"


def test_known_spellings_are_available_sold_held_and_catalog_hold() -> None:
    rows = [
        {"ma": "S06", "status": "available", "priceUsd": 25},
        {"ma": "D05", "status": "sold", "priceUsd": 26},
        {"ma": "Z94", "status": "held", "priceUsd": 36},
        {"ma": "P02", "status": "hold", "priceUsd": None},
    ]
    before = json.dumps(rows)
    report = flag_catalog_status(rows, load_held_policy())
    assert json.dumps(rows) == before
    assert report.flag_count == 0
    assert rows[0]["priceUsd"] == 25


def test_cli_writes_a_report_and_leaves_shop_files(tmp_path: Path) -> None:
    held_bytes = HELD.read_bytes()
    catalog_bytes = CATALOG.read_bytes()
    gaps_bytes = GAPS.read_bytes()
    clean_bytes = CLEAN.read_bytes()
    data_names = sorted(path.name for path in (ROOT / "data").iterdir())
    out = tmp_path / "out"
    gaps = subprocess.run(
        [sys.executable, str(SCRIPT), "--fixture", str(GAPS), "--out", str(out)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert gaps.returncode == 1, gaps.stderr
    assert "Catalog status flags:" in gaps.stdout
    markdown = (out / "catalog-status.md").read_text(encoding="utf-8")
    saved = json.loads((out / "catalog-status.json").read_text(encoding="utf-8"))
    assert "S06 stays $25." in markdown
    assert saved["flagCount"] == sum(len(flags) for flags in EXPECTED.values())
    assert saved["s06PriceUsd"] == "25"
    assert saved["writes"] == []
    assert saved["rows"][0]["priceUsd"] == "25"
    assert saved["rows"][0]["status"] == "available"
    k02 = next(row for row in saved["rows"] if row["ma"] == "K02")
    assert k02["status"] == "draft"
    assert k02["held"] is True
    assert HELD.read_bytes() == held_bytes
    assert CATALOG.read_bytes() == catalog_bytes
    assert GAPS.read_bytes() == gaps_bytes
    assert sorted(path.name for path in (ROOT / "data").iterdir()) == data_names

    clean_out = tmp_path / "clean"
    clean = subprocess.run(
        [sys.executable, str(SCRIPT), "--fixture", str(CLEAN), "--out", str(clean_out)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert clean.returncode == 0, clean.stderr
    assert json.loads((clean_out / "catalog-status.json").read_text(encoding="utf-8"))["flagCount"] == 0
    assert HELD.read_bytes() == held_bytes
    assert CATALOG.read_bytes() == catalog_bytes
    assert CLEAN.read_bytes() == clean_bytes
    held_text = HELD.read_text(encoding="utf-8")
    assert "K06" in held_text
    assert "V05" in held_text
    assert "K02" in held_text


def test_cli_refuses_live_catalogs_shop_files_and_bad_fixtures(tmp_path: Path) -> None:
    held_bytes = HELD.read_bytes()
    catalog_bytes = CATALOG.read_bytes()
    out = tmp_path / "out"
    refused = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--fixture",
            "https://sassycloset.vercel.app/sassy-closet-shop/catalog.v1.json",
            "--out",
            str(out),
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert refused.returncode == 2
    assert "Live catalogs are not read." in refused.stderr
    assert not out.exists()

    shop = main(["--fixture", str(CATALOG), "--out", str(out)])
    assert shop == 2
    assert CATALOG.read_bytes() == catalog_bytes
    assert not out.exists()

    held_as_catalog = main(["--fixture", str(HELD), "--out", str(out)])
    assert held_as_catalog == 2
    assert HELD.read_bytes() == held_bytes

    protected_out = main(["--fixture", str(CLEAN), "--out", str(ROOT / "data" / "status-out")])
    assert protected_out == 2
    assert not (ROOT / "data" / "status-out").exists()
    assert HELD.read_bytes() == held_bytes

    missing = main(["--fixture", str(tmp_path / "missing.json"), "--out", str(out)])
    assert missing == 2
    broken = tmp_path / "broken.json"
    broken.write_text("{", encoding="utf-8")
    assert main(["--fixture", str(broken), "--out", str(out)]) == 2
    assert broken.read_text(encoding="utf-8") == "{"
    nameless = tmp_path / "nameless.json"
    nameless.write_text('{"products": [{"status": "available", "priceUsd": 25}]}', encoding="utf-8")
    assert main(["--fixture", str(nameless), "--out", str(out)]) == 2
    assert nameless.read_text(encoding="utf-8") == '{"products": [{"status": "available", "priceUsd": 25}]}'
    live_held = main(
        ["--fixture", str(CLEAN), "--held", "https://example.invalid/held.json", "--out", str(out)]
    )
    assert live_held == 2
    assert HELD.read_bytes() == held_bytes


def test_script_has_no_live_client() -> None:
    text = SCRIPT.read_text(encoding="utf-8").casefold()
    assert "urllib" not in text
    assert "requests" not in text
    assert "http.client" not in text
    assert "vercel.app" not in text
    assert "square.com" not in text
    assert "tesla" not in text
    assert "restock_note" not in text
