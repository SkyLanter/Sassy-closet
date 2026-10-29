"""Piece 99: grouped 'Waiting on you' lines cover each listed mã in 'Boss decisions'
(placeholder mãs only)."""
import importlib.util
from pathlib import Path

spec = importlib.util.spec_from_file_location(
    "dsd99", Path(__file__).resolve().parents[1] / "daily_summary_draft.py")
d = importlib.util.module_from_spec(spec)
spec.loader.exec_module(d)

Q = {
    "popular_order_held": "Held mã in popular order. Remove it?",
    "flip_under": "Under the price formula at Nhung's intake cost (OK at baseline cost). Flag/decide price?",
    "price_approval": "Needs a price (held). Approve one?",
    "pr": "Boss-gated PR still open. Merge or close?",
}


def _f(tmp_path, rows):
    p = tmp_path / "BOSS-DECISIONS.md"
    p.write_text("# Boss decisions 2000-01-01\n\n" + "".join(
        f"- {m} | {q} | x/e.md | ?\n" for m, q in rows), encoding="utf-8")
    return p


def _sec(t):
    return t.split("Boss decisions (")[1].split("Full list")[0]


def test_held_order_question_maps_to_kind():
    assert d.dec_kind(Q["popular_order_held"]) == "popular_order_held"


def test_grouped_held_order_line_covers_each_ma(tmp_path):
    rows = [(m, Q["popular_order_held"]) for m in ("Z91", "Z92", "Z93")] + [("PR #9", Q["pr"])]
    t = d.build(None, {}, {}, None, None, None, None, "2000-01-01",
                held_order=["Z91", "Z92", "Z93"], decisions=_f(tmp_path, rows), decisions_rel="f.md")
    assert "Remove held mãs from popular order? Z91, Z92, Z93" in t
    sec = _sec(t)
    assert sec.startswith("1 open):")
    assert "PR #9" in sec and "Z9" not in sec.split("already listed")[0]
    assert "3 already listed above" in sec


def test_held_ma_not_in_grouped_line_stays(tmp_path):
    rows = [(m, Q["popular_order_held"]) for m in ("Z91", "Z92")]
    t = d.build(None, {}, {}, None, None, None, None, "2000-01-01",
                held_order=["Z91"], decisions=_f(tmp_path, rows), decisions_rel="f.md")
    sec = _sec(t)
    assert sec.startswith("1 open):") and "Z92" in sec


def test_flip_other_covers_price_formula_question(tmp_path):
    rows = [("Z81", Q["flip_under"])]
    t = d.build(None, {}, {}, None, None, None, None, "2000-01-01",
                flips={"Z81": ("OK", "UNDER")}, decisions=_f(tmp_path, rows), decisions_rel="f.md")
    assert "Price verdict depends on cost source: Z81" in t
    assert _sec(t).startswith("0 open):")


def test_proposal_lines_cover_needs_price(tmp_path):
    rows = [("Z71", Q["price_approval"]), ("Z72", Q["price_approval"]), ("Z73", Q["price_approval"])]
    prop = {"verdicts": {"Z71": "$" + "30", "Z72": "NEEDS_INPUT"}}
    t = d.build(None, {}, {}, None, prop, None, None, "2000-01-01",
                decisions=_f(tmp_path, rows), decisions_rel="f.md")
    sec = _sec(t)
    assert sec.startswith("1 open):") and "Z73" in sec
    assert "Z71" not in sec.split("already listed")[0]


def test_every_grouped_kind_question_maps(tmp_path):
    """Audit: each question with a grouped Waiting line resolves to a DEC_KINDS kind."""
    import importlib
    bd_spec = importlib.util.spec_from_file_location(
        "bd99", Path(__file__).resolve().parents[1] / "boss_decisions.py")
    bd = importlib.util.module_from_spec(bd_spec)
    bd_spec.loader.exec_module(bd)
    for key, q in bd.QUESTIONS.items():
        if key == "pr":
            assert d.dec_kind(q) is None
        else:
            assert d.dec_kind(q) is not None, key
