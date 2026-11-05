#!/usr/bin/env python3
"""Piece 49: READ-ONLY, WARN-only Taobao unreachable streak watch.

Reads verify/cost-recheck/cost-recheck-YYYY-MM-DD-flags.csv files and counts,
per mã, how many consecutive recheck files (newest backwards) flagged it
"unreachable". A missing calendar day does not end that count; the report
names those days so a "day N" line is not read as N calendar days.

An empty file, a file with no ma/flag columns, a non-date name, or a file
that cannot be read is UNUSABLE. It is not a clean day and does not clear
a streak. No usable file is MISSING, not "OK", unless every dated flag file
is a signed-out block (sibling summary.YYYY-MM-DD.json with
taobao_login_needed). A blocked day is not a usable run: it does not count
and does not break a streak, and it is not a missing calendar day. When
--as-of (default: today in America/Los_Angeles) is after the newest usable
or blocked file, the report says STALE. An unusable file alone does not
set that date.

Output carries mã codes, dates, filenames and those status words only:
never ¥, links, item ids, names or costs. No network, no writes.
"""
import argparse
import csv
import datetime as dt
import glob
import io
import json
import os
import re
import sys
from zoneinfo import ZoneInfo

import cost_recheck_block
from held_policy import norm_ma

DATE_RE = re.compile(r"cost-recheck-(\d{4}-\d{2}-\d{2})-flags\.csv$")
MA_RE = re.compile(r"^[A-Z]\d{2}$")
PT = ZoneInfo("America/Los_Angeles")
GAP_LIST_MAX = 14


def today_pt(now=None):
    now = now or dt.datetime.now(dt.timezone.utc)
    return now.astimezone(PT).date()


def _real_day(text):
    try:
        return dt.date.fromisoformat(text)
    except (TypeError, ValueError):
        return None


def _norm_row(row):
    out = {}
    for key, value in row.items():
        if key is None:
            continue
        out[key.strip()] = value
    return out


def _row_broken(row):
    """True when this data row cannot be trusted as a clean flag line."""
    extra = row.get("_extra") or []
    if any(str(part).strip() for part in extra):
        return True
    for key, value in row.items():
        if key == "_extra" or isinstance(value, list):
            continue
        if value is not None and ("\n" in value or "\r" in value or "\x00" in value):
            return True
    flag = None
    for key, value in row.items():
        if key is not None and key.strip() == "flag":
            flag = value
            break
    return flag is None


def read_flags(path):
    """Return ('ok', set of mã) or ('unusable', short reason). Never includes cell text."""
    try:
        with open(path, "rb") as fh:
            raw = fh.read()
    except OSError:
        return "unusable", "unreadable"
    if not raw:
        return "unusable", "empty file"
    if b"\x00" in raw:
        return "unusable", "bad csv"
    try:
        text = raw.decode("utf-8-sig")
    except UnicodeDecodeError:
        return "unusable", "unreadable"
    try:
        reader = csv.DictReader(io.StringIO(text), restkey="_extra")
        if not reader.fieldnames:
            return "unusable", "no header"
        names = {(name or "").strip() for name in reader.fieldnames}
        if "ma" not in names or "flag" not in names:
            return "unusable", "missing ma or flag column"
        unreachable = set()
        for raw_row in reader:
            if _row_broken(raw_row):
                return "unusable", "bad csv"
            row = _norm_row(raw_row)
            ma = norm_ma(row.get("ma") or "")
            flags = (row.get("flag") or "").split("|")
            if MA_RE.match(ma) and "unreachable" in [part.strip() for part in flags]:
                unreachable.add(ma)
        return "ok", unreachable
    except (OSError, UnicodeDecodeError):
        return "unusable", "unreadable"
    except csv.Error:
        return "unusable", "bad csv"


def _summary_blocked(directory, date_iso):
    """True only when sibling summary.<date>.json is an explicit signed-out block.

    A missing file, or a file that is not valid JSON, is not a block, so the
    flag CSV stays evidence. UTF-8 BOM is accepted so it cannot hide the flag.
    """
    path = os.path.join(directory, f"summary.{date_iso}.json")
    try:
        with open(path, encoding="utf-8-sig") as fh:
            doc = json.load(fh)
    except (OSError, UnicodeError, json.JSONDecodeError):
        return False
    return cost_recheck_block.login_blocked(doc)


def scan(directory):
    """Usable runs, problems, real dates, and signed-out blocked dates.

    A missing directory yields four empty results. A filename that is not
    cost-recheck-YYYY-MM-DD-flags.csv is ignored. An impossible date is a problem.
    A sibling summary with taobao_login_needed is not a usable run. That date
    stays in the real dates and the blocked dates. A missing summary, or a
    summary that is not valid JSON, leaves the flag file to be read as usual.
    """
    if not os.path.isdir(directory):
        return [], [], [], []
    runs = []
    problems = []
    real_dates = []
    blocked = []
    pattern = os.path.join(directory, "cost-recheck-*-flags.csv")
    for path in sorted(glob.glob(pattern)):
        name = os.path.basename(path)
        match = DATE_RE.search(name)
        if not match:
            continue
        day = _real_day(match.group(1))
        if day is None:
            problems.append((name, "not a real date"))
            continue
        real_dates.append(day)
        if _summary_blocked(directory, day.isoformat()):
            blocked.append(day)
            continue
        status, payload = read_flags(path)
        if status != "ok":
            problems.append((name, payload))
            continue
        runs.append((day.isoformat(), payload))
    runs.sort()
    problems.sort()
    blocked.sort()
    return runs, problems, real_dates, blocked


def load_runs(directory):
    runs, _problems, _dates, _blocked = scan(directory)
    return runs


def streaks(runs):
    """Return {ma: (files, since_date)} for mãs unreachable in the newest usable run.

    The count is consecutive files, newest backwards, until a usable file
    does not list the mã. Missing days between those files stay in the count.
    """
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


def calendar_gaps(dates):
    """Calendar days strictly between the earliest and latest date that have no file."""
    if len(dates) < 2:
        return []
    have = set(dates)
    start, end = min(dates), max(dates)
    missing = []
    cur = start + dt.timedelta(days=1)
    while cur < end:
        if cur not in have:
            missing.append(cur)
        cur += dt.timedelta(days=1)
    return missing


def _contiguous(missing):
    groups = []
    start = prev = missing[0]
    for day in missing[1:]:
        if day == prev + dt.timedelta(days=1):
            prev = day
            continue
        groups.append((start, prev))
        start = prev = day
    groups.append((start, prev))
    return groups


def gap_line(missing):
    if not missing:
        return None
    tail = ". Day counts are consecutive files, not calendar days."
    if len(missing) <= GAP_LIST_MAX:
        shown = ", ".join(day.isoformat() for day in missing)
        return "NOTE missing cost-recheck days " + shown + tail
    groups = _contiguous(missing)
    if len(groups) == 1:
        start, end = groups[0]
        shown = f"{len(missing)} days from {start.isoformat()} through {end.isoformat()}"
    else:
        shown = (f"{len(missing)} days in separate gaps, "
                 f"earliest {missing[0].isoformat()}, latest {missing[-1].isoformat()}")
    return "NOTE missing cost-recheck days " + shown + tail


def build_report(directory, min_days=2, as_of=None):
    """Full stdout. as_of is a datetime.date or None (no stale check)."""
    folder_missing = not os.path.isdir(directory)
    if folder_missing:
        runs, problems, real_dates, blocked = [], [], [], []
    else:
        runs, problems, real_dates, blocked = scan(directory)
    lines = []
    every_dated_blocked = bool(real_dates) and len(blocked) == len(real_dates) and not runs
    if folder_missing:
        lines.append("MISSING cost-recheck folder (no cost-recheck flag files found)")
    elif every_dated_blocked:
        lines.append(
            f"OK signed-out block on {len(blocked)} cost-recheck run(s); unreachable flags not used"
        )
    elif not runs:
        if problems:
            lines.append("MISSING no usable cost-recheck flag files found")
        else:
            lines.append("MISSING no cost-recheck flag files found")
    else:
        lines.append(f"latest_run {runs[-1][0]} runs_read {len(runs)}")
    for name, reason in problems:
        lines.append(f"UNUSABLE {name}: {reason}")
    note = gap_line(calendar_gaps(real_dates))
    if note:
        lines.append(note)
    if runs:
        for day in blocked:
            lines.append(
                "NOTE signed-out cost-recheck block "
                f"{day.isoformat()} (unreachable flags not used)"
            )
    evidence_days = []
    for date_iso, _mas in runs:
        parsed = _real_day(date_iso)
        if parsed is not None:
            evidence_days.append(parsed)
    evidence_days.extend(blocked)
    if as_of is not None and evidence_days:
        latest = max(evidence_days)
        if latest < as_of:
            lines.append(
                f"STALE latest cost-recheck flags {latest.isoformat()} are before {as_of.isoformat()}"
            )
        elif latest > as_of:
            lines.append(
                f"NOTE latest cost-recheck flags {latest.isoformat()} are after {as_of.isoformat()}"
            )
    if runs:
        warns = warn_lines(streaks(runs), min_days)
        if warns:
            lines.extend(warns)
        else:
            lines.append("OK no unreachable streaks")
    return "\n".join(lines) + "\n"


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--dir", default="verify/cost-recheck")
    p.add_argument("--min-days", type=int, default=2)
    p.add_argument("--as-of", default=None,
                   help="YYYY-MM-DD to judge stale against (default: today in America/Los_Angeles)")
    a = p.parse_args(argv)
    if a.as_of is None:
        as_of = today_pt()
    else:
        as_of = _real_day(a.as_of)
        if as_of is None:
            print("bad --as-of, want YYYY-MM-DD", file=sys.stderr)
            return 2
    sys.stdout.write(build_report(a.dir, a.min_days, as_of))
    return 0


if __name__ == "__main__":
    sys.exit(main())
