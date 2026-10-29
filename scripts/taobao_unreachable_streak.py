#!/usr/bin/env python3
"""Piece 49: READ-ONLY, WARN-only Taobao unreachable streak watch.

Reads verify/cost-recheck/cost-recheck-YYYY-MM-DD-flags.csv files and counts,
per mã, how many consecutive recheck runs (newest backwards) flagged it
"unreachable". Output carries mã codes and day counts ONLY: never ¥, links,
item ids, names or costs. No network, no writes.
"""
import argparse
import csv
import glob
import os
import re
import sys
from held_policy import norm_ma

DATE_RE = re.compile(r"cost-recheck-(\d{4}-\d{2}-\d{2})-flags\.csv$")
MA_RE = re.compile(r"^[A-Z]\d{2}$")


def load_runs(directory):
    runs = []
    for path in glob.glob(os.path.join(directory, "cost-recheck-*-flags.csv")):
        m = DATE_RE.search(os.path.basename(path))
        if not m:
            continue
        unreachable = set()
        with open(path, newline="", encoding="utf-8-sig") as fh:
            for row in csv.DictReader(fh):
                ma = norm_ma((row.get("ma") or ""))
                flags = (row.get("flag") or "").split("|")
                if MA_RE.match(ma) and "unreachable" in [f.strip() for f in flags]:
                    unreachable.add(ma)
        runs.append((m.group(1), unreachable))
    runs.sort()
    return runs


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
    runs = load_runs(a.dir)
    if not runs:
        print("OK no cost-recheck flag files found")
        return 0
    lines = warn_lines(streaks(runs), a.min_days)
    print(f"latest_run {runs[-1][0]} runs_read {len(runs)}")
    for line in lines:
        print(line)
    if not lines:
        print("OK no unreachable streaks")
    return 0


if __name__ == "__main__":
    sys.exit(main())
