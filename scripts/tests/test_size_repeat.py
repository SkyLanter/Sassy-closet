"""Repeated-size flags from fixtures. Stored lists and the S06 dollar stay put."""

from __future__ import annotations

import io
import json
import subprocess
import sys
from contextlib import redirect_stderr
from pathlib import Path

from size_repeat import (
    SizeList,
    SizeRepeatFlag,
    flag_repeated_sizes,
    load_fixture,
    main,
    repeated_sizes,
    rows_from_fixture,
)

ROOT = Path(__file__).resolve().parents[2]
FIXTURE = Path(__file__).resolve().parent / "fixtures" / "size_repeat.json"
HELD = ROOT / "data" / "held.json"
CATALOG = ROOT / "sassy-closet-shop" / "data" / "products.json"
EXTRAS = ROOT / "sassy-closet-shop" / "data" / "intake-extras.json"
QUIET = {
    "Z02",
    "Z03",
    "Z04",
    "Z05",
    "Z06",
    "Z08",
    "Z09",
    "S06",
    "Z13",
    "Z14",
    "Z15",
    "Z17",
    "Z19",
    "Z20",
    "Z21",
    "Z22",
    "Z23",
}


def test_fixture_flags_a_repeat_and_keeps_the_stored_list() -> None:
    raw = json.loads(FIXTURE.read_text(encoding="utf-8"))
    s06 = next(row for row in raw["catalog"] if row["ma"] == "S06")
    assert s06["priceUsd"] == 25
    assert s06["sizes"] == ["S", "M", "L"]
    rows = rows_from_fixture(raw)
    before = [(row.ma, row.source, row.stored, row.parts, row.price_usd) for row in rows]
    flags = flag_repeated_sizes(rows)
    assert [
        (flag.ma, flag.source, flag.kind, flag.stored, flag.size, flag.count, flag.indexes) for flag in flags
    ] == [
        ("Z01", "catalog", "repeated_size", "S, M, S", "S", 2, (0, 2)),
        ("Z07", "catalog", "repeated_size", "36, 38, 36", "36", 2, (0, 2)),
        ("Z10", "catalog", "repeated_size", "s, M, S", "s", 2, (0, 2)),
        ("Z11", "catalog", "repeated_size", "S, M, S, M", "S", 2, (0, 2)),
        ("Z11", "catalog", "repeated_size", "S, M, S, M", "M", 2, (1, 3)),
        ("Z12", "catalog", "repeated_size", "S, S, S", "S", 3, (0, 1, 2)),
        ("Z16", "intake", "repeated_size", "S, M, S", "S", 2, (0, 2)),
        ("Z18", "intake", "repeated_size", "S / M / S", "S", 2, (0, 2)),
    ]
    assert not any(flag.ma in QUIET for flag in flags)
    assert [row.ma for row in rows if row.ma == "S06"] == ["S06"]
    assert next(row for row in rows if row.ma == "S06").price_usd == 25
    assert [(row.ma, row.source, row.stored, row.parts, row.price_usd) for row in rows] == before
    assert raw["catalog"][0]["sizes"] == ["S", "M", "S"]
    for flag in flags:
        body = flag.as_json()
        assert body["stored"] == flag.stored
        assert flag.count == len(flag.indexes)
        assert flag.count >= 2
        assert "suggested" not in body
        assert "corrected" not in body
        assert "deduped" not in body
        assert "priceUsd" not in body
        assert set(body) == {"ma", "source", "kind", "stored", "size", "count", "indexes"}


def test_single_size_stays_quiet() -> None:
    rows = [
        SizeList("Z03", "catalog", "M", ("M",)),
        SizeList("Z04", "catalog", "S", ("S",)),
        SizeList("Z05", "catalog", "36", ("36",)),
        SizeList("Z06", "catalog", "36, 38", ("36", "38")),
        SizeList("Z08", "intake", "free 80cm", ("free 80cm",)),
        SizeList("Z09", "catalog", "S 84cm", ("S 84cm",)),
        SizeList("S06", "catalog", "S, M, L", ("S", "M", "L"), 25),
        SizeList("Z15", "catalog", "S, S 84cm", ("S", "S 84cm")),
        SizeList("Z14", "catalog", "2XL, XXL", ("2XL", "XXL")),
        SizeList("Z17", "intake", "M", ("M",)),
        SizeList("Z22", "intake", " ", ()),
    ]
    assert flag_repeated_sizes(rows) == []
    assert repeated_sizes(("M",)) == []
    assert rows[6].price_usd == 25
    assert rows[6].parts == ("S", "M", "L")


def test_flagging_twice_does_not_drop_the_repeat() -> None:
    parts = ("S", "M", "S")
    row = SizeList("Z01", "catalog", "S, M, S", parts)
    first = flag_repeated_sizes([row])
    second = flag_repeated_sizes([row])
    assert row.parts is parts
    assert len(row.parts) == 3
    assert first == second
    assert first == [SizeRepeatFlag("Z01", "catalog", "repeated_size", "S, M, S", "S", 2, (0, 2))]
    assert repeated_sizes(parts) == ["S"]


def test_case_and_space_match_and_both_copies_stay() -> None:
    parts = ("S", " s ", "M")
    row = SizeList("Z10", "catalog", "S,  s , M", parts)
    flags = flag_repeated_sizes([row])
    assert row.parts is parts
    assert flags == [SizeRepeatFlag("Z10", "catalog", "repeated_size", "S,  s , M", "S", 2, (0, 1))]
    assert repeated_sizes(("S", "S 84cm")) == []
    assert repeated_sizes(("M", "S", "M", "S")) == ["M", "S"]


def test_s06_repeat_keeps_25_and_every_copy() -> None:
    payload = {
        "catalog": [{"ma": "S06", "sizes": ["S", "M", "S"], "priceUsd": 25}],
        "intake": [{"ma": "Z17", "size": "M"}],
    }
    rows = rows_from_fixture(payload)
    flags = flag_repeated_sizes(rows)
    assert payload["catalog"][0]["sizes"] == ["S", "M", "S"]
    assert payload["catalog"][0]["priceUsd"] == 25
    assert rows[0].parts == ("S", "M", "S")
    assert rows[0].price_usd == 25
    assert rows[1].parts == ("M",)
    assert flags == [SizeRepeatFlag("S06", "catalog", "repeated_size", "S, M, S", "S", 2, (0, 2))]
    assert "priceUsd" not in flags[0].as_json()


def test_array_items_stay_whole_and_a_comma_string_splits() -> None:
    payload = {
        "catalog": [{"ma": "Z30", "sizes": ["S, M", "S"]}],
        "intake": [{"ma": "Z16", "size": "S, M, S"}],
    }
    rows = rows_from_fixture(payload)
    assert rows[0].parts == ("S, M", "S")
    assert rows[1].parts == ("S", "M", "S")
    assert rows[1].stored == "S, M, S"
    flags = flag_repeated_sizes(rows)
    assert [flag.ma for flag in flags] == ["Z16"]
    assert payload["catalog"][0]["sizes"] == ["S, M", "S"]
    assert payload["intake"][0]["size"] == "S, M, S"


def test_same_list_on_two_sources_does_not_merge() -> None:
    rows = [
        SizeList("Z01", "catalog", "S, M, S", ("S", "M", "S")),
        SizeList("Z01", "intake", "S", ("S",)),
    ]
    flags = flag_repeated_sizes(rows)
    assert flags == [SizeRepeatFlag("Z01", "catalog", "repeated_size", "S, M, S", "S", 2, (0, 2))]
    assert rows[1].parts == ("S",)


def test_cli_prints_the_fixture_report_and_writes_nothing() -> None:
    held_before = HELD.read_bytes()
    catalog_before = CATALOG.read_bytes()
    extras_before = EXTRAS.read_bytes()
    fixture_before = FIXTURE.read_bytes()
    script = ROOT / "scripts" / "size_repeat.py"
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
    assert any(flag["stored"] == "S, M, S" and flag["size"] == "S" and flag["indexes"] == [0, 2] for flag in flags)
    assert any(flag["ma"] == "Z12" and flag["count"] == 3 and flag["stored"] == "S, S, S" for flag in flags)
    assert all(flag["ma"] != "S06" for flag in flags)
    assert all("priceUsd" not in flag for flag in flags)
    assert all("suggested" not in flag and "corrected" not in flag and "deduped" not in flag for flag in flags)
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
    script = ROOT / "scripts" / "size_repeat.py"
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
        json.dumps({"catalog": [{"ma": "Z01", "size": "S", "sizes": ["S", "S"]}], "intake": []}),
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
    text = (ROOT / "scripts" / "size_repeat.py").read_text(encoding="utf-8")
    lowered = text.lower()
    for banned in ("vercel", "tesla", "urllib", "requests", "write_text", "size_gap", "deduped", "corrected"):
        assert banned not in lowered
    assert "repeated_size" in text


def test_s06_dollar_lock_stays_25() -> None:
    assert "S06_LOCK_USD = 25" in (ROOT / "scripts" / "autolist.py").read_text(encoding="utf-8")
    assert "S06_LOCK = 25" in (ROOT / "scripts" / "pickup.py").read_text(encoding="utf-8")
    shop = (ROOT / "sassy-closet" / "lib" / "shop-catalog.ts").read_text(encoding="utf-8")
    admin = (ROOT / "sassy-closet-shop" / "lib" / "admin-ops.ts").read_text(encoding="utf-8")
    assert "S06 stays available at $25." in shop
    assert 'error: "S06 stays $25."' in admin
    extras = json.loads(EXTRAS.read_text(encoding="utf-8"))
    s06 = next(row for row in extras["products"] if row["ma"] == "S06")
    assert s06["sizes"] == ["S", "M", "L"]


def _run_main(argv: list[str]) -> tuple[int, str]:
    err = io.StringIO()
    with redirect_stderr(err):
        code = main(argv)
    return code, err.getvalue()
