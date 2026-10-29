import json, sys, time
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import meta_snapshot_save as ms  # noqa: E402
import meta_caption_gap_report as gr  # noqa: E402

CSV = ("platform,media_type,post_id,ma,has_gia,checked_at,caption\n"
       "FB,post,1000000001,X01,yes,2026-01-01T00:00:00Z,PLACEHOLDER\n"
       "ig,reel,2000000001,,no,2026-01-01T00:00:00Z,\n"
       "ig,post,2000000002,X02,true,2026-01-01T00:00:00Z,\n")


def _cat(root, mas):
    d = root / "out" / "cat"; d.mkdir(parents=True, exist_ok=True)
    (d / "catalog.v1.json").write_text(json.dumps(
        {"products": [{"ma": m, "status": "available"} for m in mas]}))


def test_normalize_drops_caption_and_validates(tmp_path):
    f = tmp_path / "in.csv"; f.write_text(CSV)
    posts, bad = ms.normalize(ms.read_rows(f))
    assert not bad and len(posts) == 3
    assert all("caption" not in p for p in posts)
    assert posts[0] == {"platform": "fb", "media_type": "post", "id": "1000000001",
                        "ma": "X01", "has_gia": True, "checked_at": "2026-01-01T00:00:00+00:00"}


def test_bad_rows_rejected_nothing_saved(tmp_path):
    f = tmp_path / "in.json"
    f.write_text(json.dumps([{"platform": "tw", "post_id": "", "ma": "bad",
                              "has_gia": "maybe", "checked_at": "x"}]))
    out = tmp_path / "snap"
    assert ms.main([str(f), "--out-dir", str(out)]) == 1
    assert not out.exists()


def test_dedup_keeps_newest(tmp_path):
    rows = [{"platform": "fb", "post_id": "1", "ma": "X01", "has_gia": "no", "checked_at": "2026-01-01T00:00:00Z"},
            {"platform": "fb", "post_id": "1", "ma": "X01", "has_gia": "yes", "checked_at": "2026-01-02T00:00:00Z"}]
    posts, _ = ms.normalize(rows)
    assert len(posts) == 1 and posts[0]["has_gia"] is True


def test_gap_report_uses_saved_snapshot(tmp_path):
    f = tmp_path / "in.csv"; f.write_text(CSV)
    out = tmp_path / "out" / "meta-snapshot"
    assert ms.main([str(f), "--out-dir", str(out)]) == 0
    saved = json.loads(next(out.glob("*.json")).read_text())
    assert "PLACEHOLDER" not in json.dumps(saved)
    _cat(tmp_path, ["X01", "X02", "X03"])
    rep = gr.build([tmp_path / "out"])
    assert rep["live_no_post"]["fb"] == ["X02", "X03"]
    assert rep["live_no_post"]["ig"] == ["X01", "X03"]
    assert ("ig", "reel", "2000000001") in rep["no_ma"]
    assert ("ig", "reel", "2000000001") in rep["no_gia"]


def test_gap_report_newest_snapshot_only(tmp_path):
    out = tmp_path / "out" / "meta-snapshot"
    old = [{"platform": "fb", "media_type": "post", "id": "1", "ma": "X01", "has_gia": False,
            "checked_at": "2026-01-01T00:00:00+00:00"}]
    new = [dict(old[0], has_gia=True)]
    ms.save(old, out, datetime(2026, 1, 1, tzinfo=timezone.utc))
    ms.save(new, out, datetime(2026, 1, 2, tzinfo=timezone.utc))
    _cat(tmp_path, ["X01"])
    rep = gr.build([tmp_path / "out"])
    assert rep["no_gia"] == [] and rep["snapshot_posts"] == 1
    assert rep["live_no_post"]["fb"] == [] and rep["live_no_post"]["ig"] is None


def test_no_snapshot_still_unknown(tmp_path):
    _cat(tmp_path, ["X01"])
    rep = gr.build([tmp_path / "out"])
    assert rep["live_no_post"] == {"fb": None, "ig": None}


def test_default_out_is_gitignored():
    assert ms.OUT_DIR.relative_to(ms.ROOT).parts[0] == "out"
