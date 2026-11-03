"""Flag intake shop links that are not a Taobao item or an e.tb.cn share.

Read a JSON fixture and write a report. Stored links stay as they were.
This module does not rewrite links, fetch Taobao, or write intake, Blob,
Square, data/held.json, prices, or catalog rows. S06 stays $25. Held mãs
stay held.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parent
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from held_policy import HeldPolicy, load_held_policy, norm_ma

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
_HTTP_RE = re.compile(
    r"^(?P<scheme>https?)://(?P<host>[A-Za-z0-9.-]+)"
    r"(?::(?P<port>\d+))?(?P<path>/[^?#]*)?(?:\?(?P<query>[^#]*))?(?:#(?P<fragment>.*))?$",
    re.IGNORECASE,
)
_SHARE_PATH_RE = re.compile(r"^/h\.[A-Za-z0-9]+$")
_WORLD_ITEM_RE = re.compile(r"^/item/(\d{6,})\.htm$", re.IGNORECASE)
_ITEM_PAGE_RE = re.compile(r"^/item\.htm$", re.IGNORECASE)
_SHORT_ITEM_RE = re.compile(r"^/i(\d{6,})\.htm$", re.IGNORECASE)
_H5_ITEM_RE = re.compile(r"^/awp/core/detail\.htm$", re.IGNORECASE)
_ITEM_ID_RE = re.compile(r"(?:^|&)id=(\d{6,})(?:&|$)")
_SCHEME_RE = re.compile(r"^[a-z][a-z0-9+.-]*:", re.IGNORECASE)
_ITEM_HOSTS = frozenset({"item.taobao.com", "detail.taobao.com"})
_MISSING = object()


@dataclass(frozen=True)
class LinkVerdict:
    kind: str | None
    reason: str
    shape: str


@dataclass(frozen=True)
class LinkFlag:
    ma: str
    kind: str
    field: str
    stored: str
    reason: str
    held: bool

    def as_json(self) -> dict[str, object]:
        return {
            "ma": self.ma,
            "kind": self.kind,
            "field": self.field,
            "stored": self.stored,
            "reason": self.reason,
            "held": self.held,
        }


@dataclass(frozen=True)
class LinkRow:
    ma: str
    held: bool
    sell_usd: str | None
    field: str
    stored: str
    shape: str
    flags: tuple[LinkFlag, ...]

    def as_json(self) -> dict[str, object]:
        return {
            "ma": self.ma,
            "held": self.held,
            "sellUsd": self.sell_usd,
            "field": self.field,
            "stored": self.stored,
            "shape": self.shape,
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


def classify_shop_link(raw: object) -> LinkVerdict:
    """Classify one stored link. Return no replacement URL."""
    if raw is None:
        return LinkVerdict("blank_link", "null", "")
    if not isinstance(raw, str):
        return LinkVerdict("not_shop_link", "not_a_string", "")
    stripped = raw.replace("\u00a0", " ").strip()
    if stripped.casefold() in _BLANK:
        return LinkVerdict("blank_link", "blank", "")
    if re.search(r"\s", stripped):
        if re.search(r"https?://", stripped, re.IGNORECASE):
            return LinkVerdict("not_shop_link", "wrapped", "")
        return LinkVerdict("not_shop_link", "not_a_url", "")
    match = _HTTP_RE.fullmatch(stripped)
    if match is None:
        if re.match(r"https?://", stripped, re.IGNORECASE):
            return LinkVerdict("not_shop_link", "not_a_url", "")
        if _SCHEME_RE.match(stripped):
            return LinkVerdict("not_shop_link", "not_http", "")
        return LinkVerdict("not_shop_link", "not_a_url", "")
    if match.group("port"):
        return LinkVerdict("not_shop_link", "has_port", "")
    host = match.group("host").casefold()
    path = match.group("path") or ""
    query = match.group("query") or ""
    if host == "e.tb.cn":
        if _SHARE_PATH_RE.fullmatch(path):
            return LinkVerdict(None, "", "e.tb.cn")
        return LinkVerdict("not_shop_link", "not_share", "")
    if host == "taobao.com" or host.endswith(".taobao.com"):
        if _is_taobao_item(host, path, query):
            return LinkVerdict(None, "", "taobao-item")
        return LinkVerdict("not_shop_link", "not_item", "")
    return LinkVerdict("not_shop_link", "not_taobao", "")


def flag_intake_shop_links(rows: list[dict[str, object]], policy: HeldPolicy) -> LinkReport:
    """Return flags. Leave every input row as it was passed in."""
    checked: list[LinkRow] = []
    for row in rows:
        if not isinstance(row, dict) or not isinstance(row.get("ma"), str) or row.get("ma", "").strip() == "":
            raise ValueError("fixture intake row needs a mã")
        checked.append(_flag_row(row, policy))
    return LinkReport(tuple(checked))


def load_rows(payload: object) -> list[dict[str, object]]:
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


def render_markdown(report: LinkReport) -> str:
    lines = [
        "# Intake shop link flags",
        "",
        "Read-only copy of fixture shop links. Links stay as stored.",
        "Taobao is not fetched. S06 stays $25. Held mãs stay held.",
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
            lines.append(
                f"- {flag.ma} {flag.kind} `{flag.field}` {flag.reason}: "
                f"stored `{_md(flag.stored)}`{hold}"
            )
    lines.extend(
        [
            "",
            "## Rows",
            "",
            "mã | held | sell | shape | flags",
            "--- | --- | --- | --- | ---",
        ]
    )
    for row in report.rows:
        kinds = ", ".join(flag.kind for flag in row.flags) or "—"
        sell = "—" if row.sell_usd is None else _md(row.sell_usd)
        shape = row.shape or "—"
        lines.append(f"{row.ma} | {str(row.held).lower()} | {sell} | {shape} | {kinds}")
    lines.append("")
    return "\n".join(lines)


def report_json(report: LinkReport) -> dict[str, object]:
    return {
        "readOnly": True,
        "links": "unchanged",
        "fetchedTaobao": False,
        "s06": "stays $25",
        "heldMas": "stay held",
        "flagCount": report.flag_count,
        "flags": [flag.as_json() for flag in report.flags],
        "rows": [row.as_json() for row in report.rows],
    }


def write_report(report: LinkReport, out_dir: Path) -> tuple[Path, Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    markdown_path = out_dir / "intake-shop-link-flags.md"
    json_path = out_dir / "intake-shop-link-flags.json"
    markdown_path.write_text(render_markdown(report), encoding="utf-8")
    json_path.write_text(json.dumps(report_json(report), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return markdown_path, json_path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Flag intake shop links that are not a Taobao item or an e.tb.cn share. Writes a report only.",
    )
    parser.add_argument("--fixture", required=True, help="Path to a JSON fixture. Live intake is not read.")
    parser.add_argument("--out", required=True, help="Directory for the markdown report and JSON sibling.")
    parser.add_argument("--held", default="", help="Held-list JSON to read. Defaults to data/held.json.")
    args = parser.parse_args(argv)
    if _is_live_target(args.fixture) or _is_live_target(args.held):
        print("Live intake is not read. Pass a fixture file.", file=sys.stderr)
        return 2
    fixture = Path(args.fixture)
    if not fixture.is_file():
        print(f"Fixture not found: {fixture}", file=sys.stderr)
        return 2
    try:
        payload = json.loads(fixture.read_text(encoding="utf-8"))
        rows = load_rows(payload)
        policy = load_held_policy(Path(args.held) if args.held else None)
        report = flag_intake_shop_links(rows, policy)
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as error:
        print(str(error), file=sys.stderr)
        return 2
    markdown_path, _json_path = write_report(report, Path(args.out))
    print(f"Intake shop link flags: {report.flag_count}")
    print(f"report: {markdown_path}")
    return 1 if report.flag_count else 0


def _flag_row(row: dict[str, object], policy: HeldPolicy) -> LinkRow:
    ma = norm_ma(str(row["ma"]))
    held = policy.skip_reason(ma) == "held"
    field, raw = _link_field(row)
    if raw is _MISSING:
        verdict = LinkVerdict("blank_link", "missing", "")
        stored = ""
    else:
        verdict = classify_shop_link(raw)
        stored = _stored(raw)
    flags: tuple[LinkFlag, ...] = ()
    if verdict.kind is not None:
        flags = (LinkFlag(ma, verdict.kind, field, stored, verdict.reason, held),)
    return LinkRow(ma, held, _sell(row), field, stored, verdict.shape, flags)


def _link_field(row: dict[str, object]) -> tuple[str, object]:
    if "link" in row:
        return "link", row["link"]
    if "source_link" in row:
        return "source_link", row["source_link"]
    if "sourceLink" in row:
        return "sourceLink", row["sourceLink"]
    return "link", _MISSING


def _is_taobao_item(host: str, path: str, query: str) -> bool:
    if host == "world.taobao.com":
        return _WORLD_ITEM_RE.fullmatch(path) is not None
    if host == "h5.m.taobao.com":
        return _H5_ITEM_RE.fullmatch(path) is not None and _ITEM_ID_RE.search(query) is not None
    if host in _ITEM_HOSTS:
        if _SHORT_ITEM_RE.fullmatch(path):
            return True
        return _ITEM_PAGE_RE.fullmatch(path) is not None and _ITEM_ID_RE.search(query) is not None
    return False


def _sell(row: dict[str, object]) -> str | None:
    if "sell_usd" not in row or row.get("sell_usd") is None:
        return None
    sell = row["sell_usd"]
    return sell if isinstance(sell, str) else str(sell)


def _stored(value: object) -> str:
    if isinstance(value, str):
        return value
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"))


def _md(value: str) -> str:
    return (
        value.replace("`", "'")
        .replace("|", "/")
        .replace("\r", "\\r")
        .replace("\n", "\\n")
        .replace("\t", "\\t")
    )


def _is_live_target(value: str) -> bool:
    text = value.strip().casefold()
    return "://" in text or text.startswith("blob:") or text.startswith("http")


if __name__ == "__main__":
    raise SystemExit(main())
