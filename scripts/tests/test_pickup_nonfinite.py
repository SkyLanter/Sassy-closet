"""Piece 166: non-finite sell $ text must read as unusable (None), never crash.

Junk punctuation must not become a whole dollar. 2$5 and 2,5 are not $25.
"""
import pickup
from held_policy import HeldPolicy


def test_nonfinite_sell_is_none():
    for bad in ("Infinity", "-inf", "NaN", "sNaN", "$Infinity"):
        assert pickup._whole_dollars(bad) is None, bad


def test_good_values_unchanged():
    assert pickup._whole_dollars("$25") == 25
    assert pickup._whole_dollars("1,200") == 1200
    assert pickup._whole_dollars("25.5") is None
    assert pickup._whole_dollars("") is None


def test_real_dollar_spellings_stay_whole():
    assert pickup._whole_dollars("25") == 25
    assert pickup._whole_dollars("25$") == 25
    assert pickup._whole_dollars("$ 25") == 25
    assert pickup._whole_dollars("25 $") == 25
    assert pickup._whole_dollars("25.00") == 25
    assert pickup._whole_dollars("25.000") == 25
    assert pickup._whole_dollars("25.") == 25
    assert pickup._whole_dollars("+25") == 25
    assert pickup._whole_dollars("$+25") == 25
    assert pickup._whole_dollars("-$25") == -25
    assert pickup._whole_dollars("$-25") == -25
    assert pickup._whole_dollars("$ -25") == -25
    assert pickup._whole_dollars("$1,200") == 1200
    assert pickup._whole_dollars("1,200$") == 1200
    assert pickup._whole_dollars("1,200.00") == 1200
    assert pickup._whole_dollars("+1,200") == 1200
    assert pickup._whole_dollars("12,000") == 12000
    assert pickup._whole_dollars("0") == 0
    assert pickup._whole_dollars("00") == 0


def test_junk_punctuation_is_not_a_whole_dollar():
    for bad in (
        "2$5",
        "2,5",
        "0,025",
        "$0,025",
        "00,025",
        "0,000,025",
        "0,250",
        "01,025",
        "12,50",
        "$2,5",
        "2,$5",
        "$$25",
        "1,2000",
        "1,2,000",
        "1e2",
        "0x19",
        "-$ 25",
        "2 $ 5",
        None,
    ):
        assert pickup._whole_dollars(bad) is None, bad


def _s06(sell: str):
    policy = HeldPolicy(held=(), never_list=())
    return pickup.plan_pickups(
        pickup.events_from_json(
            [
                {
                    "ma": "S06",
                    "sell_usd": sell,
                    "sizes": ["M"],
                    "photo_count": 1,
                    "public_cny": "20",
                    "boss_approved": True,
                }
            ]
        ),
        policy,
    )[0]


def test_junk_text_does_not_confirm_the_s06_lock():
    for sell in ("2$5", "2,5", "$$25", "$2,5", "0,025", "01,025"):
        decision = _s06(sell)
        assert decision.flags == ("s06_lock",), sell
        assert decision.quoted_usd is None
        assert decision.publish is False
        assert decision.live is False
        assert decision.blocks_live is True


def test_real_s06_spellings_stay_locked_at_25():
    for sell in ("$25", "25", "25.00", "25$", "$ 25"):
        decision = _s06(sell)
        assert decision.flags == (), sell
        assert decision.quoted_usd == 25
        assert decision.publish is False
        assert decision.live is False


def _listed(sell: str, listed: str):
    policy = HeldPolicy(held=(), never_list=())
    return pickup.plan_pickups(
        pickup.events_from_json(
            [
                {
                    "ma": "Z99",
                    "already_listed": True,
                    "sell_usd": sell,
                    "listed_sell_usd": listed,
                    "sizes": ["M"],
                    "photo_count": 1,
                    "public_cny": "20",
                    "boss_approved": True,
                }
            ]
        ),
        policy,
    )[0]


def test_junk_text_does_not_match_a_listed_price():
    decision = _listed("2$5", "25")
    assert decision.flags == ("no_reprice",)
    assert decision.blocks_live is True
    assert decision.publish is False
    collapsed = _listed("12,50", "1250")
    assert collapsed.flags == ("no_reprice",)
    assert collapsed.blocks_live is True


def test_same_whole_dollar_spellings_still_match():
    for sell, listed in (("$25", "25"), ("1,200", "1200"), ("28.00", "28")):
        decision = _listed(sell, listed)
        assert decision.flags == (), (sell, listed)
        assert decision.blocks_live is False
        assert decision.publish is False
