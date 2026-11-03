"""Live catalog dollars versus the tiered quote. Fixture only — no catalog write.

Supplier cost fields in the committed snapshot are null. Sell dollars stay.
The tiered formula is checked with a synthetic landed amount, not a shop cost.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from decimal import Decimal
from pathlib import Path

from autolist import listing_quote, price
from held_policy import load_held_policy

ROOT = Path(__file__).resolve().parents[2]
SNAPSHOT = ROOT / "shared" / "live-price-snapshot.json"
REDACTED = ("costCny", "costUsd", "costSource", "landedUsd")


def test_snapshot_keeps_sell_dollars_redacts_costs_and_s06_stays_25() -> None:
    payload = json.loads(SNAPSHOT.read_text(encoding="utf-8"))
    assert payload["readOnly"] is True
    assert payload["writesCatalog"] is False
    assert payload["fx"] == "6.723"
    assert payload["liveCount"] == 62
    assert payload["blobSha256"] == "5a61d106e697a781c3c829f2c1d9c11aeec41670b13627cfc1a72c3f99fa4ed3"
    rows = payload["rows"]
    assert len(rows) == 62
    codes = [row["ma"] for row in rows]
    assert len(codes) == len(set(codes))
    policy = load_held_policy()
    assert set(codes).isdisjoint(policy.held)
    assert "Q02" not in codes

    for row in rows:
        for key in REDACTED:
            assert row[key] is None, row["ma"]
        assert isinstance(row["liveUsd"], int) and row["liveUsd"] >= 1
        assert isinstance(row["wouldBeUsd"], int) and row["wouldBeUsd"] >= 1
        if row["ma"] == "S06":
            assert row["liveUsd"] == 25
            assert row["wouldBeUsd"] == 25
            assert row["applied"] is False
            assert row["flat25Usd"] == 12
            assert row["note"] == "Locked. Shown price stays $25."
            continue
        if row["flat25Usd"] is None:
            assert row["applied"] is False
            assert row["wouldBeUsd"] == row["liveUsd"]
            assert row["ma"] == "O04"
            assert row["liveUsd"] == 12
            assert row["note"] == "No usable intake cost. Live price stays."
            continue
        assert row["applied"] is True
        assert isinstance(row["flat25Usd"], int) and row["flat25Usd"] >= 1

    locked = listing_quote("S06", Decimal("30"))
    assert locked.action == "locked"
    assert locked.sell_usd == 25
    assert price(Decimal("30")) == 42
    assert price(Decimal("30")) != locked.sell_usd

    module = (ROOT / "shared" / "tiered-pricing.ts").read_text(encoding="utf-8")
    assert "held.json" not in module
    assert "products.json" not in module
    closet = (ROOT / "sassy-closet" / "lib" / "pricing.ts").read_text(encoding="utf-8")
    shop = (ROOT / "sassy-closet-shop" / "lib" / "pricing.ts").read_text(encoding="utf-8")
    assert "tiered-pricing" not in closet
    assert "tiered-pricing" not in shop
    assert 0.75 in _decimals(closet)
    assert 0.75 in _decimals(shop)


def test_committed_snapshot_has_no_supplier_cost_hits() -> None:
    proc = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "privacy_scan.py"), "--no-allowlist", str(SNAPSHOT)],
        check=False,
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0
    assert "privacy_scan: CLEAN" in proc.stdout
    assert proc.stderr == ""


def _decimals(source: str) -> set[float]:
    return {float(m) for m in re.findall(r"\d+\.\d+", source)}
