"""Piece 77 placeholder tests: cost-basis flips + popular_order_held in the daily summary."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import daily_summary_draft as d  # noqa: E402

CB = """| mã | live $ | intake ¥ | baseline ¥ | reprice ¥ | list ¥ | kg | spread % | a | b | c | result |
|---|---|
| Z01 | 1 | 9.00 | 1.00 | 1.00 | | 0.100 | 10.0 | 5 / UNDER | 1 / OK | 1 / OK | FLIP |
| Z02 | 1 | 1.00 | 1.00 | 1.00 | | 0.100 | 0.0 | 1 / OK | 1 / OK | 1 / OK | AGREE |
"""
DIGEST = "- [intake_mismatch] Z01  first_seen=x\n- [popular_order_held] Remove held mãs Z03, Z04 from popular order? (x)\n"


def test_parse_cost_basis_flip_only():
    assert d.parse_cost_basis(CB) == {"Z01": ("UNDER", "OK")}


def test_parse_held_order_codes():
    assert d.parse_held_order(DIGEST) == ["Z03", "Z04"]


def test_build_no_duplicate_and_no_costs():
    qc = {"warns": ["INTAKE_COST_VS_LIVE Z01 under-priced"]}
    t = d.build(qc, None, d.parse_digest(DIGEST), None, None, "pass", "pass", "2026-01-01",
                flips=d.parse_cost_basis(CB), held_order=d.parse_held_order(DIGEST))
    assert t.count("Z01") == 1
    assert "Nhung's intake cost" in t and "Z03, Z04" in t
    assert "popular_order_held" not in t
    assert "9.00" not in t and "¥" not in t and "tesla" not in t.lower()


def test_build_without_new_sources_unchanged_shape():
    t = d.build(None, None, {}, None, None, "pass", "pass", "2026-01-01")
    # piece 80: override pass is single-source -> UNCHECKED, so the day is not cleared
    assert "Mini Boss" in t and "override pass needs Luxubu + Mini Boss record" in t
