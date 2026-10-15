"""Flag popular mãs that are absent from a catalog fixture.

Read-only. A popular fixture and a catalog fixture are read and left
unchanged. A popular mã that is not in the catalog is flagged. The mã is
not added to the catalog. Prices are copied into the report and are not
rewritten. This check does not read or write data/held.json, the live
popular ranking, or the live catalog. S06 stays $25 and stays clean when
that mã is in both fixtures at $25.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

MA_RE = re.compile(r"^[A-Z][0-9]{2}$")
S06 = "S06"
S06_USD = 25
ABSENT = "absent_from_catalog"

ROOT = Path(__file__).resolve().parents[1]
LIVE_FILES = (
    ROOT / "data" / "held.json",
    ROOT / "sassy-closet-shop" / "data" / "popular-order.json",
    ROOT / "sassy-closet-shop" / "data" / "products.json",
)


@dataclass(frozen=True)
class Piece:
    ma: str
    price_usd: int | None


@dataclass(frozen=True)
class MissingFlag:
    ma: str
    price_usd: int | None

    def as_json(self) -> dict[str, object]:
        return {
            "ma": self.ma,
            "kind": ABSENT,
            "priceUsd": self.price_usd,
        }


@dataclass(frozen=True)
class MissingReport:
    popular: tuple[Piece, ...]
    catalog: tuple[Piece, ...]
    flags: tuple[MissingFlag, ...]

    def as_json(self) -> dict[str, object]:
        return {
            "readOnly": True,
            "s06": "stays $25",
            "popular": [_piece_json(piece) for piece in self.popular],
            "catalog": [_piece_json(piece) for piece in self.catalog],
            "flagCount": len(self.flags),
            "flags": [flag.as_json() for flag in self.flags],
        }


def flag_popular_missing(
    popular: Sequence[Piece],
    catalog: Sequence[Piece],
) -> MissingReport:
    """Return flags for popular mãs missing from the catalog.

    Does not mutate either sequence and does not append a missing mã.
    """
    popular_rows = tuple(_canonical(piece) for piece in popular)
    catalog_rows = tuple(_canonical(piece) for piece in catalog)
    _require_s06(popular_rows)
    _require_s06(catalog_rows)
    present = {piece.ma for piece in catalog_rows}
    flags: list[MissingFlag] = []
    seen: set[str] = set()
    for piece in popular_rows:
        if piece.ma in present or piece.ma in seen:
            continue
        seen.add(piece.ma)
        flags.append(MissingFlag(piece.ma, piece.price_usd))
    return MissingReport(popular_rows, catalog_rows, tuple(flags))


def load_popular(path: Path) -> tuple[Piece, ...]:
    payload = _read_json(_guard(path))
    if not isinstance(payload, dict):
        raise ValueError("popular fixture must be a JSON object")
    pieces = payload.get("pieces")
    if not isinstance(pieces, list):
        raise ValueError("popular fixture needs a pieces list")
    return tuple(_piece(item) for item in pieces)


def load_catalog(path: Path) -> tuple[Piece, ...]:
    payload = _read_json(_guard(path))
    if not isinstance(payload, dict):
        raise ValueError("catalog fixture must be a JSON object")
    schema = payload.get("schema")
    if schema is not None and schema != "catalog.v1":
        raise ValueError("catalog fixture schema must be catalog.v1")
    version = payload.get("version")
    if version is not None and version != 1:
        raise ValueError("catalog fixture version must be 1")
    products = payload.get("products")
    if not isinstance(products, list):
        raise ValueError("catalog fixture needs a products list")
    return tuple(_piece(item) for item in products)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Flag popular mãs that are absent from a catalog fixture. "
            "Reads fixtures and writes nothing."
        ),
    )
    parser.add_argument("--popular", required=True, help="Popular fixture JSON. Not the live ranking.")
    parser.add_argument("--catalog", required=True, help="Catalog fixture JSON. Not the live catalog.")
    args = parser.parse_args(argv)
    try:
        report = flag_popular_missing(
            load_popular(_cli_path(args.popular)),
            load_catalog(_cli_path(args.catalog)),
        )
    except (OSError, UnicodeError, ValueError) as error:
        print(str(error), file=sys.stderr)
        return 2
    print(json.dumps(report.as_json(), ensure_ascii=False, indent=2))
    return 1 if report.flags else 0


def _require_s06(pieces: Sequence[Piece]) -> None:
    for piece in pieces:
        if piece.ma == S06 and piece.price_usd != S06_USD:
            raise ValueError("S06 stays $25")


def _canonical(piece: Piece) -> Piece:
    code = _code(piece.ma)
    if code == piece.ma:
        return piece
    return Piece(code, piece.price_usd)


def _piece(item: object) -> Piece:
    if not isinstance(item, dict):
        raise ValueError("piece must be an object")
    raw = item.get("ma")
    if not isinstance(raw, str):
        raise ValueError("piece needs a mã")
    code = _code(raw)
    return Piece(code, _price(code, item))


def _code(ma: str) -> str:
    code = ma.strip().upper()
    if MA_RE.fullmatch(code) is None:
        raise ValueError(f"invalid mã {ma!r}")
    return code


def _price(ma: str, item: dict[str, object]) -> int | None:
    if "priceUsd" not in item:
        if ma == S06:
            raise ValueError("S06 stays $25")
        return None
    value = item.get("priceUsd")
    if value is None:
        if ma == S06:
            raise ValueError("S06 stays $25")
        return None
    if isinstance(value, bool) or isinstance(value, float):
        raise ValueError(f"{ma} price stays as written")
    if isinstance(value, int):
        number = value
    elif isinstance(value, str) and value.isdecimal():
        number = int(value)
        if str(number) != value:
            raise ValueError(f"{ma} price stays as written")
    else:
        raise ValueError(f"{ma} price stays as written")
    if ma == S06 and number != S06_USD:
        raise ValueError("S06 stays $25")
    return number


def _piece_json(piece: Piece) -> dict[str, object]:
    body: dict[str, object] = {"ma": piece.ma}
    if piece.price_usd is not None:
        body["priceUsd"] = piece.price_usd
    return body


def _cli_path(value: str) -> Path:
    text = value.strip()
    folded = text.casefold()
    if folded.startswith("http://") or folded.startswith("https://"):
        raise ValueError("fixtures only; live catalogs are not read")
    return Path(text)


def _guard(path: Path) -> Path:
    resolved = path.expanduser().resolve()
    if resolved in {item.resolve() for item in LIVE_FILES}:
        raise ValueError(
            "fixtures only; this check does not read data/held.json, "
            "the live popular ranking, or the live catalog"
        )
    return resolved


def _read_json(path: Path) -> object:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as error:
        raise ValueError(f"fixture file cannot be read: {error.strerror}") from error
    try:
        return json.loads(text)
    except json.JSONDecodeError as error:
        raise ValueError(f"fixture must be JSON: {error.msg}") from error


if __name__ == "__main__":
    raise SystemExit(main())
