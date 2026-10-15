"""Live catalog dollars versus the tiered quote. Fixture only — no catalog write."""

from __future__ import annotations

import json
import re
from decimal import Decimal, ROUND_CEILING
from pathlib import Path

from autolist import listing_quote, price
from held_policy import load_held_policy

ROOT = Path(__file__).resolve().parents[2]
SNAPSHOT = ROOT / "shared" / "live-price-snapshot.json"
FX = Decimal("6.723")
DEBOX = {"V": Decimal("7.50"), "Q": Decimal("7.50"), "D": Decimal("7.50")}
_DECIMAL = re.compile(r"^\d+(?:\.\d+)?$")


def _positive(raw: object) -> Decimal | None:
    if raw is None:
        return None
    text = str(raw).strip()
    if _DECIMAL.fullmatch(text) is None:
        return None
    value = Decimal(text)
    if value <= 0:
        return None
    return value


def _landed(row: dict[str, object]) -> Decimal | None:
    kind = str(row["kind"]).strip().upper()[:1]
    debox = DEBOX.get(kind, Decimal("0"))
    cny = _positive(row.get("costCny"))
    if cny is not None:
        return cny / FX + debox
    usd = _positive(row.get("costUsd"))
    if usd is not None:
        return usd + debox
    return None


def _flat(landed: Decimal) -> int:
    quoted = int((landed / Decimal("0.75")).to_integral_value(rounding=ROUND_CEILING))
    if quoted < 10:
        return quoted + 2
    return quoted


def test_live_prices_would_become_the_tiered_quote_and_s06_stays_25() -> None:
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
        landed = _landed(row)
        if row["ma"] == "S06":
            assert row["liveUsd"] == 25
            assert row["wouldBeUsd"] == 25
            assert row["applied"] is False
            assert landed is not None
            assert format(landed, "f") == row["landedUsd"]
            assert _flat(landed) == row["flat25Usd"]
            locked = listing_quote("S06", landed)
            assert locked.action == "locked"
            assert locked.sell_usd == 25
            assert price(landed) != row["wouldBeUsd"]
            continue
        if landed is None:
            assert row["applied"] is False
            assert row["wouldBeUsd"] == row["liveUsd"]
            assert row["flat25Usd"] is None
            assert row["landedUsd"] is None
            continue
        assert row["applied"] is True
        assert format(landed, "f") == row["landedUsd"]
        assert price(landed) == row["wouldBeUsd"]
        assert _flat(landed) == row["flat25Usd"]
        assert price(landed) >= 1

    module = (ROOT / "shared" / "tiered-pricing.ts").read_text(encoding="utf-8")
    assert "held.json" not in module
    assert "products.json" not in module
    closet = (ROOT / "sassy-closet" / "lib" / "pricing.ts").read_text(encoding="utf-8")
    shop = (ROOT / "sassy-closet-shop" / "lib" / "pricing.ts").read_text(encoding="utf-8")
    assert "tiered-pricing" not in closet
    assert "tiered-pricing" not in shop
    assert "0.75" in closet
    assert "0.75" in shop
