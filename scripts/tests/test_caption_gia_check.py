import json

import pytest

import caption_gia_check as c
from held_policy import HeldPolicy

LIVE = {"S13": 26.0, "A02": 23.0, "S06": 25.0, "K01": 36.0, "A11": 27.0}
POL = HeldPolicy(held=("S15", "K04", "A24"), never_list=("Z99",))
APP = {"S15": 30.0, "K04": 101.0}


def run(text, strict=False):
    return c.check_post("p", text, LIVE, POL, APP, strict)


@pytest.mark.parametrize("text,price", [
    ("Mã S13\nGiá: $26", 26), ("Mã S13\nGiá $26", 26), ("Mã S13\nGiá 26$", 26),
    ("Mã S13\ngiá 26 đô", 26), ("Mã S13\nGIÁ $ 26", 26), ("Mã S13\nGia 26 USD", 26),
    ("Mã S13\nGiá: $26.00", 26),
])
def test_vietnamese_formats_pass(text, price):
    r = run(text)
    assert r.gia_usd == price and r.status == "PASS", r


def test_decomposed_unicode_gia():
    import unicodedata
    assert run(unicodedata.normalize("NFD", "Mã S13\nGiá $26")).status == "PASS"


def test_missing_gia_warns():
    r = run("Mã A11\nDép bông")
    assert r.status == "WARN" and "no_gia" in r.issues


def test_gia_word_without_number():
    assert "gia_unparsed" in run("Mã A11\nGiá inbox ạ").issues


def test_wrong_ma_price_fails():
    r = run("Mã A02\nGiá $26")  # S13's price on A02's post
    assert r.status == "FAIL" and "price_mismatch" in r.issues and r.expected_usd == 23


def test_no_ma():
    r = run("WHITE ANGEL SET\nGiá $ 32")
    assert r.ma is None and r.gia_usd == 32 and "no_ma" in r.issues


def test_ma_not_first_line_warn_and_strict():
    t = "ÁO KIỂU VINTAGE\nMã A02\nGiá $23"
    assert run(t).status == "WARN" and "ma_not_first_line" in run(t).issues
    assert run(t, strict=True).status == "FAIL"


def test_ma_variants():
    assert c.find_ma("Ma D06 | x")[0] == "D06"
    assert c.find_ma("M A09 | áo")[0] == "A09"
    assert c.find_ma("MÃ: S13")[0] == "S13"


def test_s06_lock():
    assert run("Mã S06\nGiá $25").status == "PASS"
    r = c.check_post("p", "Mã S06\nGiá $30", {"S06": 30.0}, POL, APP)
    assert "s06_not_25" in r.issues and r.expected_usd == 25


def test_held_approved_and_differs():
    assert run("Mã S15\nGiá $30").status == "PASS"
    assert "held_gia_differs" in run("Mã K04\nGiá $100").issues
    assert "held_no_approved_gia" in run("Mã A24\nGiá $24").issues


def test_never_list_fails():
    assert "never_list" in run("Mã Z99\nGiá $10").issues


def test_not_in_catalog_warns():
    assert "not_in_live_catalog" in run("Mã S19\nSize M L").issues


def test_ig_wrapper_is_stripped():
    t = '0 likes, 0 comments - sassycloset.boutique on September 25, 2026: "Mã S13 | x | Giá $26". '
    assert run(t).status == "PASS"


def test_loaders_and_main(tmp_path):
    (tmp_path / "live.json").write_text(json.dumps({"prices": {"S13": 26}}))
    (tmp_path / "held.json").write_text(json.dumps({"heldIncomplete": ["S15"], "neverList": []}))
    (tmp_path / "ap.json").write_text(json.dumps({"approvedGia": {"S15": 30}}))
    (tmp_path / "a.txt").write_text("Mã S13\nGiá $26\n---\nMã S15\nGiá $31\n", encoding="utf-8")
    (tmp_path / "b.json").write_text(json.dumps([{"id": "x", "text": "Mã S13 Giá 26$"}]), encoding="utf-8")
    out = tmp_path / "o.json"
    rc = c.main([str(tmp_path / "a.txt"), str(tmp_path / "b.json"), "--live", str(tmp_path / "live.json"),
                 "--held", str(tmp_path / "held.json"), "--approved", str(tmp_path / "ap.json"),
                 "--out-json", str(out), "--out-md", str(tmp_path / "o.md")])
    s = json.loads(out.read_text())
    assert rc == 1 and s["counts"] == {"PASS": 2, "WARN": 0, "FAIL": 1}
    assert "held_gia_differs" in s["posts"][1]["issues"]


def test_html_og_description(tmp_path):
    f = tmp_path / "raw-Abc.html"
    f.write_text('<meta property="og:description" content="0 likes: &quot;M\u00e3 S13\nGi\u00e1 $26&quot;. " />', encoding="utf-8")
    [(pid, txt)] = c.load_posts(f)
    assert pid == "Abc" and run(txt).status == "PASS"
