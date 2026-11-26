"""A catalog row that is not on the shop is not a live sell price.

The catalog keeps a sold piece's last price (sell-contract: sold may keep priceUsd)
but the shop hides it, and a hold piece shows an inbox-price label, not a $. The
check read every catalog row as live, so a sold piece still sitting at its old low
price was reported as UNDER and failed the daily check: Boss was told to raise the
price of a piece that is no longer for sale.
"""
import json

import pytest

import too_cheap_check as tc

COSTS = "ma,intake_cny,kg\nA01,100,0.3\nZ03,100,0.3\nH05,100,0.3\nS06,60,0.5\n"
A01 = {"ma": "A01", "priceUsd": 30, "status": "available"}
S06 = {"ma": "S06", "priceUsd": 25, "status": "available"}
SOLD_LOW = {"ma": "Z03", "priceUsd": 5, "status": "sold"}
HOLD_LOW = {"ma": "H05", "priceUsd": 5, "status": "hold"}


def catalog(tmp_path, *rows):
    path = tmp_path / "live.json"
    path.write_text(json.dumps({"products": list(rows)}), encoding="utf-8")
    return path


def report(tmp_path, live):
    costs = tmp_path / "costs.csv"
    costs.write_text(COSTS, encoding="utf-8")
    out = tmp_path / "r.json"
    rc = tc.main(["--live", str(live), "--costs", str(costs),
                  "--out-json", str(out), "--out-md", str(tmp_path / "r.md")])
    return rc, json.loads(out.read_text(encoding="utf-8"))


def test_sold_row_is_not_reported_under(tmp_path):
    rc, s = report(tmp_path, catalog(tmp_path, A01, S06, SOLD_LOW))
    assert rc == 0
    assert s["outcome"] == "QUIET_OK"
    assert s["under_target"] == []
    assert [r["ma"] for r in s["rows"]] == ["A01", "S06"]


def test_hold_row_is_not_a_live_sell_price(tmp_path):
    rc, s = report(tmp_path, catalog(tmp_path, A01, S06, HOLD_LOW))
    assert rc == 0
    assert s["under_target"] == []
    assert [r["ma"] for r in s["rows"]] == ["A01", "S06"]


def test_available_row_still_reported_under(tmp_path):
    low = {"ma": "Z03", "priceUsd": 5, "status": "available"}
    rc, s = report(tmp_path, catalog(tmp_path, A01, S06, low))
    assert rc == 0 and s["outcome"] == "UNDER_FOUND"
    assert [r["ma"] for r in s["under_target"]] == ["Z03"]


def test_live_count_counts_only_shop_rows(tmp_path):
    _, s = report(tmp_path, catalog(tmp_path, A01, S06, SOLD_LOW, HOLD_LOW))
    assert s["live_count"] == 2


@pytest.mark.parametrize("status", ["sold", "hold", " sold ", "SOLD", "Hold"])
def test_any_off_shop_status_is_not_priced(tmp_path, status):
    off = {"ma": "Z03", "priceUsd": 5, "status": status}
    _, s = report(tmp_path, catalog(tmp_path, A01, S06, off))
    assert "Z03" not in [r["ma"] for r in s["rows"]]
    assert s["outcome"] == "QUIET_OK"


@pytest.mark.parametrize("status", ["available", "live", "active", "in_stock", "", None])
def test_shop_live_statuses_are_priced(tmp_path, status):
    row = {"ma": "Z03", "priceUsd": 5}
    if status is not None:
        row["status"] = status
    _, s = report(tmp_path, catalog(tmp_path, A01, S06, row))
    assert [r["ma"] for r in s["under_target"]] == ["Z03"]


def test_prices_map_has_no_status_so_all_rows_stay(tmp_path):
    live = tmp_path / "prices.json"
    live.write_text(json.dumps({"prices": {"A01": 30, "S06": 25, "Z03": 5}}), encoding="utf-8")
    _, s = report(tmp_path, live)
    assert [r["ma"] for r in s["under_target"]] == ["Z03"]
    assert s["live_count"] == 3
