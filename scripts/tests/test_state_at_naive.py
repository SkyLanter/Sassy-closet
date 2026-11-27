"""A state file's "at" written without an offset must not crash the daily watchers.

`run_gap_check.py` and `hung_run_watch.py` both parse `last_check.json`'s "at"
with `datetime.fromisoformat`. A value such as `2026-10-01T12:00:00` (no `Z`,
no `+00:00`) parses as a naive datetime, and every later comparison against a
timezone-aware `now` raises `TypeError`. `daily_shop_check.py` swallows that into
a WARN section, so the watch silently reports nothing instead of the streak.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import hung_run_watch as h
import run_gap_check as g

NOW = datetime(2026, 10, 1, 20, 0, tzinfo=timezone.utc)
NAIVE_AT = "2026-10-01T12:00:00"

STATE_JOB = {
    "name": "auto_list_state",
    "kind": "state",
    "pattern": "auto-list/state/last_check.json",
    "timezone": "UTC",
    "max_age_hours": 6,
}


def _write_state(root: Path, at: str) -> Path:
    state = root / "auto-list" / "state"
    state.mkdir(parents=True, exist_ok=True)
    path = state / "last_check.json"
    path.write_text(json.dumps({"at": at, "result": "noop"}), encoding="utf-8")
    return path


def test_run_gap_check_reads_a_naive_at_as_utc(tmp_path: Path) -> None:
    _write_state(tmp_path, NAIVE_AT)
    result = g.check_state(STATE_JOB, tmp_path, NOW, 14)
    assert result["last_at"] == "2026-10-01T12:00:00+00:00"
    assert result["age_hours"] == 8.0
    assert result["stale"] is True
    assert result["status"] == "WARN"


def test_run_gap_check_naive_at_in_the_active_window(tmp_path: Path) -> None:
    _write_state(tmp_path, NAIVE_AT)
    job = dict(
        STATE_JOB,
        active_window={
            "timezone": "UTC",
            "start": "08:09",
            "end": "22:54",
            "max_age_minutes": 45,
        },
    )
    result = g.check_state(job, tmp_path, NOW, 14)
    assert result["in_active_window"] is True
    assert result["stale"] is True


def test_hung_run_watch_heartbeat_accepts_a_naive_at(tmp_path: Path) -> None:
    _write_state(tmp_path, NAIVE_AT)
    beat = h.heartbeat(tmp_path / "auto-list" / "state")
    assert beat == datetime(2026, 10, 1, 12, 0, tzinfo=timezone.utc)


def test_hung_run_watch_naive_at_without_lock_files(tmp_path: Path) -> None:
    _write_state(tmp_path, NAIVE_AT)
    report = h.run(tmp_path / "auto-list", NOW, window=h.DEFAULT_WINDOW, held=set())
    assert report["heartbeat"] == "2026-10-01T12:00:00+00:00"
    # 12:00 UTC is before today's 15:09 UTC (08:09 PT) window opening, so the
    # watch owes slots only from the window start: 13:00 PT is 4h51m - 5m grace.
    assert report["slots"]["missed"] == 19
    assert report["overall"] == "WARN"


def test_hung_run_watch_naive_at_inside_the_window(tmp_path: Path) -> None:
    """16:00 UTC is 09:00 PT, so today's window is open and the naive beat is owed."""
    _write_state(tmp_path, "2026-10-01T16:00:00")
    report = h.run(tmp_path / "auto-list", NOW, window=h.DEFAULT_WINDOW, held=set())
    assert report["heartbeat"] == "2026-10-01T16:00:00+00:00"
    assert report["slots"]["missed"] == 15  # 235 min since 16:00 after the 5-min grace
    assert report["overall"] == "WARN"


def test_aware_at_still_wins_over_a_naive_one(tmp_path: Path) -> None:
    """Mixing spellings must keep the newest beat, not raise."""
    state = tmp_path / "auto-list" / "state"
    state.mkdir(parents=True, exist_ok=True)
    (state / "last_check.json").write_text(
        json.dumps({"at": "2026-10-01T18:00:00+00:00"}), encoding="utf-8"
    )
    lock = state / "run.sh.lock"
    lock.write_text("")
    late = datetime(2026, 10, 1, 19, 0, tzinfo=timezone.utc).timestamp()
    import os

    os.utime(lock, (late, late))
    assert h.heartbeat(state) == datetime(2026, 10, 1, 19, 0, tzinfo=timezone.utc)
