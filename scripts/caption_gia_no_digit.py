"""Flag fixture Giá lines that contain no digit.

A Giá line starts with Giá or Gia. "Giá: Inbox" is flagged. "Giá $25" is quiet.
Caption text is not rewritten, no price is changed, and nothing is posted.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path

GIA_NO_DIGIT = "gia_no_digit"
KINDS = (GIA_NO_DIGIT,)
_GIA_WORDS = frozenset({"giá", "gia"})


@dataclass(frozen=True)
class Caption:
    id: str
    text: str


@dataclass(frozen=True)
class Finding:
    caption_id: str
    kind: str
    line: int
    excerpt: str

    def as_json(self) -> dict[str, str | int]:
        return {
            "id": self.caption_id,
            "kind": self.kind,
            "line": self.line,
            "excerpt": self.excerpt,
        }


@dataclass(frozen=True)
class LintResult:
    findings: tuple[Finding, ...]


def flag_gia_no_digit(captions: list[Caption]) -> LintResult:
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
        "# Giá line with no digit",
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
    lines.append(f"## {_kind_heading(GIA_NO_DIGIT)}")
    lines.append("")
    for item in result.findings:
        lines.append(f"- {item.caption_id}: {_report_line(item)}")
    lines.append("")
    return "\n".join(lines)


def write_outputs(result: LintResult, out_dir: Path) -> Path:
    report = render_report(result)
    out_dir.mkdir(parents=True, exist_ok=True)
    report_path = out_dir / "report.md"
    report_path.write_text(report, encoding="utf-8")
    return report_path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Flag fixture Giá lines that contain no digit. Read-only.",
    )
    parser.add_argument("--fixture", help="Caption fixture JSON. Required. No live reads.")
    parser.add_argument("--out", help="Directory for the report.")
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
        result = flag_gia_no_digit(captions)
        report_path = write_outputs(result, Path(args.out))
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(str(error), flush=True)
        return 2
    print(report_path)
    return 1 if result.findings else 0


def _flag_one(caption: Caption) -> list[Finding]:
    findings: list[Finding] = []
    for line_no, line in enumerate(caption.text.splitlines(), start=1):
        if _is_gia_line(line) and not _has_digit(line):
            findings.append(
                Finding(
                    caption_id=caption.id,
                    kind=GIA_NO_DIGIT,
                    line=line_no,
                    excerpt=line,
                )
            )
    return findings


def _is_gia_line(line: str) -> bool:
    stripped = line.lstrip(" \t")
    if stripped == "":
        return False
    token = stripped.split(None, 1)[0]
    head = token.split(":", 1)[0]
    return head.casefold() in _GIA_WORDS


def _has_digit(line: str) -> bool:
    return any(character.isdecimal() for character in line)


def _reject_unknown(result: LintResult) -> None:
    for item in result.findings:
        if item.kind not in KINDS:
            raise ValueError(f"unknown finding kind {item.kind}")
        if item.line < 1 or item.excerpt == "":
            raise ValueError("a no-digit finding needs the Giá line")


def _kind_heading(kind: str) -> str:
    if kind == GIA_NO_DIGIT:
        return "Giá line with no digit"
    raise ValueError(f"unknown finding kind {kind}")


def _report_line(item: Finding) -> str:
    if item.kind not in KINDS:
        raise ValueError(f"unknown finding kind {item.kind}")
    return f"line {item.line} `{item.excerpt}`"


if __name__ == "__main__":
    raise SystemExit(main())
