import subprocess, sys
from pathlib import Path
import pytest
import muse_pace as mp

HERE = Path(__file__).parent
FX = HERE / "fixtures" / "pace"


def test_expected_44pct():
    exp, start, end = mp.expected_pct(mp.parse_now("2026-10-15T02:49Z"), "2026-10-19", 7)
    assert 44.0 <= exp < 45.0
    assert start.day == 12 and end.day == 19


def test_clamps():
    assert mp.expected_pct(mp.parse_now("2026-10-25T00:00Z"), "2026-10-19")[0] == 100.0
    assert mp.expected_pct(mp.parse_now("2026-10-01T00:00Z"), "2026-10-19")[0] == 0.0


def test_backlog_states():
    items = mp.parse_backlog((FX / "backlog_basic.md").read_text())
    assert [i[2] for i in items] == ["partial", "open", "open"]
    assert mp.next_item(items)[0] == 1  # PARTIAL stays open


def test_next_skips_done_and_handles_all_done():
    items = mp.parse_backlog((FX / "backlog_first_done.md").read_text())
    assert mp.next_item(items)[0] == 2
    assert mp.next_item(mp.parse_backlog((FX / "backlog_all_done.md").read_text())) is None


def test_real_backlog_parses_8_items_if_present():
    p = mp.DEFAULT_BACKLOG
    if not p.exists():
        pytest.skip("real backlog not present")
    items = mp.parse_backlog(p.read_text(encoding="utf-8"))
    assert [i[0] for i in items] == list(range(1, 9))


def run(*args):
    return subprocess.run([sys.executable, str(HERE / "muse_pace.py"), *args], capture_output=True, text=True)


def test_cli_behind():
    r = run("--used-pct", "0", "--reset-date", "2026-10-19", "--now", "2026-10-15T02:49Z",
            "--week-days", "7", "--backlog", str(FX / "backlog_basic.md"))
    assert r.returncode == 0, r.stderr
    assert "expected used (straight line): 44.5%" in r.stdout
    assert "BEHIND by 44.5 points" in r.stdout
    assert "#1 IG full sweep table" in r.stdout and "partial" in r.stdout


def test_cli_ahead():
    r = run("--used-pct", "60", "--reset-date", "2026-10-19", "--now", "2026-10-15T02:49Z",
            "--backlog", str(FX / "backlog_first_done.md"))
    assert "AHEAD by 15.5 points" in r.stdout and "#2 Beta" in r.stdout
