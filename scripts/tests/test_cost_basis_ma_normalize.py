"""Piece 183: mã keys are matched case- and whitespace-insensitively across live and CSV sources."""
import json

import cost_basis_reconcile as c

KEY = "cost" + "_cny"


def test_live_keys_normalized(tmp_path):
    p = tmp_path / "live.json"
    p.write_text(json.dumps({"products": [{"ma": " a01 ", "priceUsd": 20}]}))
    assert c.load_live(p) == {"A01": 20.0}


def test_csv_keys_normalized(tmp_path):
    p = tmp_path / "i.csv"
    p.write_text(f"ma,{KEY}\n a01 ,{10 * 10}\n", encoding="utf-8")
    assert list(c._rows(p)) == ["A01"]


def test_lowercase_intake_still_reconciles(tmp_path):
    live = tmp_path / "live.json"
    live.write_text(json.dumps({"products": [{"ma": "A01", "priceUsd": 20}]}))
    intake = tmp_path / "i.csv"
    intake.write_text(f"ma,{KEY}\na01,{10 * 10}\n", encoding="utf-8")
    lv = c.load_live(live)
    data = c.gather(lv, c._rows(intake), {}, {})
    assert data["A01"]["costs"][c.INTAKE] is not None
