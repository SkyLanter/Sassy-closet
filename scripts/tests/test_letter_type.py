"""Letter and type flags from fixtures. Mãs, prices, and held.json stay put."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from letter_type import CatalogRow, flag_letter_type, main, type_to_letter

ROOT = Path(__file__).resolve().parents[2]
HELD = ROOT / "data" / "held.json"
PRODUCTS = ROOT / "sassy-closet-shop" / "data" / "products.json"
HELD_BYTES = HELD.read_bytes()
PRODUCTS_BYTES = PRODUCTS.read_bytes()


def test_dress_and_top_words_resolve_to_their_letters() -> None:
    assert type_to_letter("dress") == "D"
    assert type_to_letter("Dresses") == "D"
    assert type_to_letter("Đầm") == "D"
    assert type_to_letter("Đầm / Dress") == "D"
    assert type_to_letter("top") == "A"
    assert type_to_letter("Tops") == "A"
    assert type_to_letter("Áo") == "A"
    assert type_to_letter("Áo khoác") == "K"
    assert type_to_letter("set") == "S"


def test_dress_under_a_and_top_under_d_are_flagged() -> None:
    dress_under_a = CatalogRow("A18", "dress", 30)
    dress_letter = CatalogRow("a19", "D", 31)
    top_under_d = CatalogRow("D18", "top", 32)
    top_letter = CatalogRow("d19", "A", 33)
    rows = [dress_under_a, dress_letter, top_under_d, top_letter]
    flags = flag_letter_type(rows)
    assert [row.ma for row in rows] == ["A18", "a19", "D18", "d19"]
    assert [row.price_usd for row in rows] == [30, 31, 32, 33]
    assert [flag.as_json() for flag in flags] == [
        {"ma": "A18", "letter": "A", "type": "dress", "typeLetter": "D", "kind": "mismatch"},
        {"ma": "A19", "letter": "A", "type": "D", "typeLetter": "D", "kind": "mismatch"},
        {"ma": "D18", "letter": "D", "type": "top", "typeLetter": "A", "kind": "mismatch"},
        {"ma": "D19", "letter": "D", "type": "A", "typeLetter": "A", "kind": "mismatch"},
    ]
    assert all("priceUsd" not in flag.as_json() for flag in flags)
    assert all("rename" not in flag.as_json() for flag in flags)


def test_matching_types_and_a_blank_type_are_quiet() -> None:
    rows = [
        CatalogRow("A01", "A", 27),
        CatalogRow("A02", "Tops", 23),
        CatalogRow("D05", "Đầm / Dress", 26),
        CatalogRow("K01", "Áo khoác", 40),
        CatalogRow("P02", "thermos", 25),
        CatalogRow("S06", "set", 25),
        CatalogRow("A04", "", 22),
        CatalogRow("A05", "   ", 21),
        CatalogRow("V05", "skirt", 36),
    ]
    assert flag_letter_type(rows) == []
    assert rows[5].ma == "S06"
    assert rows[5].price_usd == 25
    assert rows[2].price_usd == 26
    assert rows[8].ma == "V05"


def test_jacket_word_under_a_top_letter_is_a_mismatch() -> None:
    row = CatalogRow("A07", "Áo khoác", 26)
    flags = flag_letter_type([row])
    assert row.ma == "A07"
    assert row.price_usd == 26
    assert len(flags) == 1
    assert flags[0].letter == "A"
    assert flags[0].type_letter == "K"
    assert flags[0].kind == "mismatch"
    assert flags[0].stored_type == "Áo khoác"


def test_unrecognized_type_is_flagged_without_a_new_letter() -> None:
    row = CatalogRow("A07", "hoodie", 22)
    flags = flag_letter_type([row])
    assert row.ma == "A07"
    assert flags[0].as_json() == {
        "ma": "A07",
        "letter": "A",
        "type": "hoodie",
        "typeLetter": None,
        "kind": "unrecognized",
    }


def test_stored_type_spacing_is_copied() -> None:
    row = CatalogRow("A11", " Dress ", 29)
    flags = flag_letter_type([row])
    assert row.stored_type == " Dress "
    assert flags[0].stored_type == " Dress "
    assert flags[0].type_letter == "D"


def test_official_alphabet_code_is_not_renamed() -> None:
    row = CatalogRow("AO001", "dress", 10)
    assert flag_letter_type([row]) == []
    assert row.ma == "AO001"
    assert row.price_usd == 10


def test_s06_mismatch_keeps_25_and_held_rows_stay() -> None:
    before_held = HELD.read_bytes()
    before_products = PRODUCTS.read_bytes()
    assert before_held == HELD_BYTES
    assert before_products == PRODUCTS_BYTES
    s06 = CatalogRow("S06", "dress", 25)
    held = CatalogRow("K06", "top", 50)
    held_match = CatalogRow("V05", "Váy", 36)
    rows = [s06, held, held_match]
    flags = flag_letter_type(rows)
    assert [row.ma for row in rows] == ["S06", "K06", "V05"]
    assert s06.price_usd == 25
    assert held.price_usd == 50
    assert held_match.price_usd == 36
    assert [(flag.ma, flag.letter, flag.type_letter) for flag in flags] == [
        ("K06", "K", "A"),
        ("S06", "S", "D"),
    ]
    assert HELD.read_bytes() == before_held == HELD_BYTES
    assert PRODUCTS.read_bytes() == before_products == PRODUCTS_BYTES


def test_cli_reports_fixture_and_does_not_write(tmp_path: Path) -> None:
    catalog = {
        "products": [
            {"ma": "A18", "type": "dress", "priceUsd": 30},
            {"ma": "D18", "type": "top", "priceUsd": 32},
            {"ma": "D05", "type": "D", "priceUsd": 26},
            {"ma": "S06", "type": "S", "priceUsd": 25},
            {"ma": "K06", "type": "K", "priceUsd": 50},
        ]
    }
    path = tmp_path / "catalog.json"
    raw = json.dumps(catalog, ensure_ascii=False, indent=2)
    path.write_text(raw, encoding="utf-8")
    before_held = HELD.read_bytes()
    before_products = PRODUCTS.read_bytes()
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "letter_type.py"), "--catalog", str(path)],
        cwd=tmp_path,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert result.stderr == ""
    report = json.loads(result.stdout)
    assert report["readOnly"] is True
    assert report["rows"] == 5
    assert report["flags"] == [
        {"ma": "A18", "letter": "A", "type": "dress", "typeLetter": "D", "kind": "mismatch"},
        {"ma": "D18", "letter": "D", "type": "top", "typeLetter": "A", "kind": "mismatch"},
    ]
    assert "priceUsd" not in result.stdout
    assert "S06" not in result.stdout
    assert path.read_text(encoding="utf-8") == raw
    assert list(tmp_path.iterdir()) == [path]
    assert HELD.read_bytes() == before_held == HELD_BYTES
    assert PRODUCTS.read_bytes() == before_products == PRODUCTS_BYTES


def test_cli_rejects_a_bad_catalog(tmp_path: Path) -> None:
    path = tmp_path / "catalog.json"
    path.write_text("{", encoding="utf-8")
    assert main(["--catalog", str(path)]) == 2
    assert path.read_text(encoding="utf-8") == "{"
    assert HELD.read_bytes() == HELD_BYTES
