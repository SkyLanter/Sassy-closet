"""Shape flags from fixtures. Stored mãs, the S06 dollar, and held.json stay put."""

from __future__ import annotations
import re

import json
import subprocess
import sys
from pathlib import Path

from ma_shape import (
    SHAPE_LABEL,
    SHAPE_RE,
    FixtureMa,
    flag_wrong_shapes,
    is_valid_shape,
    load_fixture,
    main,
    report_json,
    stored_code,
)

ROOT = Path(__file__).resolve().parents[2]
FIXTURE = Path(__file__).resolve().parent / "fixtures" / "ma_shape.json"
HELD = ROOT / "data" / "held.json"
PRODUCTS = ROOT / "sassy-closet-shop" / "data" / "products.json"
SEED = ROOT / "sassy-closet-shop" / "public" / "data" / "taobao_confirm_seed.json"
MINT = ROOT / "sassy-closet" / "lib" / "mint.ts"
HELD_BYTES = HELD.read_bytes()
PRODUCTS_BYTES = PRODUCTS.read_bytes()
SEED_BYTES = SEED.read_bytes()
MINT_BYTES = MINT.read_bytes()
FIXTURE_BYTES = FIXTURE.read_bytes()

WRONG = (
    ("A1", "A1"),
    ("AA01", "AA01"),
    ("a01", "a01"),
)


def _bare_numbers(text: str) -> set[str]:
    """Standalone numbers in output, ignoring anything inside a path-like token (temp dirs carry digits)."""
    words = [w for w in text.split() if "/" not in w and "\\" not in w]
    return set(re.findall(r"(?<![\w.])\d+(?:\.\d+)?(?![\w.])", " ".join(words)))


def test_shape_is_one_uppercase_letter_and_two_digits() -> None:
    assert SHAPE_LABEL == "one letter plus two digits"
    assert SHAPE_RE.pattern == r"^[A-Z][0-9]{2}$"
    valid = [
        FixtureMa(f"{letter}{number:02d}", 10)
        for letter in "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        for number in (0, 2, 6, 99)
    ]
    assert flag_wrong_shapes(valid) == []
    assert is_valid_shape("Q02") is True
    assert is_valid_shape(" S06 ") is True
    assert is_valid_shape("A1") is False
    assert is_valid_shape("AA01") is False
    assert is_valid_shape("a01") is False
    assert is_valid_shape("A001") is False
    assert [row.price_usd for row in valid] == [10] * len(valid)
    assert valid[0].ma == "A00"


def test_a1_aa01_and_a01_are_flagged_and_stay_stored() -> None:
    rows = [
        FixtureMa("A1", 41),
        FixtureMa("AA01", 42),
        FixtureMa("a01", 43),
        FixtureMa(" a01 ", 44),
        FixtureMa("A001", 45),
        FixtureMa("AO001", 46),
    ]
    flags = flag_wrong_shapes(rows)
    assert [flag.as_json() for flag in flags] == [
        {"ma": "A001", "kind": "wrong_shape"},
        {"ma": "A1", "kind": "wrong_shape"},
        {"ma": "AA01", "kind": "wrong_shape"},
        {"ma": "AO001", "kind": "wrong_shape"},
        {"ma": "a01", "kind": "wrong_shape"},
        {"ma": "a01", "kind": "wrong_shape"},
    ]
    assert [row.ma for row in rows] == ["A1", "AA01", "a01", " a01 ", "A001", "AO001"]
    assert [row.price_usd for row in rows] == [41, 42, 43, 44, 45, 46]
    assert all(flag.ma != "A01" for flag in flags)
    assert all("priceUsd" not in flag.as_json() for flag in flags)
    for stored, flagged in WRONG:
        assert stored_code(stored) == flagged
        assert flagged != "A01"


def test_q02_and_s06_stay_valid() -> None:
    rows = [
        FixtureMa("Q02", 28),
        FixtureMa("S06", 25),
        FixtureMa("A01", 27),
        FixtureMa(" q02 ", 28),
        FixtureMa("s06", 25),
    ]
    flags = flag_wrong_shapes(rows)
    assert [flag.ma for flag in flags] == ["q02", "s06"]
    assert rows[0].ma == "Q02"
    assert rows[0].price_usd == 28
    assert rows[1].ma == "S06"
    assert rows[1].price_usd == 25
    assert rows[3].ma == " q02 "
    assert rows[4].ma == "s06"
    assert rows[4].price_usd == 25
    report = report_json(rows, flags)
    assert report["q02"] == "valid"
    assert report["s06PriceUsd"] == 25
    assert report["writes"] == []
    assert "Q02" not in [flag.ma for flag in flags]
    assert "S06" not in [flag.ma for flag in flags]
    lower = [FixtureMa("q02"), FixtureMa("s06", 25)]
    lower_flags = flag_wrong_shapes(lower)
    lower_report = report_json(lower, lower_flags)
    assert lower_report["q02"] == "absent"
    assert lower_report["s06PriceUsd"] is None
    assert lower[1].price_usd == 25


def test_mixed_fixture_flags_only_the_wrong_shapes() -> None:
    short = FixtureMa("A1", 41)
    double = FixtureMa("AA01", 42)
    lower = FixtureMa("a01", 43)
    queen = FixtureMa("Q02", 28)
    locked = FixtureMa("S06", 25)
    top = FixtureMa("A01", 27)
    rows = [short, double, lower, queen, locked, top]
    flags = flag_wrong_shapes(rows)
    assert [flag.ma for flag in flags] == ["A1", "AA01", "a01"]
    assert [flag.kind for flag in flags] == ["wrong_shape"] * 3
    assert [row.ma for row in rows] == ["A1", "AA01", "a01", "Q02", "S06", "A01"]
    assert [row.price_usd for row in rows] == [41, 42, 43, 28, 25, 27]
    report = report_json(rows, flags)
    assert report["checked"] == ["A1", "AA01", "a01", "Q02", "S06", "A01"]
    assert report["q02"] == "valid"
    assert report["s06PriceUsd"] == 25


def test_surrounding_space_on_a_valid_code_stays_stored() -> None:
    queen = FixtureMa(" Q02 ")
    locked = FixtureMa("S06\n", 25)
    rows = [queen, locked, FixtureMa("A1")]
    flags = flag_wrong_shapes(rows)
    assert [flag.ma for flag in flags] == ["A1"]
    assert queen.ma == " Q02 "
    assert locked.ma == "S06\n"
    assert locked.price_usd == 25
    assert report_json(rows, flags)["q02"] == "valid"
    assert report_json(rows, flags)["s06PriceUsd"] == 25


def test_held_codes_already_match_and_stay_on_disk() -> None:
    payload = json.loads(HELD_BYTES.decode("utf-8"))
    codes = [*payload["heldIncomplete"], *payload["neverList"]]
    rows = [FixtureMa(code) for code in codes]
    assert codes
    assert flag_wrong_shapes(rows) == []
    assert HELD.read_bytes() == HELD_BYTES


def test_loader_rejects_a_blank_or_non_object_ma() -> None:
    for payload in (["  "], [{"ma": ""}], [{"ma": 1}], [None], {"products": "A1"}):
        try:
            load_fixture(payload)
        except ValueError:
            continue
        raise AssertionError(f"accepted {payload!r}")
    rows = load_fixture(["Q02", {"ma": "A1", "priceUsd": 41}])
    assert rows[0].ma == "Q02"
    assert rows[0].price_usd is None
    assert rows[1].ma == "A1"
    assert rows[1].price_usd == 41


def test_committed_fixture_flags_a1_aa01_and_a01() -> None:
    payload = json.loads(FIXTURE_BYTES.decode("utf-8"))
    rows = load_fixture(payload)
    flags = flag_wrong_shapes(rows)
    assert [flag.as_json() for flag in flags] == [
        {"ma": "A1", "kind": "wrong_shape"},
        {"ma": "AA01", "kind": "wrong_shape"},
        {"ma": "a01", "kind": "wrong_shape"},
    ]
    by_ma = {row.ma: row for row in rows}
    assert by_ma["Q02"].ma == "Q02"
    assert is_valid_shape(by_ma["Q02"].ma) is True
    assert by_ma["S06"].ma == "S06"
    assert by_ma["S06"].price_usd == 25
    assert by_ma["A01"].ma == "A01"
    assert by_ma["A1"].ma == "A1"
    assert by_ma["A1"].price_usd == 41
    assert by_ma["AA01"].ma == "AA01"
    assert by_ma["a01"].ma == "a01"
    assert by_ma["a01"].price_usd == 43
    report = report_json(rows, flags)
    assert report["q02"] == "valid"
    assert report["s06PriceUsd"] == 25
    assert report["writes"] == []
    assert FIXTURE.read_bytes() == FIXTURE_BYTES
    assert HELD.read_bytes() == HELD_BYTES
    assert PRODUCTS.read_bytes() == PRODUCTS_BYTES
    assert SEED.read_bytes() == SEED_BYTES
    assert MINT.read_bytes() == MINT_BYTES


def test_cli_reports_the_fixture_and_writes_nothing(tmp_path: Path) -> None:
    before_fixture = FIXTURE.read_bytes()
    before_held = HELD.read_bytes()
    before_products = PRODUCTS.read_bytes()
    before_seed = SEED.read_bytes()
    before_mint = MINT.read_bytes()
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "ma_shape.py"), "--fixture", str(FIXTURE)],
        cwd=tmp_path,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert result.stderr == ""
    report = json.loads(result.stdout)
    assert report == {
        "readOnly": True,
        "shape": "one letter plus two digits",
        "rows": 6,
        "checked": ["Q02", "S06", "A01", "A1", "AA01", "a01"],
        "q02": "valid",
        "s06PriceUsd": 25,
        "flags": [
            {"ma": "A1", "kind": "wrong_shape"},
            {"ma": "AA01", "kind": "wrong_shape"},
            {"ma": "a01", "kind": "wrong_shape"},
        ],
        "writes": [],
    }
    assert _bare_numbers(result.stdout).isdisjoint({"41"})
    assert _bare_numbers(result.stdout).isdisjoint({"42"})
    assert _bare_numbers(result.stdout).isdisjoint({"43"})
    assert "rename" not in result.stdout
    assert list(tmp_path.iterdir()) == []
    assert FIXTURE.read_bytes() == before_fixture == FIXTURE_BYTES
    assert HELD.read_bytes() == before_held == HELD_BYTES
    assert PRODUCTS.read_bytes() == before_products == PRODUCTS_BYTES
    assert SEED.read_bytes() == before_seed == SEED_BYTES
    assert MINT.read_bytes() == before_mint == MINT_BYTES


def test_cli_rejects_a_bad_fixture(tmp_path: Path) -> None:
    path = tmp_path / "rows.json"
    path.write_text("{", encoding="utf-8")
    before = path.read_bytes()
    assert main(["--fixture", str(path)]) == 2
    assert path.read_bytes() == before
    assert HELD.read_bytes() == HELD_BYTES
    assert MINT.read_bytes() == MINT_BYTES


def test_cli_rejects_a_price_that_is_not_a_whole_dollar(tmp_path: Path) -> None:
    for price in ("25", 25.0, True, False):
        path = tmp_path / "rows.json"
        raw = json.dumps({"products": [{"ma": "S06", "priceUsd": price}, {"ma": "Q02"}]})
        path.write_text(raw, encoding="utf-8")
        assert main(["--fixture", str(path)]) == 2
        assert path.read_text(encoding="utf-8") == raw
    whole = tmp_path / "whole.json"
    whole.write_text(
        json.dumps({"products": [{"ma": "S06", "priceUsd": 25}, {"ma": "Q02"}]}),
        encoding="utf-8",
    )
    before = whole.read_bytes()
    assert main(["--fixture", str(whole)]) == 0
    assert whole.read_bytes() == before
    assert HELD.read_bytes() == HELD_BYTES


def test_cli_refuses_live_urls_and_shop_files() -> None:
    before_held = HELD.read_bytes()
    before_products = PRODUCTS.read_bytes()
    before_seed = SEED.read_bytes()
    before_mint = MINT.read_bytes()
    assert main(["--fixture", "https://example.com/catalog"]) == 2
    assert main(["--fixture", str(HELD)]) == 2
    assert main(["--fixture", str(PRODUCTS)]) == 2
    assert main(["--fixture", str(SEED)]) == 2
    assert main(["--fixture", str(ROOT / "sassy-closet-shop" / "data")]) == 2
    assert main(["--fixture", str(ROOT / "sassy-closet-shop" / "public" / "data")]) == 2
    assert HELD.read_bytes() == before_held == HELD_BYTES
    assert PRODUCTS.read_bytes() == before_products == PRODUCTS_BYTES
    assert SEED.read_bytes() == before_seed == SEED_BYTES
    assert MINT.read_bytes() == before_mint == MINT_BYTES


def test_cli_refuses_a_missing_fixture(tmp_path: Path) -> None:
    missing = tmp_path / "missing.json"
    assert main(["--fixture", str(missing)]) == 2
    assert not missing.exists()
    assert HELD.read_bytes() == HELD_BYTES
    assert FIXTURE.read_bytes() == FIXTURE_BYTES
