"""Piece 38: run_gap_check.py — offline, tmp-dir fixtures only."""
import json
import os
from datetime import datetime, timezone
from pathlib import Path

import pytest

import daily_shop_check as d
import run_gap_check as g

REPO = Path(__file__).resolve().parents[2]
NOW = "2026-10-21T14:00:00+00:00"   # 07:00 PT


def cfg(tmp_path, jobs):
    p = tmp_path / "rg.json"
    p.write_text(json.dumps({"schema": "run-gaps/v1", "jobs": jobs}))
    return p


QC = {"name": "qc", "kind": "dated", "pattern": "out/midnight-qc/{date}/", "timezone": "America/Los_Angeles",
      "expected_hour": 2, "required": ["started.json", "summary.json"], "json_files": ["started.json", "summary.json"]}


def qc_dir(root, day, files=None):
    p = root / "out/midnight-qc" / day
    p.mkdir(parents=True, exist_ok=True)
    for n, body in (files or {"started.json": "{}", "summary.json": "{}"}).items():
        (p / n).write_text(body)
    return p


def rep(root, c, now=NOW, days=7):
    return g.run(root, c, datetime.fromisoformat(now), days)


def job(r, name):
    return next(j for j in r["jobs"] if j["job"] == name)


def test_shipped_config_loads():
    jobs = g.load_config(REPO / "data/run-gaps.json")
    names = {j["name"] for j in jobs}
    assert {"midnight_qc", "muse_pack", "muse_extras", "muse_today", "cost_recheck", "auto_list_state"} <= names


def test_all_days_present_ok(tmp_path):
    for i in range(15, 22):
        qc_dir(tmp_path, f"2026-10-{i}")
    r = job(rep(tmp_path, cfg(tmp_path, [QC])), "qc")
    assert r["status"] == "OK" and r["missing"] == [] and r["last_output"] == "2026-10-21"


def test_silent_gap_like_oct_17_19(tmp_path):
    for day in ("2026-10-15", "2026-10-16", "2026-10-20", "2026-10-21"):
        qc_dir(tmp_path, day)
    r = job(rep(tmp_path, cfg(tmp_path, [QC])), "qc")
    assert r["missing"] == ["2026-10-17", "2026-10-18", "2026-10-19"]
    assert r["status"] == "WARN" and not r["stale"]


def test_stale_only_after_expected_hour(tmp_path):
    for i in range(15, 21):
        qc_dir(tmp_path, f"2026-10-{i}")
    c = cfg(tmp_path, [QC])
    early = job(rep(tmp_path, c, now="2026-10-21T08:30:00+00:00"), "qc")  # 01:30 PT
    assert not early["stale"] and "2026-10-21" not in early["missing"] and early["status"] == "OK"
    late = job(rep(tmp_path, c), "qc")  # 07:00 PT
    assert late["stale"] and "2026-10-21" in late["missing"]


def test_timezone_decides_today(tmp_path):
    qc_dir(tmp_path, "2026-10-20")
    r = job(rep(tmp_path, cfg(tmp_path, [QC]), now="2026-10-21T05:00:00+00:00", days=1), "qc")  # 22:00 PT Oct 20
    assert r["expected_today"] == "2026-10-20" and r["status"] == "OK"


def test_half_written_missing_required_and_zero_byte(tmp_path):
    qc_dir(tmp_path, "2026-10-21", {"started.json": "{}"})
    p = qc_dir(tmp_path, "2026-10-20")
    (p / "shot.png").write_bytes(b"")
    (p / "x.tmp").write_text("a")
    r = job(rep(tmp_path, cfg(tmp_path, [QC]), days=2), "qc")
    hw = r["half_written"]
    assert hw["2026-10-21"] == ["missing required out/midnight-qc/2026-10-21/summary.json"]
    assert "zero-byte out/midnight-qc/2026-10-20/shot.png" in hw["2026-10-20"]
    assert "partial file out/midnight-qc/2026-10-20/x.tmp" in hw["2026-10-20"]
    assert r["status"] == "WARN"


def test_bad_json_is_half_written(tmp_path):
    qc_dir(tmp_path, "2026-10-21", {"started.json": "{}", "summary.json": '{"overall": "PA'})
    r = job(rep(tmp_path, cfg(tmp_path, [QC]), days=1), "qc")
    assert r["half_written"]["2026-10-21"] == ["bad JSON out/midnight-qc/2026-10-21/summary.json"]


def test_dated_file_with_offset(tmp_path):
    j = {"name": "pack", "kind": "dated", "pattern": "out/muse/pack-{date}.md", "timezone": "UTC",
         "expected_hour": 12, "date_offset_days": -1}
    (tmp_path / "out/muse").mkdir(parents=True)
    (tmp_path / "out/muse/pack-2026-10-20.md").write_text("x")
    (tmp_path / "out/muse/pack-message-2026-10-21.txt").write_text("x")  # must not match
    r = job(rep(tmp_path, cfg(tmp_path, [j]), now="2026-10-21T13:00:00+00:00", days=1), "pack")
    assert r["expected_today"] == "2026-10-20" and r["status"] == "OK" and r["last_output"] == "2026-10-20"


def test_zero_byte_dated_file(tmp_path):
    j = {"name": "cost", "kind": "dated", "pattern": "verify/c/c-{date}.csv", "timezone": "UTC", "expected_hour": 11}
    (tmp_path / "verify/c").mkdir(parents=True)
    (tmp_path / "verify/c/c-2026-10-21.csv").write_text("")
    r = job(rep(tmp_path, cfg(tmp_path, [j]), days=1), "cost")
    assert r["half_written"] == {"2026-10-21": ["zero-byte verify/c/c-2026-10-21.csv"]}


def test_single_file_mtime(tmp_path):
    j = {"name": "today", "kind": "single", "pattern": "TODAY.md", "timezone": "UTC", "expected_hour": 12}
    f = tmp_path / "TODAY.md"
    f.write_text("x")
    ts = datetime(2026, 10, 20, 11, tzinfo=timezone.utc).timestamp()
    os.utime(f, (ts, ts))
    r = job(rep(tmp_path, cfg(tmp_path, [j])), "today")
    assert r["last_output"] == "2026-10-20" and r["stale"]
    ts = datetime(2026, 10, 21, 11, tzinfo=timezone.utc).timestamp()
    os.utime(f, (ts, ts))
    assert job(rep(tmp_path, cfg(tmp_path, [j])), "today")["status"] == "OK"


AL = {"name": "al", "kind": "state", "pattern": "state/last_check.json", "timezone": "UTC", "max_age_hours": 6,
      "json_files": ["state/last_check.json", "state/cat.json"], "zero_byte_ok": ["*.lock"], "scan_dir": "state"}


def al_state(root, at="2026-10-21T13:00:00+00:00", cat='{"products": []}'):
    s = root / "state"
    s.mkdir(parents=True, exist_ok=True)
    (s / "last_check.json").write_text(json.dumps({"at": at, "result": "noop"}))
    (s / "cat.json").write_text(cat)
    (s / "run.sh.lock").write_text("")
    return s


def test_state_fresh_ok_and_lock_files_allowed(tmp_path):
    al_state(tmp_path)
    r = job(rep(tmp_path, cfg(tmp_path, [AL])), "al")
    assert r["status"] == "OK" and r["age_hours"] == 1.0 and r["last_at"] == "2026-10-21T13:00:00+00:00"


def test_state_stale(tmp_path):
    al_state(tmp_path, at="2026-10-21T04:27:35+00:00")
    r = job(rep(tmp_path, cfg(tmp_path, [AL])), "al")
    assert r["stale"] and r["status"] == "WARN" and not r["half_written"]


def test_state_half_written(tmp_path):
    s = al_state(tmp_path, cat='{"products": [')
    (s / "held.json").write_text("")
    (s / "last_check.json.partial").write_text("x")
    r = job(rep(tmp_path, cfg(tmp_path, [AL])), "al")
    probs = r["half_written"]["2026-10-21"]
    assert "bad JSON state/cat.json" in probs and "zero-byte state/held.json" in probs
    assert "partial file state/last_check.json.partial" in probs


def test_state_empty_last_check(tmp_path):
    s = al_state(tmp_path)
    lc = s / "last_check.json"
    lc.write_text("")
    t = datetime.fromisoformat(NOW).timestamp()
    os.utime(lc, (t, t))  # pin mtime: unreadable state is dated by mtime (was real-clock dependent)
    r = job(rep(tmp_path, cfg(tmp_path, [AL])), "al")
    assert r["stale"] and "zero-byte state/last_check.json" in r["half_written"]["2026-10-21"]


def test_state_missing(tmp_path):
    r = job(rep(tmp_path, cfg(tmp_path, [AL])), "al")
    assert r["last_output"] is None and r["stale"]


@pytest.mark.parametrize("bad", [{"schema": "x", "jobs": []},
                                 {"schema": "run-gaps/v1", "jobs": [{"name": "a", "kind": "dated", "pattern": "x", "timezone": "UTC"}]},
                                 {"schema": "run-gaps/v1", "jobs": [{"name": "a", "kind": "weird", "pattern": "{date}", "timezone": "UTC"}]},
                                 {"schema": "run-gaps/v1", "jobs": [{"name": "a", "kind": "dated", "pattern": "{date}", "timezone": "Mars/X"}]}])
def test_bad_config_exit_2(tmp_path, bad):
    p = tmp_path / "c.json"
    p.write_text(json.dumps(bad))
    assert g.main(["--root", str(tmp_path), "--config", str(p)]) == 2


def test_cli_exit_codes_and_no_writes(tmp_path, capsys):
    qc_dir(tmp_path, "2026-10-21")
    c = cfg(tmp_path, [QC])
    before = sorted(str(p) for p in tmp_path.rglob("*"))
    assert g.main(["--root", str(tmp_path), "--config", str(c), "--days", "1", "--now", NOW]) == 0
    assert g.main(["--root", str(tmp_path), "--config", str(c), "--days", "3", "--now", NOW]) == 1
    assert sorted(str(p) for p in tmp_path.rglob("*")) == before
    assert "| qc |" in capsys.readouterr().out


def test_output_has_paths_and_dates_only(tmp_path):
    qc_dir(tmp_path, "2026-10-21", {"started.json": '{"marker": 98765}', "summary.json": '{"note": "zz-secret-zz"}'})
    out = json.dumps(rep(tmp_path, cfg(tmp_path, [QC]), days=1))
    assert "98765" not in out and "zz-secret-zz" not in out


# --- daily_shop_check hook ---------------------------------------------------

def snap(tmp_path):
    p = tmp_path / "snap.json"
    p.write_text((REPO / "data/fixtures/daily-inputs-synthetic.json").read_text(encoding="utf-8"))
    return p


def dsc(tmp_path, *extra):
    out = tmp_path / "o.json"
    rc = d.main(["--reduced", "--snapshot", str(snap(tmp_path)), "--out-json", str(out), *extra])
    return rc, json.loads(out.read_text())


def test_hook_absent_without_flag(tmp_path):
    _rc, s = dsc(tmp_path)
    assert "run_gaps" not in [x["name"] for x in s["sections"]]


def test_hook_warn_only(tmp_path):
    root = tmp_path / "shop"
    qc_dir(root, "2026-10-21", {"started.json": "{}"})
    base_rc, base = dsc(tmp_path)
    rc, s = dsc(tmp_path, "--run-gaps", str(root), "--run-gaps-config", str(cfg(tmp_path, [QC])),
                "--run-gaps-now", NOW, "--run-gaps-days", "3")
    sec = next(x for x in s["sections"] if x["name"] == "run_gaps")
    assert sec["status"] == "WARN" and not sec["fail"]
    assert any("2026-10-19" in w and "half-written 2026-10-21" in w for w in sec["warn"])
    assert s["overall"] != "FAIL" or base["overall"] == "FAIL"


def test_hook_bad_config_is_warn(tmp_path):
    bad = tmp_path / "bad.json"
    bad.write_text("{")
    _rc, s = dsc(tmp_path, "--run-gaps", str(tmp_path), "--run-gaps-config", str(bad))
    sec = next(x for x in s["sections"] if x["name"] == "run_gaps")
    assert sec["status"] == "WARN" and "could not run" in sec["warn"][0]


def test_hook_ok_is_pass(tmp_path):
    root = tmp_path / "shop"
    qc_dir(root, "2026-10-21")
    _rc, s = dsc(tmp_path, "--run-gaps", str(root), "--run-gaps-config", str(cfg(tmp_path, [QC])),
                 "--run-gaps-now", NOW, "--run-gaps-days", "1")
    assert next(x for x in s["sections"] if x["name"] == "run_gaps")["status"] == "PASS"


# --- auto-list active window (08:09-22:54 America/Los_Angeles, every 15 min) ---
WIN = {"timezone": "America/Los_Angeles", "start": "08:09", "end": "22:54", "max_age_minutes": 45}
ALW = {k: v for k, v in AL.items() if k != "max_age_hours"} | {"active_window": WIN}


def test_window_outside_morning_not_stale(tmp_path):
    al_state(tmp_path, at="2026-10-21T05:50:00+00:00")   # 22:50 PT last night
    r = job(rep(tmp_path, cfg(tmp_path, [ALW]), now="2026-10-21T14:35:00+00:00"), "al")  # 07:35 PT
    assert r["in_active_window"] is False and not r["stale"] and r["status"] == "OK"


def test_window_outside_late_night_not_stale(tmp_path):
    al_state(tmp_path, at="2026-10-22T05:50:00+00:00")   # 22:50 PT
    r = job(rep(tmp_path, cfg(tmp_path, [ALW]), now="2026-10-22T09:00:00+00:00"), "al")  # 02:00 PT
    assert r["in_active_window"] is False and not r["stale"]


def test_window_inside_fresh_ok(tmp_path):
    al_state(tmp_path, at="2026-10-21T18:00:00+00:00")   # 11:00 PT
    r = job(rep(tmp_path, cfg(tmp_path, [ALW]), now="2026-10-21T18:30:00+00:00"), "al")
    assert r["in_active_window"] and not r["stale"]


def test_window_inside_stale_over_45(tmp_path):
    al_state(tmp_path, at="2026-10-21T18:00:00+00:00")
    r = job(rep(tmp_path, cfg(tmp_path, [ALW]), now="2026-10-21T18:46:00+00:00"), "al")
    assert r["in_active_window"] and r["stale"] and r["status"] == "WARN"


def test_window_exactly_45_not_stale(tmp_path):
    al_state(tmp_path, at="2026-10-21T18:00:00+00:00")
    r = job(rep(tmp_path, cfg(tmp_path, [ALW]), now="2026-10-21T18:45:00+00:00"), "al")
    assert not r["stale"]


def test_window_grace_after_open(tmp_path):
    al_state(tmp_path, at="2026-10-21T05:50:00+00:00")   # last night
    c = cfg(tmp_path, [ALW])
    assert not job(rep(tmp_path, c, now="2026-10-21T15:30:00+00:00"), "al")["stale"]   # 08:30 PT, 21 min after open
    assert job(rep(tmp_path, c, now="2026-10-21T15:55:00+00:00"), "al")["stale"]       # 08:55 PT, 46 min after open


def test_window_missing_state_inside_vs_outside(tmp_path):
    c = cfg(tmp_path, [ALW])
    assert not job(rep(tmp_path, c, now="2026-10-21T14:00:00+00:00"), "al")["stale"]
    assert job(rep(tmp_path, c, now="2026-10-21T20:00:00+00:00"), "al")["stale"]


def test_window_max_age_configurable(tmp_path):
    al_state(tmp_path, at="2026-10-21T18:00:00+00:00")
    c = cfg(tmp_path, [{**ALW, "active_window": {**WIN, "max_age_minutes": 90}}])
    assert not job(rep(tmp_path, c, now="2026-10-21T19:15:00+00:00"), "al")["stale"]


def test_shipped_config_has_window():
    j = next(x for x in json.loads((REPO / "data/run-gaps.json").read_text())["jobs"] if x["name"] == "auto_list_state")
    assert j["active_window"] == WIN
