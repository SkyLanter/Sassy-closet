#!/usr/bin/env python3
"""Piece 44: read-only hung-run watch for the 15-minute auto-list job (WARN-only).

Built on piece 38 run_gap_check (active-window helper). Three checks:
  missed_slots  15-minute slots inside the active window with no heartbeat since the
                newest of state/last_check.json "at", state/run.sh.lock mtime and
                state/autolist.lock mtime (run.sh truncates the lock on each start).
  stale_locks   a *.lock in state/ that a process still holds (from /proc/locks) and
                whose mtime is older than --stale-lock-minutes (run.sh times out at 25).
  half_written  timestamped run folders in runs/ missing summary.json, or holding
                zero-byte (run.log excepted) / bad-JSON / *.tmp / *.partial files. The newest folder is
                skipped while the run lock is held (run still in progress).

Prints names, paths, times and counts only, never file contents.
Never writes, deletes, locks or touches anything under --autolist.
Exit: 0 OK, 1 WARN, 2 usage error.
"""
from __future__ import annotations

import argparse
import json
import math
import re
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import run_gap_check as g

DEFAULT_WINDOW = {"timezone": "America/Los_Angeles", "start": "08:09", "end": "22:54"}
REQUIRED = ("summary.json",)
ZERO_BYTE_OK = ("run.log",)  # autolist.py leaves run.log empty on normal runs
RUN_DIR = re.compile(r"^\d{8}T\d{6}Z")


def held_inodes(proc_locks: Path = Path("/proc/locks")) -> set[int]:
    """Inodes with an active FLOCK/POSIX lock (read-only parse of /proc/locks)."""
    out: set[int] = set()
    try:
        text = proc_locks.read_text()
    except OSError:
        return out
    for line in text.splitlines():
        parts = line.split()
        dev = next((x for x in parts if x.count(":") == 2), None)
        if dev:
            try:
                out.add(int(dev.rsplit(":", 1)[1]))
            except ValueError:
                pass
    return out


def _mtime(p: Path) -> datetime | None:
    try:
        return datetime.fromtimestamp(p.stat().st_mtime, tz=timezone.utc)
    except OSError:
        return None


def heartbeat(state: Path) -> datetime | None:
    seen = []
    lc = state / "last_check.json"
    if lc.exists() and lc.stat().st_size:
        try:
            seen.append(datetime.fromisoformat(json.loads(lc.read_text(encoding="utf-8"))["at"]))
        except Exception:  # noqa: BLE001
            pass
    for n in ("run.sh.lock", "autolist.lock"):
        m = _mtime(state / n)
        if m:
            seen.append(m)
    return max(seen) if seen else None


def missed_slots(hb: datetime | None, now: datetime, slot_min: int, grace_min: int, window: dict | None) -> dict:
    inside, start = (True, None) if window is None else g._window(window, now)
    if not inside:
        return {"in_active_window": False, "missed": 0, "since": None}
    ref = hb
    if start is not None and (ref is None or ref < start):
        ref = start  # nothing is owed before today's window opened
    if ref is None:
        return {"in_active_window": True, "missed": None, "since": None}
    gap = (now - ref - timedelta(minutes=grace_min)).total_seconds() / 60
    return {"in_active_window": True, "missed": max(0, math.floor(gap / slot_min)),
            "since": ref.astimezone(timezone.utc).isoformat(timespec="seconds")}


def stale_locks(state: Path, now: datetime, stale_min: int, held: set[int]) -> list[dict]:
    out = []
    for p in sorted(state.glob("*.lock")):
        m = _mtime(p)
        is_held = p.stat().st_ino in held
        age = round((now - m).total_seconds() / 60, 1) if m else None
        if is_held and age is not None and age > stale_min:
            out.append({"lock": p.name, "held": True, "age_minutes": age})
    return out


def half_written(runs: Path, run_in_progress: bool) -> dict[str, list[str]]:
    if not runs.is_dir():
        return {}
    dirs = sorted(d for d in runs.iterdir() if d.is_dir() and RUN_DIR.match(d.name))
    if run_in_progress and dirs:
        dirs = dirs[:-1]
    out: dict[str, list[str]] = {}
    for d in dirs:
        probs = [f"missing {r}" for r in REQUIRED if not (d / r).exists()]
        for f in sorted(x for x in d.iterdir() if x.is_file()):
            if f.name.endswith(g.PARTIAL_SUFFIXES):
                probs.append(f"partial file {f.name}")
            elif f.stat().st_size == 0 and f.name not in ZERO_BYTE_OK:
                probs.append(f"zero-byte {f.name}")
            elif f.suffix == ".json" and g._json_bad(f):
                probs.append(f"bad JSON {f.name}")
        if probs:
            out[d.name] = probs
    return out


def run(autolist: Path, now: datetime, slot_min=15, grace_min=5, stale_min=30,
        window: dict | None = DEFAULT_WINDOW, held: set[int] | None = None) -> dict:
    state = autolist / "state"
    held = held_inodes() if held is None else held
    hb = heartbeat(state)
    slots = missed_slots(hb, now, slot_min, grace_min, window)
    locks = stale_locks(state, now, stale_min, held) if state.is_dir() else []
    rl = state / "run.sh.lock"
    in_prog = rl.exists() and rl.stat().st_ino in held
    hw = half_written(autolist / "runs", in_prog)
    warn = []
    if slots["missed"]:
        warn.append(f"{slots['missed']} missed {slot_min}-min slot(s) since {slots['since']}")
    if slots["missed"] is None:
        warn.append("no heartbeat found in state/")
    warn += [f"stale lock {l['lock']} held {l['age_minutes']} min" for l in locks]
    warn += [f"half-written run {k}: {', '.join(v)}" for k, v in hw.items()]
    return {"schema": "hung-run-watch/v1", "now": now.astimezone(timezone.utc).isoformat(timespec="seconds"),
            "heartbeat": hb.astimezone(timezone.utc).isoformat(timespec="seconds") if hb else None,
            "run_in_progress": in_prog, "slots": slots, "stale_locks": locks, "half_written": hw,
            "warn": warn, "overall": "WARN" if warn else "OK"}


def render(r: dict) -> str:
    lines = [f"hung-run watch {r['overall']} at {r['now']} (heartbeat {r['heartbeat']})"]
    lines += [f"  WARN {w}" for w in r["warn"]] or ["  no missed slots, stale locks or half-written runs"]
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--autolist", type=Path, required=True, help="auto-list dir holding state/ and runs/")
    p.add_argument("--now")
    p.add_argument("--slot-minutes", type=int, default=15)
    p.add_argument("--grace-minutes", type=int, default=5)
    p.add_argument("--stale-lock-minutes", type=int, default=30)
    p.add_argument("--no-window", action="store_true", help="treat every slot as owed (24h)")
    p.add_argument("--json", action="store_true")
    a = p.parse_args(argv)
    if a.slot_minutes < 1 or a.stale_lock_minutes < 1 or a.grace_minutes < 0:
        p.error("minutes must be positive")
    if not a.autolist.is_dir():
        print(f"hung_run_watch: no such dir {a.autolist}", file=sys.stderr)
        return 2
    now = datetime.fromisoformat(a.now) if a.now else datetime.now(timezone.utc)
    if now.tzinfo is None:
        now = now.replace(tzinfo=timezone.utc)
    r = run(a.autolist, now, a.slot_minutes, a.grace_minutes, a.stale_lock_minutes,
            None if a.no_window else DEFAULT_WINDOW)
    print(json.dumps(r, indent=2) if a.json else render(r), end="\n" if a.json else "")
    return 1 if r["overall"] == "WARN" else 0


if __name__ == "__main__":
    sys.exit(main())
