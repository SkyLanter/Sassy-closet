"""Mã-only catalog titles from fixtures. Rows stay as stored. held.json stays put."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from held_policy import load_held_policy
from ma_only_titles import CatalogRow, flag_ma_only_titles, load_catalog, main, report_json

ROOT = Path(__file__).resolve().parents[2]
FIXTURES = Path(__file__).resolve().parent / "fixtures"
GAPS = FIXTURES / "ma_only_titles.json"
CLEAN = FIXTURES / "ma_only_titles_clean.json"
HELD = ROOT / "data" / "held.json"
CATALOG = ROOT / "sassy-closet-shop" / "data" / "products.json"
EXTRAS = ROOT / "sassy-closet-shop" / "data" / "intake-extras.json"
HELD_CODES = frozenset(load_held_policy().held)

EXPECTED = [
    ("A01", "titleEn", "A01", False),
    ("K06", "titleEn", "K06", True),
    ("K06", "titleVn", "  k06 ", True),
]


def test_gap_fixture_flags_a_title_that_is_only_the_ma() -> None:
    original = GAPS.read_text(encoding="utf-8")
    rows = load_catalog(GAPS)
    before = [(row.ma, row.title_en, row.title_vn, row.price_usd) for row in rows]
    flags = flag_ma_only_titles(rows, HELD_CODES)
    assert [(row.ma, row.title_en, row.title_vn, row.price_usd) for row in rows] == before
    assert GAPS.read_text(encoding="utf-8") == original
    assert len(rows) == 4
    found = [(flag.ma, flag.field, flag.stored, flag.held) for flag in flags]
    assert found == EXPECTED
    s06 = rows[0]
    assert s06.ma == "S06"
    assert s06.title_en == "Washed distressed overalls"
    assert s06.title_vn == "Yếm jean wash rách"
    assert s06.price_usd == 25
    a01 = rows[1]
    assert a01.title_en == "A01"
    assert a01.title_vn == "Áo len puppy A01"
    assert a01.price_usd == 27
    assert rows[2].title_en == "Rabbit hair bows H01"
    assert rows[2].price_usd == 8
    assert rows[3].ma == "k06"
    assert rows[3].price_usd is None
    body = json.dumps(report_json(rows, flags, HELD_CODES), ensure_ascii=False)
    assert '"s06": "stays $25"' in body
    assert '"heldMas": "stay held"' in body
    assert '"readOnly": true' in body
    assert '"kind": "ma_only"' in body
    assert "corrected" not in body
    assert "suggestedTitle" not in body
    parsed = json.loads(body)
    assert parsed["rows"][0] == {"ma": "S06", "held": False, "priceUsd": 25}
    assert parsed["rows"][3] == {"ma": "K06", "held": True, "priceUsd": None}
    assert "Washed distressed overalls" not in body
    assert "Áo len puppy A01" not in body
    assert "Rabbit hair bows H01" not in body


def test_real_title_that_contains_the_ma_stays_quiet() -> None:
    rows = load_catalog(CLEAN)
    flags = flag_ma_only_titles(rows, HELD_CODES)
    assert flags == []
    assert [row.ma for row in rows] == ["S06", "A01", "K06"]
    assert rows[0].price_usd == 25
    assert rows[0].title_en == "Washed distressed overalls"
    assert rows[0].title_vn == "Yếm jean wash rách"
    assert rows[1].title_en == "Puppy cardigan A01"
    assert rows[1].title_vn == "Áo len puppy"
    assert rows[1].price_usd == 27
    assert rows[2].price_usd is None
    report = report_json(rows, flags, HELD_CODES)
    assert report["flagCount"] == 0
    assert report["rows"][0]["priceUsd"] == 25
    assert report["rows"][0]["held"] is False
    assert report["rows"][2]["held"] is True
    assert "Puppy cardigan A01" not in json.dumps(report)


def test_surrounding_space_and_case_still_count_as_only_the_ma() -> None:
    row = CatalogRow("a01", "  a01  ", "Áo len puppy A01", True, True, 27, True)
    flags = flag_ma_only_titles([row], HELD_CODES)
    assert [(flag.field, flag.stored) for flag in flags] == [("titleEn", "  a01  ")]
    assert row.title_en == "  a01  "
    assert row.title_vn == "Áo len puppy A01"
    assert row.price_usd == 27


def test_other_shapes_stay_quiet() -> None:
    rows = [
        CatalogRow("A01", "A01.", "Áo len puppy", True, True, 27, True),
        CatalogRow("A01", "A010", "(A01)", True, True, 27, True),
        CatalogRow("A01", "S06", "A01 A01", True, True, 27, True),
        CatalogRow("A01", "", "   ", True, True, 27, True),
        CatalogRow("A01", None, 0, True, True, 27, True),
        CatalogRow("A01", "A01", "Áo len puppy", False, True, 27, True),
        CatalogRow("S06", "Washed distressed overalls S06", "Yếm jean wash rách", True, True, 25, True),
    ]
    assert flag_ma_only_titles(rows, HELD_CODES) == []
    assert rows[6].price_usd == 25
    assert rows[6].title_en == "Washed distressed overalls S06"
    assert rows[2].title_en == "S06"


def test_same_ma_rows_stay_separate() -> None:
    rows = [
        CatalogRow("A01", "A01", "Áo len puppy", True, True, 27, True),
        CatalogRow("A01", "Puppy cardigan", "A01", True, True, 28, True),
    ]
    flags = flag_ma_only_titles(rows, HELD_CODES)
    assert [row.price_usd for row in rows] == [27, 28]
    assert [(flag.field, flag.stored) for flag in flags] == [
        ("titleEn", "A01"),
        ("titleVn", "A01"),
    ]


def test_cli_reports_fixture_and_does_not_write(tmp_path: Path) -> None:
    held_bytes = HELD.read_bytes()
    catalog_bytes = CATALOG.read_bytes()
    extras_bytes = EXTRAS.read_bytes()
    gaps_bytes = GAPS.read_bytes()
    clean_bytes = CLEAN.read_bytes()
    gaps = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "ma_only_titles.py"), "--catalog", str(GAPS)],
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
    found = [(flag["ma"], flag["field"], flag["stored"], flag["held"]) for flag in report["flags"]]
    assert found == EXPECTED
    assert report["rows"][0]["priceUsd"] == 25
    assert report["rows"][1]["priceUsd"] == 27
    assert report["rows"][2]["priceUsd"] == 8
    assert report["rows"][3]["held"] is True
    assert "Washed distressed overalls" not in gaps.stdout
    assert "Áo len puppy A01" not in gaps.stdout
    assert "Rabbit hair bows H01" not in gaps.stdout
    assert list(tmp_path.iterdir()) == []
    assert HELD.read_bytes() == held_bytes
    assert CATALOG.read_bytes() == catalog_bytes
    assert EXTRAS.read_bytes() == extras_bytes
    assert GAPS.read_bytes() == gaps_bytes
    assert "K06" in HELD.read_text(encoding="utf-8")
    assert "V05" in HELD.read_text(encoding="utf-8")

    clean = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "ma_only_titles.py"), "--catalog", str(CLEAN)],
        cwd=tmp_path,
        check=False,
        capture_output=True,
        text=True,
    )
    assert clean.returncode == 0, clean.stderr
    clean_report = json.loads(clean.stdout)
    assert clean_report["flagCount"] == 0
    assert clean_report["rows"][0] == {"ma": "S06", "held": False, "priceUsd": 25}
    assert clean_report["rows"][1]["priceUsd"] == 27
    assert clean_report["rows"][2]["held"] is True
    assert "Puppy cardigan A01" not in clean.stdout
    assert HELD.read_bytes() == held_bytes
    assert CATALOG.read_bytes() == catalog_bytes
    assert EXTRAS.read_bytes() == extras_bytes
    assert CLEAN.read_bytes() == clean_bytes


def test_cli_rejects_live_and_bad_catalogs(tmp_path: Path) -> None:
    refused = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "ma_only_titles.py"), "--catalog", "https://example.invalid/catalog.json"],
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
    listed.write_text(
        json.dumps([{"ma": "A01", "titleEn": "A01", "titleVn": "Áo len puppy", "priceUsd": 27}]),
        encoding="utf-8",
    )
    raw = listed.read_text(encoding="utf-8")
    assert main(["--catalog", str(listed)]) == 1
    assert listed.read_text(encoding="utf-8") == raw


def test_script_does_not_write_or_edit_sibling_checks() -> None:
    text = (ROOT / "scripts" / "ma_only_titles.py").read_text(encoding="utf-8")
    assert ".write_text" not in text
    assert "urlopen" not in text
    assert "requests" not in text
    assert "blank_titles" not in text
    assert "title_overlap" not in text
    assert "suggestedTitle" not in text
