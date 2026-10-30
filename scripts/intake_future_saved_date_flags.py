"""Flag fixture intake rows whose saved date is after the fixture as-of date.

Read a JSON fixture and write a report. The as-of date is the fixture
asOf or as_of value. The clock is not used. The saved date is saved_at
or saved_date when the row has one, otherwise updated_at. A value that
is not an ISO-8601 date is not flagged and is not rewritten. No date is
invented. Prices are not changed. S06 stays $25. Held mãs stay held.
This module does not write intake, Blob, Square, data/held.json, or
catalog rows. A live intake URL is refused.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parent
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from held_policy import HeldPolicy, load_held_policy, norm_ma

_ROOT = Path(__file__).resolve().parents[1]
_SAVED_KEYS = ("saved_at", "savedAt", "saved_date", "savedDate", "updated_at", "updatedAt")
_AS_OF_KEYS = ("asOf", "as_of")
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
_AFTER = "saved_after_as_of"
_LIVE = "Live intake is not read. Pass a fixture file."


@dataclass(frozen=True)
class FutureSavedFlag:
    ma: str
    kind: str
    saved: str
    saved_field: str
    as_of: str
    held: bool
    sell_usd: str | None

    def as_json(self) -> dict[str, object]:
        return {
            "ma": self.ma,
            "kind": self.kind,
            "saved": self.saved,
            "savedField": self.saved_field,
            "asOf": self.as_of,
            "held": self.held,
            "sellUsd": self.sell_usd,
        }


@dataclass(frozen=True)
class FutureSavedRow:
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
class FutureSavedReport:
    as_of: str
    rows: tuple[FutureSavedRow, ...]

    @property
    def flags(self) -> tuple[FutureSavedFlag, ...]:
        found: list[FutureSavedFlag] = []
        for row in self.rows:
            if row.kind is None or row.saved is None:
                continue
            found.append(
                FutureSavedFlag(
                    row.ma,
                    row.kind,
                    row.saved,
                    row.saved_field,
                    self.as_of,
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


def flag_saved_after_as_of(payload: object, policy: HeldPolicy) -> FutureSavedReport:
    """Return flags. The as-of date comes from the fixture. Rows are not rewritten."""
    if _remote_pointer(payload):
        raise ValueError(_LIVE)
    if not isinstance(payload, dict):
        raise ValueError("fixture must be an object with an as-of date and submissions")
    as_of_text, as_of = _as_of(payload)
    checked = tuple(_flag_row(row, policy, as_of) for row in _submission_rows(payload))
    return FutureSavedReport(as_of_text, checked)


def render_markdown(report: FutureSavedReport) -> str:
    lines = [
        "# Intake saved dates after the as-of date",
        "",
        "Read-only copy of fixture rows. A saved date after the fixture as-of date is flagged.",
        "The as-of date comes from the fixture. The clock is not used.",
        "The saved date is not changed. Prices are not changed.",
        "S06 stays $25. Held mãs stay held.",
        "A live intake URL is refused.",
        "",
        f"As of: {_saved_cell(report.as_of)}",
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


def report_json(report: FutureSavedReport) -> dict[str, object]:
    return {
        "readOnly": True,
        "datesChanged": False,
        "clockUsed": False,
        "asOf": report.as_of,
        "asOfSource": "fixture",
        "pricesChanged": False,
        "liveIntake": "refused",
        "s06": "stays $25",
        "s06SellUsd": report.s06_sell_usd,
        "heldMas": "stay held",
        "flagCount": report.flag_count,
        "flags": [flag.as_json() for flag in report.flags],
        "rows": [row.as_json() for row in report.rows],
    }


def write_report(report: FutureSavedReport, out_dir: Path) -> tuple[Path, Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    markdown_path = out_dir / "intake-future-saved-date-flags.md"
    json_path = out_dir / "intake-future-saved-date-flags.json"
    markdown_path.write_text(render_markdown(report), encoding="utf-8")
    json_path.write_text(json.dumps(report_json(report), indent=2) + "\n", encoding="utf-8")
    return markdown_path, json_path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Flag fixture intake rows whose saved date is after the fixture as-of date.",
    )
    parser.add_argument("--fixture", required=True, help="Intake JSON fixture with an as-of date. A live intake URL is refused.")
    parser.add_argument("--out", required=True, help="Directory for the markdown report and JSON sibling.")
    parser.add_argument("--held", default="", help="Held-list JSON to read. Defaults to data/held.json.")
    args = parser.parse_args(argv)
    if any(_is_live_target(value) for value in (args.fixture, args.held, args.out)):
        print(_LIVE, file=sys.stderr)
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
        payload = json.loads(fixture.read_text(encoding="utf-8"))
        policy = load_held_policy(Path(args.held) if args.held else None)
        report = flag_saved_after_as_of(payload, policy)
        markdown_path, _json_path = write_report(report, out_dir)
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as error:
        print(str(error), file=sys.stderr)
        return 2
    print(f"Saved dates after as-of: {report.flag_count}")
    print(f"report: {markdown_path}")
    return 1 if report.flag_count else 0


def _flag_row(row: dict[str, object], policy: HeldPolicy, as_of: datetime) -> FutureSavedRow:
    ma = norm_ma(str(row["ma"]))
    held = policy.skip_reason(ma) == "held"
    field, raw = _saved_field(row)
    kind, saved = _classify(raw, as_of)
    return FutureSavedRow(ma, held, saved, field, _sell_text(row), kind)


def _submission_rows(payload: dict[str, object]) -> list[dict[str, object]]:
    rows: object | None = None
    if isinstance(payload.get("submissions"), list):
        rows = payload["submissions"]
    elif isinstance(payload.get("intake"), list):
        rows = payload["intake"]
    if not isinstance(rows, list):
        raise ValueError("fixture must be an object with an as-of date and submissions")
    checked: list[dict[str, object]] = []
    for row in rows:
        if not isinstance(row, dict) or not isinstance(row.get("ma"), str) or row.get("ma", "").strip() == "":
            raise ValueError("fixture intake row needs a mã")
        checked.append(row)
    return checked


def _as_of(payload: dict[str, object]) -> tuple[str, datetime]:
    present = [key for key in _AS_OF_KEYS if key in payload]
    if not present:
        raise ValueError("Fixture as-of date is required.")
    parsed: list[tuple[str, datetime]] = []
    for key in present:
        raw = payload[key]
        if isinstance(raw, str) and _is_live_target(raw):
            raise ValueError(_LIVE)
        if not isinstance(raw, str) or raw.strip() == "":
            raise ValueError("Fixture as-of date is required.")
        instant = _parse_instant(raw)
        if instant is None:
            raise ValueError("Fixture as-of date is not an ISO-8601 date.")
        parsed.append((raw, instant))
    first = parsed[0][1]
    if any(item[1] != first for item in parsed[1:]):
        raise ValueError("Fixture as-of dates disagree.")
    return parsed[0][0], first


def _saved_field(row: dict[str, object]) -> tuple[str, object]:
    for key in _SAVED_KEYS:
        if key in row:
            return key, row[key]
    return "", _ABSENT


def _classify(raw: object, as_of: datetime) -> tuple[str | None, str | None]:
    if raw is _ABSENT or raw is None:
        return None, None
    if isinstance(raw, str):
        stored = raw
        parsed = _parse_instant(raw)
    else:
        stored = _stored(raw)
        parsed = None
    # Strictly after the fixture as-of instant. An equal instant stays unflagged.
    if parsed is not None and parsed > as_of:
        return _AFTER, stored
    return None, stored


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


def _aware(moment: datetime) -> datetime:
    if moment.tzinfo is None:
        return moment.replace(tzinfo=timezone.utc)
    return moment.astimezone(timezone.utc)


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
