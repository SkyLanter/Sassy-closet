#!/usr/bin/env python3
"""muse_pace.py - straight-line weekly usage pace for Muse/Luxubu (read-only).

Usage:
  python3 muse_pace.py --used-pct 0 --reset-date 2026-10-19 \
      --now 2026-10-15T02:49Z --week-days 7 [--backlog PATH] [--reset-time HH:MM]

Assumes the weekly window ends at reset-date <reset-time> UTC (default 00:00,
because Muse shows a date but no time) and started week-days earlier.
"""
import argparse
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

DEFAULT_BACKLOG = Path(__file__).resolve().parent.parent / "muse" / "muse-backlog.md"
ITEM = re.compile(r"^\s*(\d+)\.\s+(.*)$")
MARKER = re.compile(r"\[([^\[\]]*)\]")


def parse_now(s):
    dt = datetime.fromisoformat(s.strip().replace("Z", "+00:00"))
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def expected_pct(now, reset_date, week_days=7.0, reset_time="00:00"):
    hh, mm = (int(x) for x in reset_time.split(":"))
    end = datetime.fromisoformat(reset_date).replace(hour=hh, minute=mm, tzinfo=timezone.utc)
    start = end - timedelta(days=week_days)
    frac = (now - start) / (end - start)
    return max(0.0, min(100.0, frac * 100.0)), start, end


def parse_backlog(text):
    """Return list of (number, title, state) with state in {'open','partial','done'}."""
    items = []
    for line in text.splitlines():
        m = ITEM.match(line)
        if not m:
            continue
        num, body = int(m.group(1)), m.group(2)
        tags = MARKER.findall(body)
        if not tags:
            continue
        tag = tags[-1].strip()
        up = tag.upper()
        if up.startswith("DONE") or up == "X":
            state = "done"
        elif up.startswith("PARTIAL"):
            state = "partial"
        elif tag == "":
            state = "open"
        else:
            continue
        title = body.split("[")[0].strip()
        items.append((num, title, state, tag))
    return items


def next_item(items):
    for it in sorted(items):
        if it[2] != "done":
            return it
    return None


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--used-pct", type=float, required=True)
    ap.add_argument("--reset-date", required=True, help="YYYY-MM-DD")
    ap.add_argument("--now", required=True, help="ISO time, e.g. 2026-10-15T02:49Z")
    ap.add_argument("--week-days", type=float, default=7)
    ap.add_argument("--reset-time", default="00:00", help="UTC HH:MM (assumed; default 00:00)")
    ap.add_argument("--backlog", default=str(DEFAULT_BACKLOG))
    a = ap.parse_args(argv)

    now = parse_now(a.now)
    exp, start, end = expected_pct(now, a.reset_date, a.week_days, a.reset_time)
    diff = a.used_pct - exp
    print(f"window: {start:%Y-%m-%d %H:%M}Z -> {end:%Y-%m-%d %H:%M}Z ({a.week_days:g} days)")
    print(f"now: {now:%Y-%m-%d %H:%M}Z")
    print(f"expected used (straight line): {exp:.1f}%")
    print(f"actual used: {a.used_pct:.1f}%")
    if abs(diff) < 0.05:
        print("pace: on pace")
    elif diff < 0:
        print(f"pace: BEHIND by {-diff:.1f} points")
    else:
        print(f"pace: AHEAD by {diff:.1f} points")
    if now >= end:
        print("note: now is at or past the reset; expected clamped to 100%")
    try:
        items = parse_backlog(Path(a.backlog).read_text(encoding="utf-8"))
    except OSError as e:
        print(f"next item: backlog unreadable ({e})")
        return 0
    n = next_item(items)
    if n:
        extra = " (still open: partial)" if n[2] == "partial" else ""
        print(f"next not-done item: #{n[0]} {n[1]}{extra}")
    else:
        print("next not-done item: none (backlog empty - add more)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
