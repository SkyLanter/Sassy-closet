"""Print S06's whole-dollar offer price from a PDP's Product JSON-LD. Read-only.

Prints the price (e.g. 25) when every S06 Product offer agrees on one whole
dollar; prints "?" and exits 1 when there is no S06 offer, offers disagree, or a
price is not a whole dollar. Neighbour cards on the page are ignored.
"""

from __future__ import annotations

import json
import re
import sys
from decimal import Decimal, InvalidOperation

from held_policy import norm_ma

_LD = re.compile(r'<script[^>]*type="application/ld\+json"[^>]*>(.*?)</script>', re.S | re.I)


def _nodes(value: object):
    if isinstance(value, list):
        for item in value:
            yield from _nodes(item)
    elif isinstance(value, dict):
        yield value
        for key in ("@graph", "itemListElement", "item"):
            if key in value:
                yield from _nodes(value[key])


def _is_s06(node: dict) -> bool:
    for key in ("sku", "mpn", "productID"):
        if norm_ma(node.get(key)) == "S06":
            return True
    url = str(node.get("url") or node.get("@id") or "")
    return re.search(r"/m/S0*6(?:[/?#]|$)", url, re.I) is not None


def s06_prices(html: str) -> list[Decimal]:
    prices: list[Decimal] = []
    for block in _LD.findall(html):
        try:
            data = json.loads(block)
        except ValueError:
            continue
        for node in _nodes(data):
            types = node.get("@type")
            types = types if isinstance(types, list) else [types]
            if "Product" not in types or not _is_s06(node):
                continue
            offers = node.get("offers")
            for offer in offers if isinstance(offers, list) else [offers]:
                if isinstance(offer, dict) and offer.get("price") is not None:
                    try:
                        prices.append(Decimal(str(offer["price"]).replace("$", "").strip()))
                    except InvalidOperation:
                        prices.append(Decimal("NaN"))
    return prices


def s06_offer_dollars(html: str) -> int | None:
    prices = s06_prices(html)
    if not prices or any(not p.is_finite() or p != p.to_integral_value() for p in prices):
        return None
    whole = {int(p) for p in prices}
    return whole.pop() if len(whole) == 1 else None


def main(argv: list[str]) -> int:
    with open(argv[1], encoding="utf-8", errors="replace") as fh:
        dollars = s06_offer_dollars(fh.read())
    print("?" if dollars is None else dollars)
    return 0 if dollars is not None else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
