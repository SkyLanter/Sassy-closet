"""Popular list drops held mãs. Fixtures only. No live ranking or price write."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

import pytest

from popular_pieces import (
    LIVE_FILES,
    S06_USD,
    DroppedMa,
    PopularPiece,
    check_fixture,
    drop_held,
    main,
)

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "popular_pieces.py"
FIXTURE = Path(__file__).with_name("popular-pieces.fixture.json")


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


@pytest.fixture(autouse=True)
def _live_files_stay():
    before = {path: _sha(path) for path in LIVE_FILES}
    yield
    after = {path: _sha(path) for path in LIVE_FILES}
    assert after == before


def test_s06_lock_is_25() -> None:
    assert S06_USD == 25


def test_popular_piece_list_drops_held_mas() -> None:
    raw = json.loads(FIXTURE.read_text(encoding="utf-8"))
    snapshot = json.dumps(raw)
    result = check_fixture(raw)
    assert json.dumps(raw) == snapshot
    assert [piece.ma for piece in result.pieces] == ["A05", "S06", "A07", "D05"]
    assert [piece.price_usd for piece in result.pieces] == [28, 25, 26, 26]
    assert result.pieces[1].available is True
    assert [(item.ma, item.reason) for item in result.dropped] == [
        ("S14", "held"),
        ("A24", "held"),
        ("K02", "held"),
    ]
    assert all(item.ma not in {"S14", "A24", "A25", "S15", "A26", "K02"} for item in result.pieces)


def test_s06_appears_only_when_the_fixture_says_available() -> None:
    held = ["S14"]
    hidden = [
        PopularPiece("A05", 28, True),
        PopularPiece("S06", 25, False),
        PopularPiece("A07", 26, True),
    ]
    omitted = drop_held(hidden, held)
    assert [piece.ma for piece in omitted.pieces] == ["A05", "A07"]
    assert omitted.dropped == (DroppedMa("S06", "unavailable"),)
    assert hidden[1].price_usd == 25

    blank = drop_held([PopularPiece("S06", 25, None), PopularPiece("D05", 26, True)], [])
    assert [piece.ma for piece in blank.pieces] == ["D05"]
    assert blank.dropped[0].reason == "unavailable"

    shown = drop_held([PopularPiece("S06", 25, True)], [])
    assert [piece.ma for piece in shown.pieces] == ["S06"]
    assert shown.pieces[0].price_usd == 25
    assert shown.dropped == ()


def test_s06_price_other_than_25_is_refused_and_not_rewritten() -> None:
    rows = [
        PopularPiece("S14", 40, True),
        PopularPiece("S06", 40, True),
        PopularPiece("A07", 26, True),
    ]
    with pytest.raises(ValueError, match="S06 stays \\$25"):
        drop_held(rows, ["S14"])
    assert [piece.price_usd for piece in rows] == [40, 40, 26]

    unavailable = [PopularPiece("S06", 40, False)]
    with pytest.raises(ValueError, match="S06 stays \\$25"):
        drop_held(unavailable, [])
    assert unavailable[0].price_usd == 40

    held_row = [PopularPiece("S06", 30, True)]
    with pytest.raises(ValueError, match="S06 stays \\$25"):
        drop_held(held_row, ["S06"])
    assert held_row[0].price_usd == 30


def test_available_s06_without_a_price_is_refused() -> None:
    rows = [PopularPiece("S06", None, True), PopularPiece("A05", 28, True)]
    with pytest.raises(ValueError, match="S06 stays \\$25"):
        drop_held(rows, [])
    assert rows[0].price_usd is None
    assert rows[1].price_usd == 28


def test_held_s06_at_25_is_dropped() -> None:
    result = drop_held([PopularPiece("A05", 28, True), PopularPiece("S06", 25, True)], ["S06"])
    assert [piece.ma for piece in result.pieces] == ["A05"]
    assert result.dropped[0].ma == "S06"
    assert result.dropped[0].reason == "held"


def test_order_and_neighbor_prices_stay() -> None:
    pieces = [
        PopularPiece("s14", 41, True),
        PopularPiece("A05", 28, True),
        PopularPiece(" k02 ", 19, False),
        PopularPiece("A07", 26, None),
        PopularPiece("S06", 25, True),
    ]
    result = drop_held(list(pieces), ["s14", "K02", "K02"])
    assert [(piece.ma, piece.price_usd) for piece in pieces] == [
        ("s14", 41),
        ("A05", 28),
        (" k02 ", 19),
        ("A07", 26),
        ("S06", 25),
    ]
    assert [piece.ma for piece in result.pieces] == ["A05", "A07", "S06"]
    assert [piece.price_usd for piece in result.pieces] == [28, 26, 25]
    assert [item.ma for item in result.dropped] == ["S14", "K02"]


def test_fixture_object_does_not_coerce_a_rewritten_price() -> None:
    payload = {
        "held": ["V05"],
        "pieces": [
            {"ma": "A07", "priceUsd": "26", "available": True},
            {"ma": "S06", "priceUsd": "25", "available": True},
            {"ma": "V05", "priceUsd": 27, "available": True},
        ],
    }
    result = check_fixture(payload)
    assert [(piece.ma, piece.price_usd) for piece in result.pieces] == [("A07", 26), ("S06", 25)]
    assert result.dropped[0].ma == "V05"
    with pytest.raises(ValueError, match="price stays as written"):
        check_fixture({"held": [], "pieces": [{"ma": "A07", "priceUsd": "026", "available": True}]})
    with pytest.raises(ValueError, match="price stays as written"):
        check_fixture({"held": [], "pieces": [{"ma": "S06", "priceUsd": 25.0, "available": True}]})


def test_checker_source_does_not_write() -> None:
    text = SCRIPT.read_text(encoding="utf-8")
    assert "write_text" not in text
    assert "write_bytes" not in text
    assert "open(" not in text


def test_cli_fixture_drops_held_and_keeps_s06_at_25() -> None:
    ran = _run(["--fixture", str(FIXTURE)])
    assert ran.returncode == 0, ran.stderr
    payload = json.loads(ran.stdout)
    assert [piece["ma"] for piece in payload["pieces"]] == ["A05", "S06", "A07", "D05"]
    assert [piece["priceUsd"] for piece in payload["pieces"]] == [28, 25, 26, 26]
    assert [item["ma"] for item in payload["dropped"]] == ["S14", "A24", "K02"]
    assert FIXTURE.read_text(encoding="utf-8").count('"priceUsd": 25') == 1


def test_cli_refuses_live_files_and_a_changed_s06_price(tmp_path: Path) -> None:
    for path in LIVE_FILES:
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
                "held": ["S14"],
                "pieces": [
                    {"ma": "S14", "priceUsd": 40, "available": True},
                    {"ma": "S06", "priceUsd": 40, "available": True},
                    {"ma": "A07", "priceUsd": 26, "available": True},
                ],
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


def test_main_prints_the_fixture_list(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["--fixture", str(FIXTURE)]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["pieces"][1] == {"ma": "S06", "priceUsd": 25, "available": True}


def _run(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
