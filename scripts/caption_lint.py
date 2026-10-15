"""Read-only Vietnamese caption linter.

Captions come from a fixture file. The linter writes a report and a
suggestion list. It does not sign in, and it does not post, edit, or
delete Facebook or Instagram content.
"""

from __future__ import annotations

import argparse
import json
import re
import unicodedata
from dataclasses import dataclass
from pathlib import Path

KIND_LETTERS = "AQVDKGBPHJSO"
CODE = rf"[{KIND_LETTERS}]\d{{2}}"
BROKEN_MA_LABEL = re.compile(
    rf"(?i)(?<!\S)(?P<label>Ma|M)[ \t]+(?P<code>{CODE})\b",
)
MA_LINE = re.compile(
    rf"(?im)^[ \t]*(?:mã[ \t]+{CODE}\b|(?:ma|m)[ \t]+{CODE}\b|{CODE}[ \t]*$)",
)
GIA_LINE = re.compile(r"(?iu)\bgiá\b")
ASCII_GIA = re.compile(r"(?iu)\bgia\b")
WORD = re.compile(r"[^\W\d_]+", re.UNICODE)

MISSING_DIACRITIC = "missing_diacritic"
MISSING_MA = "missing_ma"
MISSING_GIA = "missing_gia"

# Catalog lines and shop words that keep their marks. Longer phrases win.
PHRASES: tuple[str, ...] = (
    "Chân váy midi acetate lai ren",
    "Chân váy satin acetate dáng đuôi cá",
    "Chân váy đuôi cá satin",
    "Áo cổ V ren trắng",
    "Đầm ren đen",
)

WORDS: tuple[str, ...] = (
    "Mã",
    "Giá",
    "Áo",
    "Cổ",
    "Quần",
    "Váy",
    "Đầm",
    "Giày",
    "Túi",
    "Màu",
    "Chân",
    "Dáng",
    "Đuôi",
    "Cá",
    "Trắng",
    "Đen",
    "Hồng",
    "Đỏ",
    "Nâu",
    "Xám",
    "Bạc",
    "Vàng",
    "Tím",
    "Nhẹ",
    "Xỉu",
    "Cưng",
)


@dataclass(frozen=True)
class Caption:
    id: str
    text: str


@dataclass(frozen=True)
class Finding:
    caption_id: str
    kind: str
    excerpt: str
    suggestion: str
    start: int

    def as_json(self) -> dict[str, str | int]:
        return {
            "id": self.caption_id,
            "kind": self.kind,
            "excerpt": self.excerpt,
            "suggestion": self.suggestion,
            "start": self.start,
        }


@dataclass(frozen=True)
class LintResult:
    findings: tuple[Finding, ...]


def lint_captions(captions: list[Caption]) -> LintResult:
    """Return findings. Caption text is not rewritten."""
    findings: list[Finding] = []
    for caption in captions:
        findings.extend(_lint_one(caption))
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
    lines = [
        "# Vietnamese caption lint",
        "",
        "Read-only. No sign-in. No Facebook or Instagram post was created, edited, or deleted.",
        "",
        f"Findings: {len(result.findings)}",
        "",
    ]
    if not result.findings:
        lines.append("No findings.")
        lines.append("")
        return "\n".join(lines)
    for kind in (MISSING_DIACRITIC, MISSING_MA, MISSING_GIA):
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
    lines = [
        "# Suggestion list",
        "",
        "Draft wording only. Nothing was posted.",
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
        description="Lint Vietnamese captions from a fixture. Read-only.",
    )
    parser.add_argument("--fixture", help="Caption fixture JSON. Required. No live reads.")
    parser.add_argument("--out", help="Directory for the report and the suggestion list.")
    args = parser.parse_args(argv)
    if not args.fixture or not args.out:
        print(
            "Pass --fixture and --out. This linter does not read Facebook or Instagram and does not sign in.",
            flush=True,
        )
        return 2
    try:
        captions = load_fixture(Path(args.fixture))
        result = lint_captions(captions)
        report_path, suggestions_path = write_outputs(result, Path(args.out))
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(str(error), flush=True)
        return 2
    print(report_path)
    print(suggestions_path)
    return 1 if result.findings else 0


def _lint_one(caption: Caption) -> list[Finding]:
    text = unicodedata.normalize("NFC", caption.text)
    occupied: list[tuple[int, int]] = []
    findings: list[Finding] = []

    for match in BROKEN_MA_LABEL.finditer(text):
        start, end = match.span()
        if _overlaps(occupied, start, end):
            continue
        code = match.group("code").upper()
        excerpt = text[start:end]
        findings.append(
            Finding(
                caption.id,
                MISSING_DIACRITIC,
                excerpt,
                f"Mã {code}",
                start,
            )
        )
        occupied.append((start, end))

    if len(fold_text(text)) == len(text):
        for phrase in sorted(PHRASES, key=len, reverse=True):
            for start, end in _phrase_spans(text, phrase):
                if _overlaps(occupied, start, end):
                    continue
                excerpt = text[start:end]
                if _marks_equivalent(excerpt, phrase):
                    occupied.append((start, end))
                    continue
                if not _plain_latin(excerpt) or fold_text(excerpt) != fold_text(phrase):
                    continue
                findings.append(Finding(caption.id, MISSING_DIACRITIC, excerpt, phrase, start))
                occupied.append((start, end))

    folded_words = {fold_text(word): word for word in WORDS}
    for match in WORD.finditer(text):
        start, end = match.span()
        if _overlaps(occupied, start, end):
            continue
        token = match.group(0)
        canonical = folded_words.get(fold_text(token))
        if canonical is None or not _plain_latin(token):
            continue
        if len(token) != len(canonical) or fold_text(token) != fold_text(canonical):
            continue
        findings.append(
            Finding(
                caption.id,
                MISSING_DIACRITIC,
                token,
                _match_case(token, canonical),
                start,
            )
        )
        occupied.append((start, end))

    if MA_LINE.search(text) is None:
        findings.append(
            Finding(
                caption.id,
                MISSING_MA,
                "",
                "Add a mã line written as Mã plus the code.",
                len(text) + 1,
            )
        )
    if GIA_LINE.search(text) is None and ASCII_GIA.search(text) is None:
        findings.append(
            Finding(
                caption.id,
                MISSING_GIA,
                "",
                "Add a Giá line. Do not invent a price.",
                len(text) + 2,
            )
        )

    findings.sort(key=lambda item: (item.start, item.kind))
    return findings


def _phrase_spans(text: str, phrase: str) -> list[tuple[int, int]]:
    folded = fold_text(text)
    needle = fold_text(phrase)
    if needle == "":
        return []
    spans: list[tuple[int, int]] = []
    start = 0
    while True:
        index = folded.find(needle, start)
        if index < 0:
            break
        end = index + len(needle)
        if _bounded(folded, index, end):
            spans.append((index, end))
        start = index + 1
    return spans


def _bounded(folded: str, start: int, end: int) -> bool:
    before = start == 0 or not folded[start - 1].isalnum()
    after = end == len(folded) or not folded[end].isalnum()
    return before and after


def _overlaps(spans: list[tuple[int, int]], start: int, end: int) -> bool:
    return any(start < right and end > left for left, right in spans)


def fold_text(text: str) -> str:
    return "".join(_fold_char(char) for char in unicodedata.normalize("NFC", text))


def _fold_char(char: str) -> str:
    if char in ("đ", "Đ"):
        base = "d"
    else:
        decomposed = unicodedata.normalize("NFD", char)
        base = "".join(piece for piece in decomposed if unicodedata.category(piece) != "Mn")
    if len(base) != 1:
        return char.casefold()
    return base.casefold()


def _mark_signature(char: str) -> str:
    if char in ("đ", "Đ"):
        return "d-stroke"
    decomposed = unicodedata.normalize("NFD", char)
    return "".join(piece for piece in decomposed if unicodedata.category(piece) == "Mn")


def _plain_latin(text: str) -> bool:
    return not any(_mark_signature(char) for char in text)


def _marks_equivalent(source: str, canonical: str) -> bool:
    if len(source) != len(canonical):
        return False
    for src, can in zip(source, canonical):
        if _fold_char(src) != _fold_char(can):
            return False
        if _mark_signature(src) != _mark_signature(can):
            return False
    return True


def _match_case(token: str, canonical: str) -> str:
    if token.isupper():
        return canonical.upper()
    if token[:1].isupper():
        return canonical[:1].upper() + canonical[1:]
    return canonical[:1].lower() + canonical[1:]


def _kind_heading(kind: str) -> str:
    if kind == MISSING_DIACRITIC:
        return "Missing diacritics"
    if kind == MISSING_MA:
        return "Missing mã line"
    if kind == MISSING_GIA:
        return "Missing Giá"
    raise ValueError(f"unknown finding kind {kind}")


def _report_line(item: Finding) -> str:
    if item.kind == MISSING_DIACRITIC:
        return f"`{_one_line(item.excerpt)}` — replace with `{item.suggestion}`"
    if item.kind == MISSING_MA:
        return item.suggestion
    if item.kind == MISSING_GIA:
        return item.suggestion
    raise ValueError(f"unknown finding kind {item.kind}")


def _suggestion_line(item: Finding) -> str:
    if item.kind == MISSING_DIACRITIC:
        return f"replace `{_one_line(item.excerpt)}` with `{item.suggestion}`"
    if item.kind == MISSING_MA:
        return item.suggestion
    if item.kind == MISSING_GIA:
        return item.suggestion
    raise ValueError(f"unknown finding kind {item.kind}")


def _one_line(text: str) -> str:
    return " ".join(text.split())


if __name__ == "__main__":
    raise SystemExit(main())
