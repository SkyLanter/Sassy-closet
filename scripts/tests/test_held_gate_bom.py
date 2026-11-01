"""A BOM-prefixed held mã (CSV first cell) still hits the held gate."""

from autolist import listing_quote
from held_policy import load_held_policy, norm_ma


def test_bom_held_ma_is_skipped() -> None:
    policy = load_held_policy()
    held = policy.held[0]
    assert policy.skip_reason("\ufeff" + held) == "held"
    q = listing_quote("\ufeff" + held.lower(), "10", policy)
    assert q.action == "skip" and q.sell_usd is None


def test_bom_s06_stays_locked() -> None:
    q = listing_quote("\ufeffS06", "10", load_held_policy())
    assert (q.ma, q.action, q.sell_usd) == ("S06", "locked", 25)


def test_fullwidth_digits_do_not_become_a_listable_code() -> None:
    assert norm_ma("A\uff12\uff14") == "A\uff12\uff14"
