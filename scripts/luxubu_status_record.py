#!/usr/bin/env python3
"""Piece 98: append or update out/muse/luxubu-status-<date>.json (local file only).

  luxubu_status_record.py --date YYYY-MM-DD --checked HH:MM \
      [--last-msg-time HH:MM --last-msg-title "..."] \
      [--last-activity-time HH:MM --last-activity-title "..."] \
      --new true|false [--root .]

Times are America/Los_Angeles (PT). Written from CLI flags only: no network,
nothing is sent. Same check time -> that entry is updated; else appended.
Titles must not hold costs, links or emails. Atomic write (temp + os.replace).
"""
import argparse
import json
import os
import re
import sys
import tempfile
from pathlib import Path

DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
HHMM = re.compile(r"^([01]\d|2[0-3]):[0-5]\d$")
BANNED = re.compile(r"[¥$]|https?://|www\.|tesla|@[\w.-]+\.\w+", re.I)


def clean(s, n=80):
    s = re.sub(r"\s+", " ", str(s or "")).strip()[:n]
    if BANNED.search(s):
        raise ValueError("titles must not hold costs, links or emails")
    return s


def _time(t, name):
    if t is None:
        return None
    if not HHMM.match(t):
        raise ValueError(f"{name} must be HH:MM (PT)")
    return t


def path_for(root, date):
    return Path(root) / "out/muse" / f"luxubu-status-{date}.json"


def load(root, date):
    p = path_for(root, date)
    if not p.exists():
        return None
    try:
        doc = json.loads(p.read_text(encoding="utf-8") or "{}")
    except json.JSONDecodeError:
        return None
    return doc if isinstance(doc, dict) and isinstance(doc.get("checks"), list) else None


def record(root, date, checked, new, msg_time=None, msg_title=None,
           act_time=None, act_title=None):
    if not DATE.match(date):
        raise ValueError("bad date")
    ent = {"checked_pt": _time(checked, "checked"), "new": bool(new),
           "last_message": {"time_pt": _time(msg_time, "last-msg-time"),
                            "title": clean(msg_title)},
           "last_activity": {"time_pt": _time(act_time, "last-activity-time"),
                             "title": clean(act_title)}}
    if not checked:
        raise ValueError("--checked is required")
    p = path_for(root, date)
    p.parent.mkdir(parents=True, exist_ok=True)
    doc = load(root, date) or {"date": date, "checks": []}
    doc["checks"] = [c for c in doc["checks"] if c.get("checked_pt") != checked] + [ent]
    doc["checks"].sort(key=lambda c: c.get("checked_pt") or "")
    fd, tmp = tempfile.mkstemp(dir=p.parent, prefix=".luxubu-status-", suffix=".tmp")
    try:
        with os.fdopen(fd, "w") as f:
            json.dump(doc, f, ensure_ascii=False, indent=2, sort_keys=True)
            f.write("\n")
        os.replace(tmp, p)
    except BaseException:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise
    return p


def summary_line(doc):
    """Factual one-liner for the daily summary; no inference about sign-in."""
    if not doc or not doc.get("checks"):
        return "Luxubu: no status record"
    c = doc["checks"][-1]
    def part(k, label):
        v = c.get(k) or {}
        if not v.get("time_pt"):
            return f"{label}: none recorded"
        t = f" '{v['title']}'" if v.get("title") else ""
        return f"{label}{t} at {v['time_pt']} PT"
    return ("Luxubu: " + part("last_message", "last reply") + "; "
            + part("last_activity", "last activity") + "; last checked "
            + f"{c.get('checked_pt')} PT ({'new since last check' if c.get('new') else 'nothing new'}).")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--date", required=True)
    ap.add_argument("--checked", required=True, help="check time HH:MM PT")
    ap.add_argument("--last-msg-time")
    ap.add_argument("--last-msg-title")
    ap.add_argument("--last-activity-time")
    ap.add_argument("--last-activity-title")
    ap.add_argument("--new", required=True, choices=["true", "false"])
    ap.add_argument("--root", default="/workspace/sassy-closet")
    a = ap.parse_args(argv)
    try:
        p = record(a.root, a.date, a.checked, a.new == "true", a.last_msg_time,
                   a.last_msg_title, a.last_activity_time, a.last_activity_title)
    except ValueError as e:
        print(f"error: {e}", file=sys.stderr)
        return 2
    print(f"wrote {p}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
