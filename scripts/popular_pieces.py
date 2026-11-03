"""Read-only popular list. Held mãs are omitted. Prices are not rewritten.

The check reads a fixture object or a fixture file. It does not read or
write the live popular ranking, catalog rows, prices, or data/held.json.
S06 stays $25 and is included only when the fixture says it is available.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from held_policy import norm_ma

MA_RE_TEXT = r"^[A-Z][0-9]{2}$"
S06 = "S06"
S06_USD = 25
HELD = "held"
UNAVAILABLE = "unavailable"

ROOT = Path(__file__).resolve().parents[1]
LIVE_FILES = (
    ROOT / "data" / "held.json",
    ROOT / "sassy-closet-shop" / "data" / "popular-order.json",
    ROOT / "sassy-closet-shop" / "data" / "products.json",
)


@dataclass(frozen=True)
class PopularPiece:
    ma: str
    price_usd: int | None
    available: bool | None


@dataclass(frozen=True)
class DroppedMa:
    ma: str
    reason: str


@dataclass(frozen=True)
class PopularList:
    pieces: tuple[PopularPiece, ...]
    dropped: tuple[DroppedMa, ...]

    def as_json(self) -> dict[str, list[dict[str, object]]]:
        return {
            "pieces": [
                {
                    "ma": piece.ma,
                    "priceUsd": piece.price_usd,
                    "available": piece.available,
                }
                for piece in self.pieces
            ],
            "dropped": [
                {"ma": item.ma, "reason": item.reason} for item in self.dropped
            ],
        }


def drop_held(
    pieces: tuple[PopularPiece, ...] | list[PopularPiece],
    held: tuple[str, ...] | list[str],
) -> PopularList:
    """Return a new list with held mãs omitted. Does not mutate pieces."""
    blocked = _held_codes(held)
    kept: list[PopularPiece] = []
    dropped: list[DroppedMa] = []
    for original in pieces:
        piece = _canonical(original)
        if piece.ma == S06 and piece.price_usd not in (None, S06_USD):
            raise ValueError("S06 stays $25")
        if piece.ma in blocked:
            dropped.append(DroppedMa(piece.ma, HELD))
            continue
        if piece.ma == S06 and piece.available is not True:
            dropped.append(DroppedMa(piece.ma, UNAVAILABLE))
            continue
        if piece.ma == S06 and piece.price_usd is None:
            raise ValueError("S06 stays $25")
        kept.append(piece)
    return PopularList(tuple(kept), tuple(dropped))


def check_fixture(payload: object) -> PopularList:
    """Filter one fixture object. Does not open a file."""
    if not isinstance(payload, dict):
        raise ValueError("fixture must be a JSON object")
    held = payload.get("held")
    raw_pieces = payload.get("pieces")
    if not isinstance(held, list) or not isinstance(raw_pieces, list):
        raise ValueError("fixture needs held and pieces lists")
    pieces = tuple(_piece(item) for item in raw_pieces)
    return drop_held(pieces, _held_list(held))


def read_fixture(path: Path) -> dict[str, object]:
    """Read a fixture file. Live ranking, catalog, and held.json are refused."""
    resolved = path.expanduser().resolve()
    if resolved in {item.resolve() for item in LIVE_FILES}:
        raise ValueError(
            "fixtures only; this check does not read the live popular ranking, catalog, or held list"
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
        description="Print a popular list with held mãs omitted. Reads a fixture and writes nothing.",
    )
    parser.add_argument("--fixture", required=True, help="Fixture JSON. Not a live ranking or catalog.")
    args = parser.parse_args(argv)
    try:
        result = check_fixture(read_fixture(Path(args.fixture)))
    except ValueError as error:
        print(str(error), file=sys.stderr)
        return 2
    print(json.dumps(result.as_json()))
    return 0


def _held_list(held: list[object]) -> list[str]:
    codes: list[str] = []
    for item in held:
        if not isinstance(item, str):
            raise ValueError("held list contains a non-string mã")
        codes.append(_code(item))
    return codes


def _held_codes(held: tuple[str, ...] | list[str]) -> frozenset[str]:
    return frozenset(_code(item) for item in held)


def _canonical(piece: PopularPiece) -> PopularPiece:
    code = _code(piece.ma)
    if code == piece.ma:
        return piece
    return PopularPiece(code, piece.price_usd, piece.available)


def _piece(item: object) -> PopularPiece:
    if not isinstance(item, dict):
        raise ValueError("popular piece must be an object")
    ma = item.get("ma")
    if not isinstance(ma, str):
        raise ValueError("popular piece needs a mã")
    code = _code(ma)
    return PopularPiece(code, _price(code, item.get("priceUsd")), _available(code, item.get("available")))


def _code(ma: str) -> str:
    code = norm_ma(ma)
    if re.fullmatch(MA_RE_TEXT, code) is None:
        raise ValueError(f"invalid mã {ma!r}")
    return code


def _price(ma: str, value: object) -> int | None:
    if value is None:
        return None
    if isinstance(value, bool):
        raise ValueError(f"{ma} price stays as written")
    if isinstance(value, int):
        return value
    if isinstance(value, str) and value.isdecimal():
        number = int(value)
        if str(number) != value:
            raise ValueError(f"{ma} price stays as written")
        return number
    raise ValueError(f"{ma} price stays as written")


def _available(ma: str, value: object) -> bool | None:
    if value is None:
        return None
    if isinstance(value, bool):
        return value
    raise ValueError(f"{ma} availability stays as written")


if __name__ == "__main__":
    raise SystemExit(main())
