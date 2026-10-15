"""Flag a fixture size token outside the known set.

Known tokens are S, M, L, XL, XXL, XS, and a plain number such as 36.
A list of S M L stays quiet. 2XL is outside that set, so the flag keeps
2XL. The stored text is copied into the flag. This module only reads a
fixture passed on the command line. It does not write catalog rows or
change a price.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

Source = Literal["catalog", "intake"]
SOURCES: tuple[Source, ...] = ("catalog", "intake")
KNOWN_SIZE_TOKENS: tuple[str, ...] = ("S", "M", "L", "XL", "XXL", "XS")
_KNOWN = frozenset(token.casefold() for token in KNOWN_SIZE_TOKENS)
_PLAIN_NUMBER = re.compile(r"[0-9]+")
_TOKENS = re.compile(r"[\s,;/|]+")


@dataclass(frozen=True)
class SizeList:
    ma: str
    source: Source
    stored: str
    parts: tuple[str, ...]
    price_usd: int | None = None


@dataclass(frozen=True)
class SizeTokenFlag:
    ma: str
    source: Source
    kind: str
    stored: str
    token: str
    index: int

    def as_json(self) -> dict[str, str | int]:
        return {
            "ma": self.ma,
            "source": self.source,
            "kind": self.kind,
            "stored": self.stored,
            "token": self.token,
            "index": self.index,
        }


def flag_unknown_sizes(rows: list[SizeList]) -> list[SizeTokenFlag]:
    """Return flags. Leave every SizeList.parts, stored text, and price as passed in."""
    flags: list[SizeTokenFlag] = []
    for row in rows:
        source = _check_source(row.source)
        for token, index in _unknown(row.parts):
            flags.append(
                SizeTokenFlag(
                    row.ma.strip().upper(),
                    source,
                    "unknown_size",
                    row.stored,
                    token,
                    index,
                )
            )
    return flags


def unknown_sizes(parts: tuple[str, ...]) -> list[str]:
    """Tokens outside the known set, in list order."""
    return [token for token, _index in _unknown(parts)]


def is_known_size_token(token: str) -> bool:
    """True for S, M, L, XL, XXL, XS, any letter case, or a plain number."""
    if token.casefold() in _KNOWN:
        return True
    return _PLAIN_NUMBER.fullmatch(token) is not None


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


def report_json(flags: list[SizeTokenFlag]) -> str:
    body = {"readOnly": True, "flags": [flag.as_json() for flag in flags]}
    return json.dumps(body, ensure_ascii=False, indent=2) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Report a size token outside the known set. Reads a fixture only."
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
        flags = flag_unknown_sizes(load_fixture(path))
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


def _unknown(parts: tuple[str, ...]) -> list[tuple[str, int]]:
    found: list[tuple[str, int]] = []
    index = 0
    for part in parts:
        for token in _tokens(part):
            if not is_known_size_token(token):
                found.append((token, index))
            index += 1
    return found


def _tokens(text: str) -> tuple[str, ...]:
    return tuple(piece for piece in _TOKENS.split(text) if piece != "")


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
        return raw, _tokens(raw)
    raise ValueError(f"{source} size text must be a string or null")


def _size_list(raw: object, ma: str, source: Source) -> tuple[str, tuple[str, ...]]:
    if not isinstance(raw, list) or not all(isinstance(part, str) for part in raw):
        raise ValueError(f"{source} sizes for {ma} must be a list of strings")
    parts = tuple(piece for part in raw for piece in _tokens(part))
    return ", ".join(raw), parts


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
