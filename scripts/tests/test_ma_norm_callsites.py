"""Piece 251: remaining mã call sites use norm_ma (S006/k3 -> S06/K03)."""

from __future__ import annotations

from freshness_check import parse_blob_catalog
from intake_flags import IntakeRow, flag_intake


def test_blob_catalog_collapses_zero_padding():
    rows = parse_blob_catalog({"products": [{"ma": " S006 ", "priceUsd": 25}, {"ma": "k3", "priceUsd": 52}]})
    assert [r.ma for r in rows] == ["S06", "K03"]


def test_intake_flag_codes_are_canonical():
    flags = flag_intake([IntakeRow(ma="s006", cost_cny=""), IntakeRow(ma=" k3 ", cost_cny=None)])
    assert {f.ma for f in flags} == {"S06", "K03"}



def test_pickup_plan_codes_canonical():
    import inspect
    import pickup
    assert "norm_ma(event.ma)" in inspect.getsource(pickup.plan_pickups)
