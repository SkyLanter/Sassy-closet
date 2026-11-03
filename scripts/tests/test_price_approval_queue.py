"""Piece 47 price_approval_queue: synthetic fixtures only, no network."""
import json
import urllib.request

import pytest

import daily_shop_check as d
import price_approval_queue as q


@pytest.fixture(autouse=True)
def no_network(monkeypatch):
    def boom(*a, **k):
        raise AssertionError("network used in test")
    monkeypatch.setattr(urllib.request, "urlopen", boom)


def files(tmp_path, held=("A29", "H02", "G01", "S15"), intake=None, approved=None):
    h = tmp_path / "held.json"
    h.write_text(json.dumps({"heldIncomplete": list(held), "neverList": []}))
    i = tmp_path / "intake.json"
    i.write_text(json.dumps(intake if intake is not None else [
        {"ma": "A29", "weight_kg": 0.3, "weight_approved": True,
         "private_a": "SENTINEL_PRIVATE_A", "private_b": "SENTINEL_PRIVATE_B"},
        {"ma": "H02", "sell_usd": 19, "weight_kg": 0.4, "weight_approved": False},
        {"ma": "G01", "sell_usd": 21, "weight_kg": 0.2, "weight_approved": True, "taobao_only": True},
        {"ma": "Z99", "sell_usd": 15, "weight_kg": 0.2, "weight_approved": True, "flags": ["intake_gt_public"]},
        {"ma": "Y88", "sell_usd": 15, "weight_kg": 0.2, "weight_approved": True},
    ]))
    a = tmp_path / "approved.json"
    a.write_text(json.dumps({"approvedGia": approved if approved is not None else {"S15": 30}}))
    return h, i, a


def rep(tmp_path, **kw):
    h, i, a = files(tmp_path, **kw)
    held, src = q.load_held(h)
    return q.run(held, json.loads(i.read_text()), q.load_approved(a), src)


def reasons(r):
    return {x["ma"]: x["reasons"] for x in r["queue"]}


def test_missing_price(tmp_path):
    assert reasons(rep(tmp_path))["A29"] == ["missing_price"]


def test_needs_weight_approval(tmp_path):
    assert reasons(rep(tmp_path))["H02"] == ["needs_weight_approval"]


def test_taobao_only(tmp_path):
    assert reasons(rep(tmp_path))["G01"] == ["taobao_only"]


def test_flagged_non_held_intake(tmp_path):
    r = rep(tmp_path)
    assert reasons(r)["Z99"] == ["flagged"]
    assert [x for x in r["queue"] if x["ma"] == "Z99"][0]["held"] is False


def test_approved_and_complete_not_queued(tmp_path):
    r = reasons(rep(tmp_path))
    assert "S15" not in r and "Y88" not in r


def test_held_without_intake_row_queued(tmp_path):
    r = rep(tmp_path, held=("K09",), intake=[], approved={})
    assert reasons(r)["K09"] == ["missing_price", "needs_weight_approval"]


def test_by_reason_and_waiting(tmp_path):
    r = rep(tmp_path)
    assert r["byReason"]["taobao_only"] == ["G01"]
    assert r["waiting"] == ["A29", "G01", "H02", "Z99"]


def test_no_costs_links_or_customer_data_in_output(tmp_path):
    out = json.dumps(rep(tmp_path)) + q.markdown(rep(tmp_path))
    for bad in ("SENTINEL", "private_", "19", "21", "0.4", "sell_usd", "weight_kg"):
        assert bad not in out


def test_unsafe_flags_dropped(tmp_path):
    r = rep(tmp_path, held=(), approved={}, intake=[
        {"ma": "A30", "sell_usd": 9, "weight_kg": 1, "weight_approved": True,
         "flags": ["ok_flag", "SENTINEL 120", "Bad-Flag/x", "UPPER"]}])
    item = r["queue"][0]
    assert item["reasons"] == ["flagged"] and item["flags"] == ["ok_flag"]


def test_bad_ma_codes_ignored(tmp_path):
    r = rep(tmp_path, held=("A29", "not a code"), intake=[{"ma": "https://x"}], approved={})
    assert r["waiting"] == ["A29"]


def test_main_exit_codes(tmp_path, capsys):
    h, i, a = files(tmp_path)
    assert q.main(["--held", str(h), "--intake", str(i), "--approved", str(a)]) == 1
    (tmp_path / "x").mkdir()
    h2, i2, a2 = files(tmp_path / "x", held=(), intake=[], approved={})
    assert q.main(["--held", str(h2), "--intake", str(i2), "--approved", str(a2)]) == 0
    bad = tmp_path / "bad.json"
    bad.write_text("{nope")
    assert q.main(["--held", str(bad)]) == 2
    assert "nope" not in capsys.readouterr().err


def test_main_json(tmp_path, capsys):
    h, i, a = files(tmp_path)
    q.main(["--held", str(h), "--intake", str(i), "--approved", str(a), "--json"])
    assert json.loads(capsys.readouterr().out)["schema"] == "price-approval-queue/v1"


def test_shared_held_default_includes_a29_h02_g01():
    held, _ = q.load_held(None)
    assert {"A29", "H02", "G01"} <= set(held)


def test_daily_section_warn(tmp_path):
    h, i, a = files(tmp_path)
    ns = type("A", (), {"price_queue_held": h, "price_queue_intake": i, "price_queue_approved": a})()
    sec = d.price_queue_section(ns)
    assert sec["name"] == "price_queue" and sec["status"] == "WARN" and not sec["fail"]
    assert "SENTINEL" not in json.dumps(sec)


def test_daily_section_error_is_warn(tmp_path):
    bad = tmp_path / "bad.json"
    bad.write_text("{")
    ns = type("A", (), {"price_queue_held": bad, "price_queue_intake": None, "price_queue_approved": None})()
    sec = d.price_queue_section(ns)
    assert sec["status"] == "WARN" and not sec["fail"]
