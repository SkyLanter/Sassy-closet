#!/usr/bin/env python3
"""Piece 74: READ-ONLY check that every live catalog mã is in popular-order.json.

Live = public Blob catalog products with status "available" (same rule as
piece 73), minus held / never-list mãs from data/held.json.

--check  exits 1 if any live mã is missing from the order (prints them).
--plan   prints where each missing mã would go, without writing:
  * if the cycle's blended Meta order ranks it, it goes right after the last
    existing entry that blended ranks ahead of it (else before the first one);
  * otherwise it goes at the end of its catalog type group (after the last
    existing entry of the same type; end of list if the type has none),
    several in one group keep catalog order.
Existing entries are never removed or reordered. Nothing is written.
--held-report  (piece 75) lists held / never-list mãs that sit in the order
  (shared list: data/held.json via popular_carryover.load_held). Report only.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from popular_carryover import _codes, catalog_live, load_held  # noqa: E402
from held_policy import norm_ma  # noqa: E402


def missing(live, order, held):
    have = set(order)
    return [m for m in live if m not in have and m not in held]


def held_in_order(order, held):
    """Piece 75: held mãs present in the order, in order position. Read-only."""
    return [m for m in order if m in held]


def place(order, add, types, blended=None):
    """Return (new_order, placements[(ma, index, reason)]). Never reorders existing."""
    out = list(order)
    rank = {m: i for i, m in enumerate(blended or [])}
    notes = []
    for ma in add:
        if ma in rank:
            ahead = [i for i, m in enumerate(out) if m in rank and rank[m] < rank[ma]]
            behind = [i for i, m in enumerate(out) if m in rank and rank[m] > rank[ma]]
            idx = ahead[-1] + 1 if ahead else (behind[0] if behind else len(out))
            why = f"blended rank {rank[ma] + 1}"
        else:
            t = types.get(ma)
            same = [i for i, m in enumerate(out) if t is not None and types.get(m) == t]
            idx = same[-1] + 1 if same else len(out)
            why = f"end of type {t} group" if same else f"no type {t} group yet: end of list"
        out.insert(idx, ma)
        notes.append((ma, idx, why))
    return out, notes


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--order", required=True)
    ap.add_argument("--catalog", required=True, help="saved catalog.v1.json")
    ap.add_argument("--held", help="data/held.json")
    ap.add_argument("--blended", help="cycle blended.json")
    ap.add_argument("--plan", action="store_true")
    ap.add_argument("--held-report", action="store_true", help="list held mãs found in the order (read-only)")
    a = ap.parse_args(argv)
    cat = json.loads(Path(a.catalog).read_text(encoding="utf-8"))
    order = _codes(json.loads(Path(a.order).read_text(encoding="utf-8")).get("order"))
    held = load_held(a.held) if a.held else set()
    if a.held_report:
        hits = held_in_order(order, held)
        print("HELD_IN_ORDER " + (" ".join(hits) if hits else "none"))
    gap = missing(catalog_live(cat), order, held)
    if a.plan:
        types = {norm_ma(str(p.get("ma", ""))): p.get("type") for p in cat.get("products", []) if isinstance(p, dict)}
        bl = _codes(json.loads(Path(a.blended).read_text(encoding="utf-8")).get("order")) if a.blended else []
        _, notes = place(order, gap, types, bl)
        for ma, idx, why in notes:
            print(f"{ma}\tposition {idx + 1}\t{why}")
    if gap:
        print("MISSING " + " ".join(gap))
        return 1
    print("OK all live mãs in popular order")
    return 0


if __name__ == "__main__":
    sys.exit(main())
