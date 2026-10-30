"""List catalog mãs whose status is sold and write a restock note.

Read-only. The catalog is a local fixture. The only file this writes is the
note path passed by the caller. It does not change catalog rows, prices, or
data/held.json. It does not post to Meta or mark a mã sold or available.

A fixture held list is parsed with load_held_policy through a temporary file
so this module does not keep a second held-list parser. That temporary file
is removed. data/held.json is not written.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import tempfile
from collections.abc import Sequence
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path

from held_policy import HeldPolicy, default_held_path, load_held_policy, norm_ma

S06 = "S06"
S06_USD = "25"
_PRICE_RE = re.compile(r"\d+(?:\.\d+)?")
_FORBIDDEN_NOTE_NAMES = frozenset(
    {"held.json", "catalog.v1.json", "products.json", "submissions.json"}
)
_FORBIDDEN_NOTE_ROOTS = frozenset({"data", "sassy-closet", "sassy-closet-shop"})


@dataclass(frozen=True)
class CatalogRow:
    ma: str
    status: str
    price_usd: str | None
    title: str


@dataclass(frozen=True)
class SoldPiece:
    ma: str
    title: str
    price_usd: str | None
    restock: bool
    reason: str


@dataclass(frozen=True)
class Stay:
    ma: str
    status: str | None
    detail: str


@dataclass(frozen=True)
class RestockNote:
    sold: tuple[SoldPiece, ...]
    stays: tuple[Stay, ...]
    s06_usd: str | None
    catalog_count: int

    @property
    def restock_count(self) -> int:
        return sum(1 for piece in self.sold if piece.restock)


def note_from_json(payload: object, policy: HeldPolicy | None = None) -> RestockNote:
    if not isinstance(payload, dict):
        raise ValueError("fixture must be a JSON object")
    if "held" in payload:
        if policy is not None:
            raise ValueError("pass held in the fixture or as a policy, not both")
        rules = _policy_from_mapping(payload.get("held"))
    else:
        rules = policy if policy is not None else load_held_policy()
    return note_from_catalog(_catalog_value(payload), rules)


def note_from_catalog(catalog: object, policy: HeldPolicy) -> RestockNote:
    rows = _catalog_rows(catalog)
    s06_usd = _s06_price(rows)
    by_ma = {row.ma: row for row in rows}
    sold_rows = [row for row in rows if row.status == "sold"]
    sold = tuple(
        sorted((_sold_piece(row, policy) for row in sold_rows), key=lambda piece: piece.ma)
    )
    stays = _stays(by_ma, policy)
    return RestockNote(sold, stays, s06_usd, len(rows))


def render_note(note: RestockNote) -> str:
    lines = [
        "# Restock note",
        "",
        "Read-only list of catalog mãs whose status is sold.",
        "This note does not change catalog rows, prices, or held mãs.",
        "It does not post to Meta.",
        "It does not mark anything sold or available.",
        "",
        (
            f"Catalog rows read: {note.catalog_count}. "
            f"Sold: {len(note.sold)}. Restock: {note.restock_count}."
        ),
        "",
        "## Sold",
        "",
    ]
    if not note.sold:
        lines.append("none")
    else:
        lines.extend(_sold_line(piece) for piece in note.sold)
    lines.extend(["", "## Stays held", "", "Held mãs stay held.", ""])
    if not note.stays:
        lines.append("none")
    else:
        lines.extend(_stay_line(stay) for stay in note.stays)
    lines.extend(["", "## S06", ""])
    if note.s06_usd is None:
        lines.append("S06 was not in this catalog. No price was written.")
    else:
        lines.append("S06 stays $25.")
    lines.extend(
        [
            "",
            "## Left alone",
            "",
            "Catalog rows, prices, and data/held.json were not written.",
            "No Blob, intake, Meta, or Square write.",
            "",
        ]
    )
    return "\n".join(lines)


def render_json(note: RestockNote) -> dict[str, object]:
    return {
        "sold": [
            {
                "ma": piece.ma,
                "title": piece.title,
                "priceUsd": piece.price_usd,
                "restock": piece.restock,
                "reason": piece.reason,
            }
            for piece in note.sold
        ],
        "staysHeld": [
            {"ma": stay.ma, "status": stay.status, "detail": stay.detail} for stay in note.stays
        ],
        "s06Usd": note.s06_usd,
        "catalogCount": note.catalog_count,
        "soldCount": len(note.sold),
        "restockCount": note.restock_count,
        "writes": [],
    }


def write_note(note: RestockNote, path: Path, *, source: Path | None = None) -> None:
    _refuse_note_target(path, source)
    body = render_note(note)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "List sold catalog mãs and write a restock note. "
            "Does not change catalog rows, prices, or data/held.json."
        )
    )
    parser.add_argument("--fixture", required=True, help="Local catalog JSON fixture.")
    parser.add_argument("--note", required=True, help="Markdown path for the restock note.")
    parser.add_argument("--held", help="Held policy JSON. Defaults to data/held.json.")
    parser.add_argument("--json", action="store_true", help="Print JSON instead of the note.")
    args = parser.parse_args(argv)
    note_path = Path(args.note)
    try:
        _refuse_remote(args.fixture)
        fixture_path = Path(args.fixture)
        payload = json.loads(fixture_path.read_text(encoding="utf-8"))
        policy = _cli_policy(payload, args.held)
        note = note_from_json(payload, policy)
        write_note(note, note_path, source=fixture_path)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(str(error), file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps(render_json(note), indent=2))
    else:
        print(render_note(note), end="")
        print(f"note: {args.note}")
    return 0


def _cli_policy(payload: object, held: str | None) -> HeldPolicy | None:
    if isinstance(payload, dict) and "held" in payload:
        if held:
            raise ValueError("fixture held and --held cannot both be set")
        return None
    if held:
        _refuse_remote(held)
        return load_held_policy(Path(held))
    return None


def _catalog_value(payload: dict[str, object]) -> object:
    if "catalog" in payload:
        return payload["catalog"]
    if "products" in payload:
        return payload
    raise ValueError("fixture needs catalog products")


def _catalog_rows(catalog: object) -> list[CatalogRow]:
    rows = _product_list(catalog)
    parsed: list[CatalogRow] = []
    seen: set[str] = set()
    for item in rows:
        if not isinstance(item, dict):
            raise ValueError("catalog row must be an object")
        ma = _ma(item.get("ma"))
        if ma in seen:
            raise ValueError(f"duplicate mã {ma}")
        seen.add(ma)
        parsed.append(
            CatalogRow(ma, _status(item.get("status"), ma), _price(item, ma), _title(item))
        )
    return parsed


def _product_list(catalog: object) -> list[object]:
    if isinstance(catalog, list):
        return list(catalog)
    if isinstance(catalog, dict) and isinstance(catalog.get("products"), list):
        return list(catalog["products"])
    raise ValueError("catalog must be a list of products")


def _sold_piece(row: CatalogRow, policy: HeldPolicy) -> SoldPiece:
    reason = policy.skip_reason(row.ma)
    if reason == "held":
        return SoldPiece(row.ma, row.title, row.price_usd, False, "held")
    if reason == "never-list":
        return SoldPiece(row.ma, row.title, row.price_usd, False, "never-list")
    if reason is None:
        return SoldPiece(row.ma, row.title, row.price_usd, True, "")
    raise AssertionError(f"unexpected skip reason {reason!r}")


def _stays(by_ma: dict[str, CatalogRow], policy: HeldPolicy) -> tuple[Stay, ...]:
    stays: list[Stay] = []
    for code in policy.held:
        stays.append(
            _stay(
                code,
                by_ma.get(code),
                "stays held, not a restock",
                "not in this catalog — stays held",
            )
        )
    for code in policy.never_list:
        stays.append(
            _stay(
                code,
                by_ma.get(code),
                "stays unlist, not a restock",
                "not in this catalog — stays unlist",
            )
        )
    return tuple(stays)


def _stay(code: str, row: CatalogRow | None, present: str, absent: str) -> Stay:
    if row is None:
        return Stay(code, None, absent)
    return Stay(code, row.status, present)


def _s06_price(rows: Sequence[CatalogRow]) -> str | None:
    found = [row for row in rows if row.ma == S06]
    if not found:
        return None
    price = found[0].price_usd
    if price != S06_USD:
        raise ValueError("S06 stays $25")
    return price


def _sold_line(piece: SoldPiece) -> str:
    if piece.restock:
        parts = [piece.ma]
        if piece.title:
            parts.append(piece.title)
        parts.append("no stored price" if piece.price_usd is None else f"${piece.price_usd}")
        return "- " + " — ".join(parts)
    if piece.reason == "held":
        return f"- {piece.ma} — stays held, not a restock"
    if piece.reason == "never-list":
        return f"- {piece.ma} — stays unlist, not a restock"
    raise AssertionError(f"unexpected sold reason {piece.reason!r}")


def _stay_line(stay: Stay) -> str:
    if stay.status is None:
        return f"- {stay.ma} — {stay.detail}"
    return f"- {stay.ma} — status {stay.status} — {stay.detail}"


def _ma(value: object) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError("catalog row needs a mã")
    code = norm_ma(value)
    if re.fullmatch(r"[A-Z][0-9]{2}", code) is None:
        raise ValueError(f"invalid mã {value!r}")
    return code


def _status(value: object, ma: str) -> str:
    if value == "available" or value == "hold" or value == "sold":
        return value
    raise ValueError(f"{ma} status must be available, hold, or sold")


def _title(item: dict[str, object]) -> str:
    for key in ("titleEn", "title_en", "titleVn", "title_vn"):
        value = item.get(key)
        if isinstance(value, str) and value.strip():
            return " ".join(value.split())
    return ""


def _price(item: dict[str, object], ma: str) -> str | None:
    present = [key for key in ("priceUsd", "price_usd") if key in item]
    if not present:
        return None
    parsed = [_whole_dollars(item[key], ma) for key in present]
    if len(set(parsed)) != 1:
        raise ValueError(f"{ma} prices disagree")
    return parsed[0]


def _whole_dollars(value: object, ma: str) -> str | None:
    if value is None:
        return None
    if isinstance(value, bool):
        raise ValueError(f"{ma} price is not a whole dollar")
    if isinstance(value, int):
        return _non_negative(value, ma)
    if isinstance(value, float):
        if value != value or value != int(value):
            raise ValueError(f"{ma} price is not a whole dollar")
        return _non_negative(int(value), ma)
    if isinstance(value, str):
        text = value.strip()
        if text.startswith("$"):
            text = text[1:].strip()
        if _PRICE_RE.fullmatch(text) is None:
            raise ValueError(f"{ma} price is not a whole dollar")
        number = Decimal(text)
        if number != number.to_integral_value():
            raise ValueError(f"{ma} price is not a whole dollar")
        return _non_negative(int(number), ma)
    raise ValueError(f"{ma} price is not a whole dollar")


def _non_negative(value: int, ma: str) -> str:
    if value < 0:
        raise ValueError(f"{ma} price is not a whole dollar")
    return str(value)


def _policy_from_mapping(value: object) -> HeldPolicy:
    if not isinstance(value, dict):
        raise ValueError("held must be a JSON object")
    fd, name = tempfile.mkstemp(suffix=".json")
    path = Path(name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(value, handle)
        return load_held_policy(path)
    finally:
        path.unlink(missing_ok=True)


def _refuse_remote(value: str) -> None:
    text = value.strip().lower()
    if text.startswith("http://") or text.startswith("https://"):
        raise ValueError("catalog must be a local fixture, not a URL")


def _refuse_note_target(path: Path, source: Path | None) -> None:
    resolved = path if path.is_absolute() else Path.cwd() / path
    resolved = resolved.resolve()
    if source is not None:
        source_resolved = source if source.is_absolute() else Path.cwd() / source
        if resolved == source_resolved.resolve():
            raise ValueError("refusing to overwrite the catalog fixture")
    if resolved == default_held_path().resolve() or resolved.name in _FORBIDDEN_NOTE_NAMES:
        raise ValueError(f"refusing to write {resolved.name}")
    if resolved.suffix.lower() not in {".md", ".markdown"}:
        raise ValueError("restock note must be a markdown file")
    repo = Path(__file__).resolve().parents[1]
    try:
        relative = resolved.relative_to(repo)
    except ValueError:
        relative = None
    if relative is not None and relative.parts and relative.parts[0] in _FORBIDDEN_NOTE_ROOTS:
        raise ValueError("refusing to write inside the shop app or data/")


if __name__ == "__main__":
    raise SystemExit(main())
