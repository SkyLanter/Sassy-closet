"""Flag intake rows saved more than 7 days ago that are still off the catalog.

Read JSON fixtures and write a report. The saved date is saved_at or
saved_date when the row has one, otherwise updated_at. A save exactly 7
days ago is not flagged. Rows are not deleted. Prices are not changed.
S06 stays $25. Held mãs stay held. This module does not write intake,
Blob, Square, data/held.json, or catalog rows. A live intake URL is refused.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parent
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from held_policy import HeldPolicy, load_held_policy

_ROOT = Path(__file__).resolve().parents[1]
STALE_DAYS = 7
_STALE_AFTER = timedelta(days=STALE_DAYS)
_SAVED_KEYS = ("saved_at", "savedAt", "saved_date", "savedDate", "updated_at", "updatedAt")
_CATALOG_KEYS = ("products", "rows", "catalog")
_PRICE_KEYS = ("priceUsd", "price_usd", "sell_usd", "price")
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
_MISSING = object()


@dataclass(frozen=True)
class StaleFlag:
    ma: str
    kind: str
    saved: str
    saved_field: str
    age_seconds: int
    held: bool
    sell_usd: str | None

    def as_json(self) -> dict[str, object]:
        return {
            "ma": self.ma,
            "kind": self.kind,
            "saved": self.saved,
            "savedField": self.saved_field,
            "ageSeconds": self.age_seconds,
            "held": self.held,
            "sellUsd": self.sell_usd,
            "inCatalog": False,
        }


@dataclass(frozen=True)
class StaleRow:
    ma: str
    held: bool
    in_catalog: bool
    saved: str | None
    saved_field: str
    sell_usd: str | None
    age_seconds: int | None
    flagged: bool

    def as_json(self) -> dict[str, object]:
        return {
            "ma": self.ma,
            "held": self.held,
            "inCatalog": self.in_catalog,
            "saved": self.saved,
            "savedField": self.saved_field,
            "sellUsd": self.sell_usd,
            "ageSeconds": self.age_seconds,
            "flagged": self.flagged,
        }


@dataclass(frozen=True)
class StaleReport:
    as_of: datetime
    rows: tuple[StaleRow, ...]
    s06_catalog_usd: str | None

    @property
    def flags(self) -> tuple[StaleFlag, ...]:
        found: list[StaleFlag] = []
        for row in self.rows:
            if not row.flagged or row.age_seconds is None or row.saved is None:
                continue
            found.append(
                StaleFlag(
                    row.ma,
                    "stale_absent",
                    row.saved,
                    row.saved_field,
                    row.age_seconds,
                    row.held,
                    row.sell_usd,
                )
            )
        return tuple(found)

    @property
    def flag_count(self) -> int:
        return len(self.flags)


def flag_stale_intake(
    rows: list[dict[str, object]],
    catalog: dict[str, str | None],
    policy: HeldPolicy,
    as_of: datetime,
) -> StaleReport:
    """Return flags. Leave every input row as it was passed in."""
    clock = _aware(as_of)
    checked: list[StaleRow] = []
    for row in rows:
        if not isinstance(row, dict) or not isinstance(row.get("ma"), str) or row.get("ma", "").strip() == "":
            raise ValueError("fixture intake row needs a mã")
        checked.append(_flag_row(row, catalog, policy, clock))
    return StaleReport(clock, tuple(checked), catalog.get("S06"))


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


def render_markdown(report: StaleReport) -> str:
    lines = [
        "# Stale intake flags",
        "",
        "Read-only copy of fixture rows. Rows are not deleted. Prices are not changed.",
        "S06 stays $25. Held mãs stay held.",
        "A live intake URL is refused.",
        "",
        f"As of: {_iso(report.as_of)}",
        f"Older than: {STALE_DAYS} days",
        f"Rows: {len(report.rows)}",
        f"Flags: {report.flag_count}",
        f"S06 catalog USD: {_cell(report.s06_catalog_usd)}",
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
                f"- {flag.ma} {flag.kind} saved `{_md(flag.saved)}` "
                f"age {flag.age_seconds}s{hold}"
            )
    lines.extend(
        [
            "",
            "## Rows",
            "",
            "mã | held | in catalog | saved | sell | flag",
            "--- | --- | --- | --- | --- | ---",
        ]
    )
    for row in report.rows:
        flag = "stale_absent" if row.flagged else "—"
        lines.append(
            " | ".join(
                [
                    row.ma,
                    str(row.held).lower(),
                    str(row.in_catalog).lower(),
                    _cell(row.saved),
                    _cell(row.sell_usd),
                    flag,
                ]
            )
        )
    lines.append("")
    return "\n".join(lines)


def report_json(report: StaleReport) -> dict[str, object]:
    return {
        "readOnly": True,
        "rowsDeleted": False,
        "pricesChanged": False,
        "liveIntake": "refused",
        "s06": "stays $25",
        "s06CatalogUsd": report.s06_catalog_usd,
        "heldMas": "stay held",
        "asOf": _iso(report.as_of),
        "olderThanDays": STALE_DAYS,
        "flagCount": report.flag_count,
        "flags": [flag.as_json() for flag in report.flags],
        "rows": [row.as_json() for row in report.rows],
    }


def write_report(report: StaleReport, out_dir: Path) -> tuple[Path, Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    markdown_path = out_dir / "intake-stale-flags.md"
    json_path = out_dir / "intake-stale-flags.json"
    markdown_path.write_text(render_markdown(report), encoding="utf-8")
    json_path.write_text(json.dumps(report_json(report), indent=2) + "\n", encoding="utf-8")
    return markdown_path, json_path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Flag fixture intake rows saved more than 7 days ago and still off the catalog.",
    )
    parser.add_argument("--fixture", required=True, help="Intake JSON fixture. A live intake URL is refused.")
    parser.add_argument("--catalog", required=True, help="Catalog JSON fixture. A live URL is refused.")
    parser.add_argument("--as-of", default="", help="Clock for the 7-day check. YYYY-MM-DD or ISO-8601.")
    parser.add_argument("--out", required=True, help="Directory for the markdown report and JSON sibling.")
    parser.add_argument("--held", default="", help="Held-list JSON to read. Defaults to data/held.json.")
    args = parser.parse_args(argv)
    if any(_is_live_target(value) for value in (args.fixture, args.catalog, args.held, args.as_of, args.out)):
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
        as_of = _clock(args.as_of)
        rows = load_rows(json.loads(fixture.read_text(encoding="utf-8")))
        catalog = catalog_index(json.loads(catalog_path.read_text(encoding="utf-8")))
        policy = load_held_policy(Path(args.held) if args.held else None)
        report = flag_stale_intake(rows, catalog, policy, as_of)
        markdown_path, _json_path = write_report(report, out_dir)
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as error:
        print(str(error), file=sys.stderr)
        return 2
    print(f"Stale intake flags: {report.flag_count}")
    print(f"report: {markdown_path}")
    return 1 if report.flag_count else 0


def _flag_row(
    row: dict[str, object],
    catalog: dict[str, str | None],
    policy: HeldPolicy,
    as_of: datetime,
) -> StaleRow:
    ma = str(row["ma"]).strip().upper()
    held = policy.skip_reason(ma) == "held"
    field, raw = _saved_field(row)
    saved = None if raw is _MISSING else _stored(raw)
    parsed = None if raw is _MISSING else _parse_instant(raw)
    age = None if parsed is None else _age_seconds(as_of - parsed)
    present = ma in catalog
    # Older than 7 days. A save exactly 7 days ago stays unflagged.
    flagged = parsed is not None and not present and (as_of - parsed) > _STALE_AFTER
    return StaleRow(ma, held, present, saved, field, _sell_text(row.get("sell_usd", _MISSING)), age, flagged)


def _saved_field(row: dict[str, object]) -> tuple[str, object]:
    for key in _SAVED_KEYS:
        if key in row:
            return key, row[key]
    return "saved_at", _MISSING


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
        value = item[key]
        if isinstance(value, bool):
            continue
        if isinstance(value, str):
            return value
        if isinstance(value, int):
            return str(value)
        if isinstance(value, float):
            text = format(value, "f")
            if "." in text:
                text = text.rstrip("0").rstrip(".")
            return text
    return None


def _sell_text(value: object) -> str | None:
    if value is _MISSING or value is None:
        return None
    if isinstance(value, str):
        return value
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return str(value)
    if isinstance(value, float):
        text = format(value, "f")
        if "." in text:
            text = text.rstrip("0").rstrip(".")
        return text
    return _stored(value)


def _parse_instant(value: object) -> datetime | None:
    if not isinstance(value, str):
        return None
    text = value.strip()
    if text == "":
        return None
    if text.endswith(("Z", "z")):
        text = text[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError:
        return None
    return _aware(parsed)


def _clock(value: str) -> datetime:
    if value.strip() == "":
        return datetime.now(timezone.utc)
    parsed = _parse_instant(value)
    if parsed is None:
        raise ValueError("as-of must be YYYY-MM-DD or ISO-8601")
    return parsed


def _age_seconds(delta: timedelta) -> int:
    return delta.days * 86400 + delta.seconds


def _aware(moment: datetime) -> datetime:
    if moment.tzinfo is None:
        return moment.replace(tzinfo=timezone.utc)
    return moment.astimezone(timezone.utc)


def _iso(moment: datetime) -> str:
    return _aware(moment).isoformat().replace("+00:00", "Z")


def _stored(value: object) -> str:
    if isinstance(value, str):
        return value
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
