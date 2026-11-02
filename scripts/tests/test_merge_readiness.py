"""Merge readiness: conflicts and hard-recheck, from a fixture. No live gh."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

import merge_readiness as mr  # noqa: E402

SCRIPT = ROOT / "scripts" / "merge_readiness.py"


def _pull(**over: object) -> dict[str, object]:
    row: dict[str, object] = {
        "number": 232,
        "title": "Run the hard recheck on pull requests",
        "url": "https://github.com/SkyLanter/Sassy-closet/pull/232",
        "isDraft": True,
        "mergeable": "MERGEABLE",
        "mergeStateStatus": "CLEAN",
        "headRefOid": "8b608ca5017d61060eb4732c4cd96fbc7947d04d",
        "statusCheckRollup": [],
    }
    row.update(over)
    return row


def _check(**over: object) -> dict[str, object]:
    row: dict[str, object] = {
        "name": "recheck",
        "workflowName": "hard-recheck",
        "status": "COMPLETED",
        "conclusion": "SUCCESS",
    }
    row.update(over)
    return row


def test_clean_hard_recheck_pass_is_not_a_conflict() -> None:
    rows, err = mr.rows_from_payload([_pull(statusCheckRollup=[_check()], mergeStateStatus="UNSTABLE")])
    assert err is None and len(rows) == 1
    assert rows[0].conflicts == "no"
    assert rows[0].recheck == "PASS"
    assert rows[0].sha == "8b608ca"
    assert rows[0].state == "UNSTABLE"


def test_dirty_and_boolean_conflicting() -> None:
    dirty, _ = mr.rows_from_payload([_pull(number=2, mergeable="MERGEABLE", mergeStateStatus="DIRTY")])
    flag, _ = mr.rows_from_payload([_pull(number=3, mergeable=False, mergeStateStatus="UNKNOWN")])
    assert dirty[0].conflicts == "yes"
    assert flag[0].conflicts == "yes"


def test_behind_is_not_a_conflict_and_unknown_stays_unknown() -> None:
    behind, _ = mr.rows_from_payload([_pull(mergeable="MERGEABLE", mergeStateStatus="BEHIND")])
    unknown, _ = mr.rows_from_payload([_pull(mergeable="UNKNOWN", mergeStateStatus="UNKNOWN")])
    assert behind[0].conflicts == "no"
    assert unknown[0].conflicts == "unknown"


def test_job_named_recheck_without_the_workflow_is_not_a_pass() -> None:
    rows, _ = mr.rows_from_payload([
        _pull(statusCheckRollup=[{"name": "recheck", "status": "COMPLETED", "conclusion": "SUCCESS"}])
    ])
    assert rows[0].recheck == "NONE"


def test_failure_beats_a_second_success_and_running_waits() -> None:
    failed, _ = mr.rows_from_payload([
        _pull(statusCheckRollup=[_check(), _check(conclusion="FAILURE")])
    ])
    running, _ = mr.rows_from_payload([
        _pull(statusCheckRollup=[_check(status="IN_PROGRESS", conclusion="")])
    ])
    hidden, _ = mr.rows_from_payload([
        _pull(statusCheckRollup=[_check(status="IN_PROGRESS", conclusion="FAILURE")])
    ])
    assert failed[0].recheck == "FAIL"
    assert running[0].recheck == "RUNNING"
    assert hidden[0].recheck == "FAIL"


def test_status_context_and_skipped_check() -> None:
    rows, _ = mr.rows_from_payload([
        _pull(statusCheckRollup=[{"context": "hard-recheck", "state": "ERROR"}])
    ])
    skipped, _ = mr.rows_from_payload([
        _pull(statusCheckRollup=[_check(conclusion="SKIPPED")])
    ])
    assert rows[0].recheck == "FAIL"
    assert skipped[0].recheck == "NONE"


def test_skips_ready_prs_bad_rows_and_title_newlines() -> None:
    payload = [
        _pull(number=9, isDraft=False, title="ready"),
        _pull(number=4, title="line\n  two  extra"),
        {"number": True, "isDraft": True},
    ]
    rows, err = mr.rows_from_payload(payload[:2])
    assert err is None and [row.number for row in rows] == [4]
    assert rows[0].title == "line two extra"
    bad, message = mr.rows_from_payload(payload)
    assert bad == () and message == "gh row needs a pull request number"


def test_smuggled_state_and_url_stay_one_row() -> None:
    rows, err = mr.rows_from_payload([
        _pull(
            number=8,
            mergeStateStatus="CLEAN\n#9  conflicts=no  recheck=PASS  deadbeef",
            url="https://github.com/a/b\njavascript:alert(1)",
        )
    ])
    assert err is None and len(rows) == 1
    text = mr.render(rows, truncated=False)
    assert text.count("#") == 1
    assert "javascript:" not in text
    assert "recheck=PASS" not in text
    assert rows[0].state == ""
    smuggled, _ = mr.rows_from_payload([
        _pull(url="https://github.com/a/b\r\nhttp://evil")
    ])
    assert smuggled[0].url == ""
    assert "http://evil" not in mr.render(smuggled, truncated=False)
    hidden, _ = mr.rows_from_payload([
        _pull(
            url="https://github.com/\x7fjavascript:alert(1)",
            title="ok\x7fjavascript\u009bname",
        )
    ])
    hidden_text = mr.render(hidden, truncated=False)
    assert hidden[0].url == ""
    assert "\x7f" not in hidden_text and "\u009b" not in hidden_text
    assert "javascript:" not in hidden_text


def test_other_workflow_name_is_not_a_pass() -> None:
    rows, _ = mr.rows_from_payload([
        _pull(statusCheckRollup=[_check(workflowName="hard-recheck-other", name="hard-recheck-other")])
    ])
    assert rows[0].recheck == "NONE"


def test_render_counts_and_drops_odd_urls() -> None:
    rows, _ = mr.rows_from_payload([
        _pull(number=1, url="javascript:alert(1)", statusCheckRollup=[_check()]),
        _pull(number=2, mergeStateStatus="DIRTY"),
    ])
    text = mr.render(rows, truncated=True)
    assert "2 drafts  conflicts 1  hard-recheck PASS 1" in text
    assert "List stopped at the requested limit." in text
    assert "javascript:" not in text
    assert "https://github.com/SkyLanter/Sassy-closet/pull/232" in text


def test_fixture_cli_does_not_need_gh(tmp_path: Path) -> None:
    path = tmp_path / "drafts.json"
    path.write_text(json.dumps([_pull()]), encoding="utf-8")
    got = subprocess.run(
        [sys.executable, str(SCRIPT), "--fixture", str(path)],
        capture_output=True,
        text=True,
        check=False,
        env={"PATH": "/usr/bin:/bin"},
    )
    assert got.returncode == 0, got.stderr
    assert "conflicts=no" in got.stdout and "recheck=NONE" in got.stdout
    assert got.stderr == ""


def test_usage_and_gh_command_is_read_only() -> None:
    assert mr.main(["--repo", "not a repo"]) == 2
    assert mr.main(["--limit", "0"]) == 2
    command = mr.gh_command("SkyLanter/Sassy-closet", 200)
    assert command[:4] == ["gh", "pr", "list", "--repo"]
    assert "--draft" in command and "--state" in command and "open" in command
    forbidden = {"merge", "comment", "close", "review", "checkout", "approve"}
    assert forbidden.isdisjoint(command)
    source = SCRIPT.read_text(encoding="utf-8")
    for bad in ("git push", "gh pr merge", "gh pr review", "gh pr close", "data/held.json"):
        assert bad not in source, bad


def test_gh_error_is_redacted_and_nonzero(tmp_path: Path) -> None:
    def runner(*_a: object, **_k: object) -> subprocess.CompletedProcess[str]:
        return subprocess.CompletedProcess(
            args=[], returncode=1, stdout="", stderr="bad ghp_abcdefghijklmnopqrstuvwxyz token"
        )

    payload, err = mr.load_gh("SkyLanter/Sassy-closet", 20, runner)
    assert payload is None and err is not None
    assert "ghp_" not in err and "redacted" in err

    def split_runner(*_a: object, **_k: object) -> subprocess.CompletedProcess[str]:
        return subprocess.CompletedProcess(
            args=[],
            returncode=1,
            stdout="",
            stderr="auth failed gho_1234567890abcdef ghs_abc ghu_abc ghr_abc bad ghp_\nsupersecrettoken tail",
        )

    _payload, split = mr.load_gh("SkyLanter/Sassy-closet", 20, split_runner)
    assert split is not None
    for needle in ("gho_", "ghs_", "ghu_", "ghr_", "ghp_", "supersecrettoken"):
        assert needle not in split
    assert split.count("redacted") >= 4
