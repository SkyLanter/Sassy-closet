"""Flag a catalog status other than available, sold, or held.

Read a JSON fixture and write a report. The sell catalog stores the held
state as "hold"; that spelling is the same status and is not a flag.
S06 stays $25. Held mãs stay held. This module does not rewrite a status
or a price, and it does not write intake, Blob, Square, data/held.json,
or catalog rows. It does not post.
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

# "hold" is the catalog.v1 spelling of the held status.
KNOWN_STATUSES = frozenset({"available", "sold", "held", "hold"})
_BLANK = frozenset(
    {
        "",
        "none",
        "n/a",
        "na",
        "null",
        "undefined",
        "blank",
        "missing",
        "todo",
        "tbd",
        "-",
        "—",
        "nil",
    }
)
_FORBIDDEN_NAMES = frozenset(
    {"held.json", "products.json", "catalog.v1.json", "submissions.json"}
)


@dataclass(frozen=True)
class StatusFlag:
    ma: str
    kind: str
    stored: str
    held: bool

    def as_json(self) -> dict[str, object]:
        return {
            "ma": self.ma,
            "kind": self.kind,
            "stored": self.stored,
            "held": self.held,
        }


@dataclass(frozen=True)
class StatusRow:
    ma: str
    status: str | None
    price_usd: str | None
    held: bool
    flags: tuple[StatusFlag, ...]

    def as_json(self) -> dict[str, object]:
        return {
            "ma": self.ma,
            "status": self.status,
            "priceUsd": self.price_usd,
            "held": self.held,
            "flags": [flag.as_json() for flag in self.flags],
        }


@dataclass(frozen=True)
class StatusReport:
    rows: tuple[StatusRow, ...]

    @property
    def flags(self) -> tuple[StatusFlag, ...]:
        return tuple(flag for row in self.rows for flag in row.flags)

    @property
    def flag_count(self) -> int:
        return len(self.flags)

    def price_for(self, ma: str) -> str | None:
        code = ma.strip().upper()
        for row in self.rows:
            if row.ma == code:
                return row.price_usd
        return None


def flag_catalog_status(rows: list[dict[str, object]], policy: HeldPolicy) -> StatusReport:
    """Return flags. Leave every input row as it was passed in."""
    checked: list[StatusRow] = []
    for row in rows:
        if not isinstance(row, dict) or not isinstance(row.get("ma"), str) or str(row.get("ma", "")).strip() == "":
            raise ValueError("fixture catalog row needs a mã")
        checked.append(_flag_row(row, policy))
    return StatusReport(tuple(checked))


def load_rows(payload: object) -> list[dict[str, object]]:
    if isinstance(payload, list):
        rows = payload
    elif isinstance(payload, dict) and isinstance(payload.get("products"), list):
        rows = payload["products"]
    else:
        raise ValueError("fixture must be a list or a catalog object with products")
    if not all(isinstance(row, dict) for row in rows):
        raise ValueError("fixture catalog row needs a mã")
    return rows


def render_markdown(report: StatusReport) -> str:
    lines = [
        "# Catalog status flags",
        "",
        "Read-only copy of fixture catalog statuses.",
        "Known statuses are available, sold, and held.",
        'The sell catalog stores held as "hold". That spelling is not a flag.',
        "S06 stays $25. Held mãs stay held.",
        "The stored status and price are not rewritten.",
        "",
        f"Rows: {len(report.rows)}",
        f"Flags: {report.flag_count}",
        "",
        "## Flags",
        "",
    ]
    if not report.flags:
        lines.append("None.")
    else:
        for flag in report.flags:
            hold = " stays held" if flag.held else ""
            lines.append(f"- {flag.ma} {flag.kind} stored `{_md(flag.stored)}`{hold}")
    lines.extend(
        [
            "",
            "## Rows",
            "",
            "mã | held | status | price | flags",
            "--- | --- | --- | --- | ---",
        ]
    )
    for row in report.rows:
        kinds = ", ".join(flag.kind for flag in row.flags) or "—"
        price = "—" if row.price_usd is None else _md(row.price_usd)
        lines.append(
            f"{row.ma} | {str(row.held).lower()} | {_status_cell(row.status)} | {price} | {kinds}"
        )
    lines.extend(["", "## Left alone", "", "Catalog rows, prices, and data/held.json were not written.", ""])
    return "\n".join(lines)


def report_json(report: StatusReport) -> dict[str, object]:
    return {
        "readOnly": True,
        "knownStatuses": ["available", "sold", "held"],
        "catalogHeldSpelling": "hold",
        "s06": "stays $25",
        "s06PriceUsd": report.price_for("S06"),
        "heldMas": "stay held",
        "flagCount": report.flag_count,
        "flags": [flag.as_json() for flag in report.flags],
        "rows": [row.as_json() for row in report.rows],
        "writes": [],
    }


def write_report(report: StatusReport, out_dir: Path) -> tuple[Path, Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    markdown_path = out_dir / "catalog-status.md"
    json_path = out_dir / "catalog-status.json"
    markdown_path.write_text(render_markdown(report), encoding="utf-8")
    json_path.write_text(json.dumps(report_json(report), indent=2) + "\n", encoding="utf-8")
    return markdown_path, json_path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Flag a catalog status other than available, sold, or held. Writes a report only.",
    )
    parser.add_argument("--fixture", required=True, help="Path to a JSON catalog fixture. Live catalogs are not read.")
    parser.add_argument("--out", required=True, help="Directory for the markdown report and JSON sibling.")
    parser.add_argument("--held", default="", help="Held-list JSON to read. Defaults to data/held.json.")
    args = parser.parse_args(argv)
    refused = _refuse_reason(args.fixture, args.out, args.held)
    if refused:
        print(refused, file=sys.stderr)
        return 2
    fixture = Path(args.fixture)
    out = Path(args.out)
    if not fixture.is_file():
        print(f"Fixture not found: {fixture}", file=sys.stderr)
        return 2
    if out.exists() and not out.is_dir():
        print(f"Report directory is not a directory: {out}", file=sys.stderr)
        return 2
    try:
        payload = json.loads(fixture.read_text(encoding="utf-8"))
        rows = load_rows(payload)
        policy = load_held_policy(Path(args.held) if args.held else None)
        report = flag_catalog_status(rows, policy)
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as error:
        print(str(error), file=sys.stderr)
        return 2
    markdown_path, _json_path = write_report(report, out)
    print(f"Catalog status flags: {report.flag_count}")
    print(f"report: {markdown_path}")
    return 1 if report.flag_count else 0


def _flag_row(row: dict[str, object], policy: HeldPolicy) -> StatusRow:
    ma = str(row["ma"]).strip().upper()
    held = policy.skip_reason(ma) == "held"
    present = "status" in row
    status = row.get("status")
    classified = _classify(status, present)
    flags: tuple[StatusFlag, ...] = ()
    if classified is not None:
        kind, stored = classified
        flags = (StatusFlag(ma, kind, stored, held),)
    shown = None if not present else _stored(status)
    return StatusRow(ma, shown, _price_text(row), held, flags)


def _classify(status: object, present: bool) -> tuple[str, str] | None:
    if not present:
        return "missing_status", ""
    if status is None:
        return "blank_status", "null"
    if isinstance(status, str):
        if status.strip().casefold() in _BLANK:
            return "blank_status", status
        if status in KNOWN_STATUSES:
            return None
        return "unknown_status", status
    return "unreadable_status", _stored(status)


def _price_text(row: dict[str, object]) -> str | None:
    if "priceUsd" not in row or row.get("priceUsd") is None:
        return None
    return _stored(row.get("priceUsd"))


def _stored(value: object) -> str:
    if isinstance(value, str):
        return value
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"))


def _status_cell(status: str | None) -> str:
    if status is None:
        return "—"
    if status == "":
        return '""'
    return _md(status)


def _md(value: str) -> str:
    return value.replace("`", "'").replace("\n", " ").replace("|", "\\|")


def _refuse_reason(fixture: str, out: str, held: str) -> str | None:
    if _is_live_target(fixture) or (held and _is_live_target(held)):
        return "Catalog status checks read a fixture file. Live catalogs are not read."
    fixture_path = Path(fixture)
    out_path = Path(out)
    if _is_protected(fixture_path):
        return "Catalog status checks read a fixture file. Shop catalog files are not read."
    if _is_protected(out_path):
        return "The report is not written into shop catalog files."
    if fixture_path.exists() and out_path.exists() and fixture_path.resolve() == out_path.resolve():
        return "The report is not written over the fixture."
    report_json_path = out_path / "catalog-status.json"
    if fixture_path.exists() and report_json_path.resolve() == fixture_path.resolve():
        return "The report is not written over the fixture."
    return None


def _is_live_target(value: str) -> bool:
    text = value.strip().casefold()
    return (
        "://" in text
        or text.startswith("//")
        or text.startswith("blob:")
        or text.startswith("http")
    )


def _is_protected(path: Path) -> bool:
    if path.name.casefold() in _FORBIDDEN_NAMES:
        return True
    resolved = path.expanduser().resolve()
    if resolved.name.casefold() in _FORBIDDEN_NAMES:
        return True
    repo = Path(__file__).resolve().parents[1]
    protected = (
        repo / "data",
        repo / "sassy-closet" / "data",
        repo / "sassy-closet-shop" / "data",
    )
    for folder in protected:
        root = folder.resolve()
        if resolved == root or root in resolved.parents:
            return True
    return False


if __name__ == "__main__":
    raise SystemExit(main())
