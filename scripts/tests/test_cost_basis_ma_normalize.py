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


def test_prices_map_and_bare_list(tmp_path):
    prices = tmp_path / "prices.json"
    prices.write_text(json.dumps({"prices": {" a01 ": 20, "B01": "NaN", "C01": True}}))
    assert c.load_live(prices) == {"A01": 20.0}
    bare = tmp_path / "bare.json"
    bare.write_text(json.dumps([{"ma": "A01", "priceUsd": 0}, {"ma": "A01", "priceUsd": 12}]))
    assert c.load_live(bare) == {"A01": 12.0}


def test_products_list_wins_and_bad_shape_raises(tmp_path):
    both = tmp_path / "both.json"
    both.write_text(json.dumps({
        "products": [{"ma": "A01", "priceUsd": 20}],
        "prices": {"B01": 30},
    }))
    assert c.load_live(both) == {"A01": 20.0}
    bad = tmp_path / "bad.json"
    bad.write_text(json.dumps({"note": "not a catalog"}))
    try:
        c.load_live(bad)
    except ValueError as err:
        assert "products" in str(err)
    else:
        raise AssertionError("expected ValueError")
    not_list = tmp_path / "not-list.json"
    not_list.write_text(json.dumps({"products": {"A01": 20}}))
    try:
        c.load_live(not_list)
    except ValueError:
        pass
    else:
        raise AssertionError("expected ValueError")
