"""Blank catalog titles from fixtures. Rows stay as stored. held.json stays put."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from blank_titles import CatalogRow, flag_blank_titles, load_catalog, main, report_json
from held_policy import load_held_policy

ROOT = Path(__file__).resolve().parents[2]
FIXTURES = Path(__file__).resolve().parent / "fixtures"
GAPS = FIXTURES / "blank_titles.json"
CLEAN = FIXTURES / "blank_titles_clean.json"
HELD = ROOT / "data" / "held.json"
CATALOG = ROOT / "sassy-closet-shop" / "data" / "products.json"
EXTRAS = ROOT / "sassy-closet-shop" / "data" / "intake-extras.json"
HELD_CODES = frozenset(load_held_policy().held)

EXPECTED = [
    ("S06", "titleVn", "blank", "   ", False),
    ("K06", "titleEn", "missing", "", True),
    ("K06", "titleVn", "null", "null", True),
    ("V05", "titleEn", "blank", "", True),
    ("V05", "titleVn", "blank", "", True),
    ("Z01", "titleEn", "not_a_string", "0", False),
]


def test_gap_fixture_flags_blank_titles_and_leaves_rows() -> None:
    original = GAPS.read_text(encoding="utf-8")
    rows = load_catalog(GAPS)
    before = [(row.ma, row.title_en, row.title_vn, row.price_usd) for row in rows]
    flags = flag_blank_titles(rows, HELD_CODES)
    assert [(row.ma, row.title_en, row.title_vn, row.price_usd) for row in rows] == before
    assert GAPS.read_text(encoding="utf-8") == original
    assert len(rows) == 7
    found = [(flag.ma, flag.field, flag.reason, flag.stored, flag.held) for flag in flags]
    assert found == EXPECTED
    s06 = rows[0]
    assert s06.ma == "S06"
    assert s06.title_en == "Washed distressed overalls"
    assert s06.title_vn == "   "
    assert s06.price_usd == 25
    assert rows[1].ma == "k06"
    assert rows[1].title_en_set is False
    assert rows[1].title_vn is None
    assert rows[1].price_usd is None
    body = json.dumps(report_json(rows, flags, HELD_CODES), ensure_ascii=False)
    assert '"s06": "stays $25"' in body
    assert '"heldMas": "stay held"' in body
    assert '"readOnly": true' in body
    assert "corrected" not in body
    assert "suggestedTitle" not in body
    s06_row = json.loads(body)["rows"][0]
    assert s06_row == {"ma": "S06", "held": False, "priceUsd": 25}
    k06_row = json.loads(body)["rows"][1]
    assert k06_row == {"ma": "K06", "held": True, "priceUsd": None}


def test_clean_fixture_has_no_flags_and_s06_stays_25() -> None:
    rows = load_catalog(CLEAN)
    flags = flag_blank_titles(rows, HELD_CODES)
    assert flags == []
    assert [row.ma for row in rows] == ["S06", "A01", "K06"]
    assert rows[0].price_usd == 25
    assert rows[0].title_en == "Washed distressed overalls"
    assert rows[0].title_vn == "Yếm jean wash rách"
    assert rows[2].price_usd is None
    report = report_json(rows, flags, HELD_CODES)
    assert report["flagCount"] == 0
    assert report["rows"][0]["priceUsd"] == 25
    assert report["rows"][0]["held"] is False
    assert report["rows"][2]["held"] is True


def test_filled_title_around_spaces_is_kept() -> None:
    row = CatalogRow("H01", "  Polo wrap dress  ", "Đầm polo", True, True, 8, True)
    assert flag_blank_titles([row], HELD_CODES) == []
    assert row.title_en == "  Polo wrap dress  "
    assert row.price_usd == 8


def test_same_ma_blank_rows_stay_separate() -> None:
    rows = [
        CatalogRow("Z02", "", "Áo len puppy", True, True, 11, True),
        CatalogRow("Z02", "Puppy cardigan", " ", True, True, 12, True),
    ]
    flags = flag_blank_titles(rows, HELD_CODES)
    assert [row.price_usd for row in rows] == [11, 12]
    assert [(flag.ma, flag.field, flag.stored) for flag in flags] == [
        ("Z02", "titleEn", ""),
        ("Z02", "titleVn", " "),
    ]


def test_cli_reports_fixture_and_does_not_write(tmp_path: Path) -> None:
    held_bytes = HELD.read_bytes()
    catalog_bytes = CATALOG.read_bytes()
    extras_bytes = EXTRAS.read_bytes()
    gaps_bytes = GAPS.read_bytes()
    clean_bytes = CLEAN.read_bytes()
    gaps = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "blank_titles.py"), "--catalog", str(GAPS)],
        cwd=tmp_path,
        check=False,
        capture_output=True,
        text=True,
    )
    assert gaps.returncode == 1, gaps.stderr
    assert gaps.stderr == ""
    report = json.loads(gaps.stdout)
    assert report["readOnly"] is True
    assert report["flagCount"] == len(EXPECTED)
    found = [
        (flag["ma"], flag["field"], flag["reason"], flag["stored"], flag["held"]) for flag in report["flags"]
    ]
    assert found == EXPECTED
    assert report["rows"][0]["priceUsd"] == 25
    assert report["rows"][1]["held"] is True
    assert report["rows"][3]["held"] is True
    assert "Washed distressed overalls" not in gaps.stdout
    assert list(tmp_path.iterdir()) == []
    assert HELD.read_bytes() == held_bytes
    assert CATALOG.read_bytes() == catalog_bytes
    assert EXTRAS.read_bytes() == extras_bytes
    assert GAPS.read_bytes() == gaps_bytes
    assert "K06" in HELD.read_text(encoding="utf-8")
    assert "V05" in HELD.read_text(encoding="utf-8")

    clean = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "blank_titles.py"), "--catalog", str(CLEAN)],
        cwd=tmp_path,
        check=False,
        capture_output=True,
        text=True,
    )
    assert clean.returncode == 0, clean.stderr
    clean_report = json.loads(clean.stdout)
    assert clean_report["flagCount"] == 0
    assert clean_report["rows"][0] == {"ma": "S06", "held": False, "priceUsd": 25}
    assert clean_report["rows"][2]["held"] is True
    assert HELD.read_bytes() == held_bytes
    assert CATALOG.read_bytes() == catalog_bytes
    assert EXTRAS.read_bytes() == extras_bytes
    assert CLEAN.read_bytes() == clean_bytes


def test_cli_rejects_live_and_bad_catalogs(tmp_path: Path) -> None:
    refused = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "blank_titles.py"), "--catalog", "https://example.invalid/catalog.json"],
        cwd=tmp_path,
        check=False,
        capture_output=True,
        text=True,
    )
    assert refused.returncode == 2
    assert "Catalog fixtures only." in refused.stderr
    assert list(tmp_path.iterdir()) == []

    missing = main(["--catalog", str(tmp_path / "missing.json")])
    assert missing == 2
    broken = tmp_path / "broken.json"
    broken.write_text("{", encoding="utf-8")
    assert main(["--catalog", str(broken)]) == 2
    assert broken.read_text(encoding="utf-8") == "{"
    listed = tmp_path / "rows.json"
    listed.write_text(json.dumps([{"ma": "S06", "titleEn": "", "titleVn": "Yếm jean wash rách", "priceUsd": 25}]), encoding="utf-8")
    raw = listed.read_text(encoding="utf-8")
    assert main(["--catalog", str(listed)]) == 1
    assert listed.read_text(encoding="utf-8") == raw


def test_script_does_not_write_or_compare_titles() -> None:
    text = (ROOT / "scripts" / "blank_titles.py").read_text(encoding="utf-8")
    assert ".write_text" not in text
    assert "urlopen" not in text
    assert "requests" not in text
    assert "title_overlap" not in text
    assert "SequenceMatcher" not in text
