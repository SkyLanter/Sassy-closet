"""Tiered margin edges. Fixtures only — no intake write and no network."""

from __future__ import annotations

import json
from decimal import Decimal
from pathlib import Path

from autolist import listing_quote, margin_for_sell, price, quote_from_sell
from held_policy import default_held_path, load_held_policy

ROOT = Path(__file__).resolve().parents[2]


def test_margin_bands() -> None:
    assert margin_for_sell(25) == Decimal("0.35")
    assert margin_for_sell(9) == Decimal("0.35")
    assert margin_for_sell(45) == Decimal("0.25")
    assert margin_for_sell(60) == Decimal("0.25")
    assert margin_for_sell(35) == Decimal("0.30")


def test_sell_25_is_the_fixed_point() -> None:
    landed = Decimal("16.25")
    sell = price(landed)
    assert sell == 25
    assert quote_from_sell(landed, sell) == sell
    assert margin_for_sell(sell) == Decimal("0.35")


def test_sell_45_is_the_fixed_point() -> None:
    landed = Decimal("33.75")
    sell = price(landed)
    assert sell == 45
    assert quote_from_sell(landed, sell) == sell
    assert margin_for_sell(sell) == Decimal("0.25")


def test_sell_under_10_adds_two_dollars() -> None:
    landed = Decimal("3.9")
    sell = price(landed)
    assert sell == 8
    assert sell < 10
    assert quote_from_sell(landed, sell) == sell
    assert margin_for_sell(sell) == Decimal("0.35")


def test_middle_band_fixed_point() -> None:
    landed = Decimal("24.5")
    sell = price(landed)
    assert sell == 35
    assert 25 < sell < 45
    assert quote_from_sell(landed, sell) == sell
    margin = margin_for_sell(sell)
    assert Decimal("0.25") < margin < Decimal("0.35")
    assert margin == Decimal("0.30")


def test_gap_between_bands_does_not_undercut() -> None:
    assert price(Decimal("16.26")) == 26
    assert price(Decimal("19.50")) == 30


def test_raw_35_percent_quote_is_replaced_when_it_undercuts() -> None:
    """Old line 72 returned the raw 35% quote: 30→47, 33→51, 19.51→31."""
    cases = (
        (Decimal("30"), 42),
        (Decimal("33"), 45),
        (Decimal("19.51"), 30),
    )
    for landed, expected in cases:
        sell = price(landed)
        assert sell == expected
        assert sell >= quote_from_sell(landed, sell)
        assert quote_from_sell(landed, sell - 1) > sell - 1
    quoted = listing_quote("A07", Decimal("30"))
    assert quoted.action == "quote"
    assert quoted.sell_usd == 42
    assert listing_quote("S06", Decimal("30")).sell_usd == 25
    skipped = listing_quote("V05", Decimal("30"))
    assert skipped.action == "skip"
    assert skipped.sell_usd is None
    assert price(Decimal("19.58")) == 30


def test_non_positive_landed_is_refused() -> None:
    try:
        price(0)
    except ValueError:
        return
    raise AssertionError("price(0) invented a sell")


def test_real_held_file_skips_k06_and_v05_and_quotes_q02() -> None:
    policy = load_held_policy()
    assert default_held_path() == ROOT / "data" / "held.json"
    assert "K06" in policy.held
    assert "V05" in policy.held
    assert "A07" not in policy.held
    assert "S10" not in policy.held
    assert policy.never_list == ()
    assert "Q02" not in policy.never_list
    assert listing_quote("K06", Decimal("20"), policy).sell_usd is None
    assert listing_quote("v05", Decimal("20"), policy).action == "skip"
    quoted_queen = listing_quote("Q02", Decimal("20"), policy)
    assert quoted_queen.action == "quote"
    assert quoted_queen.sell_usd is not None
    listed = listing_quote("A07", Decimal("10"), policy)
    assert listed.action == "quote"
    assert listed.sell_usd is not None
    assert listing_quote("S10", Decimal("10"), policy).action == "quote"


def test_s06_stays_25_and_blank_landed_is_not_invented() -> None:
    policy = load_held_policy()
    locked = listing_quote("S06", Decimal("3.9"), policy)
    assert locked.action == "locked"
    assert locked.sell_usd == 25
    blank = listing_quote("A01", None, policy)
    assert blank.sell_usd is None
    assert blank.action == "no-price"


def test_held_file_override_is_the_only_list(tmp_path: Path) -> None:
    path = tmp_path / "held.json"
    path.write_text(
        json.dumps({"heldIncomplete": ["Z01"], "neverList": ["Z02"]}),
        encoding="utf-8",
    )
    policy = load_held_policy(path)
    assert listing_quote("Z01", Decimal("10"), policy).action == "skip"
    assert listing_quote("Z02", Decimal("10"), policy).action == "skip"
    assert listing_quote("Q02", Decimal("10"), policy).action == "quote"
    assert listing_quote("K06", Decimal("10"), policy).action == "quote"
    source = (ROOT / "scripts" / "autolist.py").read_text(encoding="utf-8")
    pickup = (ROOT / "scripts" / "pickup.py").read_text(encoding="utf-8")
    assert "load_held_policy" in source
    assert "S14" not in source
    assert "K06" not in source
    assert "V05" not in source
    assert "Q02" not in source
    assert "Q02" not in pickup
