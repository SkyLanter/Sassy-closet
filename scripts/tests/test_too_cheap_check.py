import json
from decimal import Decimal
from pathlib import Path

import pytest

import too_cheap_check as tc
from held_policy import HeldPolicy

POLICY = HeldPolicy(held=("K03", "V04"), never_list=("Z99",))


def cost(intake="", listed="", kg=""):
    return {"intake_cny": str(intake), "list_cny": str(listed), "kg": str(kg)}


def one(ma, live, c, policy=POLICY, weights=None):
    (row,) = tc.evaluate({ma: live}, {ma: c}, policy, weights)
    return row


def test_landed_formula():
    assert tc.landed_usd(Decimal("67.23"), Decimal("1")) == Decimal("20.52")


@pytest.mark.parametrize("landed,sell", [
    ("16.25", 25),   # 25 * 0.65 = 16.25 exactly: still the 35% tier
    ("16.26", 26),   # just over: next dollar, margin starts sliding
    ("33.75", 45),   # 45 * 0.75 = 33.75: flat 25% starts at $45
    ("37.50", 50),   # above $45 stays 25%
    ("5.00", 10),    # 5/0.65 = 7.7 -> 8 -> under-$10 bump
])
def test_tier_boundaries(landed, sell):
    assert tc.price(Decimal(landed)) == sell


def test_under_target_found_at_intake_yen():
    r = one("A99", 20, cost(intake=100, kg="0.3"))
    assert r.decision == "under" and r.target_usd > 20


def test_ok_and_list_only_kept_separate():
    ok = one("A98", 30, cost(intake=80, listed=82, kg="0.3"))
    lo = one("A97", 25, cost(intake=80, listed=140, kg="0.3"))
    assert ok.decision == "ok"
    assert lo.decision == "list-only" and lo.target_usd <= 25 < lo.list_target_usd
    s = tc.summarize([ok, lo])
    assert s["under_target"] == [] and [r["ma"] for r in s["list_only"]] == ["A97"]


def test_uses_intake_not_list_yen():
    # Public list ¥ would say under; intake ¥ says fine -> never "under".
    assert one("A96", 25, cost(intake=60, listed=500, kg="0.3")).decision == "list-only"


def test_s06_locked_at_25_even_if_cost_says_more():
    r = one("S06", 25, cost(intake=500, kg="2"))
    assert r.decision == "locked" and r.target_usd == 25
    assert one("S06", 27, cost(intake=60, kg="0.5")).decision == "lock-drift"


@pytest.mark.parametrize("ma", ["K03", "v04", "Z99"])
def test_held_and_never_list_skipped(ma):
    r = one(ma, 1, cost(intake=999, kg="1"))
    assert r.decision == "skip-held" and r.target_usd is None


def test_missing_weight_skipped_not_guessed():
    r = one("O01", 22, cost(intake="73.8"))
    assert r.decision == "skip-missing" and r.reason == "missing kg" and r.landed_usd is None


def test_missing_intake_skipped_even_with_list_yen():
    assert one("A95", 22, cost(listed=80, kg="0.3")).decision == "skip-missing"


def test_fallback_weight_used_only_when_cost_kg_blank():
    r = one("A94", 30, cost(intake=80), weights={"A94": Decimal("0.3")})
    assert r.kg == 0.3 and r.decision == "ok"


def test_held_list_resolves_through_ts_loader():
    path = tc.held_json_from_ts()
    assert path == (tc.ROOT / "data" / "held.json").resolve()
    real = tc.load_held_from_ts()
    held = json.loads(path.read_text(encoding="utf-8"))["heldIncomplete"]
    assert all(real.skip_reason(m) == "held" for m in held)


def test_ts_without_json_import_refused(tmp_path):
    ts = tmp_path / "held-incomplete.ts"
    ts.write_text('export const HELD = ["K03", "V04"];\n')
    with pytest.raises(ValueError):
        tc.held_json_from_ts(ts)


def test_cli_writes_only_named_outputs(tmp_path: Path):
    live = tmp_path / "live.json"
    live.write_text(json.dumps({"products": [{"ma": "A01", "priceUsd": 27}, {"ma": "S06", "priceUsd": 25},
                                             {"ma": "O01", "priceUsd": 22}]}))
    costs = tmp_path / "c.csv"
    costs.write_text("ma,baseline_cny,recheck_cny,kg\nA01,95.0,109.0,0.3\nS06,60.39,59.9,0.5\nO01,73.8,,\n")
    md, js = tmp_path / "r.md", tmp_path / "r.json"
    before = set(tmp_path.iterdir())
    assert tc.main(["--live", str(live), "--costs", str(costs), "--out-md", str(md), "--out-json", str(js)]) == 0
    assert set(tmp_path.iterdir()) - before == {md, js}
    s = json.loads(js.read_text())
    assert s["outcome"] == "QUIET_OK" and s["writes"] == "none"
    assert s["counts"]["list-only"] == 1 and s["counts"]["locked"] == 1 and s["counts"]["skip-missing"] == 1
    assert "## List-only" in md.read_text()


def test_no_network_imports():
    src = Path(tc.__file__).read_text(encoding="utf-8")
    for bad in ("urllib", "requests", "http.client", "socket", "subprocess"):
        assert f"import {bad}" not in src and f"from {bad}" not in src
