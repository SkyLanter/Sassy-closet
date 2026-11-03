"""Flag fixture intake rows with a missing or unreadable saved date.

Read a JSON fixture and write a report. The saved date is saved_at or
saved_date when the row has one, otherwise updated_at. A blank value is
missing. A value that is not an ISO-8601 date is unreadable. No date is
invented. Prices are not changed. S06 stays $25. Held mãs stay held.
This module does not write intake, Blob, Square, data/held.json, or
catalog rows. A live intake URL is refused.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parent
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from held_policy import HeldPolicy, load_held_policy, norm_ma

_ROOT = Path(__file__).resolve().parents[1]
_SAVED_KEYS = ("saved_at", "savedAt", "saved_date", "savedDate", "updated_at", "updatedAt")
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
)
_ABSENT = object()
_MISSING = "missing_saved_date"
_UNREADABLE = "unreadable_saved_date"


@dataclass(frozen=True)
class SavedDateFlag:
    ma: str
    kind: str
    saved: str | None
    saved_field: str
    held: bool
    sell_usd: str | None

    def as_json(self) -> dict[str, object]:
        return {
            "ma": self.ma,
            "kind": self.kind,
            "saved": self.saved,
            "savedField": self.saved_field,
            "held": self.held,
            "sellUsd": self.sell_usd,
        }


@dataclass(frozen=True)
class SavedDateRow:
    ma: str
    held: bool
    saved: str | None
    saved_field: str
    sell_usd: str | None
    kind: str | None

    def as_json(self) -> dict[str, object]:
        return {
            "ma": self.ma,
            "held": self.held,
            "saved": self.saved,
            "savedField": self.saved_field,
            "sellUsd": self.sell_usd,
            "kind": self.kind,
        }


@dataclass(frozen=True)
class SavedDateReport:
    rows: tuple[SavedDateRow, ...]

    @property
    def flags(self) -> tuple[SavedDateFlag, ...]:
        found: list[SavedDateFlag] = []
        for row in self.rows:
            if row.kind is None:
                continue
            found.append(
                SavedDateFlag(
                    row.ma,
                    row.kind,
                    row.saved,
                    row.saved_field,
                    row.held,
                    row.sell_usd,
                )
            )
        return tuple(found)

    @property
    def flag_count(self) -> int:
        return len(self.flags)

    @property
    def s06_sell_usd(self) -> str | None:
        for row in self.rows:
            if row.ma == "S06":
                return row.sell_usd
        return None


def flag_saved_dates(rows: list[dict[str, object]], policy: HeldPolicy) -> SavedDateReport:
    """Return flags. Leave every input row as it was passed in."""
    checked = [_flag_row(row, policy) for row in rows]
    return SavedDateReport(tuple(checked))


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
    checked: list[dict[str, object]] = []
    for row in rows:
        if not isinstance(row, dict) or not isinstance(row.get("ma"), str) or row.get("ma", "").strip() == "":
            raise ValueError("fixture intake row needs a mã")
        checked.append(row)
    return checked


def render_markdown(report: SavedDateReport) -> str:
    lines = [
        "# Intake saved-date flags",
        "",
        "Read-only copy of fixture rows. A missing or unreadable saved date is flagged.",
        "A date is not invented. Prices are not changed.",
        "S06 stays $25. Held mãs stay held.",
        "A live intake URL is refused.",
        "",
        f"Rows: {len(report.rows)}",
        f"Flags: {report.flag_count}",
        f"S06 sell USD: {_cell(report.s06_sell_usd)}",
        "",
        "## Flags",
        "",
    ]
    if not report.flags:
        lines.append("None.")
    else:
        for flag in report.flags:
            hold = " stays held" if flag.held else ""
            lines.append(f"- {flag.ma} {flag.kind} saved {_saved_cell(flag.saved)}{hold}")
    lines.extend(
        [
            "",
            "## Rows",
            "",
            "mã | held | saved field | saved | sell | flag",
            "--- | --- | --- | --- | --- | ---",
        ]
    )
    for row in report.rows:
        lines.append(
            " | ".join(
                [
                    row.ma,
                    str(row.held).lower(),
                    _cell(row.saved_field),
                    _saved_cell(row.saved),
                    _cell(row.sell_usd),
                    row.kind or "—",
                ]
            )
        )
    lines.append("")
    return "\n".join(lines)


def report_json(report: SavedDateReport) -> dict[str, object]:
    return {
        "readOnly": True,
        "datesInvented": False,
        "pricesChanged": False,
        "liveIntake": "refused",
        "s06": "stays $25",
        "s06SellUsd": report.s06_sell_usd,
        "heldMas": "stay held",
        "flagCount": report.flag_count,
        "flags": [flag.as_json() for flag in report.flags],
        "rows": [row.as_json() for row in report.rows],
    }


def write_report(report: SavedDateReport, out_dir: Path) -> tuple[Path, Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    markdown_path = out_dir / "intake-saved-date-flags.md"
    json_path = out_dir / "intake-saved-date-flags.json"
    markdown_path.write_text(render_markdown(report), encoding="utf-8")
    json_path.write_text(json.dumps(report_json(report), indent=2) + "\n", encoding="utf-8")
    return markdown_path, json_path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Flag fixture intake rows with a missing or unreadable saved date.",
    )
    parser.add_argument("--fixture", required=True, help="Intake JSON fixture. A live intake URL is refused.")
    parser.add_argument("--out", required=True, help="Directory for the markdown report and JSON sibling.")
    parser.add_argument("--held", default="", help="Held-list JSON to read. Defaults to data/held.json.")
    args = parser.parse_args(argv)
    if any(_is_live_target(value) for value in (args.fixture, args.held, args.out)):
        print("Live intake is not read. Pass a fixture file.", file=sys.stderr)
        return 2
    fixture = Path(args.fixture)
    out_dir = Path(args.out)
    if _reserved_output(out_dir) or _same_file(out_dir, fixture):
        print(f"Report path is reserved: {out_dir}", file=sys.stderr)
        return 2
    if not fixture.is_file():
        print(f"Fixture not found: {fixture}", file=sys.stderr)
        return 2
    try:
        rows = load_rows(json.loads(fixture.read_text(encoding="utf-8")))
        policy = load_held_policy(Path(args.held) if args.held else None)
        report = flag_saved_dates(rows, policy)
        markdown_path, _json_path = write_report(report, out_dir)
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as error:
        print(str(error), file=sys.stderr)
        return 2
    print(f"Saved-date flags: {report.flag_count}")
    print(f"report: {markdown_path}")
    return 1 if report.flag_count else 0


def _flag_row(row: dict[str, object], policy: HeldPolicy) -> SavedDateRow:
    ma = norm_ma(str(row["ma"]))
    held = policy.skip_reason(ma) == "held"
    field, raw = _saved_field(row)
    kind, saved = _classify(raw)
    return SavedDateRow(ma, held, saved, field, _sell_text(row), kind)


def _saved_field(row: dict[str, object]) -> tuple[str, object]:
    for key in _SAVED_KEYS:
        if key in row:
            return key, row[key]
    return "", _ABSENT


def _classify(raw: object) -> tuple[str | None, str | None]:
    if raw is _ABSENT or raw is None:
        return _MISSING, None
    if isinstance(raw, str):
        if raw.strip() == "":
            return _MISSING, raw
        if _readable_instant(raw):
            return None, raw
        return _UNREADABLE, raw
    return _UNREADABLE, _stored(raw)


def _readable_instant(value: str) -> bool:
    text = value.strip()
    if text.endswith(("Z", "z")):
        text = text[:-1] + "+00:00"
    try:
        datetime.fromisoformat(text)
    except ValueError:
        return False
    return True


def _sell_text(row: dict[str, object]) -> str | None:
    if "sell_usd" not in row:
        return None
    value = row["sell_usd"]
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
    return _stored(value)


def _stored(value: object) -> str:
    if isinstance(value, str):
        return value
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"))


def _saved_cell(value: str | None) -> str:
    if value is None or value == "":
        return "—"
    return f"`{_md(value)}`"


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
