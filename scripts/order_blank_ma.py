"""Flag a fixture order line whose mã is blank.

Read-only. A blank, missing, or null mã is reported on that line. No mã is
filled in, and no price is filled in. The fixture file is not rewritten.
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

from held_policy import HeldPolicy, default_held_path, load_held_policy

BLANK_MA = "blank-ma"
MISSING = "missing"
NULL = "null"
EMPTY = "empty"
WHITESPACE = "whitespace"
BLANK_FORMS = (MISSING, NULL, EMPTY, WHITESPACE)
NO_PRICE = "no-price"
HELD = "held"
NEVER_LIST = "never-list"
OMIT_REASONS = (NO_PRICE, HELD, NEVER_LIST)

_MA_CODE = re.compile(r"^[A-Z][0-9]{2}$")
_AMOUNT = re.compile(r"\d+(?:\.\d+)?")
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
class CleanLine:
    line: int
    ma: str
    title: str | None
    price_usd: str

    def as_json(self) -> dict[str, object]:
        return {
            "line": self.line,
            "ma": self.ma,
            "title": self.title,
            "priceUsd": self.price_usd,
        }


@dataclass(frozen=True)
class BlankFlag:
    line: int
    kind: str
    blank: str
    stored_ma: str | None
    title: str | None
    price_usd: str | None

    def as_json(self) -> dict[str, object]:
        _require_kind(self.kind)
        _require_blank(self.blank)
        return {
            "line": self.line,
            "kind": self.kind,
            "blank": self.blank,
            "storedMa": self.stored_ma,
            "title": self.title,
            "priceUsd": self.price_usd,
        }


@dataclass(frozen=True)
class OmittedLine:
    line: int
    ma: str
    reason: str

    def as_json(self) -> dict[str, object]:
        _require_reason(self.reason)
        return {"line": self.line, "ma": self.ma, "reason": self.reason}


@dataclass(frozen=True)
class BlankResult:
    order_id: str | None
    lines: tuple[CleanLine, ...]
    flags: tuple[BlankFlag, ...]
    omitted: tuple[OmittedLine, ...]


def flag_fixture(payload: object, policy: HeldPolicy | None = None) -> BlankResult:
    """Return blank-mã flags. Leave every line, mã, and price as passed in."""
    if not isinstance(payload, dict):
        raise ValueError("fixture must be a JSON object")
    rules = policy if policy is not None else load_held_policy()
    raw_lines = payload.get("lines")
    if not isinstance(raw_lines, list):
        raise ValueError("fixture lines must be a list")
    lines: list[CleanLine] = []
    flags: list[BlankFlag] = []
    omitted: list[OmittedLine] = []
    for index, item in enumerate(raw_lines, start=1):
        if not isinstance(item, dict):
            raise ValueError("fixture order line must be an object")
        title = _title(item)
        price = _price(item)
        code, blank, stored = _ma(item)
        if blank is not None:
            flags.append(BlankFlag(index, BLANK_MA, blank, stored, title, price))
            continue
        if code is None:
            raise ValueError("fixture order line needs a mã")
        reason = rules.skip_reason(code)
        if reason is not None:
            omitted.append(OmittedLine(index, code, reason))
            continue
        if price is None:
            omitted.append(OmittedLine(index, code, NO_PRICE))
            continue
        lines.append(CleanLine(index, code, title, price))
    return BlankResult(_order_id(payload), tuple(lines), tuple(flags), tuple(omitted))


def render_report(result: BlankResult) -> str:
    _reject_unknown(result)
    rows = [
        "# Blank mã on an order line",
        "",
        "Read-only. A line with a blank mã is flagged. No mã was invented. "
        "No price was invented. The fixture file was not rewritten.",
        "",
        f"Flags: {len(result.flags)}",
        "",
        "## Clean lines",
        "",
    ]
    if result.lines:
        rows.extend(_clean_line(item) for item in result.lines)
    else:
        rows.append("None.")
    rows.extend(["", "## Blank mã", ""])
    if result.flags:
        rows.extend(_flag_line(item) for item in result.flags)
    else:
        rows.append("No flags.")
    rows.extend(["", "## Left off this check", ""])
    if result.omitted:
        rows.extend(_omit_line(item) for item in result.omitted)
    else:
        rows.append("None.")
    rows.append("")
    return "\n".join(rows)


def findings_payload(result: BlankResult) -> dict[str, object]:
    _reject_unknown(result)
    return {
        "orderId": result.order_id,
        "lines": [item.as_json() for item in result.lines],
        "flags": [item.as_json() for item in result.flags],
        "omitted": [item.as_json() for item in result.omitted],
    }


def write_outputs(result: BlankResult, out_dir: Path, *, source: Path | None = None) -> tuple[Path, Path]:
    _refuse_out(out_dir, source)
    report = render_report(result)
    payload = json.dumps(findings_payload(result), indent=2) + "\n"
    out_dir.mkdir(parents=True, exist_ok=True)
    report_path = out_dir / "report.md"
    flags_path = out_dir / "flags.json"
    _refuse_output_file(report_path, source)
    _refuse_output_file(flags_path, source)
    report_path.write_text(report, encoding="utf-8")
    flags_path.write_text(payload, encoding="utf-8")
    return report_path, flags_path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Flag a fixture order line with a blank mã. "
            "Read-only. Does not invent a mã or a price."
        ),
    )
    parser.add_argument("--fixture", help="Fixture order JSON.")
    parser.add_argument("--held", help="Held policy JSON. Defaults to the repo held list.")
    parser.add_argument("--out", help="Directory for the report. Does not rewrite the fixture.")
    args = parser.parse_args(argv)
    if not args.fixture or not args.out:
        print(
            "Pass --fixture and --out. This check reads a fixture only. "
            "It does not invent a mã or a price.",
            flush=True,
        )
        return 2
    try:
        _refuse_remote(args.fixture)
        if args.held:
            _refuse_remote(args.held)
        fixture_path = Path(args.fixture)
        out_dir = Path(args.out)
        _refuse_out(out_dir, fixture_path)
        payload = json.loads(fixture_path.read_text(encoding="utf-8"))
        policy = load_held_policy(Path(args.held)) if args.held else None
        result = flag_fixture(payload, policy)
        report_path, flags_path = write_outputs(result, out_dir, source=fixture_path)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(str(error), flush=True)
        return 2
    print(report_path)
    print(flags_path)
    return 1 if result.flags else 0


def _clean_line(item: CleanLine) -> str:
    title = item.title if item.title is not None else "untitled"
    return f"- Line {item.line} {item.ma} — {title} — ${item.price_usd}"


def _flag_line(item: BlankFlag) -> str:
    _require_kind(item.kind)
    price = (
        "No price was on the line. No price was added."
        if item.price_usd is None
        else f"Price stays ${item.price_usd}."
    )
    return f"- Line {item.line} has a blank mã. {_blank_phrase(item)} {price} No mã was invented."


def _blank_phrase(item: BlankFlag) -> str:
    if item.blank == MISSING:
        return "The mã field is missing."
    if item.blank == NULL:
        return "The mã field is null."
    if item.blank == EMPTY:
        return "Stored mã is empty."
    if item.blank == WHITESPACE:
        return f"Stored mã is {item.stored_ma!r}."
    raise ValueError(f"unknown blank form {item.blank}")


def _omit_line(item: OmittedLine) -> str:
    if item.reason == NO_PRICE:
        return f"- Line {item.line} {item.ma} has no price. No price was added."
    if item.reason == HELD:
        return f"- Line {item.line} {item.ma} is held and stays off the order."
    if item.reason == NEVER_LIST:
        return f"- Line {item.line} {item.ma} is on the never-list and stays off the order."
    raise ValueError(f"unknown omit reason {item.reason}")


def _order_id(payload: dict[str, object]) -> str | None:
    if "orderId" not in payload:
        return None
    value = payload.get("orderId")
    if value is None:
        return None
    if not isinstance(value, str):
        raise ValueError("fixture order id must be a string")
    text = value.strip()
    return text or None


def _ma(item: dict[str, object]) -> tuple[str | None, str | None, str | None]:
    if "ma" not in item:
        return None, MISSING, None
    value = item.get("ma")
    if value is None:
        return None, NULL, None
    if not isinstance(value, str):
        raise ValueError("mã must be a string")
    if value.strip() == "":
        form = EMPTY if value == "" else WHITESPACE
        return None, form, value
    code = value.strip().upper()
    if _MA_CODE.fullmatch(code) is None:
        raise ValueError(f"fixture order line has an invalid mã {value!r}")
    return code, None, value


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
    if isinstance(value, bool) or isinstance(value, (list, dict)):
        raise ValueError("price must be a number")
    if isinstance(value, int):
        if value < 0:
            raise ValueError("price must be a non-negative number")
        return str(value)
    if isinstance(value, float):
        if not math.isfinite(value) or value < 0:
            raise ValueError("price must be a non-negative number")
        return format(Decimal(str(value)), "f")
    if isinstance(value, str):
        text = value.strip().replace("$", "").replace(",", "").strip()
        if _AMOUNT.fullmatch(text) is None:
            raise ValueError("price must be a number")
        try:
            amount = Decimal(text)
        except InvalidOperation as error:
            raise ValueError("price must be a number") from error
        if amount < 0:
            raise ValueError("price must be a non-negative number")
        return text
    raise ValueError("price must be a number")


def _reject_unknown(result: BlankResult) -> None:
    for item in result.flags:
        _require_kind(item.kind)
        _require_blank(item.blank)
    for item in result.omitted:
        _require_reason(item.reason)


def _require_kind(kind: str) -> None:
    if kind != BLANK_MA:
        raise ValueError(f"unknown finding kind {kind}")


def _require_blank(blank: str) -> None:
    if blank not in BLANK_FORMS:
        raise ValueError(f"unknown blank form {blank}")


def _require_reason(reason: str) -> None:
    if reason not in OMIT_REASONS:
        raise ValueError(f"unknown omit reason {reason}")


def _refuse_remote(path: str) -> None:
    lowered = path.strip().lower()
    if lowered.startswith(("http://", "https://", "blob:")):
        raise ValueError("fixture must be a local file")


def _refuse_out(path: Path, source: Path | None) -> None:
    resolved = _resolve(path)
    if source is not None and resolved == _resolve(source):
        raise ValueError("refusing to overwrite the fixture")
    if resolved == default_held_path().resolve() or resolved.name in _FORBIDDEN_NAMES:
        raise ValueError(f"refusing to write {resolved.name}")
    repo = Path(__file__).resolve().parents[1]
    try:
        relative = resolved.relative_to(repo)
    except ValueError:
        relative = None
    if relative is not None and relative.parts and relative.parts[0] in _FORBIDDEN_ROOTS:
        raise ValueError("refusing to write inside shop data, intake, or the sell catalog")


def _refuse_output_file(path: Path, source: Path | None) -> None:
    resolved = _resolve(path)
    if source is not None and resolved == _resolve(source):
        raise ValueError("refusing to overwrite the fixture")
    if resolved == default_held_path().resolve() or resolved.name in _FORBIDDEN_NAMES:
        raise ValueError(f"refusing to write {resolved.name}")


def _resolve(path: Path) -> Path:
    candidate = path if path.is_absolute() else Path.cwd() / path
    return candidate.resolve()


if __name__ == "__main__":
    raise SystemExit(main())
