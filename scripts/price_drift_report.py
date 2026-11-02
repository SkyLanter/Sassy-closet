#!/usr/bin/env python3
"""Read-only: print sell-$ drift table (live vs hub vs intake vs seed products.json).
Writes nothing. Boss picks which column wins; this applies no dollars."""
import json, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
FX = ROOT / "docs/fixtures/price-drift/snapshot-2026-10-28.json"
SEED = ROOT / "sassy-closet-shop/data/products.json"

sys.path.insert(0, str(Path(__file__).resolve().parent))
from held_policy import norm_ma as norm  # shared mã normalization

def _grouped(mapping):
    grouped = {}
    for key, value in mapping.items():
        grouped.setdefault(norm(key), []).append(value)
    return grouped


def _finite(value):
    if isinstance(value, bool) or value is None:
        return None
    try:
        number = float(value)
    except (TypeError, ValueError, OverflowError):
        return None
    if number != number or number == float("inf") or number == float("-inf"):
        return None
    return number


def _blank(value):
    return value is None or (isinstance(value, str) and value.strip() == "")


def _is_lock(value):
    number = _finite(value)
    return number is not None and number == S06_LOCK


def _shown(code, values):
    if code == "S06":
        for value in values:
            if not _blank(value) and not _is_lock(value):
                return value
    return values[-1]


def _collapse(mapping):
    return {code: _shown(code, values) for code, values in _grouped(mapping).items()}


def rows(fx=FX, seed=SEED):
    f = json.loads(Path(fx).read_text())
    s = _collapse({p["ma"]: p.get("priceUsd") for p in json.loads(Path(seed).read_text())["products"]})
    live = _collapse(f["live"])
    hub = _collapse(f["hub"])
    intake = _collapse(f["intake"])
    out = []
    for m in sorted(set(live) | set(hub) | set(s)):
        vals = [live.get(m), hub.get(m), intake.get(m) if m in intake else hub.get(m), s.get(m)]
        present = set()
        for value in vals:
            number = _finite(value)
            if number is not None:
                present.add(number)
        if len(present) > 1 or (m in intake and intake[m] is None):
            out.append((m, *vals))
    return out

S06_LOCK = 25.0

def s06_intake_check(fx=FX):
    """Read-only S06 intake check. Returns (status, message). Never fills anything.
    WARN when intake sell_usd is blank (Boss must OK filling 25); FAIL when any
    spelling is set to anything other than the $25 lock or live S06 is not $25;
    PASS otherwise."""
    f = json.loads(Path(fx).read_text())
    live_vals = _grouped(f["live"]).get("S06", [])
    if not live_vals or any(not _is_lock(v) for v in live_vals):
        shown = next((v for v in live_vals if not _is_lock(v)), None)
        return "FAIL", f"S06 live is {shown!r}, lock is $25"
    intake_vals = _grouped(f["intake"]).get("S06", [])
    off = [v for v in intake_vals if not _blank(v) and not _is_lock(v)]
    if off:
        return "FAIL", f"S06 intake sell_usd {off[0]} != $25 lock"
    if not intake_vals or any(_blank(v) for v in intake_vals):
        return "WARN", "S06 intake sell_usd blank (live $25). Not auto-filled; Boss must OK filling 25."
    return "PASS", "S06 intake sell_usd = $25"

def fmt(v):
    number = _finite(v)
    return "—" if number is None else f"{number:g}"

def main():
    print("| mã | live | hub | intake | seed products.json |")
    print("|---|---|---|---|---|")
    for m, *v in rows():
        print(f"| {m} | " + " | ".join(fmt(x) for x in v) + " |")
    st, msg = s06_intake_check()
    print(f"\nS06 intake check: {st} — {msg}")
    print("\nNo dollars applied. Boss picks which column wins.")
    if "--strict" in sys.argv and st != "PASS":
        return 1
    return 0

if __name__ == "__main__":
    sys.exit(main())
