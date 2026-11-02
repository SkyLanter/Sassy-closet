"""Held-sheet landed must reprice to the same tier and flat quote.

Four-decimal storage and a two-decimal markdown cell used to reprice $1 below
the tier printed on the sheet. A tiny positive landed must not print 0.00, and
a float just below the true landed must not be stored on the neighboring tier.
"""

from __future__ import annotations

from decimal import Decimal

import held_price_proposal as hp
from autolist import price
from held_policy import HeldPolicy

POLICY = HeldPolicy(held=("S14", "K03"), never_list=("Q01", "Q02"))

# Explicit kg on the row (kind B has no category proxy). A29 must not pass kg.
ROW_79 = {"ma": "B79", "kind": "B", "cost_cny": "79.13", "kg": "0.5"}
ROW_117 = {"ma": "B18", "kind": "B", "cost_cny": "117.72", "kg": "0.5"}
ROW_143 = {"ma": "B44", "kind": "B", "cost_cny": "143.2", "kg": "1"}
ROW_9 = {"ma": "B09", "kind": "B", "cost_cny": "9", "kg": "0.8"}
ROW_A29 = {"ma": "A29", "kind": "A", "cost_cny": "110"}
QUOTED_ROWS = (ROW_79, ROW_117, ROW_143, ROW_9, ROW_A29)


def _landed_cell(md: str, ma: str) -> str:
    header: list[str] | None = None
    for line in md.splitlines():
        if not line.startswith("|"):
            continue
        cells = [part.strip() for part in line.strip().strip("|").split("|")]
        if header is None:
            header = cells
            assert cells[3] == "landed $"
            continue
        if cells[0] == ma:
            assert len(cells) == len(header)
            return cells[3]
    raise AssertionError(f"no markdown row for {ma}")


def _propose_and_markdown(row: dict[str, str]) -> tuple[hp.Proposal, str, str]:
    proposal = hp.propose(row, POLICY)
    sheet = hp.build([row], {}, POLICY)
    saved = next(item for item in sheet["proposals"] if item["ma"] == proposal.ma)
    assert saved["landed_usd"] == proposal.landed_usd
    assert saved["tiered_usd"] == proposal.tiered_usd
    assert saved["flat25_usd"] == proposal.flat25_usd
    text = hp.markdown(sheet)
    return proposal, _landed_cell(text, proposal.ma), text


def _assert_reprices(proposal: hp.Proposal, cell: str) -> None:
    assert proposal.status == "quote"
    assert proposal.tiered_usd is not None and proposal.flat25_usd is not None
    stored = Decimal(str(proposal.landed_usd))
    printed = Decimal(cell)
    assert price(stored) == proposal.tiered_usd
    assert hp.flat_quote(stored) == proposal.flat25_usd
    assert price(printed) == proposal.tiered_usd
    assert hp.flat_quote(printed) == proposal.flat25_usd


def test_yen_79_13_kg_0_5_not_17_03() -> None:
    proposal, cell, _text = _propose_and_markdown(ROW_79)
    exact = hp.landed_usd(Decimal("79.13"), Decimal("0.5"))
    assert proposal.kg_source == "intake"
    assert proposal.landed_usd != 17.03
    assert str(proposal.landed_usd) != "17.03"
    assert price(Decimal("17.03")) == 26
    assert proposal.tiered_usd == price(exact) == 27
    assert price(Decimal(str(proposal.landed_usd))) == proposal.tiered_usd == price(exact)
    assert hp.flat_quote(Decimal(str(proposal.landed_usd))) == proposal.flat25_usd == hp.flat_quote(exact)
    assert cell != "17.03"
    assert price(Decimal(cell)) == proposal.tiered_usd
    assert hp.flat_quote(Decimal(cell)) == proposal.flat25_usd
    _assert_reprices(proposal, cell)


def test_yen_117_72_kg_0_5_tier_34_not_22_77() -> None:
    proposal, cell, _text = _propose_and_markdown(ROW_117)
    exact = hp.landed_usd(Decimal("117.72"), Decimal("0.5"))
    assert proposal.kg_source == "intake"
    assert proposal.landed_usd != 22.77
    assert str(proposal.landed_usd) != "22.77"
    assert cell != "22.77"
    assert price(Decimal("22.77")) == 33  # old 4dp quote
    assert proposal.tiered_usd == price(exact) == 34
    assert price(Decimal(str(proposal.landed_usd))) == proposal.tiered_usd
    assert hp.flat_quote(Decimal(str(proposal.landed_usd))) == proposal.flat25_usd == hp.flat_quote(exact)
    assert price(Decimal(cell)) == proposal.tiered_usd
    assert hp.flat_quote(Decimal(cell)) == proposal.flat25_usd
    _assert_reprices(proposal, cell)


def test_yen_143_2_kg_1_tier_44_not_31_82() -> None:
    proposal, cell, _text = _propose_and_markdown(ROW_143)
    exact = hp.landed_usd(Decimal("143.2"), Decimal("1"))
    assert proposal.kg_source == "intake"
    assert proposal.landed_usd != 31.82
    assert str(proposal.landed_usd) != "31.82"
    assert cell != "31.82"
    assert price(Decimal("31.82")) == 43
    assert proposal.tiered_usd == price(exact) == 44
    assert price(Decimal(str(proposal.landed_usd))) == proposal.tiered_usd
    assert hp.flat_quote(Decimal(str(proposal.landed_usd))) == proposal.flat25_usd == hp.flat_quote(exact)
    assert price(Decimal(cell)) == proposal.tiered_usd
    assert hp.flat_quote(Decimal(cell)) == proposal.flat25_usd
    _assert_reprices(proposal, cell)


def test_yen_9_kg_0_8_markdown_not_9_75() -> None:
    proposal, cell, _text = _propose_and_markdown(ROW_9)
    exact = hp.landed_usd(Decimal("9"), Decimal("0.8"))
    four = exact.quantize(Decimal("0.0001"))
    assert four == Decimal("9.7547")
    assert price(Decimal(str(float(four)))) == 16
    assert hp.flat_quote(Decimal(str(float(four)))) == hp.flat_quote(exact)
    assert price(Decimal("9.75")) == 15
    assert hp.flat_quote(Decimal("9.75")) == 13
    assert proposal.kg_source == "intake"
    assert proposal.tiered_usd == price(exact) == 16
    assert proposal.flat25_usd == hp.flat_quote(exact)
    assert cell != "9.75"
    assert price(Decimal(cell)) == 16 == proposal.tiered_usd
    assert hp.flat_quote(Decimal(cell)) == proposal.flat25_usd
    _assert_reprices(proposal, cell)


def test_a29_category_proxy_keeps_four_dp_and_prints_19_52() -> None:
    assert "kg" not in ROW_A29
    proposal, cell, md = _propose_and_markdown(ROW_A29)
    assert proposal.kg_source == "A category proxy"
    assert proposal.kg == 0.3
    assert proposal.landed_usd == 19.5177
    assert proposal.tiered_usd == 30
    assert proposal.flat25_usd == 27
    assert price(Decimal(str(proposal.landed_usd))) == 30
    assert hp.flat_quote(Decimal(str(proposal.landed_usd))) == proposal.flat25_usd
    assert cell == "19.52"
    assert "| A29 | 110 |" in md
    _assert_reprices(proposal, cell)


def test_non_boundary_row_prints_two_decimals() -> None:
    proposal, cell, _text = _propose_and_markdown(ROW_A29)
    assert cell == f"{proposal.landed_usd:.2f}" == "19.52"
    assert len(cell.split(".")[1]) == 2


def test_digest_lock_5_85_is_11_and_5_86_is_10() -> None:
    assert price(Decimal("5.85")) == 11
    assert price(Decimal("5.86")) == 10


def test_every_quoted_proposal_reprices_from_stored_and_markdown() -> None:
    for row in QUOTED_ROWS:
        proposal, cell, _text = _propose_and_markdown(row)
        stored = Decimal(str(proposal.landed_usd))
        printed = Decimal(cell)
        assert price(stored) == proposal.tiered_usd, (row["ma"], str(stored), proposal.tiered_usd)
        assert hp.flat_quote(stored) == proposal.flat25_usd, (row["ma"], str(stored), proposal.flat25_usd)
        assert price(printed) == proposal.tiered_usd, (row["ma"], cell, proposal.tiered_usd)
        assert hp.flat_quote(printed) == proposal.flat25_usd, (row["ma"], cell, proposal.flat25_usd)


def test_tiny_cost_0_01_kg_0_0002_cell_not_0_00() -> None:
    row = {"ma": "B01", "kind": "B", "cost_cny": "0.01", "kg": "0.0002"}
    exact = hp.landed_usd(Decimal("0.01"), Decimal("0.0002"))
    proposal, cell, _text = _propose_and_markdown(row)
    assert proposal.kg_source == "intake"
    assert cell != "0.00"
    assert proposal.tiered_usd == price(exact)
    assert proposal.flat25_usd == hp.flat_quote(exact)
    stored = Decimal(str(proposal.landed_usd))
    printed = Decimal(cell)
    assert price(stored) == proposal.tiered_usd == price(exact)
    assert hp.flat_quote(stored) == proposal.flat25_usd == hp.flat_quote(exact)
    assert price(printed) == proposal.tiered_usd == price(exact)
    assert hp.flat_quote(printed) == proposal.flat25_usd == hp.flat_quote(exact)
    _assert_reprices(proposal, cell)


def test_tinier_cost_0_0001_stored_landed_not_zero() -> None:
    row = {"ma": "B02", "kind": "B", "cost_cny": "0.0001", "kg": "0.000001"}
    exact = hp.landed_usd(Decimal("0.0001"), Decimal("0.000001"))
    quantized = exact.quantize(Decimal("0.0001"))
    assert quantized == 0
    refused = False
    try:
        price(quantized)
    except ValueError:
        refused = True
    assert refused
    proposal, cell, _text = _propose_and_markdown(row)
    assert proposal.landed_usd != 0
    assert proposal.landed_usd != 0.0
    assert price(Decimal(str(proposal.landed_usd))) == proposal.tiered_usd == price(exact)
    assert hp.flat_quote(Decimal(str(proposal.landed_usd))) == proposal.flat25_usd == hp.flat_quote(exact)
    _assert_reprices(proposal, cell)


def test_float_cliff_20_25_keeps_tier_31() -> None:
    yen = Decimal("79.559982000000006723")
    kg = Decimal("0.8")
    exact = hp.landed_usd(yen, kg)
    assert float(exact) == 20.25
    assert price(Decimal("20.25")) == 30
    assert price(exact) == 31
    assert hp.flat_quote(exact) == 28
    row = {"ma": "B31", "kind": "B", "cost_cny": "79.559982000000006723", "kg": "0.8"}
    proposal, cell, _text = _propose_and_markdown(row)
    stored_float = hp.sheet_landed(exact)
    assert proposal.landed_usd == stored_float
    assert price(Decimal(str(stored_float))) == 31
    assert hp.flat_quote(Decimal(str(stored_float))) == 28
    assert price(Decimal(str(proposal.landed_usd))) == proposal.tiered_usd == 31
    assert hp.flat_quote(Decimal(str(proposal.landed_usd))) == proposal.flat25_usd == 28
    assert cell != "20.25"
    assert price(Decimal(cell)) == 31
    assert hp.flat_quote(Decimal(cell)) == 28
    _assert_reprices(proposal, cell)


def test_float_cliff_exact_tier_10_not_printed_5_85() -> None:
    # price(Decimal("5.85")) stays 11; test_digest_lock_5_85_is_11_and_5_86_is_10 holds that.
    yen = Decimal("3.96657000000000006723")
    kg = Decimal("0.5")
    exact = hp.landed_usd(yen, kg)
    assert float(exact) == 5.85
    assert price(exact) == 10
    assert price(exact) != 11
    row = {"ma": "B85", "kind": "B", "cost_cny": "3.96657000000000006723", "kg": "0.5"}
    proposal, cell, _text = _propose_and_markdown(row)
    stored_float = hp.sheet_landed(exact)
    assert proposal.landed_usd == stored_float
    assert proposal.tiered_usd == price(exact) == 10
    assert proposal.flat25_usd == hp.flat_quote(exact)
    assert price(Decimal(str(proposal.landed_usd))) == proposal.tiered_usd == price(exact)
    assert hp.flat_quote(Decimal(str(proposal.landed_usd))) == proposal.flat25_usd == hp.flat_quote(exact)
    assert cell != "5.85"
    assert price(Decimal(cell)) == 10
    assert hp.flat_quote(Decimal(cell)) == proposal.flat25_usd
    _assert_reprices(proposal, cell)
