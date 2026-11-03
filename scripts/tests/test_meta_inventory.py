"""Synthetic-fixture tests for scripts/meta_inventory.py (piece 35)."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import meta_inventory as mi  # noqa: E402

FX = ROOT / "data" / "fixtures" / "meta-inventory"
LIVE = {"A09": 30.0, "D06": 28.0, "S06": 25.0}
KNOWN = {"A09", "D06", "S06", "S19"}
HELD = {"S19", "G01"}


def run(posts, live=LIVE, plats=("fb", "ig")):
    return mi.reconcile(posts, live, KNOWN, HELD, {}, set(), plats)


def P(i, cap, plat="fb", media="photo"):
    return {"id": i, "url": f"u/{i}", "platform": plat, "created_at": "", "caption": cap, "media_type": media}


def kinds(rep, k):
    return [f for f in rep["flags"] if f["flag"] == k]


def test_uncaptioned_reel_no_ma():
    f = kinds(run([P("r", "", media="reel")]), "no_ma")
    assert len(f) == 1 and f[0]["media_type"] == "reel" and "uncaptioned" in f[0]["detail"]


def test_held_s19_promoted():
    f = kinds(run([P("s", "Mã S19\nGiá $20")]), "held_promoted")
    assert [x["ma"] for x in f] == ["S19"]


def test_held_g01_no_gia():
    rep = run([P("g", "Mã G01")])
    assert kinds(rep, "held_promoted") and kinds(rep, "missing_gia")


def test_duplicate_same_platform_only():
    rep = run([P("a", "Mã A09\nGiá $30"), P("b", "Mã A09\nGiá $30"), P("c", "Mã A09\nGiá $30", "ig")])
    d = kinds(rep, "duplicate")
    assert len(d) == 1 and d[0]["ids"] == ["a", "b"] and d[0]["platform"] == "fb"


def test_live_no_post_per_platform():
    rep = run([P("a", "Mã A09\nGiá $30")], plats=("fb",))
    assert sorted(f["ma"] for f in kinds(rep, "live_no_post")) == ["D06", "S06"]


def test_malformed_gia_counts_as_missing_gia():
    assert kinds(run([P("a", "Mã A09\nGiá")]), "missing_gia")


def test_wrong_price_passthrough():
    f = kinds(run([P("a", "Mã D06\nGiá $29")]), "caption_lint")
    assert f and "gia_differs_live" in f[0]["detail"]


def test_clean_no_flags():
    rep = run([P("a", "Mã A09\nGiá $30")], live={"A09": 30.0}, plats=("fb",))
    assert rep["flags"] == []


def test_never_suggests_delete_or_repost():
    rep = run([P("r", "", media="reel"), P("a", "Mã S19"), P("b", "Mã S19")])
    txt = json.dumps(rep, ensure_ascii=False).lower()
    assert "delete" not in txt and "repost" not in txt
    assert all(f["action"] == "edit original only / Boss decides" for f in rep["flags"])


def test_cli_fixture(capsys):
    rc = mi.main([str(FX / "posts.json"), "--snapshot", str(FX / "snapshot.json"),
                  "--held", str(FX / "held.json"), "--approved", str(FX / "none.json"), "--json"])
    rep = json.loads(capsys.readouterr().out)
    assert rc == 1
    c = rep["counts"]
    assert c["no_ma"] == 1 and c["held_promoted"] == 1 and c["duplicate"] == 1
    assert c["missing_gia"] == 1 and c["caption_lint"] == 1
    assert c["live_no_post"] == 3  # S06 fb, A09 ig, D06 fb


def test_csv_export(tmp_path):
    p = tmp_path / "x.csv"
    p.write_text("id,url,platform,created_at,caption,media_type\nr,u,Facebook,2026,,reel\n", encoding="utf-8")
    rows = mi.load_export(p)
    assert rows[0]["platform"] == "fb" and rows[0]["media_type"] == "reel"


def test_usage_error(tmp_path):
    assert mi.main([str(tmp_path / "missing.json"), "--snapshot", str(FX / "snapshot.json")]) == 2
