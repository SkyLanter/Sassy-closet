"""Flag messy USD amounts on caption Giá lines.

Captions come from a fixture file. A tidy display is listed in the report.
Caption text is not rewritten, no price is changed, and nothing is posted.
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from pathlib import Path

TRAILING_DOLLAR = "trailing_dollar"
SPACED_DOLLAR = "spaced_dollar"
MISSING_DOLLAR = "missing_dollar"
KINDS = (TRAILING_DOLLAR, SPACED_DOLLAR, MISSING_DOLLAR)

# Giá or Gia at the start of a line, then the rest of that line.
_GIA_LINE = re.compile(r"(?iu)^[ \t]*(?:giá|gia)\b[ \t]*:?[ \t]*(?P<rest>.*)$")
_NOT_INSIDE = r"(?<![A-Za-z\d.])"
# Yen amounts are skipped. Dollar shapes cover $25, $ 25, 25$, and $25$.
# A remaining number has no dollar sign. Digits inside a mã such as A07 are left alone.
_TOKEN = re.compile(
    rf"(?P<yen>¥[ \t]*\d+(?:\.\d+)?|{_NOT_INSIDE}\d+(?:\.\d+)?[ \t]*¥)"
    rf"|(?P<dollar>\$(?:[ \t]+\d+(?:\.\d+)?\$?|\d+(?:\.\d+)?\$?)"
    rf"|{_NOT_INSIDE}\d+(?:\.\d+)?[ \t]*\$)"
    rf"|(?P<bare>{_NOT_INSIDE}\d+(?:\.\d+)?)"
)
_AMOUNT = re.compile(r"\d+(?:\.\d+)?")
_CLEAN_DOLLAR = re.compile(r"\$\d+(?:\.\d+)?")
_SPACED_DOLLAR = re.compile(r"\$[ \t]+\d+(?:\.\d+)?\$?")
_ATTACHED_TRAILING = re.compile(r"\$\d+(?:\.\d+)?\$")
_TRAILING_DOLLAR = re.compile(r"\d+(?:\.\d+)?[ \t]*\$")


@dataclass(frozen=True)
class Caption:
    id: str
    text: str


@dataclass(frozen=True)
class Finding:
    caption_id: str
    kind: str
    excerpt: str
    amount: str
    suggestion: str
    line: int

    def as_json(self) -> dict[str, str | int]:
        return {
            "id": self.caption_id,
            "kind": self.kind,
            "excerpt": self.excerpt,
            "amount": self.amount,
            "suggestion": self.suggestion,
            "line": self.line,
        }


@dataclass(frozen=True)
class LintResult:
    findings: tuple[Finding, ...]


def flag_gia_prices(captions: list[Caption]) -> LintResult:
    """Return findings. Caption text is not rewritten and no price is changed."""
    findings: list[Finding] = []
    for caption in captions:
        findings.extend(_flag_one(caption))
    return LintResult(tuple(findings))


def load_fixture(path: Path) -> list[Caption]:
    data = json.loads(path.read_text(encoding="utf-8"))
    rows = data.get("captions") if isinstance(data, dict) else None
    if not isinstance(rows, list):
        raise ValueError("fixture captions must be a list")
    captions: list[Caption] = []
    for row in rows:
        if not isinstance(row, dict):
            raise ValueError("fixture caption must be an object")
        caption_id = row.get("id")
        text = row.get("text")
        if not isinstance(caption_id, str) or caption_id.strip() == "":
            raise ValueError("fixture caption needs an id")
        if not isinstance(text, str):
            raise ValueError("fixture caption needs text")
        captions.append(Caption(caption_id.strip(), text))
    return captions


def render_report(result: LintResult) -> str:
    _reject_unknown(result)
    lines = [
        "# Giá price format",
        "",
        "Read-only. Captions came from a fixture. No caption was rewritten. "
        "No price was changed. No Facebook or Instagram post was created, edited, or deleted.",
        "",
        f"Findings: {len(result.findings)}",
        "",
    ]
    if not result.findings:
        lines.append("No findings.")
        lines.append("")
        return "\n".join(lines)
    for kind in KINDS:
        group = [item for item in result.findings if item.kind == kind]
        if not group:
            continue
        lines.append(f"## {_kind_heading(kind)}")
        lines.append("")
        for item in group:
            lines.append(f"- {item.caption_id}: {_report_line(item)}")
        lines.append("")
    return "\n".join(lines)


def render_suggestions(result: LintResult) -> str:
    _reject_unknown(result)
    lines = [
        "# Suggestion list",
        "",
        "Draft display only. No caption was rewritten. No price was changed. Nothing was posted.",
        "",
    ]
    if not result.findings:
        lines.append("No suggestions.")
        lines.append("")
        return "\n".join(lines)
    for index, item in enumerate(result.findings, start=1):
        lines.append(f"{index}. {item.caption_id}: {_suggestion_line(item)}")
    lines.append("")
    return "\n".join(lines)


def write_outputs(result: LintResult, out_dir: Path) -> tuple[Path, Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    report_path = out_dir / "report.md"
    suggestions_path = out_dir / "suggestions.md"
    report_path.write_text(render_report(result), encoding="utf-8")
    suggestions_path.write_text(render_suggestions(result), encoding="utf-8")
    return report_path, suggestions_path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Flag messy Giá price formats in a caption fixture. Read-only.",
    )
    parser.add_argument("--fixture", help="Caption fixture JSON. Required. No live reads.")
    parser.add_argument("--out", help="Directory for the report and the suggestion list.")
    args = parser.parse_args(argv)
    if not args.fixture or not args.out:
        print(
            "Pass --fixture and --out. This check reads a fixture only. "
            "It does not rewrite captions, change a price, sign in, or post.",
            flush=True,
        )
        return 2
    try:
        captions = load_fixture(Path(args.fixture))
        result = flag_gia_prices(captions)
        report_path, suggestions_path = write_outputs(result, Path(args.out))
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(str(error), flush=True)
        return 2
    print(report_path)
    print(suggestions_path)
    return 1 if result.findings else 0


def _flag_one(caption: Caption) -> list[Finding]:
    findings: list[Finding] = []
    for line_no, line in enumerate(caption.text.splitlines(), start=1):
        match = _GIA_LINE.match(line)
        if match is None:
            continue
        findings.extend(_flag_rest(caption.id, line_no, match.group("rest")))
    return findings


def _flag_rest(caption_id: str, line_no: int, rest: str) -> list[Finding]:
    findings: list[Finding] = []
    for match in _TOKEN.finditer(rest):
        if match.group("yen"):
            continue
        excerpt = match.group(0)
        if match.group("bare"):
            kind = MISSING_DOLLAR
        else:
            kind = _dollar_kind(excerpt)
            if kind is None:
                continue
        amount = _amount(excerpt)
        findings.append(
            Finding(
                caption_id=caption_id,
                kind=kind,
                excerpt=excerpt,
                amount=amount,
                suggestion=f"${amount}",
                line=line_no,
            )
        )
    return findings


def _dollar_kind(token: str) -> str | None:
    if _CLEAN_DOLLAR.fullmatch(token):
        return None
    if _SPACED_DOLLAR.fullmatch(token):
        return SPACED_DOLLAR
    if _ATTACHED_TRAILING.fullmatch(token):
        return TRAILING_DOLLAR
    if _TRAILING_DOLLAR.fullmatch(token):
        return TRAILING_DOLLAR
    raise ValueError(f"unrecognized dollar token: {token}")


def _amount(token: str) -> str:
    match = _AMOUNT.search(token)
    if match is None:
        raise ValueError(f"price token has no amount: {token}")
    return match.group(0)


def _reject_unknown(result: LintResult) -> None:
    for item in result.findings:
        if item.kind not in KINDS:
            raise ValueError(f"unknown finding kind {item.kind}")


def _kind_heading(kind: str) -> str:
    if kind == TRAILING_DOLLAR:
        return "Dollar sign after the amount"
    if kind == SPACED_DOLLAR:
        return "Space after the dollar sign"
    if kind == MISSING_DOLLAR:
        return "Missing dollar sign"
    raise ValueError(f"unknown finding kind {kind}")


def _report_line(item: Finding) -> str:
    if item.kind not in KINDS:
        raise ValueError(f"unknown finding kind {item.kind}")
    return f"line {item.line} `{item.excerpt}` → {item.suggestion}"


def _suggestion_line(item: Finding) -> str:
    if item.kind not in KINDS:
        raise ValueError(f"unknown finding kind {item.kind}")
    return (
        f"`{item.excerpt}` is messy. Display as `{item.suggestion}`. "
        f"Amount stays {item.amount}."
    )


if __name__ == "__main__":
    raise SystemExit(main())
