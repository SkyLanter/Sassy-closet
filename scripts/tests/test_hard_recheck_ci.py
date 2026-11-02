"""CI gate: hard recheck on pull requests, with no required SKIP."""
from __future__ import annotations

import json
import os
import stat
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
ASSERT = ROOT / "scripts" / "assert_hard_recheck_complete.py"
RUNNER = ROOT / "scripts" / "run_hard_recheck_ci.sh"
WORKFLOW = ROOT / ".github" / "workflows" / "hard-recheck.yml"

REQUIRED = (
    "git",
    "pytest",
    "privacy",
    "intake-npm-test",
    "intake-tsc",
    "shop-npm-test",
    "shop-tsc",
    "held-json",
)


def _step(name: str, status: str = "PASS", required: bool = False) -> dict:
    return {
        "step": name,
        "required": required or name in REQUIRED,
        "status": status,
        "exit": 0,
        "seconds": 1,
        "detail": "",
        "note": "",
    }


def _doc(steps: list[dict], result: str = "PASS") -> dict:
    return {
        "branch": "t",
        "head": "abc",
        "base": "origin/main",
        "total_seconds": 1,
        "result": result,
        "steps": steps,
    }


def _passing() -> dict:
    steps = [_step(name, "PASS", True) for name in REQUIRED]
    steps.append(_step("guard:example.py", "SKIP", False))
    steps.append(_step("working-tree", "WARN", False))
    steps.append(_step("tip-status", "INFO", False))
    return _doc(steps)


def _run_assert(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["python3", str(ASSERT), *args],
        capture_output=True,
        text=True,
        check=False,
    )


def test_pass_allows_optional_skip_warn_info(tmp_path: Path) -> None:
    path = tmp_path / "summary.json"
    path.write_text(json.dumps(_passing()), encoding="utf-8")
    got = _run_assert(str(path))
    assert got.returncode == 0, got.stdout + got.stderr
    assert "HARD RECHECK COMPLETE: PASS" in got.stdout
    assert "SKIP=1" in got.stdout and "WARN=1" in got.stdout and "INFO=1" in got.stdout


def test_required_skip_fails_even_when_result_says_pass(tmp_path: Path) -> None:
    doc = _passing()
    for step in doc["steps"]:
        if step["step"] == "intake-npm-test":
            step["status"] = "SKIP"
            step["note"] = "node_modules missing"
    path = tmp_path / "summary.json"
    path.write_text(json.dumps(doc), encoding="utf-8")
    got = _run_assert(str(path))
    assert got.returncode == 1
    assert "intake-npm-test" in got.stdout and "SKIP" in got.stdout


def test_missing_required_step_fails(tmp_path: Path) -> None:
    doc = _passing()
    doc["steps"] = [s for s in doc["steps"] if s["step"] != "held-json"]
    path = tmp_path / "summary.json"
    path.write_text(json.dumps(doc), encoding="utf-8")
    got = _run_assert(str(path))
    assert got.returncode == 1 and "held-json: missing" in got.stdout


def test_result_fail_and_extra_required_step(tmp_path: Path) -> None:
    doc = _passing()
    doc["result"] = "FAIL"
    doc["steps"].append(_step("privacy-extra", "FAIL", True))
    path = tmp_path / "summary.json"
    path.write_text(json.dumps(doc), encoding="utf-8")
    got = _run_assert(str(path))
    assert got.returncode == 1
    assert "not PASS" in got.stdout and "privacy-extra" in got.stdout


def test_latest_picks_newest_file(tmp_path: Path) -> None:
    older = tmp_path / "20200101-000000-1"
    newer = tmp_path / "20200101-000000-2"
    older.mkdir()
    newer.mkdir()
    (older / "summary.json").write_text(json.dumps(_doc([_step("git", "FAIL", True)], "FAIL")), encoding="utf-8")
    (newer / "summary.json").write_text(json.dumps(_passing()), encoding="utf-8")
    os.utime(older / "summary.json", (1_000_000_000, 1_000_000_000))
    os.utime(newer / "summary.json", (1_900_000_000, 1_900_000_000))
    got = _run_assert("--latest", str(tmp_path))
    assert got.returncode == 0, got.stdout + got.stderr
    assert "20200101-000000-2" in got.stdout


def test_bad_usage_missing_and_broken_json(tmp_path: Path) -> None:
    assert _run_assert().returncode == 2
    assert _run_assert(str(tmp_path / "nope.json")).returncode == 2
    bad = tmp_path / "summary.json"
    bad.write_text("{", encoding="utf-8")
    assert _run_assert(str(bad)).returncode == 2
    empty = tmp_path / "empty"
    empty.mkdir()
    assert _run_assert("--latest", str(empty)).returncode == 2


def _git(repo: Path, *args: str) -> None:
    subprocess.run(
        ["git", *args],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
        env={
            **os.environ,
            "GIT_AUTHOR_NAME": "t",
            "GIT_AUTHOR_EMAIL": "t@t",
            "GIT_COMMITTER_NAME": "t",
            "GIT_COMMITTER_EMAIL": "t@t",
        },
    )


def _copy_runner(repo: Path) -> None:
    dest = repo / "scripts" / "run_hard_recheck_ci.sh"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(RUNNER.read_bytes())
    dest.chmod(dest.stat().st_mode | stat.S_IXUSR)


def _init_repo(repo: Path) -> None:
    _copy_runner(repo)
    _git(repo, "init", "-q", "-b", "main")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-qm", "base")


def test_runner_refuses_missing_origin_main(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _init_repo(repo)
    got = subprocess.run(
        ["bash", str(repo / "scripts" / "run_hard_recheck_ci.sh")],
        capture_output=True,
        text=True,
        check=False,
    )
    assert got.returncode == 1
    assert "origin/main is missing" in got.stdout
    assert "hard_recheck.sh" not in got.stdout


def test_runner_refuses_missing_node_modules(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _init_repo(repo)
    subprocess.run(
        ["git", "update-ref", "refs/remotes/origin/main", "HEAD"],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    )
    got = subprocess.run(
        ["bash", str(repo / "scripts" / "run_hard_recheck_ci.sh")],
        capture_output=True,
        text=True,
        check=False,
    )
    assert got.returncode == 1
    assert "sassy-closet/node_modules is missing" in got.stdout


def test_runner_refuses_when_npm_is_absent(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _init_repo(repo)
    subprocess.run(
        ["git", "update-ref", "refs/remotes/origin/main", "HEAD"],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    )
    bindir = tmp_path / "bin"
    bindir.mkdir()
    git = bindir / "git"
    git.symlink_to("/usr/bin/git")
    got = subprocess.run(
        ["/bin/bash", str(repo / "scripts" / "run_hard_recheck_ci.sh")],
        capture_output=True,
        text=True,
        check=False,
        env={**os.environ, "PATH": str(bindir)},
    )
    assert got.returncode == 1
    assert "npm is not installed" in got.stdout


def test_workflow_is_read_only_pr_gate() -> None:
    text = WORKFLOW.read_text(encoding="utf-8")
    assert "pull_request:" in text
    assert "workflow_dispatch:" in text
    assert "pull_request_target" not in text
    assert "schedule:" not in text
    assert "permissions:\n  contents: read\n" in text
    assert "persist-credentials: false" in text
    assert "fetch-depth: 0" in text
    assert "working-directory: sassy-closet\n" in text
    assert "working-directory: sassy-closet-shop\n" in text
    assert text.count("run: npm ci") == 2
    assert "bash scripts/run_hard_recheck_ci.sh" in text
    assert "HARD_RECHECK_PYTHON: python" in text
    assert "secrets." not in text
    for bad in ("git push", "gh pr", "vercel", "BLOB_", "META_", "SQUARE", "held.json", ": write"):
        assert bad not in text, bad


@pytest.mark.parametrize("needle", [
    "--base origin/main",
    "--json",
    "assert_hard_recheck_complete.py",
    'for app in sassy-closet sassy-closet-shop; do',
    '"$app/node_modules"',
])
def test_runner_invokes_recheck_with_base_and_no_skip_gate(needle: str) -> None:
    text = RUNNER.read_text(encoding="utf-8")
    assert needle in text


def _ready_fake(repo: Path, stub: str) -> None:
    _init_repo(repo)
    subprocess.run(
        ["git", "update-ref", "refs/remotes/origin/main", "HEAD"],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    )
    for app in ("sassy-closet", "sassy-closet-shop"):
        (repo / app / "node_modules").mkdir(parents=True)
    (repo / "scripts" / "assert_hard_recheck_complete.py").write_bytes(ASSERT.read_bytes())
    dest = repo / "scripts" / "hard_recheck.sh"
    dest.write_text(stub, encoding="utf-8")
    dest.chmod(dest.stat().st_mode | stat.S_IXUSR)


def test_runner_fails_closed_when_recheck_passes_with_required_skip(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    doc = _passing()
    for step in doc["steps"]:
        if step["step"] == "shop-tsc":
            step["status"] = "SKIP"
            step["note"] = "npm not installed"
    body = json.dumps(doc)
    _ready_fake(
        repo,
        "#!/bin/bash\nmkdir -p out/recheck/stamp\ncat > out/recheck/stamp/summary.json << 'EOF'\n"
        + body
        + "\nEOF\nexit 0\n",
    )
    got = subprocess.run(
        ["bash", str(repo / "scripts" / "run_hard_recheck_ci.sh")],
        cwd=repo,
        capture_output=True,
        text=True,
        check=False,
    )
    assert got.returncode == 1, got.stdout + got.stderr
    assert "HARD RECHECK CI: FAIL (recheck=0 assert=1)" in got.stdout
    assert "shop-tsc" in got.stdout


def test_runner_passes_when_stub_recheck_is_complete(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    body = json.dumps(_passing())
    _ready_fake(
        repo,
        "#!/bin/bash\nmkdir -p out/recheck/stamp\ncat > out/recheck/stamp/summary.json << 'EOF'\n"
        + body
        + "\nEOF\nexit 0\n",
    )
    got = subprocess.run(
        ["bash", str(repo / "scripts" / "run_hard_recheck_ci.sh")],
        cwd=repo,
        capture_output=True,
        text=True,
        check=False,
    )
    assert got.returncode == 0, got.stdout + got.stderr
    assert "HARD RECHECK CI: PASS" in got.stdout
