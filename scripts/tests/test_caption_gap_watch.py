"""Piece 48 caption_gap_watch: synthetic fixtures only, no network, no Meta."""
import json
import socket

import pytest

import caption_gap_watch as g
import daily_shop_check as d

POSTS = [
    {"id": "1476862711014662", "platform": "fb", "caption": ""},
    {"id": "100001", "platform": "fb", "caption": "Mã G01\nÁo xinh"},
    {"id": "100002", "platform": "ig", "caption": "Mã H02\nSize M"},
    {"id": "100003", "platform": "fb", "caption": "Mã A08\nGiá $29"},
    {"id": "100004", "platform": "fb", "caption": "Mã A08\nGiá $31"},
    {"id": "100005", "platform": "ig", "caption": "Đầm đẹp\nGiá $20"},
    {"id": "100006", "platform": "fb", "caption": "Mã S06\nGiá $24"},
    {"id": "100007", "platform": "fb", "caption": "Mã S15\nGiá $30"},
]
LIVE = {"A08": 29, "S06": 25}
APPROVED = {"approvedGia": {"S15": 30}}


@pytest.fixture(autouse=True)
def no_net(monkeypatch):
    def boom(*a, **k):
        raise AssertionError("network used")
    monkeypatch.setattr(socket, "create_connection", boom)
    monkeypatch.setattr(socket.socket, "connect", boom)


def files(tmp_path):
    e = tmp_path / "posts.json"; e.write_text(json.dumps(POSTS, ensure_ascii=False), encoding="utf-8")
    l = tmp_path / "live.json"; l.write_text(json.dumps(LIVE))
    a = tmp_path / "approved.json"; a.write_text(json.dumps(APPROVED))
    return e, l, a


def rep(tmp_path):
    e, l, a = files(tmp_path)
    return g.run(g.load_posts(e), g.load_prices(l, a))


def test_known_reel_no_caption(tmp_path):
    assert {"post": "1476862711014662", "ma": None, "issue": "missing_caption"} in rep(tmp_path)["flags"]


def test_g01_h02_no_gia(tmp_path):
    r = rep(tmp_path)
    assert {"post": "100001", "ma": "G01", "issue": "missing_gia"} in r["flags"]
    assert {"post": "100002", "ma": "H02", "issue": "missing_gia"} in r["flags"]


def test_gia_differs_and_match(tmp_path):
    r = rep(tmp_path)
    assert r["byIssue"]["gia_differs"] == ["100004", "100006"]
    assert not [f for f in r["flags"] if f["post"] in ("100003", "100007")]


def test_missing_ma(tmp_path):
    assert rep(tmp_path)["byIssue"]["missing_ma"] == ["100005"]


def test_s06_locked_even_if_list_says_otherwise(tmp_path):
    l = tmp_path / "l.json"; l.write_text(json.dumps({"S06": 24}))
    assert g.load_prices(l)["S06"] == 25.0


def test_output_fields_only(tmp_path):
    for f in rep(tmp_path)["flags"]:
        assert set(f) == {"post", "ma", "issue"}


def test_never_suggests_delete_or_repost(tmp_path):
    r = rep(tmp_path)
    txt = (json.dumps(r) + g.markdown(r)).lower()
    assert "delete" not in txt and "repost" not in txt
    assert r["writes"] == "none" and r["network"] == "none"


def test_caption_text_not_echoed(tmp_path):
    txt = json.dumps(rep(tmp_path), ensure_ascii=False)
    assert "Áo xinh" not in txt and "Đầm đẹp" not in txt


def test_text_export(tmp_path):
    t = tmp_path / "posts.txt"
    t.write_text("=== 1476862711014662 fb\n\n=== 200001 ig\nMã A08\nGiá $29\n", encoding="utf-8")
    r = g.run(g.load_posts(t), {"A08": 29.0})
    assert r["posts"] == 2 and [f["issue"] for f in r["flags"]] == ["missing_caption"]


def test_bad_id_sanitized():
    r = g.run([{"id": "https://x.example/a b", "caption": ""}], {})
    assert r["flags"][0]["post"] == "invalid_id"


def test_main_exit_codes(tmp_path, capsys):
    e, l, a = files(tmp_path)
    assert g.main([str(e), "--live", str(l), "--approved", str(a)]) == 1
    ok = tmp_path / "ok.json"; ok.write_text(json.dumps([{"id": "1", "caption": "Mã A08\nGiá $29"}], ensure_ascii=False), encoding="utf-8")
    assert g.main([str(ok), "--live", str(l)]) == 0
    bad = tmp_path / "bad.json"; bad.write_text("{not json")
    assert g.main([str(bad)]) == 2


def test_main_json(tmp_path, capsys):
    e, l, a = files(tmp_path)
    g.main([str(e), "--live", str(l), "--approved", str(a), "--json"])
    assert json.loads(capsys.readouterr().out)["schema"] == "caption-gap-watch/v1"


def test_daily_section_warn_never_fail(tmp_path):
    e, l, a = files(tmp_path)
    ns = type("A", (), {"caption_gaps": e, "caption_gaps_live": l, "caption_gaps_approved": a})()
    sec = d.caption_gaps_section(ns)
    assert sec["name"] == "caption_gaps" and sec["status"] == "WARN" and not sec["fail"]
    assert "1476862711014662 -: missing_caption" in sec["warn"]


def test_daily_section_bad_input_warns(tmp_path):
    bad = tmp_path / "bad.json"; bad.write_text("{not json")
    ns = type("A", (), {"caption_gaps": bad, "caption_gaps_live": None, "caption_gaps_approved": None})()
    sec = d.caption_gaps_section(ns)
    assert sec["status"] == "WARN" and not sec["fail"]
