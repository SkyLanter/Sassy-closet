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


def test_full_catalog_missing_s06_is_lock_drift():
    c = {"A50": {"intake_cny": "100", "list_cny": "", "kg": "0.3"}}
    rows = tc.evaluate({"A50": 999}, c, POLICY, require_s06=True)
    drift = [r for r in rows if r.decision == "lock-drift"]
    assert [r.ma for r in drift] == ["S06"] and "missing from live catalog" in drift[0].reason
    s = tc.summarize(rows)
    assert s["outcome"] == "LOCK_DRIFT" and s["counts"]["lock-drift"] == 1
    json.dumps(s, allow_nan=False)  # strict-JSON safe


def test_full_catalog_with_s06_spelled_s6_is_fine():
    rows = tc.evaluate({"s6": 25}, {}, POLICY, require_s06=True)
    assert [(r.ma, r.decision) for r in rows] == [("S06", "locked")]
    assert tc.summarize(rows)["outcome"] == "QUIET_OK"


def test_partial_input_does_not_require_s06():
    assert tc.evaluate({}, {}, POLICY) == []


def test_s06_off_25_outcome_is_lock_drift_not_quiet():
    s = tc.summarize(tc.evaluate({"S06": 27}, {}, POLICY))
    assert s["outcome"] == "LOCK_DRIFT"


def test_under_outranks_lock_drift_outcome():
    c = {"A50": {"intake_cny": "100", "list_cny": "", "kg": "0.3"}}
    s = tc.summarize(tc.evaluate({"A50": 1, "S06": 27}, c, POLICY))
    assert s["outcome"] == "UNDER_FOUND" and s["counts"]["lock-drift"] == 1


def test_main_requires_s06_in_live_file(tmp_path):
    live = tmp_path / "live.json"
    live.write_text(json.dumps({"prices": {"A50": 999}}), encoding="utf-8")
    costs = tmp_path / "c.csv"
    costs.write_text("ma,intake_cny,kg\nA50,100,0.3\n", encoding="utf-8")
    out = tmp_path / "o.json"
    tc.main(["--live", str(live), "--costs", str(costs), "--out-json", str(out), "--out-md", str(tmp_path / "o.md")])
    assert json.loads(out.read_text())["outcome"] == "LOCK_DRIFT"


def _catalog(tmp_path, payload):
    path = tmp_path / "live.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    return tc.load_live(path)


def test_hold_null_does_not_abort_and_padded_s06_stays_visible(tmp_path):
    loaded = _catalog(tmp_path, {"products": [
        {"ma": "S006", "priceUsd": 40, "status": "available"},
        {"ma": "K06", "priceUsd": None, "status": "hold"},
        {"ma": "A01", "priceUsd": 30, "status": "available"},
        {"ma": "S06", "priceUsd": 25, "status": "available"},
        "not-a-row",
    ]})
    assert loaded["S06"] == 40
    assert loaded["A01"] == 30
    assert "K06" not in loaded
    rows = tc.evaluate(loaded, {}, POLICY, require_s06=True)
    assert [(r.ma, r.decision) for r in rows if r.ma == "S06"] == [("S06", "lock-drift")]


def test_sold_hold_and_bad_dollars_are_not_live_prices(tmp_path):
    loaded = _catalog(tmp_path, {"products": [
        {"ma": "A02", "priceUsd": 1, "status": "sold"},
        {"ma": "A03", "priceUsd": 1, "status": "hold"},
        {"ma": "A04", "priceUsd": True, "status": "available"},
        {"ma": "A05", "priceUsd": "2.5e1"},
        {"ma": "A06", "priceUsd": "2$5"},
        {"ma": "A07", "priceUsd": "0,025"},
        {"ma": "A08", "priceUsd": "12,50"},
        {"ma": "A09", "priceUsd": "$28"},
        {"ma": "A10", "priceUsd": "1,200"},
        {"ma": "A01", "priceUsd": 22},
        {"ma": "A01", "priceUsd": None},
        {"ma": "A01", "priceUsd": 33},
        {"ma": "O01", "priceUsd": 19, "status": ""},
        {"ma": "O01", "priceUsd": "oops", "status": "live"},
    ]})
    assert loaded["A09"] == 28
    assert loaded["A10"] == 1200
    assert loaded["A01"] == 33
    assert loaded["O01"] == 19
    assert set(loaded) == {"A09", "A10", "A01", "O01"}


def test_prices_map_keeps_an_off_lock_s06_spelling(tmp_path):
    loaded = _catalog(tmp_path, {"prices": {"S06": 25, "S006": 40, "A01": True, "K03": "$30"}})
    assert loaded["S06"] == 40
    assert loaded["K03"] == 30
    assert "A01" not in loaded
    first = _catalog(tmp_path, {"products": [
        {"ma": "S006", "priceUsd": 40},
        {"ma": "S06", "priceUsd": 25},
    ]})
    assert first == {"S06": 40.0}
    locked = _catalog(tmp_path, {"products": [
        {"ma": "S006", "priceUsd": "25.00"},
        {"ma": "S06", "priceUsd": 25},
    ]})
    assert locked == {"S06": 25.0}


def test_main_hold_null_and_sold_row_stay_quiet(tmp_path):
    live = tmp_path / "live.json"
    live.write_text(json.dumps({"products": [
        {"ma": "K06", "priceUsd": None, "status": "hold"},
        {"ma": "S06", "priceUsd": 25, "status": "available"},
        {"ma": "A50", "priceUsd": 1, "status": "sold"},
    ]}), encoding="utf-8")
    costs = tmp_path / "c.csv"
    costs.write_text("ma,intake_cny,kg\nA50,100,0.3\nS06,60,0.5\n", encoding="utf-8")
    out = tmp_path / "o.json"
    assert tc.main([
        "--live", str(live), "--costs", str(costs),
        "--out-json", str(out), "--out-md", str(tmp_path / "o.md"),
    ]) == 0
    summary = json.loads(out.read_text())
    assert summary["outcome"] == "QUIET_OK"
    assert summary["counts"]["under"] == 0
    assert summary["counts"]["locked"] == 1
