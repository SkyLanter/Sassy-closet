"""Popular mãs missing from a catalog fixture. No live ranking or price write."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

import pytest

from popular_missing import (
    LIVE_FILES,
    S06_USD,
    MissingFlag,
    Piece,
    flag_popular_missing,
    load_catalog,
    load_popular,
    main,
)

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "popular_missing.py"
FIXTURES = Path(__file__).resolve().parent / "fixtures"
POPULAR = FIXTURES / "popular_missing_popular.json"
CATALOG = FIXTURES / "popular_missing_catalog.json"
CLEAN_POPULAR = FIXTURES / "popular_missing_clean_popular.json"
CLEAN_CATALOG = FIXTURES / "popular_missing_clean_catalog.json"


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


def test_absent_popular_ma_is_flagged_and_not_added() -> None:
    popular_text = POPULAR.read_text(encoding="utf-8")
    catalog_text = CATALOG.read_text(encoding="utf-8")
    popular = load_popular(POPULAR)
    catalog = load_catalog(CATALOG)
    report = flag_popular_missing(popular, catalog)
    assert [piece.ma for piece in report.popular] == ["S06", "Z09", "A07"]
    assert [piece.price_usd for piece in report.popular] == [25, 18, 26]
    assert [piece.ma for piece in report.catalog] == ["S06", "A07"]
    assert [piece.price_usd for piece in report.catalog] == [25, 26]
    assert report.flags == (MissingFlag("Z09", 18),)
    assert all(flag.ma != "S06" for flag in report.flags)
    assert "Z09" not in {piece.ma for piece in report.catalog}
    assert POPULAR.read_text(encoding="utf-8") == popular_text
    assert CATALOG.read_text(encoding="utf-8") == catalog_text
    body = report.as_json()
    assert body["readOnly"] is True
    assert body["s06"] == "stays $25"
    assert body["flagCount"] == 1
    assert body["flags"] == [{"ma": "Z09", "kind": "absent_from_catalog", "priceUsd": 18}]
    assert body["catalog"] == [
        {"ma": "S06", "priceUsd": 25},
        {"ma": "A07", "priceUsd": 26},
    ]
    assert "added" not in body
    assert "corrected" not in json.dumps(body)


def test_s06_in_both_fixtures_at_25_is_clean() -> None:
    popular = load_popular(CLEAN_POPULAR)
    catalog = load_catalog(CLEAN_CATALOG)
    before_popular = [(piece.ma, piece.price_usd) for piece in popular]
    before_catalog = [(piece.ma, piece.price_usd) for piece in catalog]
    report = flag_popular_missing(popular, catalog)
    assert report.flags == ()
    assert [(piece.ma, piece.price_usd) for piece in popular] == before_popular
    assert [(piece.ma, piece.price_usd) for piece in catalog] == before_catalog
    assert report.popular[0] == Piece("S06", 25)
    assert report.catalog[0] == Piece("S06", 25)
    assert [piece.price_usd for piece in report.catalog] == [25, 26, 26]
    body = report.as_json()
    assert body["flagCount"] == 0
    assert body["flags"] == []
    assert body["popular"][0] == {"ma": "S06", "priceUsd": 25}
    assert body["catalog"][0] == {"ma": "S06", "priceUsd": 25}


def test_absent_s06_is_flagged_at_25_and_not_added() -> None:
    popular = [Piece("S06", 25), Piece("A07", 26)]
    catalog = [Piece("A07", 26)]
    report = flag_popular_missing(popular, catalog)
    assert report.flags == (MissingFlag("S06", 25),)
    assert [piece.ma for piece in report.catalog] == ["A07"]
    assert catalog[0].price_usd == 26
    assert popular[0].price_usd == 25
    assert report.catalog[0].price_usd == 26


def test_price_differences_are_not_rewritten() -> None:
    popular = [Piece("A07", 26), Piece("S06", 25)]
    catalog = [Piece("A07", 30), Piece("S06", 25)]
    report = flag_popular_missing(popular, catalog)
    assert report.flags == ()
    assert [piece.price_usd for piece in popular] == [26, 25]
    assert [piece.price_usd for piece in catalog] == [30, 25]
    assert report.popular[0].price_usd == 26
    assert report.catalog[0].price_usd == 30


def test_s06_price_other_than_25_is_refused_and_not_rewritten() -> None:
    popular = [Piece("S06", 40), Piece("Z09", 18)]
    catalog = [Piece("A07", 26)]
    with pytest.raises(ValueError, match="S06 stays \\$25"):
        flag_popular_missing(popular, catalog)
    assert [piece.price_usd for piece in popular] == [40, 18]
    assert [piece.price_usd for piece in catalog] == [26]

    priced = [Piece("S06", 30)]
    locked = [Piece("S06", 25)]
    with pytest.raises(ValueError, match="S06 stays \\$25"):
        flag_popular_missing(locked, priced)
    assert locked[0].price_usd == 25
    assert priced[0].price_usd == 30

    blank = [Piece("S06", None)]
    with pytest.raises(ValueError, match="S06 stays \\$25"):
        flag_popular_missing(blank, locked)
    assert blank[0].price_usd is None
    assert locked[0].price_usd == 25


def test_duplicate_popular_ma_is_flagged_once() -> None:
    popular = [Piece(" z09 ", 18), Piece("Z09", 19), Piece("S06", 25)]
    catalog = [Piece("s06", 25)]
    report = flag_popular_missing(popular, catalog)
    assert [piece.ma for piece in popular] == [" z09 ", "Z09", "S06"]
    assert [piece.price_usd for piece in popular] == [18, 19, 25]
    assert report.flags == (MissingFlag("Z09", 18),)
    assert report.popular[2].price_usd == 25
    assert report.catalog == (Piece("S06", 25),)


def test_checker_source_does_not_write() -> None:
    text = SCRIPT.read_text(encoding="utf-8")
    assert "write_text" not in text
    assert "write_bytes" not in text
    assert "open(" not in text
    assert "urlopen" not in text
    assert "requests" not in text
    assert "held.json" in text
    assert "popular-order.json" in text


def test_cli_flags_the_missing_ma_and_keeps_s06(tmp_path: Path) -> None:
    before = {path: path.read_bytes() for path in LIVE_FILES}
    popular_bytes = POPULAR.read_bytes()
    catalog_bytes = CATALOG.read_bytes()
    ran = _run(["--popular", str(POPULAR), "--catalog", str(CATALOG)], tmp_path)
    assert ran.returncode == 1, ran.stderr
    assert ran.stderr == ""
    payload = json.loads(ran.stdout)
    assert payload["readOnly"] is True
    assert payload["s06"] == "stays $25"
    assert payload["flagCount"] == 1
    assert payload["flags"] == [{"ma": "Z09", "kind": "absent_from_catalog", "priceUsd": 18}]
    assert [row["ma"] for row in payload["catalog"]] == ["S06", "A07"]
    assert payload["catalog"][0]["priceUsd"] == 25
    assert payload["popular"][0] == {"ma": "S06", "priceUsd": 25}
    assert "Z09" not in {row["ma"] for row in payload["catalog"]}
    assert "added" not in payload
    assert list(tmp_path.iterdir()) == []
    assert {path: path.read_bytes() for path in LIVE_FILES} == before
    assert POPULAR.read_bytes() == popular_bytes
    assert CATALOG.read_bytes() == catalog_bytes
    assert "Z09" not in (ROOT / "data" / "held.json").read_text(encoding="utf-8")
    assert "Z09" not in (ROOT / "sassy-closet-shop" / "data" / "popular-order.json").read_text(encoding="utf-8")


def test_cli_clean_fixture_exits_zero(tmp_path: Path) -> None:
    ran = _run(
        ["--popular", str(CLEAN_POPULAR), "--catalog", str(CLEAN_CATALOG)],
        tmp_path,
    )
    assert ran.returncode == 0, ran.stderr
    payload = json.loads(ran.stdout)
    assert payload["flagCount"] == 0
    assert payload["flags"] == []
    assert payload["popular"][0] == {"ma": "S06", "priceUsd": 25}
    assert payload["catalog"][0] == {"ma": "S06", "priceUsd": 25}
    assert [row["priceUsd"] for row in payload["catalog"]] == [25, 26, 26]
    assert list(tmp_path.iterdir()) == []


def test_cli_refuses_live_files_and_a_changed_s06_price(tmp_path: Path) -> None:
    before = {path: path.read_bytes() for path in LIVE_FILES}
    for path in LIVE_FILES:
        refused_popular = _run(["--popular", str(path), "--catalog", str(CATALOG)], tmp_path)
        assert refused_popular.returncode == 2
        assert refused_popular.stdout == ""
        assert "fixtures only" in refused_popular.stderr
        refused_catalog = _run(["--popular", str(POPULAR), "--catalog", str(path)], tmp_path)
        assert refused_catalog.returncode == 2
        assert refused_catalog.stdout == ""
        assert "fixtures only" in refused_catalog.stderr
    assert {path: path.read_bytes() for path in LIVE_FILES} == before

    remote = _run(
        ["--popular", "https://example.invalid/popular.json", "--catalog", str(CATALOG)],
        tmp_path,
    )
    assert remote.returncode == 2
    assert remote.stdout == ""
    assert "fixtures only" in remote.stderr

    missing = _run(["--popular", str(POPULAR)], tmp_path)
    assert missing.returncode == 2
    assert missing.stdout == ""

    popular = tmp_path / "popular.json"
    catalog = tmp_path / "catalog.json"
    popular.write_text(
        json.dumps({"pieces": [{"ma": "S06", "priceUsd": 40}, {"ma": "Z09", "priceUsd": 18}]}),
        encoding="utf-8",
    )
    catalog.write_text(
        json.dumps({"products": [{"ma": "S06", "priceUsd": 25}]}),
        encoding="utf-8",
    )
    popular_before = popular.read_bytes()
    catalog_before = catalog.read_bytes()
    refused = _run(["--popular", str(popular), "--catalog", str(catalog)], tmp_path)
    assert refused.returncode == 2
    assert refused.stdout == ""
    assert "S06 stays $25" in refused.stderr
    assert popular.read_bytes() == popular_before
    assert catalog.read_bytes() == catalog_before
    assert {path: path.read_bytes() for path in LIVE_FILES} == before


def test_main_prints_the_missing_flag(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["--popular", str(POPULAR), "--catalog", str(CATALOG)]) == 1
    payload = json.loads(capsys.readouterr().out)
    assert payload["flags"][0]["ma"] == "Z09"
    assert payload["popular"][0] == {"ma": "S06", "priceUsd": 25}
    assert payload["catalog"][0] == {"ma": "S06", "priceUsd": 25}


def _run(args: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        cwd=cwd,
        text=True,
        capture_output=True,
        check=False,
    )
