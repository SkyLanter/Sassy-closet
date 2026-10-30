"""Flag a fixture shop link that contains a space or a newline.

Read a JSON fixture and write a report. Stored links stay as they were.
A blank link stays blank. This module does not encode or rewrite the link,
fetch a shop, or write intake, Blob, Square, data/held.json, prices, or
catalog rows. S06 stays $25.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path

_MISSING = object()


@dataclass(frozen=True)
class LinkFlag:
    ma: str
    kind: str
    field: str
    stored: str

    def as_json(self) -> dict[str, str]:
        return {
            "ma": self.ma,
            "kind": self.kind,
            "field": self.field,
            "stored": self.stored,
        }


@dataclass(frozen=True)
class LinkRow:
    ma: str
    sell_usd: str | None
    field: str
    stored: str
    mark: str
    flags: tuple[LinkFlag, ...]

    def as_json(self) -> dict[str, object]:
        return {
            "ma": self.ma,
            "sellUsd": self.sell_usd,
            "field": self.field,
            "stored": self.stored,
            "mark": self.mark,
            "flags": [flag.as_json() for flag in self.flags],
        }


@dataclass(frozen=True)
class LinkReport:
    rows: tuple[LinkRow, ...]

    @property
    def flags(self) -> tuple[LinkFlag, ...]:
        return tuple(flag for row in self.rows for flag in row.flags)

    @property
    def flag_count(self) -> int:
        return len(self.flags)


def flag_space_newline_shop_links(rows: list[dict[str, object]]) -> LinkReport:
    """Return flags. Leave every input row as it was passed in."""
    checked: list[LinkRow] = []
    for row in rows:
        if not isinstance(row, dict) or not isinstance(row.get("ma"), str) or row.get("ma", "").strip() == "":
            raise ValueError("fixture shop row needs a mã")
        checked.append(_flag_row(row))
    return LinkReport(tuple(checked))


def load_rows(payload: object) -> list[dict[str, object]]:
    if isinstance(payload, list):
        rows = payload
    elif isinstance(payload, dict):
        rows = None
        for key in ("submissions", "products", "intake"):
            value = payload.get(key)
            if isinstance(value, list):
                rows = value
                break
        if rows is None:
            raise ValueError("fixture must be a list or an object with submissions, products, or intake")
    else:
        raise ValueError("fixture must be a list or an object with submissions, products, or intake")
    if not all(isinstance(row, dict) for row in rows):
        raise ValueError("fixture shop row needs a mã")
    return rows


def render_markdown(report: LinkReport) -> str:
    lines = [
        "# Shop link space or newline flags",
        "",
        "Read-only copy of fixture shop links. A space or a newline is flagged and left as stored.",
        "A blank link stays blank. S06 stays $25.",
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
            lines.append(
                f"- {flag.ma} {flag.kind} `{flag.field}`: stored `{_md(flag.stored)}`"
            )
    lines.extend(
        [
            "",
            "## Rows",
            "",
            "mã | sell | field | mark | flags",
            "--- | --- | --- | --- | ---",
        ]
    )
    for row in report.rows:
        kinds = ", ".join(flag.kind for flag in row.flags) or "—"
        sell = "—" if row.sell_usd is None else _md(row.sell_usd)
        lines.append(f"{row.ma} | {sell} | {row.field} | {row.mark} | {kinds}")
    lines.append("")
    return "\n".join(lines)


def report_json(report: LinkReport) -> dict[str, object]:
    s06_sell = next((row.sell_usd for row in report.rows if row.ma == "S06"), None)
    return {
        "readOnly": True,
        "links": "unchanged",
        "rewritten": False,
        "s06SellUsd": s06_sell,
        "flagCount": report.flag_count,
        "flags": [flag.as_json() for flag in report.flags],
        "rows": [row.as_json() for row in report.rows],
    }


def write_report(report: LinkReport, out_dir: Path) -> tuple[Path, Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    markdown_path = out_dir / "space-newline-shop-link-flags.md"
    json_path = out_dir / "space-newline-shop-link-flags.json"
    markdown_path.write_text(render_markdown(report), encoding="utf-8")
    json_path.write_text(
        json.dumps(report_json(report), indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return markdown_path, json_path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Flag a fixture shop link that contains a space or a newline. Writes a report only.",
    )
    parser.add_argument("--fixture", required=True, help="Path to a JSON fixture. The shop catalog is not read.")
    parser.add_argument("--out", required=True, help="Directory for the markdown report and JSON sibling.")
    args = parser.parse_args(argv)
    try:
        _reject_live(args.fixture)
        _reject_live(args.out)
        fixture = Path(args.fixture).resolve()
        out_dir = Path(args.out).resolve()
        if out_dir == fixture or fixture.is_relative_to(out_dir):
            raise ValueError("refusing to overwrite the fixture")
        if not fixture.is_file():
            raise ValueError(f"Fixture not found: {fixture}")
        payload = json.loads(fixture.read_text(encoding="utf-8"))
        report = flag_space_newline_shop_links(load_rows(payload))
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as error:
        print(str(error), file=sys.stderr)
        return 2
    markdown_path, _json_path = write_report(report, out_dir)
    print(f"Shop link space or newline flags: {report.flag_count}")
    print(f"report: {markdown_path}")
    return 1 if report.flag_count else 0


def _flag_row(row: dict[str, object]) -> LinkRow:
    ma = str(row["ma"]).strip().upper()
    field, raw = _link_field(row)
    sell = _sell(row)
    if raw is _MISSING or _is_blank(raw):
        stored = "" if raw is _MISSING or raw is None else _stored(raw)
        return LinkRow(ma, sell, field, stored, "blank", ())
    stored = _stored(raw)
    if not isinstance(raw, str):
        return LinkRow(ma, sell, field, stored, "other", ())
    kind = _kind(raw)
    flags = () if kind is None else (LinkFlag(ma, kind, field, stored),)
    return LinkRow(ma, sell, field, stored, "clean" if kind is None else kind, flags)


def _kind(text: str) -> str | None:
    space = " " in text
    newline = "\n" in text or "\r" in text
    if space and newline:
        return "space_and_newline"
    if space:
        return "space"
    if newline:
        return "newline"
    return None


def _link_field(row: dict[str, object]) -> tuple[str, object]:
    if "link" in row:
        return "link", row["link"]
    if "source_link" in row:
        return "source_link", row["source_link"]
    if "sourceLink" in row:
        return "sourceLink", row["sourceLink"]
    return "link", _MISSING


def _is_blank(raw: object) -> bool:
    if raw is None:
        return True
    if isinstance(raw, str):
        return raw.strip() == ""
    return False


def _sell(row: dict[str, object]) -> str | None:
    if "sell_usd" in row and row.get("sell_usd") is not None:
        sell = row["sell_usd"]
        return sell if isinstance(sell, str) else str(sell)
    if "priceUsd" in row and row.get("priceUsd") is not None:
        price = row["priceUsd"]
        return price if isinstance(price, str) else str(price)
    return None


def _stored(value: object) -> str:
    if isinstance(value, str):
        return value
    if value is None:
        return ""
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"))


def _md(value: str) -> str:
    return (
        value.replace("`", "'")
        .replace("|", "/")
        .replace("\r", "\\r")
        .replace("\n", "\\n")
        .replace("\t", "\\t")
    )


def _reject_live(raw: str) -> None:
    text = raw.strip()
    if "://" in text or text.lower().startswith("blob:"):
        raise ValueError("fixtures only; refusing a URL")
    path = Path(raw).resolve()
    root = Path(__file__).resolve().parents[1]
    banned_roots = (
        root / "data",
        root / "sassy-closet-shop" / "data",
        root / "sassy-closet-shop" / "public" / "data",
    )
    for ban in banned_roots:
        folder = ban.resolve()
        if path == folder or path.is_relative_to(folder):
            raise ValueError("fixtures only; refusing the shop catalog and held list")


if __name__ == "__main__":
    raise SystemExit(main())
