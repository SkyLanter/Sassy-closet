"""Tiered auto-list sell price.

m = 0.35 when the resulting sell is <= $25.
m = 0.25 when the resulting sell is >= $45.
Between those, m moves in a straight line.
sell = ceil(landed / (1 - m)).
When that ceil is under $10, add $2.
The margin uses the resulting sell. The quote is the smallest whole dollar
that does not undercut that sell: sell >= quote_from_sell(landed, sell).

This module reads data/held.json and does not write intake, Blob, the hub,
Square, or Meta. It does not change a stored ¥.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from decimal import Decimal, ROUND_CEILING

from held_policy import HeldPolicy, load_held_policy

LOW_SELL = 25
HIGH_SELL = 45
LOW_MARGIN = Decimal("0.35")
HIGH_MARGIN = Decimal("0.25")
UNDER_TEN = 10
UNDER_TEN_BUMP = 2
S06_LOCK_USD = 25


def margin_for_sell(sell: int) -> Decimal:
    if sell <= LOW_SELL:
        return LOW_MARGIN
    if sell >= HIGH_SELL:
        return HIGH_MARGIN
    span = Decimal(HIGH_SELL - LOW_SELL)
    return LOW_MARGIN + (HIGH_MARGIN - LOW_MARGIN) * (Decimal(sell - LOW_SELL) / span)


def quote_from_sell(landed: Decimal, sell_for_margin: int) -> int:
    divisor = Decimal(1) - margin_for_sell(sell_for_margin)
    quoted = int((landed / divisor).to_integral_value(rounding=ROUND_CEILING))
    if quoted < UNDER_TEN:
        return quoted + UNDER_TEN_BUMP
    return quoted


def _money(value: Decimal | int | str | float) -> Decimal:
    if isinstance(value, Decimal):
        return value
    if isinstance(value, float):
        return Decimal(str(value))
    return Decimal(value)


def price(landed: Decimal | int | str | float) -> int:
    """Smallest whole-dollar sell that does not undercut. Refuse a non-positive landed cost."""
    money = _money(landed)
    if money <= 0:
        raise ValueError("landed cost must be positive; refusing to invent a sell price")
    # A 2-cycle has no exact dollar. Its higher dollar is the smallest one
    # that does not undercut (16.26 → 26, 19.50 → 30). The old fallback
    # returned the raw 35% quote instead (30 → 47, 33 → 51, 19.51 → 31).
    # The low-end margin produces the usual highest quote. The under-$10 bump
    # can lift a neighbor by $2, so the search runs a little past that quote.
    ceiling = quote_from_sell(money, 1) + UNDER_TEN_BUMP
    for sell in range(1, ceiling + 1):
        quoted = quote_from_sell(money, sell)
        if sell >= quoted:
            return sell
    raise RuntimeError(f"no non-undercutting sell for landed {money}")


@dataclass(frozen=True)
class ListingQuote:
    ma: str
    action: str
    sell_usd: int | None
    reason: str


def listing_quote(
    ma: str,
    landed: Decimal | int | str | float | None,
    policy: HeldPolicy | None = None,
) -> ListingQuote:
    """Decide whether a mã can be quoted. Never writes the stored intake row."""
    rules = policy or load_held_policy()
    code = ma.strip().upper()
    reason = rules.skip_reason(code)
    if reason == "held":
        return ListingQuote(code, "skip", None, "held incomplete; not listed")
    if reason == "never-list":
        return ListingQuote(code, "skip", None, "never listed")
    if code == "S06":
        return ListingQuote(code, "locked", S06_LOCK_USD, "S06 stays $25")
    if landed is None:
        return ListingQuote(code, "no-price", None, "no landed cost; no invented price")
    try:
        sell = price(landed)
    except (ValueError, ArithmeticError):
        return ListingQuote(code, "no-price", None, "landed cost is not usable; no invented price")
    return ListingQuote(code, "quote", sell, "tiered fixed point")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Print a tiered sell quote. Does not write intake, Blob, or Meta.",
    )
    parser.add_argument("--landed", required=True, help="Landed USD. Not an intake ¥.")
    parser.add_argument("--ma", default="", help="Optional mã. Held mãs and never-list mãs are skipped.")
    args = parser.parse_args(argv)
    policy = load_held_policy()
    if args.ma.strip():
        quote = listing_quote(args.ma, args.landed, policy)
        print(
            json.dumps(
                {
                    "ma": quote.ma,
                    "action": quote.action,
                    "sell_usd": quote.sell_usd,
                    "reason": quote.reason,
                }
            )
        )
        return 0
    try:
        print(price(args.landed))
    except ValueError as error:
        print(str(error))
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
