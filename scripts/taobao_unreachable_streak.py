#!/usr/bin/env python3
"""Piece 49: READ-ONLY, WARN-only Taobao unreachable streak watch.

Reads verify/cost-recheck/cost-recheck-YYYY-MM-DD-flags.csv files and counts,
per mã, how many consecutive recheck runs (newest backwards) flagged it
"unreachable". Output carries mã codes and day counts ONLY: never ¥, links,
item ids, names or costs. No network, no writes. A sibling summary.<date>.json
with an explicit taobao_login_needed block is signed-out: those flags are not
used, and the day neither counts nor breaks a streak. A missing summary is
unchanged: the flag CSV for that date still counts. An existing summary that
is unreadable or malformed is not real data: flags are not used and the day
neither counts nor breaks a streak. Strings false and no are not a block.
Summary JSON and flag CSVs are read as utf-8-sig.
"""
import argparse
import csv
import glob
import os
import re
import sys

import cost_recheck_block
from held_policy import norm_ma

DATE_RE = re.compile(r"cost-recheck-(\d{4}-\d{2}-\d{2})-flags\.csv$")
MA_RE = re.compile(r"^[A-Z]\d{2}$")


def partition_runs(directory):
    """Return (runs, blocked_dates, bad_dates).

    blocked_dates are flag files ignored for a signed-out summary.
    bad_dates are flag files whose summary exists but is unreadable or
    malformed: not real data, so the day neither counts nor breaks a streak.
    A missing summary still reads the flag CSV.
    """
    runs = []
    blocked_dates = []
    bad_dates = []
    for path in glob.glob(os.path.join(directory, "cost-recheck-*-flags.csv")):
        m = DATE_RE.search(os.path.basename(path))
        if not m:
            continue
        date = m.group(1)
        summary = os.path.join(directory, f"summary.{date}.json")
        state, _doc = cost_recheck_block.load_summary(summary)
        if state == "blocked":
            blocked_dates.append(date)
            continue
        if state == "bad":
            bad_dates.append(date)
            continue
        unreachable = set()
        with open(path, newline="", encoding=cost_recheck_block.ENCODING) as fh:
            for row in csv.DictReader(fh):
                ma = norm_ma((row.get("ma") or ""))
                flags = (row.get("flag") or "").split("|")
                if MA_RE.match(ma) and "unreachable" in [f.strip() for f in flags]:
                    unreachable.add(ma)
        runs.append((date, unreachable))
    runs.sort()
    blocked_dates.sort()
    bad_dates.sort()
    return runs, blocked_dates, bad_dates


def load_runs(directory):
    return partition_runs(directory)[0]


def streaks(runs):
    """Return {ma: (days, since_date)} for mãs unreachable in the newest run."""
    if not runs:
        return {}
    out = {}
    for ma in runs[-1][1]:
        n, since = 0, None
        for date, bad in reversed(runs):
            if ma not in bad:
                break
            n, since = n + 1, date
        out[ma] = (n, since)
    return out


def warn_lines(result, min_days=1):
    rows = sorted(result.items(), key=lambda kv: (-kv[1][0], kv[0]))
    return [f"WARN unreachable_streak {ma} day {n} (since {since})"
            for ma, (n, since) in rows if n >= min_days]


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--dir", default="verify/cost-recheck")
    p.add_argument("--min-days", type=int, default=2)
    a = p.parse_args(argv)
    runs, blocked_dates, bad_dates = partition_runs(a.dir)
    if not runs and not blocked_dates and not bad_dates:
        print("OK no cost-recheck flag files found")
        return 0
    if not runs and not bad_dates:
        print(f"OK signed-out block on {len(blocked_dates)} cost-recheck run(s); unreachable flags not used")
        return 0
    if not runs and not blocked_dates:
        print(f"OK unreadable cost-recheck summary on {len(bad_dates)} run(s); unreachable flags not used")
        return 0
    if not runs:
        print(f"OK no usable cost-recheck run ({len(blocked_dates)} signed-out, {len(bad_dates)} unreadable); unreachable flags not used")
        return 0
    lines = warn_lines(streaks(runs), a.min_days)
    header = f"latest_run {runs[-1][0]} runs_read {len(runs)} blocked_runs {len(blocked_dates)}"
    if bad_dates:
        header += f" unreadable_runs {len(bad_dates)}"
    print(header)
    for line in lines:
        print(line)
    if not lines:
        print("OK no unreachable streaks")
    return 0


if __name__ == "__main__":
    sys.exit(main())
