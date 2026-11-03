#!/usr/bin/env python3
"""Piece 79: write or update one sub-entry of out/muse/meta-qc-<date>.json.

  meta_qc_record.py --date YYYY-MM-DD --side ig|fb --who luxubu|miniboss \
      --status pass|fail|unchecked --reason "..." [--proof out/path.png] [--root .]

Local file only, atomic (temp file + os.replace). Old flat side entries are
kept as "legacy" and never count as a PASS. Nothing is sent anywhere.
"""
import argparse
import json
import os
import re
import sys
import tempfile
from pathlib import Path

DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
BANNED = re.compile(r"[¥$]|https?://|www\.|tesla|@[\w.-]+\.\w+", re.I)


def clean(s, n=60):
    return re.sub(r"\s+", " ", str(s or "")).strip()[:n]


def record(root, date, side, who, status, reason="", proof=None):
    if not DATE.match(date):
        raise ValueError("bad date")
    reason = clean(reason)
    if BANNED.search(reason):
        raise ValueError("reason must not hold costs, links or emails")
    if proof:
        pp = Path(proof)
        if pp.is_absolute() or ".." in pp.parts or BANNED.search(proof):
            raise ValueError("proof must be a relative local path")
    path = Path(root) / "out/muse" / f"meta-qc-{date}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    doc = {}
    if path.exists():
        doc = json.loads(path.read_text() or "{}")
        if not isinstance(doc, dict):
            doc = {}
    cur = doc.get(side)
    if not (isinstance(cur, dict) and any(w in cur for w in ("luxubu", "miniboss"))):
        cur = {"legacy": cur} if cur is not None else {}
    ent = {"status": status, "reason": reason}
    if proof:
        ent["proof"] = str(proof)
    cur[who] = ent
    doc[side] = cur
    fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=".meta-qc-", suffix=".tmp")
    try:
        with os.fdopen(fd, "w") as f:
            json.dump(doc, f, ensure_ascii=False, indent=2, sort_keys=True)
            f.write("\n")
        os.replace(tmp, path)
    except BaseException:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise
    return path


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", required=True)
    ap.add_argument("--side", required=True, choices=["ig", "fb"])
    ap.add_argument("--who", required=True, choices=["luxubu", "miniboss"])
    ap.add_argument("--status", required=True, choices=["pass", "fail", "unchecked"])
    ap.add_argument("--reason", default="")
    ap.add_argument("--proof")
    ap.add_argument("--root", default=".")
    a = ap.parse_args(argv)
    try:
        p = record(a.root, a.date, a.side, a.who, a.status, a.reason, a.proof)
    except ValueError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 2
    print(f"wrote {p}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
