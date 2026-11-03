#!/usr/bin/env python3
"""Read-only: compare seed products.json sell USD vs a live-Blob sell snapshot fixture.
Prints a markdown table. Writes nothing. Sell dollars only.

Every spelling of a mã is kept. A later S06 at $25 does not hide an earlier
S006 at another price. No price is rewritten.
"""
import argparse, json, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from held_policy import norm_ma  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
SEED = ROOT / "sassy-closet-shop/data/products.json"
LIVE = ROOT / "data/fixtures/seed-vs-live/live-sell-2026-10-22.json"


def _equal(left, right):
    """25.0 matches 25. A boolean does not match a dollar."""
    if isinstance(left, bool) or isinstance(right, bool):
        return isinstance(left, bool) and isinstance(right, bool) and left is right
    return left == right


def _group(rows):
    grouped = {}
    for row in rows:
        grouped.setdefault(norm_ma(row["ma"]), []).append(row.get("priceUsd"))
    return grouped


def load(path):
    d = json.loads(Path(path).read_text())
    rows = d if isinstance(d, list) else d.get("products", [])
    return _group(rows)


def _agreed(values):
    return all(_equal(value, values[-1]) for value in values)


def compare(seed, live):
    out = []
    for ma in sorted(set(seed) | set(live)):
        seed_prices = seed.get(ma)
        live_prices = live.get(ma)
        if ma not in seed:
            kind = "live-only"
        elif ma not in live:
            kind = "seed-only"
        elif not _agreed(seed_prices) or not _agreed(live_prices) or not _equal(seed_prices[-1], live_prices[-1]):
            kind = "price-diff"
        else:
            kind = "match"
        out.append((ma, seed_prices, live_prices, kind))
    return out


def _cell(values):
    if not values:
        return "—"
    if _agreed(values):
        value = values[-1]
        return "—" if value is None else f"${value}"
    shown = ["—" if value is None else f"${value}" for value in values]
    return ", ".join(shown)


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
    for ma, seed_prices, live_prices, kind in rows:
        if a.all or kind != "match":
            print(f"| {ma} | {_cell(seed_prices)} | {_cell(live_prices)} | {kind} |")
    print("\n" + ", ".join(f"{k}={v}" for k, v in sorted(counts.items())))
    return 0


if __name__ == "__main__":
    sys.exit(main())
