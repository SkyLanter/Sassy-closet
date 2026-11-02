"""Unknown size-token flags from fixtures. Stored tokens and the S06 dollar stay put."""

from __future__ import annotations

import io
import json
import subprocess
import sys
from contextlib import redirect_stderr
from pathlib import Path

from size_token import (
    KNOWN_SIZE_TOKENS,
    SizeList,
    SizeTokenFlag,
    flag_unknown_sizes,
    is_known_size_token,
    load_fixture,
    main,
    rows_from_fixture,
    unknown_sizes,
)

ROOT = Path(__file__).resolve().parents[2]
FIXTURE = Path(__file__).resolve().parent / "fixtures" / "size_token.json"
HELD = ROOT / "data" / "held.json"
CATALOG = ROOT / "sassy-closet-shop" / "data" / "products.json"
EXTRAS = ROOT / "sassy-closet-shop" / "data" / "intake-extras.json"
QUIET = {
    "Z02",
    "Z03",
    "Z04",
    "Z05",
    "Z06",
    "S06",
    "Z10",
    "Z15",
    "Z17",
    "Z19",
    "Z20",
    "Z21",
    "Z22",
    "Z23",
    "Z24",
    "Z26",
    "Z27",
}


def test_fixture_flags_an_unknown_token_and_keeps_it() -> None:
    raw = json.loads(FIXTURE.read_text(encoding="utf-8"))
    s06 = next(row for row in raw["catalog"] if row["ma"] == "S06")
    assert s06["priceUsd"] == 25
    assert s06["sizes"] == ["S", "M", "L"]
    assert raw["catalog"][1]["sizes"] == ["S", "M", "L"]
    assert raw["catalog"][2]["size"] == "S M L"
    rows = rows_from_fixture(raw)
    before = [(row.ma, row.source, row.stored, row.parts, row.price_usd) for row in rows]
    flags = flag_unknown_sizes(rows)
    assert [
        (flag.ma, flag.source, flag.kind, flag.stored, flag.token, flag.index) for flag in flags
    ] == [
        ("Z01", "catalog", "unknown_size", "S, 2XL, M", "2XL", 1),
        ("Z07", "catalog", "unknown_size", "XXXL", "XXXL", 0),
        ("Z08", "catalog", "unknown_size", "free 80cm", "free", 0),
        ("Z08", "catalog", "unknown_size", "free 80cm", "80cm", 1),
        ("Z09", "catalog", "unknown_size", "S 84cm", "84cm", 1),
        ("Z11", "catalog", "unknown_size", "2XS", "2XS", 0),
        ("Z12", "catalog", "unknown_size", "3XL, XXS", "3XL", 0),
        ("Z12", "catalog", "unknown_size", "3XL, XXS", "XXS", 1),
        ("Z13", "catalog", "unknown_size", "onesize", "onesize", 0),
        ("Z14", "catalog", "unknown_size", "36.5", "36.5", 0),
        ("Z16", "catalog", "unknown_size", "S, 2XL, L", "2XL", 1),
        ("Z18", "intake", "unknown_size", "均码", "均码", 0),
        ("Z28", "intake", "unknown_size", "2XL", "2XL", 0),
    ]
    assert not any(flag.ma in QUIET for flag in flags)
    assert [row.ma for row in rows if row.ma == "S06"] == ["S06"]
    assert next(row for row in rows if row.ma == "S06").price_usd == 25
    assert next(row for row in rows if row.ma == "Z01").parts == ("S", "2XL", "M")
    assert next(row for row in rows if row.ma == "Z10").parts == ("s", "m", "l")
    assert next(row for row in rows if row.ma == "Z28").parts == ("2XL",)
    assert [(row.ma, row.source, row.stored, row.parts, row.price_usd) for row in rows] == before
    assert raw["catalog"][0]["sizes"] == ["S", "2XL", "M"]
    for flag in flags:
        body = flag.as_json()
        assert body["stored"] == flag.stored
        assert body["token"] == flag.token
        assert flag.token != "XXL"
        assert "suggested" not in body
        assert "corrected" not in body
        assert "priceUsd" not in body
        assert set(body) == {"ma", "source", "kind", "stored", "token", "index"}


def test_s_m_l_and_plain_numbers_stay_quiet() -> None:
    assert KNOWN_SIZE_TOKENS == ("S", "M", "L", "XL", "XXL", "XS")
    rows = [
        SizeList("Z02", "catalog", "S, M, L", ("S", "M", "L")),
        SizeList("Z03", "catalog", "S M L", ("S", "M", "L")),
        SizeList("Z17", "intake", "S M L", ("S M L",)),
        SizeList("Z04", "catalog", "XL, XXL, XS", ("XL", "XXL", "XS")),
        SizeList("Z10", "catalog", "s, m, l", ("s", "m", "l")),
        SizeList("Z15", "catalog", "xxl", ("xxl",)),
        SizeList("Z05", "catalog", "36", ("36",)),
        SizeList("Z06", "catalog", "36, 38", ("36", "38")),
        SizeList("Z26", "catalog", "8, 100", ("8", "100")),
        SizeList("S06", "catalog", "S, M, L", ("S", "M", "L"), 25),
    ]
    assert flag_unknown_sizes(rows) == []
    assert unknown_sizes(("S", "M", "L")) == []
    assert unknown_sizes(("S M L",)) == []
    assert unknown_sizes(("S  M   L",)) == []
    assert unknown_sizes(("XL", "XXL", "XS", "36")) == []
    assert unknown_sizes(("s", "xl", "xxl", "xs")) == []
    assert rows[9].price_usd == 25
    assert rows[9].parts == ("S", "M", "L")
    for token in (*KNOWN_SIZE_TOKENS, "s", "xxl", "36", "40", "8"):
        assert is_known_size_token(token)


def test_outside_token_stays_outside() -> None:
    parts = ("S", "2XL", "M")
    row = SizeList("Z01", "catalog", "S, 2XL, M", parts)
    first = flag_unknown_sizes([row])
    second = flag_unknown_sizes([row])
    assert row.parts is parts
    assert parts[1] == "2XL"
    assert first == second
    assert first == [SizeTokenFlag("Z01", "catalog", "unknown_size", "S, 2XL, M", "2XL", 1)]
    assert unknown_sizes(("2XL",)) == ["2XL"]
    assert unknown_sizes(("2xl",)) == ["2xl"]
    assert unknown_sizes(("XXL",)) == []
    assert unknown_sizes(("SML",)) == ["SML"]
    assert unknown_sizes(("EU36",)) == ["EU36"]
    assert unknown_sizes(("36.5",)) == ["36.5"]
    assert unknown_sizes(("84cm",)) == ["84cm"]
    assert unknown_sizes(("2XL", "2XL")) == ["2XL", "2XL"]
    assert is_known_size_token("2XL") is False
    assert is_known_size_token("3XL") is False
    assert is_known_size_token("2XS") is False


def test_flagging_twice_does_not_change_2xl() -> None:
    parts = ("2XL", "XXL")
    row = SizeList("Z14", "catalog", "2XL, XXL", parts)
    flags = flag_unknown_sizes([row])
    again = flag_unknown_sizes([row])
    assert row.parts is parts
    assert flags == again
    assert flags == [SizeTokenFlag("Z14", "catalog", "unknown_size", "2XL, XXL", "2XL", 0)]
    assert "XXL" not in unknown_sizes(parts)


def test_s06_unknown_token_keeps_25_and_2xl() -> None:
    payload = {
        "catalog": [{"ma": "S06", "sizes": ["S", "2XL"], "priceUsd": 25}],
        "intake": [{"ma": "Z17", "size": "S M L"}],
    }
    rows = rows_from_fixture(payload)
    flags = flag_unknown_sizes(rows)
    assert payload["catalog"][0]["sizes"] == ["S", "2XL"]
    assert payload["catalog"][0]["priceUsd"] == 25
    assert rows[0].parts == ("S", "2XL")
    assert rows[0].price_usd == 25
    assert rows[1].parts == ("S", "M", "L")
    assert flags == [SizeTokenFlag("S06", "catalog", "unknown_size", "S, 2XL", "2XL", 1)]
    assert flags[0].token == "2XL"
    assert "priceUsd" not in flags[0].as_json()


def test_letter_case_stays_on_the_token() -> None:
    parts = ("xxl", "2xl", "Xs")
    row = SizeList("Z10", "catalog", "xxl 2xl Xs", parts)
    flags = flag_unknown_sizes([row])
    assert row.parts is parts
    assert flags == [SizeTokenFlag("Z10", "catalog", "unknown_size", "xxl 2xl Xs", "2xl", 1)]
    assert unknown_sizes(("S", "S 84cm")) == ["84cm"]


def test_array_item_with_spaces_stays_a_list() -> None:
    payload = {
        "catalog": [{"ma": "Z30", "sizes": ["S M L"]}],
        "intake": [{"ma": "Z16", "size": "S, 2XL, L"}],
    }
    rows = rows_from_fixture(payload)
    assert rows[0].parts == ("S", "M", "L")
    assert rows[0].stored == "S M L"
    assert rows[1].parts == ("S", "2XL", "L")
    assert rows[1].stored == "S, 2XL, L"
    flags = flag_unknown_sizes(rows)
    assert [flag.ma for flag in flags] == ["Z16"]
    assert flags[0].token == "2XL"
    assert payload["catalog"][0]["sizes"] == ["S M L"]
    assert payload["intake"][0]["size"] == "S, 2XL, L"


def test_same_list_on_two_sources_does_not_merge() -> None:
    rows = [
        SizeList("Z01", "catalog", "S, 2XL", ("S", "2XL")),
        SizeList("Z01", "intake", "S M L", ("S", "M", "L")),
    ]
    flags = flag_unknown_sizes(rows)
    assert flags == [SizeTokenFlag("Z01", "catalog", "unknown_size", "S, 2XL", "2XL", 1)]
    assert rows[1].parts == ("S", "M", "L")


def test_cli_prints_the_fixture_report_and_writes_nothing() -> None:
    held_before = HELD.read_bytes()
    catalog_before = CATALOG.read_bytes()
    extras_before = EXTRAS.read_bytes()
    fixture_before = FIXTURE.read_bytes()
    script = ROOT / "scripts" / "size_token.py"
    result = subprocess.run(
        [sys.executable, str(script), "--fixture", str(FIXTURE)],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    report = json.loads(result.stdout)
    assert report["readOnly"] is True
    flags = report["flags"]
    assert any(flag["stored"] == "S, 2XL, M" and flag["token"] == "2XL" and flag["index"] == 1 for flag in flags)
    assert any(flag["ma"] == "Z28" and flag["token"] == "2XL" and flag["stored"] == "2XL" for flag in flags)
    assert any(flag["token"] == "均码" and flag["stored"] == "均码" for flag in flags)
    assert all(flag["token"] != "XXL" for flag in flags)
    assert all(flag["ma"] != "S06" for flag in flags)
    assert all("priceUsd" not in flag for flag in flags)
    assert all("suggested" not in flag and "corrected" not in flag for flag in flags)
    assert "25" not in result.stdout
    loaded = load_fixture(FIXTURE)
    s06 = next(row for row in loaded if row.ma == "S06")
    assert s06.price_usd == 25
    assert s06.parts == ("S", "M", "L")
    assert HELD.read_bytes() == held_before
    assert CATALOG.read_bytes() == catalog_before
    assert EXTRAS.read_bytes() == extras_before
    assert FIXTURE.read_bytes() == fixture_before


def test_missing_fixture_does_not_open_the_live_catalog() -> None:
    held_before = HELD.read_bytes()
    catalog_before = CATALOG.read_bytes()
    extras_before = EXTRAS.read_bytes()
    code, err = _run_main([])
    assert code == 2
    assert "Pass --fixture" in err
    assert HELD.read_bytes() == held_before
    assert CATALOG.read_bytes() == catalog_before
    assert EXTRAS.read_bytes() == extras_before


def test_held_shop_and_urls_are_refused_and_stay_unchanged() -> None:
    held_before = HELD.read_bytes()
    catalog_before = CATALOG.read_bytes()
    extras_before = EXTRAS.read_bytes()
    script = ROOT / "scripts" / "size_token.py"
    for target in (str(HELD), str(CATALOG), str(EXTRAS), "https://example.test/sizes"):
        result = subprocess.run(
            [sys.executable, str(script), "--fixture", target],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        assert result.returncode == 2
        assert "fixtures only" in result.stderr
    assert HELD.read_bytes() == held_before
    assert CATALOG.read_bytes() == catalog_before
    assert EXTRAS.read_bytes() == extras_before


def test_bad_fixture_is_rejected(tmp_path: Path) -> None:
    broken = tmp_path / "broken.json"
    broken.write_text("{", encoding="utf-8")
    code, err = _run_main(["--fixture", str(broken)])
    assert code == 2
    assert err
    assert broken.read_text(encoding="utf-8") == "{"
    both = tmp_path / "both.json"
    both.write_text(
        json.dumps({"catalog": [{"ma": "Z01", "size": "2XL", "sizes": ["2XL"]}], "intake": []}),
        encoding="utf-8",
    )
    code, err = _run_main(["--fixture", str(both)])
    assert code == 2
    assert "both size and sizes" in err
    priced = tmp_path / "priced.json"
    priced.write_text(
        json.dumps({"catalog": [{"ma": "S06", "sizes": ["S"], "priceUsd": "25"}], "intake": []}),
        encoding="utf-8",
    )
    code, err = _run_main(["--fixture", str(priced)])
    assert code == 2
    assert "whole dollar" in err
    assert json.loads(priced.read_text(encoding="utf-8"))["catalog"][0]["priceUsd"] == "25"
    missing = tmp_path / "missing.json"
    code, err = _run_main(["--fixture", str(missing)])
    assert code == 2
    assert err
    assert not missing.exists()


def test_checker_does_not_rewrite_a_size_or_name_a_deploy() -> None:
    text = (ROOT / "scripts" / "size_token.py").read_text(encoding="utf-8")
    lowered = text.lower()
    for banned in (
        "vercel",
        "tesla",
        "urllib",
        "requests",
        "write_text",
        "size_gap",
        "size_repeat",
        "suggested",
        "corrected",
        "replacement",
    ):
        assert banned not in lowered
    assert "unknown_size" in text
    assert "2XL" in text
    assert KNOWN_SIZE_TOKENS == ("S", "M", "L", "XL", "XXL", "XS")


def test_s06_dollar_lock_stays_25() -> None:
    assert "S06_LOCK_USD = 25" in (ROOT / "scripts" / "autolist.py").read_text(encoding="utf-8")
    assert "S06_LOCK = 25" in (ROOT / "scripts" / "pickup.py").read_text(encoding="utf-8")
    shop = (ROOT / "sassy-closet" / "lib" / "shop-catalog.ts").read_text(encoding="utf-8")
    admin = (ROOT / "sassy-closet-shop" / "lib" / "admin-ops.ts").read_text(encoding="utf-8")
    assert 'error: "S06 stays $25."' in shop
    assert 'error: "S06 stays $25."' in admin
    extras = json.loads(EXTRAS.read_text(encoding="utf-8"))
    s06 = next(row for row in extras["products"] if row["ma"] == "S06")
    assert s06["sizes"] == ["S", "M", "L"]


def _run_main(argv: list[str]) -> tuple[int, str]:
    err = io.StringIO()
    with redirect_stderr(err):
        code = main(argv)
    return code, err.getvalue()
