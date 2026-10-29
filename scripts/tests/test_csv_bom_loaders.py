"""Piece 177: Excel-saved CSVs start with a UTF-8 BOM; the first column ('ma') must still be read."""
from decimal import Decimal

import held_price_proposal
import intake_code_reuse_check
import intake_gaps
import meta_caption_gap_report
import meta_snapshot_save
import taobao_unreachable_streak

BOM = b"\xef\xbb\xbf"


def _csv(path, text):
    path.write_bytes(BOM + text.encode("utf-8"))
    return path


def test_held_price_weights(tmp_path):
    p = _csv(tmp_path / "w.csv", "ma,weight_kg\nK03,0.4\n")
    assert held_price_proposal.load_weights([p]) == {"K03": Decimal("0.4")}


def test_intake_gaps_weights(tmp_path):
    p = _csv(tmp_path / "w.csv", "ma,kg\nK03,0.4\n")
    assert intake_gaps.load_weights([p]) == {"K03": (Decimal("0.4"), "csv")}


def test_meta_caption_gap_records(tmp_path):
    p = _csv(tmp_path / "s.csv", "ma,url\nA01,x\n")
    assert meta_caption_gap_report._records(p)[0]["ma"] == "A01"


def test_meta_snapshot_read_rows(tmp_path):
    p = _csv(tmp_path / "s.csv", "ma,url\nA01,x\n")
    assert meta_snapshot_save.read_rows(p)[0]["ma"] == "A01"


def test_taobao_streak_runs(tmp_path):
    _csv(tmp_path / "cost-recheck-2026-10-01-flags.csv", "ma,flag\nA01,unreachable\n")
    runs = taobao_unreachable_streak.load_runs(str(tmp_path))
    assert runs and runs[0][1] == {"A01"}


def test_intake_code_reuse_rows(tmp_path):
    p = _csv(tmp_path / "r.csv", "ma,title\nA01,top\n")
    assert [r.ma for r in intake_code_reuse_check.load_rows(p)] == ["A01"]
