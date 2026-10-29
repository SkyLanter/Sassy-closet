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
import re
from dataclasses import dataclass
from decimal import Decimal, ROUND_CEILING

from held_policy import HeldPolicy, load_held_policy, norm_ma

LOW_SELL = 25
HIGH_SELL = 45
LOW_MARGIN = Decimal("0.35")
HIGH_MARGIN = Decimal("0.25")
UNDER_TEN = 10
UNDER_TEN_BUMP = 2
S06_LOCK_USD = 25

# Sizes. Clothing uses Asia letter sizes. Shoe mãs (G, O) also keep
# numeric EU/CN sizes 33-46; before this, G01 "35 36 37 38 39 40" lost every size.
ASIA = ("2XS", "XS", "S", "M", "L", "XL", "2XL")
SHOE_KINDS = frozenset({"G", "O"})
SHOE_EU = tuple(str(n) for n in range(33, 47))
_SIZE_ALIASES = {"XXS": "2XS", "XXL": "2XL", "3XL": "2XL"}
_SIZE_ORDER = ASIA + SHOE_EU


def _is_shoe(kind: str | None) -> bool:
    return (kind or "").strip()[:1].upper() in SHOE_KINDS


def is_valid_size(size: str, kind: str | None = None) -> bool:
    """kind is a mã (G01) or its letter (G). Numeric sizes are valid only for shoes."""
    return size in ASIA or (_is_shoe(kind) and size in SHOE_EU)


def norm_sizes(raw: str | None, kind: str | None = None) -> list[str]:
    """Normalize an intake size string. Unknown tokens are dropped, never invented."""
    shoe = _is_shoe(kind)
    out: list[str] = []
    for token in re.split(r"[\s,;/|]+", (raw or "").upper().strip()):
        token = _SIZE_ALIASES.get(token, token)
        if shoe and re.fullmatch(r"\d{2}(\.0)?", token):
            token = token.split(".")[0]
        if is_valid_size(token, kind) and token not in out:
            out.append(token)
    return sorted(out, key=_SIZE_ORDER.index)


def _size_token(token: str, kind: str | None) -> str:
    token = _SIZE_ALIASES.get(token, token)
    if _is_shoe(kind) and re.fullmatch(r"\d{2}(\.0)?", token):
        token = token.split(".")[0]
    return token


def invalid_size_tokens(raw: str | None, kind: str | None = None) -> list[str]:
    """Raw tokens norm_sizes would drop. Any of these means the item is flagged, not listed."""
    bad: list[str] = []
    for token in re.split(r"[\s,;/|]+", (raw or "").upper().strip()):
        if token and not is_valid_size(_size_token(token, kind), kind) and token not in bad:
            bad.append(token)
    return bad


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
    try:
        if isinstance(value, Decimal):
            money = value
        elif isinstance(value, float):
            money = Decimal(str(value))
        else:
            money = Decimal(value)
    except ArithmeticError:
        raise ValueError(f"landed cost {value!r} is not a number; refusing to invent a sell price") from None
    if not money.is_finite():
        raise ValueError(f"landed cost {value!r} is not finite; refusing to invent a sell price")
    return money


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
    sizes: tuple[str, ...] = ()


def listing_quote(
    ma: str,
    landed: Decimal | int | str | float | None,
    policy: HeldPolicy | None = None,
    sizes_raw: str | None = None,
) -> ListingQuote:
    """Decide whether a mã can be quoted. Never writes the stored intake row.

    sizes_raw is optional. When given, sizes are normalized before listing and an
    item with any invalid (or no) size is flagged, not listed. Held and never-list
    checks still run first; price logic is untouched."""
    rules = policy or load_held_policy()
    code = norm_ma(ma)
    reason = rules.skip_reason(code)
    if reason == "held":
        return ListingQuote(code, "skip", None, "held incomplete; not listed")
    if reason == "never-list":
        return ListingQuote(code, "skip", None, "never listed")
    if sizes_raw is not None:
        bad = invalid_size_tokens(sizes_raw, code)
        sizes = tuple(norm_sizes(sizes_raw, code))
        if bad or not sizes:
            detail = ", ".join(bad) if bad else "none given"
            return ListingQuote(code, "flag-size", None, f"invalid sizes: {detail}; not listed", sizes)
        base = listing_quote(code, landed, rules)
        return ListingQuote(base.ma, base.action, base.sell_usd, base.reason, sizes)
    if code == "S06":
        return ListingQuote(code, "locked", S06_LOCK_USD, "S06 stays $25")
    if landed is None:
        return ListingQuote(code, "no-price", None, "no landed cost; no invented price")
    try:
        sell = price(landed)
    except (ValueError, ArithmeticError):
        return ListingQuote(code, "no-price", None, "landed cost is not usable; no invented price")
    return ListingQuote(code, "quote", sell, "tiered fixed point")


def listing_report(
    items: list[dict],
    policy: HeldPolicy | None = None,
) -> dict[str, list[dict]]:
    """Group items ({ma, landed, sizes}) into listed / flagged / skipped. Writes nothing."""
    rules = policy or load_held_policy()
    report: dict[str, list[dict]] = {"listed": [], "flagged": [], "skipped": []}
    for item in items:
        q = listing_quote(item["ma"], item.get("landed"), rules, sizes_raw=item.get("sizes"))
        row = {"ma": q.ma, "action": q.action, "sell_usd": q.sell_usd, "reason": q.reason, "sizes": list(q.sizes)}
        if q.action in ("quote", "locked"):
            report["listed"].append(row)
        elif q.action == "flag-size":
            report["flagged"].append(row)
        else:
            report["skipped"].append(row)
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Print a tiered sell quote. Does not write intake, Blob, or Meta.",
    )
    parser.add_argument("--landed", required=True, help="Landed USD. Not an intake ¥.")
    parser.add_argument("--ma", default="", help="Optional mã. Held mãs and never-list mãs are skipped.")
    parser.add_argument("--sizes", default=None, help="Optional raw intake sizes; invalid sizes are flagged, not listed.")
    args = parser.parse_args(argv)
    policy = load_held_policy()
    if args.ma.strip():
        quote = listing_quote(args.ma, args.landed, policy, sizes_raw=args.sizes)
        print(
            json.dumps(
                {
                    "ma": quote.ma,
                    "action": quote.action,
                    "sell_usd": quote.sell_usd,
                    "reason": quote.reason,
                    **({"sizes": list(quote.sizes)} if args.sizes is not None else {}),
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
