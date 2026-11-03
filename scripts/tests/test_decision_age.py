"""Piece 107: first-raised date + days open per Boss decision (placeholder data built at runtime)."""
import importlib.util
import sys
from pathlib import Path

S = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(S))
import boss_decisions as bd  # noqa: E402

spec = importlib.util.spec_from_file_location("dsd107", S / "daily_summary_draft.py")
ds = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ds)

Q = bd.QUESTIONS["hold_call"]


def _row(ma, q=Q):
    return f"- {ma} | {q} | x/{ma.lower()}.md | ?\n"


def _put(root, sub, date, rows):
    p = root / sub / date / "BOSS-DECISIONS.md"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text("# t\n\n" + "".join(rows), encoding="utf-8")


def _dec(ma, cat="hold_call"):
    return {"cat": cat, "ma": ma, "q": bd.QUESTIONS[cat], "ev": "x", "since": None, "days": None}


def test_earliest_report_or_archive_wins(tmp_path):
    _put(tmp_path, "out/reports", "2000-01-05", [_row("Z01")])
    _put(tmp_path, "out/archive", "2000-01-03", [_row("Z01")])
    _put(tmp_path, "out/reports", "2000-01-09", [_row("Z01")])  # future: ignored
    m = bd.first_raised_map(tmp_path, "2000-01-08")
    assert m[("Z01", Q)] == "2000-01-03"


def test_new_today_when_absent_or_only_today(tmp_path):
    _put(tmp_path, "out/reports", "2000-01-08", [_row("Z02")])
    D = bd.apply_first_raised([_dec("Z02"), _dec("Z03")], tmp_path, "2000-01-08")
    assert all(d["raised"] is None for d in D)
    assert bd.raised_text(D[0]) == "new today"


def test_key_is_ma_and_question(tmp_path):
    _put(tmp_path, "out/reports", "2000-01-01", [_row("Z04", "Other question?")])
    D = bd.apply_first_raised([_dec("Z04")], tmp_path, "2000-01-08")
    assert D[0]["raised"] is None


def test_compile_sorts_oldest_first_and_renders(tmp_path):
    digest = ("- [hold_call] Z05 first_seen=? source=x/a.md\n"
              "- [hold_call] Z06 first_seen=? source=x/a.md\n"
              "- [hold_call] Z07 first_seen=? source=x/a.md\n")
    _put(tmp_path, "out/reports", "2000-01-02", [_row("Z06")])
    _put(tmp_path, "out/archive", "2000-01-04", [_row("Z05")])
    D = bd.compile_decisions(tmp_path, "2000-01-08", digest)
    assert [d["ma"] for d in D] == ["Z06", "Z05", "Z07"]
    t = bd.render(D, "2000-01-08")
    assert "| first raised 2000-01-02 (6d open)" in t
    assert "Z07 | " in t and t.split("Z07")[1].split("\n")[0].endswith("| new today")


def test_summary_section_shows_age_oldest_first(tmp_path):
    digest = "".join(f"- [hold_call] {m} first_seen=? source=x/a.md\n" for m in ("Z08", "Z09"))
    _put(tmp_path, "out/archive", "2000-01-01", [_row("Z09")])
    D = bd.compile_decisions(tmp_path, "2000-01-08", digest)
    f = tmp_path / "today.md"
    f.write_text(bd.render(D, "2000-01-08"), encoding="utf-8")
    L = ds.decision_lines(f, set(), "full.md")
    assert L[0] == "Boss decisions (2 open, oldest first):"
    assert L[1].startswith("- Z09 ") and L[1].endswith("| open 7 days (since 2000-01-01)")
    assert L[2].startswith("- Z08 ") and L[2].endswith("| open ? days (no dated source)")


def test_old_format_lines_still_parse(tmp_path):
    f = tmp_path / "old.md"
    f.write_text("- Z10 | Hold call needed. | x/c.md | 5d (since 1999-12-27)\n", encoding="utf-8")
    L = ds.decision_lines(f, set(), "full.md")
    assert L[0] == "Boss decisions (1 open):"
    assert L[1] == "- Z10 | Hold call needed. | x/c.md | 5d"


def test_read_only(tmp_path):
    _put(tmp_path, "out/reports", "2000-01-02", [_row("Z11")])
    before = sorted(p for p in tmp_path.rglob("*"))
    bd.first_raised_map(tmp_path, "2000-01-08")
    assert sorted(p for p in tmp_path.rglob("*")) == before
