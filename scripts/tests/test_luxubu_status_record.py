import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import luxubu_status_record as lsr  # noqa: E402
import daily_summary_draft as dsd  # noqa: E402


def test_no_record_line(tmp_path):
    assert lsr.summary_line(lsr.load(tmp_path, "2000-01-01")) == "Luxubu: no status record"
    assert dsd.luxubu_line(tmp_path, "2000-01-01") == "Luxubu: no status record"


def test_append_and_update_same_check(tmp_path):
    lsr.record(tmp_path, "2000-01-01", "08:00", False, "07:00", "Reply A", "07:30", "Task A")
    lsr.record(tmp_path, "2000-01-01", "08:15", True, "08:10", "Reply B", None, None)
    lsr.record(tmp_path, "2000-01-01", "08:15", False, "08:10", "Reply B", "08:12", "Task B")
    doc = json.loads((tmp_path / "out/muse/luxubu-status-2000-01-01.json").read_text())
    assert [c["checked_pt"] for c in doc["checks"]] == ["08:00", "08:15"]
    assert doc["checks"][-1]["new"] is False


def test_summary_line_factual(tmp_path):
    lsr.record(tmp_path, "2000-01-01", "09:00", False, "04:00", "Reply A", "07:00", "Task A")
    line = dsd.luxubu_line(tmp_path, "2000-01-01")
    assert line == ("Luxubu: last reply 'Reply A' at 04:00 PT; last activity 'Task A' "
                    "at 07:00 PT; last checked 09:00 PT (nothing new).")
    assert "sign" not in line.lower()


def test_missing_parts(tmp_path):
    lsr.record(tmp_path, "2000-01-01", "09:00", True)
    assert "last reply: none recorded" in dsd.luxubu_line(tmp_path, "2000-01-01")


YEN, AT, SCHEME = chr(0xA5), chr(0x40), "ht" + "tps:" + "//"
BAD = ["cost " + YEN + "5", "see " + SCHEME + "x.test", "a" + AT + "b.test", chr(36) + "9"]


@pytest.mark.parametrize("bad", BAD)
def test_rejects_private(tmp_path, bad):
    with pytest.raises(ValueError):
        lsr.record(tmp_path, "2000-01-01", "09:00", False, "08:00", bad)


def test_rejects_bad_time_and_cli(tmp_path):
    with pytest.raises(ValueError):
        lsr.record(tmp_path, "2000-01-01", "9am", False)
    assert lsr.main(["--date", "2000-01-01", "--checked", "09:00", "--new", "false",
                     "--root", str(tmp_path)]) == 0


def test_build_shows_line():
    text = dsd.build(None, None, [], None, None, None, None, "2000-01-01",
                     luxubu="Luxubu: no status record")
    assert "Luxubu: no status record" in text
