"""Piece 71 placeholder tests: 'What it does' from commit subject / PROOF.md first line."""
import draft_review_guide as g


def test_strips_piece_prefix_and_fixup():
    assert g.clean_description("Piece 99: add a widget check") == "Add a widget check."
    assert g.clean_description("fixup! Piece 99: drop stale hosts") == "Drop stale hosts."
    assert g.clean_description("# Piece 99 — summary fixes (draft only)") == "Summary fixes (draft only)."


def test_keeps_identifiers_and_caps_length():
    assert "privacy_scan.py" in g.clean_description("Piece 99: wire privacy_scan.py in")
    d = g.clean_description("Piece 99: " + "word " * 80)
    assert len(d) <= g.DESC_MAX and d.endswith("\u2026") and "\n" not in d


def test_one_line_only():
    assert g.clean_description("Piece 99: first line\nsecond line") == "First line."


def test_empty_or_bare_heading_gives_none(tmp_path):
    assert g.clean_description("") == "" and g.clean_description("# Piece 99 proof") == ""
    assert g.describe(99, "", None) is None


def test_subject_then_proof_fallback(tmp_path):
    d = tmp_path / "99-x"
    (d / "proof").mkdir(parents=True)
    (d / "proof" / "PROOF.md").write_text("\n# Piece 99: placeholder proof line\n")
    assert g.describe(99, "Piece 99: from the subject", str(d)) == "From the subject."
    assert g.describe(99, "", str(d)) == "Placeholder proof line."
    assert g.describe(50, "Piece 50: ignored", str(d)) == g.NOTES[50][0]


def test_render_uses_desc():
    p = dict(folder="99-x", commit="abc", branch="draft/99-x", base="main", tests=1,
             privacy="CLEAN", live=[], readonly=False, included=None, desc="Placeholder.")
    t = g.render([p], [])
    assert "What it does: Placeholder." in t and "no description recorded" not in t
