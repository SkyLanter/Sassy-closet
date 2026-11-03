"""Piece 187b: a saved snapshot row with a padded mã (' a01 ') still covers that live mã."""
import json

import meta_caption_gap_report as m


def _run(tmp_path, ma, capsys):
    root = tmp_path / f"r{len(ma)}"
    (root / "s").mkdir(parents=True)
    (root / "s" / "snap.csv").write_text(
        f"platform,id,media_type,ma,has_gia\nfb,1,post,{ma},true\nig,2,post,{ma},true\n", encoding="utf-8")
    cat = tmp_path / "catalog.json"
    cat.write_text(json.dumps({"products": [{"ma": "A01", "status": "available"}]}))
    m.main(["--root", str(root), "--dirs", "s", "--catalog", str(cat), "--json"])
    return json.loads(capsys.readouterr().out)


def test_padded_snapshot_ma_covers_live(tmp_path, capsys):
    clean = _run(tmp_path, "A01", capsys)
    assert clean["live_no_post"] == {"fb": [], "ig": []}
    assert _run(tmp_path, " a01 ", capsys)["live_no_post"] == clean["live_no_post"]
