import json

import pytest

import daily_shop_check as d


def tc_summary(**over):
    s = {"outcome": "QUIET_OK", "live_count": 3, "under_target": [], "skipped": [],
         "counts": {"under": 0, "list-only": 0, "ok": 3, "locked": 1, "lock-drift": 0,
                    "skip-held": 0, "skip-missing": 0},
         "no_headroom": [{"ma": "A08"}], "headroom_pct": 0.0, "headroom_band": []}
    s.update(over)
    return s


def test_too_cheap_clean_is_pass_and_no_headroom_is_info_only():
    sec = d.judge_too_cheap(tc_summary())
    assert sec["status"] == "PASS" and sec["detail"]["no_headroom"] == ["A08"]


def test_too_cheap_under_is_fail():
    s = tc_summary(under_target=[{"ma": "A01"}])
    s["counts"]["under"] = 1
    sec = d.judge_too_cheap(s)
    assert sec["status"] == "FAIL" and "A01" in sec["fail"][0]


def test_s06_lock_drift_is_fail():
    s = tc_summary()
    s["counts"]["lock-drift"] = 1
    assert d.judge_too_cheap(s)["status"] == "FAIL"


def test_skip_missing_and_band_warn():
    s = tc_summary(skipped=[{"ma": "O01", "decision": "skip-missing"}],
                   headroom_band=[{"ma": "D04"}], headroom_pct=10.0)
    s["counts"]["skip-missing"] = 1
    sec = d.judge_too_cheap(s)
    assert sec["status"] == "WARN" and len(sec["warn"]) == 2


def test_held_needs_boss_warns_quotes_info():
    sec = d.judge_held({"count": 2, "needs_boss": ["G01"], "approved": False, "already_live": {},
                        "proposals": [{"ma": "A29", "status": "quote", "tiered_usd": 30, "flat25_usd": 27}]})
    assert sec["status"] == "WARN" and "A29 $30/$27" in sec["info"][0]
    assert d.judge_held({"needs_boss": [], "proposals": []})["status"] == "PASS"


def post(status, ma="A01", issues=()):
    return {"post": "x", "ma": ma, "status": status, "issues": list(issues)}


@pytest.mark.parametrize("statuses,want", [(["PASS"], "PASS"), (["PASS", "WARN"], "WARN"),
                                           (["WARN", "FAIL"], "FAIL")])
def test_captions(statuses, want):
    c = {k: statuses.count(k) for k in ("PASS", "WARN", "FAIL")}
    assert d.judge_captions({"counts": c, "posts": [post(s) for s in statuses]})["status"] == want


@pytest.mark.parametrize("statuses,want", [
    (["PASS", "PASS", "PASS"], "PASS"), (["PASS", "SKIP", "SKIP"], "PASS"),
    (["WARN", "PASS", "SKIP"], "WARN"), (["WARN", "FAIL", "PASS"], "FAIL"), (["SKIP", "FAIL", "WARN"], "FAIL")])
def test_combine_worst_wins(statuses, want):
    secs = [{"name": str(i), "status": s, "fail": [], "warn": [], "info": []} for i, s in enumerate(statuses)]
    out = d.combine(secs)
    assert out["overall"] == want and out["writes"] == "none" and out["network"] == "none"


def test_errored_section_is_fail():
    assert d.errored("x", FileNotFoundError("nope"))["status"] == "FAIL"


# ---- end-to-end exit codes on tiny local fixtures ----

def write_inputs(tmp_path, live_a01=27, cost_yen=95, caption_gia=None):
    live = tmp_path / "live.json"
    live.write_text(json.dumps({"products": [
        {"ma": "A01", "priceUsd": live_a01, "status": "available"},
        {"ma": "S06", "priceUsd": 25, "status": "available"}]}), encoding="utf-8")
    costs = tmp_path / "costs.csv"
    costs.write_text("ma,intake_cny,kg\nA01,%s,0.3\nS06,100,0.5\n" % cost_yen, encoding="utf-8")
    args = ["--live", str(live), "--costs", str(costs)]
    if caption_gia is not None:
        cap = tmp_path / "cap.txt"
        cap.write_text(f"Mã A01\nGiá ${caption_gia}\n", encoding="utf-8")
        args += ["--captions", str(cap)]
    return args


def run(tmp_path, args):
    out = tmp_path / "r.json"
    rc = d.main(args + ["--out-json", str(out), "--out-md", str(tmp_path / "r.md")])
    return rc, json.loads(out.read_text(encoding="utf-8"))


def test_e2e_bad_input_is_fail_exit_2(tmp_path):
    rc, s = run(tmp_path, ["--live", str(tmp_path / "missing.json"), "--costs", str(tmp_path / "no.csv")])
    assert rc == 2 and s["overall"] == "FAIL"
    assert [x["status"] for x in s["sections"]] == ["FAIL", "SKIP", "SKIP", "SKIP", "SKIP"]


def test_e2e_exit_codes_follow_overall(tmp_path):
    rc, s = run(tmp_path, write_inputs(tmp_path))
    assert rc == d.EXIT[s["overall"]]
    assert (tmp_path / "r.md").read_text(encoding="utf-8").startswith(f"# Daily shop check: {s['overall']}")


def test_e2e_caption_mismatch_fails(tmp_path):
    rc, s = run(tmp_path, write_inputs(tmp_path, caption_gia=5))
    cap = [x for x in s["sections"] if x["name"] == "captions"][0]
    assert cap["status"] == "FAIL" and rc == 2


def test_warn_ok_maps_warn_to_zero(monkeypatch, tmp_path):
    monkeypatch.setattr(d, "combine", lambda secs: {"overall": "WARN", "sections": secs,
                                                     "writes": "none", "network": "none"})
    assert d.main(write_inputs(tmp_path) + ["--warn-ok"]) == 0
    assert d.main(write_inputs(tmp_path)) == 1


# ---- piece 24: intake gaps section (WARN only, never FAIL, never fixes) ----

def gaps_summary(by_type=None, rows=None):
    return {"report_only": True, "intake_mas": 2,
            "counts": {"live": {"mas": 2, "with_gaps": 1, "with_suspect": 1}},
            "by_type": by_type or {"kg": [], "sell_vs_live": []}, "rows": rows or []}


def test_intake_gaps_clean_is_pass():
    assert d.judge_intake_gaps(gaps_summary())["status"] == "PASS"


def test_intake_gaps_and_suspect_are_warn_never_fail():
    rows = [{"ma": "P03", "suspect": [{"type": "sell_vs_live", "detail": "intake $18 vs live $11"}], "gaps": []}]
    sec = d.judge_intake_gaps(gaps_summary({"kg": ["S14"], "sell_vs_live": ["P03"]}, rows))
    assert sec["status"] == "WARN" and sec["fail"] == []
    assert any("P03" in w for w in sec["warn"])
    assert any("not fixed" in i and "intake $18 vs live $11" in i for i in sec["info"])
    assert sec["detail"]["suspect"][0]["ma"] == "P03"


def test_intake_gaps_crash_is_warn_not_fail():
    assert d.warn_errored("intake_gaps", ValueError("x"))["status"] == "WARN"


def _intake(tmp_path, cny="", usd=""):
    p = tmp_path / "intake.json"
    p.write_text(json.dumps({"submissions": [{"ma": "A01", "kind": "A", "cost_cny": cny, "cost_usd": usd}]}),
                 encoding="utf-8")
    return p


def test_e2e_intake_gaps_warn_does_not_fail_and_input_untouched(tmp_path):
    ip = _intake(tmp_path)
    before = ip.read_bytes()
    rc, s = run(tmp_path, write_inputs(tmp_path) + ["--gaps-intake", str(ip)])
    sec = [x for x in s["sections"] if x["name"] == "intake_gaps"][0]
    assert sec["status"] == "WARN" and sec["fail"] == []
    assert s["overall"] != "FAIL" or any(x["status"] == "FAIL" for x in s["sections"] if x["name"] != "intake_gaps")
    assert ip.read_bytes() == before


def test_e2e_intake_gaps_bad_file_is_warn(tmp_path):
    rc, s = run(tmp_path, write_inputs(tmp_path) + ["--gaps-intake", str(tmp_path / "nope.json")])
    sec = [x for x in s["sections"] if x["name"] == "intake_gaps"][0]
    assert sec["status"] == "WARN" and "could not run" in sec["warn"][0]


def test_e2e_no_intake_gaps_flag_skips(tmp_path):
    rc, s = run(tmp_path, write_inputs(tmp_path) + ["--gaps-intake", str(_intake(tmp_path)), "--no-intake-gaps"])
    assert [x["status"] for x in s["sections"] if x["name"] == "intake_gaps"] == ["SKIP"]


def test_p249_e2e_bare_list_intake_runs_intake_gaps_not_errored(tmp_path):
    p = tmp_path / "intake.json"
    p.write_text(json.dumps([{"ma": "A01", "kind": "A", "cost_cny": "", "cost_usd": ""}]), encoding="utf-8")
    rc, s = run(tmp_path, write_inputs(tmp_path) + ["--gaps-intake", str(p)])
    sec = [x for x in s["sections"] if x["name"] == "intake_gaps"][0]
    assert not any("could not run" in w for w in sec["warn"])
    assert sec["detail"]["intake_mas"] == 1
