"""Drift report: every S06 spelling is checked against the $25 lock."""
import json

import price_drift_report as drift


def test_thirteen_gaps_and_s06():
    rows = {row[0]: row for row in drift.rows()}
    for code in "A01 A02 A03 A04 B01 B02 J01 J02 K01 P03 P04 P05 S01".split():
        assert rows[code][1] != rows[code][2]
    assert rows["S06"][1] == 25 and rows["S06"][3] is None


def test_norm():
    assert drift.norm("s006") == "S06" and drift.norm(" k3") == "K03"


def _fx(tmp_path, intake_s06, live_s06=25.0):
    payload = {"live": {"S06": live_s06}, "hub": {"S06": 25.0}, "intake": {"S06": intake_s06}}
    path = tmp_path / "fx.json"
    path.write_text(json.dumps(payload))
    return path


def test_s06_blank_intake_warns_on_real_fixture():
    before = drift.FX.read_bytes()
    status, message = drift.s06_intake_check()
    assert status == "WARN" and "Boss" in message
    assert drift.FX.read_bytes() == before


def test_s06_intake_variants(tmp_path):
    assert drift.s06_intake_check(_fx(tmp_path, None))[0] == "WARN"
    assert drift.s06_intake_check(_fx(tmp_path, ""))[0] == "WARN"
    assert drift.s06_intake_check(_fx(tmp_path, 25))[0] == "PASS"
    assert drift.s06_intake_check(_fx(tmp_path, 16))[0] == "FAIL"
    assert drift.s06_intake_check(_fx(tmp_path, 25, live_s06=16))[0] == "FAIL"


def test_s06_lock_is_25():
    assert drift.S06_LOCK == 25.0


def _map(tmp_path, live, intake):
    payload = {"live": live, "hub": {"S06": 25}, "intake": intake}
    path = tmp_path / "fx.json"
    path.write_text(json.dumps(payload))
    return path


def test_earlier_live_spelling_off_lock_fails(tmp_path):
    path = _map(tmp_path, {"S006": 30, "S06": 25}, {"S06": 25})
    assert drift.s06_intake_check(path)[0] == "FAIL"
    table = {row[0]: row for row in drift.rows(path)}
    assert table["S06"][1] == 30


def test_later_intake_spelling_off_lock_fails(tmp_path):
    path = _map(tmp_path, {"S06": 25.0}, {"S06": 25, "s06": 16})
    assert drift.s06_intake_check(path)[0] == "FAIL"


def test_earlier_intake_spelling_off_lock_fails(tmp_path):
    path = _map(tmp_path, {"S06": 25.0}, {"s006": 16, "S06": 25})
    assert drift.s06_intake_check(path)[0] == "FAIL"


def test_non_numeric_live_spelling_fails_without_aborting_the_table(tmp_path):
    path = _map(tmp_path, {"S006": "nope", "S06": 25}, {"S06": 25})
    assert drift.s06_intake_check(path)[0] == "FAIL"
    assert drift.rows(path) == []


def test_bool_live_is_not_the_lock(tmp_path):
    assert drift.s06_intake_check(_fx(tmp_path, 25, live_s06=True))[0] == "FAIL"
