"""Vietnamese caption lint on fixtures. No live reads and no held.json edits."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from caption_lint import (
    MISSING_DIACRITIC,
    MISSING_GIA,
    MISSING_MA,
    WORDS,
    fold_text,
    load_fixture,
    lint_captions,
    main,
    render_report,
    render_suggestions,
)

ROOT = Path(__file__).resolve().parents[2]
FIXTURE = Path(__file__).resolve().parent / "fixtures" / "caption_lint.json"
HELD = ROOT / "data" / "held.json"


def _by_id():
    captions = load_fixture(FIXTURE)
    result = lint_captions(captions)
    return captions, result


def test_fixture_flags_m_a09_and_ma_d06() -> None:
    _captions, result = _by_id()
    a09 = [item for item in result.findings if item.caption_id == "m-a09"]
    d06 = [item for item in result.findings if item.caption_id == "ma-d06"]
    assert [(item.kind, item.excerpt, item.suggestion) for item in a09] == [
        (MISSING_DIACRITIC, "M A09", "Mã A09"),
    ]
    assert [(item.kind, item.excerpt, item.suggestion) for item in d06] == [
        (MISSING_DIACRITIC, "Ma D06", "Mã D06"),
    ]


def test_fixture_flags_v01_and_v02_caption_text() -> None:
    _captions, result = _by_id()
    v01 = [item for item in result.findings if item.caption_id == "v01"]
    v02 = [item for item in result.findings if item.caption_id == "v02"]
    assert [(item.kind, item.excerpt, item.suggestion) for item in v01] == [
        (
            MISSING_DIACRITIC,
            "Chan vay midi acetate lai ren",
            "Chân váy midi acetate lai ren",
        ),
    ]
    assert [(item.kind, item.excerpt, item.suggestion) for item in v02] == [
        (
            MISSING_DIACRITIC,
            "Chan vay satin acetate dang duoi ca",
            "Chân váy satin acetate dáng đuôi cá",
        ),
    ]


def test_fixture_flags_missing_ma_line_and_missing_gia() -> None:
    _captions, result = _by_id()
    missing_ma = [item for item in result.findings if item.caption_id == "missing-ma"]
    missing_gia = [item for item in result.findings if item.caption_id == "missing-gia"]
    assert [item.kind for item in missing_ma] == [MISSING_MA]
    assert missing_ma[0].suggestion.startswith("Add a mã line")
    assert "$" not in missing_ma[0].suggestion
    assert [item.kind for item in missing_gia] == [MISSING_GIA]
    assert "Giá" in missing_gia[0].suggestion
    assert "$" not in missing_gia[0].suggestion


def test_catalog_captions_and_bare_ma_are_clean() -> None:
    _captions, result = _by_id()
    clean_ids = {item.caption_id for item in result.findings}
    assert "v01-catalog" not in clean_ids
    assert "v02-catalog" not in clean_ids
    assert "bare-ma" not in clean_ids


def test_ascii_gia_is_a_diacritic_suggestion() -> None:
    _captions, result = _by_id()
    gia = [item for item in result.findings if item.caption_id == "ascii-gia"]
    assert [(item.kind, item.excerpt, item.suggestion) for item in gia] == [
        (MISSING_DIACRITIC, "Gia", "Giá"),
    ]


def test_report_and_suggestion_list_cover_every_finding() -> None:
    _captions, result = _by_id()
    report = render_report(result)
    suggestions = render_suggestions(result)
    assert "Read-only" in report
    assert "No sign-in" in report
    assert "Missing diacritics" in report
    assert "Missing mã line" in report
    assert "Missing Giá" in report
    assert "M A09" in report
    assert "Ma D06" in report
    assert "Chan vay midi acetate lai ren" in report
    assert "Chan vay satin acetate dang duoi ca" in report
    assert "# Suggestion list" in suggestions
    assert "Nothing was posted." in suggestions
    for item in result.findings:
        assert item.caption_id in suggestions
        assert item.suggestion in suggestions


def test_lint_leaves_fixture_text_and_held_json_unchanged() -> None:
    before = HELD.read_bytes()
    raw = FIXTURE.read_text(encoding="utf-8")
    captions = load_fixture(FIXTURE)
    originals = [caption.text for caption in captions]
    lint_captions(captions)
    assert [caption.text for caption in captions] == originals
    assert FIXTURE.read_text(encoding="utf-8") == raw
    assert HELD.read_bytes() == before


def test_cli_writes_report_and_suggestions(tmp_path: Path) -> None:
    before = HELD.read_bytes()
    out = tmp_path / "caption-lint"
    completed = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "caption_lint.py"),
            "--fixture",
            str(FIXTURE),
            "--out",
            str(out),
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    assert completed.returncode == 1
    report = (out / "report.md").read_text(encoding="utf-8")
    suggestions = (out / "suggestions.md").read_text(encoding="utf-8")
    assert "Mã A09" in report
    assert "Mã D06" in report
    assert "Chân váy midi acetate lai ren" in suggestions
    assert "Chân váy satin acetate dáng đuôi cá" in suggestions
    assert "Add a mã line" in suggestions
    assert "Add a Giá line" in suggestions
    assert HELD.read_bytes() == before


def test_cli_without_fixture_does_not_write(tmp_path: Path) -> None:
    code = main(["--out", str(tmp_path / "unused")])
    assert code == 2
    assert not (tmp_path / "unused").exists()


def test_linter_source_stays_fixture_only() -> None:
    source = (ROOT / "scripts" / "caption_lint.py").read_text(encoding="utf-8").lower()
    for banned in ("urllib", "requests", "held.json", "facebook.com", "instagram.com"):
        assert banned not in source


def test_caption_words_do_not_share_a_fold() -> None:
    folded = [fold_text(word) for word in WORDS]
    assert len(folded) == len(set(folded))


def test_size_m_is_not_a_broken_ma_label() -> None:
    captions = load_fixture(FIXTURE)
    text = next(caption.text for caption in captions if caption.id == "m-a09")
    assert "Size S / M / L" in text
    result = lint_captions(captions)
    excerpts = [item.excerpt for item in result.findings if item.caption_id == "m-a09"]
    assert excerpts == ["M A09"]
    assert json.loads(FIXTURE.read_text(encoding="utf-8"))["captions"][0]["text"].startswith("M A09")
