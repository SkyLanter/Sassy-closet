"""Piece 49 taobao_unreachable_streak: synthetic fixtures only, no network."""
import datetime as dt
import socket
from pathlib import Path

import pytest

import taobao_unreachable_streak as s

HDR = "ma,name,source_link,baseline_cny,flag\n"


@pytest.fixture(autouse=True)
def no_net(monkeypatch):
    def boom(*a, **k):
        raise AssertionError("network used")
    monkeypatch.setattr(socket, "create_connection", boom)
    monkeypatch.setattr(socket.socket, "connect", boom)


def write(tmp_path, date, rows):
    body = HDR + "".join(f"{ma},Secret name,LINK_REDACTED,99.5,{fl}\n" for ma, fl in rows)
    (tmp_path / f"cost-recheck-{date}-flags.csv").write_text(body, encoding="utf-8")


def fixture(tmp_path):
    write(tmp_path, "2026-10-16", [("A07", "unreachable"), ("D01", "unreachable"), ("A22", "loss")])
    write(tmp_path, "2026-10-20", [("A07", "unreachable"), ("D01", "loss"), ("A22", "loss")])
    write(tmp_path, "2026-10-21", [("A07", "unreachable"), ("D01", "unreachable"), ("A22", "unreachable"), ("O01", "unreachable|missing_kg")])
    write(tmp_path, "2026-10-22", [("A07", "unreachable"), ("D01", "unreachable"), ("A22", "unreachable"), ("O01", "unreachable|missing_kg"), ("S13", "under_25")])


def test_streak_counts(tmp_path):
    fixture(tmp_path)
    r = s.streaks(s.load_runs(str(tmp_path)))
    assert r == {"A07": (4, "2026-10-16"), "D01": (2, "2026-10-21"),
                 "A22": (2, "2026-10-21"), "O01": (2, "2026-10-21")}


def test_warn_order_and_min(tmp_path):
    fixture(tmp_path)
    lines = s.warn_lines(s.streaks(s.load_runs(str(tmp_path))), 3)
    assert lines == ["WARN unreachable_streak A07 day 4 (since 2026-10-16)"]


def test_output_has_no_private_data(tmp_path, capsys):
    fixture(tmp_path)
    assert s.main(["--dir", str(tmp_path), "--min-days", "1"]) == 0
    out = capsys.readouterr().out
    for bad in ("¥", "99.5", "LINK", "Secret", "$"):
        assert bad not in out
    assert "A22 day 2" in out and "S13" not in out


def test_empty_dir(tmp_path, capsys):
    assert s.main(["--dir", str(tmp_path)]) == 0
    assert "no cost-recheck" in capsys.readouterr().out


def test_no_streaks(tmp_path, capsys):
    write(tmp_path, "2026-10-22", [("A06", "loss")])
    s.main(["--dir", str(tmp_path)])
    assert "OK no unreachable streaks" in capsys.readouterr().out


def test_ignores_bad_names_and_ma(tmp_path):
    write(tmp_path, "2026-10-22", [("bad", "unreachable"), ("A03", "unreachable")])
    (tmp_path / "cost-recheck-notadate-flags.csv").write_text(HDR + "A09,x,y,1,unreachable\n")
    assert s.streaks(s.load_runs(str(tmp_path))) == {"A03": (1, "2026-10-22")}


def test_read_only(tmp_path):
    fixture(tmp_path)
    before = sorted(p.name for p in tmp_path.iterdir())
    s.main(["--dir", str(tmp_path)])
    assert sorted(p.name for p in tmp_path.iterdir()) == before


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
    assert s.streaks(s.load_runs(str(tmp_path))) == {"A07": (1, "2026-10-21")}
    text = s.build_report(str(tmp_path), min_days=1, as_of=dt.date(2026, 10, 22))
    assert "WARN unreachable_streak A07 day 1 (since 2026-10-21)" in text
    assert "UNUSABLE cost-recheck-2026-10-22-flags.csv: empty file" in text
    assert "OK no unreachable streaks" not in text


def test_header_only_file_is_a_real_clean_day(tmp_path):
    _flags(tmp_path / "cost-recheck-2026-10-21-flags.csv", [("A07", "unreachable")])
    (tmp_path / "cost-recheck-2026-10-22-flags.csv").write_text("ma,flag\n", encoding="utf-8")
    assert s.streaks(s.load_runs(str(tmp_path))) == {}
    text = s.build_report(str(tmp_path), as_of=dt.date(2026, 10, 22))
    assert "latest_run 2026-10-22 runs_read 2" in text
    assert "OK no unreachable streaks" in text
    assert "UNUSABLE" not in text and "STALE" not in text


def test_bad_date_is_not_the_latest_run(tmp_path):
    _flags(tmp_path / "cost-recheck-2026-10-22-flags.csv", [("A07", "unreachable")])
    _flags(tmp_path / "cost-recheck-2026-99-99-flags.csv", [("A01", "unreachable")])
    runs = s.load_runs(str(tmp_path))
    assert [d for d, _ in runs] == ["2026-10-22"]
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
    assert s.load_runs(str(tmp_path)) == [("2026-10-22", {"A07"})]


def test_missing_folder_and_future_file(tmp_path, capsys):
    missing = tmp_path / "no-such-folder"
    assert s.build_report(str(missing), as_of=dt.date(2026, 10, 22)) == (
        "MISSING cost-recheck folder (no cost-recheck flag files found)\n")
    _flags(tmp_path / "cost-recheck-2026-10-22-flags.csv", [("A06", "loss")])
    text = s.build_report(str(tmp_path), as_of=dt.date(2026, 10, 20))
    assert "NOTE latest cost-recheck flags 2026-10-22 are after 2026-10-20" in text
    assert "STALE" not in text
    assert s.main(["--dir", str(tmp_path), "--as-of", "2026-99-99"]) == 2
    err = capsys.readouterr().err
    assert "YYYY-MM-DD" in err


def test_cli_matches_golden(tmp_path, capsys):
    _flags(tmp_path / "cost-recheck-2026-10-16-flags.csv", [("A07", "unreachable")])
    _flags(tmp_path / "cost-recheck-2026-10-20-flags.csv", [("A07", "unreachable"), ("D01", "loss")])
    (tmp_path / "cost-recheck-2026-10-21-flags.csv").write_bytes(b"")
    _flags(tmp_path / "cost-recheck-2026-99-99-flags.csv", [("A09", "unreachable")])
    assert s.main(["--dir", str(tmp_path), "--min-days", "2", "--as-of", "2026-10-22"]) == 0
    out = capsys.readouterr().out
    assert out == (GOLDEN / "cost_recheck_streak_stale.txt").read_text(encoding="utf-8")
    assert str(tmp_path) not in out
