"""Local packing-slip preview from a fixture order.

Each slip line copies the mã, title, and priceUsd already on that fixture
line. Held mãs and never-list mãs are left off the slip. A line with no
priceUsd is left off too. No price is calculated.

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
    {"held.json", "submissions.json", "catalog.v1.json", "orders.json"}
)
_FORBIDDEN_ROOTS = frozenset({"data", "sassy-closet", "sassy-closet-shop", "excel-kit"})


@dataclass(frozen=True)
class SlipLine:
    ma: str
    title: str
    price_usd: str


@dataclass(frozen=True)
class OmittedLine:
    ma: str
    reason: str


@dataclass(frozen=True)
class PackingSlip:
    order_id: str | None
    lines: tuple[SlipLine, ...]
    omitted: tuple[OmittedLine, ...]
    local: bool


def preview_order(payload: object, policy: HeldPolicy | None = None) -> PackingSlip:
    """Copy fixture lines. Omit held mãs. Leave every fixture price as it was."""
    if not isinstance(payload, dict):
        raise ValueError("fixture order must be a JSON object")
    rules = policy or load_held_policy()
    raw_lines = payload.get("lines")
    if not isinstance(raw_lines, list):
        raise ValueError("fixture order lines must be a list")
    lines: list[SlipLine] = []
    omitted: list[OmittedLine] = []
    for item in raw_lines:
        if not isinstance(item, dict):
            raise ValueError("fixture order line must be an object")
        code = _ma(item.get("ma"))
        reason = rules.skip_reason(code)
        if reason is not None:
            omitted.append(OmittedLine(code, reason))
            continue
        title = _title(item)
        if title is None:
            omitted.append(OmittedLine(code, "no-title"))
            continue
        price = _price(item)
        if price is None:
            omitted.append(OmittedLine(code, "no-price"))
            continue
        if code == "S06" and Decimal(price) != S06_USD:
            raise ValueError("S06 stays $25")
        lines.append(SlipLine(code, title, price))
    return PackingSlip(_order_id(payload), tuple(lines), tuple(omitted), True)


def render_text(slip: PackingSlip) -> str:
    header = "Packing slip" if slip.order_id is None else f"Packing slip {slip.order_id}"
    rows = [header]
    rows.extend(f"{line.ma}  {line.title}  ${line.price_usd}" for line in slip.lines)
    return "\n".join(rows) + "\n"


def render_json(slip: PackingSlip) -> dict[str, object]:
    return {
        "orderId": slip.order_id,
        "lines": [
            {"ma": line.ma, "title": line.title, "priceUsd": line.price_usd} for line in slip.lines
        ],
        "omitted": [{"ma": item.ma, "reason": item.reason} for item in slip.omitted],
        "local": slip.local,
    }


def render_page(slip: PackingSlip) -> str:
    if not slip.local:
        raise ValueError("local preview needs a fixture order")
    heading = "Packing slip" if slip.order_id is None else f"Packing slip {slip.order_id}"
    body = "\n".join(
        "<tr>"
        f"<td>{_escape(line.ma)}</td>"
        f"<td>{_escape(line.title)}</td>"
        f"<td>${_escape(line.price_usd)}</td>"
        "</tr>"
        for line in slip.lines
    )
    return (
        "<!DOCTYPE html>\n"
        '<html lang="en">\n'
        "<head>\n"
        '<meta charset="utf-8">\n'
        f"<title>{_escape(heading)}</title>\n"
        "</head>\n"
        "<body>\n"
        f"<h1>{_escape(heading)}</h1>\n"
        "<p>Local fixture preview. No order is written.</p>\n"
        "<table>\n"
        "<thead><tr><th>Mã</th><th>Title</th><th>Price</th></tr></thead>\n"
        f"<tbody>\n{body}\n</tbody>\n"
        "</table>\n"
        "</body>\n"
        "</html>\n"
    )


def write_page(slip: PackingSlip, path: Path) -> None:
    if not slip.local:
        raise ValueError("local preview needs a fixture order")
    _refuse_page_target(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_page(slip), encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Print a packing slip from a fixture order. "
            "Does not write orders, Blob, intake, or data/held.json."
        )
    )
    parser.add_argument("--fixture", required=True, help="Fixture order JSON.")
    parser.add_argument("--page", help="Write a local HTML preview from the fixture already loaded.")
    parser.add_argument("--json", action="store_true", help="Print JSON instead of text.")
    args = parser.parse_args(argv)
    try:
        payload = json.loads(Path(args.fixture).read_text(encoding="utf-8"))
        slip = preview_order(payload)
        if args.page:
            write_page(slip, Path(args.page))
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(str(error), file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps(render_json(slip), indent=2))
    else:
        print(render_text(slip), end="")
        if args.page:
            print(f"page: {args.page}")
    return 0


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


def _escape(value: str) -> str:
    return (
        value.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def _refuse_page_target(path: Path) -> None:
    resolved = path if path.is_absolute() else Path.cwd() / path
    resolved = resolved.resolve()
    if resolved == default_held_path().resolve() or resolved.name in _FORBIDDEN_NAMES:
        raise ValueError(f"refusing to write {resolved.name}")
    repo = Path(__file__).resolve().parents[1]
    try:
        relative = resolved.relative_to(repo)
    except ValueError:
        relative = None
    if relative is not None and relative.parts and relative.parts[0] in _FORBIDDEN_ROOTS:
        raise ValueError("refusing to write inside shop data, intake, or the sell catalog")
    if resolved.suffix.lower() not in {".html", ".htm"}:
        raise ValueError("local preview must be an html file")


if __name__ == "__main__":
    raise SystemExit(main())
