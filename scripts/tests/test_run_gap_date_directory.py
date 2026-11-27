"""A dated run-gap pattern may put `{date}` in a directory, not only the file name.

`check_dated` built `last_output` by splitting the *last* path component on
`{date}`:

    pre, post = Path(pat).name.split("{date}")

For a pattern such as `out/{date}/summary.md` the last component is
`summary.md`, which holds no `{date}`, so `split` returned one item and the
module raised

    ValueError: not enough values to unpack (expected 2, got 1)

`run_gap_check.main` catches that and returns exit 2, so the daily check's
WARN-only `run_gaps` section could not report at all — the whole job list went
dark for a legal config the loader already accepts (`load_config` only requires
that a dated pattern *contains* `{date}`).

The date is now read from the whole relative path, anchored on the pattern, so
`{date}` works in any component and a sibling that merely contains a date is
still not mistaken for this job's output.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import pytest

import run_gap_check as g

NOW = datetime(2026, 11, 27, 12, 0, tzinfo=timezone.utc)


def _root(tmp_path: Path, pattern: str, day: str, *, write_file: bool = True) -> Path:
    target = tmp_path / pattern.format(date=day)
    if pattern.rstrip().endswith("/"):
        target.mkdir(parents=True, exist_ok=True)
    else:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("output\n", encoding="utf-8")
    return target


def _config(tmp_path: Path, pattern: str) -> Path:
    cfg = {
        "schema": "run-gaps/v1",
        "jobs": [{"name": "daydir", "kind": "dated", "pattern": pattern,
                  "timezone": "UTC", "expected_hour": 0}],
    }
    path = tmp_path / "run-gaps.json"
    path.write_text(json.dumps(cfg), encoding="utf-8")
    return path


@pytest.mark.parametrize("pattern", [
    "out/{date}/summary.md",          # date in a directory, file below it
    "out/{date}/",                    # date is the directory itself
    "out/midnight-qc/{date}/",        # the shipped midnight_qc shape
    "out/deep/{date}/nested/ok.md",   # date in the middle of the path
    "verify/cost-recheck-{date}.csv", # date in the file name (the old shape)
])
def test_date_in_any_path_component_is_read(tmp_path, pattern):
    """Every legal dated shape reports last_output instead of crashing."""
    _root(tmp_path, pattern, "2026-11-26")
    report = g.run(tmp_path, _config(tmp_path, pattern), NOW, 2)
    job = report["jobs"][0]
    assert job["last_output"] == "2026-11-26"
    assert job["status"] == "WARN"      # yesterday's output, today missing


def test_date_in_directory_does_not_raise(tmp_path):
    """The regression: this exact call raised ValueError before the fix."""
    _root(tmp_path, "out/{date}/summary.md", "2026-11-26")
    job = g.run(tmp_path, _config(tmp_path, "out/{date}/summary.md"), NOW, 2)["jobs"][0]
    assert "stale" in job and "missing" in job and job["stale"] is True


def test_config_loader_accepts_the_shape_the_checker_crashed_on(tmp_path):
    """The loader already allowed a date directory, so the crash was reachable."""
    pattern = "out/{date}/summary.md"
    jobs = g.load_config(_config(tmp_path, pattern))
    assert jobs[0]["pattern"] == pattern
    _root(tmp_path, pattern, "2026-11-26")
    assert g.run(tmp_path, _config(tmp_path, pattern), NOW, 2)["jobs"][0]["last_output"] == "2026-11-26"


def test_a_sibling_file_is_not_read_as_this_jobs_output(tmp_path):
    """Only the named file under the matching day counts, never a decoy."""
    (tmp_path / "out" / "2026-11-26").mkdir(parents=True)
    (tmp_path / "out" / "2026-11-26" / "summary.md").write_text("x", encoding="utf-8")
    (tmp_path / "out" / "2026-11-25").mkdir(parents=True)
    (tmp_path / "out" / "2026-11-25" / "other.md").write_text("x", encoding="utf-8")
    job = g.run(tmp_path, _config(tmp_path, "out/{date}/summary.md"), NOW, 5)["jobs"][0]
    assert job["last_output"] == "2026-11-26"


def test_cli_exits_zero_on_a_date_directory_and_reports_the_day(tmp_path):
    """Before: exit 2 with `ValueError: not enough values to unpack`."""
    _root(tmp_path, "out/{date}/summary.md", "2026-11-27")
    cfg = _config(tmp_path, "out/{date}/summary.md")
    rc = g.main(["--root", str(tmp_path), "--config", str(cfg),
                 "--now", "2026-11-27T23:00:00+00:00", "--days", "1"])
    assert rc == 0  # today's output is present and past expected_hour


def test_ambiguous_double_date_is_not_guessed(tmp_path):
    """Two {date} placeholders have no single day; report no last_output."""
    (tmp_path / "out" / "2026-11-26" / "2026-11-26").mkdir(parents=True)
    job = g.run(tmp_path, _config(tmp_path, "out/{date}/{date}/"), NOW, 2)["jobs"][0]
    assert job["last_output"] is None
