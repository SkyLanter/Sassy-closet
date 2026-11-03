"""Piece 193: padded / lower-case mãs must still match held, approved, intake and S06 rows."""
import json

import boss_decisions_digest as bdd
import daily_shop_check as dsc
import held_photo_exposure as hpe
import held_policy
import price_approval_queue as paq


def test_norm_ma_helper():
    assert held_policy.norm_ma(" k03 ") == "K03"
    assert held_policy.norm_ma(None) == ""
    assert held_policy.norm_ma(7) == "7"


def test_price_queue_held_padded(tmp_path):
    p = tmp_path / "held.json"
    p.write_text(json.dumps({"heldIncomplete": [" K03 ", "a01"]}))
    assert paq.load_held(p)[0] == ["K03", "A01"]


def test_price_queue_approved_padded(tmp_path):
    p = tmp_path / "approved.json"
    p.write_text(json.dumps({"approvedGia": {" k03 ": 30}}))
    assert paq.load_approved(p) == {"K03"}


def test_price_queue_intake_row_padded():
    row = {"ma": " k03 ", "sell_usd": 30, "weight_kg": 0.5, "weight_approved": True}
    rep = paq.run(["K03"], [row], set())
    assert [i["ma"] for i in rep["queue"]] == []


def test_held_photo_exposure_held_padded(tmp_path):
    p = tmp_path / "held.json"
    p.write_text(json.dumps({"heldIncomplete": [" a24 ", "S14"]}))
    assert hpe.load_held(tmp_path, p) == ["A24", "S14"]


def test_public_held_padded(tmp_path):
    p = tmp_path / "pub.json"
    p.write_text(json.dumps({"exposedMas": [" a24 "]}))
    assert bdd.load_public_held(p) == {"A24"}


def test_snapshot_s06_and_held_padded():
    snap = {"items": [{"ma": " s06 ", "live": True, "sellUsd": 19, "held": False},
                      {"ma": " k03", "live": True, "sellUsd": 30, "held": True}]}
    rep = dsc.judge_snapshot(snap)
    text = " ".join(rep["fail"])
    assert "S06 off $25 lock" in text and "held mã live: K03" in text
