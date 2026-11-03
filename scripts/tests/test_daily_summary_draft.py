import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import daily_summary_draft as d  # noqa: E402

QC = {"overall": "WARN", "fails": [], "warns": ["X99_CODE placeholder free text"],
      "counts": {"live": 3, "held": 1, "intake": 4, "new_since_oct21": 0},
      "s06": {"blob": 25}, "pass2": {"agrees": True}}
COST = {"counts": {"unreachable": 1}, "unreachable_mas": ["Z01"],
        "persistent_new_unreachable": ["Z01"], "live_price_changed": [],
        "new_under_or_loss": [], "wake_reason": "Z01 FREE_TEXT_MUST_NOT_COPY"}
DIG = "- [hold_call] Z01  first_seen=2000-01-01  source=x\nTOTAL 1"
GAPS = {"snapshot_posts": 2, "no_ma": [{"id": "1"}], "no_gia": []}
PROP = {"verdicts": {"Z02": "$30", "Z03": "NEEDS_INPUT"}}


def _b(ig="pass", fb="pass", gaps=GAPS):
    return d.build(QC, COST, d.parse_digest(DIG), gaps, PROP, ig, fb, "2000-01-01")


def test_clear_only_when_both_pass():
    assert "CLEAR" in _b()
    for ig, fb in [("pass", "unchecked"), ("fail", "pass"), ("unchecked", "unchecked")]:
        assert "CLEAR" not in _b(ig, fb).upper().replace("NOT CLEAR", "")


def test_no_free_text_leak():
    t = _b()
    assert "FREE_TEXT" not in t and "placeholder" not in t
    assert "Z02 $30" in t and "Z03" in t and "Hold call: Z01" in t


def test_no_report_not_counted():
    assert "not counted" in _b(gaps=None)


def test_notes_fallback_without_snapshot():
    g = {"snapshot_posts": 0, "no_ma": [["fb", "reel", "1000000001"]],
         "no_gia": [["fb", "post", "ma:Z05"], ["fb", "reel", "1000000001"], ["ig", "post", "ma:Z06"]]}
    t = _b(gaps=g)
    assert "from QC notes" in t and "1 post(s) with no mã, 3 with no Giá" in t
    assert "FB reel 1000000001" in t and "FB post Z05" in t and "IG post Z06" in t


def test_newly_gone_is_hold_question():
    t = _b()
    assert "- Should Z01 go on hold?" in t


def test_under_price_warn_to_intake_mismatch():
    qc = dict(QC, warns=["INTAKE_COST_VS_LIVE Z07 (placeholder) and Z08 under-price", "OTHER_CODE Z09 note"])
    t = d.build(qc, COST, d.parse_digest(DIG), GAPS, PROP, "pass", "pass", "2000-01-01")
    assert "Under-priced at intake cost (midnight QC): Z07, Z08" in t and "Z09" not in t and "placeholder" not in t


def test_mismatch_split_by_reason():
    qc = dict(QC, warns=["INTAKE_COST_VS_LIVE Z07 under-price"])
    cost = dict(COST, unreachable_mas=["Z01", "Z10", "Z11"], persistent_new_unreachable=["Z01"])
    dig = ("- [intake_mismatch] Z01  first_seen=2000-01-01  source=x\n"
           "- [intake_mismatch] Z10  first_seen=2000-01-01  source=x\n"
           "- [intake_mismatch] Z12  first_seen=2000-01-01  source=x\nTOTAL 3")
    t = d.build(qc, cost, d.parse_digest(dig), GAPS, PROP, "pass", "pass", "2000-01-01")
    assert "Under-priced at intake cost (midnight QC): Z07\n" in t
    assert "Taobao listing unreachable or gone: Z10\n" in t
    assert "Intake cost doesn't match public Taobao price: Z12\n" in t
    assert "Intake vs live mismatch" not in t and "Z11" not in t.split("Waiting on you:")[1]
    assert "Should Z01 go on hold?" in t and t.split("Waiting on you:")[1].count("Z01") == 1


def test_main_writes_file_only(tmp_path):
    for n, o in [("qc.json", QC), ("c.json", COST), ("g.json", GAPS), ("p.json", PROP)]:
        (tmp_path / n).write_text(json.dumps(o))
    (tmp_path / "d.txt").write_text(DIG)
    out = tmp_path / "out"
    d.main(["--date", "2000-01-01", "--qc", str(tmp_path / "qc.json"), "--cost", str(tmp_path / "c.json"),
            "--digest", str(tmp_path / "d.txt"), "--gaps", str(tmp_path / "g.json"),
            "--proposal", str(tmp_path / "p.json"), "--out-dir", str(out)])
    assert [p.name for p in out.iterdir()] == ["daily-summary-2000-01-01.md"]
