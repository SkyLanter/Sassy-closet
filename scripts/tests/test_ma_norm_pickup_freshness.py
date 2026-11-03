"""Piece 246: pickup + freshness treat padded/short mã spellings as canonical."""
import freshness_check
import pickup
from held_policy import HeldPolicy, norm_ma


def _events(*mas):
    return pickup.events_from_json([{"ma": m, "sizes": ["M"]} for m in mas])


def test_events_loader_canonical():
    assert [e.ma for e in _events(" s006 ", "k3", "A100")] == ["S06", "K03", "A100"]


def test_s006_is_s06_locked_and_duplicate_of_s06():
    policy = HeldPolicy(held=(), never_list=())
    [d] = pickup.plan_pickups(_events("S006"), policy)
    assert d.ma == "S06"
    both = pickup.plan_pickups(_events("S006", "S06"), policy)
    assert all("duplicate" in d.flags for d in both)


def test_padded_held_ma_is_held():
    policy = HeldPolicy(held=("K03",), never_list=())
    [d] = pickup.plan_pickups(_events("k003"), policy)
    assert d.held and "held" in d.flags


def test_intake_fixture_rows_canonical():
    rows = freshness_check._intake_from_json([{"ma": " s006 "}, {"ma": "K003"}])
    assert [r.ma for r in rows] == ["S06", "K03"]
    assert norm_ma("S006") == "S06"


def test_landed_kind_uses_canonical():
    assert pickup.landed_usd_from_cny(" s006", None) == pickup.landed_usd_from_cny("S06", None)
