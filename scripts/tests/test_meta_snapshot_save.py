import json, sys, time
from datetime import date, datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

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


def test_dedup_keeps_later_instant_when_the_text_sorts_earlier():
    """A later offset string can be an earlier instant. The stale line uses the survivor."""
    utc_evening = {"platform": "fb", "post_id": "1", "ma": "X02", "has_gia": "no",
                   "checked_at": "2026-11-03T07:30:00+00:00"}
    pacific_midnight = {"platform": "fb", "post_id": "1", "ma": "X01", "has_gia": "yes",
                        "checked_at": "2026-11-03T00:00:00-08:00"}
    for rows in ((utc_evening, pacific_midnight), (pacific_midnight, utc_evening)):
        sheet = ms.normalize_sheet(list(rows))
        assert sheet.bad == [] and sheet.assumed_zone == 0
        assert len(sheet.posts) == 1
        kept = sheet.posts[0]
        assert kept["ma"] == "X01" and kept["has_gia"] is True
        assert kept["checked_at"] == "2026-11-03T00:00:00-08:00"
        text = ms.render_status(
            sheet.posts, sheet.bad, as_of=date(2026, 11, 3), outcome="saved")
        assert text == (
            "OK checked_at 2026-11-03 America/Los_Angeles\n"
            "saved posts=1\n"
        )
    naive_later = ms.normalize_sheet([
        {"platform": "fb", "post_id": "1", "ma": "X02", "has_gia": "no",
         "checked_at": "2026-11-03T06:00:00+00:00"},
        {"platform": "fb", "post_id": "1", "ma": "X01", "has_gia": "yes",
         "checked_at": "2026-11-02T23:00:00"},
    ])
    assert naive_later.assumed_zone == 1
    assert naive_later.posts[0]["ma"] == "X01" and naive_later.posts[0]["has_gia"] is True
    same_instant = ms.normalize_sheet([
        {"platform": "fb", "post_id": "1", "ma": "X01", "has_gia": "yes",
         "checked_at": "2026-11-02T12:00:00-08:00"},
        {"platform": "fb", "post_id": "1", "ma": "X02", "has_gia": "no",
         "checked_at": "2026-11-02T20:00:00+00:00"},
    ])
    assert same_instant.posts[0]["ma"] == "X01" and same_instant.assumed_zone == 0


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


# Golden freshness reports. Status text is exact; paths stay out of the files.
GOLDEN = Path(__file__).resolve().parent / "fixtures" / "golden"
HELD_JSON = Path(__file__).resolve().parents[2] / "data" / "held.json"
AS_OF = date(2026, 11, 2)
PT = ZoneInfo("America/Los_Angeles")
CAPTION = "HiddenCaptionWord"
POST_KEYS = ["platform", "media_type", "id", "ma", "has_gia", "checked_at"]


def _golden(name):
    return (GOLDEN / name).read_text(encoding="utf-8")


def _row(post_id, checked_at, ma="X01", caption=None):
    row = {"platform": "FB", "media_type": "post", "post_id": post_id, "ma": ma,
           "has_gia": "yes", "checked_at": checked_at}
    if caption is not None:
        row["caption"] = caption
    return row


def _status(rows, outcome):
    sheet = ms.normalize_sheet(rows)
    text = ms.render_status(sheet.posts, sheet.bad, as_of=AS_OF,
                            assumed_zone=sheet.assumed_zone, outcome=outcome)
    return sheet, text


def test_meta_snapshot_golden_files_have_one_trailing_newline():
    names = [
        "meta_snapshot_empty.txt",
        "meta_snapshot_fresh.txt",
        "meta_snapshot_future.txt",
        "meta_snapshot_mixed.txt",
        "meta_snapshot_naive.txt",
        "meta_snapshot_stale.txt",
        "meta_snapshot_unusable.txt",
    ]
    assert [p.name for p in sorted(GOLDEN.glob("meta_snapshot_*.txt"))] == names
    for name in names:
        raw = (GOLDEN / name).read_bytes()
        assert raw.endswith(b"\n") and not raw.endswith(b"\n\n")
        text = raw.decode("utf-8")
        assert "\r" not in text and "->" not in text and "hidden-sheet-dir" not in text


def test_checked_on_utc_midnight_is_prior_los_angeles_day():
    assert ms.checked_on("2026-01-01T00:00:00+00:00") == date(2025, 12, 31)


def test_parse_as_of_none_is_today_pt_and_bad_value():
    today = datetime.now(PT).date()
    assert ms.parse_as_of(None) == (today, None)
    assert ms.parse_as_of("2026-11-02") == (AS_OF, None)
    assert ms.parse_as_of("2026-99-99") == (None, "bad --as-of, want YYYY-MM-DD")
    assert ms.parse_as_of("not-a-date") == (None, "bad --as-of, want YYYY-MM-DD")


def test_golden_stale_status():
    rows = [_row("1000000001", "2026-01-01T00:00:00Z")]
    posts, bad = ms.normalize(rows)
    assert bad == []
    assert posts[0] == {"platform": "fb", "media_type": "post", "id": "1000000001",
                        "ma": "X01", "has_gia": True, "checked_at": "2026-01-01T00:00:00+00:00"}
    assert list(posts[0]) == POST_KEYS
    text = ms.render_status(posts, bad, as_of=AS_OF, outcome="saved")
    assert text == _golden("meta_snapshot_stale.txt")
    sheet = ms.normalize_sheet(rows)
    assert sheet.assumed_zone == 0
    assert list(sheet.posts) == posts and list(sheet.bad) == bad


def test_golden_empty_status():
    text = ms.render_status([], [], as_of=AS_OF, outcome="not-saved")
    assert text == _golden("meta_snapshot_empty.txt")
    sheet = ms.normalize_sheet([])
    assert list(sheet.posts) == [] and list(sheet.bad) == [] and sheet.assumed_zone == 0


def test_golden_fresh_status():
    rows = [_row("1000000001", "2026-11-02T20:00:00-08:00")]
    sheet, text = _status(rows, "saved")
    assert sheet.assumed_zone == 0
    assert text == _golden("meta_snapshot_fresh.txt")


def test_golden_future_status():
    rows = [_row("1000000001", "2026-12-01T00:00:00-08:00")]
    sheet, text = _status(rows, "saved")
    assert sheet.assumed_zone == 0
    assert text == _golden("meta_snapshot_future.txt")


def test_golden_mixed_status():
    # Later calendar day sorts first, so "latest" is the max date, not the last row.
    rows = [
        _row("1000000001", "2026-11-02T12:00:00-08:00", ma="X01"),
        _row("1000000002", "2026-11-01T12:00:00-08:00", ma="X02"),
    ]
    sheet, text = _status(rows, "saved")
    assert sheet.assumed_zone == 0 and len(list(sheet.posts)) == 2
    assert text == _golden("meta_snapshot_mixed.txt")


def test_golden_unusable_status():
    rows = [_row("1000000001", "not-a-date")]
    _, bad = ms.normalize(rows)
    sheet, text = _status(rows, "not-saved")
    assert list(sheet.posts) == [] and list(sheet.bad) == list(bad)
    assert sheet.assumed_zone == 0
    assert text == _golden("meta_snapshot_unusable.txt")


def test_golden_naive_status():
    rows = [_row("1000000001", "2026-11-02T15:00:00")]
    sheet, text = _status(rows, "saved")
    assert sheet.assumed_zone == 1
    assert text == _golden("meta_snapshot_naive.txt")
    stored = list(sheet.posts)[0]["checked_at"]
    assert list(list(sheet.posts)[0]) == POST_KEYS
    # Offset present. Do not pin a numeric zone suffix.
    aware = datetime.fromisoformat(stored)
    assert aware.tzinfo is not None and aware.utcoffset() is not None
    assert stored != "2026-11-02T15:00:00"
    assert ms.checked_on(stored) == AS_OF


def test_assumed_zone_counts_surviving_naive_posts():
    dup = ms.normalize_sheet([
        _row("1000000001", "2026-11-01T15:00:00"),
        _row("1000000001", "2026-11-02T15:00:00"),
    ])
    assert len(list(dup.posts)) == 1 and dup.assumed_zone == 1
    assert ms.checked_on(list(dup.posts)[0]["checked_at"]) == AS_OF
    replaced = ms.normalize_sheet([
        _row("1000000001", "2026-11-01T15:00:00"),
        _row("1000000001", "2026-11-02T20:00:00-08:00"),
    ])
    assert len(list(replaced.posts)) == 1 and replaced.assumed_zone == 0
    assert ms.checked_on(list(replaced.posts)[0]["checked_at"]) == AS_OF
    kept_naive = ms.normalize_sheet([
        _row("1000000001", "2026-11-01T20:00:00-08:00"),
        _row("1000000001", "2026-11-02T15:00:00"),
    ])
    assert len(list(kept_naive.posts)) == 1 and kept_naive.assumed_zone == 1
    mixed = ms.normalize_sheet([
        _row("1000000001", "2026-11-02T15:00:00"),
        _row("1000000002", "2026-11-02T20:00:00-08:00"),
    ])
    assert len(list(mixed.posts)) == 2 and mixed.assumed_zone == 1


def test_assumed_zone_note_is_plural():
    rows = [
        _row("1000000001", "2026-11-02T15:00:00"),
        _row("1000000002", "2026-11-02T16:00:00"),
    ]
    sheet, text = _status(rows, "saved")
    assert sheet.assumed_zone == 2
    assert text == (
        "NOTE 2 checked_at values had no timezone; read as America/Los_Angeles\n"
        "OK checked_at 2026-11-02 America/Los_Angeles\n"
        "saved posts=2\n"
    )


def test_older_posts_note_is_plural():
    rows = [
        _row("1000000001", "2026-11-02T12:00:00-08:00"),
        _row("1000000002", "2026-11-01T12:00:00-08:00"),
        _row("1000000003", "2026-10-31T12:00:00-08:00"),
    ]
    _, text = _status(rows, "saved")
    assert text == (
        "OK checked_at 2026-11-02 America/Los_Angeles\n"
        "NOTE 2 posts checked before 2026-11-02\n"
        "saved posts=3\n"
    )


def test_future_latest_still_notes_older_posts():
    rows = [
        _row("1000000001", "2026-12-01T00:00:00-08:00"),
        _row("1000000002", "2026-11-01T12:00:00-08:00"),
    ]
    _, text = _status(rows, "saved")
    assert text == (
        "NOTE latest checked_at 2026-12-01 America/Los_Angeles is after 2026-11-02\n"
        "NOTE 1 post checked before 2026-11-02\n"
        "saved posts=2\n"
    )


def test_stale_status_omits_older_count():
    rows = [
        _row("1000000001", "2026-01-02T00:00:00Z"),
        _row("1000000002", "2026-01-01T00:00:00Z"),
    ]
    _, text = _status(rows, "saved")
    assert text == (
        "STALE latest checked_at 2026-01-01 America/Los_Angeles is before 2026-11-02\n"
        "saved posts=2\n"
    )


def test_zone_note_then_stale_omits_older_count():
    rows = [_row("1000000001", "2026-01-01T10:00:00")]
    sheet, text = _status(rows, "saved")
    assert sheet.assumed_zone == 1
    assert text == (
        "NOTE 1 checked_at value had no timezone; read as America/Los_Angeles\n"
        "STALE latest checked_at 2026-01-01 America/Los_Angeles is before 2026-11-02\n"
        "saved posts=1\n"
    )


def test_zone_note_precedes_ok_and_older_count():
    rows = [
        _row("1000000001", "2026-11-02T12:00:00-08:00"),
        _row("1000000002", "2026-11-01T15:00:00"),
    ]
    sheet, text = _status(rows, "saved")
    assert sheet.assumed_zone == 1
    assert text == (
        "NOTE 1 checked_at value had no timezone; read as America/Los_Angeles\n"
        "OK checked_at 2026-11-02 America/Los_Angeles\n"
        "NOTE 1 post checked before 2026-11-02\n"
        "saved posts=2\n"
    )


def test_not_saved_omits_freshness():
    posts, _ = ms.normalize([_row("1000000001", "2026-11-02T20:00:00-08:00")])
    text = ms.render_status(posts, [(1, "checked_at")], as_of=AS_OF, assumed_zone=2, outcome="not-saved")
    assert text == "REJECT row 1: checked_at\nnot saved: 1 bad row(s)\n"


def test_dry_run_fresh_status():
    _, text = _status([_row("1000000001", "2026-11-02T20:00:00-08:00")], "dry-run")
    assert text == (
        "OK checked_at 2026-11-02 America/Los_Angeles\n"
        "dry-run OK posts=1\n"
    )


def test_dry_run_stale_status_keeps_stale_line():
    _, text = _status([_row("1000000001", "2026-01-01T00:00:00Z")], "dry-run")
    assert text == (
        "STALE latest checked_at 2025-12-31 America/Los_Angeles is before 2026-11-02\n"
        "dry-run OK posts=1\n"
    )


def test_save_without_freshness_kwargs_omits_keys(tmp_path):
    posts, bad = ms.normalize([_row("1000000001", "2026-01-01T00:00:00Z", caption=CAPTION)])
    assert bad == []
    assert posts[0]["checked_at"] == "2026-01-01T00:00:00+00:00"
    path = ms.save(posts, tmp_path / "snap")
    doc = json.loads(path.read_text(encoding="utf-8"))
    assert "as_of" not in doc
    assert "latest_checked_on" not in doc
    assert "stale" not in doc
    assert CAPTION not in path.read_text(encoding="utf-8")
    assert "caption" not in doc["posts"][0]


def _write_sheet(tmp_path, payload, name="sheet.json"):
    src = tmp_path / name
    src.write_text(payload if isinstance(payload, str) else json.dumps(payload), encoding="utf-8")
    return src


def _saved_from_stdout(last_line, out):
    prefix = "saved posts=1 -> "
    assert last_line.startswith(prefix)
    saved = Path(last_line[len(prefix):])
    assert saved.is_file() and out.resolve() in saved.resolve().parents
    return json.loads(saved.read_text(encoding="utf-8"))


def test_main_stale_as_of_saves_freshness_without_caption(tmp_path, capsys):
    src = _write_sheet(tmp_path, [_row("1000000001", "2026-01-01T00:00:00Z", caption=CAPTION)])
    out = tmp_path / "snap"
    code = ms.main([str(src), "--out-dir", str(out), "--as-of", "2026-11-02"])
    captured = capsys.readouterr()
    assert code == 0
    gold = _golden("meta_snapshot_stale.txt").splitlines()
    got = captured.out.splitlines()
    assert got[:-1] == gold[:-1]
    doc = _saved_from_stdout(got[-1], out)
    assert doc["stale"] is True
    assert doc["as_of"] == "2026-11-02"
    assert doc["latest_checked_on"] == "2025-12-31"
    assert doc["posts"][0]["checked_at"] == "2026-01-01T00:00:00+00:00"
    assert doc["posts"][0]["id"] == "1000000001"
    assert "caption" not in doc["posts"][0]
    assert CAPTION not in captured.out and CAPTION not in captured.err
    assert CAPTION not in json.dumps(doc)


def test_main_fresh_save_is_not_stale(tmp_path, capsys):
    src = _write_sheet(tmp_path, [_row("1000000001", "2026-11-02T20:00:00-08:00")])
    out = tmp_path / "snap"
    code = ms.main([str(src), "--out-dir", str(out), "--as-of", "2026-11-02"])
    captured = capsys.readouterr()
    assert code == 0
    gold = _golden("meta_snapshot_fresh.txt").splitlines()
    got = captured.out.splitlines()
    assert got[:-1] == gold[:-1]
    doc = _saved_from_stdout(got[-1], out)
    assert doc["stale"] is False
    assert doc["as_of"] == "2026-11-02"
    assert doc["latest_checked_on"] == "2026-11-02"


def test_main_empty_json_matches_golden(tmp_path, capsys):
    src = _write_sheet(tmp_path, "[]", name="empty.json")
    out = tmp_path / "snap"
    code = ms.main([str(src), "--out-dir", str(out), "--as-of", "2026-11-02"])
    captured = capsys.readouterr()
    assert code == 1
    assert captured.out == _golden("meta_snapshot_empty.txt")
    assert not out.exists()


def test_main_unusable_json_exits_1_and_writes_nothing(tmp_path, capsys):
    src = _write_sheet(tmp_path, [_row("1000000001", "not-a-date")], name="bad.json")
    out = tmp_path / "snap"
    code = ms.main([str(src), "--out-dir", str(out), "--as-of", "2026-11-02"])
    captured = capsys.readouterr()
    assert code == 1
    assert not out.exists()
    assert captured.out == _golden("meta_snapshot_unusable.txt")


def test_main_missing_file_stderr_has_no_path(tmp_path, capsys):
    missing = tmp_path / "hidden-sheet-dir" / "sheet.json"
    out = tmp_path / "snap"
    code = ms.main([str(missing), "--out-dir", str(out), "--as-of", "2026-11-02"])
    captured = capsys.readouterr()
    assert code == 2
    assert captured.err == "MISSING meta snapshot input\n"
    assert "hidden-sheet-dir" not in captured.err
    assert not out.exists()


def test_main_bad_as_of_is_exit_2_before_read(tmp_path, capsys):
    missing = tmp_path / "hidden-sheet-dir" / "sheet.json"
    out = tmp_path / "snap"
    code = ms.main([str(missing), "--as-of", "2026-99-99", "--out-dir", str(out)])
    captured = capsys.readouterr()
    assert code == 2
    assert captured.err == "bad --as-of, want YYYY-MM-DD\n"
    assert "MISSING" not in captured.err
    assert not out.exists()


def test_main_dry_run_fresh_writes_nothing(tmp_path, capsys):
    src = _write_sheet(tmp_path, [_row("1000000001", "2026-11-02T20:00:00-08:00")], name="fresh.json")
    out = tmp_path / "snap"
    code = ms.main([str(src), "--out-dir", str(out), "--as-of", "2026-11-02", "--dry-run"])
    captured = capsys.readouterr()
    assert code == 0
    assert captured.out == (
        "OK checked_at 2026-11-02 America/Los_Angeles\n"
        "dry-run OK posts=1\n"
    )
    assert not out.exists()


def test_main_leaves_held_json_bytes_unchanged(tmp_path):
    before = HELD_JSON.read_bytes()
    src = _write_sheet(tmp_path, [_row("1000000001", "2026-01-01T00:00:00Z")])
    out = tmp_path / "snap"
    assert ms.main([str(src), "--out-dir", str(out)]) == 0
    assert HELD_JSON.read_bytes() == before
