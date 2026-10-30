"""Two Giá line flags from fixtures. No caption rewrites and no held.json edits."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from caption_two_gia import (
    KINDS,
    TWO_GIA_LINES,
    Caption,
    Finding,
    LintResult,
    flag_two_gia_lines,
    load_fixture,
    main,
    render_report,
    write_outputs,
)

ROOT = Path(__file__).resolve().parents[2]
FIXTURE = Path(__file__).resolve().parent / "fixtures" / "caption_two_gia.json"
HELD = ROOT / "data" / "held.json"
SCRIPT = ROOT / "scripts" / "caption_two_gia.py"

QUIET_IDS = (
    "s06",
    "one-line",
    "one-inbox",
    "inbox-only",
    "shoe-word",
    "sentence",
    "size-line",
    "no-gia",
    "one-line-twice",
)


def _flagged():
    captions = load_fixture(FIXTURE)
    return captions, flag_two_gia_lines(captions)


def test_fixture_flags_a_caption_with_two_gia_lines() -> None:
    _captions, result = _flagged()
    found = [(item.caption_id, item.kind, item.lines, item.excerpts) for item in result.findings]
    assert found == [
        ("two-gia", TWO_GIA_LINES, (3, 5), ("Giá: $24", "Giá: $30")),
        ("two-same", TWO_GIA_LINES, (2, 3), ("Giá $37", "Giá $37")),
        ("two-mixed", TWO_GIA_LINES, (2, 3), ("Gia $17", "Giá $19")),
        ("three-gia", TWO_GIA_LINES, (2, 3, 4), ("Giá $20", "Giá $21", "Giá $22")),
    ]
    assert all(item.kind in KINDS for item in result.findings)


def test_one_gia_line_stays_quiet() -> None:
    captions = [
        Caption("plain", "Giá $18"),
        Caption("colon", "Mã A07\nGiá: $26"),
        Caption("inbox", "Mã K06\nGiá: Inbox giá"),
        Caption("sentence", "Mã A01\nÁo giá tốt\nGiá $12"),
        Caption("shoe", "Giày trắng\nGiá $26"),
        Caption("twice-on-one", "Giá $25 Giá $30"),
        Caption("none", "Mã V05\nSize S M L"),
        Caption("size", "Mã G02\nSize 36\nGiá: $42"),
    ]
    originals = [caption.text for caption in captions]
    result = flag_two_gia_lines(captions)
    assert result.findings == ()
    assert [caption.text for caption in captions] == originals

    _fixture_captions, fixture_result = _flagged()
    flagged = {item.caption_id for item in fixture_result.findings}
    for caption_id in QUIET_IDS:
        assert caption_id not in flagged


def test_s06_caption_with_one_line_at_25_stays_clean() -> None:
    captions, result = _flagged()
    assert "s06" not in {item.caption_id for item in result.findings}
    s06 = next(caption for caption in captions if caption.id == "s06")
    assert s06.text.splitlines() == ["Mã S06", "Set đồ cưng xỉu", "Giá $25"]
    stored_rows = json.loads(FIXTURE.read_text(encoding="utf-8"))["captions"]
    stored = next(row for row in stored_rows if row["id"] == "s06")
    assert stored["text"].endswith("Giá $25")
    direct = flag_two_gia_lines(
        [
            Caption("s06", "Mã S06\nGiá $25"),
            Caption("s06-only", "Giá $25"),
        ]
    )
    assert direct.findings == ()


def test_two_gia_lines_are_flagged_without_rewriting() -> None:
    text = "Mã A08\nGiá: $24\nGiá: $30"
    caption = Caption("two", text)
    result = flag_two_gia_lines([caption])
    assert caption.text == text
    assert len(result.findings) == 1
    item = result.findings[0]
    assert item.as_json() == {
        "id": "two",
        "kind": TWO_GIA_LINES,
        "lines": [2, 3],
        "excerpts": ["Giá: $24", "Giá: $30"],
    }


def test_s06_two_lines_stay_priced_at_25_and_are_not_rewritten() -> None:
    text = "Mã S06\nGiá $25\nGiá $30"
    caption = Caption("s06", text)
    result = flag_two_gia_lines([caption])
    assert caption.text == text
    assert "$25" in caption.text
    assert [item.excerpts for item in result.findings] == [("Giá $25", "Giá $30")]


def test_gia_line_shapes() -> None:
    captions = [
        Caption("spaced", "  Giá $10\n\tGia: $11"),
        Caption("tight", "giá:$12\nGIÁ $13"),
        Caption("blank", "Giá $1\n\nGiá $2"),
        Caption("bare", "Giá:\nGiá"),
        Caption("shoe", "Giày trắng\nGiá $14"),
        Caption("sentence", "Áo giá tốt\nGiá $15"),
        Caption("one-double", "Giá $16 Giá $17"),
        Caption("one-bare", "Giá"),
        Caption("inbox", "Inbox giá"),
    ]
    originals = [caption.text for caption in captions]
    result = flag_two_gia_lines(captions)
    assert [(item.caption_id, item.lines, item.excerpts) for item in result.findings] == [
        ("spaced", (1, 2), ("  Giá $10", "\tGia: $11")),
        ("tight", (1, 2), ("giá:$12", "GIÁ $13")),
        ("blank", (1, 3), ("Giá $1", "Giá $2")),
        ("bare", (1, 2), ("Giá:", "Giá")),
    ]
    assert [caption.text for caption in captions] == originals


def test_report_quotes_both_lines_and_does_not_rewrite() -> None:
    captions, result = _flagged()
    report = render_report(result)
    assert "Read-only" in report
    assert "No caption was rewritten" in report
    assert "No price was changed" in report
    assert "No Facebook or Instagram post was created, edited, or deleted." in report
    assert "Two or more Giá lines" in report
    assert "two-gia: 2 Giá lines — line 3 `Giá: $24`; line 5 `Giá: $30`" in report
    assert "three-gia: 3 Giá lines — line 2 `Giá $20`; line 3 `Giá $21`; line 4 `Giá $22`" in report
    assert "Giá $25" not in report
    two = next(caption for caption in captions if caption.id == "two-gia")
    s06 = next(caption for caption in captions if caption.id == "s06")
    assert two.text not in report
    assert s06.text not in report
    assert two.text == "Mã A08\nÁo hoa\nGiá: $24\nSize S / M / L\nGiá: $30"


def test_unknown_kind_is_rejected() -> None:
    result = LintResult((Finding("x", "nope", (1, 2), ("Giá $1", "Giá $2")),))
    with pytest.raises(ValueError, match="unknown finding kind"):
        render_report(result)
    short = LintResult((Finding("x", TWO_GIA_LINES, (1,), ("Giá $1",)),))
    with pytest.raises(ValueError, match="at least two lines"):
        render_report(short)


def test_lint_leaves_fixture_and_held_json_unchanged() -> None:
    before = HELD.read_bytes()
    raw = FIXTURE.read_text(encoding="utf-8")
    captions = load_fixture(FIXTURE)
    originals = [caption.text for caption in captions]
    flag_two_gia_lines(captions)
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
    out = tmp_path / "two-gia"
    completed = subprocess.run(
        [sys.executable, str(SCRIPT), "--fixture", str(FIXTURE), "--out", str(out)],
        check=False,
        capture_output=True,
        text=True,
    )
    assert completed.returncode == 1, completed.stderr
    assert completed.stdout.splitlines() == [str(out / "report.md")]
    assert "Giá: $30" not in completed.stdout
    report = (out / "report.md").read_text(encoding="utf-8")
    assert "two-gia: 2 Giá lines — line 3 `Giá: $24`; line 5 `Giá: $30`" in report
    assert "No caption was rewritten" in report
    assert "No Facebook or Instagram post was created, edited, or deleted." in report
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


def test_cli_one_gia_line_exits_zero(tmp_path: Path) -> None:
    fixture = tmp_path / "one.json"
    fixture.write_text(
        json.dumps(
            {"captions": [{"id": "one-line", "text": "Mã A07\nGiá: $26"}]},
            ensure_ascii=False,
        ),
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
    assert "Giá: $26" not in report


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
    ):
        assert banned not in source
