#!/usr/bin/env python3
"""Read-only merge readiness for open draft pull requests.

Prints each draft's conflict state against the base branch and whether the
hard-recheck check passed on that commit. Reads `gh pr list` or a fixture.
Does not merge, comment, or push.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from pathlib import Path

_REPO = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
_SHA = re.compile(r"^[0-9a-fA-F]{7,40}$")
_STATE = re.compile(r"^[A-Z][A-Z_]{0,31}$")
_URL = re.compile(r"^https://github\.com/[A-Za-z0-9._~:/?#@!$&'()*+,;=%-]+$")
_TOKEN = re.compile(
    r"(?:gh[pousr]_|github_pat_)(?:\s*[A-Za-z0-9_]+)?",
    re.IGNORECASE,
)
_FAIL = frozenset({"FAILURE", "CANCELLED", "TIMED_OUT", "STARTUP_FAILURE", "ACTION_REQUIRED", "ERROR"})
_RUNNING = frozenset({"QUEUED", "IN_PROGRESS", "PENDING", "WAITING", "REQUESTED"})
_CLEAR_STATES = frozenset({"CLEAN", "UNSTABLE", "BEHIND", "BLOCKED", "DRAFT", "HAS_HOOKS"})
_DEFAULT_REPO = "SkyLanter/Sassy-closet"
_DEFAULT_LIMIT = 200
_MAX_LIMIT = 500

Runner = Callable[..., subprocess.CompletedProcess[str]]


@dataclass(frozen=True)
class Row:
    number: int
    title: str
    url: str
    sha: str
    conflicts: str
    recheck: str
    state: str


def merge_word(value: object) -> str:
    if value is True:
        return "MERGEABLE"
    if value is False:
        return "CONFLICTING"
    if not isinstance(value, str):
        return ""
    text = value.strip().upper()
    if text in {"TRUE", "MERGEABLE"}:
        return "MERGEABLE"
    if text in {"FALSE", "CONFLICTING"}:
        return "CONFLICTING"
    if text == "UNKNOWN":
        return "UNKNOWN"
    return ""


def state_token(value: object) -> str:
    if not isinstance(value, str):
        return ""
    text = value.strip().upper()
    if not _STATE.fullmatch(text):
        return ""
    return text


def safe_url(value: object) -> str:
    if not isinstance(value, str) or not _URL.fullmatch(value):
        return ""
    return value


def conflict_state(mergeable: object, merge_state: object) -> str:
    state = state_token(merge_state)
    word = merge_word(mergeable)
    if state == "DIRTY" or word == "CONFLICTING":
        return "yes"
    if word == "MERGEABLE":
        return "no"
    if state in _CLEAR_STATES:
        return "unknown"
    return "unknown"


def _hard_recheck(check: dict[str, object]) -> bool:
    workflow = check.get("workflowName")
    name = check.get("name") if isinstance(check.get("name"), str) else ""
    context = check.get("context") if isinstance(check.get("context"), str) else ""
    label = name or context
    if isinstance(workflow, str) and workflow == "hard-recheck":
        return True
    return label == "hard-recheck" or label.startswith("hard-recheck/") or label.startswith("hard-recheck ")


def recheck_state(checks: object) -> str:
    if checks is None:
        return "NONE"
    if not isinstance(checks, list):
        return "UNKNOWN"
    found: list[dict[str, object]] = []
    for item in checks:
        if isinstance(item, dict) and _hard_recheck(item):
            found.append(item)
    if not found:
        return "NONE"
    saw_pass = False
    saw_unknown = False
    running = False
    for item in found:
        status = item.get("status")
        status_text = status.strip().upper() if isinstance(status, str) else ""
        conclusion = item.get("conclusion")
        if not isinstance(conclusion, str) or not conclusion.strip():
            conclusion = item.get("state") if isinstance(item.get("state"), str) else ""
        conclusion_text = conclusion.strip().upper()
        if conclusion_text in _FAIL:
            return "FAIL"
        if status_text in _RUNNING or conclusion_text in _RUNNING:
            running = True
            continue
        if conclusion_text == "SUCCESS" and status_text in {"", "COMPLETED"}:
            saw_pass = True
            continue
        if conclusion_text in {"SKIPPED", "NEUTRAL", "STALE"}:
            continue
        saw_unknown = True
    if running:
        return "RUNNING"
    if saw_unknown:
        return "UNKNOWN"
    if saw_pass:
        return "PASS"
    return "NONE"


def rows_from_payload(payload: object) -> tuple[tuple[Row, ...], str | None]:
    if not isinstance(payload, list):
        return (), "gh JSON must be a list"
    rows: list[Row] = []
    seen: set[int] = set()
    for item in payload:
        if not isinstance(item, dict):
            return (), "gh row was not an object"
        if item.get("isDraft") is False:
            continue
        number = item.get("number")
        if isinstance(number, bool) or not isinstance(number, int) or number < 1:
            return (), "gh row needs a pull request number"
        if number in seen:
            continue
        seen.add(number)
        title = item.get("title")
        url = item.get("url")
        sha = item.get("headRefOid")
        state = item.get("mergeStateStatus")
        rows.append(
            Row(
                number=number,
                title=_one_line(title if isinstance(title, str) else ""),
                url=safe_url(url),
                sha=sha[:7] if isinstance(sha, str) and _SHA.match(sha) else "",
                conflicts=conflict_state(item.get("mergeable"), state),
                recheck=recheck_state(item.get("statusCheckRollup")),
                state=state_token(state),
            )
        )
    rows.sort(key=lambda row: row.number)
    return tuple(rows), None


def render(rows: Sequence[Row], *, truncated: bool) -> str:
    conflicts = sum(1 for row in rows if row.conflicts == "yes")
    passed = sum(1 for row in rows if row.recheck == "PASS")
    noun = "draft" if len(rows) == 1 else "drafts"
    lines = [f"Merge readiness  {len(rows)} {noun}  conflicts {conflicts}  hard-recheck PASS {passed}"]
    if truncated:
        lines.append("List stopped at the requested limit.")
    for row in rows:
        sha = f"  {row.sha}" if row.sha else ""
        title = f"  {row.title}" if row.title else ""
        lines.append(
            f"#{row.number}  conflicts={row.conflicts}  recheck={row.recheck}  {row.state or '-'}{sha}{title}"
        )
        if row.url:
            lines.append(f"  {row.url}")
    lines.append("Read-only. No merges.")
    return "\n".join(lines) + "\n"


def gh_command(repo: str, limit: int) -> list[str]:
    return [
        "gh",
        "pr",
        "list",
        "--repo",
        repo,
        "--state",
        "open",
        "--draft",
        "--limit",
        str(limit),
        "--json",
        "number,title,url,isDraft,mergeable,mergeStateStatus,headRefOid,statusCheckRollup",
    ]


def load_gh(repo: str, limit: int, runner: Runner | None = None) -> tuple[object, str | None]:
    run = runner or subprocess.run
    try:
        completed = run(gh_command(repo, limit), text=True, capture_output=True, check=False)
    except OSError as error:
        detail = "gh not found" if isinstance(error, FileNotFoundError) else error.__class__.__name__
        return None, detail
    if completed.returncode != 0:
        return None, _safe(completed.stderr or completed.stdout or "gh failed")
    try:
        return json.loads(completed.stdout), None
    except json.JSONDecodeError:
        return None, "gh JSON did not parse"


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Read-only draft merge readiness. Does not merge.")
    parser.add_argument("--repo", default=_DEFAULT_REPO)
    parser.add_argument("--limit", type=int, default=_DEFAULT_LIMIT)
    parser.add_argument("--fixture", type=Path)
    args = parser.parse_args(list(argv) if argv is not None else None)
    if not _REPO.match(args.repo):
        print("usage: --repo owner/name", file=sys.stderr)
        return 2
    if args.limit < 1 or args.limit > _MAX_LIMIT:
        print(f"usage: --limit 1..{_MAX_LIMIT}", file=sys.stderr)
        return 2
    if args.fixture is not None:
        try:
            payload = json.loads(args.fixture.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as error:
            print(f"fixture: {error.__class__.__name__}", file=sys.stderr)
            return 1
        truncated = isinstance(payload, list) and len(payload) >= args.limit
    else:
        payload, error = load_gh(args.repo, args.limit)
        if error:
            print(error, file=sys.stderr)
            return 1
        truncated = isinstance(payload, list) and len(payload) >= args.limit
    rows, error = rows_from_payload(payload)
    if error:
        print(error, file=sys.stderr)
        return 1
    print(render(rows, truncated=truncated), end="")
    return 0


def _one_line(value: str) -> str:
    chars = []
    for ch in value:
        code = ord(ch)
        if code < 32 or code == 127 or 128 <= code <= 159:
            chars.append(" ")
        else:
            chars.append(ch)
    return " ".join("".join(chars).split())[:72]


def _safe(value: str) -> str:
    return " ".join(_TOKEN.sub("redacted", value).split())[:160]


if __name__ == "__main__":
    raise SystemExit(main())
