"""A state file's "at" with no zone must not crash the two state readers.

`auto-list/state/last_check.json` is written by the auto-list job, and a stamp
such as `2026-10-21T13:00:00` (no offset) is a valid ISO time. Both readers
compared it against an aware `now`:

  * run_gap_check.py crashed with `TypeError: can't subtract offset-naive and
    offset-aware datetimes`, which daily_shop_check turns into a run_gaps WARN
    for the whole check;
  * hung_run_watch.py raised the same TypeError as an uncaught traceback, so
    the WARN-only hung_runs section could not report at all.

A zone-less stamp is read as UTC, the same clock both modules already use for
`now` and for the mtime fallback. The file is never rewritten.
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path

import hung_run_watch as h
import run_gap_check as g

NOW = datetime(2026, 10, 21, 14, 0, tzinfo=timezone.utc)  # 07:00 PT
NOW_TS = NOW.timestamp()
JOB = {"name": "al", "kind": "state", "pattern": "state/last_check.json",
       "timezone": "UTC", "max_age_hours": 6}


def _shop(tmp_path: Path, at: str, *, with_locks: bool = False, mtime: float | None = None) -> Path:
    state = tmp_path / "state"
    state.mkdir(parents=True)
    stamp = state / "last_check.json"
    stamp.write_text(json.dumps({"at": at, "result": "noop"}), encoding="utf-8")
    if with_locks:
        for name in ("run.sh.lock", "autolist.lock"):
            (state / name).write_text("", encoding="utf-8")
    if mtime is not None:
        # pin every file: an unreadable "at" and the locks fall back to mtime,
        # and the real clock would otherwise decide which day that is.
        for path in state.iterdir():
            os.utime(path, (mtime, mtime))
    (tmp_path / "runs").mkdir()
    return tmp_path


def _config(tmp_path: Path) -> Path:
    cfg = tmp_path / "run-gaps.json"
    cfg.write_text(json.dumps({"schema": "run-gaps/v1", "jobs": [JOB]}), encoding="utf-8")
    return cfg


def _job(root: Path, cfg: Path) -> dict:
    report = g.run(root, cfg, NOW, 7)
    return next(item for item in report["jobs"] if item["job"] == "al")


def test_state_at_reads_a_zone_less_stamp_as_utc() -> None:
    assert g.state_at("2026-10-21T13:00:00") == datetime(2026, 10, 21, 13, 0, tzinfo=timezone.utc)
    assert g.state_at("2026-10-21T13:00:00+00:00") == datetime(2026, 10, 21, 13, 0, tzinfo=timezone.utc)
    assert g.state_at("2026-10-21T06:00:00-07:00") == datetime(2026, 10, 21, 13, 0, tzinfo=timezone.utc)


def test_state_at_rejects_junk_without_raising() -> None:
    for bad in (None, "", "   ", "not-a-time", 123, {"at": "x"}, ["2026-10-21"]):
        assert g.state_at(bad) is None


def test_run_gap_check_reads_a_zone_less_state_stamp(tmp_path: Path) -> None:
    root, cfg = _shop(tmp_path, "2026-10-21T13:00:00"), _config(tmp_path)
    result = _job(root, cfg)
    assert result["status"] == "OK"
    assert result["age_hours"] == 1.0
    assert result["last_at"] == "2026-10-21T13:00:00+00:00"
    assert result["half_written"] == {}


def test_run_gap_check_still_flags_a_stale_zone_less_stamp(tmp_path: Path) -> None:
    root, cfg = _shop(tmp_path, "2026-10-21T04:27:35"), _config(tmp_path)
    result = _job(root, cfg)
    assert result["stale"] is True and result["status"] == "WARN"
    assert result["half_written"] == {}


def test_run_gap_check_reports_junk_at_instead_of_crashing(tmp_path: Path) -> None:
    root = _shop(tmp_path, "yesterday-ish", mtime=NOW_TS)
    result = _job(root, _config(tmp_path))
    assert "bad JSON or no 'at' in state/last_check.json" in result["half_written"]["2026-10-21"]
    assert result["last_at"] is None


def test_run_gap_check_cli_exits_clean_on_a_zone_less_stamp(tmp_path: Path) -> None:
    root, cfg = _shop(tmp_path, "2026-10-21T13:00:00"), _config(tmp_path)
    assert g.main(["--root", str(root), "--config", str(cfg),
                   "--now", "2026-10-21T14:00:00+00:00", "--days", "1"]) == 0


def test_hung_run_watch_reads_a_zone_less_heartbeat(tmp_path: Path) -> None:
    root = _shop(tmp_path, "2026-10-21T21:50:00", with_locks=True, mtime=NOW_TS)
    now = datetime(2026, 10, 21, 22, 0, tzinfo=timezone.utc)  # 15:00 PT, inside the window
    report = h.run(root, now, held=set())
    assert report["overall"] == "OK"
    assert report["heartbeat"] == "2026-10-21T21:50:00+00:00"
    assert report["slots"]["missed"] == 0


def test_hung_run_watch_still_counts_missed_slots_from_a_zone_less_heartbeat(tmp_path: Path) -> None:
    root = _shop(tmp_path, "2026-10-21T21:10:00", with_locks=True)
    old = datetime(2026, 10, 21, 21, 10, tzinfo=timezone.utc).timestamp()
    for path in (tmp_path / "state").iterdir():
        os.utime(path, (old, old))
    now = datetime(2026, 10, 21, 22, 0, tzinfo=timezone.utc)
    report = h.run(root, now, held=set())
    assert report["slots"]["missed"] == 3
    assert report["overall"] == "WARN"


def test_hung_run_watch_cli_has_no_traceback_on_a_zone_less_stamp(tmp_path: Path, capsys) -> None:
    root = _shop(tmp_path, "2026-10-21T21:50:00", with_locks=True, mtime=NOW_TS)
    assert h.main(["--autolist", str(root), "--now", "2026-10-21T22:00:00+00:00", "--json"]) == 0
    out = capsys.readouterr()
    assert "Traceback" not in out.err
    assert json.loads(out.out)["heartbeat"] == "2026-10-21T21:50:00+00:00"
