"""Piece 78 placeholder tests: Meta status read from a saved record."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import daily_summary_draft as d  # noqa: E402

DATE = "2026-01-02"


def test_no_record_is_unchecked(tmp_path):
    st, src = d.read_meta_status(tmp_path, DATE)
    assert src is None
    assert st["ig"][0] == st["fb"][0] == "unchecked"
    lines = d.meta_lines(st, src)
    assert "NOT CLEAR" in lines[-1]
    assert not any(": PASS" in x for x in lines)


def test_muse_record_mixed(tmp_path):
    p = tmp_path / "out/muse"; p.mkdir(parents=True)
    (p / f"meta-qc-{DATE}.json").write_text(json.dumps(
        {"ig": {"status": "pass", "reason": "placeholder qc"},
         "fb": {"status": "unchecked", "reason": "signed out"}}))
    st, src = d.read_meta_status(tmp_path, DATE)
    assert src.startswith("Muse QC record")
    lines = d.meta_lines(st, src)
    assert "- Instagram: UNCHECKED (single-source pass; needs Luxubu + Mini Boss)" in lines
    assert "- Facebook: UNCHECKED (signed out)" in lines
    assert lines[-1].startswith("Meta verdict: NOT CLEAR")


def test_flat_both_pass_not_clear(tmp_path):
    p = tmp_path / "out/muse"; p.mkdir(parents=True)
    (p / f"meta-qc-{DATE}.json").write_text(json.dumps({"ig": "pass", "fb": "pass"}))
    st, src = d.read_meta_status(tmp_path, DATE)
    assert d.meta_lines(st, src)[-1].startswith("Meta verdict: NOT CLEAR")  # piece 79: flat = single-source


def test_bad_status_ignored(tmp_path):
    p = tmp_path / "out/muse"; p.mkdir(parents=True)
    (p / f"meta-qc-{DATE}.json").write_text(json.dumps({"ig": "great", "fb": {"status": "ok"}}))
    st, src = d.read_meta_status(tmp_path, DATE)
    assert src is None and st["ig"][0] == "unchecked"


def test_snapshot_qc_block_and_side_missing(tmp_path):
    p = tmp_path / "out/meta-snapshot"; p.mkdir(parents=True)
    (p / "meta-snapshot-20260102T010000Z.json").write_text(json.dumps(
        {"kind": "meta-snapshot", "posts": [], "qc": {"fb": {"status": "fail", "reason": "dup post"}}}))
    st, src = d.read_meta_status(tmp_path, DATE)
    assert src.startswith("Meta snapshot")
    assert st["fb"] == ("fail", "dup post")
    assert st["ig"] == ("unchecked", "not in record")


def test_other_day_snapshot_not_used(tmp_path):
    p = tmp_path / "out/meta-snapshot"; p.mkdir(parents=True)
    (p / "meta-snapshot-20260101T010000Z.json").write_text(json.dumps({"qc": {"ig": "fail", "fb": "fail"}}))
    st, src = d.read_meta_status(tmp_path, DATE)
    assert src is None
