"""S06 $25 spellings, held never-publish, incomplete Taobao never quotes.

No network. Does not write intake, Blob, held.json, or a price.
"""

from decimal import Decimal

from autolist import listing_quote
from held_policy import HeldPolicy, load_held_policy
from pickup import events_from_json, plan_pickups


def _ready(ma: str, sell: str | None = None) -> dict:
    row = {
        "ma": ma,
        "sizes": ["M"],
        "photo_count": 1,
        "public_cny": "20",
        "boss_approved": True,
    }
    if sell is not None:
        row["sell_usd"] = sell
    return row


def test_s06_lock_holds_for_short_and_padded_spellings() -> None:
    policy = load_held_policy()
    for spelling in ("S06", "S6", "s006", " S006 "):
        quote = listing_quote(spelling, Decimal("4"), policy)
        assert quote.ma == "S06"
        assert quote.action == "locked"
        assert quote.sell_usd == 25
        blocked = plan_pickups(events_from_json([_ready(spelling, "40")]), policy)[0]
        assert blocked.publish is False
        assert blocked.live is False
        assert blocked.quoted_usd is None
        assert "s06_lock" in blocked.flags


def test_held_spellings_never_publish() -> None:
    policy = load_held_policy()
    held = next(code for code in policy.held if len(code) == 3 and code[1] == "0")
    spellings = (held, held[0] + str(int(held[1:])), held[0] + "0" + held[1:])
    for spelling in spellings:
        decision = plan_pickups(events_from_json([_ready(spelling)]), policy)[0]
        assert decision.ma == held
        assert decision.publish is False
        assert decision.live is False
        assert decision.held is True
        assert decision.quoted_usd is None
        assert "held" in decision.flags


def test_never_list_spelling_never_publishes() -> None:
    policy = HeldPolicy(held=(), never_list=("Z90",))
    decision = plan_pickups(events_from_json([_ready("z090")]), policy)[0]
    assert decision.ma == "Z90"
    assert decision.publish is False
    assert "never_list" in decision.flags
    assert decision.quoted_usd is None


def test_incomplete_taobao_is_not_quoted_or_published() -> None:
    policy = HeldPolicy(held=(), never_list=())
    decision = plan_pickups(
        events_from_json(
            [
                {
                    "ma": "Z91",
                    "sizes": [],
                    "photo_count": 0,
                    "boss_approved": True,
                }
            ]
        ),
        policy,
    )[0]
    assert decision.publish is False
    assert decision.live is False
    assert decision.held is True
    assert decision.quoted_usd is None
    assert decision.flags == ("missing_size", "missing_photos", "missing_yen")
