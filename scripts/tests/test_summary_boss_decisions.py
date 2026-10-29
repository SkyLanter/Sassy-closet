"""Piece 91: placeholder tests for the 'Boss decisions' summary section (made-up data only)."""
import importlib.util
from pathlib import Path

spec = importlib.util.spec_from_file_location(
    "dsd", Path(__file__).resolve().parents[1] / "daily_summary_draft.py")
d = importlib.util.module_from_spec(spec)
spec.loader.exec_module(d)

FILE = """# Boss decisions 2000-01-01 (DRAFT)

- Z01 | Hold it? Newly gone on Taobao and still live. | x/a.json | 1d (since 1999-12-31)
- Z02 | Needs a price (held). Approve one? | x/b.md | 0d (since 2000-01-01)
- Z02 | Needs a price (held). Approve one? | x/b.md | 0d (since 2000-01-01)
- Z03 | Hold call needed. | x/c.md | 5d (since 1999-12-27)
- - | Meta QC not PASS on both sides. Sign-in/recheck needed? | x/d.json (missing) | ?

TOTAL 5
"""


def _f(tmp_path, text=FILE):
    p = tmp_path / "BOSS-DECISIONS.md"
    p.write_text(text, encoding="utf-8")
    return p


def test_missing_file_says_missing(tmp_path):
    L = d.decision_lines(tmp_path / "nope.md", set(), "out/reports/x/BOSS-DECISIONS.md")
    assert L[0] == "Boss decisions: MISSING"
    assert "MISSING" in L[-1]


def test_dedupes_exact_repeats_and_sorts_by_days(tmp_path):
    L = d.decision_lines(_f(tmp_path), set(), "full.md")
    assert L[0] == "Boss decisions (4 open):"
    assert L[1].startswith("- Z03 ")
    assert L[-2].startswith("- - |")
    assert L[-1] == "- Full list: full.md"


def test_skips_items_already_in_summary(tmp_path):
    L = d.decision_lines(_f(tmp_path), {("Z01", "gone"), ("-", "meta")}, "full.md")
    assert L[0] == "Boss decisions (2 open):"
    assert not any("Z01" in x for x in L)
    assert "- 2 already listed above under 'Waiting on you'" in L


def test_caps_at_twelve(tmp_path):
    rows = "".join(f"- Y{i:02d} | Hold call needed. | x/c.md | {i}d (since 1999-01-01)\n"
                   for i in range(15))
    L = d.decision_lines(_f(tmp_path, rows), set(), "full.md")
    assert L[0] == "Boss decisions (15 open):"
    assert L[1].startswith("- Y14 ")
    assert "- ...3 more" in L


def test_build_includes_section_and_dedupes(tmp_path):
    t = d.build(None, {"persistent_new_unreachable": ["Z01"]}, {}, None, None,
                None, None, "2000-01-01", decisions=_f(tmp_path), decisions_rel="full.md")
    sec = t.split("Boss decisions (")[1]
    assert "Z01" not in sec and "Z03" in sec
