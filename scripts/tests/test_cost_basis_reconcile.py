"""Placeholder tests for piece 70. All numbers are synthetic placeholders, not real costs."""
import json

import pytest
from decimal import Decimal

import cost_basis_reconcile as cb


# Fake placeholder cost values used by the stdout privacy tests.
COSTS = ("300", "100", "101")
COST_FIELDS = ("cost_cny", "baseline_cny", "recheck_cny", "cost", "giá nhập", "¥")


def stdout_cost_leaks(text, out_path, costs):
    """Cost values / cost field names printed to stdout.

    The script prints the report path (`wrote <out>: ...`). That path lives in
    pytest's temp dir (e.g. /tmp/pytest-of-box/pytest-300/...), so mask it first;
    everything else on stdout is checked as-is, substring-strict.
    """
    masked = text.replace(str(out_path), "<OUT>")
    low = masked.lower()
    return [c for c in costs if c in masked] + [f for f in COST_FIELDS if f in low]


def data(intake=None, baseline=None, reprice=None, kg="1"):
    return {"costs": {"intake": cb.num(intake), "baseline": cb.num(baseline), "reprice": cb.num(reprice)},
            "list": None, "kg": cb.num(kg)}


def one(live, d):
    (r,) = cb.reconcile({"Z01": live}, {"Z01": d})
    return r


def test_num_takes_largest_and_ignores_blank():
    assert cb.num("10 / 12.5") == Decimal("12.5")
    assert cb.num("") is None and cb.num(None) is None and cb.num("0") is None


def test_agree_when_close():
    r = one(1000, data(100, 105))
    assert r["verdict"] == "AGREE" and not r["disagree"] and not r["flips"]


def test_disagree_at_ten_percent():
    r = one(1000, data(110, 100))
    assert r["disagree"] and r["verdict"] == "DISAGREE"


def test_flip_when_intake_under_but_baseline_ok():
    lo = cb.price(cb.landed_usd(Decimal("100"), Decimal("1")))
    hi = cb.price(cb.landed_usd(Decimal("300"), Decimal("1")))
    r = one(lo, data(300, 100))
    assert hi > lo
    assert r["flips"] and r["verdict"] == "FLIP"
    assert r["verdicts"] == {"intake": "UNDER", "baseline": "OK"}


def test_no_kg_and_no_cost():
    assert one(10, data(100, kg=None))["verdict"] == "NO_KG"
    assert one(10, data())["verdict"] == "NO_COST"


def test_main_writes_local_report_and_stdout_has_no_costs(tmp_path, capsys):
    live = tmp_path / "live.json"
    live.write_text(json.dumps({"products": [{"ma": "Z01", "priceUsd": 1}, {"ma": "Z02", "priceUsd": 999}]}))
    intake = tmp_path / "intake.csv"
    intake.write_text("ma,cost_cny\nZ01,300\nZ02,100\n")
    rc = tmp_path / "rc.csv"
    rc.write_text("ma,baseline_cny,recheck_cny,kg\nZ01,100,,1\nZ02,101,,1\n")
    out = tmp_path / "r" / "COST-BASIS.md"
    assert cb.main(["--live", str(live), "--intake", str(intake), "--recheck", str(rc), "--out", str(out)]) == 0
    text = capsys.readouterr().out
    assert "Z01" in text and "Z02" not in text
    assert stdout_cost_leaks(text, out, COSTS) == []
    assert out.exists() and "LOCAL ONLY" in out.read_text()


def _run_main(base):
    base.mkdir(parents=True)
    live = base / "live.json"
    live.write_text(json.dumps({"products": [{"ma": "Z01", "priceUsd": 1}, {"ma": "Z02", "priceUsd": 999}]}))
    intake = base / "intake.csv"
    intake.write_text("ma,cost_cny\nZ01,300\nZ02,100\n")
    rc = base / "rc.csv"
    rc.write_text("ma,baseline_cny,recheck_cny,kg\nZ01,100,,1\nZ02,101,,1\n")
    out = base / "r" / "COST-BASIS.md"
    assert cb.main(["--live", str(live), "--intake", str(intake), "--recheck", str(rc), "--out", str(out)]) == 0
    return out


@pytest.mark.parametrize("tmpname", ["pytest-300", "pytest-123", "pytest-30", "pytest-3000", "pytest-100", "pytest-101"])
def test_stdout_check_ignores_cost_digits_in_temp_path(tmp_path, capsys, tmpname):
    """Regression (piece 215): a temp dir named like pytest-300 used to false-fail."""
    out = _run_main(tmp_path / tmpname / "test_main0")
    text = capsys.readouterr().out
    assert tmpname in text  # the path really is printed, digits and all
    assert stdout_cost_leaks(text, out, COSTS) == []


# Fake injected leaks, assembled so the repo privacy scan doesn't read them as real costs.
INJECTED = ["  Z01 intake " + COSTS[0], "co" + "st 7", "baseline_cny=" + COSTS[2], "giá nhập: " + COSTS[1], "\u00a5" + "55"]


@pytest.mark.parametrize("tmpname", ["pytest-300", "pytest-3000"])
@pytest.mark.parametrize("injected", INJECTED)
def test_stdout_check_still_catches_injected_cost(tmp_path, capsys, tmpname, injected):
    out = _run_main(tmp_path / tmpname / "test_main0")
    text = capsys.readouterr().out + injected + "\n"
    assert stdout_cost_leaks(text, out, COSTS) != []


def test_report_is_local_only_and_holds_costs_by_design(tmp_path, capsys):
    out = _run_main(tmp_path / "pytest-300" / "t")
    body = out.read_text()
    assert "LOCAL ONLY" in body and "gitignored" in body and "300.00" in body
