#!/usr/bin/env python3
"""Piece 72: READ-ONLY Meta Popular carry-over order builder.

A 28-day Meta Popular cycle only ranks recent posts, so live best-sellers
with older posts drop out. This builder proposes a site order that:
  1. puts live mãs ranked in the window first, by the cycle's blended rank;
  2. then lists live mãs not in the window in their previous order
     (PR #101's Oct 13 order if given, else the order on the site now);
  3. leaves held / never-list / unlisted mãs out entirely;
  4. skips caption-less Reels (rows with no mã).
Writes only a markdown proposal. No deploy, no Blob/Meta writes.

Piece 73: the live set comes from ONE source only, the public Blob catalog
(the same catalog.v1.json freshness_check.py reads): products with status
"available". It is read from a saved file (--catalog) or by a single GET
(--catalog-url). The cycle SUMMARY text is never used for the live set.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from held_policy import MA_RE, norm_ma  # noqa: E402

DEFAULT_CATALOG_URL = (
    "https://efsi0jejsfy7j058.public.blob.vercel-storage.com/sassy-closet-shop/catalog.v1.json"
)
LIVE_STATUSES = {"available"}
LIVE_LINE_RE = re.compile(r"^Live on sell site among ranked:\s*(.*)$", re.M)
HOME_MA_RE = re.compile(r"/m/([A-Z][0-9]{2})\b")


def _codes(seq):
    out = []
    for x in seq or []:
        if not isinstance(x, str):
            continue  # caption-less Reel / unmapped row
        c = norm_ma(x)
        if MA_RE.match(c) and c not in out:
            out.append(c)
    return out


def load_order(path):
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return _codes(data.get("order") if isinstance(data, dict) else data)


def home_order(html):
    return _codes(HOME_MA_RE.findall(html))


def summary_live(text):
    m = LIVE_LINE_RE.search(text or "")
    return _codes(re.findall(r"[A-Z][0-9]{2}", m.group(1))) if m else []


def catalog_live(data):
    """Live mãs from catalog JSON: products whose status is available, in catalog order."""
    prods = data.get("products", []) if isinstance(data, dict) else []
    return _codes([p.get("ma") for p in prods
                   if isinstance(p, dict) and str(p.get("status", "")).lower() in LIVE_STATUSES])


def fetch_catalog(url, timeout=20):
    """Single read-only GET of the public catalog."""
    from urllib.request import Request, urlopen
    req = Request(url, method="GET", headers={"User-Agent": "SassyClosetPopular/1.0"})
    with urlopen(req, timeout=timeout) as r:  # noqa: S310 - fixed public https url
        return json.loads(r.read().decode("utf-8"))


def load_held(path):
    d = json.loads(Path(path).read_text(encoding="utf-8"))
    return set(_codes(d.get("heldIncomplete", []) + d.get("held", []) + d.get("neverList", [])))


def build(ranked, live, held, previous):
    """Return (order, ranked_live, carried, dropped) — pure function."""
    live_ok = [m for m in _codes(live) if m not in held]
    live_set = set(live_ok)
    ranked_live = [m for m in _codes(ranked) if m in live_set]
    seen = set(ranked_live)
    carried = []
    for m in _codes(previous) + live_ok:  # previous order, then any live leftovers
        if m in live_set and m not in seen:
            carried.append(m)
            seen.add(m)
    dropped = [m for m in _codes(ranked) if m not in live_set]
    return ranked_live + carried, ranked_live, carried, dropped


def render(order, ranked_live, carried, dropped, held, src):
    L = ["# Proposed Popular order (carry-over) — DRAFT, not deployed", "",
         "Read-only proposal from pieces 72-73 (live set = Blob catalog). Nothing deployed; PR #101 untouched.", "",
         f"- Ranked source: {src['ranked']}",
         f"- Previous order source: {src['previous']}",
         f"- Live set source: {src['live']}",
         f"- Live mãs: {len(order)}; ranked in window: {len(ranked_live)}; carried over: {len(carried)}",
         f"- Left out (ranked but held/unlisted): {', '.join(dropped) or 'none'}",
         "- Caption-less Reels: skipped", "", "## Order", ""]
    for i, m in enumerate(order, 1):
        tag = "window rank" if m in ranked_live else "carried (previous order)"
        L.append(f"{i}. {m} — {tag}")
    return "\n".join(L) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--cycle", required=True, help="cycle dir with blended.json and SUMMARY.txt")
    ap.add_argument("--held", default=str(Path(__file__).resolve().parents[1] / "data" / "held.json"))
    ap.add_argument("--prev-oct13", help="PR #101 order json, used first if given")
    ap.add_argument("--site-home", help="saved site home html (current site order + live set)")
    ap.add_argument("--prev-order", help="popular-order.json fallback for previous order")
    ap.add_argument("--catalog", help="saved catalog.v1.json (live set source)")
    ap.add_argument("--catalog-url", nargs="?", const=DEFAULT_CATALOG_URL,
                    help="GET the public catalog for the live set (default URL if no value)")
    ap.add_argument("--out", help="write markdown here (default: stdout)")
    a = ap.parse_args(argv)
    cyc = Path(a.cycle)
    ranked = load_order(cyc / "blended.json")
    summ = (cyc / "SUMMARY.txt").read_text(encoding="utf-8") if (cyc / "SUMMARY.txt").exists() else ""
    previous, live, psrc, lsrc = [], [], [], []
    if a.prev_oct13:
        previous += load_order(a.prev_oct13); psrc.append("PR #101 Oct 13 order")
    if a.site_home:
        h = home_order(Path(a.site_home).read_text(encoding="utf-8"))
        previous += h; psrc.append("site home snapshot order")
    if a.prev_order:
        previous += load_order(a.prev_order); psrc.append("popular-order.json")
    if a.catalog:
        live = catalog_live(json.loads(Path(a.catalog).read_text(encoding="utf-8")))
        lsrc.append("Blob catalog.v1.json (saved copy)")
    elif a.catalog_url:
        live = catalog_live(fetch_catalog(a.catalog_url)); lsrc.append("Blob catalog.v1.json (GET)")
    else:
        ap.error("live set needs --catalog or --catalog-url (SUMMARY text is never used)")
    sl = summary_live(summ)
    disagree = sorted(set(sl) ^ (set(live) & set(sl))) if sl else []
    held = load_held(a.held)
    order, rl, carried, dropped = build(ranked, live, held, previous)
    md = render(order, rl, carried, dropped, held,
                {"ranked": f"{cyc.name}/blended.json", "previous": " then ".join(psrc) or "none",
                 "live": " + ".join(lsrc) or "none"})
    if sl:
        md += ("\nSUMMARY live line (info only, not used): " + " ".join(sl)
               + ("; not live in catalog: " + ", ".join(disagree) if disagree else "; all live in catalog") + "\n")
    if a.out:
        Path(a.out).write_text(md, encoding="utf-8")
        print(f"wrote {a.out}: {len(order)} live mãs ({len(rl)} ranked, {len(carried)} carried)")
    else:
        sys.stdout.write(md)
    return 0


if __name__ == "__main__":
    sys.exit(main())
