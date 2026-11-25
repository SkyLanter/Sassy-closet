"""Compare live sell-price functions to scripts/testdata/price-characterization.json."""

from __future__ import annotations

import json
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path

import pytest

import autolist
import held_price_proposal
import pickup
import too_cheap_check
from held_policy import HeldPolicy

ROOT = Path(__file__).resolve().parents[2]
GOLDEN_PATH = ROOT / "scripts" / "testdata" / "price-characterization.json"


def golden() -> dict:
    return json.loads(GOLDEN_PATH.read_text(encoding="utf-8"))


def policy_from(data: dict) -> HeldPolicy:
    rules = data["policy"]
    return HeldPolicy(held=tuple(rules["held"]), never_list=tuple(rules["neverList"]))


def landed_string(cent: int) -> str:
    return f"{cent // 100}.{cent % 100:02d}"


def band_sell(bands: list[list[int]], cent: int) -> int:
    sell: int | None = None
    for start, value in bands:
        if cent < start:
            break
        sell = value
    if sell is None:
        raise AssertionError(f"cent {cent} is outside the golden bands")
    return sell


def test_price_constants() -> None:
    data = golden()
    fx = Decimal(data["fxCnyPerUsd"])
    ship = Decimal(data["shipUsdPerKg"])
    assert too_cheap_check.FX_CNY_PER_USD == fx
    assert held_price_proposal.FX_CNY_PER_USD == fx
    assert too_cheap_check.SHIP_USD_PER_KG == ship
    assert held_price_proposal.SHIP_USD_PER_KG == ship
    assert autolist.UNDER_TEN_BUMP == data["underTenBump"]
    assert autolist.S06_LOCK_USD == data["s06LockUsd"]


def test_tiered_cent_grid() -> None:
    # 5.85 stays $11 and the next cent, 5.86, drops to $10.
    bands = golden()["tieredBands"]
    for cent in range(1, 8001):
        landed = landed_string(cent)
        assert autolist.price(landed) == band_sell(bands, cent), landed


def test_flat_cent_grid() -> None:
    # 6.75 stays $11 and the next cent, 6.76, drops to $10.
    bands = golden()["flatBands"]
    for cent in range(1, 8001):
        landed = landed_string(cent)
        assert held_price_proposal.flat_quote(Decimal(landed)) == band_sell(bands, cent), landed


def test_tiered_and_flat_edges_stay_split() -> None:
    # Tiered and flat quotes are pinned separately. The same landed cost can sell at two different dollars.
    data = golden()
    for case in data["tieredEdges"]:
        assert autolist.price(case["landed"]) == case["sell"], case["landed"]
    for case in data["flatEdges"]:
        assert held_price_proposal.flat_quote(Decimal(case["landed"])) == case["sell"], case["landed"]


def test_price_refuses_non_positive_and_non_finite() -> None:
    refusal = golden()["tieredRefusal"]
    for raw in refusal["inputs"]:
        with pytest.raises(ValueError) as caught:
            autolist.price(raw)
        assert str(caught.value) == refusal["message"]
    with pytest.raises(ValueError) as caught:
        autolist.price(refusal["nonFiniteInput"])
    assert str(caught.value) == refusal["nonFiniteMessage"]


def test_flat_quote_invents_a_sell_for_non_positive() -> None:
    # A $0 landed cost is not refused: the flat quote turns it into $2.
    for case in golden()["flatInvent"]:
        assert held_price_proposal.flat_quote(Decimal(case["landed"])) == case["sellUsd"]


def test_margin_strings() -> None:
    for case in golden()["margins"]:
        text = format(autolist.margin_for_sell(case["sell"]).normalize(), "f")
        assert text == case["text"]


def test_cny_landed_exact_shown_tiered_and_flat() -> None:
    for case in golden()["cnyLanded"]:
        yen = Decimal(case["yen"])
        kg = Decimal(case["kg"])
        exact = too_cheap_check.landed_usd(yen, kg)
        assert exact == held_price_proposal.landed_usd(yen, kg)
        assert format(exact, "f") == case["exact"]
        shown = exact.quantize(Decimal("0.0001"), ROUND_HALF_UP)
        assert format(shown, "f") == case["shown"]
        assert autolist.price(exact) == case["tiered"]
        assert held_price_proposal.flat_quote(exact) == case["flat"]


def test_pickup_landed_from_cny() -> None:
    for case in golden()["pickupLanded"]:
        assert pickup.landed_usd_from_cny(case["ma"], case["cny"]) == case["landed"]


def test_too_cheap_decisions() -> None:
    data = golden()
    rules = policy_from(data)
    for case in data["tooCheap"]:
        rows = too_cheap_check.evaluate({case["ma"]: case["live"]}, {case["ma"]: case["cost"]}, rules)
        assert len(rows) == 1
        row = rows[0]
        assert row.ma == case["ma"]
        assert row.decision == case["decision"]
        assert row.reason == case["reason"]
        assert row.landed_usd == case["landedUsd"]
        assert row.target_usd == case["target"]
        assert row.kg == case["kg"]


def test_load_live_skips_null_price(tmp_path: Path) -> None:
    # Was pinned as a TypeError crash. A null price is now dropped, not raised:
    # the null mã has no live price, so it is never checked and never priced.
    catalog = tmp_path / "catalog.json"
    catalog.write_text(json.dumps(golden()["loadLiveNullPrice"]), encoding="utf-8")
    assert too_cheap_check.load_live(catalog) == {"A01": 20.0}


def test_held_proposals() -> None:
    data = golden()
    rules = policy_from(data)
    for case in data["heldProposals"]:
        sheet = held_price_proposal.build([case["row"]], {}, rules)
        assert sheet["count"] == case["count"]
        assert sheet["proposals"] == case["proposals"]


def test_s06_listing_quote() -> None:
    data = golden()
    rules = policy_from(data)
    for case in data["listingQuotes"]:
        quote = autolist.listing_quote(case["ma"], case["landed"], rules)
        assert quote.ma == case["maOut"]
        assert quote.action == case["action"]
        assert quote.sell_usd == case["sellUsd"]
        assert quote.reason == case["reason"]
