"""Flag a fixture popular list when the same mã appears twice.

Read-only. The list is reported in its given order and is not rewritten.
Prices are copied into the report and are not changed. S06 stays $25.
This module does not read or write data/held.json or
sassy-closet-shop/data/popular-order.json.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from held_policy import norm_ma

MA_RE = re.compile(r"^[A-Z][0-9]{2}$")
S06 = "S06"
S06_USD = 25
REPEATED = "repeated"

ROOT = Path(__file__).resolve().parents[1]
LIVE_FILES = (
    ROOT / "data" / "held.json",
    ROOT / "sassy-closet-shop" / "data" / "popular-order.json",
    ROOT / "sassy-closet-shop" / "data" / "products.json",
)


@dataclass(frozen=True)
class PopularEntry:
    ma: str
    price_usd: int | None


@dataclass(frozen=True)
class RepeatFlag:
    ma: str
    count: int
    indexes: tuple[int, ...]
    prices: tuple[int | None, ...]

    @property
    def kind(self) -> str:
        return REPEATED


@dataclass(frozen=True)
class RepeatReport:
    order: tuple[PopularEntry, ...]
    flags: tuple[RepeatFlag, ...]
    rewritten: bool

    def as_json(self) -> dict[str, object]:
        return {
            "order": [
                {"ma": entry.ma, "priceUsd": entry.price_usd} for entry in self.order
            ],
            "flags": [
                {
                    "ma": flag.ma,
                    "kind": flag.kind,
                    "count": flag.count,
                    "indexes": list(flag.indexes),
                    "prices": list(flag.prices),
                }
                for flag in self.flags
            ],
            "rewritten": self.rewritten,
        }


def flag_repeats(payload: object) -> RepeatReport:
    """Report mãs that appear twice. Leave the fixture object as it was."""
    entries = _entries(payload)
    seen: dict[str, list[int]] = {}
    prices: dict[str, list[int | None]] = {}
    first: list[str] = []
    order: list[PopularEntry] = []
    for index, entry in enumerate(entries):
        order.append(entry)
        if entry.ma not in seen:
            first.append(entry.ma)
            seen[entry.ma] = []
            prices[entry.ma] = []
        seen[entry.ma].append(index)
        prices[entry.ma].append(entry.price_usd)
    flags = tuple(
        RepeatFlag(code, len(seen[code]), tuple(seen[code]), tuple(prices[code]))
        for code in first
        if len(seen[code]) >= 2
    )
    return RepeatReport(tuple(order), flags, False)


def read_fixture(path: Path) -> dict[str, object]:
    """Read a fixture file. The live popular list and held list are refused."""
    resolved = path.expanduser().resolve()
    if resolved in {item.resolve() for item in LIVE_FILES}:
        raise ValueError(
            "fixtures only; this check does not read the live popular list or held list"
        )
    try:
        text = resolved.read_text(encoding="utf-8")
    except OSError as error:
        raise ValueError(f"fixture file cannot be read: {error.strerror}") from error
    try:
        payload = json.loads(text)
    except json.JSONDecodeError as error:
        raise ValueError(f"fixture must be JSON: {error.msg}") from error
    if not isinstance(payload, dict):
        raise ValueError("fixture must be a JSON object")
    return payload


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Flag a fixture popular list when the same mã appears twice. "
            "Does not rewrite the list or change a price."
        )
    )
    parser.add_argument(
        "--fixture",
        required=True,
        help="Fixture JSON. Not the live popular list or held list.",
    )
    args = parser.parse_args(argv)
    try:
        report = flag_repeats(read_fixture(Path(args.fixture)))
    except ValueError as error:
        print(str(error), file=sys.stderr)
        return 2
    print(json.dumps(report.as_json(), indent=2))
    return 0


def _entries(payload: object) -> list[PopularEntry]:
    if not isinstance(payload, dict):
        raise ValueError("fixture must be a JSON object")
    raw = payload.get("order", payload.get("pieces"))
    if "order" not in payload and "pieces" not in payload:
        raise ValueError("fixture needs an order list")
    if not isinstance(raw, list):
        raise ValueError("fixture order must be a list")
    return [_entry(item) for item in raw]


def _entry(item: object) -> PopularEntry:
    if isinstance(item, str):
        return PopularEntry(_code(item), None)
    if not isinstance(item, dict):
        raise ValueError("popular entry must be a mã or an object")
    ma = item.get("ma")
    if not isinstance(ma, str):
        raise ValueError("popular entry needs a mã")
    code = _code(ma)
    return PopularEntry(code, _price(code, item.get("priceUsd") if "priceUsd" in item else None))


def _code(ma: str) -> str:
    code = norm_ma(ma)
    if MA_RE.fullmatch(code) is None:
        raise ValueError(f"invalid mã {ma!r}")
    return code


def _price(ma: str, value: object) -> int | None:
    if value is None:
        return None
    number = _whole_dollars(ma, value)
    if ma == S06 and number != S06_USD:
        raise ValueError("S06 stays $25")
    return number


def _whole_dollars(ma: str, value: object) -> int:
    if isinstance(value, bool) or not isinstance(value, (int, str)):
        raise ValueError(f"{ma} price stays as written")
    if isinstance(value, int):
        if value < 0:
            raise ValueError(f"{ma} price stays as written")
        return value
    if not value.isdecimal():
        raise ValueError(f"{ma} price stays as written")
    number = int(value)
    if str(number) != value:
        raise ValueError(f"{ma} price stays as written")
    return number


if __name__ == "__main__":
    raise SystemExit(main())
