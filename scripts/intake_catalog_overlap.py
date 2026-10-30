"""Flag fixture intake mãs that are already in the fixture catalog.

Read JSON fixtures and write a report. A mã on an intake row and in the
catalog is flagged already_cataloged. That intake row stays in the report
and in the fixture file. Prices are not changed. S06 stays $25 and may be
flagged as already cataloged. Held mãs stay held. This module does not
write intake, Blob, data/held.json, or catalog rows. A live intake URL is
refused.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parent
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from held_policy import HeldPolicy, load_held_policy

_ROOT = Path(__file__).resolve().parents[1]
_CATALOG_KEYS = ("products", "rows", "catalog")
_PRICE_KEYS = ("priceUsd", "price_usd", "sell_usd", "price")
_SELL_KEYS = ("sell_usd", "sellUsd")
_REMOTE_KEYS = (
    "url",
    "href",
    "source",
    "endpoint",
    "intakeUrl",
    "intake_url",
    "catalogUrl",
    "catalog_url",
    "submissions",
    "intake",
    "products",
    "rows",
    "catalog",
)


@dataclass(frozen=True)
class OverlapFlag:
    ma: str
    kind: str
    sell_usd: str | None
    catalog_usd: str | None
    held: bool

    def as_json(self) -> dict[str, object]:
        return {
            "ma": self.ma,
            "kind": self.kind,
            "sellUsd": self.sell_usd,
            "catalogUsd": self.catalog_usd,
            "held": self.held,
            "inCatalog": True,
            "deleted": False,
        }


@dataclass(frozen=True)
class OverlapRow:
    ma: str
    held: bool
    in_catalog: bool
    sell_usd: str | None
    catalog_usd: str | None
    flagged: bool

    def as_json(self) -> dict[str, object]:
        return {
            "ma": self.ma,
            "held": self.held,
            "inCatalog": self.in_catalog,
            "sellUsd": self.sell_usd,
            "catalogUsd": self.catalog_usd,
            "flagged": self.flagged,
            "deleted": False,
        }


@dataclass(frozen=True)
class OverlapReport:
    rows: tuple[OverlapRow, ...]
    s06_catalog_usd: str | None

    @property
    def flags(self) -> tuple[OverlapFlag, ...]:
        found: list[OverlapFlag] = []
        for row in self.rows:
            if not row.flagged:
                continue
            found.append(
                OverlapFlag(
                    row.ma,
                    "already_cataloged",
                    row.sell_usd,
                    row.catalog_usd,
                    row.held,
                )
            )
        return tuple(found)

    @property
    def flag_count(self) -> int:
        return len(self.flags)

    @property
    def s06_intake_usd(self) -> str | None:
        for row in self.rows:
            if row.ma == "S06":
                return row.sell_usd
        return None

    @property
    def s06_kind(self) -> str | None:
        for flag in self.flags:
            if flag.ma == "S06":
                return flag.kind
        return None


def flag_catalog_overlap(
    rows: list[dict[str, object]],
    catalog: dict[str, str | None],
    policy: HeldPolicy,
) -> OverlapReport:
    """Return flags. Leave every input row in place."""
    checked: list[OverlapRow] = []
    for row in rows:
        if not isinstance(row, dict) or not isinstance(row.get("ma"), str) or row.get("ma", "").strip() == "":
            raise ValueError("fixture intake row needs a mã")
        checked.append(_flag_row(row, catalog, policy))
    return OverlapReport(tuple(checked), catalog.get("S06"))


def load_rows(payload: object) -> list[dict[str, object]]:
    if _remote_pointer(payload):
        raise ValueError("Live intake is not read. Pass a fixture file.")
    if isinstance(payload, list):
        rows = payload
    elif isinstance(payload, dict) and isinstance(payload.get("submissions"), list):
        rows = payload["submissions"]
    elif isinstance(payload, dict) and isinstance(payload.get("intake"), list):
        rows = payload["intake"]
    else:
        raise ValueError("fixture must be a list or an object with submissions")
    if not all(isinstance(row, dict) for row in rows):
        raise ValueError("fixture intake row needs a mã")
    return rows


def catalog_index(payload: object) -> dict[str, str | None]:
    """Map catalog mã to the price text stored on that fixture row."""
    if _remote_pointer(payload):
        raise ValueError("Live intake is not read. Pass a fixture file.")
    rows = _catalog_rows(payload)
    index: dict[str, str | None] = {}
    for item in rows:
        if not isinstance(item, dict) or not isinstance(item.get("ma"), str) or item.get("ma", "").strip() == "":
            raise ValueError("catalog fixture row needs a mã")
        code = str(item["ma"]).strip().upper()
        if code in index:
            continue
        index[code] = _price_text(item)
    return index


def render_markdown(report: OverlapReport) -> str:
    lines = [
        "# Intake mãs already in the catalog",
        "",
        "Read-only copy of fixture rows. Intake rows are not deleted. Prices are not changed.",
        "S06 stays $25 and may be flagged as already cataloged.",
        "Held mãs stay held.",
        "A live intake URL is refused.",
        "",
        f"Rows: {len(report.rows)}",
        f"Flags: {report.flag_count}",
        f"S06 catalog USD: {_cell(report.s06_catalog_usd)}",
        f"S06 intake USD: {_cell(report.s06_intake_usd)}",
        "",
        "## Flags",
        "",
    ]
    if not report.flags:
        lines.append("None.")
    else:
        for flag in report.flags:
            hold = " stays held" if flag.held else ""
            lines.append(
                f"- {flag.ma} {flag.kind} sell `{_md(_cell(flag.sell_usd))}` "
                f"catalog `{_md(_cell(flag.catalog_usd))}`{hold}"
            )
    lines.extend(
        [
            "",
            "## Rows",
            "",
            "mã | held | in catalog | sell | catalog | flag",
            "--- | --- | --- | --- | --- | ---",
        ]
    )
    for row in report.rows:
        flag = "already_cataloged" if row.flagged else "—"
        lines.append(
            " | ".join(
                [
                    row.ma,
                    str(row.held).lower(),
                    str(row.in_catalog).lower(),
                    _cell(row.sell_usd),
                    _cell(row.catalog_usd),
                    flag,
                ]
            )
        )
    lines.append("")
    return "\n".join(lines)


def report_json(report: OverlapReport) -> dict[str, object]:
    return {
        "readOnly": True,
        "rowsDeleted": False,
        "pricesChanged": False,
        "liveIntake": "refused",
        "s06": "stays $25",
        "s06CatalogUsd": report.s06_catalog_usd,
        "s06IntakeUsd": report.s06_intake_usd,
        "s06Kind": report.s06_kind,
        "heldMas": "stay held",
        "rowCount": len(report.rows),
        "flagCount": report.flag_count,
        "flags": [flag.as_json() for flag in report.flags],
        "rows": [row.as_json() for row in report.rows],
    }


def write_report(report: OverlapReport, out_dir: Path) -> tuple[Path, Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    markdown_path = out_dir / "intake-catalog-overlap.md"
    json_path = out_dir / "intake-catalog-overlap.json"
    markdown_path.write_text(render_markdown(report), encoding="utf-8")
    json_path.write_text(json.dumps(report_json(report), indent=2) + "\n", encoding="utf-8")
    return markdown_path, json_path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Flag fixture intake mãs that are already in the fixture catalog.",
    )
    parser.add_argument("--fixture", required=True, help="Intake JSON fixture. A live intake URL is refused.")
    parser.add_argument("--catalog", required=True, help="Catalog JSON fixture. A live URL is refused.")
    parser.add_argument("--out", required=True, help="Directory for the markdown report and JSON sibling.")
    parser.add_argument("--held", default="", help="Held-list JSON to read. Defaults to data/held.json.")
    args = parser.parse_args(argv)
    if any(_is_live_target(value) for value in (args.fixture, args.catalog, args.held, args.out)):
        print("Live intake is not read. Pass a fixture file.", file=sys.stderr)
        return 2
    fixture = Path(args.fixture)
    catalog_path = Path(args.catalog)
    out_dir = Path(args.out)
    if _reserved_output(out_dir) or _same_file(out_dir, fixture) or _same_file(out_dir, catalog_path):
        print(f"Report path is reserved: {out_dir}", file=sys.stderr)
        return 2
    if not fixture.is_file():
        print(f"Fixture not found: {fixture}", file=sys.stderr)
        return 2
    if not catalog_path.is_file():
        print(f"Catalog not found: {catalog_path}", file=sys.stderr)
        return 2
    try:
        rows = load_rows(json.loads(fixture.read_text(encoding="utf-8")))
        catalog = catalog_index(json.loads(catalog_path.read_text(encoding="utf-8")))
        policy = load_held_policy(Path(args.held) if args.held else None)
        report = flag_catalog_overlap(rows, catalog, policy)
        markdown_path, _json_path = write_report(report, out_dir)
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as error:
        print(str(error), file=sys.stderr)
        return 2
    print(f"Already cataloged intake flags: {report.flag_count}")
    print(f"Intake rows kept: {len(report.rows)}")
    print(f"report: {markdown_path}")
    return 1 if report.flag_count else 0


def _flag_row(
    row: dict[str, object],
    catalog: dict[str, str | None],
    policy: HeldPolicy,
) -> OverlapRow:
    ma = str(row["ma"]).strip().upper()
    held = policy.skip_reason(ma) == "held"
    present = ma in catalog
    catalog_usd = catalog.get(ma) if present else None
    return OverlapRow(ma, held, present, _row_sell(row), catalog_usd, present)


def _row_sell(row: dict[str, object]) -> str | None:
    for key in _SELL_KEYS:
        if key in row:
            return _sell_text(row[key])
    return None


def _catalog_rows(payload: object) -> list[object]:
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict):
        for key in _CATALOG_KEYS:
            value = payload.get(key)
            if isinstance(value, list):
                return value
    raise ValueError("catalog fixture must be a list or an object with products")


def _price_text(item: dict[str, object]) -> str | None:
    for key in _PRICE_KEYS:
        if key not in item or item[key] is None:
            continue
        return _sell_text(item[key])
    return None


def _sell_text(value: object) -> str | None:
    if value is None or isinstance(value, bool):
        return None
    if isinstance(value, str):
        return value
    if isinstance(value, int):
        return str(value)
    if isinstance(value, float):
        text = format(value, "f")
        if "." in text:
            text = text.rstrip("0").rstrip(".")
        return text
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"))


def _cell(value: str | None) -> str:
    if value is None or value == "":
        return "—"
    return _md(value)


def _md(value: str) -> str:
    return value.replace("|", "/").replace("`", "'")


def _is_live_target(value: str) -> bool:
    text = value.strip().casefold()
    return "://" in text or text.startswith("//") or text.startswith("blob:") or text.startswith("http")


def _remote_pointer(payload: object) -> bool:
    if isinstance(payload, str):
        return _is_live_target(payload)
    if not isinstance(payload, dict):
        return False
    for key in _REMOTE_KEYS:
        value = payload.get(key)
        if isinstance(value, str) and _is_live_target(value):
            return True
    return False


def _reserved_output(path: Path) -> bool:
    resolved = path.resolve()
    reserved = (
        (_ROOT / "data").resolve(),
        (_ROOT / "sassy-closet-shop" / "data").resolve(),
        (_ROOT / "sassy-closet" / "data").resolve(),
    )
    for folder in reserved:
        if resolved == folder or folder in resolved.parents:
            return True
    return False


def _same_file(out_dir: Path, source: Path) -> bool:
    try:
        return out_dir.resolve() == source.resolve()
    except OSError:
        return False


if __name__ == "__main__":
    raise SystemExit(main())
