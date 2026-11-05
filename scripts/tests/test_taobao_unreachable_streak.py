"""Piece 49 taobao_unreachable_streak: synthetic fixtures only, no network."""
import json
import socket

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


def write_min(tmp_path, date, rows):
    body = "ma,flag\n" + "".join(f"{ma},{fl}\n" for ma, fl in rows)
    (tmp_path / f"cost-recheck-{date}-flags.csv").write_text(body, encoding="utf-8")


def write_summary(tmp_path, date, doc, bom=False):
    raw = json.dumps(doc).encode("utf-8")
    if bom:
        raw = b"\xef\xbb\xbf" + raw
    (tmp_path / f"summary.{date}.json").write_bytes(raw)


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


def test_load_runs_ignores_blocked_sibling_summary(tmp_path):
    write_min(tmp_path, "2026-11-01", [("Z71", "unreachable"), ("Z72", "loss")])
    write_min(tmp_path, "2026-11-02", [("Z72", "unreachable")])
    write_summary(tmp_path, "2026-11-02", {"taobao_login_needed": True})
    runs = s.load_runs(str(tmp_path))
    assert runs == [("2026-11-01", {"Z71"})]
    assert isinstance(runs, list)
    assert isinstance(runs[0], tuple)
    assert isinstance(runs[0][1], set)


def test_blocked_day_between_usable_runs_does_not_count_or_break(tmp_path, capsys):
    write_min(tmp_path, "2026-11-01", [("Z71", "unreachable")])
    write_min(tmp_path, "2026-11-02", [("Z71", "unreachable"), ("Z72", "unreachable")])
    write_min(tmp_path, "2026-11-03", [("Z71", "unreachable")])
    write_summary(tmp_path, "2026-11-02", {"taobao_login_needed": " YES "})
    write_summary(tmp_path, "2026-11-03", {"taobao_login_needed": "false"})
    runs, blocked = s.partition_runs(str(tmp_path))
    assert blocked == ["2026-11-02"]
    assert runs == [("2026-11-01", {"Z71"}), ("2026-11-03", {"Z71"})]
    assert s.load_runs(str(tmp_path)) == runs
    assert s.streaks(runs) == {"Z71": (2, "2026-11-01")}
    rc = s.main(["--dir", str(tmp_path)])
    out = capsys.readouterr().out
    assert rc == 0
    assert out.splitlines() == [
        "latest_run 2026-11-03 runs_read 2 blocked_runs 1",
        "WARN unreachable_streak Z71 day 2 (since 2026-11-01)",
    ]


def test_newest_blocked_warns_from_older_usable_run(tmp_path, capsys):
    write_min(tmp_path, "2026-11-01", [("Z71", "unreachable")])
    write_min(tmp_path, "2026-11-02", [("Z71", "unreachable"), ("Z72", "unreachable")])
    write_summary(tmp_path, "2026-11-02", {"taobao_login_needed": 1})
    rc = s.main(["--dir", str(tmp_path), "--min-days", "1"])
    out = capsys.readouterr().out
    assert rc == 0
    assert out.splitlines() == [
        "latest_run 2026-11-01 runs_read 1 blocked_runs 1",
        "WARN unreachable_streak Z71 day 1 (since 2026-11-01)",
    ]


def test_all_dated_runs_blocked(tmp_path, capsys):
    dates = ("2026-11-01", "2026-11-02")
    write_min(tmp_path, dates[0], [("Z71", "unreachable")])
    write_min(tmp_path, dates[1], [("Z72", "unreachable")])
    write_summary(tmp_path, dates[0], {"taobao_login_needed": True})
    write_summary(tmp_path, dates[1], {"taobao_login_needed": "y"})
    rc = s.main(["--dir", str(tmp_path)])
    out = capsys.readouterr().out
    assert rc == 0
    assert out.strip() == (
        f"OK signed-out block on {len(dates)} cost-recheck run(s); unreachable flags not used"
    )
    assert "Z71" not in out
    assert "Z72" not in out


def test_missing_summary_and_bad_json_still_count(tmp_path):
    write_min(tmp_path, "2026-11-01", [("Z71", "unreachable")])
    write_min(tmp_path, "2026-11-02", [("Z72", "unreachable")])
    (tmp_path / "summary.2026-11-02.json").write_text("{", encoding="utf-8")
    assert s.load_runs(str(tmp_path)) == [
        ("2026-11-01", {"Z71"}),
        ("2026-11-02", {"Z72"}),
    ]


def test_float_one_blocks_and_false_words_do_not(tmp_path):
    write_min(tmp_path, "2026-11-01", [("Z71", "unreachable")])
    write_min(tmp_path, "2026-11-02", [("Z71", "unreachable"), ("Z72", "unreachable")])
    write_min(tmp_path, "2026-11-03", [("Z71", "unreachable")])
    write_summary(tmp_path, "2026-11-02", {"taobao_login_needed": 1.0})
    write_summary(tmp_path, "2026-11-03", {"taobao_login_needed": " NO "})
    runs, blocked = s.partition_runs(str(tmp_path))
    assert blocked == ["2026-11-02"]
    assert runs == [("2026-11-01", {"Z71"}), ("2026-11-03", {"Z71"})]
    assert s.streaks(runs) == {"Z71": (2, "2026-11-01")}


def test_utf8_bom_on_summary_still_blocks(tmp_path):
    write_min(tmp_path, "2026-11-01", [("Z71", "unreachable")])
    write_summary(tmp_path, "2026-11-01", {"taobao_login_needed": True}, bom=True)
    runs, blocked = s.partition_runs(str(tmp_path))
    assert runs == []
    assert blocked == ["2026-11-01"]
    assert s.load_runs(str(tmp_path)) == []
