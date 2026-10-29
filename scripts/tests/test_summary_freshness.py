"""Piece 84 placeholder tests: Data freshness section (temp files only)."""
import datetime as dt
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import daily_summary_draft as d  # noqa: E402

NOW = dt.datetime(2026, 1, 2, 12, 0, tzinfo=dt.timezone.utc)


def _touch(p, hours_ago):
    p.write_text("placeholder\n")
    t = (NOW - dt.timedelta(hours=hours_ago)).timestamp()
    os.utime(p, (t, t))
    return p


def test_ok_stale_missing(tmp_path):
    fresh = _touch(tmp_path / "a.json", 1)
    old = _touch(tmp_path / "b.json", 30)
    L = d.freshness_lines([("A", fresh), ("B", old), ("C", tmp_path / "none.json")], now=NOW)
    assert L[1].startswith("- A: OK, a.json file time ")
    assert L[1].endswith(" PT")
    assert L[2].startswith("- B: STALE")
    assert L[3] == "- C: MISSING (none.json)"


def test_pt_time(tmp_path):
    p = _touch(tmp_path / "a.json", 0)  # 12:00 UTC on Jan 2 = 04:00 PST
    assert "2026-01-02 04:00 PT" in d.freshness_lines([("A", p)], now=NOW)[1]


def test_five_inputs_and_contents_not_read(tmp_path):
    ins = d.freshness_inputs(tmp_path, "2026-01-02")
    assert [x[0] for x in ins] == ["Blob catalog snapshot", "Intake", "Meta QC json",
                                   "Cost-basis report", "Popular order"]
    secret = tmp_path / "x.json"
    secret.write_text("PLACEHOLDER-SECRET")
    text = "\n".join(d.freshness_lines([("X", secret)], now=NOW))
    assert "PLACEHOLDER-SECRET" not in text


def test_section_in_build():
    t = d.build(None, None, {}, None, None, None, None, "2026-01-02",
                freshness=["Data freshness (x):", "- A: MISSING (a.json)"])
    assert "Data freshness" in t and "- A: MISSING (a.json)" in t
    assert "Data freshness" not in d.build(None, None, {}, None, None, None, None, "2026-01-02")
