"""Flag a fixture size list that repeats a size.

S, M, S is a repeated S. The stored list is copied into the flag with
both copies still there. A single size stays quiet. Comparison ignores
case and surrounding space. This module only reads a fixture passed on
the command line. It does not write catalog rows or change a price.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from held_policy import norm_ma

Source = Literal["catalog", "intake"]
SOURCES: tuple[Source, ...] = ("catalog", "intake")
_SPLIT = re.compile(r"[,;/|]+")


@dataclass(frozen=True)
class SizeList:
    ma: str
    source: Source
    stored: str
    parts: tuple[str, ...]
    price_usd: int | None = None


@dataclass(frozen=True)
class SizeRepeatFlag:
    ma: str
    source: Source
    kind: str
    stored: str
    size: str
    count: int
    indexes: tuple[int, ...]

    def as_json(self) -> dict[str, str | int | list[int]]:
        return {
            "ma": self.ma,
            "source": self.source,
            "kind": self.kind,
            "stored": self.stored,
            "size": self.size,
            "count": self.count,
            "indexes": list(self.indexes),
        }


def flag_repeated_sizes(rows: list[SizeList]) -> list[SizeRepeatFlag]:
    """Return flags. Leave every SizeList.parts, stored text, and price as passed in."""
    flags: list[SizeRepeatFlag] = []
    for row in rows:
        source = _check_source(row.source)
        for size, indexes in _repeats(row.parts):
            flags.append(
                SizeRepeatFlag(
                    norm_ma(row.ma),
                    source,
                    "repeated_size",
                    row.stored,
                    size,
                    len(indexes),
                    indexes,
                )
            )
    return flags


def repeated_sizes(parts: tuple[str, ...]) -> list[str]:
    """Size text that appears more than once, in first-seen order."""
    return [size for size, _indexes in _repeats(parts)]


def rows_from_fixture(payload: object) -> list[SizeList]:
    if not isinstance(payload, dict):
        raise ValueError("fixture must be an object with catalog and intake lists")
    extra = sorted(set(payload) - set(SOURCES))
    if extra:
        raise ValueError(f"fixture may only contain catalog and intake, found {extra}")
    missing = [source for source in SOURCES if source not in payload]
    if missing:
        raise ValueError(f"fixture needs catalog and intake lists, missing {missing}")
    rows: list[SizeList] = []
    for source in SOURCES:
        rows.extend(_rows(payload[source], source))
    return rows


def load_fixture(path: Path) -> list[SizeList]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return rows_from_fixture(payload)


def report_json(flags: list[SizeRepeatFlag]) -> str:
    body = {"readOnly": True, "flags": [flag.as_json() for flag in flags]}
    return json.dumps(body, ensure_ascii=False, indent=2) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Report a size list that repeats a size. Reads a fixture only."
    )
    parser.add_argument("--fixture", help="Fixture JSON with catalog and intake size lists.")
    args = parser.parse_args(argv)
    if not args.fixture:
        print(
            "Pass --fixture. This check reads a fixture only and does not open the live catalog.",
            file=sys.stderr,
        )
        return 2
    path = Path(args.fixture)
    try:
        _reject_live(args.fixture)
        flags = flag_repeated_sizes(load_fixture(path))
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(str(error), file=sys.stderr)
        return 2
    sys.stdout.write(report_json(flags))
    return 0


def _check_source(source: str) -> Source:
    if source == "catalog":
        return "catalog"
    if source == "intake":
        return "intake"
    raise ValueError(f"size source must be catalog or intake, found {source!r}")


def _repeats(parts: tuple[str, ...]) -> list[tuple[str, tuple[int, ...]]]:
    grouped: dict[str, list[int]] = {}
    display: dict[str, str] = {}
    order: list[str] = []
    for index, part in enumerate(parts):
        token = part.strip()
        if token == "":
            continue
        key = token.casefold()
        if key not in grouped:
            grouped[key] = []
            display[key] = token
            order.append(key)
        grouped[key].append(index)
    found: list[tuple[str, tuple[int, ...]]] = []
    for key in order:
        indexes = tuple(grouped[key])
        if len(indexes) < 2:
            continue
        found.append((display[key], indexes))
    return found


def _rows(value: object, source: Source) -> list[SizeList]:
    if not isinstance(value, list):
        raise ValueError(f"{source} must be a list")
    rows: list[SizeList] = []
    for item in value:
        if not isinstance(item, dict):
            raise ValueError(f"{source} row needs a mã")
        ma = item.get("ma")
        if not isinstance(ma, str) or ma.strip() == "":
            raise ValueError(f"{source} row needs a mã")
        if "size" in item and "sizes" in item:
            raise ValueError(f"{source} row {ma} has both size and sizes")
        price = _price(item)
        if "size" in item:
            stored, parts = _size_text(item.get("size"), source)
            rows.append(SizeList(ma, source, stored, parts, price))
            continue
        if "sizes" in item:
            stored, parts = _size_list(item.get("sizes"), ma, source)
            rows.append(SizeList(ma, source, stored, parts, price))
            continue
        rows.append(SizeList(ma, source, "", (), price))
    return rows


def _size_text(raw: object, source: Source) -> tuple[str, tuple[str, ...]]:
    if raw is None:
        return "", ()
    if isinstance(raw, str):
        parts = tuple(piece.strip() for piece in _SPLIT.split(raw) if piece.strip() != "")
        return raw, parts
    raise ValueError(f"{source} size text must be a string or null")


def _size_list(raw: object, ma: str, source: Source) -> tuple[str, tuple[str, ...]]:
    if not isinstance(raw, list) or not all(isinstance(part, str) for part in raw):
        raise ValueError(f"{source} sizes for {ma} must be a list of strings")
    parts = tuple(raw)
    return ", ".join(parts), parts


def _price(item: dict[str, object]) -> int | None:
    if "priceUsd" not in item:
        return None
    value = item["priceUsd"]
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"{item.get('ma')} priceUsd must be a whole dollar or null")
    return value


def _reject_live(raw: str) -> None:
    if "://" in raw:
        raise ValueError("fixtures only; refusing a URL")
    path = Path(raw).resolve()
    root = Path(__file__).resolve().parents[1]
    banned = {
        (root / "data" / "held.json").resolve(),
        (root / "sassy-closet-shop" / "data" / "products.json").resolve(),
        (root / "sassy-closet-shop" / "data" / "intake-extras.json").resolve(),
    }
    if path in banned:
        raise ValueError("fixtures only; refusing the shop catalog and held list")


if __name__ == "__main__":
    raise SystemExit(main())
