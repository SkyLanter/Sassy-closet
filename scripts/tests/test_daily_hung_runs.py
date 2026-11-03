"""Piece 45: hung_runs section in daily_shop_check (WARN-only, read-only)."""
import json
from pathlib import Path

import daily_shop_check as d
from test_hung_run_watch import GOOD, NOW, mk

REPO = Path(__file__).resolve().parents[2]


def dsc(tmp_path, *extra):
    snap = tmp_path / "snap.json"
    snap.write_text((REPO / "data/fixtures/daily-inputs-synthetic.json").read_text(encoding="utf-8"))
    out = tmp_path / "o.json"
    md = tmp_path / "o.md"
    rc = d.main(["--reduced", "--snapshot", str(snap), "--out-json", str(out), "--out-md", str(md), *extra])
    return rc, json.loads(out.read_text()), md.read_text()


def sec(s):
    return next(x for x in s["sections"] if x["name"] == "hung_runs")


def test_absent_without_flag(tmp_path):
    _rc, s, _ = dsc(tmp_path)
    assert "hung_runs" not in [x["name"] for x in s["sections"]]


def test_healthy_is_pass(tmp_path):
    al = mk(tmp_path / "al", runs={"20261021T210000Z": GOOD})
    _rc, s, md = dsc(tmp_path, "--hung-runs", str(al), "--hung-runs-now", NOW)
    x = sec(s)
    assert x["status"] == "PASS" and not x["warn"] and "| hung_runs | PASS |" in md


def test_missed_slots_warn_never_fail(tmp_path):
    al = mk(tmp_path / "al", hb_min=50, lock_min=50)
    base_rc, base, _ = dsc(tmp_path)
    _rc, s, md = dsc(tmp_path, "--hung-runs", str(al), "--hung-runs-now", NOW)
    x = sec(s)
    assert x["status"] == "WARN" and not x["fail"] and any("missed 15-min slot" in w for w in x["warn"])
    assert "WARN: " in md and (s["overall"] != "FAIL" or base["overall"] == "FAIL")


def test_half_written_run_warns(tmp_path):
    al = mk(tmp_path / "al", runs={"20261021T200000Z": {"run.log": ""}, "20261021T210000Z": GOOD})
    _rc, s, _ = dsc(tmp_path, "--hung-runs", str(al), "--hung-runs-now", NOW)
    assert any("half-written run 20261021T200000Z" in w for w in sec(s)["warn"])


def test_no_window_flag(tmp_path):
    al = mk(tmp_path / "al", hb_min=300, lock_min=300)
    night = "2026-10-22T09:00:00+00:00"  # 02:00 PT next day, outside window
    _rc, s, _ = dsc(tmp_path, "--hung-runs", str(al), "--hung-runs-now", night)
    assert sec(s)["status"] == "PASS"
    _rc, s, _ = dsc(tmp_path, "--hung-runs", str(al), "--hung-runs-now", night, "--hung-runs-no-window")
    assert sec(s)["status"] == "WARN"


def test_error_is_warn(tmp_path):
    _rc, s, _ = dsc(tmp_path, "--hung-runs", str(tmp_path / "al"), "--hung-runs-now", "not-a-time")
    x = sec(s)
    assert x["status"] == "WARN" and not x["fail"] and "could not run" in x["warn"][0]


def test_read_only(tmp_path):
    al = mk(tmp_path / "al", hb_min=50, lock_min=50, runs={"20261021T200000Z": {"run.log": ""}})
    before = {str(p): (p.stat().st_mtime, p.stat().st_size) for p in al.rglob("*")}
    dsc(tmp_path, "--hung-runs", str(al), "--hung-runs-now", NOW)
    assert {str(p): (p.stat().st_mtime, p.stat().st_size) for p in al.rglob("*")} == before
