"""Giá lines with no digit, from fixtures. No caption rewrites and no held.json edits."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from caption_gia_no_digit import (
    GIA_NO_DIGIT,
    KINDS,
    Caption,
    Finding,
    LintResult,
    flag_gia_no_digit,
    load_fixture,
    main,
    render_report,
    write_outputs,
)

ROOT = Path(__file__).resolve().parents[2]
FIXTURE = Path(__file__).resolve().parent / "fixtures" / "caption_gia_no_digit.json"
HELD = ROOT / "data" / "held.json"
SCRIPT = ROOT / "scripts" / "caption_gia_no_digit.py"

QUIET_IDS = (
    "s06",
    "clean-colon",
    "clean-plain",
    "cents",
    "bare-amount",
    "yen",
    "inbox-only",
    "shoe",
    "sentence",
    "same-line-digit",
    "no-gia",
)


def _flagged():
    captions = load_fixture(FIXTURE)
    return captions, flag_gia_no_digit(captions)


def test_fixture_flags_a_gia_line_with_no_digit() -> None:
    _captions, result = _flagged()
    found = [(item.caption_id, item.kind, item.line, item.excerpt) for item in result.findings]
    assert found == [
        ("inbox", GIA_NO_DIGIT, 2, "Giá: Inbox"),
        ("inbox-gia", GIA_NO_DIGIT, 2, "Giá: Inbox giá"),
        ("bare", GIA_NO_DIGIT, 2, "Giá"),
        ("colon", GIA_NO_DIGIT, 2, "Giá:"),
        ("mixed", GIA_NO_DIGIT, 3, "Giá: Inbox"),
        ("words", GIA_NO_DIGIT, 2, "Giá: twenty"),
        ("size", GIA_NO_DIGIT, 3, "Giá: Inbox"),
        ("no-accent", GIA_NO_DIGIT, 2, "Gia: Inbox"),
        ("two-blank", GIA_NO_DIGIT, 2, "Giá:"),
        ("two-blank", GIA_NO_DIGIT, 3, "Giá"),
    ]
    assert all(item.kind in KINDS for item in result.findings)


def test_priced_gia_lines_stay_quiet() -> None:
    captions = [
        Caption("plain", "Giá $18"),
        Caption("colon", "Mã A07\nGiá: $26"),
        Caption("cents", "Giá: $24.50"),
        Caption("bare-amount", "Giá: 39"),
        Caption("yen", "Giá: ¥100"),
        Caption("same-line", "Giá $25 Inbox"),
        Caption("sentence", "Mã A01\nÁo giá tốt\nGiá $12"),
        Caption("shoe", "Giày trắng\nGiá $26"),
        Caption("inbox-word", "Inbox giá"),
        Caption("none", "Mã V05\nSize S M L"),
        Caption("size", "Mã G02\nSize 36\nGiá: $42"),
    ]
    originals = [caption.text for caption in captions]
    result = flag_gia_no_digit(captions)
    assert result.findings == ()
    assert [caption.text for caption in captions] == originals

    _fixture_captions, fixture_result = _flagged()
    flagged = {item.caption_id for item in fixture_result.findings}
    for caption_id in QUIET_IDS:
        assert caption_id not in flagged


def test_s06_line_at_25_stays_clean() -> None:
    captions, result = _flagged()
    assert "s06" not in {item.caption_id for item in result.findings}
    s06 = next(caption for caption in captions if caption.id == "s06")
    assert s06.text.splitlines() == ["Mã S06", "Set đồ cưng xỉu", "Giá $25"]
    stored_rows = json.loads(FIXTURE.read_text(encoding="utf-8"))["captions"]
    stored = next(row for row in stored_rows if row["id"] == "s06")
    assert stored["text"].endswith("Giá $25")
    direct = flag_gia_no_digit(
        [
            Caption("s06", "Mã S06\nGiá $25"),
            Caption("s06-only", "Giá $25"),
        ]
    )
    assert direct.findings == ()


def test_gia_inbox_is_flagged_without_rewriting() -> None:
    text = "Mã D06\nGiá: Inbox"
    caption = Caption("inbox", text)
    result = flag_gia_no_digit([caption])
    assert caption.text == text
    assert len(result.findings) == 1
    item = result.findings[0]
    assert item.as_json() == {
        "id": "inbox",
        "kind": GIA_NO_DIGIT,
        "line": 2,
        "excerpt": "Giá: Inbox",
    }
    assert "$" not in caption.text


def test_s06_digitless_line_is_flagged_and_not_rewritten() -> None:
    text = "Mã S06\nGiá: Inbox"
    caption = Caption("s06", text)
    result = flag_gia_no_digit([caption])
    assert caption.text == text
    assert "$25" not in caption.text
    assert [item.excerpt for item in result.findings] == ["Giá: Inbox"]


def test_mixed_caption_flags_only_the_line_with_no_digit() -> None:
    text = "Mã A05\nGiá $25\nGiá: Inbox"
    caption = Caption("mixed", text)
    result = flag_gia_no_digit([caption])
    assert caption.text == text
    assert [(item.line, item.excerpt) for item in result.findings] == [(3, "Giá: Inbox")]


def test_gia_line_shapes() -> None:
    captions = [
        Caption("spaced", "  Giá: Inbox"),
        Caption("tab", "\tGia: Inbox"),
        Caption("tight", "giá:Inbox"),
        Caption("upper", "GIÁ: INBOX"),
        Caption("space-colon", "Giá : Inbox"),
        Caption("digit-later", "Giá: Inbox 2"),
        Caption("fullwidth", "Giá: ２５"),
        Caption("shoe", "Giày trắng"),
        Caption("sentence", "Áo giá tốt"),
        Caption("inbox-word", "Inbox"),
        Caption("priced", "Giá $25 Giá Inbox"),
        Caption("blank", "\nGiá: Inbox\n"),
    ]
    originals = [caption.text for caption in captions]
    result = flag_gia_no_digit(captions)
    assert [(item.caption_id, item.line, item.excerpt) for item in result.findings] == [
        ("spaced", 1, "  Giá: Inbox"),
        ("tab", 1, "\tGia: Inbox"),
        ("tight", 1, "giá:Inbox"),
        ("upper", 1, "GIÁ: INBOX"),
        ("space-colon", 1, "Giá : Inbox"),
        ("blank", 2, "Giá: Inbox"),
    ]
    assert [caption.text for caption in captions] == originals


def test_report_quotes_the_line_and_does_not_rewrite() -> None:
    captions, result = _flagged()
    report = render_report(result)
    assert "Read-only" in report
    assert "No caption was rewritten" in report
    assert "No price was changed" in report
    assert "No Facebook or Instagram post was created, edited, or deleted." in report
    assert "Giá line with no digit" in report
    assert "inbox: line 2 `Giá: Inbox`" in report
    assert "size: line 3 `Giá: Inbox`" in report
    assert "Giá $25" not in report
    inbox = next(caption for caption in captions if caption.id == "inbox")
    s06 = next(caption for caption in captions if caption.id == "s06")
    assert inbox.text not in report
    assert s06.text not in report
    assert inbox.text == "Mã D06\nGiá: Inbox"


def test_unknown_kind_is_rejected() -> None:
    result = LintResult((Finding("x", "nope", 1, "Giá: Inbox"),))
    with pytest.raises(ValueError, match="unknown finding kind"):
        render_report(result)
    short = LintResult((Finding("x", GIA_NO_DIGIT, 0, "Giá: Inbox"),))
    with pytest.raises(ValueError, match="needs the Giá line"):
        render_report(short)
    empty = LintResult((Finding("x", GIA_NO_DIGIT, 1, ""),))
    with pytest.raises(ValueError, match="needs the Giá line"):
        render_report(empty)


def test_lint_leaves_fixture_and_held_json_unchanged() -> None:
    before = HELD.read_bytes()
    raw = FIXTURE.read_text(encoding="utf-8")
    captions = load_fixture(FIXTURE)
    originals = [caption.text for caption in captions]
    flag_gia_no_digit(captions)
    assert [caption.text for caption in captions] == originals
    assert FIXTURE.read_text(encoding="utf-8") == raw
    assert HELD.read_bytes() == before


def test_outputs_are_only_the_report(tmp_path: Path) -> None:
    _captions, result = _flagged()
    write_outputs(result, tmp_path)
    assert sorted(path.name for path in tmp_path.iterdir()) == ["report.md"]


def test_cli_writes_report_without_rewriting(tmp_path: Path) -> None:
    before_held = HELD.read_bytes()
    before_fixture = FIXTURE.read_bytes()
    out = tmp_path / "gia-no-digit"
    completed = subprocess.run(
        [sys.executable, str(SCRIPT), "--fixture", str(FIXTURE), "--out", str(out)],
        check=False,
        capture_output=True,
        text=True,
    )
    assert completed.returncode == 1, completed.stderr
    assert completed.stdout.splitlines() == [str(out / "report.md")]
    assert "Giá: Inbox" not in completed.stdout
    report = (out / "report.md").read_text(encoding="utf-8")
    assert "inbox: line 2 `Giá: Inbox`" in report
    assert "No caption was rewritten" in report
    assert "No Facebook or Instagram post was created, edited, or deleted." in report
    assert "Giá $25" not in report
    assert sorted(path.name for path in out.iterdir()) == ["report.md"]
    assert HELD.read_bytes() == before_held
    assert FIXTURE.read_bytes() == before_fixture


def test_cli_clean_s06_exits_zero(tmp_path: Path) -> None:
    fixture = tmp_path / "clean.json"
    raw = json.dumps(
        {"captions": [{"id": "s06", "text": "Mã S06\nSet đồ cưng xỉu\nGiá $25"}]},
        ensure_ascii=False,
    )
    fixture.write_text(raw, encoding="utf-8")
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
    assert fixture.read_text(encoding="utf-8") == raw
    assert raw.endswith('Giá $25"}]}')


def test_cli_without_fixture_does_not_write(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    code = main(["--out", str(tmp_path / "unused")])
    assert code == 2
    assert not (tmp_path / "unused").exists()
    message = capsys.readouterr().out
    assert "fixture" in message
    assert "does not rewrite captions" in message
    assert "or post" in message

    code = main(["--fixture", str(FIXTURE)])
    assert code == 2
    assert capsys.readouterr().out


def test_cli_rejects_a_bad_fixture(tmp_path: Path) -> None:
    bad = tmp_path / "bad.json"
    bad.write_text("{", encoding="utf-8")
    code = main(["--fixture", str(bad), "--out", str(tmp_path / "out")])
    assert code == 2
    assert not (tmp_path / "out").exists()

    missing = tmp_path / "missing.json"
    code = main(["--fixture", str(missing), "--out", str(tmp_path / "out")])
    assert code == 2
    assert not (tmp_path / "out").exists()

    wrong = tmp_path / "wrong.json"
    wrong.write_text(json.dumps({"captions": [{"id": "x"}]}), encoding="utf-8")
    code = main(["--fixture", str(wrong), "--out", str(tmp_path / "out")])
    assert code == 2
    assert not (tmp_path / "out").exists()


def test_source_stays_fixture_only() -> None:
    source = SCRIPT.read_text(encoding="utf-8").lower()
    for banned in (
        "urllib",
        "requests",
        "httpx",
        "http.client",
        "socket",
        "subprocess",
        "held.json",
        "facebook.com",
        "instagram.com",
        "vercel",
        "caption_lint",
        "caption_price_format",
        "caption_price_mismatch",
        "caption_two_gia",
    ):
        assert banned not in source
