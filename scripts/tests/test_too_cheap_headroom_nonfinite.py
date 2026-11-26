"""--headroom-pct must be a finite percentage, and its report must be strict JSON.

`--headroom-pct nan` crashed the whole check with decimal.InvalidOperation, so the
daily runner got no report at all. `--headroom-pct inf` (or a huge value like
1e400, which parses to inf) wrote `"headroom_pct": Infinity` into the JSON:
json.dumps allows that, but it is not JSON, and a strict reader of the report
fails. Both are typos, never a real warning band.
"""
import json
import math
from dataclasses import replace
from decimal import Decimal
from pathlib import Path

import pytest

import too_cheap_check as tc

LIVE = {"products": [{"ma": "A01", "priceUsd": 30}, {"ma": "S06", "priceUsd": 25}]}
COSTS = "ma,intake_cny,kg\nA01,100,0.3\nS06,60,0.5\n"


def strict_loads(text: str):
    """json.loads that rejects NaN/Infinity, like any non-Python reader."""
    def reject(token):
        raise AssertionError(f"report is not strict JSON: bare {token}")

    return json.loads(text, parse_constant=reject)


def cli(tmp_path: Path, pct: str):
    (tmp_path / "live.json").write_text(json.dumps(LIVE), encoding="utf-8")
    (tmp_path / "costs.csv").write_text(COSTS, encoding="utf-8")
    out = tmp_path / "r.json"
    rc = tc.main(["--live", str(tmp_path / "live.json"), "--costs", str(tmp_path / "costs.csv"),
                  "--headroom-pct", pct, "--out-json", str(out), "--out-md", str(tmp_path / "r.md")])
    return rc, out


def test_nan_percent_is_refused_not_a_crash(tmp_path):
    with pytest.raises(SystemExit) as exit_info:
        cli(tmp_path, "nan")
    assert exit_info.value.code == 2
    assert not (tmp_path / "r.json").exists()


@pytest.mark.parametrize("pct", ["inf", "Infinity", "-inf", "1e400"])
def test_nonfinite_percent_is_refused(tmp_path, pct):
    with pytest.raises(SystemExit) as exit_info:
        cli(tmp_path, pct)
    assert exit_info.value.code == 2
    assert not (tmp_path / "r.json").exists()


def test_finite_percent_report_is_strict_json(tmp_path):
    rc, out = cli(tmp_path, "7.5")
    assert rc == 0
    doc = strict_loads(out.read_text(encoding="utf-8"))
    assert doc["headroom_pct"] == 7.5 and doc["writes"] == "none"


def test_zero_percent_report_is_strict_json(tmp_path):
    rc, out = cli(tmp_path, "0")
    assert rc == 0
    assert strict_loads(out.read_text(encoding="utf-8"))["headroom_pct"] == 0


def test_summarize_refuses_a_nonfinite_band():
    key = "intake" + "_cny"
    rows = tc.evaluate({"A01": 30}, {"A01": {key: "100", "kg": "0.3"}}, tc.HeldPolicy(held=(), never_list=()))
    for bad in (math.nan, math.inf):
        with pytest.raises(ValueError):
            tc.summarize(rows, bad)


def test_headroom_band_math_unchanged():
    # A real priced row, moved 10% above its own target.
    key = "intake" + "_cny"
    (row,) = tc.evaluate({"B01": 30}, {"B01": {key: "100", "kg": "0.3"}},
                         tc.HeldPolicy(held=(), never_list=()))
    assert row.decision == "ok" and row.target_usd
    at_ten = replace(row, live_usd=round(row.target_usd * 1.1, 2))
    zero, band = tc.headroom([at_ten], 10)
    assert zero == [] and [b["ma"] for b in band] == ["B01"]
    assert band[0]["headroom_usd"] == pytest.approx(round(row.target_usd * 0.1, 2))
    assert Decimal(str(band[0]["headroom_pct"])) == Decimal("10")
