#!/usr/bin/env python3
"""Fail unless a hard_recheck summary.json passed with every required step PASS.

hard_recheck.sh treats a required SKIP as an overall PASS. CI must not.
A step in REQUIRED that is missing or not PASS fails. Any other step marked
required fails unless it is PASS. Optional SKIP / WARN / INFO are allowed.

Usage:
  scripts/assert_hard_recheck_complete.py summary.json
  scripts/assert_hard_recheck_complete.py --latest out/recheck
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

# Names hard_recheck.sh records with required=1. Kept here so a summary that
# omits one (or marks it SKIP) cannot pass this gate.
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

STATUS_ORDER = ("PASS", "FAIL", "SKIP", "WARN", "INFO")


def newest_summary(directory: Path) -> Path:
    found = [p for p in directory.glob("*/summary.json") if p.is_file()]
    if not found:
        raise FileNotFoundError(f"no summary.json under {directory}")
    found.sort(key=lambda p: (p.stat().st_mtime, p.as_posix()))
    return found[-1]


def problems(doc: dict) -> list[str]:
    steps = doc.get("steps")
    if not isinstance(steps, list) or not steps:
        return ["summary has no steps"]
    out: list[str] = []
    if doc.get("result") != "PASS":
        out.append(f"result {doc.get('result')!r} is not PASS")
    by: dict[str, dict] = {}
    seen: list[str] = []
    for step in steps:
        if not isinstance(step, dict) or not isinstance(step.get("step"), str):
            out.append("step is not an object with a name")
            continue
        name = step["step"]
        if name in by:
            out.append(f"{name}: duplicated")
        by[name] = step
        seen.append(name)
    reported: set[str] = set()
    for name in REQUIRED:
        step = by.get(name)
        if step is None:
            out.append(f"{name}: missing")
            reported.add(name)
            continue
        if step.get("status") != "PASS":
            out.append(_status_line(step))
            reported.add(name)
    for name in seen:
        step = by[name]
        if name in reported:
            continue
        if step.get("required") is True and step.get("status") != "PASS":
            out.append(_status_line(step))
    return out


def _status_line(step: dict) -> str:
    note = step.get("note") or ""
    extra = f" ({note})" if note else ""
    return f"{step.get('step')}: status {step.get('status')!r}{extra}"


def counts(doc: dict) -> str:
    tally: dict[str, int] = {}
    for step in doc.get("steps") or []:
        if isinstance(step, dict):
            status = str(step.get("status"))
            tally[status] = tally.get(status, 0) + 1
    parts = [f"{name}={tally[name]}" for name in STATUS_ORDER if name in tally]
    extra = [f"{name}={tally[name]}" for name in sorted(tally) if name not in STATUS_ORDER]
    return " ".join(parts + extra)


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if len(args) == 2 and args[0] == "--latest":
        try:
            path = newest_summary(Path(args[1]))
        except FileNotFoundError as err:
            print(f"FAIL {err}", file=sys.stderr)
            return 2
    elif len(args) == 1 and not args[0].startswith("-"):
        path = Path(args[0])
    else:
        print(
            "usage: assert_hard_recheck_complete.py summary.json | --latest out/recheck",
            file=sys.stderr,
        )
        return 2
    if not path.is_file():
        print(f"FAIL missing {path}", file=sys.stderr)
        return 2
    try:
        doc = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as err:
        print(f"FAIL {path}: {err}", file=sys.stderr)
        return 2
    if not isinstance(doc, dict):
        print(f"FAIL {path}: summary is not an object", file=sys.stderr)
        return 2
    print(f"hard recheck summary {path} result={doc.get('result')} {counts(doc)}")
    bad = problems(doc)
    if bad:
        for line in bad:
            print(f"FAIL {line}")
        return 1
    print("HARD RECHECK COMPLETE: PASS (no required SKIP)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
