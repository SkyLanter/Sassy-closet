"""Richer Taobao unreachable-streak report. Synthetic fixtures only, no network."""
import datetime as dt
import json
import socket
from pathlib import Path

import pytest

import taobao_unreachable_streak as s


@pytest.fixture(autouse=True)
def no_net(monkeypatch):
    def boom(*_a, **_k):
        raise AssertionError("network used")
    monkeypatch.setattr(socket, "create_connection", boom)
    monkeypatch.setattr(socket.socket, "connect", boom)


GOLDEN = Path(__file__).resolve().parent / "fixtures" / "golden"
SECRET = "SECRET_NAME_DO_NOT_PRINT"


def _flags(path, rows):
    body = "ma,name,source_link,baseline_cny,flag\n" + "".join(
        f"{ma},{SECRET},https://example.invalid/item,99.5,{fl}\n" for ma, fl in rows)
    path.write_text(body, encoding="utf-8")


def test_golden_stale_gap_and_unusable(tmp_path):
    _flags(tmp_path / "cost-recheck-2026-10-16-flags.csv", [("A07", "unreachable")])
    _flags(tmp_path / "cost-recheck-2026-10-20-flags.csv", [("A07", "unreachable"), ("D01", "loss")])
    (tmp_path / "cost-recheck-2026-10-21-flags.csv").write_bytes(b"")
    _flags(tmp_path / "cost-recheck-2026-99-99-flags.csv", [("A09", "unreachable")])
    _flags(tmp_path / "cost-recheck-notadate-flags.csv", [("A08", "unreachable")])
    text = s.build_report(str(tmp_path), min_days=2, as_of=dt.date(2026, 10, 22))
    golden = (GOLDEN / "cost_recheck_streak_stale.txt").read_text(encoding="utf-8")
    assert text == golden
    for hidden in (SECRET, "99.5", "example.invalid", "¥", "$", str(tmp_path)):
        assert hidden not in text
    assert "A09" not in text and "A08" not in text


def test_golden_unusable_only_is_not_a_clean_day(tmp_path):
    (tmp_path / "cost-recheck-2026-10-22-flags.csv").write_bytes(b"")
    (tmp_path / "cost-recheck-2026-10-23-flags.csv").write_text("name,note\nSecret,nope\n", encoding="utf-8")
    text = s.build_report(str(tmp_path), as_of=dt.date(2026, 10, 23))
    assert text == (GOLDEN / "cost_recheck_streak_unusable_only.txt").read_text(encoding="utf-8")
    assert "OK" not in text and "Secret" not in text


def test_golden_fresh_quiet(tmp_path):
    _flags(tmp_path / "cost-recheck-2026-10-22-flags.csv", [("A06", "loss")])
    text = s.build_report(str(tmp_path), as_of=dt.date(2026, 10, 22))
    assert text == (GOLDEN / "cost_recheck_streak_fresh_quiet.txt").read_text(encoding="utf-8")
    assert SECRET not in text


def test_empty_file_does_not_clear_a_streak(tmp_path):
    _flags(tmp_path / "cost-recheck-2026-10-21-flags.csv", [("A07", "unreachable")])
    (tmp_path / "cost-recheck-2026-10-22-flags.csv").write_bytes(b"")
    runs, problems, _dates, _blocked, _bad = s.scan(str(tmp_path))
    assert problems == [("cost-recheck-2026-10-22-flags.csv", "empty file")]
    assert s.streaks(runs) == {"A07": (1, "2026-10-21")}
    text = s.build_report(str(tmp_path), min_days=1, as_of=dt.date(2026, 10, 22))
    assert "WARN unreachable_streak A07 day 1 (since 2026-10-21)" in text
    assert "UNUSABLE cost-recheck-2026-10-22-flags.csv: empty file" in text
    assert "OK no unreachable streaks" not in text


def test_header_only_file_is_a_real_clean_day(tmp_path):
    _flags(tmp_path / "cost-recheck-2026-10-21-flags.csv", [("A07", "unreachable")])
    (tmp_path / "cost-recheck-2026-10-22-flags.csv").write_text("ma,flag\n", encoding="utf-8")
    runs, problems, _dates, _blocked, _bad = s.scan(str(tmp_path))
    assert problems == []
    assert s.streaks(runs) == {}
    text = s.build_report(str(tmp_path), as_of=dt.date(2026, 10, 22))
    assert "latest_run 2026-10-22 runs_read 2" in text
    assert "OK no unreachable streaks" in text
    assert "UNUSABLE" not in text and "STALE" not in text


def test_bad_date_is_not_the_latest_run(tmp_path):
    _flags(tmp_path / "cost-recheck-2026-10-22-flags.csv", [("A07", "unreachable")])
    _flags(tmp_path / "cost-recheck-2026-99-99-flags.csv", [("A01", "unreachable")])
    runs, problems, _dates, _blocked, _bad = s.scan(str(tmp_path))
    assert [d for d, _ in runs] == ["2026-10-22"]
    assert ("cost-recheck-2026-99-99-flags.csv", "not a real date") in problems
    assert s.streaks(runs) == {"A07": (1, "2026-10-22")}
    text = s.build_report(str(tmp_path), min_days=1, as_of=dt.date(2026, 10, 22))
    assert "UNUSABLE cost-recheck-2026-99-99-flags.csv: not a real date" in text
    assert "A01" not in text


def test_unusable_day_inside_the_span_is_not_listed_as_missing(tmp_path):
    _flags(tmp_path / "cost-recheck-2026-10-16-flags.csv", [("A07", "unreachable")])
    (tmp_path / "cost-recheck-2026-10-18-flags.csv").write_bytes(b"")
    _flags(tmp_path / "cost-recheck-2026-10-20-flags.csv", [("A07", "unreachable")])
    text = s.build_report(str(tmp_path), min_days=1, as_of=dt.date(2026, 10, 20))
    assert "2026-10-17" in text and "2026-10-19" in text
    assert "2026-10-18" not in text.split("NOTE", 1)[-1].split("UNUSABLE", 1)[0]
    assert "UNUSABLE cost-recheck-2026-10-18-flags.csv: empty file" in text
    assert "WARN unreachable_streak A07 day 2 (since 2026-10-16)" in text


def test_long_gap_is_counted_not_listed(tmp_path):
    _flags(tmp_path / "cost-recheck-2026-10-01-flags.csv", [("A07", "unreachable")])
    _flags(tmp_path / "cost-recheck-2026-10-20-flags.csv", [("A07", "unreachable")])
    text = s.build_report(str(tmp_path), min_days=1, as_of=dt.date(2026, 10, 20))
    assert "NOTE missing cost-recheck days 18 days from 2026-10-02 through 2026-10-19." in text
    assert "2026-10-03" not in text


def test_split_gap_does_not_cover_a_day_that_has_a_file(tmp_path):
    for day in ("2026-10-01", "2026-10-10", "2026-10-20"):
        _flags(tmp_path / f"cost-recheck-{day}-flags.csv", [("A07", "unreachable")])
    text = s.build_report(str(tmp_path), min_days=1, as_of=dt.date(2026, 10, 20))
    assert "WARN unreachable_streak A07 day 3 (since 2026-10-01)" in text
    note = next(line for line in text.splitlines() if line.startswith("NOTE missing"))
    assert "17 days in separate gaps" in note
    assert "earliest 2026-10-02" in note and "latest 2026-10-19" in note
    assert "through" not in note and "2026-10-10" not in note


def test_broken_csv_does_not_clear_a_streak(tmp_path):
    _flags(tmp_path / "cost-recheck-2026-10-20-flags.csv", [("A07", "unreachable")])
    _flags(tmp_path / "cost-recheck-2026-10-21-flags.csv", [("A07", "unreachable")])
    broken = tmp_path / "cost-recheck-2026-10-22-flags.csv"
    broken.write_bytes(b"ma,flag\nA07,unreachable\x00\n")
    text = s.build_report(str(tmp_path), min_days=1, as_of=dt.date(2026, 10, 22))
    assert "UNUSABLE cost-recheck-2026-10-22-flags.csv: bad csv" in text
    assert "WARN unreachable_streak A07 day 2 (since 2026-10-20)" in text
    assert "OK no unreachable streaks" not in text

    broken.write_text("ma,name,flag\nA07,Dress, red,unreachable\n", encoding="utf-8")
    text = s.build_report(str(tmp_path), min_days=1, as_of=dt.date(2026, 10, 22))
    assert "UNUSABLE cost-recheck-2026-10-22-flags.csv: bad csv" in text
    assert "Dress" not in text and "OK no unreachable streaks" not in text

    broken.write_text(
        'ma,name,source_link,baseline_cny,flag\n'
        'A07,"Secret name,https://example.invalid/item,99.5,unreachable\n',
        encoding="utf-8")
    text = s.build_report(str(tmp_path), min_days=1, as_of=dt.date(2026, 10, 22))
    assert "UNUSABLE cost-recheck-2026-10-22-flags.csv: bad csv" in text
    assert all(hidden not in text for hidden in ("Secret name", "99.5"))
    assert "OK no unreachable streaks" not in text


def test_quoted_comma_in_another_column_stays_usable(tmp_path):
    path = tmp_path / "cost-recheck-2026-10-22-flags.csv"
    path.write_text('ma,name,flag\nA07,"Dress, red",unreachable\n', encoding="utf-8")
    runs, problems, _dates, _blocked, _bad = s.scan(str(tmp_path))
    assert problems == []
    assert runs == [("2026-10-22", {"A07"})]


def test_missing_folder_and_future_file(tmp_path, capsys):
    missing = tmp_path / "no-such-folder"
    assert s.build_report(str(missing), as_of=dt.date(2026, 10, 22)) == (
        "MISSING cost-recheck folder (no cost-recheck flag files found)\n")
    _flags(tmp_path / "cost-recheck-2026-10-22-flags.csv", [("A06", "loss")])
    text = s.build_report(str(tmp_path), as_of=dt.date(2026, 10, 20))
    assert "NOTE latest cost-recheck flags 2026-10-22 are after 2026-10-20" in text
    assert "STALE" not in text
    assert s.rich_main(["--dir", str(tmp_path), "--as-of", "2026-99-99"]) == 2
    err = capsys.readouterr().err
    assert "YYYY-MM-DD" in err


def _summary(tmp_path, date, doc, bom=False):
    raw = json.dumps(doc).encode("utf-8")
    if bom:
        raw = b"\xef\xbb\xbf" + raw
    (tmp_path / f"summary.{date}.json").write_bytes(raw)


def test_signed_out_block_does_not_count_or_break(tmp_path):
    _flags(tmp_path / "cost-recheck-2026-10-20-flags.csv", [("A07", "unreachable")])
    _flags(tmp_path / "cost-recheck-2026-10-21-flags.csv", [("A07", "loss")])
    _summary(tmp_path, "2026-10-21", {"taobao_login_needed": True, "unreachable_mas": []})
    _flags(tmp_path / "cost-recheck-2026-10-22-flags.csv", [("A07", "unreachable")])
    runs = s.load_runs(str(tmp_path))
    assert runs == [("2026-10-20", {"A07"}), ("2026-10-22", {"A07"})]
    assert s.streaks(runs)["A07"] == (2, "2026-10-20")
    text = s.build_report(str(tmp_path), min_days=2, as_of=dt.date(2026, 10, 22))
    assert "latest_run 2026-10-22 runs_read 2" in text
    assert "NOTE signed-out cost-recheck block 2026-10-21 (unreachable flags not used)" in text
    assert "missing cost-recheck days" not in text
    assert "STALE" not in text
    assert "WARN unreachable_streak A07 day 2 (since 2026-10-20)" in text
    for hidden in (SECRET, "99.5", "example.invalid", "¥"):
        assert hidden not in text


def test_blocked_day_is_not_a_missing_calendar_day(tmp_path):
    _flags(tmp_path / "cost-recheck-2026-10-16-flags.csv", [("A07", "unreachable")])
    _flags(tmp_path / "cost-recheck-2026-10-20-flags.csv", [("A07", "unreachable")])
    _summary(tmp_path, "2026-10-20", {"taobao_login_needed": True})
    _flags(tmp_path / "cost-recheck-2026-10-22-flags.csv", [("A07", "unreachable")])
    text = s.build_report(str(tmp_path), min_days=1, as_of=dt.date(2026, 10, 22))
    note = next(line for line in text.splitlines() if line.startswith("NOTE missing"))
    assert "2026-10-20" not in note
    assert "2026-10-17" in note and "2026-10-21" in note
    assert "NOTE signed-out cost-recheck block 2026-10-20 (unreachable flags not used)" in text
    assert "WARN unreachable_streak A07 day 2 (since 2026-10-16)" in text


def test_blocked_newest_equal_as_of_is_not_stale(tmp_path):
    _flags(tmp_path / "cost-recheck-2026-10-20-flags.csv", [("A07", "unreachable")])
    _flags(tmp_path / "cost-recheck-2026-10-22-flags.csv", [("A07", "unreachable")])
    _summary(tmp_path, "2026-10-22", {"taobao_login_needed": True})
    text = s.build_report(str(tmp_path), min_days=1, as_of=dt.date(2026, 10, 22))
    assert "latest_run 2026-10-20 runs_read 1" in text
    assert "NOTE signed-out cost-recheck block 2026-10-22 (unreachable flags not used)" in text
    assert "STALE" not in text
    assert "WARN unreachable_streak A07 day 1 (since 2026-10-20)" in text


def test_stale_uses_newer_blocked_day(tmp_path):
    _flags(tmp_path / "cost-recheck-2026-10-20-flags.csv", [("A07", "unreachable")])
    _flags(tmp_path / "cost-recheck-2026-10-21-flags.csv", [("A07", "unreachable")])
    _summary(tmp_path, "2026-10-21", {"taobao_login_needed": True})
    text = s.build_report(str(tmp_path), min_days=1, as_of=dt.date(2026, 10, 22))
    assert "STALE latest cost-recheck flags 2026-10-21 are before 2026-10-22" in text
    assert "latest_run 2026-10-20 runs_read 1" in text


def test_all_blocked_is_ok_not_missing(tmp_path):
    _flags(tmp_path / "cost-recheck-2026-10-20-flags.csv", [("A07", "unreachable")])
    _flags(tmp_path / "cost-recheck-2026-10-22-flags.csv", [("A07", "unreachable")])
    for day in ("2026-10-20", "2026-10-22"):
        _summary(tmp_path, day, {"taobao_login_needed": True})
    text = s.build_report(str(tmp_path), as_of=dt.date(2026, 10, 22))
    assert text.splitlines()[0] == (
        "OK signed-out block on 2 cost-recheck run(s); unreachable flags not used")
    assert "MISSING" not in text and "A07" not in text
    assert "NOTE missing cost-recheck days 2026-10-21" in text
    assert "STALE" not in text
    assert "signed-out cost-recheck block 2026-10-20" not in text
    for hidden in (SECRET, "99.5", "example.invalid", "¥"):
        assert hidden not in text


def test_all_blocked_before_as_of_is_stale_without_mas(tmp_path):
    _flags(tmp_path / "cost-recheck-2026-10-20-flags.csv", [("A07", "unreachable")])
    _summary(tmp_path, "2026-10-20", {"taobao_login_needed": 1})
    text = s.build_report(str(tmp_path), as_of=dt.date(2026, 10, 22))
    assert text.splitlines()[0] == (
        "OK signed-out block on 1 cost-recheck run(s); unreachable flags not used")
    assert "STALE latest cost-recheck flags 2026-10-20 are before 2026-10-22" in text
    assert "A07" not in text and "MISSING" not in text


def test_unusable_name_still_prints_when_dated_files_are_blocked(tmp_path):
    _flags(tmp_path / "cost-recheck-2026-10-22-flags.csv", [("A07", "unreachable")])
    _summary(tmp_path, "2026-10-22", {"taobao_login_needed": True})
    _flags(tmp_path / "cost-recheck-2026-99-99-flags.csv", [("A09", "unreachable")])
    text = s.build_report(str(tmp_path), as_of=dt.date(2026, 10, 22))
    assert "OK signed-out block on 1 cost-recheck run(s); unreachable flags not used" in text
    assert "UNUSABLE cost-recheck-2026-99-99-flags.csv: not a real date" in text
    assert "MISSING" not in text and "A07" not in text and "A09" not in text


def test_blocked_plus_unusable_dated_file_is_not_the_all_blocked_line(tmp_path):
    _flags(tmp_path / "cost-recheck-2026-10-20-flags.csv", [("A07", "unreachable")])
    _summary(tmp_path, "2026-10-20", {"taobao_login_needed": True})
    (tmp_path / "cost-recheck-2026-10-21-flags.csv").write_bytes(b"")
    text = s.build_report(str(tmp_path), as_of=dt.date(2026, 10, 21))
    assert "OK signed-out block" not in text
    assert "MISSING no usable cost-recheck flag files found" in text
    assert "UNUSABLE cost-recheck-2026-10-21-flags.csv: empty file" in text
    assert "signed-out cost-recheck block" not in text
    assert "NOTE missing" not in text
    assert "A07" not in text and SECRET not in text


def test_bad_json_summary_is_skipped(tmp_path):
    _flags(tmp_path / "cost-recheck-2026-10-22-flags.csv", [("A07", "unreachable")])
    (tmp_path / "summary.2026-10-22.json").write_text("{", encoding="utf-8")
    runs, problems, _dates, blocked, bad = s.scan(str(tmp_path))
    assert problems == []
    assert blocked == []
    assert [day.isoformat() for day in bad] == ["2026-10-22"]
    assert runs == []
    assert s.load_runs(str(tmp_path)) == []
    text = s.build_report(str(tmp_path), min_days=1, as_of=dt.date(2026, 10, 22))
    assert "signed-out" not in text
    assert "A07" not in text
    assert "WARN" not in text
    assert text.splitlines()[0] == (
        "OK unreadable cost-recheck summary on 1 run(s); unreachable flags not used")


def test_bad_summary_between_runs_does_not_break(tmp_path):
    _flags(tmp_path / "cost-recheck-2026-10-20-flags.csv", [("A07", "unreachable")])
    _flags(tmp_path / "cost-recheck-2026-10-21-flags.csv", [("A07", "unreachable"), ("D01", "unreachable")])
    _flags(tmp_path / "cost-recheck-2026-10-22-flags.csv", [("A07", "unreachable")])
    (tmp_path / "summary.2026-10-21.json").write_text("{", encoding="utf-8")
    text = s.build_report(str(tmp_path), min_days=1, as_of=dt.date(2026, 10, 22))
    assert "WARN unreachable_streak A07 day 2 (since 2026-10-20)" in text
    assert "D01" not in text
    assert "NOTE unreadable cost-recheck summary 2026-10-21 (unreachable flags not used)" in text
    assert "missing cost-recheck days" not in text
    assert "signed-out" not in text


def test_bom_summary_blocks_and_false_string_does_not(tmp_path):
    _flags(tmp_path / "cost-recheck-2026-10-21-flags.csv", [("A07", "unreachable")])
    _flags(tmp_path / "cost-recheck-2026-10-22-flags.csv", [("A07", "loss")])
    _summary(tmp_path, "2026-10-22", {"taobao_login_needed": True}, bom=True)
    assert s.load_runs(str(tmp_path)) == [("2026-10-21", {"A07"})]
    kept = tmp_path / "kept"
    kept.mkdir()
    _flags(kept / "cost-recheck-2026-10-22-flags.csv", [("A07", "unreachable")])
    _summary(kept, "2026-10-22", {"taobao_login_needed": "false", "unreachable_mas": ["A01", "A02"]})
    assert s.load_runs(str(kept)) == [("2026-10-22", {"A07"})]
    text = s.build_report(str(kept), min_days=1, as_of=dt.date(2026, 10, 22))
    assert "signed-out" not in text


def test_cli_matches_golden(tmp_path, capsys):
    _flags(tmp_path / "cost-recheck-2026-10-16-flags.csv", [("A07", "unreachable")])
    _flags(tmp_path / "cost-recheck-2026-10-20-flags.csv", [("A07", "unreachable"), ("D01", "loss")])
    (tmp_path / "cost-recheck-2026-10-21-flags.csv").write_bytes(b"")
    _flags(tmp_path / "cost-recheck-2026-99-99-flags.csv", [("A09", "unreachable")])
    assert s.rich_main(["--dir", str(tmp_path), "--min-days", "2", "--as-of", "2026-10-22"]) == 0
    out = capsys.readouterr().out
    assert out == (GOLDEN / "cost_recheck_streak_stale.txt").read_text(encoding="utf-8")
    assert str(tmp_path) not in out
