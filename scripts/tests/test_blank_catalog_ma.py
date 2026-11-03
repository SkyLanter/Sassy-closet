"""Blank catalog mãs from fixtures. Rows stay as stored. No mã is assigned."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from blank_catalog_ma import CatalogRow, flag_blank_catalog_mas, load_catalog, main, report_json
from held_policy import load_held_policy

ROOT = Path(__file__).resolve().parents[2]
FIXTURES = Path(__file__).resolve().parent / "fixtures"
GAPS = FIXTURES / "blank_catalog_ma.json"
CLEAN = FIXTURES / "blank_catalog_ma_clean.json"
HELD = ROOT / "data" / "held.json"
CATALOG = ROOT / "sassy-closet-shop" / "data" / "products.json"
EXTRAS = ROOT / "sassy-closet-shop" / "data" / "intake-extras.json"
HELD_CODES = frozenset(load_held_policy().held)

EXPECTED = [
    (1, "missing", ""),
    (2, "null", "null"),
    (3, "blank", ""),
    (4, "blank", "   "),
    (5, "not_a_string", "0"),
]


def test_gap_fixture_flags_blank_mas_and_leaves_rows() -> None:
    original = GAPS.read_text(encoding="utf-8")
    rows = load_catalog(GAPS)
    before = [(row.index, row.ma, row.ma_set, row.price_usd, row.price_set) for row in rows]
    flags = flag_blank_catalog_mas(rows)
    assert [(row.index, row.ma, row.ma_set, row.price_usd, row.price_set) for row in rows] == before
    assert GAPS.read_text(encoding="utf-8") == original
    assert len(rows) == 10
    found = [(flag.index, flag.reason, flag.stored) for flag in flags]
    assert found == EXPECTED
    assert rows[0].ma == "S06"
    assert rows[0].price_usd == 25
    assert rows[1].ma_set is False
    assert rows[1].ma is None
    assert rows[1].price_usd == 25
    assert rows[4].ma == "   "
    assert rows[4].price_usd == 25
    assert rows[5].ma == 0
    assert rows[9].ma == "  s06  "
    assert rows[9].price_usd == 25
    for flag in flags:
        body = flag.as_json()
        assert "ma" not in body
        assert body["held"] is False
        assert body["kind"] == "blank_ma"
        assert body["field"] == "ma"
    report = report_json(rows, flags, HELD_CODES)
    assert report["rows"][0] == {"index": 0, "ma": "S06", "held": False, "priceUsd": 25}
    coded = report["rows"][1]
    assert coded["index"] == 1
    assert "ma" not in coded
    assert coded["held"] is False
    assert coded["priceUsd"] == 25
    spaces = report["rows"][4]
    assert spaces == {"index": 4, "held": False, "priceUsd": 25}
    assert "ma" not in spaces
    number = report["rows"][5]
    assert number == {"index": 5, "held": False}
    assert "ma" not in number
    assert report["rows"][6] == {"index": 6, "ma": "A01", "held": False, "priceUsd": 27}
    assert report["rows"][7] == {"index": 7, "ma": "K06", "held": True, "priceUsd": None}
    assert report["rows"][8] == {"index": 8, "ma": "V05", "held": True, "priceUsd": None}
    assert report["rows"][9] == {"index": 9, "ma": "S06", "held": False, "priceUsd": 25}
    text = json.dumps(report, ensure_ascii=False)
    assert '"s06": "stays $25"' in text
    assert '"heldMas": "stay held"' in text
    assert '"readOnly": true' in text
    assert "suggestedMa" not in text
    assert "nextMa" not in text
    assert "assignedMa" not in text


def test_clean_fixture_has_no_flags_and_s06_stays_25() -> None:
    rows = load_catalog(CLEAN)
    flags = flag_blank_catalog_mas(rows)
    assert flags == []
    assert [(row.ma, row.price_usd) for row in rows] == [("S06", 25), ("A01", 27), ("K06", None)]
    report = report_json(rows, flags, HELD_CODES)
    assert report["flagCount"] == 0
    assert report["rows"][0] == {"index": 0, "ma": "S06", "held": False, "priceUsd": 25}
    assert report["rows"][2] == {"index": 2, "ma": "K06", "held": True, "priceUsd": None}


def test_padded_s06_is_kept_and_blank_price_25_is_not_turned_into_s06() -> None:
    padded = CatalogRow(0, "  s06  ", True, 25, True)
    blank = CatalogRow(1, "   ", True, 25, True)
    missing = CatalogRow(2, None, False, 25, True)
    assert flag_blank_catalog_mas([padded]) == []
    flags = flag_blank_catalog_mas([padded, blank, missing])
    assert [(flag.index, flag.reason, flag.stored) for flag in flags] == [
        (1, "blank", "   "),
        (2, "missing", ""),
    ]
    assert padded.ma == "  s06  "
    assert blank.ma == "   "
    assert missing.ma is None
    assert missing.ma_set is False
    report = report_json([padded, blank, missing], flags, HELD_CODES)
    assert report["rows"][0] == {"index": 0, "ma": "S06", "held": False, "priceUsd": 25}
    assert report["rows"][1] == {"index": 1, "held": False, "priceUsd": 25}
    assert "ma" not in report["rows"][1]
    assert "ma" not in report["rows"][2]


def test_non_string_ma_is_not_coerced() -> None:
    rows = [
        CatalogRow(0, ["S06"], True, 25, True),
        CatalogRow(1, True, True, None, False),
        CatalogRow(2, {"ma": "A01"}, True, 27, True),
    ]
    flags = flag_blank_catalog_mas(rows)
    assert [(flag.index, flag.reason, flag.stored) for flag in flags] == [
        (0, "not_a_string", '["S06"]'),
        (1, "not_a_string", "true"),
        (2, "not_a_string", '{"ma": "A01"}'),
    ]
    report = report_json(rows, flags, HELD_CODES)
    for row in report["rows"]:
        assert "ma" not in row
    assert rows[0].ma == ["S06"]
    assert rows[0].price_usd == 25


def test_other_field_named_like_a_ma_does_not_fill_the_blank() -> None:
    row = CatalogRow(3, None, False, 25, True)
    flags = flag_blank_catalog_mas([row])
    assert flags[0].reason == "missing"
    assert flags[0].stored == ""
    assert "ma" not in flags[0].as_json()
    assert row.ma is None


def test_cli_reports_fixture_and_does_not_write(tmp_path: Path) -> None:
    held_bytes = HELD.read_bytes()
    catalog_bytes = CATALOG.read_bytes()
    extras_bytes = EXTRAS.read_bytes()
    gaps_bytes = GAPS.read_bytes()
    clean_bytes = CLEAN.read_bytes()
    gaps = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "blank_catalog_ma.py"), "--catalog", str(GAPS)],
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
    found = [(flag["index"], flag["reason"], flag["stored"], flag["held"]) for flag in report["flags"]]
    assert found == [(index, reason, stored, False) for index, reason, stored in EXPECTED]
    assert all("ma" not in flag for flag in report["flags"])
    assert report["rows"][0] == {"index": 0, "ma": "S06", "held": False, "priceUsd": 25}
    assert "ma" not in report["rows"][1]
    assert report["rows"][1]["priceUsd"] == 25
    assert report["rows"][7]["ma"] == "K06"
    assert report["rows"][7]["held"] is True
    assert report["rows"][8]["held"] is True
    assert report["rows"][9] == {"index": 9, "ma": "S06", "held": False, "priceUsd": 25}
    assert "suggestedMa" not in gaps.stdout
    assert list(tmp_path.iterdir()) == []
    assert HELD.read_bytes() == held_bytes
    assert CATALOG.read_bytes() == catalog_bytes
    assert EXTRAS.read_bytes() == extras_bytes
    assert GAPS.read_bytes() == gaps_bytes
    assert "K06" in HELD.read_text(encoding="utf-8")
    assert "V05" in HELD.read_text(encoding="utf-8")

    clean = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "blank_catalog_ma.py"), "--catalog", str(CLEAN)],
        cwd=tmp_path,
        check=False,
        capture_output=True,
        text=True,
    )
    assert clean.returncode == 0, clean.stderr
    clean_report = json.loads(clean.stdout)
    assert clean_report["flagCount"] == 0
    assert clean_report["rows"][0] == {"index": 0, "ma": "S06", "held": False, "priceUsd": 25}
    assert clean_report["rows"][2]["held"] is True
    assert HELD.read_bytes() == held_bytes
    assert CATALOG.read_bytes() == catalog_bytes
    assert EXTRAS.read_bytes() == extras_bytes
    assert CLEAN.read_bytes() == clean_bytes


def test_cli_rejects_live_and_bad_catalogs(tmp_path: Path) -> None:
    refused = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "blank_catalog_ma.py"), "--catalog", "https://example.invalid/catalog.json"],
        cwd=tmp_path,
        check=False,
        capture_output=True,
        text=True,
    )
    assert refused.returncode == 2
    assert "Catalog fixtures only." in refused.stderr
    assert list(tmp_path.iterdir()) == []

    held_refused = main(["--catalog", str(CLEAN), "--held", "http://example.invalid/held.json"])
    assert held_refused == 2

    missing = main(["--catalog", str(tmp_path / "missing.json")])
    assert missing == 2
    broken = tmp_path / "broken.json"
    broken.write_text("{", encoding="utf-8")
    assert main(["--catalog", str(broken)]) == 2
    assert broken.read_text(encoding="utf-8") == "{"
    listed = tmp_path / "rows.json"
    listed.write_text(
        json.dumps([{"priceUsd": 25}, {"ma": "S06", "priceUsd": 25}]),
        encoding="utf-8",
    )
    raw = listed.read_text(encoding="utf-8")
    assert main(["--catalog", str(listed)]) == 1
    assert listed.read_text(encoding="utf-8") == raw
    not_object = tmp_path / "bad-row.json"
    not_object.write_text(json.dumps({"products": ["S06"]}), encoding="utf-8")
    assert main(["--catalog", str(not_object)]) == 2
    assert not_object.read_text(encoding="utf-8") == json.dumps({"products": ["S06"]})


def test_script_does_not_write_or_assign_a_ma() -> None:
    text = (ROOT / "scripts" / "blank_catalog_ma.py").read_text(encoding="utf-8")
    assert ".write_text" not in text
    assert ".write_bytes" not in text
    assert "urlopen" not in text
    assert "requests" not in text
    assert "nextMa" not in text
    assert "photo_src_paths" not in text
    assert "suggestedMa" not in text
