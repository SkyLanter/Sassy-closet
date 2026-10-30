"""Flag fixture captions whose Giá dollars differ from that mã's catalog price.

Captions and catalog prices come from a fixture file. The report names both
amounts. Caption text is not rewritten, no price is changed, and nothing is posted.
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path
from held_policy import norm_ma

MISMATCH = "mismatch"
KINDS = (MISMATCH,)

# Giá or Gia at the start of a line, then the rest of that line.
_GIA_LINE = re.compile(r"(?iu)^[ \t]*(?:giá|gia)\b[ \t]*:?[ \t]*(?P<rest>.*)$")
# "Mã A07", "Ma D06", and "M A09" on their own line.
_MA_LABEL = re.compile(r"(?iu)(?:^|\n)[ \t]*(?:mã|ma|m)[ \t]+([A-Za-z]\d{2})\b")
# A line that is only the mã.
_MA_BARE = re.compile(r"(?iu)(?:^|\n)[ \t]*([A-Za-z]\d{2})[ \t]*(?:$|\n)")
_MA_CODE = re.compile(r"[A-Z]\d{2}")
_YEN = re.compile(r"¥[ \t]*\d+(?:\.\d+)?|(?<![A-Za-z\d.$])\d+(?:\.\d+)?[ \t]*¥")
_DOLLAR = re.compile(
    r"\$(?:[ \t]*\d+(?:\.\d+)?)"
    r"|(?<![A-Za-z\d.])\d+(?:\.\d+)?[ \t]*\$"
    r"|(?<![A-Za-z\d.])\d+(?:\.\d+)?[ \t]*USD\b",
    re.IGNORECASE,
)
_BARE_AMOUNT = re.compile(r"[ \t]*(\d+(?:\.\d+)?)[ \t]*")
_AMOUNT = re.compile(r"\d+(?:\.\d+)?")
_MONEY_TEXT = re.compile(r"\d+(?:\.\d+)?")


@dataclass(frozen=True)
class Caption:
    id: str
    text: str


@dataclass(frozen=True)
class CatalogPrice:
    ma: str
    amount: Decimal
    text: str


@dataclass(frozen=True)
class Fixture:
    captions: tuple[Caption, ...]
    catalog: dict[str, CatalogPrice]


@dataclass(frozen=True)
class Finding:
    caption_id: str
    ma: str
    kind: str
    excerpt: str
    caption_usd: str
    catalog_usd: str
    line: int

    def as_json(self) -> dict[str, str | int]:
        _require_kind(self.kind)
        return {
            "id": self.caption_id,
            "ma": self.ma,
            "kind": self.kind,
            "excerpt": self.excerpt,
            "captionUsd": self.caption_usd,
            "catalogUsd": self.catalog_usd,
            "line": self.line,
        }


@dataclass(frozen=True)
class CompareResult:
    findings: tuple[Finding, ...]


def compare_prices(captions: list[Caption], catalog: dict[str, CatalogPrice]) -> CompareResult:
    """Return mismatch findings. Caption text and catalog amounts stay as passed in."""
    findings: list[Finding] = []
    for caption in captions:
        code = _caption_ma(caption.text)
        if code is None:
            continue
        listed = catalog.get(code)
        if listed is None:
            continue
        findings.extend(_flag_caption(caption, listed))
    return CompareResult(tuple(findings))


def load_fixture(path: Path) -> Fixture:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("fixture must be a JSON object")
    return Fixture(
        captions=_captions_from_json(data.get("captions")),
        catalog=_catalog_from_json(data.get("catalog")),
    )


def render_report(result: CompareResult) -> str:
    _reject_unknown(result)
    lines = [
        "# Caption Giá vs catalog",
        "",
        "Read-only. Captions and catalog prices came from a fixture. "
        "No caption was rewritten. No price was changed. "
        "No Facebook or Instagram post was created, edited, or deleted.",
        "",
        f"Findings: {len(result.findings)}",
        "",
    ]
    if not result.findings:
        lines.append("No findings.")
        lines.append("")
        return "\n".join(lines)
    lines.append(f"## {_heading(MISMATCH)}")
    lines.append("")
    for item in result.findings:
        lines.append(f"- {item.caption_id}: {_report_line(item)}")
    lines.append("")
    return "\n".join(lines)


def findings_payload(result: CompareResult) -> dict[str, list[dict[str, str | int]]]:
    _reject_unknown(result)
    return {"findings": [item.as_json() for item in result.findings]}


def write_outputs(result: CompareResult, out_dir: Path) -> tuple[Path, Path]:
    report = render_report(result)
    payload = json.dumps(findings_payload(result), indent=2) + "\n"
    out_dir.mkdir(parents=True, exist_ok=True)
    report_path = out_dir / "report.md"
    findings_path = out_dir / "findings.json"
    report_path.write_text(report, encoding="utf-8")
    findings_path.write_text(payload, encoding="utf-8")
    return report_path, findings_path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Flag fixture captions whose Giá dollars differ from that mã's catalog price. "
            "Read-only."
        ),
    )
    parser.add_argument("--fixture", help="Fixture JSON with captions and catalog prices. Required.")
    parser.add_argument("--out", help="Directory for the report. Required.")
    args = parser.parse_args(argv)
    if not args.fixture or not args.out:
        print(
            "Pass --fixture and --out. This check reads a fixture only. "
            "It does not rewrite captions, change a price, sign in, or post.",
            flush=True,
        )
        return 2
    try:
        fixture = load_fixture(Path(args.fixture))
        result = compare_prices(list(fixture.captions), fixture.catalog)
        report_path, findings_path = write_outputs(result, Path(args.out))
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(str(error), flush=True)
        return 2
    print(report_path)
    print(findings_path)
    return 1 if result.findings else 0


def _flag_caption(caption: Caption, listed: CatalogPrice) -> list[Finding]:
    findings: list[Finding] = []
    for line_no, line in enumerate(caption.text.splitlines(), start=1):
        match = _GIA_LINE.match(line)
        if match is None:
            continue
        for excerpt, amount, digits in _dollar_amounts(match.group("rest")):
            if amount == listed.amount:
                continue
            findings.append(
                Finding(
                    caption_id=caption.id,
                    ma=listed.ma,
                    kind=MISMATCH,
                    excerpt=excerpt,
                    caption_usd=digits,
                    catalog_usd=listed.text,
                    line=line_no,
                )
            )
    return findings


def _dollar_amounts(rest: str) -> list[tuple[str, Decimal, str]]:
    without_yen = _YEN.sub(" ", rest)
    marked = list(_DOLLAR.finditer(without_yen))
    if marked:
        return [_amount_from_excerpt(match.group(0)) for match in marked]
    bare = _BARE_AMOUNT.fullmatch(without_yen)
    if bare is None:
        return []
    return [_amount_from_excerpt(bare.group(1))]


def _amount_from_excerpt(excerpt: str) -> tuple[str, Decimal, str]:
    match = _AMOUNT.search(excerpt)
    if match is None:
        raise ValueError(f"price token has no amount: {excerpt}")
    digits = match.group(0)
    return excerpt, Decimal(digits), digits


def _caption_ma(text: str) -> str | None:
    labeled = _MA_LABEL.search(text)
    if labeled:
        return labeled.group(1).upper()
    bare = _MA_BARE.search(text)
    if bare:
        return bare.group(1).upper()
    return None


def _captions_from_json(value: object) -> tuple[Caption, ...]:
    if not isinstance(value, list):
        raise ValueError("fixture captions must be a list")
    captions: list[Caption] = []
    for row in value:
        if not isinstance(row, dict):
            raise ValueError("fixture caption must be an object")
        caption_id = row.get("id")
        text = row.get("text")
        if not isinstance(caption_id, str) or caption_id.strip() == "":
            raise ValueError("fixture caption needs an id")
        if not isinstance(text, str):
            raise ValueError("fixture caption needs text")
        captions.append(Caption(caption_id.strip(), text))
    return tuple(captions)


def _catalog_from_json(value: object) -> dict[str, CatalogPrice]:
    if not isinstance(value, list):
        raise ValueError("fixture catalog must be a list")
    catalog: dict[str, CatalogPrice] = {}
    for row in value:
        if not isinstance(row, dict):
            raise ValueError("fixture catalog row must be an object")
        raw_ma = row.get("ma")
        if not isinstance(raw_ma, str):
            raise ValueError("fixture catalog row needs a mã")
        code = norm_ma(raw_ma)
        if _MA_CODE.fullmatch(code) is None:
            raise ValueError(f"fixture catalog mã is invalid: {raw_ma!r}")
        if code in catalog:
            raise ValueError(f"fixture catalog lists {code} twice")
        amount, text = _catalog_amount(row.get("price_usd"))
        catalog[code] = CatalogPrice(code, amount, text)
    return catalog


def _catalog_amount(value: object) -> tuple[Decimal, str]:
    if isinstance(value, bool) or not isinstance(value, (int, str)):
        raise ValueError("catalog price_usd must be a string or whole number")
    text = str(value).strip() if isinstance(value, int) else value.strip()
    if _MONEY_TEXT.fullmatch(text) is None:
        raise ValueError("catalog price_usd is not a dollar amount")
    return Decimal(text), text


def _reject_unknown(result: CompareResult) -> None:
    for item in result.findings:
        _require_kind(item.kind)


def _require_kind(kind: str) -> None:
    if kind not in KINDS:
        raise ValueError(f"unknown finding kind {kind}")


def _heading(kind: str) -> str:
    if kind == MISMATCH:
        return "Giá dollars differ from the catalog price"
    raise ValueError(f"unknown finding kind {kind}")


def _report_line(item: Finding) -> str:
    _require_kind(item.kind)
    return (
        f"Mã {item.ma} line {item.line} caption `{item.excerpt}` "
        f"catalog `${item.catalog_usd}`. Neither amount was changed."
    )


if __name__ == "__main__":
    raise SystemExit(main())
