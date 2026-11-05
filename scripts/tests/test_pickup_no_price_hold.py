"""Boss approval never un-holds a pickup that has no usable price."""

from decimal import Decimal

import pytest

from held_policy import load_held_policy
from pickup import PickupEvent, plan_pickups


def _event(cost_cny: str, *, approved: bool, landed: str | None = None) -> PickupEvent:
    return PickupEvent(
        ma="Z09", via="form", action="new", cost_cny=cost_cny, landed_usd=landed,
        sell_usd=None, sizes=("S", "M"), photo_count=2, public_cny=Decimal("60"),
        taobao_state="ok", boss_approved=approved, already_listed=False,
        listed_sell_usd=None, reused=False,
    )


@pytest.mark.parametrize("cny", ["", "abc", "  ", "-5"])
@pytest.mark.parametrize("approved", [True, False])
def test_no_usable_cost_stays_held(cny: str, approved: bool) -> None:
    (d,) = plan_pickups([_event(cny, approved=approved)], load_held_policy())
    assert d.held is True
    assert d.quoted_usd is None
    assert d.flags == ("no_price",)
    assert d.blocks_live is True
    assert d.live is False and d.publish is False
    assert d.stored_cny == cny


def test_approved_with_cost_still_unheld() -> None:
    (d,) = plan_pickups([_event("60", approved=True)], load_held_policy())
    assert d.held is False
    assert isinstance(d.quoted_usd, int) and d.quoted_usd > 0
    assert d.flags == ()


def test_unapproved_with_cost_still_boss_approval() -> None:
    (d,) = plan_pickups([_event("60", approved=False)], load_held_policy())
    assert d.held is True and d.flags == ("boss_approval",)
    assert isinstance(d.quoted_usd, int)
