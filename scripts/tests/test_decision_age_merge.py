"""Piece 109: one merged age per Boss decision line. Placeholder data built at runtime."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import daily_summary_draft as ds


def _line(ma, days, since, tail):
    n = "?" if days is None else f"{days}d" + (f" (since {since})" if since else "")
    return f"- {ma} | Hold call needed. | x/{ma}.md | {n}" + (f" | {tail}" if tail else "")


def _sec(tmp_path, lines):
    f = tmp_path / "bd.md"
    f.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return ds.decision_lines(f, set(), "full.md")


def test_source_older_than_raised_wins(tmp_path):
    # the reported bug: '9d | new today' -> one age
    L = _sec(tmp_path, [_line("Z01", 9, "2000-01-01", "new today")])
    assert L[1] == "- Z01 | Hold call needed. | x/Z01.md | open 9 days (since 2000-01-01)"
    assert "new today" not in L[1]


def test_raised_older_than_source_wins(tmp_path):
    L = _sec(tmp_path, [_line("Z02", 2, "2000-01-08", "first raised 2000-01-03 (7d open)")])
    assert L[1].endswith("| open 7 days (since 2000-01-03)")


def test_new_today_only_when_both_today(tmp_path):
    L = _sec(tmp_path, [_line("Z03", 0, "2000-01-10", "new today"),
                        _line("Z04", 1, "2000-01-09", "new today")])
    assert L[2].endswith("| new today") and L[2].startswith("- Z03")
    assert L[1].endswith("| open 1 day (since 2000-01-09)")


def test_unknown_source_uses_raised_or_unknown(tmp_path):
    L = _sec(tmp_path, [_line("Z05", None, None, "first raised 2000-01-05 (5d open)"),
                        _line("Z06", None, None, "new today")])
    assert L[1].endswith("| open 5 days (since 2000-01-05)")
    assert L[2].endswith("| open ? days (no dated source)")


def test_oldest_first_by_merged_age(tmp_path):
    L = _sec(tmp_path, [_line("Z07", 1, "2000-01-09", "new today"),
                        _line("Z08", 2, "2000-01-08", "first raised 2000-01-01 (9d open)")])
    assert L[1].startswith("- Z08") and L[2].startswith("- Z07")


def test_pre107_file_unchanged(tmp_path):
    L = _sec(tmp_path, [_line("Z09", 5, "2000-01-05", None)])
    assert L[0] == "Boss decisions (1 open):"
    assert L[1] == "- Z09 | Hold call needed. | x/Z09.md | 5d"


def test_one_age_per_line(tmp_path):
    L = _sec(tmp_path, [_line("Z10", 4, "2000-01-06", "first raised 2000-01-02 (8d open)")])
    assert L[1].count("|") == 3 and "first raised" not in L[1]
