"""Sizes are normalized before listing; invalid sizes are flagged, never listed."""

from __future__ import annotations

from decimal import Decimal

from autolist import invalid_size_tokens, listing_quote, listing_report, main, price
from held_policy import load_held_policy


def test_valid_sizes_normalized_and_price_unchanged() -> None:
    q = listing_quote("A07", Decimal("10"), sizes_raw="xxl s m")
    assert q.action == "quote" and q.sizes == ("S", "M", "2XL")
    assert q.sell_usd == listing_quote("A07", Decimal("10")).sell_usd == price(Decimal("10"))


def test_shoe_sizes_list_for_g_and_o() -> None:
    q = listing_quote("G05", Decimal("20"), sizes_raw="40.0 35,36")
    assert q.action == "quote" and q.sizes == ("35", "36", "40")


def test_invalid_sizes_flagged_not_listed() -> None:
    q = listing_quote("A07", Decimal("10"), sizes_raw="S 38 free")
    assert q.action == "flag-size" and q.sell_usd is None
    assert "38" in q.reason and "FREE" in q.reason
    assert listing_quote("G05", Decimal("10"), sizes_raw="47").action == "flag-size"
    assert listing_quote("A07", Decimal("10"), sizes_raw="").action == "flag-size"
    assert invalid_size_tokens("40.0 XXL", "G") == []
    assert invalid_size_tokens("32 M", "G") == ["32"]


def test_held_still_skip_before_size_check() -> None:
    policy = load_held_policy()
    for ma in policy.held:
        assert listing_quote(ma, Decimal("20"), policy, sizes_raw="M").action == "skip"
        assert listing_quote(ma, Decimal("20"), policy, sizes_raw="bad").action == "skip"


def test_q02_and_s06_unchanged() -> None:
    q = listing_quote("Q02", Decimal("20"), sizes_raw="M")
    base = listing_quote("Q02", Decimal("20"))
    assert (q.action, q.sell_usd, q.reason) == (base.action, base.sell_usd, base.reason)
    s06 = listing_quote("S06", Decimal("3.9"), sizes_raw="S M")
    assert s06.action == "locked" and s06.sell_usd == 25


def test_no_sizes_arg_is_identical_to_before() -> None:
    for ma in ("A07", "S10", "Q02", "S06", "K06"):
        assert listing_quote(ma, Decimal("12")) == listing_quote(ma, Decimal("12"), sizes_raw=None)


def test_report_groups() -> None:
    r = listing_report([
        {"ma": "A07", "landed": "10", "sizes": "S M"},
        {"ma": "A08", "landed": "10", "sizes": "38"},
        {"ma": "K06", "landed": "10", "sizes": "M"},
        {"ma": "S10", "landed": "10"},
    ])
    assert [x["ma"] for x in r["listed"]] == ["A07", "S10"]
    assert [x["ma"] for x in r["flagged"]] == ["A08"]
    assert [x["ma"] for x in r["skipped"]] == ["K06"]


def test_cli_sizes(capsys) -> None:
    assert main(["--landed", "10", "--ma", "A07", "--sizes", "S 99"]) == 0
    assert '"flag-size"' in capsys.readouterr().out
