#!/usr/bin/env python3
"""Read-only: compare seed products.json sell USD vs a live-Blob sell snapshot fixture.
Prints a markdown table. Writes nothing. Sell dollars only."""
import argparse, json, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from held_policy import norm_ma  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
SEED = ROOT / "sassy-closet-shop/data/products.json"
LIVE = ROOT / "data/fixtures/seed-vs-live/live-sell-2026-10-22.json"


def load(path):
    d = json.loads(Path(path).read_text())
    rows = d if isinstance(d, list) else d.get("products", [])
    return {norm_ma(r["ma"]): r.get("priceUsd") for r in rows}


def compare(seed, live):
    out = []
    for ma in sorted(set(seed) | set(live)):
        s, l = seed.get(ma), live.get(ma)
        if ma not in seed:
            kind = "live-only"
        elif ma not in live:
            kind = "seed-only"
        elif s != l:
            kind = "price-diff"
        else:
            kind = "match"
        out.append((ma, s, l, kind))
    return out


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", default=SEED)
    ap.add_argument("--live", default=LIVE)
    ap.add_argument("--all", action="store_true", help="include matches")
    a = ap.parse_args(argv)
    rows = compare(load(a.seed), load(a.live))
    counts = {}
    for r in rows:
        counts[r[3]] = counts.get(r[3], 0) + 1
    print("| mã | seed $ | live $ | kind |\n|---|---|---|---|")
    for ma, s, l, k in rows:
        if a.all or k != "match":
            f = lambda v: "—" if v is None else f"${v}"
            print(f"| {ma} | {f(s)} | {f(l)} | {k} |")
    print("\n" + ", ".join(f"{k}={v}" for k, v in sorted(counts.items())))
    return 0


if __name__ == "__main__":
    sys.exit(main())
