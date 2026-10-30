"""Flag a fixture popular entry when its mã is blank.

Read-only. The list is reported as given and is not rewritten.
A blank mã is copied into the flag and is not filled in.
S06 stays $25. An entry whose mã is S06 at $25 is not a blank flag.
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
BLANK = "blank"

ROOT = Path(__file__).resolve().parents[1]
LIVE_FILES = (
    ROOT / "data" / "held.json",
    ROOT / "sassy-closet-shop" / "data" / "popular-order.json",
    ROOT / "sassy-closet-shop" / "data" / "products.json",
)


@dataclass(frozen=True)
class PopularEntry:
    code: str
    stored: object
    price_usd: int | None
    blank: bool
    reason: str | None


@dataclass(frozen=True)
class BlankFlag:
    index: int
    stored: object
    price_usd: int | None
    reason: str

    @property
    def kind(self) -> str:
        return BLANK

    @property
    def ma(self) -> str:
        return ""

    @property
    def filled(self) -> bool:
        return False

    def as_json(self) -> dict[str, object]:
        return {
            "index": self.index,
            "kind": self.kind,
            "reason": self.reason,
            "ma": self.ma,
            "stored": self.stored,
            "priceUsd": self.price_usd,
            "filled": self.filled,
        }


@dataclass(frozen=True)
class BlankReport:
    order: tuple[PopularEntry, ...]
    flags: tuple[BlankFlag, ...]

    @property
    def filled(self) -> bool:
        return False

    @property
    def rewritten(self) -> bool:
        return False

    def as_json(self) -> dict[str, object]:
        return {
            "order": [_entry_json(index, entry) for index, entry in enumerate(self.order)],
            "flags": [flag.as_json() for flag in self.flags],
            "filled": self.filled,
            "rewritten": self.rewritten,
        }


def flag_blank_mas(payload: object) -> BlankReport:
    """Report popular entries whose mã is blank. Leave the fixture object as it was."""
    entries = _entries(payload)
    flags = tuple(
        BlankFlag(index, entry.stored, entry.price_usd, _known_reason(entry.reason))
        for index, entry in enumerate(entries)
        if entry.blank
    )
    return BlankReport(tuple(entries), flags)


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
            "Flag a fixture popular entry whose mã is blank. "
            "Does not fill a mã or change a price."
        )
    )
    parser.add_argument(
        "--fixture",
        required=True,
        help="Fixture JSON. Not the live popular list or held list.",
    )
    args = parser.parse_args(argv)
    try:
        report = flag_blank_mas(read_fixture(Path(args.fixture)))
    except ValueError as error:
        print(str(error), file=sys.stderr)
        return 2
    print(json.dumps(report.as_json(), indent=2))
    return 1 if report.flags else 0


def _entries(payload: object) -> list[PopularEntry]:
    if not isinstance(payload, dict):
        raise ValueError("fixture must be a JSON object")
    if "order" not in payload and "pieces" not in payload:
        raise ValueError("fixture needs an order list")
    raw = payload.get("order", payload.get("pieces"))
    if not isinstance(raw, list):
        raise ValueError("fixture order must be a list")
    return [_entry(item) for item in raw]


def _entry(item: object) -> PopularEntry:
    if isinstance(item, str):
        return _from_text(item, None)
    if not isinstance(item, dict):
        raise ValueError("popular entry must be a mã or an object")
    present = "ma" in item
    price_raw = item.get("priceUsd") if "priceUsd" in item else None
    if not present:
        return PopularEntry("", "", _price("", price_raw, blank=True), True, "missing")
    return _from_value(item.get("ma"), price_raw)


def _from_value(ma: object, price_raw: object) -> PopularEntry:
    if ma is None:
        return PopularEntry("", None, _price("", price_raw, blank=True), True, "null")
    if not isinstance(ma, str):
        raise ValueError("popular entry mã stays as written")
    return _from_text(ma, price_raw)


def _from_text(ma: str, price_raw: object) -> PopularEntry:
    if ma.strip() == "":
        return PopularEntry("", ma, _price("", price_raw, blank=True), True, "blank")
    code = norm_ma(ma)
    if MA_RE.fullmatch(code) is None:
        raise ValueError(f"invalid mã {ma!r}")
    return PopularEntry(code, ma, _price(code, price_raw, blank=False), False, None)


def _price(code: str, value: object, *, blank: bool) -> int | None:
    if value is None:
        return None
    label = "blank mã" if blank else code
    number = _whole_dollars(value, label)
    if not blank and code == S06 and number != S06_USD:
        raise ValueError("S06 stays $25")
    return number


def _whole_dollars(value: object, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, (int, str)):
        raise ValueError(f"{label} price stays as written")
    if isinstance(value, int):
        if value < 0:
            raise ValueError(f"{label} price stays as written")
        return value
    if not value.isdecimal():
        raise ValueError(f"{label} price stays as written")
    number = int(value)
    if str(number) != value:
        raise ValueError(f"{label} price stays as written")
    return number


def _known_reason(reason: str | None) -> str:
    if reason == "missing" or reason == "null" or reason == "blank":
        return reason
    raise ValueError("blank mã stays blank")


def _entry_json(index: int, entry: PopularEntry) -> dict[str, object]:
    return {
        "index": index,
        "ma": "" if entry.blank else entry.code,
        "stored": entry.stored,
        "priceUsd": entry.price_usd,
        "blank": entry.blank,
    }


if __name__ == "__main__":
    raise SystemExit(main())
