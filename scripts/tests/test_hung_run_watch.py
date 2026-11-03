"""Piece 44: hung_run_watch.py — offline, tmp-dir fixtures only."""
import json
import os
from datetime import datetime, timezone
from pathlib import Path

import hung_run_watch as h

NOW = "2026-10-21T22:00:00+00:00"   # 15:00 PT, inside 08:09-22:54 window
T = datetime.fromisoformat(NOW)


def at(minutes_ago):
    return T.timestamp() - minutes_ago * 60


def mk(root, hb_min=5, lock_min=5, runs=None):
    s = root / "state"; s.mkdir(parents=True)
    iso = datetime.fromtimestamp(at(hb_min), tz=timezone.utc).isoformat()
    (s / "last_check.json").write_text(json.dumps({"at": iso, "result": "noop"}))
    for n in ("run.sh.lock", "autolist.lock"):
        (s / n).write_text("")
        os.utime(s / n, (at(lock_min), at(lock_min)))
    r = root / "runs"; r.mkdir()
    for name, files in (runs or {}).items():
        d = r / name; d.mkdir()
        for f, body in files.items():
            (d / f).write_text(body)
    return root


GOOD = {"run.log": "x", "summary.json": "{}"}


def ino(root, n):
    return (root / "state" / n).stat().st_ino


def test_healthy_ok(tmp_path):
    r = h.run(mk(tmp_path, runs={"20261021T210000Z": GOOD}), T, held=set())
    assert r["overall"] == "OK" and r["slots"]["missed"] == 0 and r["warn"] == []


def test_missed_slots_counted(tmp_path):
    r = h.run(mk(tmp_path, hb_min=50, lock_min=50), T, held=set())
    assert r["slots"]["missed"] == 3 and r["overall"] == "WARN"
    assert "3 missed 15-min slot(s)" in r["warn"][0]


def test_outside_window_not_owed(tmp_path):
    night = datetime.fromisoformat("2026-10-22T09:00:00+00:00")  # 02:00 PT
    r = h.run(mk(tmp_path, hb_min=600, lock_min=600), night, held=set())
    assert r["slots"]["in_active_window"] is False and r["overall"] == "OK"


def test_window_start_resets_debt(tmp_path):
    morning = datetime.fromisoformat("2026-10-21T15:20:00+00:00")  # 08:20 PT, window opened 08:09
    r = h.run(mk(tmp_path, hb_min=600, lock_min=600), morning, held=set())
    assert r["slots"]["missed"] == 0


def test_no_window_counts_all(tmp_path):
    r = h.run(mk(tmp_path, hb_min=60, lock_min=60), T, window=None, held=set())
    assert r["slots"]["missed"] == 3


def test_stale_lock_held(tmp_path):
    root = mk(tmp_path, hb_min=5, lock_min=40)
    r = h.run(root, T, held={ino(root, "run.sh.lock")})
    assert [l["lock"] for l in r["stale_locks"]] == ["run.sh.lock"] and r["overall"] == "WARN"


def test_old_unheld_lock_is_fine(tmp_path):
    root = mk(tmp_path, hb_min=5, lock_min=40)
    assert h.run(root, T, held=set())["stale_locks"] == []


def test_fresh_held_lock_is_fine(tmp_path):
    root = mk(tmp_path, hb_min=5, lock_min=5)
    r = h.run(root, T, held={ino(root, "run.sh.lock")})
    assert r["stale_locks"] == [] and r["run_in_progress"] is True


def test_half_written_runs(tmp_path):
    runs = {"20261021T100000Z": {"run.log": "x"},
            "20261021T110000Z": {"run.log": "", "summary.json": '{"a": ', "drafts.json": ""},
            "20261021T120000Z": dict(GOOD, **{"x.partial": "y"}),
            "20261021T130000Z": {"run.log": "", "summary.json": "{}"},
            "hold-incomplete-20260930": {}}
    r = h.run(mk(tmp_path, runs=runs), T, held=set())
    hw = r["half_written"]
    assert hw["20261021T100000Z"] == ["missing summary.json"]
    assert hw["20261021T110000Z"] == ["zero-byte drafts.json", "bad JSON summary.json"]
    assert hw["20261021T120000Z"] == ["partial file x.partial"]
    assert set(hw) == {"20261021T100000Z", "20261021T110000Z", "20261021T120000Z"}  # empty run.log ok, non-run dir skipped


def test_newest_run_skipped_while_in_progress(tmp_path):
    root = mk(tmp_path, runs={"20261021T210000Z": GOOD, "20261021T215500Z": {"run.log": "x"}})
    assert h.run(root, T, held={ino(root, "run.sh.lock")})["half_written"] == {}
    assert "20261021T215500Z" in h.run(root, T, held=set())["half_written"]


def test_no_heartbeat_warns(tmp_path):
    (tmp_path / "state").mkdir()
    r = h.run(tmp_path, T, window=None, held=set())
    assert r["overall"] == "WARN" and "no heartbeat" in r["warn"][0]


def test_bad_last_check_falls_back_to_lock_mtime(tmp_path):
    root = mk(tmp_path, hb_min=5, lock_min=20)
    (root / "state/last_check.json").write_text("")
    r = h.run(root, T, held=set())
    assert r["slots"]["missed"] == 1


def test_held_inodes_parse(tmp_path):
    p = tmp_path / "locks"
    p.write_text("1: FLOCK  ADVISORY  WRITE 123 fd:01:4567 0 EOF\n2: POSIX  ADVISORY  WRITE 9 00:2a:89 0 EOF\n")
    assert h.held_inodes(p) == {4567, 89}
    assert h.held_inodes(tmp_path / "missing") == set()


def test_readonly_and_no_contents(tmp_path, capsys):
    root = mk(tmp_path, hb_min=50, lock_min=50, runs={"20261021T200000Z": {"run.log": "zz-secret-zz"}})
    before = {str(p): (p.stat().st_mtime, p.stat().st_size) for p in root.rglob("*")}
    rc = h.main(["--autolist", str(root), "--now", NOW, "--json"])
    after = {str(p): (p.stat().st_mtime, p.stat().st_size) for p in root.rglob("*")}
    out = capsys.readouterr().out
    assert rc == 1 and before == after and "zz-secret-zz" not in out


def test_cli_ok_and_usage(tmp_path):
    root = mk(tmp_path, runs={"20261021T200000Z": GOOD})
    assert h.main(["--autolist", str(root), "--now", NOW]) == 0
    assert h.main(["--autolist", str(tmp_path / "nope"), "--now", NOW]) == 2
