"""Compare two catalog JSON fixtures.

Reports added mãs, removed mãs, and price changes.
Reads the two fixture files and data/held.json.
Does not write Blob, the live catalog, data/held.json, or either fixture.
Does not change a price.
"""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
from collections.abc import Mapping
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path

from held_policy import HeldPolicy, default_held_path, load_held_policy, norm_ma

MA_RE = re.compile(r"^[A-Z][0-9]{2}$")
STATUSES = frozenset({"available", "hold", "sold"})
S06 = "S06"


@dataclass(frozen=True)
class CatalogRow:
    ma: str
    price_usd: Decimal | None
    status: str | None


@dataclass(frozen=True)
class PriceChange:
    ma: str
    before: str | None
    after: str | None


@dataclass(frozen=True)
class HeldRow:
    ma: str
    before_status: str | None
    after_status: str | None
    stays_held: bool


@dataclass(frozen=True)
class CatalogDiff:
    added: tuple[str, ...]
    removed: tuple[str, ...]
    price_changes: tuple[PriceChange, ...]
    s06_before: str | None
    s06_after: str | None
    held: tuple[HeldRow, ...]


def format_price(value: Decimal | None) -> str | None:
    if value is None:
        return None
    text = format(value, "f")
    if "." in text:
        text = text.rstrip("0").rstrip(".")
    return text


def parse_price(value: object, ma: str) -> Decimal | None:
    if value is None:
        return None
    if isinstance(value, bool):
        raise ValueError(f"{ma} priceUsd must be a number or null")
    if isinstance(value, int):
        number = Decimal(value)
    elif isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError(f"{ma} priceUsd must be a number or null")
        number = Decimal(str(value))
    else:
        raise ValueError(f"{ma} priceUsd must be a number or null")
    if number < 0:
        raise ValueError(f"{ma} priceUsd cannot be negative")
    return number


def parse_catalog(payload: object) -> dict[str, CatalogRow]:
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
    rows: dict[str, CatalogRow] = {}
    for item in products:
        row = _row(item)
        if row.ma in rows:
            raise ValueError(f"catalog fixture repeats {row.ma}")
        rows[row.ma] = row
    return rows


def load_catalog(path: str | Path) -> dict[str, CatalogRow]:
    fixture = _local_fixture(path)
    try:
        payload = json.loads(fixture.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise ValueError(f"{path} is not catalog JSON") from error
    return parse_catalog(payload)


def diff_catalogs(
    before: Mapping[str, CatalogRow],
    after: Mapping[str, CatalogRow],
    policy: HeldPolicy | None = None,
) -> CatalogDiff:
    """Describe mã and price differences. Does not mutate either catalog."""
    rules = load_held_policy() if policy is None else policy
    before_codes = set(before)
    after_codes = set(after)
    changes: list[PriceChange] = []
    for ma in sorted(before_codes & after_codes):
        left = before[ma].price_usd
        right = after[ma].price_usd
        if left != right:
            changes.append(PriceChange(ma, format_price(left), format_price(right)))
    held_notes: list[HeldRow] = []
    for ma in sorted(rules.held):
        left_row = before.get(ma)
        right_row = after.get(ma)
        if left_row is None and right_row is None:
            continue
        held_notes.append(
            HeldRow(
                ma=ma,
                before_status=None if left_row is None else left_row.status,
                after_status=None if right_row is None else right_row.status,
                stays_held=_stays_held(left_row, right_row),
            )
        )
    return CatalogDiff(
        added=tuple(sorted(after_codes - before_codes)),
        removed=tuple(sorted(before_codes - after_codes)),
        price_changes=tuple(changes),
        s06_before=_s06_price(before),
        s06_after=_s06_price(after),
        held=tuple(held_notes),
    )


def diff_catalog_files(
    before: str | Path,
    after: str | Path,
    policy: HeldPolicy | None = None,
) -> CatalogDiff:
    rules = load_held_policy() if policy is None else policy
    return diff_catalogs(load_catalog(before), load_catalog(after), rules)


def report_json(report: CatalogDiff) -> dict[str, object]:
    return {
        "added": list(report.added),
        "removed": list(report.removed),
        "priceChanges": [
            {"ma": change.ma, "before": change.before, "after": change.after}
            for change in report.price_changes
        ],
        "s06": {"before": report.s06_before, "after": report.s06_after},
        "held": [
            {
                "ma": row.ma,
                "beforeStatus": row.before_status,
                "afterStatus": row.after_status,
                "staysHeld": row.stays_held,
            }
            for row in report.held
        ],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Compare two catalog JSON fixtures and print added mãs, "
            "removed mãs, and price changes. Does not write."
        ),
    )
    parser.add_argument("--before", required=True, help="Earlier catalog fixture.")
    parser.add_argument("--after", required=True, help="Later catalog fixture.")
    args = parser.parse_args(argv)
    try:
        report = diff_catalog_files(args.before, args.after)
    except (OSError, ValueError) as error:
        print(error, file=sys.stderr)
        return 2
    print(json.dumps(report_json(report), indent=2))
    return 0


def _row(item: object) -> CatalogRow:
    if not isinstance(item, dict):
        raise ValueError("catalog product must be an object")
    raw_ma = item.get("ma")
    if not isinstance(raw_ma, str):
        raise ValueError("catalog product needs a mã")
    ma = norm_ma(raw_ma)
    if MA_RE.fullmatch(ma) is None:
        raise ValueError(f"catalog product has an invalid mã {raw_ma!r}")
    if "priceUsd" not in item:
        raise ValueError(f"{ma} needs priceUsd")
    return CatalogRow(ma, parse_price(item.get("priceUsd"), ma), _status(item.get("status"), ma))


def _status(value: object, ma: str) -> str | None:
    if value is None:
        return None
    if isinstance(value, str) and value in STATUSES:
        return value
    raise ValueError(f"{ma} status must be available, hold, or sold")


def _stays_held(before: CatalogRow | None, after: CatalogRow | None) -> bool:
    present = [row for row in (before, after) if row is not None]
    return all(row.status == "hold" for row in present)


def _s06_price(rows: Mapping[str, CatalogRow]) -> str | None:
    row = rows.get(S06)
    if row is None:
        return None
    return format_price(row.price_usd)


def _is_remote(path: str) -> bool:
    return "://" in path or path.startswith("http:") or path.startswith("https:")


def _local_fixture(path: str | Path) -> Path:
    if isinstance(path, str) and _is_remote(path):
        raise ValueError("catalog diff reads local JSON fixtures only")
    file = Path(path)
    if not file.is_file():
        raise ValueError(f"missing catalog fixture {path}")
    resolved = file.resolve()
    if resolved == default_held_path().resolve():
        raise ValueError("catalog diff does not use data/held.json as a catalog")
    return resolved


if __name__ == "__main__":
    raise SystemExit(main())
