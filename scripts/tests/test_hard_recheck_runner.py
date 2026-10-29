"""Piece 219: scripts/hard_recheck.sh against a tiny fake repo (fast, no network)."""
from __future__ import annotations

import json
import os
import shutil
import stat
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "hard_recheck.sh"


def _x(path: Path, body: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")
    path.chmod(path.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)


def _git(repo: Path, *args: str) -> str:
    return subprocess.run(["git", *args], cwd=repo, check=True, capture_output=True, text=True,
                          env={**os.environ, "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t",
                               "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t"}).stdout.strip()


@pytest.fixture
def fake(tmp_path: Path):
    repo = tmp_path / "repo"
    (repo / "scripts").mkdir(parents=True)
    shutil.copy(SCRIPT, repo / "scripts" / "hard_recheck.sh")
    _x(repo / "scripts" / "run_tests.sh",
       '#!/usr/bin/env bash\nif [ -f "$(dirname "$0")/../FAIL_PYTEST" ]; then echo "== 2 failed, 8 passed, 1 skipped in 0.1s =="; exit 1; fi\n'
       'echo "== 10 passed, 1 skipped in 0.1s =="\n')
    _x(repo / "scripts" / "privacy_scan.py", 'print("privacy_scan: CLEAN")\n')
    (repo / "data").mkdir()
    (repo / "data" / "held.json").write_text('{"heldIncomplete": ["K93"], "neverList": []}\n')
    (repo / ".gitignore").write_text("out/\nnode_modules/\n")
    for app in ("sassy-closet", "sassy-closet-shop"):
        (repo / app).mkdir()
        (repo / app / "package.json").write_text('{"name": "x"}\n')
        (repo / app / "node_modules").mkdir()
    shim = tmp_path / "bin"
    _x(shim / "npm", '#!/usr/bin/env bash\necho "# tests 5"\necho "# pass 5"\necho "# fail 0"\necho "# skipped 0"\n')
    _x(shim / "npx", '#!/usr/bin/env bash\nexit 0\n')
    _git(repo, "init", "-q", "-b", "main")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-qm", "base")
    base = _git(repo, "rev-parse", "HEAD")
    env = {**os.environ, "PATH": f"{shim}:{os.environ['PATH']}", "HARD_RECHECK_PYTHON": "python3"}
    return repo, base, env


def run(repo: Path, base: str, env: dict, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["bash", str(repo / "scripts" / "hard_recheck.sh"), "--base", base, *args],
                          cwd="/", env=env, capture_output=True, text=True, timeout=120)


def latest(repo: Path) -> Path:
    return sorted((repo / "out" / "recheck").iterdir())[-1]


def test_help_exits_zero():
    r = subprocess.run(["bash", str(SCRIPT), "--help"], capture_output=True, text=True)
    assert r.returncode == 0 and "hard_recheck.sh" in r.stdout


def test_all_pass(fake):
    repo, base, env = fake
    r = run(repo, base, env)
    assert r.returncode == 0, r.stdout + r.stderr
    assert "HARD RECHECK: PASS" in r.stdout
    summary = (latest(repo) / "summary.txt").read_text()
    assert "10 passed" in summary and "1 skipped" in summary
    assert "conflict markers 0" in summary and "held.json unchanged: yes" in summary


def test_failing_pytest_fails_but_others_run(fake):
    repo, base, env = fake
    (repo / "FAIL_PYTEST").write_text("x")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-qm", "fail")
    r = run(repo, base, env, "--json")
    assert r.returncode != 0
    assert "HARD RECHECK: FAIL" in r.stdout
    doc = json.loads((latest(repo) / "summary.json").read_text())
    by = {s["step"]: s for s in doc["steps"]}
    assert by["pytest"]["status"] == "FAIL"
    assert by["privacy"]["status"] == "PASS" and by["shop-npm-test"]["status"] == "PASS"
    assert doc["result"] == "FAIL"


def test_missing_node_modules_skips(fake):
    repo, base, env = fake
    shutil.rmtree(repo / "sassy-closet" / "node_modules")
    r = run(repo, base, env, "--json")
    assert r.returncode == 0, r.stdout
    by = {s["step"]: s for s in json.loads((latest(repo) / "summary.json").read_text())["steps"]}
    assert by["intake-npm-test"]["status"] == "SKIP" and by["intake-tsc"]["status"] == "SKIP"
    assert "node_modules missing" in by["intake-npm-test"]["note"]


def test_conflict_marker_flagged(fake):
    repo, base, env = fake
    (repo / "x.txt").write_text("a\n<<<<<<< HEAD\nb\n=======\nc\n>>>>>>> other\n")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-qm", "marker")
    r = run(repo, base, env)
    assert r.returncode != 0 and "conflict markers 3" in r.stdout


def test_held_json_change_detected(fake):
    repo, base, env = fake
    (repo / "data" / "held.json").write_text('{"heldIncomplete": [], "neverList": []}\n')
    _git(repo, "commit", "-qam", "held")
    r = run(repo, base, env)
    assert r.returncode != 0 and "held.json unchanged: no" in r.stdout


def test_node_modules_link_is_noted_not_failed(fake):
    repo, base, env = fake
    shutil.rmtree(repo / "sassy-closet" / "node_modules")
    (repo / "sassy-closet" / "node_modules").symlink_to(repo / "sassy-closet-shop" / "node_modules")
    r = run(repo, base, env)
    assert r.returncode == 0, r.stdout
    assert "node_modules link (ignored)" in r.stdout
