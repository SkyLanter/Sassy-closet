"""A garbled amount must not crash the too-cheap check or price for hours.

A ¥ or kg cell pasted twice ("1e400", a 30-digit number) crashed the report with
decimal.InvalidOperation. A merely huge one made the tiered search run up to the
sell price, so the daily check looked hung. No real piece lands this high.
"""
import json
from pathlib import Path

import pytest

import too_cheap_check as tc

LIVE = {"products": [{"ma": "B02", "priceUsd": 30}, {"ma": "S06", "priceUsd": 25}]}
COSTS_HEADER = "ma,intake_cny,list_cny,kg"


def cli(tmp_path: Path, intake: str, kg: str = "0.3", listed: str = ""):
    live = tmp_path / "live.json"
    live.write_text(json.dumps(LIVE), encoding="utf-8")
    costs = tmp_path / "costs.csv"
    costs.write_text(f"{COSTS_HEADER}\nB02,{intake},{listed},{kg}\n", encoding="utf-8")
    out = tmp_path / "r.json"
    rc = tc.main(["--live", str(live), "--costs", str(costs),
                  "--out-json", str(out), "--out-md", str(tmp_path / "r.md")])
    return rc, json.loads(out.read_text(encoding="utf-8"))


def row(summary, ma="B02"):
    return next(r for r in summary["rows"] if r["ma"] == ma)


@pytest.mark.parametrize("intake", ["1e400", "1" + "0" * 29])
def test_absurd_intake_is_skipped_not_a_crash(tmp_path, intake):
    rc, s = cli(tmp_path, intake)
    assert rc == 0
    assert row(s)["decision"] == "skip-missing"
    assert "not priced" in row(s)["reason"]
    assert s["counts"]["under"] == 0 and s["counts"]["locked"] == 1


@pytest.mark.parametrize("kg", ["1e400", "1" + "0" * 29])
def test_absurd_kg_is_skipped_not_a_crash(tmp_path, kg):
    rc, s = cli(tmp_path, "100", kg=kg)
    assert rc == 0
    assert row(s)["decision"] == "skip-missing"
    assert "not priced" in row(s)["reason"]


def test_absurd_public_list_yen_never_crashes_the_row(tmp_path):
    rc, s = cli(tmp_path, "100", listed="1e400")
    assert rc == 0
    assert row(s)["decision"] == "ok"
    assert row(s)["list_target_usd"] is None


def test_landed_above_the_ceiling_is_not_priced(tmp_path):
    # Well past any real piece, and the tiered search would walk ~230k dollars.
    rc, s = cli(tmp_path, "1000000")
    assert rc == 0
    assert row(s)["decision"] == "skip-missing"
    assert row(s)["target_usd"] is None
