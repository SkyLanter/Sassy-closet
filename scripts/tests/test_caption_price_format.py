"""Giá price-format flags from fixtures. No caption rewrites and no held.json edits."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from caption_price_format import (
    KINDS,
    MISSING_DOLLAR,
    SPACED_DOLLAR,
    TRAILING_DOLLAR,
    Caption,
    Finding,
    LintResult,
    flag_gia_prices,
    load_fixture,
    main,
    render_report,
    render_suggestions,
    write_outputs,
)

ROOT = Path(__file__).resolve().parents[2]
FIXTURE = Path(__file__).resolve().parent / "fixtures" / "caption_price_format.json"
HELD = ROOT / "data" / "held.json"
SCRIPT = ROOT / "scripts" / "caption_price_format.py"


def _flagged():
    captions = load_fixture(FIXTURE)
    return captions, flag_gia_prices(captions)


def test_fixture_flags_trailing_spaced_and_missing_dollar() -> None:
    _captions, result = _flagged()
    found = [
        (item.caption_id, item.kind, item.excerpt, item.suggestion, item.line)
        for item in result.findings
    ]
    assert found == [
        ("trailing", TRAILING_DOLLAR, "25$", "$25", 2),
        ("trailing-space", TRAILING_DOLLAR, "18 $", "$18", 2),
        ("trailing-cents", TRAILING_DOLLAR, "24.50$", "$24.50", 2),
        ("size-not-price", TRAILING_DOLLAR, "42$", "$42", 3),
        ("spaced", SPACED_DOLLAR, "$ 37", "$37", 2),
        ("spaced-example", SPACED_DOLLAR, "$ 25", "$25", 2),
        ("spaced-cents", SPACED_DOLLAR, "$ 20.00", "$20.00", 2),
        ("missing", MISSING_DOLLAR, "39", "$39", 2),
        ("missing-usd", MISSING_DOLLAR, "40", "$40", 2),
    ]


def test_clean_gia_lines_and_s06_are_not_flagged() -> None:
    captions, result = _flagged()
    flagged = {item.caption_id for item in result.findings}
    clean_ids = (
        "s06",
        "clean-colon",
        "clean-cents",
        "clean-usd-word",
        "inbox",
        "inbox-only",
        "yen",
        "yen-space",
    )
    for caption_id in clean_ids:
        assert caption_id not in flagged
    s06 = next(caption for caption in captions if caption.id == "s06")
    assert s06.text.splitlines() == ["Mã S06", "Set đồ cưng xỉu", "Giá $25"]
    stored = next(row for row in json.loads(FIXTURE.read_text(encoding="utf-8"))["captions"] if row["id"] == "s06")
    assert stored["text"].endswith("Giá $25")
    assert "25$" not in stored["text"]
    assert "$ 25" not in stored["text"]


def test_size_line_is_not_a_price() -> None:
    _captions, result = _flagged()
    size_findings = [item for item in result.findings if item.caption_id == "size-not-price"]
    assert [item.excerpt for item in size_findings] == ["42$"]
    assert all("36" not in item.excerpt for item in result.findings)


def test_suggestions_keep_the_written_amount() -> None:
    _captions, result = _flagged()
    assert result.findings
    for item in result.findings:
        assert item.kind in KINDS
        assert item.suggestion == f"${item.amount}"
        assert item.amount in item.excerpt.replace(" ", "")
        assert item.suggestion != item.excerpt


def test_named_examples_keep_the_amount() -> None:
    captions = [
        Caption("trailing", "Giá: 25$"),
        Caption("spaced", "Giá: $ 25"),
        Caption("missing", "Giá: 25"),
    ]
    originals = [caption.text for caption in captions]
    result = flag_gia_prices(captions)
    found = [
        (item.kind, item.excerpt, item.amount, item.suggestion) for item in result.findings
    ]
    assert found == [
        (TRAILING_DOLLAR, "25$", "25", "$25"),
        (SPACED_DOLLAR, "$ 25", "25", "$25"),
        (MISSING_DOLLAR, "25", "25", "$25"),
    ]
    assert [caption.text for caption in captions] == originals


def test_s06_messy_amount_stays_25_and_text_is_not_rewritten() -> None:
    caption = Caption("s06", "Mã S06\nGiá: 25$")
    result = flag_gia_prices([caption])
    assert caption.text == "Mã S06\nGiá: 25$"
    found = [
        (item.kind, item.excerpt, item.amount, item.suggestion) for item in result.findings
    ]
    assert found == [
        (TRAILING_DOLLAR, "25$", "25", "$25"),
    ]


def test_token_shapes() -> None:
    captions = [
        Caption("double-space", "Giá: $  25"),
        Caption("both", "Giá: $25$"),
        Caption("ma-on-line", "Giá: A07 $25"),
        Caption("yen-after", "Giá: 100 ¥"),
        Caption("ascii", "Gia: 15"),
        Caption("tight", "giá:25$"),
        Caption("two", "Giá: 25$ and $ 30"),
    ]
    result = flag_gia_prices(captions)
    assert [(item.caption_id, item.kind, item.excerpt, item.suggestion) for item in result.findings] == [
        ("double-space", SPACED_DOLLAR, "$  25", "$25"),
        ("both", TRAILING_DOLLAR, "$25$", "$25"),
        ("ascii", MISSING_DOLLAR, "15", "$15"),
        ("tight", TRAILING_DOLLAR, "25$", "$25"),
        ("two", TRAILING_DOLLAR, "25$", "$25"),
        ("two", SPACED_DOLLAR, "$ 30", "$30"),
    ]


def test_report_lists_each_kind() -> None:
    _captions, result = _flagged()
    report = render_report(result)
    suggestions = render_suggestions(result)
    assert "Read-only" in report
    assert "No caption was rewritten" in report
    assert "No price was changed" in report
    assert "Dollar sign after the amount" in report
    assert "Space after the dollar sign" in report
    assert "Missing dollar sign" in report
    assert "`25$` → $25" in report
    assert "`$ 25` → $25" in report
    assert "`$ 37` → $37" in report
    assert "`39` → $39" in report
    assert "Draft display only" in suggestions
    assert "Nothing was posted." in suggestions
    for item in result.findings:
        assert item.caption_id in suggestions
        assert f"Amount stays {item.amount}." in suggestions


def test_unknown_kind_is_rejected() -> None:
    result = LintResult((Finding("x", "nope", "25", "25", "$25", 1),))
    with pytest.raises(ValueError, match="unknown finding kind"):
        render_report(result)
    with pytest.raises(ValueError, match="unknown finding kind"):
        render_suggestions(result)


def test_lint_leaves_fixture_and_held_json_unchanged() -> None:
    before = HELD.read_bytes()
    raw = FIXTURE.read_text(encoding="utf-8")
    captions = load_fixture(FIXTURE)
    originals = [caption.text for caption in captions]
    flag_gia_prices(captions)
    assert [caption.text for caption in captions] == originals
    assert FIXTURE.read_text(encoding="utf-8") == raw
    assert HELD.read_bytes() == before


def test_outputs_are_the_report_files(tmp_path: Path) -> None:
    _captions, result = _flagged()
    write_outputs(result, tmp_path)
    assert sorted(path.name for path in tmp_path.iterdir()) == ["report.md", "suggestions.md"]


def test_cli_writes_report(tmp_path: Path) -> None:
    before_held = HELD.read_bytes()
    before_fixture = FIXTURE.read_bytes()
    out = tmp_path / "gia-price"
    completed = subprocess.run(
        [sys.executable, str(SCRIPT), "--fixture", str(FIXTURE), "--out", str(out)],
        check=False,
        capture_output=True,
        text=True,
    )
    assert completed.returncode == 1, completed.stderr
    report = (out / "report.md").read_text(encoding="utf-8")
    suggestions = (out / "suggestions.md").read_text(encoding="utf-8")
    assert "`25$` → $25" in report
    assert "`$ 25` → $25" in report
    assert "`$ 37` → $37" in report
    assert "`39` → $39" in report
    assert "Amount stays 25." in suggestions
    assert "Amount stays 20.00." in suggestions
    assert HELD.read_bytes() == before_held
    assert FIXTURE.read_bytes() == before_fixture


def test_cli_clean_fixture_exits_zero(tmp_path: Path) -> None:
    fixture = tmp_path / "clean.json"
    fixture.write_text(
        json.dumps({"captions": [{"id": "s06", "text": "Mã S06\nGiá $25"}]}),
        encoding="utf-8",
    )
    out = tmp_path / "out"
    completed = subprocess.run(
        [sys.executable, str(SCRIPT), "--fixture", str(fixture), "--out", str(out)],
        check=False,
        capture_output=True,
        text=True,
    )
    assert completed.returncode == 0, completed.stderr
    report = (out / "report.md").read_text(encoding="utf-8")
    assert "Findings: 0" in report
    assert "No findings." in report
    assert "Giá $25" not in report


def test_cli_without_fixture_does_not_write(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    code = main(["--out", str(tmp_path / "unused")])
    assert code == 2
    assert not (tmp_path / "unused").exists()
    message = capsys.readouterr().out
    assert "fixture" in message
    assert "does not rewrite captions" in message
    assert "change a price" in message


def test_cli_rejects_a_bad_fixture(tmp_path: Path) -> None:
    bad = tmp_path / "bad.json"
    bad.write_text("{", encoding="utf-8")
    code = main(["--fixture", str(bad), "--out", str(tmp_path / "out")])
    assert code == 2
    assert not (tmp_path / "out").exists()


def test_source_stays_fixture_only() -> None:
    source = SCRIPT.read_text(encoding="utf-8").lower()
    for banned in (
        "urllib",
        "requests",
        "httpx",
        "http.client",
        "held.json",
        "facebook.com",
        "instagram.com",
        "vercel",
        "caption_lint",
    ):
        assert banned not in source
