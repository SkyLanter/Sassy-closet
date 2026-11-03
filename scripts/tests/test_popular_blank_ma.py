"""Flag a fixture popular entry when its mã is blank.

The fixture is not rewritten. A blank mã is not filled in. S06 stays $25.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

import pytest

from popular_blank_ma import (
    LIVE_FILES,
    S06_USD,
    flag_blank_mas,
    main,
)

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "popular_blank_ma.py"
FIXTURE = Path(__file__).resolve().parent / "fixtures" / "popular_blank_ma.json"
CLEAN = Path(__file__).resolve().parent / "fixtures" / "popular_blank_ma_clean.json"
HELD = ROOT / "data" / "held.json"
POPULAR = ROOT / "sassy-closet-shop" / "data" / "popular-order.json"
REPEATS = ROOT / "scripts" / "popular_repeats.py"


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


@pytest.fixture(autouse=True)
def _live_files_stay():
    before = {path: path.read_bytes() for path in LIVE_FILES}
    repeats_before = REPEATS.read_bytes() if REPEATS.exists() else None
    yield
    after = {path: path.read_bytes() for path in LIVE_FILES}
    assert after == before
    repeats_after = REPEATS.read_bytes() if REPEATS.exists() else None
    assert repeats_after == repeats_before


def test_s06_lock_is_25() -> None:
    assert S06_USD == 25


def test_fixture_flags_blank_mas_and_leaves_s06_clean() -> None:
    raw = json.loads(FIXTURE.read_text(encoding="utf-8"))
    snapshot = json.dumps(raw)
    report = flag_blank_mas(raw)
    assert json.dumps(raw) == snapshot
    assert report.rewritten is False
    assert report.filled is False
    assert [(entry.code, entry.price_usd, entry.blank) for entry in report.order] == [
        ("A05", 28, False),
        ("S06", 25, False),
        ("", 30, True),
        ("", 22, True),
        ("", 19, True),
        ("", 21, True),
        ("S06", 25, False),
        ("D05", 26, False),
    ]
    found = [
        (flag.index, flag.kind, flag.reason, flag.ma, flag.stored, flag.price_usd, flag.filled)
        for flag in report.flags
    ]
    assert found == [
        (2, "blank", "blank", "", "", 30, False),
        (3, "blank", "blank", "", "   ", 22, False),
        (4, "blank", "null", "", None, 19, False),
        (5, "blank", "missing", "", "", 21, False),
    ]
    assert raw["order"][1]["ma"] == "S06"
    assert raw["order"][1]["priceUsd"] == 25
    assert raw["order"][2]["ma"] == ""
    assert raw["order"][3]["ma"] == "   "
    assert raw["order"][4]["ma"] is None
    assert "ma" not in raw["order"][5]
    assert raw["order"][6]["ma"] == " s06 "
    assert raw["order"][6]["priceUsd"] == "25"


def test_clean_list_has_no_flags_and_keeps_s06_at_25() -> None:
    raw = json.loads(CLEAN.read_text(encoding="utf-8"))
    snapshot = json.dumps(raw)
    report = flag_blank_mas(raw)
    assert json.dumps(raw) == snapshot
    assert report.flags == ()
    assert report.filled is False
    assert report.rewritten is False
    assert [(entry.code, entry.price_usd, entry.blank) for entry in report.order] == [
        ("A05", 28, False),
        ("S06", 25, False),
        ("A07", 26, False),
        ("D05", 26, False),
    ]
    assert not any(entry.code == "S06" and entry.price_usd != 25 for entry in report.order)


def test_s06_at_25_stays_clean_when_the_ma_is_s06() -> None:
    payload = {
        "order": [
            {"ma": "S06", "priceUsd": 25},
            {"ma": " s06 ", "priceUsd": "25"},
            {"ma": "A05", "priceUsd": 28},
        ]
    }
    before = json.dumps(payload)
    report = flag_blank_mas(payload)
    assert json.dumps(payload) == before
    assert report.flags == ()
    assert report.filled is False
    assert [entry.code for entry in report.order] == ["S06", "S06", "A05"]
    assert [entry.price_usd for entry in report.order] == [25, 25, 28]
    assert payload["order"][0]["ma"] == "S06"
    assert payload["order"][1]["ma"] == " s06 "
    assert payload["order"][1]["priceUsd"] == "25"


def test_blank_ma_is_not_filled_in() -> None:
    payload = {
        "order": [
            {"ma": "S06", "priceUsd": 25},
            {"ma": "", "priceUsd": 25},
            {"ma": "   ", "priceUsd": 25},
            {"ma": None, "priceUsd": 25},
            {"priceUsd": 25},
        ]
    }
    before = json.dumps(payload)
    report = flag_blank_mas(payload)
    assert json.dumps(payload) == before
    assert payload["order"][1]["ma"] == ""
    assert payload["order"][2]["ma"] == "   "
    assert payload["order"][3]["ma"] is None
    assert "ma" not in payload["order"][4]
    assert [entry.code for entry in report.order] == ["S06", "", "", "", ""]
    assert report.order[0].blank is False
    assert report.order[0].price_usd == 25
    assert [flag.ma for flag in report.flags] == ["", "", "", ""]
    assert [flag.filled for flag in report.flags] == [False, False, False, False]
    assert [flag.index for flag in report.flags] == [1, 2, 3, 4]
    assert all(flag.ma != "S06" for flag in report.flags)
    assert report.filled is False
    assert report.as_json()["filled"] is False
    assert "S06" not in [row["ma"] for row in report.as_json()["order"][1:]]


def test_string_list_flags_a_blank_and_keeps_s06() -> None:
    payload = {"pieces": ["A05", "", "S06", "   "]}
    before = json.dumps(payload)
    report = flag_blank_mas(payload)
    assert json.dumps(payload) == before
    assert [entry.code for entry in report.order] == ["A05", "", "S06", ""]
    assert [entry.price_usd for entry in report.order] == [None, None, None, None]
    assert [(flag.index, flag.reason, flag.stored, flag.ma) for flag in report.flags] == [
        (1, "blank", "", ""),
        (3, "blank", "   ", ""),
    ]
    assert payload["pieces"] == ["A05", "", "S06", "   "]


def test_s06_other_dollar_is_refused_and_not_rewritten() -> None:
    other = {
        "order": [
            {"ma": "S06", "priceUsd": 25},
            {"ma": "", "priceUsd": 30},
            {"ma": "S06", "priceUsd": 30},
        ]
    }
    with pytest.raises(ValueError, match=r"S06 stays \$25"):
        flag_blank_mas(other)
    assert other["order"][0]["priceUsd"] == 25
    assert other["order"][1]["ma"] == ""
    assert other["order"][2]["priceUsd"] == 30

    single = {"order": [{"ma": "S06", "priceUsd": 24}]}
    with pytest.raises(ValueError, match=r"S06 stays \$25"):
        flag_blank_mas(single)
    assert single["order"][0]["ma"] == "S06"
    assert single["order"][0]["priceUsd"] == 24


def test_odd_price_text_stays_unparsed() -> None:
    payload = {"order": [{"ma": "", "priceUsd": "030"}]}
    with pytest.raises(ValueError, match="price stays as written"):
        flag_blank_mas(payload)
    assert payload["order"][0]["ma"] == ""
    assert payload["order"][0]["priceUsd"] == "030"
    floated = {"order": [{"ma": "S06", "priceUsd": 25.0}]}
    with pytest.raises(ValueError, match="price stays as written"):
        flag_blank_mas(floated)
    assert floated["order"][0]["priceUsd"] == 25.0
    numbered = {"order": [{"ma": 6, "priceUsd": 25}]}
    with pytest.raises(ValueError, match="mã stays as written"):
        flag_blank_mas(numbered)
    assert numbered["order"][0]["ma"] == 6


def test_checker_source_does_not_write() -> None:
    text = SCRIPT.read_text(encoding="utf-8")
    lowered = text.lower()
    assert "write_text" not in text
    assert "write_bytes" not in text
    assert "open(" not in text
    assert "popular_repeats" not in text
    assert 'or "S06"' not in text
    assert "or 'S06'" not in text
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
    assert ran.returncode == 1, ran.stderr
    assert ran.stderr == ""
    payload = json.loads(ran.stdout)
    assert payload["filled"] is False
    assert payload["rewritten"] is False
    assert [entry["ma"] for entry in payload["order"]] == [
        "A05",
        "S06",
        "",
        "",
        "",
        "",
        "S06",
        "D05",
    ]
    assert [entry["priceUsd"] for entry in payload["order"]] == [28, 25, 30, 22, 19, 21, 25, 26]
    assert [entry["blank"] for entry in payload["order"]] == [
        False,
        False,
        True,
        True,
        True,
        True,
        False,
        False,
    ]
    assert payload["order"][1]["stored"] == "S06"
    assert payload["order"][6]["stored"] == " s06 "
    flags = payload["flags"]
    assert [flag["index"] for flag in flags] == [2, 3, 4, 5]
    assert [flag["ma"] for flag in flags] == ["", "", "", ""]
    assert [flag["filled"] for flag in flags] == [False, False, False, False]
    assert flags[0]["stored"] == ""
    assert flags[1]["stored"] == "   "
    assert flags[2]["stored"] is None
    assert flags[3]["reason"] == "missing"
    assert FIXTURE.read_bytes() == fixture_before
    assert HELD.read_bytes() == held_before
    assert POPULAR.read_bytes() == popular_before
    assert '"ma": "S06"' in FIXTURE.read_text(encoding="utf-8")
    assert '"ma": ""' in FIXTURE.read_text(encoding="utf-8")


def test_cli_clean_fixture_exits_0() -> None:
    before = CLEAN.read_bytes()
    ran = _run(["--fixture", str(CLEAN)])
    assert ran.returncode == 0, ran.stderr
    payload = json.loads(ran.stdout)
    assert payload["flags"] == []
    assert payload["filled"] is False
    assert payload["rewritten"] is False
    s06 = next(entry for entry in payload["order"] if entry["ma"] == "S06")
    assert s06["priceUsd"] == 25
    assert s06["blank"] is False
    assert CLEAN.read_bytes() == before


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
                    {"ma": "", "priceUsd": 40},
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
    assert '"ma": ""' in fixture.read_text(encoding="utf-8")


def test_main_prints_the_blank_ma(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["--fixture", str(FIXTURE)]) == 1
    payload = json.loads(capsys.readouterr().out)
    assert payload["flags"][0] == {
        "index": 2,
        "kind": "blank",
        "reason": "blank",
        "ma": "",
        "stored": "",
        "priceUsd": 30,
        "filled": False,
    }
    assert payload["order"][1]["ma"] == "S06"
    assert payload["order"][1]["priceUsd"] == 25
    assert payload["order"][1]["blank"] is False
    assert payload["filled"] is False
    assert payload["rewritten"] is False


def _run(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
