"""Piece 227: scripts/branch_inventory.sh on a throwaway git repo (no network, no real repo writes)."""
from __future__ import annotations

import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "branch_inventory.sh"
ENV = {**os.environ, "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t",
       "GIT_COMMITTER_EMAIL": "t@t", "GIT_CONFIG_GLOBAL": "/dev/null"}


def git(repo: Path, *args: str) -> str:
    return subprocess.run(["git", *args], cwd=repo, env=ENV, check=True, capture_output=True, text=True).stdout.strip()


def commit(repo: Path, name: str, body: str, msg: str) -> None:
    (repo / name).write_text(body)
    git(repo, "add", name)
    git(repo, "commit", "-qm", msg)


def build(tmp: Path):
    repo = tmp / "repo"
    repo.mkdir()
    git(repo, "init", "-q", "-b", "main")
    commit(repo, "base.txt", "base\n", "base")
    git(repo, "checkout", "-qb", "piece-1-merged")
    commit(repo, "a.txt", "a\n", "piece 1: add a")
    git(repo, "checkout", "-q", "main")
    git(repo, "checkout", "-qb", "piece-2-missing")
    commit(repo, "b.txt", "b\n", "piece 2: add b")
    git(repo, "checkout", "-q", "main")
    git(repo, "checkout", "-qb", "piece-3-picked")
    commit(repo, "c.txt", "c\n", "piece 3: add c")
    pick = git(repo, "rev-parse", "HEAD")
    git(repo, "checkout", "-q", "main")
    git(repo, "checkout", "-qb", "piece-4-combined-check")
    git(repo, "merge", "-q", "--no-ff", "--no-edit", "piece-1-merged")
    commit(repo, "other.txt", "x\n", "combined: unrelated")
    git(repo, "cherry-pick", pick)
    base = git(repo, "rev-parse", "HEAD")
    git(repo, "checkout", "-q", "main")
    wt = tmp / "wt-dirty"
    git(repo, "worktree", "add", "-q", str(wt), "piece-2-missing")
    (wt / "b.txt").write_text("edited\n")
    return repo, base, wt


def run(repo: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["bash", str(SCRIPT), *args], cwd=repo, env=ENV, capture_output=True, text=True, timeout=120)


def row(md: str, branch: str) -> str:
    return next(line for line in md.splitlines() if line.startswith(f"| {branch} |"))


def test_classification(tmp_path):
    repo, base, wt = build(tmp_path)
    out = tmp_path / "inv.md"
    r = run(repo, "--base", base, "--out", str(out), "--since", "main")
    assert r.returncode == 0, r.stderr
    md = out.read_text()
    assert "MERGED" in row(md, "piece-1-merged") and "UNMERGED" not in row(md, "piece-1-merged")
    assert "already in combined" in row(md, "piece-3-picked")
    assert "MISSING - needs merge" in row(md, "piece-2-missing")
    assert "| piece-4-combined-check |" in md
    summary = next(line for line in md.splitlines() if line.startswith("Summary:"))
    assert "branches 4" in summary and "merged 2" in summary and "unmerged 2" in summary
    assert "missing changes 1" in summary and "dirty worktrees 1" in summary
    assert str(wt) in md.split("## Worktrees", 1)[1]
    assert "piece-2-missing" in md.split("Suggested next step", 1)[1]
    assert git(wt, "status", "--porcelain")  # report only; dirty change left alone


def test_default_base_is_latest_combined(tmp_path):
    repo, base, _ = build(tmp_path)
    out = tmp_path / "inv.md"
    assert run(repo, "--out", str(out), "--since", "main").returncode == 0
    assert base[:7] in out.read_text().split("Summary:", 1)[0]


def test_help():
    assert subprocess.run(["bash", str(SCRIPT), "--help"], capture_output=True).returncode == 0
