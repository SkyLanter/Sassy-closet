#!/usr/bin/env python3
"""Piece 60: offline Meta snapshot saver for Sassy Closet.

Turns a hand/Muse/QC-filled caption-check sheet (CSV or JSON, one row per
post) into the structured snapshot that meta_caption_gap_report reads.

Input columns: platform, media_type, post_id, ma, has_gia, checked_at
(post_id may also be given as "id"). Caption text is never read or stored:
any "caption" column is dropped. Output goes to
out/meta-snapshot/meta-snapshot-<UTC stamp>.json (out/ is gitignored).

No network, no Meta calls. Exit: 0 saved, 1 rows rejected (nothing saved
unless --allow-partial), 2 usage error.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "out" / "meta-snapshot"
PLAT = {"fb": "fb", "facebook": "fb", "ig": "ig", "instagram": "ig"}
MEDIA = {"post", "reel", "story", "carousel", "photo", "video"}
MA_RE = re.compile(r"^[A-Z][0-9]{2}$")
TRUE = {"1", "true", "yes", "y", "t"}
FALSE = {"0", "false", "no", "n", "f", ""}
FIELDS = ("platform", "media_type", "id", "ma", "has_gia", "checked_at")


def read_rows(path: Path):
    if path.suffix.lower() == ".csv":
        with path.open(newline="", encoding="utf-8-sig") as f:
            return list(csv.DictReader(f))
    d = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(d, dict):
        d = d.get("posts", [])
    if not isinstance(d, list):
        raise ValueError("JSON must be a list or {\"posts\": [...]}")
    return d


def _ts(v: str):
    v = v.strip()
    try:
        dt = datetime.fromisoformat(v.replace("Z", "+00:00"))
    except ValueError:
        return None
    return dt.isoformat()


def normalize(rows):
    good, bad = [], []
    for n, r in enumerate(rows, 1):
        if not isinstance(r, dict):
            bad.append((n, "not_an_object")); continue
        r = {str(k).strip().lower(): ("" if v is None else str(v).strip()) for k, v in r.items()}
        plat = PLAT.get(r.get("platform", "").lower())
        media = (r.get("media_type") or "post").lower()
        pid = r.get("post_id") or r.get("id") or ""
        ma = r.get("ma", "").upper()
        hg = r.get("has_gia", "").lower()
        ts = _ts(r.get("checked_at", ""))
        errs = []
        if not plat: errs.append("platform")
        if media not in MEDIA: errs.append("media_type")
        if not pid: errs.append("post_id")
        if ma and not MA_RE.match(ma): errs.append("ma")
        if hg not in TRUE | FALSE: errs.append("has_gia")
        if ts is None: errs.append("checked_at")
        if errs:
            bad.append((n, ",".join(errs))); continue
        good.append({"platform": plat, "media_type": media, "id": pid,
                     "ma": ma or None, "has_gia": hg in TRUE, "checked_at": ts})
    # de-dup by (platform, id): keep newest checked_at
    best = {}
    for p in good:
        k = (p["platform"], p["id"])
        if k not in best or p["checked_at"] > best[k]["checked_at"]:
            best[k] = p
    return sorted(best.values(), key=lambda p: (p["platform"], p["id"])), bad


def save(posts, out_dir: Path, now=None) -> Path:
    now = now or datetime.now(timezone.utc)
    out_dir.mkdir(parents=True, exist_ok=True)
    stamp = now.strftime("%Y%m%dT%H%M%SZ")
    path = out_dir / f"meta-snapshot-{stamp}.json"
    doc = {"kind": "meta-snapshot", "version": 1, "saved_at": now.isoformat(),
           "platforms": sorted({p["platform"] for p in posts}), "posts": posts}
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(doc, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    tmp.replace(path)
    return path


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("input", type=Path)
    ap.add_argument("--out-dir", type=Path, default=OUT_DIR)
    ap.add_argument("--allow-partial", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args(argv)
    try:
        rows = read_rows(a.input)
    except (OSError, ValueError, UnicodeDecodeError) as e:
        print(f"usage: cannot read input: {type(e).__name__}", file=sys.stderr)
        return 2
    posts, bad = normalize(rows)
    for n, why in bad:
        print(f"REJECT row {n}: {why}")
    if bad and not a.allow_partial:
        print(f"not saved: {len(bad)} bad row(s)")
        return 1
    if not posts:
        print("not saved: no valid rows")
        return 1
    if a.dry_run:
        print(f"dry-run OK posts={len(posts)}")
        return 0
    p = save(posts, a.out_dir)
    print(f"saved posts={len(posts)} -> {p}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
