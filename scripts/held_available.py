"""Flag a mã that is on a held-list fixture and marked available in a catalog fixture.

Reads the two fixture files and prints a JSON report.
Does not write data/held.json, either fixture, Blob, the hub, or a sell price.
S06 stays $25 and off the held list.
Exit 0 when nothing is flagged, 1 when a held mã is marked available, and 2 when a fixture is refused.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path

from held_policy import MA_RE, HeldPolicy, default_held_path, load_held_policy, norm_ma

S06 = "S06"
S06_USD = 25
KIND = "held_available"
SHOP_CATALOG_NAMES = frozenset({"products.json", "catalog.v1.json"})


@dataclass(frozen=True)
class CatalogRow:
    ma: str
    price_usd: int | None
    status: str | None


@dataclass(frozen=True)
class AvailableFlag:
    ma: str
    status: str
    price_usd: int | None

    def as_json(self) -> dict[str, object]:
        return {
            "ma": self.ma,
            "kind": KIND,
            "status": self.status,
            "priceUsd": self.price_usd,
        }


@dataclass(frozen=True)
class HeldAvailableReport:
    flags: tuple[AvailableFlag, ...]
    s06_price_usd: int | None
    s06_status: str | None
    s06_on_held: bool

    def as_json(self) -> dict[str, object]:
        return {
            "readOnly": True,
            "flags": [flag.as_json() for flag in self.flags],
            "s06": {
                "priceUsd": self.s06_price_usd,
                "status": self.s06_status,
                "onHeldList": self.s06_on_held,
            },
            "writes": [],
        }


def flag_held_available(
    policy: HeldPolicy,
    rows: Mapping[str, CatalogRow],
) -> HeldAvailableReport:
    """Return flags. Does not mutate the held list or the catalog rows."""
    if S06 in policy.held or S06 in policy.never_list:
        raise ValueError("S06 stays off the held list")
    s06 = rows.get(S06)
    if s06 is not None and s06.price_usd != S06_USD:
        raise ValueError("S06 stays $25")
    flags: list[AvailableFlag] = []
    for code in sorted(policy.held):
        row = rows.get(code)
        if row is None:
            continue
        status = row.status
        if not isinstance(status, str) or status.strip().casefold() != "available":
            continue
        flags.append(AvailableFlag(code, status, row.price_usd))
    return HeldAvailableReport(
        flags=tuple(flags),
        s06_price_usd=None if s06 is None else s06.price_usd,
        s06_status=None if s06 is None else s06.status,
        s06_on_held=False,
    )


def flag_files(held: str | Path, catalog: str | Path) -> HeldAvailableReport:
    return flag_held_available(load_held_fixture(held), load_catalog(catalog))


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
    fixture = _local_fixture(path, "catalog")
    try:
        payload = json.loads(fixture.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise ValueError(f"{path} is not catalog JSON") from error
    return parse_catalog(payload)


def load_held_fixture(path: str | Path) -> HeldPolicy:
    fixture = _local_fixture(path, "held-list")
    try:
        return load_held_policy(fixture)
    except json.JSONDecodeError as error:
        raise ValueError(f"{path} is not held-list JSON") from error


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Flag a mã that is on a held-list fixture and marked available "
            "in a catalog fixture. Does not write."
        ),
    )
    parser.add_argument("--held", required=True, help="Held-list JSON fixture.")
    parser.add_argument("--catalog", required=True, help="Catalog JSON fixture.")
    args = parser.parse_args(argv)
    try:
        report = flag_files(args.held, args.catalog)
    except (OSError, ValueError) as error:
        print(str(error), file=sys.stderr)
        return 2
    print(json.dumps(report.as_json(), indent=2))
    return 1 if report.flags else 0


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
    status = item.get("status", None)
    if "status" in item and status is not None and not isinstance(status, str):
        raise ValueError(f"{ma} status must be a string or null")
    shown = status if isinstance(status, str) else None
    return CatalogRow(ma, _price(item.get("priceUsd"), ma), shown)


def _price(value: object, ma: str) -> int | None:
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"{ma} priceUsd must be an integer or null")
    if value < 0:
        raise ValueError(f"{ma} priceUsd cannot be negative")
    return value


def _local_fixture(path: str | Path, kind: str) -> Path:
    if _is_remote(path):
        raise ValueError(f"{kind} checks read local fixtures only")
    file = Path(path)
    if not file.is_file():
        raise ValueError(f"missing {kind} fixture {path}")
    resolved = file.resolve()
    if resolved == default_held_path().resolve():
        raise ValueError("held available checks read fixtures only and do not read data/held.json")
    if resolved.name.casefold() in SHOP_CATALOG_NAMES:
        raise ValueError("held available checks read a catalog fixture. Shop catalog files are not read.")
    return resolved


def _is_remote(path: str | Path) -> bool:
    text = str(path).strip()
    return "://" in text or text.startswith("//") or text.startswith("http:") or text.startswith("https:")


if __name__ == "__main__":
    raise SystemExit(main())
