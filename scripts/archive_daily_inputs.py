#!/usr/bin/env python3
"""Piece 92: keep dated copies of the day's decision inputs (BOX ONLY).

Copies, when present, into <root>/out/archive/<date>/ (under gitignored /out/):
  out/reports/<date>/COST-BASIS.md        -> COST-BASIS.md
  out/reports/<date>/BOSS-DECISIONS.md    -> BOSS-DECISIONS.md
  out/midnight-qc/<date>/summary.md|json  -> midnight-qc-summary.md|json
  out/muse/TODAY.md, extras-<date>.md, pack-message-<date>.txt,
  meta-qc-<date>.json                     -> muse/<name>
  <repo>/sassy-closet-shop/data/popular-order.json -> popular-order.json

The archive may hold costs: it must never enter the repo or the draft bundle
(privacy_scan.py flags any out/archive path). Existing archive files are never
overwritten unless --force. No network, no sends, no live writes.
"""
from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import daily_summary_draft as ds  # noqa: E402

ROOT = Path("/workspace/sassy-closet")


def sources(root, date, order=None):
    root = Path(root)
    rep, qc, muse = root / "out/reports" / date, root / "out/midnight-qc" / date, root / "out/muse"
    order = Path(order) if order else ds.default_paths()["order"]
    return [
        (rep / "COST-BASIS.md", "COST-BASIS.md"),
        (rep / "BOSS-DECISIONS.md", "BOSS-DECISIONS.md"),
        (qc / "summary.md", "midnight-qc-summary.md"),
        (qc / "summary.json", "midnight-qc-summary.json"),
        (muse / "TODAY.md", "muse/TODAY.md"),
        (muse / f"extras-{date}.md", f"muse/extras-{date}.md"),
        (muse / f"pack-message-{date}.txt", f"muse/pack-message-{date}.txt"),
        (muse / f"meta-qc-{date}.json", f"muse/meta-qc-{date}.json"),
        (order, "popular-order.json"),
    ]


def archive(root, date, order=None, force=False):
    """-> list of (status, dest_rel); status in copied|kept|missing|overwritten."""
    dest = Path(root) / "out/archive" / date
    res = []
    for src, name in sources(root, date, order):
        out = dest / name
        if not src.is_file():
            res.append(("missing", name))
            continue
        existed = out.exists()
        if existed and not force:
            res.append(("kept", name))
            continue
        out.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, out)
        res.append(("overwritten" if existed else "copied", name))
    return res


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--date", default=ds.today_pt())
    ap.add_argument("--root", type=Path, default=ROOT)
    ap.add_argument("--order", type=Path)
    ap.add_argument("--force", action="store_true", help="overwrite existing archive files")
    a = ap.parse_args(argv)
    res = archive(a.root, a.date, a.order, a.force)
    for st, name in res:
        print(f"{st:11} out/archive/{a.date}/{name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
