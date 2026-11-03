"""Piece 163: non-finite prices must never pass as 'ok' or crash the check."""
import math

import too_cheap_check as t
from held_policy import HeldPolicy

P = HeldPolicy(held=(), never_list=())
KEY = "intake" + "_cny"


def _cost(intake, listed="", kg="0.3"):
    return {"A01": {KEY: intake, "list_cny": listed, "kg": kg}}


COST = _cost(str(10 * 10))


def test_nan_live_price_is_not_ok():
    for bad in (math.nan, math.inf, -math.inf, 0.0, -5.0):
        row = t.evaluate({"A01": bad}, COST, P)[0]
        assert row.decision == "skip-missing", (bad, row)
        assert "live price" in row.reason


def test_infinite_intake_is_missing_not_crash():
    for bad in ("Infinity", "inf", "-Infinity", "NaN", "sNaN"):
        cost = _cost(bad, bad)
        row = t.evaluate({"A01": 20.0}, cost, P)[0]
        assert row.decision == "skip-missing", (bad, row)


def test_infinite_kg_is_missing():
    row = t.evaluate({"A01": 20.0}, _cost(str(10 * 10), kg="Infinity"), P)[0]
    assert row.decision == "skip-missing"


def test_good_row_unchanged():
    row = t.evaluate({"A01": 999.0}, COST, P)[0]
    assert row.decision == "ok"
