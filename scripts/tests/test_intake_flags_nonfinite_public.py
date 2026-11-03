"""Piece 173: a NaN/Infinity public ¥ must not crash intake flagging."""
from decimal import Decimal

from intake_flags import IntakeRow, PublicCny, flag_intake


def test_nan_public_does_not_crash():
    for bad in ("NaN", "sNaN"):
        flags = flag_intake([IntakeRow("A01", "88")], {"A01": PublicCny("ok", Decimal(bad))})
        assert [f for f in flags if f.ma == "A01"] == []


def test_infinite_public_never_flags_above():
    flags = flag_intake([IntakeRow("A01", "88")], {"A01": PublicCny("ok", Decimal("-Infinity"))})
    assert flags == []


def test_good_public_unchanged():
    flags = flag_intake([IntakeRow("A01", "88")], {"A01": PublicCny("ok", Decimal("50"))})
    assert [f.ma for f in flags] == ["A01"]
