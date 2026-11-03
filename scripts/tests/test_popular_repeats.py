"""Flag a fixture popular list when the same mã appears twice.

The fixture is not rewritten. Prices stay as written. S06 stays $25.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

import pytest

from popular_repeats import (
    LIVE_FILES,
    S06_USD,
    flag_repeats,
    main,
)

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "popular_repeats.py"
FIXTURE = Path(__file__).resolve().parent / "fixtures" / "popular_repeats.json"
HELD = ROOT / "data" / "held.json"
POPULAR = ROOT / "sassy-closet-shop" / "data" / "popular-order.json"


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


@pytest.fixture(autouse=True)
def _live_files_stay():
    before = {path: path.read_bytes() for path in LIVE_FILES}
    yield
    after = {path: path.read_bytes() for path in LIVE_FILES}
    assert after == before


def test_s06_lock_is_25() -> None:
    assert S06_USD == 25


def test_fixture_flags_a_ma_that_appears_twice() -> None:
    raw = json.loads(FIXTURE.read_text(encoding="utf-8"))
    snapshot = json.dumps(raw)
    report = flag_repeats(raw)
    assert json.dumps(raw) == snapshot
    assert report.rewritten is False
    assert [entry.ma for entry in report.order] == [
        "A05",
        "S06",
        "A07",
        "A05",
        "D05",
        "S06",
    ]
    assert [entry.price_usd for entry in report.order] == [28, 25, 26, 28, 26, 25]
    assert [(flag.ma, flag.kind, flag.count, flag.indexes, flag.prices) for flag in report.flags] == [
        ("A05", "repeated", 2, (0, 3), (28, 28)),
        ("S06", "repeated", 2, (1, 5), (25, 25)),
    ]
    assert raw["scores"]["S06"] == 0.022727
    assert raw["order"][1]["priceUsd"] == 25
    assert raw["order"][5]["priceUsd"] == 25


def test_unique_list_has_no_flags_and_keeps_s06_at_25() -> None:
    payload = {
        "order": [
            {"ma": "A05", "priceUsd": 28},
            {"ma": "S06", "priceUsd": 25},
            {"ma": "A07", "priceUsd": 26},
        ]
    }
    before = json.dumps(payload)
    report = flag_repeats(payload)
    assert json.dumps(payload) == before
    assert report.flags == ()
    assert report.rewritten is False
    assert [(entry.ma, entry.price_usd) for entry in report.order] == [
        ("A05", 28),
        ("S06", 25),
        ("A07", 26),
    ]


def test_same_ma_with_two_prices_is_flagged_and_both_prices_stay() -> None:
    payload = {
        "pieces": [
            {"ma": "A07", "priceUsd": 26},
            {"ma": "D05", "priceUsd": 26},
            {"ma": "A07", "priceUsd": 27},
        ]
    }
    before = json.dumps(payload)
    report = flag_repeats(payload)
    assert json.dumps(payload) == before
    assert [entry.price_usd for entry in report.order] == [26, 26, 27]
    assert len(report.flags) == 1
    flag = report.flags[0]
    assert flag.ma == "A07"
    assert flag.count == 2
    assert flag.prices == (26, 27)
    assert report.rewritten is False


def test_three_copies_count_as_one_repeated_ma() -> None:
    payload = {"order": ["A05", "S06", "A05", "A05"]}
    report = flag_repeats(payload)
    assert [entry.ma for entry in report.order] == ["A05", "S06", "A05", "A05"]
    assert [entry.price_usd for entry in report.order] == [None, None, None, None]
    assert len(report.flags) == 1
    assert report.flags[0].ma == "A05"
    assert report.flags[0].count == 3
    assert report.flags[0].indexes == (0, 2, 3)
    assert payload["order"] == ["A05", "S06", "A05", "A05"]


def test_spelling_is_left_alone_while_the_same_ma_is_flagged() -> None:
    payload = {
        "order": [
            {"ma": " s06 ", "priceUsd": "25"},
            {"ma": "A05", "priceUsd": 28},
            {"ma": "S06", "priceUsd": 25},
        ]
    }
    before = json.dumps(payload)
    report = flag_repeats(payload)
    assert json.dumps(payload) == before
    assert payload["order"][0]["ma"] == " s06 "
    assert payload["order"][0]["priceUsd"] == "25"
    assert [entry.ma for entry in report.order] == ["S06", "A05", "S06"]
    assert [entry.price_usd for entry in report.order] == [25, 28, 25]
    assert report.flags[0].ma == "S06"
    assert report.flags[0].count == 2
    assert report.flags[0].prices == (25, 25)


def test_s06_other_dollar_is_refused_and_not_rewritten() -> None:
    other = {
        "order": [
            {"ma": "S06", "priceUsd": 25},
            {"ma": "A05", "priceUsd": 28},
            {"ma": "S06", "priceUsd": 30},
        ]
    }
    with pytest.raises(ValueError, match=r"S06 stays \$25"):
        flag_repeats(other)
    assert other["order"][0]["priceUsd"] == 25
    assert other["order"][2]["priceUsd"] == 30

    single = {"order": [{"ma": "S06", "priceUsd": 24}]}
    with pytest.raises(ValueError, match=r"S06 stays \$25"):
        flag_repeats(single)
    assert single["order"][0]["priceUsd"] == 24


def test_odd_price_text_stays_unparsed() -> None:
    payload = {"order": [{"ma": "A05", "priceUsd": "028"}]}
    with pytest.raises(ValueError, match="price stays as written"):
        flag_repeats(payload)
    assert payload["order"][0]["priceUsd"] == "028"
    floated = {"pieces": [{"ma": "S06", "priceUsd": 25.0}]}
    with pytest.raises(ValueError, match="price stays as written"):
        flag_repeats(floated)
    assert floated["pieces"][0]["priceUsd"] == 25.0


def test_checker_source_does_not_write() -> None:
    text = SCRIPT.read_text(encoding="utf-8")
    lowered = text.lower()
    assert "write_text" not in text
    assert "write_bytes" not in text
    assert "open(" not in text
    assert "popular_pieces" not in text
    assert "urllib" not in lowered
    assert "import requests" not in lowered
    assert "tesla" not in lowered
    assert "vercel" not in lowered
    assert "meta" not in lowered


def test_cli_flags_the_fixture_and_leaves_files_alone() -> None:
    fixture_before = FIXTURE.read_bytes()
    held_before = HELD.read_bytes()
    popular_before = POPULAR.read_bytes()
    ran = _run(["--fixture", str(FIXTURE)])
    assert ran.returncode == 0, ran.stderr
    payload = json.loads(ran.stdout)
    assert payload["rewritten"] is False
    assert [entry["ma"] for entry in payload["order"]] == [
        "A05",
        "S06",
        "A07",
        "A05",
        "D05",
        "S06",
    ]
    assert [entry["priceUsd"] for entry in payload["order"]] == [28, 25, 26, 28, 26, 25]
    flags = {flag["ma"]: flag for flag in payload["flags"]}
    assert set(flags) == {"A05", "S06"}
    assert flags["A05"]["kind"] == "repeated"
    assert flags["A05"]["count"] == 2
    assert flags["S06"]["prices"] == [25, 25]
    assert FIXTURE.read_bytes() == fixture_before
    assert HELD.read_bytes() == held_before
    assert POPULAR.read_bytes() == popular_before
    assert '"priceUsd": 25' in FIXTURE.read_text(encoding="utf-8")


def test_cli_refuses_live_files_and_a_changed_s06_price(tmp_path: Path) -> None:
    for path in (HELD, POPULAR):
        ran = _run(["--fixture", str(path)])
        assert ran.returncode == 2
        assert ran.stdout == ""
        assert "fixtures only" in ran.stderr

    missing = _run([])
    assert missing.returncode == 2
    assert missing.stdout == ""

    fixture = tmp_path / "popular.json"
    fixture.write_text(
        json.dumps(
            {
                "order": [
                    {"ma": "S06", "priceUsd": 25},
                    {"ma": "S06", "priceUsd": 40},
                ]
            }
        ),
        encoding="utf-8",
    )
    before = fixture.read_bytes()
    refused = _run(["--fixture", str(fixture)])
    assert refused.returncode == 2
    assert refused.stdout == ""
    assert "S06 stays $25" in refused.stderr
    assert fixture.read_bytes() == before


def test_main_prints_the_repeated_ma(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["--fixture", str(FIXTURE)]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["flags"][1] == {
        "ma": "S06",
        "kind": "repeated",
        "count": 2,
        "indexes": [1, 5],
        "prices": [25, 25],
    }
    assert payload["rewritten"] is False


def _run(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
