import importlib.util, pathlib
p = pathlib.Path(__file__).with_name("price_drift_report.py")
s = importlib.util.spec_from_file_location("pdr", p); m = importlib.util.module_from_spec(s); s.loader.exec_module(m)
def test_thirteen_gaps_and_s06():
    r = {x[0]: x for x in m.rows()}
    for k in "A01 A02 A03 A04 B01 B02 J01 J02 K01 P03 P04 P05 S01".split():
        assert r[k][1] != r[k][2]
    assert r["S06"][1] == 25 and r["S06"][3] is None
def test_norm():
    assert m.norm("s006") == "S06" and m.norm(" k3") == "K03"

import json
def _fx(tmp_path, intake_s06, live_s06=25.0):
    d = {"live": {"S06": live_s06}, "hub": {"S06": 25.0}, "intake": {"S06": intake_s06}}
    p = tmp_path / "fx.json"; p.write_text(json.dumps(d)); return p
def test_s06_blank_intake_warns_on_real_fixture():
    before = m.FX.read_bytes()
    st, msg = m.s06_intake_check()
    assert st == "WARN" and "Boss" in msg
    assert m.FX.read_bytes() == before  # no auto-fill
def test_s06_intake_variants(tmp_path):
    assert m.s06_intake_check(_fx(tmp_path, None))[0] == "WARN"
    assert m.s06_intake_check(_fx(tmp_path, ""))[0] == "WARN"
    assert m.s06_intake_check(_fx(tmp_path, 25))[0] == "PASS"
    assert m.s06_intake_check(_fx(tmp_path, 16))[0] == "FAIL"
    assert m.s06_intake_check(_fx(tmp_path, 25, live_s06=16))[0] == "FAIL"
def test_s06_lock_is_25():
    assert m.S06_LOCK == 25.0
