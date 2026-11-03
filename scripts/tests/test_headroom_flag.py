import json
import pytest

import too_cheap_check as tc
from held_policy import HeldPolicy

POLICY = HeldPolicy(held=("K03",), never_list=())


def row(ma, live, target, decision="ok"):
    return tc.Row(ma=ma, live_usd=float(live), intake_cny=1.0, list_cny=None, kg=0.3,
                  landed_usd=1.0, target_usd=target, list_target_usd=None, decision=decision, reason="")


def names(items):
    return [i["ma"] for i in items]


def test_exact_target_is_no_headroom():
    zero, band = tc.headroom([row("A08", 30, 30), row("A01", 31, 30)])
    assert names(zero) == ["A08"] and band == []
    assert zero[0]["headroom_usd"] == 0 and zero[0]["headroom_pct"] == 0


def test_list_only_at_target_also_flagged():
    zero, _ = tc.headroom([row("A13", 25, 25, "list-only")])
    assert names(zero) == ["A13"]


@pytest.mark.parametrize("decision", ["under", "locked", "lock-drift", "skip-held", "skip-missing"])
def test_non_priced_rows_never_flagged(decision):
    zero, band = tc.headroom([row("X01", 25, 25, decision)], 50)
    assert zero == [] and band == []


def test_band_inclusive_edge_and_outside():
    rows = [row("B01", 33, 30), row("B02", 34, 30), row("B03", 30.5, 30)]
    zero, band = tc.headroom(rows, 10)  # 10% of 30 = $3
    assert zero == [] and names(band) == ["B01", "B03"]
    assert band[0]["headroom_usd"] == 3 and band[0]["headroom_pct"] == 10


def test_band_off_by_default():
    _, band = tc.headroom([row("B01", 31, 30)])
    assert band == []


def test_negative_pct_refused():
    with pytest.raises(ValueError):
        tc.headroom([], -1)


def test_decisions_and_counts_unchanged_by_headroom():
    rows = [row("A08", 30, 30), row("A01", 31, 30)]
    a, b = tc.summarize(rows), tc.summarize(rows, 20)
    assert a["counts"] == b["counts"] and a["outcome"] == b["outcome"] and a["rows"] == b["rows"]
    assert names(b["headroom_band"]) == ["A01"] and b["headroom_pct"] == 20


def test_markdown_sections():
    md0 = tc.markdown(tc.summarize([row("A08", 30, 30)]))
    assert "## No headroom (live = target)" in md0 and "A08" in md0 and "warning band" not in md0
    md5 = tc.markdown(tc.summarize([row("A01", 31, 30)], 5))
    assert "## No headroom (live = target)\n\nNone." in md5 and "≤ 5% above target" in md5


def test_evaluate_end_to_end_exact_target():
    (r,) = tc.evaluate({"A50": 999}, {"A50": {"intake_cny": "100", "list_cny": "", "kg": "0.3"}}, POLICY)
    live = r.target_usd
    (r2,) = tc.evaluate({"A50": live}, {"A50": {"intake_cny": "100", "list_cny": "", "kg": "0.3"}}, POLICY)
    assert names(tc.summarize([r2])["no_headroom"]) == ["A50"]


def _cli(tmp_path, *extra):
    live = tmp_path / "live.json"; costs = tmp_path / "c.csv"; out = tmp_path / "r.json"
    live.write_text(json.dumps({"prices": {"A50": 1000}}))
    costs.write_text("ma,intake_cny,list_cny,kg\nA50,100,,0.3\n")
    rc = tc.main(["--live", str(live), "--costs", str(costs),
                  "--out-json", str(out), "--out-md", str(tmp_path / "r.md"), *extra])
    return rc, out


def test_cli_rejects_negative_pct(tmp_path):
    with pytest.raises(SystemExit):
        _cli(tmp_path, "--headroom-pct", "-5")


def test_cli_pct_recorded(tmp_path):
    rc, out = _cli(tmp_path, "--headroom-pct", "7.5")
    d = json.loads(out.read_text())
    assert rc == 0 and d["headroom_pct"] == 7.5 and d["no_headroom"] == [] and d["writes"] == "none"
