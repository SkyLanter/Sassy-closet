"""Piece 85 placeholder tests: git-tracked inputs use last commit time (temp git repo only)."""
import datetime as dt
import os
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import daily_summary_draft as d  # noqa: E402

NOW = dt.datetime(2026, 1, 2, 12, 0, tzinfo=dt.timezone.utc)
COMMIT = "2026-01-02T03:00:00+00:00"  # 2026-01-01 19:00 PST


def _git(repo, *args):
    env = dict(os.environ, GIT_AUTHOR_DATE=COMMIT, GIT_COMMITTER_DATE=COMMIT,
               GIT_AUTHOR_NAME="t", GIT_COMMITTER_NAME="t",
               GIT_AUTHOR_EMAIL="t", GIT_COMMITTER_EMAIL="t")
    subprocess.run(["git", *args], cwd=repo, env=env, check=True, capture_output=True)


def _repo(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-q")
    f = repo / "order.json"
    f.write_text("[]\n")
    _git(repo, "add", "order.json")
    _git(repo, "commit", "-q", "-m", "placeholder")
    t = (NOW - dt.timedelta(minutes=5)).timestamp()
    os.utime(f, (t, t))  # fresh checkout mtime must be ignored
    return repo, f


def test_tracked_uses_last_commit(tmp_path):
    _, f = _repo(tmp_path)
    L = d.freshness_lines([("Order", f)], now=NOW)
    assert L[1] == "- Order: OK, order.json last commit 2026-01-01 19:00 PT"


def test_tracked_old_commit_is_stale(tmp_path):
    _, f = _repo(tmp_path)
    later = NOW + dt.timedelta(days=2)
    assert d.freshness_lines([("Order", f)], now=later)[1].startswith("- Order: STALE, order.json last commit ")


def test_untracked_in_repo_uses_file_time(tmp_path):
    repo, _ = _repo(tmp_path)
    u = repo / "scratch.json"
    u.write_text("{}\n")
    t = (NOW - dt.timedelta(hours=1)).timestamp()
    os.utime(u, (t, t))
    assert d.freshness_lines([("U", u)], now=NOW)[1] == "- U: OK, scratch.json file time 2026-01-02 03:00 PT"


def test_no_repo_uses_file_time(tmp_path):
    f = tmp_path / "plain.json"
    f.write_text("{}\n")
    assert d.git_commit_time(f) is None
    assert " file time " in d.freshness_lines([("P", f)], now=NOW)[1]


def test_header_labels(tmp_path):
    h = d.freshness_lines([], now=NOW)[0]
    assert "last commit" in h and "file time" in h and "PT" in h
