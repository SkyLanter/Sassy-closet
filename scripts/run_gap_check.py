#!/usr/bin/env python3
"""Piece 38: read-only run-gap check — did each daily shop job leave its output?

Catches silent failures (e.g. Midnight QC Oct 17-19 left no folder at all).
Jobs come from data/run-gaps.json. For each job it reports:
  last_output   newest date (or mtime date) that has output
  missing       days in the last N (default 14) with no output
  stale         no output for "today" (job timezone) although it is past expected_hour
  half_written  zero-byte files, missing required files, or JSON that does not parse

Job kinds
  dated   pattern holds {date}; a dir (ends with '/') or a file per day
  single  one file that is rewritten daily; its mtime is the output date
  state   a state file (e.g. auto-list last_check.json) with an "at" ISO time;
          stale when older than max_age_hours. scan_dir is checked for
          zero-byte / *.tmp / *.partial files (zero_byte_ok globs excepted).

Output lists paths and dates only — never file contents (no costs, no customer data).
Never writes into --root. Exit: 0 OK, 1 gaps found (WARN), 2 usage/config error.
"""
from __future__ import annotations

import argparse
import fnmatch
import json
import os
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

DEFAULT_CONFIG = Path(__file__).resolve().parent.parent / "data" / "run-gaps.json"
PARTIAL_SUFFIXES = (".tmp", ".partial", ".part", ".swp")


def load_config(path: Path) -> list[dict]:
    cfg = json.loads(path.read_text(encoding="utf-8"))
    if cfg.get("schema") != "run-gaps/v1":
        raise ValueError(f"{path}: not a run-gaps/v1 config")
    jobs = cfg.get("jobs") or []
    for j in jobs:
        for k in ("name", "kind", "pattern", "timezone"):
            if k not in j:
                raise ValueError(f"job {j.get('name', '?')}: missing {k}")
        if j["kind"] not in ("dated", "single", "state"):
            raise ValueError(f"job {j['name']}: unknown kind {j['kind']}")
        if j["kind"] == "dated" and "{date}" not in j["pattern"]:
            raise ValueError(f"job {j['name']}: dated pattern needs {{date}}")
        ZoneInfo(j["timezone"])
    return jobs


def _zero_ok(name: str, globs: list[str]) -> bool:
    return any(fnmatch.fnmatch(name, g) for g in globs)


def _json_bad(p: Path) -> bool:
    try:
        json.loads(p.read_text(encoding="utf-8"))
        return False
    except Exception:  # noqa: BLE001
        return True


def _half_written(target: Path, job: dict, root: Path) -> list[str]:
    """Problems inside one output (dir or file). Paths are relative to root."""
    probs: list[str] = []
    ok = job.get("zero_byte_ok", [])
    rel = lambda p: os.path.relpath(p, root)  # noqa: E731
    if target.is_dir():
        for dp, _dn, fn in os.walk(target):
            for f in sorted(fn):
                fp = Path(dp) / f
                if f.endswith(PARTIAL_SUFFIXES):
                    probs.append(f"partial file {rel(fp)}")
                elif fp.stat().st_size == 0 and not _zero_ok(f, ok):
                    probs.append(f"zero-byte {rel(fp)}")
        for r in job.get("required", []):
            if not (target / r).exists():
                probs.append(f"missing required {rel(target / r)}")
        for jf in job.get("json_files", []):
            p = target / jf
            if p.exists() and p.stat().st_size > 0 and _json_bad(p):
                probs.append(f"bad JSON {rel(p)}")
    elif target.exists():
        if target.stat().st_size == 0 and not _zero_ok(target.name, ok):
            probs.append(f"zero-byte {rel(target)}")
    return probs


def _today(job: dict, now: datetime) -> tuple[date, bool]:
    local = now.astimezone(ZoneInfo(job["timezone"]))
    return local.date(), local.hour >= int(job.get("expected_hour", 0))


def check_dated(job: dict, root: Path, now: datetime, days: int) -> dict:
    today, past_hour = _today(job, now)
    off = timedelta(days=int(job.get("date_offset_days", 0)))
    expect_today = today + off
    window = [expect_today - timedelta(days=i) for i in range(days)]
    present, half = [], {}
    for d in window:
        t = root / job["pattern"].format(date=d.isoformat())
        if t.exists():
            present.append(d)
            pr = _half_written(t, job, root)
            if pr:
                half[d.isoformat()] = pr
    # last output over everything on disk (not only the window)
    pat = job["pattern"].rstrip("/")
    parent = (root / pat).parent
    pre, post = Path(pat).name.split("{date}")
    alld = []
    if parent.is_dir():
        for e in parent.iterdir():
            n = e.name
            if n.startswith(pre) and n.endswith(post) and len(n) == len(pre) + 10 + len(post):
                try:
                    alld.append(date.fromisoformat(n[len(pre):len(pre) + 10]))
                except ValueError:
                    pass
    last = max(alld) if alld else None
    missing = [d for d in window if d not in present]
    # today's slot only counts as missing once past the expected hour
    if expect_today in missing and not past_hour:
        missing.remove(expect_today)
    stale = past_hour and expect_today not in present
    return _result(job, last, sorted(missing), stale, half, expect_today)


def check_single(job: dict, root: Path, now: datetime, days: int) -> dict:
    today, past_hour = _today(job, now)
    p = root / job["pattern"]
    half, last = {}, None
    if p.exists():
        last = datetime.fromtimestamp(p.stat().st_mtime, tz=timezone.utc).astimezone(ZoneInfo(job["timezone"])).date()
        pr = _half_written(p, job, root)
        if pr:
            half[last.isoformat()] = pr
    stale = past_hour and last != today
    return _result(job, last, [], stale, half, today, note="single file: only the latest day is visible")


def check_state(job: dict, root: Path, now: datetime, days: int) -> dict:
    today, _ = _today(job, now)
    p = root / job["pattern"]
    half: dict[str, list[str]] = {}
    last, at = None, None
    probs: list[str] = []
    if p.exists():
        if p.stat().st_size == 0:
            probs.append(f"zero-byte {job['pattern']}")
        else:
            try:
                at = datetime.fromisoformat(json.loads(p.read_text(encoding="utf-8"))["at"])
            except Exception:  # noqa: BLE001
                probs.append(f"bad JSON or no 'at' in {job['pattern']}")
        # unreadable state: date from mtime, but it counts as stale (no trusted run time)
        seen = at or datetime.fromtimestamp(p.stat().st_mtime, tz=timezone.utc)
        last = seen.astimezone(ZoneInfo(job["timezone"])).date()
    for jf in job.get("json_files", []):
        q = root / jf
        if q.exists() and q.stat().st_size > 0 and _json_bad(q) and jf != job["pattern"]:
            probs.append(f"bad JSON {jf}")
    if job.get("scan_dir") and (root / job["scan_dir"]).is_dir():
        sd = root / job["scan_dir"]
        ok = job.get("zero_byte_ok", [])
        for e in sorted(sd.iterdir()):
            if e.is_file():
                if e.name.endswith(PARTIAL_SUFFIXES):
                    probs.append(f"partial file {os.path.relpath(e, root)}")
                elif e.stat().st_size == 0 and not _zero_ok(e.name, ok):
                    probs.append(f"zero-byte {os.path.relpath(e, root)}")
    if probs:
        half[(last or today).isoformat()] = probs
    win = job.get("active_window")
    in_window = None
    if win:
        in_window, win_start = _window(win, now)
        max_age = timedelta(minutes=float(win.get("max_age_minutes", 45)))
        if not in_window:
            stale = False  # job is not scheduled to run now
        else:
            # time since the later of the last run and today's window opening
            ref = win_start if at is None or at < win_start else at
            stale = (now - ref) > max_age
    else:
        stale = at is None or (now - at) > timedelta(hours=float(job.get("max_age_hours", 24)))
    r = _result(job, last, [], stale, half, today)
    if win:
        r["in_active_window"] = in_window
    r["last_at"] = at.astimezone(timezone.utc).isoformat(timespec="seconds") if at else None
    r["age_hours"] = round((now - at).total_seconds() / 3600, 1) if at else None
    return r


def _window(win: dict, now: datetime) -> tuple[bool, datetime]:
    """(inside window now?, today's window start) for {"timezone","start":"HH:MM","end":"HH:MM"}."""
    tz = ZoneInfo(win.get("timezone", "UTC"))
    loc = now.astimezone(tz)
    sh, sm = map(int, win["start"].split(":")); eh, em = map(int, win["end"].split(":"))
    start = loc.replace(hour=sh, minute=sm, second=0, microsecond=0)
    end = loc.replace(hour=eh, minute=em, second=0, microsecond=0)
    return start <= loc <= end, start


def _result(job, last, missing, stale, half, expect, note=None) -> dict:
    r = {"job": job["name"], "kind": job["kind"], "timezone": job["timezone"],
         "pattern": job["pattern"], "expected_today": expect.isoformat(),
         "last_output": last.isoformat() if last else None,
         "missing": [d.isoformat() for d in missing], "stale": bool(stale),
         "half_written": half}
    r["status"] = "WARN" if (missing or stale or half) else "OK"
    if note or job.get("note"):
        r["note"] = note or job.get("note")
    return r


CHECKERS = {"dated": check_dated, "single": check_single, "state": check_state}


def run(root: Path, config: Path, now: datetime, days: int) -> dict:
    jobs = load_config(config)
    res = [CHECKERS[j["kind"]](j, root, now, days) for j in jobs]
    return {"schema": "run-gaps-report/v1", "checked_at": now.astimezone(timezone.utc).isoformat(timespec="seconds"),
            "days": days, "jobs": res,
            "overall": "WARN" if any(r["status"] == "WARN" for r in res) else "OK", "writes": "none"}


def render(rep: dict) -> str:
    out = [f"Run-gap check ({rep['days']} days, at {rep['checked_at']}): {rep['overall']}", "",
           "| job | last output | missing days | stale | half-written | status |", "|---|---|---|---|---|---|"]
    for r in rep["jobs"]:
        hw = "; ".join(f"{d}: {', '.join(v)}" for d, v in r["half_written"].items()) or "-"
        out.append(f"| {r['job']} | {r['last_output'] or 'never'} | {len(r['missing'])}"
                   + (f" ({', '.join(r['missing'])})" if r["missing"] else "")
                   + f" | {'yes' if r['stale'] else 'no'} | {hw} | {r['status']} |")
    return "\n".join(out) + "\n"


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--root", type=Path, required=True, help="shop work dir holding out/ verify/ auto-list/")
    p.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    p.add_argument("--days", type=int, default=14)
    p.add_argument("--now", help="ISO time to judge against (tests / replays); default now UTC")
    p.add_argument("--json", action="store_true")
    p.add_argument("--out-json", type=Path)
    a = p.parse_args(argv)
    if a.days < 1:
        p.error("--days must be >= 1")
    now = datetime.fromisoformat(a.now) if a.now else datetime.now(timezone.utc)
    if now.tzinfo is None:
        now = now.replace(tzinfo=timezone.utc)
    try:
        rep = run(a.root, a.config, now, a.days)
    except Exception as e:  # noqa: BLE001
        print(f"run_gap_check: {type(e).__name__}: {e}", file=sys.stderr)
        return 2
    if a.out_json:
        a.out_json.write_text(json.dumps(rep, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(rep, indent=2) if a.json else render(rep), end="" if not a.json else "\n")
    return 1 if rep["overall"] == "WARN" else 0


if __name__ == "__main__":
    sys.exit(main())
