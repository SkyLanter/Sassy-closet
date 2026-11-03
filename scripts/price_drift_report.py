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

def rows(fx=FX, seed=SEED):
    f = json.loads(Path(fx).read_text())
    s = {norm(p["ma"]): p.get("priceUsd") for p in json.loads(Path(seed).read_text())["products"]}
    live = {norm(k): v for k, v in f["live"].items()}
    hub = {norm(k): v for k, v in f["hub"].items()}
    intake = {norm(k): v for k, v in f["intake"].items()}
    out = []
    for m in sorted(set(live) | set(hub) | set(s)):
        vals = [live.get(m), hub.get(m), intake.get(m) if m in intake else hub.get(m), s.get(m)]
        present = {float(v) for v in vals if v is not None}
        if len(present) > 1 or (m in intake and intake[m] is None):
            out.append((m, *vals))
    return out

S06_LOCK = 25.0

def s06_intake_check(fx=FX):
    """Read-only S06 intake check. Returns (status, message). Never fills anything.
    WARN when intake sell_usd is blank (Boss must OK filling 25); FAIL when it is
    set to anything other than the $25 lock or live S06 is not $25; PASS otherwise."""
    f = json.loads(Path(fx).read_text())
    live = {norm(k): v for k, v in f["live"].items()}.get("S06")
    intake_map = {norm(k): v for k, v in f["intake"].items()}
    if live is None or float(live) != S06_LOCK:
        return "FAIL", f"S06 live is {live!r}, lock is $25"
    v = intake_map.get("S06")
    if v is None or str(v).strip() == "":
        return "WARN", "S06 intake sell_usd blank (live $25). Not auto-filled; Boss must OK filling 25."
    if float(v) != S06_LOCK:
        return "FAIL", f"S06 intake sell_usd {v} != $25 lock"
    return "PASS", "S06 intake sell_usd = $25"

def fmt(v):
    return "—" if v is None else f"{float(v):g}"

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
