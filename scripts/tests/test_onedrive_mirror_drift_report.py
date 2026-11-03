import importlib.util
import json
from pathlib import Path
spec = importlib.util.spec_from_file_location("r", Path(__file__).resolve().parents[1] / "onedrive_mirror_drift_report.py")
r = importlib.util.module_from_spec(spec); spec.loader.exec_module(r)


def test_fixture_drift(capsys):
    before = r.FIXTURE.read_bytes()
    assert r.main([]) == 0
    out = capsys.readouterr().out
    assert "| D05 | 28 | 26 | DRIFT |" in out
    assert "| V03 | 24 | 21 | DRIFT |" in out
    assert "\n2 mismatch(es). Read-only; mirror refresh needs Boss OK." in out
    assert r.main(["--strict"]) == 1
    assert r.FIXTURE.read_bytes() == before


def test_norm_ma_compare():
    rows = r.compare({"d005": 28, " v3 ": 24, "S06": 25}, {"D05": 26, "V03": 24})
    assert rows == [
        ("D05", [28], [26], "DRIFT"),
        ("S06", [25], None, "NO_LIVE"),
        ("V03", [24], [24], "MATCH"),
    ]


def test_later_lock_does_not_hide_an_earlier_mirror_spelling():
    rows = {ma: (mirror, live, status) for ma, mirror, live, status in r.compare(
        {"S006": 30, "S06": 25},
        {"S06": 25},
    )}
    assert rows["S06"] == ([30, 25], [25], "DRIFT")


def test_later_lock_does_not_hide_an_earlier_live_spelling():
    rows = {ma: status for ma, _mirror, _live, status in r.compare(
        {"S06": 25},
        {"S006": 30, "s06": 25},
    )}
    assert rows["S06"] == "DRIFT"


def test_same_price_on_every_spelling_still_matches():
    rows = r.compare({"S06": 25.0}, {"S006": 25, "S06": 25})
    assert rows == [("S06", [25.0], [25, 25], "MATCH")]


def test_bool_does_not_match_one_dollar(tmp_path, capsys):
    fixture = tmp_path / "mirror.json"
    fixture.write_text(json.dumps({"od_mirror": {"A01": True}, "live": {"A01": 1}}))
    before = fixture.read_bytes()
    assert r.main(["--fixture", str(fixture), "--strict"]) == 1
    out = capsys.readouterr().out
    assert "| A01 | true | 1 | DRIFT |" in out
    assert fixture.read_bytes() == before


def test_non_numeric_does_not_abort_the_table(tmp_path, capsys):
    fixture = tmp_path / "mirror.json"
    fixture.write_text(json.dumps({"od_mirror": {"S06": "nope"}, "live": {"S06": 25}}))
    assert r.main(["--fixture", str(fixture)]) == 0
    out = capsys.readouterr().out
    assert "| S06 | nope | 25 | DRIFT |" in out
