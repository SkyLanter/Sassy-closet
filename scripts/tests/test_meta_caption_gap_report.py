"""Placeholder-only tests for scripts/meta_caption_gap_report.py (piece 53)."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import meta_caption_gap_report as g  # noqa: E402

SECRET = "PLACEHOLDER-CAPTION-TEXT-XYZ"


def mk(tmp, posts=None, notes=None, live=("A09", "D06")):
    out = tmp / "out"
    (out / "qc").mkdir(parents=True)
    (out / "qc" / "catalog.v1.json").write_text(json.dumps(
        {"products": [{"ma": m, "status": "available"} for m in live] + [{"ma": "Z99", "status": "held"}]}))
    if posts is not None:
        (out / "qc" / "meta-snapshot.json").write_text(json.dumps({"posts": posts}), encoding="utf-8")
    if notes is not None:
        (out / "qc" / "notes.md").write_text(notes, encoding="utf-8")
    return tmp


def P(i, cap, plat="fb", media="photo"):
    return {"id": i, "platform": plat, "caption": cap, "media_type": media}


def test_snapshot_flags_no_ma_and_no_gia(tmp_path):
    root = mk(tmp_path, posts=[P("100", f"Mã A09\nGiá $30\n{SECRET}"), P("200", "", media="reel"),
                               P("300", "Mã D06\nđẹp", plat="ig")])
    rep = g.build([root / "out"])
    assert rep["no_ma"] == [("fb", "reel", "200")]
    assert ("fb", "reel", "200") in rep["no_gia"] and ("ig", "photo", "300") in rep["no_gia"]


def test_live_no_post_per_platform(tmp_path):
    root = mk(tmp_path, posts=[P("1", "Mã A09\nGiá $30"), P("2", "Mã A09\nGiá $30", plat="ig")])
    rep = g.build([root / "out"])
    assert rep["live_no_post"] == {"fb": ["D06"], "ig": ["D06"]}
    assert rep["live_mas"] == 2  # held Z99 not live


def test_live_no_post_unknown_without_snapshot(tmp_path):
    rep = g.build([mk(tmp_path)/"out"])
    assert rep["live_no_post"] == {"fb": None, "ig": None}


def test_notes_parsing(tmp_path):
    notes = ("- FB Reel 1111111111 (X01, held) still has no caption, mã, or Giá. The IG X02 caption has no Giá.\n"
             '- FB "Mã X03" hair-clip post: Mã present, no Giá (held).\n'
             "- FB Reel 2222222222: still no caption or mã?\n")
    rep = g.build([mk(tmp_path, notes=notes)/"out"])
    assert rep["no_ma"] == [("fb", "reel", "1111111111")]
    assert set(rep["no_gia"]) == {("fb", "reel", "1111111111"), ("ig", "post", "ma:X02"), ("fb", "post", "ma:X03")}


def test_padded_note_ma_uses_the_shop_key(tmp_path):
    notes = (
        "IG Reel Mã S006 has no Giá.\n"
        "FB post MãS006 has no Giá.\n"
        "FB Reel Mã S6 has no Giá.\n"
        'FB "Mã S015" hair-clip post has no Giá.\n'
        "IG Reel Mã A100 Mã A09 has no Giá.\n"
        "FB Reel Mã S06B has no Giá.\n"
        "IG Reel Mã K12345 has no Giá.\n"
        "The IG S006 caption has no Giá.\n"
        "IG A100 caption has no Giá and the IG A09 caption has no Giá.\n"
    )
    rep = g.build([mk(tmp_path, notes=notes) / "out"])
    gia = set(rep["no_gia"])
    assert ("ig", "reel", "ma:S06") in gia
    assert ("fb", "post", "ma:S06") in gia
    assert ("fb", "reel", "ma:S06") in gia
    assert ("fb", "post", "ma:S15") in gia
    assert ("ig", "reel", "ma:A09") in gia
    assert ("ig", "post", "ma:S06") in gia
    assert ("ig", "post", "ma:A09") in gia
    ids = [item[2] for item in gia]
    assert "ma:S00" not in ids
    assert "ma:A10" not in ids
    assert "ma:A100" not in ids
    assert "ma:K12" not in ids
    assert not any("S06B" in item or item == "ma:K12345" for item in ids)


def test_stuck_suffix_note_is_not_s06(tmp_path):
    notes = (
        "FB Reel Mã S06Đ has no Giá.\n"
        "IG Reel Mã S06\uFF22 has no Giá.\n"
        "FB post Mã S06\u200bB has no Giá.\n"
        "IG Reel Mã S06\u00adB has no Giá.\n"
        "FB post Mã S06\u200eB has no Giá.\n"
        "IG S06Đ caption has no Giá.\n"
    )
    rep = g.build([mk(tmp_path, notes=notes) / "out"])
    ids = [item[2] for item in rep["no_gia"]]
    assert "ma:S06" not in ids


def test_cli_never_prints_caption(tmp_path, capsys):
    root = mk(tmp_path, posts=[P("9", f"{SECRET} no code here")])
    rc = g.main(["--root", str(root), "--dirs", "out"])
    o = capsys.readouterr().out
    assert rc == 1 and SECRET not in o
    # Parse rows by label instead of a bare-digit substring (a printed path could hold a 9).
    lines = o.splitlines()
    assert "no_ma: 1" in lines
    assert lines[lines.index("no_ma: 1") + 1].split() == ["fb", "photo", "9"]
    rc = g.main(["--root", str(root), "--dirs", "out", "--json"])
    js = capsys.readouterr().out
    assert rc == 1 and SECRET not in js
    rep = json.loads(js)
    assert rep["no_ma"] == [["fb", "photo", "9"]]
    assert rep["no_gia"] == [["fb", "photo", "9"]]


def test_clean_exit_zero_and_usage(tmp_path, capsys):
    root = mk(tmp_path, posts=[P("1", "Mã A09\nGiá $30"), P("2", "Mã D06\nGiá $28"),
                               P("3", "Mã A09\nGiá $30", plat="ig"), P("4", "Mã D06\nGiá $28", plat="ig")])
    assert g.main(["--root", str(root), "--dirs", "out"]) == 0
    assert g.main(["--root", str(tmp_path / "nope")]) == 2


def test_skips_bundle_dir(tmp_path):
    root = mk(tmp_path)
    b = root / "out" / "pending-draft-prs"
    b.mkdir()
    (b / "x.md").write_text("FB Reel 3333333333 has no caption.")
    assert g.build([root / "out"])["no_ma"] == []
