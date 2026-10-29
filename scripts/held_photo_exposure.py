#!/usr/bin/env python3
"""Piece 95: held photo exposure check (READ-ONLY).

Which held mãs still have publicly reachable photos? Uses the SAME URL source
Midnight QC used for its "held photos still public on Blob" WARN:
  out/midnight-qc/<date>/pass1-raw.json   `heldblob` = [[url, status, ctype], ...]
                                          (cover + photo-2..8 probed by name)
  out/midnight-qc/<date>/raw/health-*.json blob.listed object paths (joined to the
                                          Blob base taken from the URLs above)
Optional extra local manifests: --manifest FILE (JSON list of URLs/paths, or
held-photos/v1 JSON with `urls`). Held set: <root>/data/held.json `heldIncomplete`
(the single held source every other check reads; --held overrides). Falls back to the newest earlier midnight-qc day.

Network: HEAD each URL (short --timeout, default 6s); GET only when HEAD
answers 405. Never PUT/POST/DELETE; never changes Blob. Deleting is Boss's call.

Writes <root>/out/reports/<date>/HELD-PHOTOS.md (box only, gitignored; URLs
may appear there, never in the repo or bundle). Table rows are parsed by
boss_decisions.py as evidence for the 'delete public photos?' line.
Exit: 0 none exposed, 1 some exposed, 2 input error.
"""
from __future__ import annotations

import argparse
import datetime as dt
import glob
import json
import re
import sys
import urllib.error
import urllib.request
from collections import Counter
from pathlib import Path

from held_policy import norm_ma

ROOT = Path("/workspace/sassy-closet")
MA_IN = re.compile(r"/products/([A-Z]\d{2})/")
ROW = re.compile(r"^\| ([A-Z]\d{2}) \| (\d+) \| (\d+) \| ([^|]*) \|$", re.M)
REPORT = "HELD-PHOTOS.md"


def today_pt():
    try:
        from zoneinfo import ZoneInfo
        return dt.datetime.now(ZoneInfo("America/Los_Angeles")).date().isoformat()
    except Exception:  # pragma: no cover
        return dt.date.today().isoformat()


def default_held_path(root):
    """Same single source as held_policy: <repo root>/data/held.json."""
    return Path(root) / "data" / "held.json"


def load_held(root, held=None):
    p = Path(held) if held else default_held_path(root)
    d = json.loads(p.read_text(encoding="utf-8"))
    if isinstance(d, dict) and isinstance(d.get("heldIncomplete"), list):
        d = d["heldIncomplete"]
    return sorted({norm_ma(m) for m in d} - {""})


def qc_dir(root, date):
    base = Path(root) / "out/midnight-qc"
    if (base / date / "pass1-raw.json").exists():
        return base / date
    days = sorted(p.parent.name for p in base.glob("*/pass1-raw.json") if p.parent.name <= date)
    return base / days[-1] if days else None


def collect(root, date, held, manifests=()):
    """-> (urls_by_ma {ma: sorted urls}, source_rel_paths)."""
    held = set(held)
    urls, srcs, base = {}, [], None
    d = qc_dir(root, date)

    def put(u):
        m = MA_IN.search(u)
        if m and m.group(1) in held:
            urls.setdefault(m.group(1), set()).add(u)

    if d is not None:
        raw = json.loads((d / "pass1-raw.json").read_text(encoding="utf-8"))
        for row in raw.get("heldblob") or []:
            u = row[0] if isinstance(row, (list, tuple)) else row
            if isinstance(u, str) and u.startswith("http"):
                base = base or u.split("/", 3)[:3]
                put(u)
        srcs.append(str((d / "pass1-raw.json").relative_to(root)))
        for h in sorted(glob.glob(str(d / "raw/health-*.json"))):
            listed = ((json.loads(Path(h).read_text(encoding="utf-8")).get("blob") or {}).get("listed")) or []
            if base and isinstance(listed, list):
                for p in listed:
                    if isinstance(p, str):
                        put("/".join(base) + "/" + p.lstrip("/"))
            srcs.append(str(Path(h).relative_to(root)))
    for mf in manifests:
        v = json.loads(Path(mf).read_text(encoding="utf-8"))
        items = v.get("urls", []) if isinstance(v, dict) else v
        for u in items:
            if isinstance(u, str):
                put(u if u.startswith("http") or not base else "/".join(base) + "/" + u.lstrip("/"))
        srcs.append(str(mf))
    return {m: sorted(s) for m, s in urls.items()}, srcs


def real_fetch(url, timeout):
    for method in ("HEAD", "GET"):
        try:
            req = urllib.request.Request(url, method=method, headers={"User-Agent": "held-photo-exposure/95"})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.status
        except urllib.error.HTTPError as e:
            if e.code == 405 and method == "HEAD":
                continue
            return e.code
        except Exception as e:  # timeout, DNS, etc.
            return f"error:{type(e).__name__}"
    return "error:none"


def probe(urls_by_ma, held, fetch):
    res = {}
    for m in held:
        st = {u: fetch(u) for u in urls_by_ma.get(m, [])}
        res[m] = st
    return res


def render(date, res, srcs):
    L = [f"# Held photo exposure {date}", "",
         "READ-ONLY. HEAD/GET probe only; nothing on Blob was changed. Delete is Boss's call.",
         "Sources: " + (", ".join(srcs) or "(none found)"), "",
         "| mã | photos | public | statuses |", "|---|---|---|---|"]
    for m in sorted(res):
        c = Counter(str(s) for s in res[m].values())
        pub = c.get("200", 0)
        st = " ".join(f"{k}={v}" for k, v in sorted(c.items())) or "-"
        L.append(f"| {m} | {len(res[m])} | {pub} | {st} |")
    exp = [m for m in sorted(res) if any(s == 200 for s in res[m].values())]
    L += ["", "Exposed: " + (", ".join(exp) or "none"), "", "## Public URLs (box only)"]
    L += [f"- {m} {u}" for m in exp for u, s in res[m].items() if s == 200] or ["- none"]
    return "\n".join(L) + "\n"


def parse_report(text):
    """-> {ma: (photos, public)} from a HELD-PHOTOS.md table."""
    return {m: (int(p), int(pub)) for m, p, pub, _ in ROW.findall(text)}


def exposed_from_report(path):
    p = Path(path)
    if not p.exists():
        return None
    return sorted(m for m, (_p, pub) in parse_report(p.read_text(encoding="utf-8")).items() if pub > 0)


def main(argv=None, fetch=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--date", default=today_pt())
    ap.add_argument("--root", type=Path, default=ROOT)
    ap.add_argument("--held", type=Path)
    ap.add_argument("--manifest", type=Path, action="append", default=[])
    ap.add_argument("--timeout", type=float, default=6.0)
    ap.add_argument("--out-dir", type=Path)
    a = ap.parse_args(argv)
    try:
        held = load_held(a.root, a.held)
        urls, srcs = collect(a.root, a.date, held, a.manifest)
    except (OSError, ValueError) as e:
        print(f"input error: {e}", file=sys.stderr)
        return 2
    f = fetch or (lambda u: real_fetch(u, a.timeout))
    res = probe(urls, held, f)
    out_dir = a.out_dir or a.root / "out/reports" / a.date
    out_dir.mkdir(parents=True, exist_ok=True)
    text = render(a.date, res, srcs)
    (out_dir / REPORT).write_text(text, encoding="utf-8")
    exp = exposed_from_report(out_dir / REPORT)
    print(f"wrote {out_dir / REPORT}; exposed: {', '.join(exp) or 'none'}")
    return 1 if exp else 0


if __name__ == "__main__":
    sys.exit(main())
