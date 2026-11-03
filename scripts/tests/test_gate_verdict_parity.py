"""Piece 204: Python gate verdicts on the shared gate-verdict fixtures (fake mãs only).

The TS apps run the same fixtures in tests/gate-verdict-parity.test.ts.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from autolist import listing_quote
from daily_shop_check import judge_snapshot
from held_policy import load_held_policy
from too_cheap_check import evaluate

ROOT = Path(__file__).resolve().parents[2]
DOC = json.loads((ROOT / "scripts/testdata/gate-verdict-fixtures.json").read_text(encoding="utf-8"))
HELD = json.loads((ROOT / "data/held.json").read_text(encoding="utf-8"))
POLICY = load_held_policy()


def spell(base: str, how: str) -> str:
    L, d = base[0], base[1:]
    short = f"{L}{int(d)}"
    return {
        "canonical": base, "padded": f"{L}0{d}", "spaced": f" {base} ", "lower": base.lower(),
        "short": short, "short-lower": short.lower(), "padded-lower-spaced": f" {L.lower()}0{d} ",
    }[how]


def resolve(fx: dict) -> str | None:
    if "ma" in fx:
        return fx["ma"]
    key, idx = ("heldIncomplete", fx["held_index"]) if "held_index" in fx else ("neverList", fx["never_index"])
    codes = HELD[key]
    return spell(codes[idx], fx["spelling"]) if idx < len(codes) else None


CASES = [pytest.param(fx, id=fx["id"]) for fx in DOC["fixtures"]]


def test_fixture_count():
    assert len(DOC["fixtures"]) >= 60


@pytest.mark.parametrize("fx", CASES)
def test_skip_gate(fx):
    ma = resolve(fx)
    if ma is None:
        pytest.skip("held.json list has no entry at this index")
    want = fx["expect"]["skip"]
    assert POLICY.skip_reason(ma) == want
    action = listing_quote(ma, 10, POLICY).action
    assert (action == "skip") == (want is not None), action


@pytest.mark.parametrize("fx", CASES)
def test_s06_gate(fx):
    ma = resolve(fx)
    if ma is None:
        pytest.skip("held.json list has no entry at this index")
    want = fx["expect"]["s06"]
    sell = fx["sell_usd"]
    rows = evaluate({ma: float(sell)}, {}, POLICY)
    decision = rows[0].decision
    verdict = {"locked": "pass", "lock-drift": "fail"}.get(decision, "n/a")
    assert verdict == want, decision
    snap = judge_snapshot({"items": [{"ma": ma, "live": True, "sellUsd": sell}]})
    s06_fail = any("S06 off" in f for f in snap.get("fail", []))
    assert s06_fail == (want == "fail"), snap
