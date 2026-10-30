"""Flag a catalog row whose status is sold when that mã is also on the held list.

Read a JSON catalog fixture and a JSON held-list fixture, then write a report.
A row is flagged only when the stored status is exactly "sold" and the mã is
on the fixture held list. The catalog status stays sold. The mã stays on the
held list. S06 stays $25.

This module does not rewrite a status or a price, and it does not write
intake, Blob, Square, data/held.json, or catalog rows. It does not post.
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

from held_policy import HeldPolicy, load_held_policy, norm_ma

SOLD_STATUS = "sold"
_FORBIDDEN_NAMES = frozenset(
    {"held.json", "products.json", "catalog.v1.json", "submissions.json"}
)


@dataclass(frozen=True)
class SoldFlag:
    ma: str
    stored: str

    def as_json(self) -> dict[str, object]:
        return {
            "ma": self.ma,
            "kind": "sold_on_held",
            "stored": self.stored,
            "onHeldList": True,
        }


@dataclass(frozen=True)
class SoldRow:
    ma: str
    status: str | None
    price_usd: str | None
    on_held_list: bool
    flags: tuple[SoldFlag, ...]

    def as_json(self) -> dict[str, object]:
        return {
            "ma": self.ma,
            "status": self.status,
            "priceUsd": self.price_usd,
            "onHeldList": self.on_held_list,
            "flags": [flag.as_json() for flag in self.flags],
        }


@dataclass(frozen=True)
class SoldReport:
    rows: tuple[SoldRow, ...]
    held: tuple[str, ...]
    never_list: tuple[str, ...]

    @property
    def flags(self) -> tuple[SoldFlag, ...]:
        return tuple(flag for row in self.rows for flag in row.flags)

    @property
    def flag_count(self) -> int:
        return len(self.flags)

    def price_for(self, ma: str) -> str | None:
        code = norm_ma(ma)
        for row in self.rows:
            if row.ma == code:
                return row.price_usd
        return None


def flag_sold_on_held(rows: list[dict[str, object]], policy: HeldPolicy) -> SoldReport:
    """Return flags. Leave every input row and the held list as they were passed in."""
    held = tuple(policy.held)
    never_list = tuple(policy.never_list)
    checked: list[SoldRow] = []
    for row in rows:
        if not isinstance(row, dict) or not isinstance(row.get("ma"), str) or str(row.get("ma", "")).strip() == "":
            raise ValueError("fixture catalog row needs a mã")
        checked.append(_flag_row(row, policy))
    return SoldReport(tuple(checked), held, never_list)


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


def render_markdown(report: SoldReport) -> str:
    lines = [
        "# Sold mã also on the held list",
        "",
        "Read-only check of a fixture catalog against a fixture held list.",
        'Status "sold" is flagged when that mã is also on the held list.',
        "The catalog status is not changed.",
        "The mã is not removed from the held list.",
        "S06 stays $25.",
        "The stored status and price are not rewritten.",
        "",
        f"Rows: {len(report.rows)}",
        f"Flags: {report.flag_count}",
        f"Held list: {', '.join(report.held) if report.held else '—'}",
        f"Never list: {', '.join(report.never_list) if report.never_list else '—'}",
        "",
        "## Flags",
        "",
    ]
    if not report.flags:
        lines.append("None.")
    else:
        for flag in report.flags:
            lines.append(
                f"- {flag.ma} sold_on_held stored `{_md(flag.stored)}` stayed sold and stayed on the held list"
            )
    lines.extend(
        [
            "",
            "## Rows",
            "",
            "mã | on held list | status | price | flags",
            "--- | --- | --- | --- | ---",
        ]
    )
    for row in report.rows:
        kinds = ", ".join("sold_on_held" for _flag in row.flags) or "—"
        price = "—" if row.price_usd is None else _md(row.price_usd)
        listed = "yes" if row.on_held_list else "no"
        lines.append(
            f"{row.ma} | {listed} | {_status_cell(row.status)} | {price} | {kinds}"
        )
    lines.extend(
        [
            "",
            "## Left alone",
            "",
            "The flagged mã stayed sold.",
            "The flagged mã was not removed from the held list.",
            "Catalog rows, prices, and data/held.json were not written.",
            "",
        ]
    )
    return "\n".join(lines)


def report_json(report: SoldReport) -> dict[str, object]:
    return {
        "readOnly": True,
        "soldStatus": SOLD_STATUS,
        "s06": "stays $25",
        "s06PriceUsd": report.price_for("S06"),
        "heldList": list(report.held),
        "neverList": list(report.never_list),
        "removedFromHeldList": [],
        "statusRewrites": [],
        "flagCount": report.flag_count,
        "flags": [flag.as_json() for flag in report.flags],
        "rows": [row.as_json() for row in report.rows],
        "writes": [],
    }


def write_report(report: SoldReport, out_dir: Path) -> tuple[Path, Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    markdown_path = out_dir / "sold-on-held.md"
    json_path = out_dir / "sold-on-held.json"
    markdown_path.write_text(render_markdown(report), encoding="utf-8")
    json_path.write_text(json.dumps(report_json(report), indent=2) + "\n", encoding="utf-8")
    return markdown_path, json_path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Flag a fixture catalog row whose status is sold when that mã is also "
            "on a fixture held list. Writes a report only."
        ),
    )
    parser.add_argument("--fixture", required=True, help="Path to a JSON catalog fixture. Live catalogs are not read.")
    parser.add_argument("--held", required=True, help="Path to a JSON held-list fixture. data/held.json is not read.")
    parser.add_argument("--out", required=True, help="Directory for the markdown report and JSON sibling.")
    args = parser.parse_args(argv)
    refused = _refuse_reason(args.fixture, args.out, args.held)
    if refused:
        print(refused, file=sys.stderr)
        return 2
    fixture = Path(args.fixture)
    held_path = Path(args.held)
    out = Path(args.out)
    if not fixture.is_file():
        print(f"Fixture not found: {fixture}", file=sys.stderr)
        return 2
    if not held_path.is_file():
        print(f"Fixture held list not found: {held_path}", file=sys.stderr)
        return 2
    if out.exists() and not out.is_dir():
        print(f"Report directory is not a directory: {out}", file=sys.stderr)
        return 2
    try:
        payload = json.loads(fixture.read_text(encoding="utf-8"))
        rows = load_rows(payload)
        policy = load_held_policy(held_path)
        report = flag_sold_on_held(rows, policy)
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as error:
        print(str(error), file=sys.stderr)
        return 2
    markdown_path, _json_path = write_report(report, out)
    print(f"Sold on held flags: {report.flag_count}")
    print(f"report: {markdown_path}")
    return 1 if report.flag_count else 0


def _flag_row(row: dict[str, object], policy: HeldPolicy) -> SoldRow:
    ma = norm_ma(str(row["ma"]))
    on_list = policy.skip_reason(ma) == "held"
    present = "status" in row
    status = row.get("status")
    stored = _sold_spelling(status)
    flags: tuple[SoldFlag, ...] = ()
    if stored is not None and on_list:
        flags = (SoldFlag(ma, stored),)
    if not present:
        shown = None
    elif status is None:
        shown = "null"
    else:
        shown = _stored(status)
    return SoldRow(ma, shown, _price_text(row), on_list, flags)


def _sold_spelling(status: object) -> str | None:
    if isinstance(status, str) and status == SOLD_STATUS:
        return status
    return None


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
    if _is_live_target(fixture) or _is_live_target(held):
        return "Sold checks read a fixture catalog and a fixture held list. Live catalogs are not read."
    fixture_path = Path(fixture)
    held_path = Path(held)
    out_path = Path(out)
    if _is_protected(fixture_path) or _is_protected(held_path):
        return "Sold checks read fixture files. Shop catalog files and data/held.json are not read or written."
    if _is_protected(out_path):
        return "The report is not written into shop catalog files."
    if _same_file(fixture_path, out_path) or _same_file(held_path, out_path):
        return "The report is not written over the fixture."
    report_json_path = out_path / "sold-on-held.json"
    report_md_path = out_path / "sold-on-held.md"
    for source in (fixture_path, held_path):
        if _same_file(source, report_json_path) or _same_file(source, report_md_path):
            return "The report is not written over the fixture."
    return None


def _same_file(left: Path, right: Path) -> bool:
    if not left.exists() or not right.exists():
        return False
    return left.resolve() == right.resolve()


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
