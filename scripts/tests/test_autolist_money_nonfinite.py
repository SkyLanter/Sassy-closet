"""Piece 168: price() refuses NaN/Infinity/garbage landed cost with ValueError, like <=0."""
import pytest

import autolist as a


@pytest.mark.parametrize("bad", ["Infinity", "-Infinity", "NaN", "sNaN", float("nan"), float("inf"), "abc"])
def test_bad_landed_refused(bad):
    with pytest.raises(ValueError):
        a.price(bad)


def test_good_landed_unchanged():
    assert a.price("10") == 16
