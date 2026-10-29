"""Piece 202: held / never-list verdicts agree with data/held.json everywhere in Python.

Loads the shared vector (also used by the shop and intake TS tests). mã codes only.
"""
import json
from pathlib import Path

import pytest

import autolist
import boss_decisions_digest as bdd
import daily_shop_check as dsc
import export_daily_inputs as edi
import gen_held_never_list_vectors as gen
import held_photo_check as hpc
import held_photo_exposure as hpe
import held_photo_public_watch as hppw
import held_policy
import held_price_proposal as hpp
import host_health_check as hhc
import meta_inventory
import popular_carryover
import price_approval_queue as paq
import too_cheap_check as tcc

ROOT = Path(__file__).resolve().parents[2]
SRC = json.loads((ROOT / "data/held.json").read_text(encoding="utf-8"))
HELD, NEVER = set(SRC["heldIncomplete"]), set(SRC["neverList"])
VEC = json.loads((ROOT / "scripts/testdata/held-never-list-vectors.json").read_text(encoding="utf-8"))
POLICY = held_policy.load_held_policy()
CASES = [(r["ma"], r["status"], v) for r in VEC["rows"] for v in [r["ma"], *r["variants"]]]
ids = [f"{m}:{v!r}" for m, _, v in CASES]


def test_vector_matches_source():
    assert gen.render(gen.build()) == (ROOT / "scripts/testdata/held-never-list-vectors.json").read_text(encoding="utf-8")
    assert set(VEC["heldIncomplete"]) == HELD and set(VEC["neverList"]) == NEVER
    assert {r["ma"] for r in VEC["rows"] if r["status"] == "held"} == HELD


def _status(ma):
    return "held" if ma in HELD else "never-list" if ma in NEVER else "none"


@pytest.mark.parametrize("ma,status,variant", CASES, ids=ids)
def test_python_verdicts(ma, status, variant):
    assert status == _status(ma)
    want = {"held": "held", "never-list": "never-list", "none": None}[status]
    assert POLICY.skip_reason(variant) == want
    q = autolist.listing_quote(variant, 10, POLICY)
    if status != "none":
        assert q.action == "skip"
    elif ma == "S06":
        assert (q.action, q.sell_usd) == ("locked", 25)
    else:
        assert q.action != "skip"
    row = tcc.evaluate({variant: 30}, {}, POLICY)[0]
    assert (row.decision == "skip-held") == (status == "held")
    assert hpp.select([{"ma": variant}], {ma: 30}, POLICY) == ([{"ma": variant}] if status == "held" else [])
    snap = dsc.judge_snapshot({"items": [{"ma": variant, "live": True, "sellUsd": 25, "held": status != "none"}]})
    assert any(s.startswith("held mã live") for s in snap["fail"]) == (status != "none")


# Every Python loader of a held.json reads the same sets, also from a file written with variant spellings.
LOADERS = {
    "held_policy.load_held_policy": lambda p: set(held_policy.load_held_policy(p).held),
    "too_cheap_check.load_held_policy": lambda p: set(tcc.load_held_policy(p).held),
    "price_approval_queue.load_held": lambda p: set(paq.load_held(p)[0]),
    "meta_inventory.load_held": lambda p: meta_inventory.load_held(p)[0],
    "held_photo_exposure.load_held": lambda p: set(hpe.load_held(".", p)),
    "held_photo_check.load_held": lambda p: set(hpc.load_held(p)),
    "held_photo_public_watch.shared_held": lambda p: set(hppw.shared_held(p)[0]),
}
UNION_LOADERS = {  # these intentionally merge held + never-list into one "keep off" set
    "popular_carryover.load_held": popular_carryover.load_held,
    "export_daily_inputs.load_held": edi.load_held,
}


def _variant_file(tmp_path):
    rows = {r["ma"]: r["variants"] for r in VEC["rows"]}
    p = tmp_path / "held.json"
    p.write_text(json.dumps({"heldIncomplete": [rows[m][1] for m in SRC["heldIncomplete"]],
                             "neverList": [rows[m][1] for m in SRC["neverList"]]}), encoding="utf-8")
    return p


@pytest.mark.parametrize("name", sorted(LOADERS))
@pytest.mark.parametrize("which", ["real", "variants"])
def test_held_loaders_agree(tmp_path, name, which):
    p = ROOT / "data/held.json" if which == "real" else _variant_file(tmp_path)
    assert LOADERS[name](p) == HELD


@pytest.mark.parametrize("name", sorted(UNION_LOADERS))
@pytest.mark.parametrize("which", ["real", "variants"])
def test_union_loaders_agree(tmp_path, name, which):
    p = ROOT / "data/held.json" if which == "real" else _variant_file(tmp_path)
    assert set(UNION_LOADERS[name](p)) == HELD | NEVER


def test_default_paths_point_at_the_one_source():
    assert held_policy.default_held_path() == ROOT / "data/held.json"
    assert tcc.held_json_from_ts() == ROOT / "data/held.json"
    assert paq.load_held(None)[1] == "held.json"


def test_hardcoded_python_lists_stay_inside_held():
    # These are subsets on purpose (known-exposed photos / one probe mã). A code that leaves
    # data/held.json must leave them too; one that is not held must never be added.
    assert set(bdd.DEFAULT_PUBLIC_HELD) <= HELD
    assert set(hppw.KNOWN_EXPOSED) <= HELD
    assert set(bdd.DEFAULT_PUBLIC_HELD) == set(hppw.KNOWN_EXPOSED)
    assert hhc.HELD_MA in HELD


def test_s06_status_and_lock():
    assert ("S06" in HELD) == (POLICY.skip_reason("S06") == "held")
    assert "S06" not in NEVER
    assert VEC["s06LockUsd"] == autolist.S06_LOCK_USD == dsc.S06_LOCK == tcc.S06_LOCK_USD == 25
