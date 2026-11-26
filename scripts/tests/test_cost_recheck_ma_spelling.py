"""A cost-recheck summary that spells a mã a07 / A007 / ' A07 ' is the same mã.

The flags CSV beside the summary already canonicalizes each row (taobao_unreachable_streak
uses norm_ma), so the same recheck run reports A07 day 3 from the CSV and reports nothing
from the summary. The daily summary then prints an empty unreachable list, drops the
"should it go on hold" question, and Boss decisions opens no gone_hold line. The streak
start date is lost the same way, because the summaries are compared as raw text.
"""
from __future__ import annotations

import json

import boss_decisions as bd
import daily_summary_draft as d
import taobao_unreachable_streak as streak


def _summary(root, day, spelling, *, new_gone=True):
    folder = root / "verify" / "cost-recheck"
    folder.mkdir(parents=True, exist_ok=True)
    doc = {
        "counts": {"unreachable": 1},
        "unreachable_mas": [spelling],
        "persistent_new_unreachable": [spelling] if new_gone else [],
        "live_price_changed": [],
        "new_under_or_loss": [],
    }
    (folder / f"summary.{day}.json").write_text(json.dumps(doc), encoding="utf-8")
    rows = "ma,name,source_link,baseline_cny,flag\n" + f"{spelling},n,L,1,unreachable\n"
    (folder / f"cost-recheck-{day}-flags.csv").write_text(rows, encoding="utf-8")
    return doc


def _text(cost, day):
    return d.build(
        None,
        cost,
        {},
        None,
        None,
        None,
        None,
        day,
        meta_status={"ig": ("pass", ""), "fb": ("pass", "")},
        decisions=False,
    )


def test_mas_canonicalizes_the_spellings_the_flags_csv_already_reads():
    assert d.mas(["a07"]) == ["A07"]
    assert d.mas(["A007"]) == ["A07"]
    assert d.mas([" A07 "]) == ["A07"]
    assert d.mas(["a7"]) == ["A07"]
    assert d.mas(["A07", "a07", " A007 "]) == ["A07"]
    assert d.mas(None) == []
    assert d.mas("A07") == []
    assert d.mas([1, True, None, "not-a-mã", "A7X"]) == []


def test_summary_line_and_hold_question_keep_a_padded_spelling(tmp_path):
    cost = {"counts": {"unreachable": 1}, "unreachable_mas": ["A007"],
            "persistent_new_unreachable": ["A007"], "live_price_changed": [" a07 "],
            "new_under_or_loss": []}
    text = _text(cost, "2026-02-04")
    assert "1 listings unreachable (A07); 1 live price change(s)" in text
    assert "Newly gone on Taobao and still live: A07." in text
    assert "- Should A07 go on hold? Newly gone on Taobao and still live." in text


def test_flags_csv_and_summary_agree_on_the_same_ma(tmp_path):
    doc = _summary(tmp_path, "2026-02-04", "a07")
    csv_runs = streak.load_runs(str(tmp_path / "verify" / "cost-recheck"))
    assert streak.streaks(csv_runs) == {"A07": (1, "2026-02-04")}
    assert d.mas(doc["unreachable_mas"]) == ["A07"]


def test_boss_decisions_opens_gone_hold_for_a_padded_spelling(tmp_path):
    doc = _summary(tmp_path, "2026-02-04", "A007")
    cost_path = tmp_path / "verify" / "cost-recheck" / "summary.2026-02-04.json"
    found = bd.compile_decisions(tmp_path, "2026-02-04", "", doc, cost_path, None, None, None, None)
    gone = [item for item in found if item["cat"] == "gone_hold"]
    assert [item["ma"] for item in gone] == ["A07"]


def test_streak_start_matches_every_spelling_in_the_run(tmp_path):
    _summary(tmp_path, "2026-02-02", "a07")
    _summary(tmp_path, "2026-02-03", "A007")
    _summary(tmp_path, "2026-02-04", " A07 ")
    assert bd.streak_start(tmp_path, "2026-02-04", "A07") == "2026-02-02"
    assert bd.streak_start(tmp_path, "2026-02-04", "a07") == "2026-02-02"


def test_streak_start_still_breaks_on_a_clean_day(tmp_path):
    _summary(tmp_path, "2026-02-02", "A007")
    _summary(tmp_path, "2026-02-03", "a07", new_gone=False)
    # 02-03 lists the mã as unreachable, so the run keeps going back to 02-02
    assert bd.streak_start(tmp_path, "2026-02-03", "A07") == "2026-02-02"
    _summary(tmp_path, "2026-02-04", "A08", new_gone=False)
    assert bd.streak_start(tmp_path, "2026-02-04", "A07") is None
