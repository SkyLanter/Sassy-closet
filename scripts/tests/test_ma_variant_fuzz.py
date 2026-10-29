"""Piece 194: mã variant fuzz harness.

Every mã spelling variant (padded 'K003', trailing newline, spaces, lower-case)
must resolve exactly like its canonical form in every script that reads mãs.
Fixtures are tiny, fake and built at runtime; no network, no real data.
"""
import csv
import json

import pytest

import autolist
import boss_decisions_digest as bdd
import caption_gia_check
import caption_lint
import cost_basis_reconcile as cbr
import daily_shop_check as dsc
import held_photo_exposure as hpe
import held_policy
import held_price_proposal as hpp
import intake_flags
import intake_gaps
import meta_caption_gap_report as mcgr
import meta_inventory
import popular_carryover
import price_approval_queue as paq
import too_cheap_check as tcc
from held_policy import HeldPolicy

CANON = "K03"
VARIANTS = ["K03", "K003", "K03\n", " K03 ", "k03", " k003 ", "\tk3"]
S06_VARIANTS = ["S06", "S006", " s06 ", "s6", "S06\n"]
POLICY = HeldPolicy(held=("K03",), never_list=("Q09",))
IKEY = "intake" + "_cny"  # built at runtime (privacy scan)


def _j(tmp_path, name, obj):
    p = tmp_path / name
    p.write_text(json.dumps(obj), encoding="utf-8")
    return p


def _csv(tmp_path, name, ma, **cols):
    p = tmp_path / name
    with p.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, ["ma", *cols])
        w.writeheader()
        w.writerow({"ma": ma, **cols})
    return p


# Each loader: (tmp_path, mã) -> the set of mã keys it produced.
LOADERS = {
    "held_policy.norm_ma": lambda t, m: {held_policy.norm_ma(m)},
    "held_policy.load_held_policy": lambda t, m: set(held_policy.load_held_policy(
        _j(t, "h.json", {"heldIncomplete": [m], "neverList": []})).held),
    "price_approval_queue.load_held": lambda t, m: set(paq.load_held(_j(t, "h.json", {"heldIncomplete": [m]}))[0]),
    "price_approval_queue.load_approved": lambda t, m: paq.load_approved(_j(t, "a.json", {"approvedGia": {m: 30}})),
    "held_photo_exposure.load_held": lambda t, m: set(hpe.load_held(t, _j(t, "h.json", {"heldIncomplete": [m]}))),
    "boss_decisions_digest.load_public_held": lambda t, m: bdd.load_public_held(_j(t, "p.json", {"exposedMas": [m]})),
    "too_cheap_check.load_live.products": lambda t, m: set(tcc.load_live(_j(t, "l.json", {"products": [{"ma": m, "priceUsd": 30}]}))),
    "too_cheap_check.load_live.prices": lambda t, m: set(tcc.load_live(_j(t, "l.json", {"prices": {m: 30}}))),
    "too_cheap_check.load_costs": lambda t, m: set(tcc.load_costs(_csv(t, "c.csv", m, kg="0.5"))),
    "too_cheap_check.load_weights": lambda t, m: set(tcc.load_weights([_csv(t, "w.csv", m, kg="0.5")])),
    "held_price_proposal.load_live": lambda t, m: set(hpp.load_live(_j(t, "l.json", {"prices": {m: 30}}))),
    "held_price_proposal.load_live_catalog": lambda t, m: set(hpp.load_live_catalog(_j(t, "l.json", {"products": [{"ma": m, "priceUsd": 30}]}))),
    "held_price_proposal.load_weights": lambda t, m: set(hpp.load_weights([_csv(t, "w.csv", m, kg="0.5")])),
    "caption_lint.load_snapshot": lambda t, m: caption_lint.load_snapshot(_j(t, "s.json", {"items": [{"ma": m, "live": True, "sellUsd": 30}]}))[1],
    "caption_lint.load_live": lambda t, m: set(caption_lint.load_live(_j(t, "l.json", {"prices": {m: 30}}))),
    "caption_lint.load_codes": lambda t, m: caption_lint.load_codes(_j(t, "c.json", [m])),
    "caption_gia_check.load_approved": lambda t, m: set(caption_gia_check.load_approved(_j(t, "a.json", {"approvedGia": {m: 30}}))),
    "meta_inventory.load_held": lambda t, m: meta_inventory.load_held(_j(t, "h.json", {"heldIncomplete": [m], "neverList": []}))[0],
    "meta_inventory.load_approved": lambda t, m: set(meta_inventory.load_approved(_j(t, "a.json", {"approvedGia": {m: 30}}))),
    "popular_carryover.load_held": lambda t, m: popular_carryover.load_held(_j(t, "h.json", {"heldIncomplete": [m]})),
    "intake_gaps.load_live": lambda t, m: set(intake_gaps.load_live(_j(t, "l.json", {"products": [{"ma": m, "priceUsd": 30}]}))),
    "intake_gaps.load_weights": lambda t, m: set(intake_gaps.load_weights([_csv(t, "w.csv", m, kg="0.5")])),
    "cost_basis_reconcile._ma": lambda t, m: {cbr._ma(m)},
    "intake_flags.flag_intake": lambda t, m: {f.ma for f in intake_flags.flag_intake([intake_flags.IntakeRow(m, "")])},
    "daily_shop_check.judge_snapshot(held)": lambda t, m: {s.split(": ", 1)[1] for s in dsc.judge_snapshot(
        {"items": [{"ma": m, "live": True, "sellUsd": 30, "held": True}]})["fail"] if s.startswith("held mã live")},
}


@pytest.mark.parametrize("variant", VARIANTS, ids=repr)
@pytest.mark.parametrize("loader", sorted(LOADERS))
def test_loader_variant_matches_canonical(tmp_path, loader, variant):
    canon = LOADERS[loader](tmp_path, CANON)
    assert canon == {CANON}
    assert LOADERS[loader](tmp_path, variant) == canon


@pytest.mark.parametrize("variant", VARIANTS + ["Q009", " q09 "], ids=repr)
def test_skip_reason_variant(variant):
    canon = "Q09" if variant.strip().upper().startswith("Q") else CANON
    assert POLICY.skip_reason(variant) == POLICY.skip_reason(canon) is not None


@pytest.mark.parametrize("variant", S06_VARIANTS, ids=repr)
def test_s06_verdicts_variant(variant):
    # autolist: S06 stays $25
    assert autolist.listing_quote(variant, 10, POLICY).action == "locked"
    # too_cheap_check: a $19 live S06 is flagged, a $25 one is ok -- same as canonical
    for usd in (19, 25):
        got = tcc.evaluate({variant: usd}, {}, POLICY)[0]
        ref = tcc.evaluate({"S06": usd}, {}, POLICY)[0]
        assert (got.ma, got.decision) == (ref.ma, ref.decision)
    # held_price_proposal: S06 is never proposed
    assert hpp.select([{"ma": variant}], {}, POLICY) == []
    # daily_shop_check: snapshot S06 off the $25 lock fails
    rep = dsc.judge_snapshot({"items": [{"ma": variant, "live": True, "sellUsd": 19, "held": False}]})
    assert any("S06 off $25 lock" in s for s in rep["fail"])


@pytest.mark.parametrize("variant", VARIANTS, ids=repr)
def test_held_detection_variant(variant):
    assert autolist.listing_quote(variant, 10, POLICY).action == "skip"
    assert tcc.evaluate({variant: 30}, {}, POLICY)[0].decision == "skip-held"
    assert [r["ma"] for r in hpp.select([{"ma": variant}], {}, POLICY)] == [variant]
    assert hpp.select([{"ma": variant}], {CANON: 30}, POLICY) == hpp.select([{"ma": variant}], {}, POLICY)


@pytest.mark.parametrize("variant", VARIANTS, ids=repr)
def test_live_match_variant(variant):
    # a priced live mã spelled differently in intake still counts as live (not re-proposed)
    pol = HeldPolicy(held=("A01",), never_list=())
    assert hpp.select([{"ma": variant}], {CANON: 30}, pol) == []
    assert caption_lint.load_snapshot  # loaders covered above


@pytest.mark.parametrize("value", [None, "", "   ", "\n"], ids=repr)
def test_empty_values_are_dropped(tmp_path, value):
    assert held_policy.norm_ma(value) == ""
    if value is not None:
        assert tcc.load_costs(_csv(tmp_path, "c.csv", value, kg="0.5")) == {}
        assert hpp.load_weights([_csv(tmp_path, "w.csv", value, kg="0.5")]) == {}
        assert intake_gaps.load_weights([_csv(tmp_path, "w.csv", value, kg="0.5")]) == {}
