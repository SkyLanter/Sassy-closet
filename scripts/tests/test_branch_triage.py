"""Piece 228: scripts/branch_triage.py classifies branches A-E on a throwaway repo."""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import branch_triage as bt  # noqa: E402

ENV = {"GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t",
       "GIT_COMMITTER_EMAIL": "t@t", "GIT_CONFIG_GLOBAL": "/dev/null"}

GUARD = "def blocked(ma):\n    return ma in HELD or ma == 'S06'\n"
TEST = "from guard import blocked\n\ndef test_held():\n    assert blocked('S06')\n"


def git(repo: Path, *args: str) -> str:
    return subprocess.run(["git", *args], cwd=repo, env={**os.environ, **ENV}, check=True,
                          capture_output=True, text=True).stdout.strip()


def put(repo: Path, rel: str, body: str, msg: str) -> str:
    p = repo / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(body)
    git(repo, "add", rel)
    git(repo, "commit", "-qm", msg)
    return git(repo, "rev-parse", "HEAD")


def branch(repo: Path, name: str, start: str = "main") -> None:
    git(repo, "checkout", "-q", "-b", name, start)


def build(tmp: Path):
    repo = tmp / "repo"
    repo.mkdir()
    git(repo, "init", "-q", "-b", "main")
    put(repo, "guard.py", "HELD = {'K93'}\n\ndef blocked(ma):\n    return ma in HELD\n", "base")
    put(repo, "tests/test_base.py", "def test_ok():\n    assert True\n", "base test")
    branch(repo, "piece-1-new-guard")
    put(repo, "guard.py", "HELD = {'K93'}\n\n" + GUARD, "piece 1: block S06")
    put(repo, "tests/test_s06.py", TEST, "piece 1: test")
    branch(repo, "piece-2-tests-only", "main")
    put(repo, "tests/test_more.py", "from guard import blocked\n\ndef test_k93():\n    assert blocked('K93')\n", "piece 2")
    branch(repo, "piece-3-picked", "main")
    picked = put(repo, "notes.py", "X = 1\n", "piece 3: notes")
    branch(repo, "piece-4-loosen", "main")
    put(repo, "guard.py", "HELD = set()\n\ndef blocked(ma):\n    return False\n", "piece 4: drop held check")
    branch(repo, "piece-5-feature", "main")
    put(repo, "report.py", "def report():\n    return 'hi'\n", "piece 5: report tool")
    branch(repo, "combined", "main")
    git(repo, "cherry-pick", picked)
    base = git(repo, "rev-parse", "HEAD")
    git(repo, "checkout", "-q", "main")
    return repo, base


def hook(cmd_ok):
    """Test hook: run the trial tree's own tests with python -m pytest."""
    def run(tree: Path, mode: str, files: list[str]) -> bool:
        tests = [f for f in files if f.startswith("tests/")] or ["tests"]
        r = subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", *tests],
                           cwd=tree, capture_output=True, text=True)
        return r.returncode == 0
    return run


def test_classes(tmp_path):
    repo, base = build(tmp_path)
    got = {b: bt.classify_branch(repo, b, base, test_hook=hook(True), scratch=tmp_path / "trial")
           for b in ["piece-1-new-guard", "piece-2-tests-only", "piece-3-picked", "piece-4-loosen", "piece-5-feature"]}
    assert got["piece-1-new-guard"]["cls"] == "A", got["piece-1-new-guard"]
    assert got["piece-1-new-guard"]["tests_only"] is False and got["piece-1-new-guard"]["full"] is True
    assert got["piece-2-tests-only"]["cls"] == "B", got["piece-2-tests-only"]
    assert got["piece-3-picked"]["cls"] == "C", got["piece-3-picked"]
    assert got["piece-4-loosen"]["cls"] == "D", got["piece-4-loosen"]
    assert any("held" in r for r in got["piece-4-loosen"]["reasons"])
    assert got["piece-5-feature"]["cls"] == "E", got["piece-5-feature"]
    for r in got.values():
        assert r["reasons"]


def test_read_only(tmp_path):
    repo, base = build(tmp_path)
    before = git(repo, "for-each-ref")
    wts = git(repo, "worktree", "list")
    bt.classify_branch(repo, "piece-1-new-guard", base, test_hook=hook(True), scratch=tmp_path / "trial")
    assert git(repo, "for-each-ref") == before
    assert git(repo, "worktree", "list") == wts
    assert not git(repo, "status", "--porcelain")
    assert not any((tmp_path / "trial").glob("*"))


def test_privacy_leak_is_d(tmp_path):
    repo, base = build(tmp_path)
    branch(repo, "piece-6-leak", "main")
    put(repo, "notes.md", "contact " + "someone" + "@" + "example.com\n", "piece 6")
    assert bt.classify_branch(repo, "piece-6-leak", base)["cls"] == "D"
