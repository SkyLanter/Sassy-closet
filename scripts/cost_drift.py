"""Read-only intake ¥ versus parsed or public Taobao ¥.

Loads a local fixture, flags a blank ¥, a garbled ¥, and a gap over 8%,
and writes a report. Stored prices are copied. Nothing is rewritten.
Live intake is not read.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path

from freshness_check import classify_taobao
from intake_flags import (
    CNY_RE,
    DRIFT_LIMIT,
    IntakeFlag,
    IntakeRow,
    PublicCny,
    flag_cost_drift,
    format_cny,
    format_drift,
)


@dataclass(frozen=True)
class CostFixture:
    rows: tuple[IntakeRow, ...]
    public: dict[str, PublicCny]
    source: dict[str, str]


@dataclass(frozen=True)
class CostReport:
    day: str
    flags: tuple[IntakeFlag, ...]
    rows: tuple[dict[str, object], ...]


def load_cost_fixture(path: Path) -> CostFixture:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("fixture must be a JSON object")
    intake = payload.get("intake")
    taobao = payload.get("taobao", [])
    if not isinstance(intake, list):
        raise ValueError("fixture intake must be a list")
    if not isinstance(taobao, list):
        raise ValueError("fixture taobao must be a list")
    rows: list[IntakeRow] = []
    seen: set[str] = set()
    for item in intake:
        row = _intake_row(item)
        if row.ma in seen:
            raise ValueError(f"duplicate intake mã {row.ma}")
        seen.add(row.ma)
        rows.append(row)
    public: dict[str, PublicCny] = {}
    source: dict[str, str] = {}
    for item in taobao:
        code, listed, kind = resolve_taobao_item(item, path.parent)
        if code in public:
            raise ValueError(f"duplicate taobao mã {code}")
        public[code] = listed
        source[code] = kind
    return CostFixture(tuple(rows), public, source)


def resolve_taobao_item(item: object, fixture_dir: Path) -> tuple[str, PublicCny, str]:
    """Return the mã, the public ¥, and whether it was stated or parsed."""
    if not isinstance(item, dict):
        raise ValueError("taobao row must be an object")
    code = _code(item.get("ma"), "taobao row")
    state = item.get("state")
    if state is not None and state not in {"ok", "skip"}:
        raise ValueError(f"{code} taobao state must be ok or skip")
    detail = item.get("detail", "")
    if not isinstance(detail, str):
        raise ValueError(f"{code} detail must be text")
    if state == "skip":
        return code, PublicCny("skip", None, detail or "skip"), "public"
    if _has_public_cny(item):
        if "html" in item or "html_file" in item:
            raise ValueError(f"{code} has both a public ¥ and page HTML")
        value = _public_decimal(item.get("public_cny"), code)
        return code, PublicCny("ok", value, detail), "public"
    html = _html_text(item, fixture_dir, code)
    if html is None:
        return code, PublicCny("skip", None, detail or "no public ¥"), "none"
    view = classify_taobao(200, html)
    parsed_detail = view.detail or detail or "parsed"
    return code, PublicCny(view.state, view.public_cny, parsed_detail), "parsed"


def build_report(day: str, loaded: CostFixture) -> CostReport:
    flags = tuple(flag_cost_drift(list(loaded.rows), loaded.public))
    kinds: dict[str, list[str]] = {}
    for flag in flags:
        kinds.setdefault(flag.ma, []).append(flag.kind)
    rows: list[dict[str, object]] = []
    for row in loaded.rows:
        listed = loaded.public.get(row.ma)
        public_cny = None
        public_state = None
        public_detail = ""
        if listed is not None:
            public_state = listed.state
            public_detail = listed.detail
            if listed.value is not None:
                public_cny = format_cny(listed.value)
        rows.append(
            {
                "ma": row.ma,
                "intakeCny": "" if row.cost_cny is None else row.cost_cny,
                "publicCny": public_cny,
                "publicState": public_state,
                "publicDetail": public_detail,
                "source": loaded.source.get(row.ma, "none"),
                "sellUsd": row.sell_usd,
                "flags": kinds.get(row.ma, []),
            }
        )
    return CostReport(day, flags, tuple(rows))


def render_markdown(report: CostReport) -> str:
    lines = [
        f"# Intake cost drift {report.day}",
        "",
        "Read-only fixture comparison. Intake ¥ is checked against parsed or public Taobao ¥.",
        "Stored text is copied here and is not corrected.",
        "",
        f"Drift limit: over {format_drift(DRIFT_LIMIT)}.",
        "",
        f"Flags: {len(report.flags)}",
        "",
        "## Flags",
        "",
    ]
    if not report.flags:
        lines.append("None.")
    else:
        for flag in report.flags:
            extra = ""
            if flag.public_cny:
                extra += f" public ¥ {flag.public_cny}"
            if flag.drift:
                extra += f" drift {flag.drift}"
            shown = json.dumps(flag.stored, ensure_ascii=False)
            lines.append(f"- {flag.ma} {flag.kind}: stored {shown}{extra}")
    lines.extend(
        [
            "",
            "## Rows",
            "",
            "mã | intake ¥ | public ¥ | source | sell USD | flags",
            "--- | --- | --- | --- | --- | ---",
        ]
    )
    for row in report.rows:
        lines.append(
            " | ".join(
                [
                    str(row["ma"]),
                    _intake_cell(row.get("intakeCny")),
                    _public_cell(row),
                    str(row.get("source")),
                    _plain(row.get("sellUsd")),
                    _flag_cell(row.get("flags")),
                ]
            )
        )
    lines.append("")
    return "\n".join(lines)


def report_json(report: CostReport) -> dict[str, object]:
    return {
        "day": report.day,
        "readOnly": True,
        "liveIntake": False,
        "driftAbove": format_drift(DRIFT_LIMIT),
        "flagCount": len(report.flags),
        "flags": [flag.as_json() for flag in report.flags],
        "rows": list(report.rows),
    }


def write_report(report: CostReport, out_dir: Path) -> tuple[Path, Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    markdown_path = out_dir / f"cost-drift-{report.day}.md"
    json_path = out_dir / f"cost-drift-{report.day}.json"
    markdown_path.write_text(render_markdown(report), encoding="utf-8")
    json_path.write_text(json.dumps(report_json(report), indent=2) + "\n", encoding="utf-8")
    return markdown_path, json_path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Write a read-only intake cost-drift report from a local fixture."
    )
    parser.add_argument("--fixture", help="Local fixture JSON. Live intake is not read.")
    parser.add_argument("--out", default="out")
    parser.add_argument("--date", default=datetime.now(timezone.utc).date().isoformat())
    args = parser.parse_args(argv)
    if not args.fixture:
        print("A local --fixture is required. Live intake is not read.", file=sys.stderr)
        return 2
    if args.fixture.startswith(("http://", "https://")):
        print("The fixture must be a local file. Live intake is not read.", file=sys.stderr)
        return 2
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", args.date) is None:
        print("date must be YYYY-MM-DD", file=sys.stderr)
        return 2
    path = Path(args.fixture)
    if not path.is_file():
        print("fixture file is missing. Live intake is not read.", file=sys.stderr)
        return 2
    try:
        report = build_report(args.date, load_cost_fixture(path))
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(str(error), file=sys.stderr)
        return 2
    markdown_path, json_path = write_report(report, Path(args.out))
    print(markdown_path)
    print(json_path)
    return 0


def _intake_row(item: object) -> IntakeRow:
    if not isinstance(item, dict):
        raise ValueError("intake row must be an object")
    code = _code(item.get("ma"), "intake row")
    if "cost_cny" not in item:
        raise ValueError(f"{code} needs cost_cny")
    cost = item.get("cost_cny")
    if cost is not None and not isinstance(cost, str):
        raise ValueError(f"{code} cost_cny must be text or null")
    sell = item.get("sell_usd")
    if "sell_usd" in item and sell is not None and not isinstance(sell, str):
        raise ValueError(f"{code} sell_usd must be text or null")
    return IntakeRow(code, cost if isinstance(cost, str) else None, sell if isinstance(sell, str) else None)


def _has_public_cny(item: dict[str, object]) -> bool:
    if "public_cny" not in item:
        return False
    value = item.get("public_cny")
    return value is not None and value != ""


def _public_decimal(raw: object, code: str) -> Decimal:
    if isinstance(raw, bool) or isinstance(raw, float) or not isinstance(raw, (int, str)):
        raise ValueError(f"{code} public ¥ must be text")
    if isinstance(raw, int):
        if raw < 0:
            raise ValueError(f"{code} public ¥ must be text")
        return Decimal(raw)
    text = raw.strip()
    if CNY_RE.fullmatch(text) is None:
        raise ValueError(f"{code} public ¥ is not a number")
    return Decimal(text)


def _html_text(item: dict[str, object], fixture_dir: Path, code: str) -> str | None:
    has_html = "html" in item
    has_file = "html_file" in item
    if has_html and has_file:
        raise ValueError(f"{code} has both html and html_file")
    if has_html:
        html = item.get("html")
        if not isinstance(html, str):
            raise ValueError(f"{code} html must be text")
        return html
    if not has_file:
        return None
    name = item.get("html_file")
    if not isinstance(name, str) or name.strip() == "":
        raise ValueError(f"{code} html_file must be a relative path")
    parts = Path(name).parts
    if name.startswith(("/", "\\")) or ".." in parts:
        raise ValueError(f"{code} html_file must stay inside the fixture directory")
    path = (fixture_dir / name).resolve()
    root = fixture_dir.resolve()
    if path != root and root not in path.parents:
        raise ValueError(f"{code} html_file must stay inside the fixture directory")
    if not path.is_file():
        raise ValueError(f"{code} html file is missing")
    return path.read_text(encoding="utf-8")


def _code(raw: object, label: str) -> str:
    if not isinstance(raw, str) or raw.strip() == "":
        raise ValueError(f"{label} needs a mã")
    return raw.strip().upper()


def _intake_cell(value: object) -> str:
    if not isinstance(value, str) or value == "":
        return "—"
    if value.strip() == "":
        return json.dumps(value, ensure_ascii=False)
    return value.replace("|", "/")


def _plain(value: object) -> str:
    if not isinstance(value, str) or value == "":
        return "—"
    return value.replace("|", "/")


def _flag_cell(value: object) -> str:
    if not isinstance(value, list) or not value:
        return "—"
    return ", ".join(str(item) for item in value)


def _public_cell(row: dict[str, object]) -> str:
    state = row.get("publicState")
    if state == "skip":
        detail = str(row.get("publicDetail") or "skip").replace("|", "/")
        return f"SKIP ({detail})"
    if state == "ok" and isinstance(row.get("publicCny"), str) and row.get("publicCny"):
        return str(row["publicCny"])
    return "—"


if __name__ == "__main__":
    raise SystemExit(main())
