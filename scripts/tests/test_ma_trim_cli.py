"""Piece 185: padded mã codes (' K03 ') behave exactly like clean ones at the CLI level."""
import json

import caption_lint
import held_price_proposal
import meta_caption_gap_report
import meta_inventory
import popular_order_gaps


def _w(path, obj):
    path.write_text(json.dumps(obj), encoding="utf-8")
    return path


def _caption_lint_run(tmp_path, capsys, pad):
    p = (lambda c: f" {c} ") if pad else (lambda c: c)
    caps = _w(tmp_path / "caps.json", [
        {"url": "u1", "platform": "fb", "text": "Mã K03\nGiá $52"},
        {"url": "u2", "platform": "ig", "text": "Mã Z99\nGiá $10"},
        {"url": "u3", "platform": "fb", "text": "Mã A01\nGiá $20"},
    ])
    live = _w(tmp_path / "live.json", {"prices": {"A01": 20}})
    held = _w(tmp_path / f"held{pad}.json", {"heldIncomplete": [p("K03")], "neverList": [p("Z99")]})
    appr = _w(tmp_path / f"appr{pad}.json", {"approvedGia": {p("K03"): 52}})
    caption_lint.main([str(caps), "--live", str(live), "--held", str(held), "--approved", str(appr), "--json"])
    return json.loads(capsys.readouterr().out)


def test_caption_lint_main_padded_held_never_approved(tmp_path, capsys):
    assert _caption_lint_run(tmp_path, capsys, True) == _caption_lint_run(tmp_path, capsys, False)


def _pog_run(tmp_path, capsys, pad):
    p = (lambda c: f" {c} ") if pad else (lambda c: c)
    cat = _w(tmp_path / f"cat{pad}.json", {"products": [
        {"ma": p("A01"), "status": "available", "type": "top"},
        {"ma": p("A05"), "status": "available", "type": "top"},
    ]})
    order = _w(tmp_path / "order.json", {"order": ["S01", "A01", "S02"]})
    popular_order_gaps.main(["--order", str(order), "--catalog", str(cat), "--plan"])
    return capsys.readouterr().out


def test_popular_order_gaps_plan_padded_catalog(tmp_path, capsys):
    clean = _pog_run(tmp_path, capsys, False)
    assert "end of type top group" in clean
    assert _pog_run(tmp_path, capsys, True) == clean


def test_held_price_only_matches_padded_row(tmp_path):
    intake = _w(tmp_path / "i.json", [{"ma": " K03 ", "kind": "K", "cost" + "_cny": str(10 * 10), "kg": "0.3"}])
    live = _w(tmp_path / "l.json", {"prices": {}})
    held = _w(tmp_path / "h.json", {"heldIncomplete": ["K03"], "neverList": []})
    out = tmp_path / "o.json"
    assert held_price_proposal.main(["--intake", str(intake), "--live", str(live), "--held", str(held),
                                     "--only", "K03", "--out-json", str(out)]) == 0
    assert "K03" in out.read_text(encoding="utf-8")


def test_meta_inventory_load_held_padded(tmp_path):
    p = _w(tmp_path / "h.json", {"heldIncomplete": [" K03 "], "neverList": ["z99 "]})
    assert meta_inventory.load_held(p) == ({"K03"}, {"Z99"})


def test_meta_caption_gap_load_live_padded(tmp_path):
    p = _w(tmp_path / "c.json", {"products": [{"ma": " a01 ", "status": "available"}]})
    assert meta_caption_gap_report.load_live([], p) == {"A01"}
