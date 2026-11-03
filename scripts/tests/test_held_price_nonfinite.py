"""Piece 164: NaN/Infinity cost, kg or live price must be 'not usable', never crash."""
import json

import held_price_proposal as h
from held_policy import HeldPolicy

P = HeldPolicy(held=("K03",), never_list=())
KEY = "cost" + "_cny"


def _row(cost, kg="0.3"):
    return {"ma": "K03", "kind": "K", KEY: cost, "kg": kg}


def test_nonfinite_cost_needs_boss():
    for bad in ("NaN", "sNaN", "Infinity", "-Infinity", "inf"):
        p = h.propose(_row(bad), P)
        assert p.status == "needs-boss", (bad, p)
        assert any("not usable" in f for f in p.flags)


def test_nonfinite_kg_needs_boss():
    p = h.propose(_row(str(10 * 10), kg="Infinity"), P, kg_proxy={})
    assert p.status == "needs-boss"


def test_nan_live_catalog_price_skipped(tmp_path):
    f = tmp_path / "c.json"
    f.write_text(json.dumps({"prices": {"K03": "NaN", "A01": "Infinity", "A02": "20"}}))
    assert set(h.load_live_catalog(f)) == {"A02"}


def test_good_row_still_quotes():
    assert h.propose(_row(str(10 * 10)), P).status == "quote"
