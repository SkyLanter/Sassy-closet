"""Every intake mã that is not live and has no approved price must be held."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FIXTURE = ROOT / "data" / "fixtures" / "held-sync-2026-10-20.json"
APPROVED = ROOT / "data" / "approved-held-gia.json"
NEW_HELD = ["S16", "S17", "S18", "S19", "A27", "A28", "A29", "H02", "G01"]


def _fixture():
    return json.loads(FIXTURE.read_text())


def _held():
    return set(json.loads((ROOT / "data" / "held.json").read_text())["heldIncomplete"])


def _approved():
    if not APPROVED.exists():
        return set()
    data = json.loads(APPROVED.read_text())
    if isinstance(data, dict):
        data = data.get("approved", data)
    return {str(m).upper() for m in data}


def missing_from_held(intake, live, held, approved):
    return sorted(m for m in set(intake) - set(live) if m not in held and m not in approved)


def test_snapshot_counts():
    fx = _fixture()
    assert len(set(fx["intakeMas"])) == 83
    assert len(set(fx["liveMas"])) == 62
    assert len(set(fx["intakeMas"]) - set(fx["liveMas"])) == 21


def test_every_not_live_unapproved_intake_ma_is_held():
    fx = _fixture()
    missing = missing_from_held(fx["intakeMas"], fx["liveMas"], _held(), _approved())
    assert missing == [], f"not live, no approved price, missing from data/held.json: {missing}"


def test_no_held_ma_is_live():
    assert sorted(_held() & set(_fixture()["liveMas"])) == []


def test_new_held_mas_present_and_s06_not_held():
    held = _held()
    for ma in NEW_HELD:
        assert ma in held
    assert "S06" not in held


def test_checker_catches_a_gap():
    assert missing_from_held(["A01", "Z99"], ["A01"], set(), set()) == ["Z99"]
    assert missing_from_held(["A01", "Z99"], ["A01"], set(), {"Z99"}) == []
