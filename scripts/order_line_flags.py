"""Flag a fixture order when the same mã appears twice.

Read-only. Each priced line stays its own line. Repeated mãs are reported
and are not folded into one line. A missing price stays missing. Held mãs
and never-list mãs stay off the order. S06 stays $25.

This module does not write orders, Blob, intake, or data/held.json, and it
does not read or change the live shop catalog.
"""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from pathlib import Path

from held_policy import HeldPolicy, default_held_path, load_held_policy, norm_ma

MA_RE = re.compile(r"^[A-Z][0-9]{2}$")
S06_USD = Decimal("25")
_FORBIDDEN_NAMES = frozenset(
    {
        "held.json",
        "submissions.json",
        "catalog.v1.json",
        "orders.json",
        "products.json",
    }
)
_FORBIDDEN_ROOTS = frozenset({"data", "sassy-closet", "sassy-closet-shop", "excel-kit"})


@dataclass(frozen=True)
class OrderLine:
    ma: str
    title: str
    price_usd: str


@dataclass(frozen=True)
class RepeatedFlag:
    ma: str
    count: int
    prices: tuple[str | None, ...]
    on_order: int

    @property
    def kind(self) -> str:
        return "repeated"


@dataclass(frozen=True)
class OmittedLine:
    ma: str
    reason: str


@dataclass(frozen=True)
class OrderFlags:
    order_id: str | None
    lines: tuple[OrderLine, ...]
    flags: tuple[RepeatedFlag, ...]
    omitted: tuple[OmittedLine, ...]
    merged: bool
    local: bool


def flag_order(payload: object, policy: HeldPolicy | None = None) -> OrderFlags:
    """Report repeated mãs. Leave every fixture line and price as it was."""
    if not isinstance(payload, dict):
        raise ValueError("fixture order must be a JSON object")
    rules = policy or load_held_policy()
    raw_lines = payload.get("lines")
    if not isinstance(raw_lines, list):
        raise ValueError("fixture order lines must be a list")
    lines: list[OrderLine] = []
    omitted: list[OmittedLine] = []
    seen: dict[str, list[str | None]] = {}
    on_order_count: dict[str, int] = {}
    first_seen: list[str] = []
    for item in raw_lines:
        if not isinstance(item, dict):
            raise ValueError("fixture order line must be an object")
        code = _ma(item.get("ma"))
        reason = rules.skip_reason(code)
        if reason is not None:
            omitted.append(OmittedLine(code, reason))
            continue
        price = _price(item)
        if code == "S06" and price is not None and Decimal(price) != S06_USD:
            raise ValueError("S06 stays $25")
        title = _title(item)
        if code not in seen:
            first_seen.append(code)
            seen[code] = []
            on_order_count[code] = 0
        seen[code].append(price)
        if title is None:
            omitted.append(OmittedLine(code, "no-title"))
            continue
        if price is None:
            omitted.append(OmittedLine(code, "no-price"))
            continue
        lines.append(OrderLine(code, title, price))
        on_order_count[code] += 1
    flags = tuple(
        RepeatedFlag(code, len(seen[code]), tuple(seen[code]), on_order_count[code])
        for code in first_seen
        if len(seen[code]) >= 2
    )
    return OrderFlags(_order_id(payload), tuple(lines), flags, tuple(omitted), False, True)


def render_text(report: OrderFlags) -> str:
    header = "Order line flags" if report.order_id is None else f"Order line flags {report.order_id}"
    rows = [
        header,
        "",
        "Read-only. The same mã on two lines is flagged. Lines are not merged.",
        "No price is invented. Held mãs stay off the order. S06 stays $25.",
        "No order, Blob, intake, or data/held.json write.",
        "",
        f"Lines on the order: {len(report.lines)}. Repeated mãs: {len(report.flags)}.",
        "",
        "## On the order",
        "",
    ]
    if not report.lines:
        rows.append("None.")
    else:
        rows.extend(
            f"- {line.ma} — {line.title} — ${line.price_usd}" for line in report.lines
        )
    rows.extend(["", "## Flags", ""])
    if not report.flags:
        rows.append("None.")
    else:
        rows.extend(_flag_line(flag) for flag in report.flags)
    rows.extend(["", "## Off the order", ""])
    if not report.omitted:
        rows.append("None.")
    else:
        rows.extend(f"- {item.ma} {item.reason}" for item in report.omitted)
    rows.extend(
        [
            "",
            "## Left alone",
            "",
            "The fixture order was not rewritten.",
            "data/held.json was not written.",
            "",
        ]
    )
    return "\n".join(rows)


def render_json(report: OrderFlags) -> dict[str, object]:
    return {
        "orderId": report.order_id,
        "lines": [
            {"ma": line.ma, "title": line.title, "priceUsd": line.price_usd}
            for line in report.lines
        ],
        "flags": [
            {
                "ma": flag.ma,
                "kind": flag.kind,
                "count": flag.count,
                "onOrder": flag.on_order,
                "prices": list(flag.prices),
            }
            for flag in report.flags
        ],
        "omitted": [{"ma": item.ma, "reason": item.reason} for item in report.omitted],
        "merged": report.merged,
        "local": report.local,
    }


def write_report(report: OrderFlags, path: Path, *, source: Path | None = None) -> None:
    if not report.local:
        raise ValueError("local flags need a fixture order")
    _refuse_report_target(path, source)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_text(report), encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Flag a fixture order when the same mã appears twice. "
            "Does not merge lines, invent a price, or write data/held.json."
        )
    )
    parser.add_argument("--fixture", required=True, help="Fixture order JSON.")
    parser.add_argument("--held", help="Held policy JSON. Defaults to data/held.json.")
    parser.add_argument("--report", help="Write a local markdown report. Does not rewrite the fixture.")
    parser.add_argument("--json", action="store_true", help="Print JSON instead of text.")
    args = parser.parse_args(argv)
    try:
        _refuse_remote(args.fixture)
        if args.held:
            _refuse_remote(args.held)
        fixture_path = Path(args.fixture)
        payload = json.loads(fixture_path.read_text(encoding="utf-8"))
        policy = load_held_policy(Path(args.held)) if args.held else None
        report = flag_order(payload, policy)
        if args.report:
            write_report(report, Path(args.report), source=fixture_path)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(str(error), file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps(render_json(report), indent=2))
    else:
        print(render_text(report), end="")
        if args.report:
            print(f"report: {args.report}")
    return 0


def _flag_line(flag: RepeatedFlag) -> str:
    prices = ", ".join("no price" if price is None else f"${price}" for price in flag.prices)
    return (
        f"- {flag.ma} repeated {flag.count}. "
        f"Prices stay {prices}. Lines were not merged."
    )


def _order_id(payload: dict[str, object]) -> str | None:
    if "orderId" in payload:
        value = payload.get("orderId")
    elif "id" in payload:
        value = payload.get("id")
    else:
        return None
    if value is None:
        return None
    if not isinstance(value, str):
        raise ValueError("fixture order id must be a string")
    text = value.strip()
    return text or None


def _ma(value: object) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError("fixture order line needs a mã")
    code = norm_ma(value)
    if MA_RE.fullmatch(code) is None:
        raise ValueError(f"fixture order line has an invalid mã {value!r}")
    return code


def _title(item: dict[str, object]) -> str | None:
    if "title" not in item or item.get("title") is None:
        return None
    value = item.get("title")
    if not isinstance(value, str):
        raise ValueError("fixture order line title must be a string")
    text = value.strip()
    return text or None


def _price(item: dict[str, object]) -> str | None:
    if "priceUsd" not in item:
        return None
    value = item.get("priceUsd")
    if value is None:
        return None
    if isinstance(value, str) and value.strip() == "":
        return None
    return _price_text(value)


def _price_text(value: object) -> str:
    if isinstance(value, bool):
        raise ValueError("price must be a number")
    if isinstance(value, int):
        money = Decimal(value)
    elif isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError("price must be a number")
        money = Decimal(str(value))
    elif isinstance(value, str):
        text = value.strip().replace("$", "").replace(",", "")
        if text == "":
            raise ValueError("price must be a number")
        try:
            money = Decimal(text)
        except InvalidOperation as error:
            raise ValueError("price must be a number") from error
    else:
        raise ValueError("price must be a number")
    if not money.is_finite() or money < 0:
        raise ValueError("price must be a non-negative number")
    rendered = format(money, "f")
    if "." in rendered:
        rendered = rendered.rstrip("0").rstrip(".")
    return rendered or "0"


def _refuse_remote(path: str) -> None:
    lowered = path.strip().lower()
    if lowered.startswith(("http://", "https://", "blob:")):
        raise ValueError("fixture order must be a local file")


def _refuse_report_target(path: Path, source: Path | None) -> None:
    resolved = path if path.is_absolute() else Path.cwd() / path
    resolved = resolved.resolve()
    if source is not None and resolved == source.resolve():
        raise ValueError("refusing to overwrite the fixture order")
    if resolved == default_held_path().resolve() or resolved.name in _FORBIDDEN_NAMES:
        raise ValueError(f"refusing to write {resolved.name}")
    repo = Path(__file__).resolve().parents[1]
    try:
        relative = resolved.relative_to(repo)
    except ValueError:
        relative = None
    if relative is not None and relative.parts and relative.parts[0] in _FORBIDDEN_ROOTS:
        raise ValueError("refusing to write inside shop data, intake, or the sell catalog")
    if resolved.suffix.lower() != ".md":
        raise ValueError("local report must be a markdown file")


if __name__ == "__main__":
    raise SystemExit(main())
