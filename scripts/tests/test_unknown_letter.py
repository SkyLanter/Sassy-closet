"""Unknown-letter flags from fixtures. Mãs, prices, and held.json stay put."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from unknown_letter import (
    KNOWN_LETTERS,
    FixtureMa,
    flag_unknown_letters,
    load_fixture,
    ma_letter,
    main,
)

ROOT = Path(__file__).resolve().parents[2]
FIXTURE = Path(__file__).resolve().parent / "fixtures" / "unknown_letter.json"
HELD = ROOT / "data" / "held.json"
PRODUCTS = ROOT / "sassy-closet-shop" / "data" / "products.json"
MINT = ROOT / "sassy-closet" / "lib" / "mint.ts"
HELD_BYTES = HELD.read_bytes()
PRODUCTS_BYTES = PRODUCTS.read_bytes()
MINT_BYTES = MINT.read_bytes()
FIXTURE_BYTES = FIXTURE.read_bytes()
OUTSIDE = tuple("CEFILMNRTUWXYZ")


def test_known_letters_are_the_shop_set() -> None:
    assert KNOWN_LETTERS == ("A", "B", "D", "G", "H", "J", "K", "O", "P", "Q", "S", "V")
    assert set(KNOWN_LETTERS) == set("AQVDKGBPHJSO")
    assert "Q" in KNOWN_LETTERS
    assert "C" not in KNOWN_LETTERS


def test_fixture_ma_outside_the_known_letters_is_flagged() -> None:
    rows = [
        FixtureMa(f"{letter}{index:02d}", 10 + index) for index, letter in enumerate(OUTSIDE, start=1)
    ]
    flags = flag_unknown_letters(rows)
    assert [flag.letter for flag in flags] == list(OUTSIDE)
    assert [flag.kind for flag in flags] == ["unknown_letter"] * len(OUTSIDE)
    assert [flag.as_json()["kind"] for flag in flags] == ["unknown_letter"] * len(OUTSIDE)
    assert [row.ma for row in rows] == [f"{letter}{index:02d}" for index, letter in enumerate(OUTSIDE, start=1)]
    assert [row.price_usd for row in rows] == [10 + index for index in range(1, len(OUTSIDE) + 1)]
    assert all("priceUsd" not in flag.as_json() for flag in flags)
    assert all("rename" not in flag.as_json() for flag in flags)


def test_lowercase_unknown_letter_is_flagged_without_renaming() -> None:
    row = FixtureMa(" c01 ", 19)
    flags = flag_unknown_letters([row])
    assert row.ma == " c01 "
    assert row.price_usd == 19
    assert len(flags) == 1
    assert flags[0].as_json() == {"ma": "C01", "letter": "C", "kind": "unknown_letter"}


def test_known_letters_q02_and_s06_stay_quiet() -> None:
    rows = [FixtureMa(f"{letter}01", 10) for letter in KNOWN_LETTERS]
    rows.extend([FixtureMa("Q02", 28), FixtureMa("q02", 28), FixtureMa("S06", 25), FixtureMa("s06", 25)])
    assert flag_unknown_letters(rows) == []
    assert ma_letter("Q02") == "Q"
    assert ma_letter("q02") == "Q"
    q02 = next(row for row in rows if row.ma == "Q02")
    s06 = next(row for row in rows if row.ma == "S06")
    assert q02.ma == "Q02"
    assert q02.price_usd == 28
    assert s06.ma == "S06"
    assert s06.price_usd == 25
    assert rows[-1].ma == "s06"
    assert rows[-1].price_usd == 25


def test_mixed_fixture_flags_only_the_unknown_letter() -> None:
    unknown = FixtureMa("C01", 19)
    queen = FixtureMa("Q02", 28)
    locked = FixtureMa("S06", 25)
    top = FixtureMa("A01", 27)
    rows = [unknown, queen, locked, top]
    flags = flag_unknown_letters(rows)
    assert [flag.ma for flag in flags] == ["C01"]
    assert [row.ma for row in rows] == ["C01", "Q02", "S06", "A01"]
    assert [row.price_usd for row in rows] == [19, 28, 25, 27]


def test_other_shapes_stay_stored() -> None:
    official = FixtureMa("AO001", 10)
    blank = FixtureMa("  ")
    digits = FixtureMa("12")
    rows = [official, blank, digits]
    assert flag_unknown_letters(rows) == []
    assert [row.ma for row in rows] == ["AO001", "  ", "12"]
    assert official.price_usd == 10


def test_flags_sort_by_letter_then_number() -> None:
    rows = [FixtureMa("C10", 1), FixtureMa("W01", 2), FixtureMa("C2", 3)]
    flags = flag_unknown_letters(rows)
    assert [flag.ma for flag in flags] == ["C2", "C10", "W01"]
    assert [row.price_usd for row in rows] == [1, 2, 3]


def test_committed_fixture_flags_c01_and_keeps_q02_and_s06() -> None:
    payload = json.loads(FIXTURE_BYTES.decode("utf-8"))
    rows = load_fixture(payload)
    flags = flag_unknown_letters(rows)
    assert [flag.as_json() for flag in flags] == [
        {"ma": "C01", "letter": "C", "kind": "unknown_letter"}
    ]
    by_ma = {row.ma: row for row in rows}
    assert by_ma["Q02"].ma == "Q02"
    assert ma_letter(by_ma["Q02"].ma) == "Q"
    assert by_ma["S06"].price_usd == 25
    assert by_ma["C01"].price_usd == 19
    assert by_ma["C01"].ma == "C01"
    assert FIXTURE.read_bytes() == FIXTURE_BYTES
    assert HELD.read_bytes() == HELD_BYTES
    assert PRODUCTS.read_bytes() == PRODUCTS_BYTES
    assert MINT.read_bytes() == MINT_BYTES


def test_cli_reports_the_fixture_and_writes_nothing(tmp_path: Path) -> None:
    before_fixture = FIXTURE.read_bytes()
    before_held = HELD.read_bytes()
    before_products = PRODUCTS.read_bytes()
    before_mint = MINT.read_bytes()
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "unknown_letter.py"), "--fixture", str(FIXTURE)],
        cwd=tmp_path,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert result.stderr == ""
    report = json.loads(result.stdout)
    assert report["readOnly"] is True
    assert report["writes"] == []
    assert report["knownLetters"] == list(KNOWN_LETTERS)
    assert report["q02"] == "known"
    assert report["s06PriceUsd"] == 25
    assert report["flags"] == [{"ma": "C01", "letter": "C", "kind": "unknown_letter"}]
    assert "Q02" in report["checked"]
    assert "S06" in report["checked"]
    assert "C01" in report["checked"]
    assert all("priceUsd" not in flag for flag in report["flags"])
    assert "rename" not in result.stdout
    assert "19" not in result.stdout
    assert list(tmp_path.iterdir()) == []
    assert FIXTURE.read_bytes() == before_fixture == FIXTURE_BYTES
    assert HELD.read_bytes() == before_held == HELD_BYTES
    assert PRODUCTS.read_bytes() == before_products == PRODUCTS_BYTES
    assert MINT.read_bytes() == before_mint == MINT_BYTES


def test_cli_rejects_a_bad_fixture(tmp_path: Path) -> None:
    path = tmp_path / "rows.json"
    path.write_text("{", encoding="utf-8")
    before = path.read_bytes()
    assert main(["--fixture", str(path)]) == 2
    assert path.read_bytes() == before
    assert HELD.read_bytes() == HELD_BYTES


def test_cli_rejects_a_price_that_is_not_a_whole_dollar(tmp_path: Path) -> None:
    path = tmp_path / "rows.json"
    raw = json.dumps({"products": [{"ma": "S06", "priceUsd": "25"}]})
    path.write_text(raw, encoding="utf-8")
    assert main(["--fixture", str(path)]) == 2
    assert path.read_text(encoding="utf-8") == raw
    assert HELD.read_bytes() == HELD_BYTES


def test_cli_refuses_live_urls_and_shop_files() -> None:
    before_held = HELD.read_bytes()
    before_products = PRODUCTS.read_bytes()
    before_mint = MINT.read_bytes()
    assert main(["--fixture", "https://example.com/catalog"]) == 2
    assert main(["--fixture", str(HELD)]) == 2
    assert main(["--fixture", str(PRODUCTS)]) == 2
    assert main(["--fixture", str(ROOT / "sassy-closet-shop" / "data")]) == 2
    assert HELD.read_bytes() == before_held == HELD_BYTES
    assert PRODUCTS.read_bytes() == before_products == PRODUCTS_BYTES
    assert MINT.read_bytes() == before_mint == MINT_BYTES


def test_cli_refuses_a_missing_fixture(tmp_path: Path) -> None:
    missing = tmp_path / "missing.json"
    assert main(["--fixture", str(missing)]) == 2
    assert not missing.exists()
    assert HELD.read_bytes() == HELD_BYTES
