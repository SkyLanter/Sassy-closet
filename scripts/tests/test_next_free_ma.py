"""Next free mã per letter, from fixtures. No intake write and no held.json write."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from held_policy import load_held_policy
from next_free_ma import count_fixture, count_next_free, next_code

ROOT = Path(__file__).resolve().parents[2]
FIXTURE = ROOT / "scripts" / "tests" / "fixtures" / "next-free-ma.json"
HELD_PATH = ROOT / "data" / "held.json"
HELD_BYTES = HELD_PATH.read_bytes()


def test_fixture_next_q_is_q02_and_held_numbers_are_skipped() -> None:
    before = FIXTURE.read_bytes()
    report = count_fixture(FIXTURE)
    assert report["next"]["Q"] == "Q02"
    assert report["next"]["S"] == "S17"
    assert report["next"]["K"] == "K07"
    assert report["next"]["A"] == "A27"
    assert report["next"]["V"] == "V06"
    assert report["next"]["D"] == "D06"
    assert report["next"]["P"] == "P06"
    assert "Q02" not in report["held"]
    assert set(report["next"].values()).isdisjoint(report["held"])
    assert report["held"] == [
        "S14",
        "S15",
        "S16",
        "K02",
        "K03",
        "K04",
        "K05",
        "K06",
        "A24",
        "A25",
        "A26",
        "V04",
        "V05",
    ]
    assert report["prices"]["S06"] == "25"
    assert FIXTURE.read_bytes() == before
    assert HELD_PATH.read_bytes() == HELD_BYTES


def test_held_walk_matches_the_shop_counter() -> None:
    assert next_code("Q", ["Q01"], []) == "Q02"
    assert next_code("q", ["q01"], ["s14"]) == "Q02"
    assert next_code("P", ["P01"], ["P02"]) == "P03"
    assert next_code("P", ["P01"], ["P02", "P03"]) == "P04"
    assert next_code("P", ["P01", "P04"], ["P02", "P03"]) == "P05"
    assert next_code("P", ["P01", "P02", "P05"], []) == "P06"
    assert next_code("D", [], []) == "D01"
    assert next_code("D", ["D01", "V01"], []) == "D02"
    assert next_code("A", ["A99"], []) == "A100"


def test_holding_q02_skips_it_without_changing_the_main_fixture() -> None:
    report = count_next_free(["q01"], ["q02", "S14"])
    assert report.next_by_letter["Q"] == "Q03"
    assert report.next_by_letter["S"] == "S01"
    assert report.held == ("Q02", "S14")
    assert count_fixture(FIXTURE)["next"]["Q"] == "Q02"


def test_lists_are_not_mutated_and_s06_other_dollar_is_refused(tmp_path: Path) -> None:
    mas = ["q01", "S06"]
    held = ["s14"]
    prices = {"S06": "25"}
    report = count_next_free(mas, held, prices)
    assert report.next_by_letter["Q"] == "Q02"
    assert report.prices["S06"] == "25"
    assert mas == ["q01", "S06"]
    assert held == ["s14"]
    assert prices == {"S06": "25"}

    payload = json.loads(FIXTURE.read_text(encoding="utf-8"))
    payload["prices"]["S06"] = "26"
    bad = tmp_path / "s06-26.json"
    bad.write_text(json.dumps(payload), encoding="utf-8")
    before = bad.read_bytes()
    try:
        count_fixture(bad)
    except ValueError as error:
        assert str(error) == "S06 stays $25"
    else:
        raise AssertionError("S06 at $26 was accepted")
    assert bad.read_bytes() == before
    assert HELD_PATH.read_bytes() == HELD_BYTES


def test_cli_prints_q02_and_writes_nothing() -> None:
    ran = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "next_free_ma.py"), "--fixture", str(FIXTURE)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert ran.returncode == 0, ran.stderr
    payload = json.loads(ran.stdout)
    assert payload["next"]["Q"] == "Q02"
    assert payload["prices"]["S06"] == "25"
    assert "Q02" not in payload["held"]
    assert HELD_PATH.read_bytes() == HELD_BYTES
    source = (ROOT / "scripts" / "next_free_ma.py").read_text(encoding="utf-8")
    assert "held.json" not in source
    assert "write_text" not in source
    assert "IntakeApp" not in source


def test_real_held_file_stays_held_and_s06_lock_stays_25() -> None:
    payload = json.loads(HELD_BYTES)
    policy = load_held_policy()
    assert payload["heldIncomplete"] == list(policy.held)
    assert "S16" in policy.held
    assert "A27" in policy.held
    assert "G01" in policy.held
    assert payload["neverList"] == []
    assert "Q02" not in payload["heldIncomplete"]
    assert "S06" not in payload["heldIncomplete"]
    lock = (ROOT / "sassy-closet-shop" / "lib" / "admin-ops.ts").read_text(encoding="utf-8")
    assert 'canonicalMaSpelling(ma) === "S06" && input.priceUsd !== 25' in lock
    assert "S06 stays $25." in lock
    assert HELD_PATH.read_bytes() == HELD_BYTES
