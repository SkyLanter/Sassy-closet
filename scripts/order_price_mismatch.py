"""Flag a fixture order line whose price differs from that mã's catalog price.

The order and the catalog both come from one fixture file. The report names
both amounts. Neither price is changed, and the fixture file is not rewritten.
"""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path

MISMATCH = "mismatch"
NO_PRICE = "no-price"
NO_CATALOG = "no-catalog"
KINDS = (MISMATCH,)
OMIT_REASONS = (NO_PRICE, NO_CATALOG)

_MA_CODE = re.compile(r"^[A-Z][0-9]{2}$")
_AMOUNT = re.compile(r"\d+(?:\.\d+)?")
_FORBIDDEN_NAMES = frozenset(
    {
        "submissions.json",
        "catalog.v1.json",
        "orders.json",
    }
)
_FORBIDDEN_ROOTS = frozenset({"data", "sassy-closet", "sassy-closet-shop", "excel-kit"})


@dataclass(frozen=True)
class CatalogPrice:
    ma: str
    amount: Decimal
    text: str


@dataclass(frozen=True)
class Finding:
    ma: str
    kind: str
    order_usd: str
    catalog_usd: str

    def as_json(self) -> dict[str, str]:
        _require_kind(self.kind)
        return {
            "ma": self.ma,
            "kind": self.kind,
            "orderUsd": self.order_usd,
            "catalogUsd": self.catalog_usd,
        }


@dataclass(frozen=True)
class OmittedLine:
    ma: str
    reason: str

    def as_json(self) -> dict[str, str]:
        _require_reason(self.reason)
        return {"ma": self.ma, "reason": self.reason}


@dataclass(frozen=True)
class CompareResult:
    findings: tuple[Finding, ...]
    omitted: tuple[OmittedLine, ...]


def flag_fixture(payload: object) -> CompareResult:
    """Return price mismatches. Leave every order price and catalog price as passed in."""
    if not isinstance(payload, dict):
        raise ValueError("fixture must be a JSON object")
    catalog = _catalog_from_json(payload.get("catalog"))
    raw_lines = payload.get("lines")
    if not isinstance(raw_lines, list):
        raise ValueError("fixture lines must be a list")
    findings: list[Finding] = []
    omitted: list[OmittedLine] = []
    for item in raw_lines:
        if not isinstance(item, dict):
            raise ValueError("fixture order line must be an object")
        code = _ma(item.get("ma"))
        parsed = _line_price(item)
        if parsed is None:
            omitted.append(OmittedLine(code, NO_PRICE))
            continue
        amount, text = parsed
        listed = catalog.get(code)
        if listed is None:
            omitted.append(OmittedLine(code, NO_CATALOG))
            continue
        if amount == listed.amount:
            continue
        findings.append(Finding(code, MISMATCH, text, listed.text))
    return CompareResult(tuple(findings), tuple(omitted))


def render_report(result: CompareResult) -> str:
    _reject_unknown(result)
    lines = [
        "# Order line vs catalog price",
        "",
        "Read-only. Each order line is compared with that mã's fixture catalog price. "
        "Neither price was changed. The fixture file was not rewritten.",
        "",
        f"Flags: {len(result.findings)}",
        "",
    ]
    if result.findings:
        lines.append("## Price differs from the catalog")
        lines.append("")
        lines.extend(f"- {_finding_line(item)}" for item in result.findings)
        lines.append("")
    else:
        lines.append("No flags.")
        lines.append("")
    lines.append("## Left uncompared")
    lines.append("")
    if result.omitted:
        lines.extend(_omit_line(item) for item in result.omitted)
    else:
        lines.append("None.")
    lines.append("")
    return "\n".join(lines)


def findings_payload(result: CompareResult) -> dict[str, list[dict[str, str]]]:
    _reject_unknown(result)
    return {
        "flags": [item.as_json() for item in result.findings],
        "omitted": [item.as_json() for item in result.omitted],
    }


def write_outputs(result: CompareResult, out_dir: Path, *, source: Path | None = None) -> tuple[Path, Path]:
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
            "Flag a fixture order line whose price differs from that mã's fixture catalog price. "
            "Read-only."
        ),
    )
    parser.add_argument("--fixture", help="Fixture JSON with catalog prices and order lines.")
    parser.add_argument("--out", help="Directory for the report. Does not rewrite the fixture.")
    args = parser.parse_args(argv)
    if not args.fixture or not args.out:
        print(
            "Pass --fixture and --out. This check reads a fixture only. "
            "It does not change an order price or a catalog price.",
            flush=True,
        )
        return 2
    try:
        _refuse_remote(args.fixture)
        fixture_path = Path(args.fixture)
        out_dir = Path(args.out)
        _refuse_out(out_dir, fixture_path)
        payload = json.loads(fixture_path.read_text(encoding="utf-8"))
        result = flag_fixture(payload)
        report_path, flags_path = write_outputs(result, out_dir, source=fixture_path)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(str(error), flush=True)
        return 2
    print(report_path)
    print(flags_path)
    return 1 if result.findings else 0


def _finding_line(item: Finding) -> str:
    _require_kind(item.kind)
    return (
        f"Mã {item.ma} order `${item.order_usd}` catalog `${item.catalog_usd}`. "
        "Neither price was changed."
    )


def _omit_line(item: OmittedLine) -> str:
    if item.reason == NO_PRICE:
        return f"- {item.ma} has no order price. No price was added."
    if item.reason == NO_CATALOG:
        return f"- {item.ma} has no catalog price. No price was added."
    raise ValueError(f"unknown omit reason {item.reason}")


def _catalog_from_json(value: object) -> dict[str, CatalogPrice]:
    if not isinstance(value, list):
        raise ValueError("fixture catalog must be a list")
    catalog: dict[str, CatalogPrice] = {}
    for row in value:
        if not isinstance(row, dict):
            raise ValueError("fixture catalog row must be an object")
        code = _ma(row.get("ma"))
        if code in catalog:
            raise ValueError(f"fixture catalog lists {code} twice")
        if "priceUsd" not in row:
            raise ValueError(f"fixture catalog row {code} needs priceUsd")
        parsed = _price(row.get("priceUsd"), required=True)
        if parsed is None:
            raise ValueError(f"fixture catalog row {code} needs priceUsd")
        amount, text = parsed
        catalog[code] = CatalogPrice(code, amount, text)
    return catalog


def _line_price(item: dict[str, object]) -> tuple[Decimal, str] | None:
    if "priceUsd" not in item:
        return None
    return _price(item.get("priceUsd"), required=False)


def _price(value: object, *, required: bool) -> tuple[Decimal, str] | None:
    if value is None:
        if required:
            raise ValueError("price must be a number")
        return None
    if isinstance(value, bool) or isinstance(value, (list, dict)):
        raise ValueError("price must be a number")
    if isinstance(value, int):
        if value < 0:
            raise ValueError("price must be a non-negative number")
        text = str(value)
        return Decimal(text), text
    if isinstance(value, float):
        if not math.isfinite(value) or value < 0:
            raise ValueError("price must be a non-negative number")
        text = format(Decimal(str(value)), "f")
        return Decimal(text), text
    if isinstance(value, str):
        raw = value.strip()
        if raw == "":
            if required:
                raise ValueError("price must be a number")
            return None
        text = raw.replace("$", "").replace(",", "").strip()
        if _AMOUNT.fullmatch(text) is None:
            raise ValueError("price must be a number")
        amount = Decimal(text)
        if amount < 0:
            raise ValueError("price must be a non-negative number")
        return amount, text
    raise ValueError("price must be a number")


def _ma(value: object) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError("fixture row needs a mã")
    code = value.strip().upper()
    if _MA_CODE.fullmatch(code) is None:
        raise ValueError(f"fixture mã is invalid: {value!r}")
    return code


def _reject_unknown(result: CompareResult) -> None:
    for item in result.findings:
        _require_kind(item.kind)
    for item in result.omitted:
        _require_reason(item.reason)


def _require_kind(kind: str) -> None:
    if kind not in KINDS:
        raise ValueError(f"unknown finding kind {kind}")


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
    if resolved.name in _FORBIDDEN_NAMES:
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
    if resolved.name in _FORBIDDEN_NAMES:
        raise ValueError(f"refusing to write {resolved.name}")


def _resolve(path: Path) -> Path:
    candidate = path if path.is_absolute() else Path.cwd() / path
    return candidate.resolve()


if __name__ == "__main__":
    raise SystemExit(main())
