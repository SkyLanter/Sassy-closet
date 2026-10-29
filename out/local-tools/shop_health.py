#!/usr/bin/env python3
"""shop_health.py - read-only local shop health report (plain text).

Reads only local snapshot files (no network):
  <root>/auto-list/state/live-catalog-latest.json  copy of the live Blob catalog (live count, prices)
  <root>/auto-list/state/held.json                 held mã list (keys)
  <root>/auto-list/state/last_check.json           last auto-list check (optional)

Usage: python3 shop_health.py [--root /workspace/sassy-closet] [--s06-price 25]
Exit 1 if S06 != expected price, a held mã is in the live catalog, or a file is missing.
"""
import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

REL = {
    "catalog": "auto-list/state/live-catalog-latest.json",
    "held": "auto-list/state/held.json",
    "last_check": "auto-list/state/last_check.json",
}


def load(path):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f), None
    except (OSError, ValueError) as e:
        return None, str(e)


def build_report(root, s06_expected=25):
    root = Path(root)
    lines, problems = [], []
    cat, err = load(root / REL["catalog"])
    held, herr = load(root / REL["held"])
    last, _ = load(root / REL["last_check"])
    lines.append("SHOP HEALTH (local snapshot, read-only, no network)")
    lines.append(f"root: {root}")
    live = {}
    if cat is None:
        problems.append(f"catalog unreadable: {err}")
    else:
        for p in cat.get("products", []):
            live[p["ma"]] = p
        lines.append(f"live count: {len(live)} (catalog updatedAt {cat.get('updatedAt', '?')})")
        s06 = live.get("S06")
        if s06 is None:
            problems.append("S06 not in live catalog")
            lines.append("S06 price: MISSING")
        else:
            price = s06.get("priceUsd")
            ok = price == s06_expected
            lines.append(f"S06 price: ${price} ({'OK' if ok else 'EXPECTED $%s' % s06_expected})")
            if not ok:
                problems.append(f"S06 is ${price}, expected ${s06_expected}")
    if held is None:
        problems.append(f"held list unreadable: {herr}")
    else:
        keys = list(held.keys()) if isinstance(held, dict) else list(held)
        lines.append(f"held count: {len(keys)}")
        lines.append("held list: " + " ".join(keys))
        leaked = [k for k in keys if k in live]
        if leaked:
            problems.append("held mã in live catalog: " + " ".join(leaked))
        else:
            lines.append("held in live catalog: none (OK)")
    if last:
        lines.append(f"last auto-list check: {last.get('at', '?')} {last.get('result', '?')} - {last.get('detail', '')}")
    lines.append("")
    if problems:
        lines.append("PROBLEMS:")
        lines += [f"- {p}" for p in problems]
    else:
        lines.append("STATUS: OK")
    return "\n".join(lines), problems


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", default=str(Path(__file__).resolve().parent.parent.parent))
    ap.add_argument("--s06-price", type=int, default=25)
    a = ap.parse_args(argv)
    text, problems = build_report(a.root, a.s06_price)
    print(text)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
