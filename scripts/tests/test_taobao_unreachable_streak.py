"""Piece 49 taobao_unreachable_streak: synthetic fixtures only, no network."""
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
