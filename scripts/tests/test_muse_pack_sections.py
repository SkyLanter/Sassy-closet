import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import boss_decisions_digest as bdd  # noqa: E402
import muse_pack_sections as m  # noqa: E402

LINK = "https://example.invalid/item?id=1"


def _root(tmp_path):
    (tmp_path / "out").mkdir()
    (tmp_path / "verify").mkdir()
    return tmp_path


def _intake(tmp_path):
    p = tmp_path / "intake.json"
    p.write_text(json.dumps({"submissions": [
        {"ma": "Z01", "created_at": "2000-01-01", "title": "dress", "link": LINK},
        {"ma": "Z01", "created_at": "2000-02-01", "title": "skirt", "link": LINK},
        {"ma": "Z02", "created_at": "2000-01-01", "title": "top"}]}))
    return [p]


def test_reuse_section_codes_only(tmp_path):
    s = m.build(_root(tmp_path), _intake(tmp_path))
    md = m.render_md(s)
    assert "Z01×2" in md and "1 reused of 3 rows" in md
    for bad in ("example.invalid", "dress", "skirt"):
        assert bad not in md and bad not in m.render_msg(s)


def test_failing_tool_marks_unavailable(tmp_path, monkeypatch):
    def boom(*a, **k):
        raise RuntimeError("x")
    monkeypatch.setattr(m, "section_captions", boom)
    s = m.build(_root(tmp_path), _intake(tmp_path))
    assert "unavailable (RuntimeError)" in m.render_md(s)
    assert "Caption gaps: unavailable" in m.render_msg(s)
    assert "Z01" in m.render_md(s)


def test_missing_intake_unavailable(tmp_path):
    s = m.build(_root(tmp_path), [])
    assert "Reused intake codes: unavailable" in m.render_msg(s)


def test_sanitizers():
    assert m._ma("a03") == "A03" and m._ma("http://x") == "?"
    assert m._pid("1476") == "1476" and m._pid("caption text here") == "?"


def test_apply_idempotent_and_before_signature(tmp_path):
    s = m.build(_root(tmp_path), _intake(tmp_path))
    t, msg = tmp_path / "TODAY.md", tmp_path / "msg.txt"
    t.write_text("# Pack\nbody\n")
    msg.write_text("hello\n- Mini Boss\n")
    m.apply(t, msg, s)
    m.apply(t, msg, s)
    assert t.read_text().count(m.START) == 1
    lines = msg.read_text().strip().split("\n")
    assert lines[-1] == "- Mini Boss" and msg.read_text().count(m.MSG_START) == 1


def test_main_prints_without_write(tmp_path, capsys):
    root = _root(tmp_path)
    assert m.main(["--root", str(root), "--intake", str(_intake(tmp_path)[0])]) == 0
    assert "Open Boss decisions" in capsys.readouterr().out


def _price_root(tmp_path):
    root = _root(tmp_path)
    extras = root / "out/muse/extras-2026-04-01.md"
    extras.parent.mkdir(parents=True)
    extras.write_text("X07 needs a Boss price\n")
    return root


def test_section_decisions_includes_popular_order_held(tmp_path, monkeypatch):
    root = _price_root(tmp_path)
    order = tmp_path / "order.json"
    held = tmp_path / "held.json"
    order.write_text(json.dumps({
        "order": ["Z91", "Z92"],
        "method": "SECRET_METHOD_TEXT",
    }))
    held.write_text(json.dumps({"held": ["Z91"], "reason": "SECRET_HELD_REASON"}))
    monkeypatch.setattr(bdd, "repo_order_held_paths", lambda: (order, held))
    sec = m.section_decisions(root)
    assert set(sec["by_cat"]) == {"popular_order_held", "price_approval"}
    assert sec["by_cat"]["popular_order_held"] == ["Z91"]
    assert sec["by_cat"]["price_approval"] == ["X07"]
    assert sec["total"] == sum(len(v) for v in sec["by_cat"].values())
    dumped = json.dumps(sec)
    assert "SECRET_METHOD_TEXT" not in dumped
    assert "SECRET_HELD_REASON" not in dumped
    assert "Z92" not in dumped


def test_section_decisions_held_error_keeps_scanned_ma(tmp_path, monkeypatch):
    root = _price_root(tmp_path)

    def boom(*_args, **_kwargs):
        raise ValueError("bad held json")

    monkeypatch.setattr(bdd, "held_in_popular_order", boom)
    sec = m.section_decisions(root)
    assert sec["by_cat"] == {"price_approval": ["X07"]}
    assert "X07" in sec["by_cat"]["price_approval"]
    assert "popular_order_held" not in sec["by_cat"]
    assert sec["total"] == sum(len(v) for v in sec["by_cat"].values())


def test_caption_rows_ids_or_ma_only(tmp_path, monkeypatch):
    import meta_caption_gap_report as mc
    monkeypatch.setattr(mc, "build", lambda roots, catalog=None: {
        "no_ma": [("fb", "reel", "1000000000000001")],
        "no_gia": [("fb", "post", "ma:Z09"), ("ig", "post", "free caption text!")],
        "live_no_post": {"fb": None, "ig": ["Z01", "Z02"]}})
    md = m.render_md(m.build(_root(tmp_path), []))
    assert "FB reel 1000000000000001" in md and "FB post mã Z09" in md
    assert "free" not in md and "IG post ?" in md
    assert "Live mã with no IG post: 2" in md
