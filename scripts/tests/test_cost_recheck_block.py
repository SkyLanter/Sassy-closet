"""Signed-out Taobao cost recheck is not price evidence and not gone evidence."""
import json

import pytest

import boss_decisions as bd
import cost_recheck_block
import daily_summary_draft as d

_NO_FLAG = object()
TRUE_FLAGS = [True, 1, "true", "TRUE", " true ", " yes ", "Y", "y", "1", " 1 ", "\nYes\t"]
FALSE_FLAGS = [False, 0, "false", "no", "", None]
BLOCKED_LINE = (
    "Taobao cost recheck: blocked on a signed-out read. "
    "Unreachable rows and price deltas in this file are not used."
)
SIGNIN_LINE = "Taobao still needs your sign-in."
DIGEST_Z72 = "- [intake_mismatch] Z72  first_seen=2000-01-03  source=out/qc/note.md\n"
PUBLIC_Z72 = "- Intake cost doesn't match public Taobao price: Z72"


def recheck_doc(flag=_NO_FLAG):
    doc = {
        "counts": {"unreachable": 8},
        "unreachable_mas": ["Z72"],
        "persistent_new_unreachable": ["Z71"],
        "live_price_changed": ["Z72"],
        "new_under_or_loss": ["Z71"],
    }
    if flag is not _NO_FLAG:
        doc["taobao_login_needed"] = flag
    return doc


def summary_text(cost, digest_text=""):
    return d.build(
        None,
        cost,
        d.parse_digest(digest_text),
        None,
        None,
        None,
        None,
        "2000-01-01",
        meta_status={"ig": ("pass", ""), "fb": ("pass", "")},
        decisions=False,
    )


def write_cost_summary(root, date, doc):
    folder = root / "verify" / "cost-recheck"
    folder.mkdir(parents=True, exist_ok=True)
    (folder / f"summary.{date}.json").write_text(json.dumps(doc), encoding="utf-8")


@pytest.mark.parametrize("flag", TRUE_FLAGS)
def test_login_blocked_true_for_explicit_flag(flag):
    doc = recheck_doc(flag)
    assert cost_recheck_block.login_blocked(doc) is True
    assert cost_recheck_block.evidence(doc) == {}
    assert doc["unreachable_mas"] == ["Z72"]
    assert doc["persistent_new_unreachable"] == ["Z71"]
    assert doc["live_price_changed"] == ["Z72"]


@pytest.mark.parametrize("flag", FALSE_FLAGS)
def test_login_blocked_false_for_negative_flag(flag):
    doc = recheck_doc(flag)
    assert cost_recheck_block.login_blocked(doc) is False
    assert cost_recheck_block.evidence(doc) is doc


def test_login_blocked_false_when_flag_missing():
    doc = recheck_doc()
    assert cost_recheck_block.login_blocked(doc) is False
    assert cost_recheck_block.evidence(doc) is doc


def test_huge_unreachable_without_flag_stays_usable():
    doc = {
        "counts": {"unreachable": 1000},
        "unreachable_mas": ["Z72"] * 1000,
        "persistent_new_unreachable": ["Z71"],
        "live_price_changed": [],
        "new_under_or_loss": [],
    }
    assert cost_recheck_block.login_blocked(doc) is False
    assert cost_recheck_block.evidence(doc) is doc
    text = summary_text(doc)
    assert "- Should Z71 go on hold?" in text
    assert "listings unreachable" in text
    assert BLOCKED_LINE not in text


@pytest.mark.parametrize("doc", [None, [], ["Z71"], ["Z72", "Z71"], "true"])
def test_non_dict_is_not_blocked_and_not_evidence(doc):
    assert cost_recheck_block.login_blocked(doc) is False
    assert cost_recheck_block.evidence(doc) == {}


@pytest.mark.parametrize("flag", [[], ["true"], [True], [1]])
def test_list_flag_is_not_blocked(flag):
    doc = recheck_doc(flag)
    assert cost_recheck_block.login_blocked(doc) is False
    assert cost_recheck_block.evidence(doc) is doc


@pytest.mark.parametrize("flag", TRUE_FLAGS)
def test_blocked_summary_drops_price_and_gone(flag):
    text = summary_text(recheck_doc(flag), DIGEST_Z72)
    assert f"{BLOCKED_LINE}\n{SIGNIN_LINE}" in text
    assert text.count(BLOCKED_LINE) == 1
    assert text.count(SIGNIN_LINE) == 1
    assert "listings unreachable" not in text
    assert "live price change" not in text
    assert "new under-price/loss" not in text
    assert "Newly gone" not in text
    assert "go on hold?" not in text
    assert "Taobao listing unreachable or gone" not in text
    assert PUBLIC_Z72 in text
    assert "Z71" not in text
    assert text.count("Z72") == 1


def test_unblocked_persistent_unreachable_still_asks_hold():
    text = summary_text(recheck_doc())
    assert "- Should Z71 go on hold?" in text
    assert "Newly gone on Taobao and still live: Z71." in text
    assert BLOCKED_LINE not in text


@pytest.mark.parametrize("flag", FALSE_FLAGS)
def test_negative_flag_still_asks_hold(flag):
    text = summary_text(recheck_doc(flag))
    assert "- Should Z71 go on hold?" in text
    assert "listings unreachable" in text
    assert BLOCKED_LINE not in text


def _compile(tmp_path, cost):
    cost_path = tmp_path / "verify" / "cost-recheck" / "summary.2000-01-05.json"
    return bd.compile_decisions(tmp_path, "2000-01-05", DIGEST_Z72, cost, cost_path)


@pytest.mark.parametrize("flag", TRUE_FLAGS)
def test_compile_blocked_cost_skips_gone_and_keeps_mismatch(tmp_path, flag):
    cost = {
        "taobao_login_needed": flag,
        "persistent_new_unreachable": ["Z71"],
        "unreachable_mas": ["Z72"],
    }
    decided = _compile(tmp_path, cost)
    assert [(item["cat"], item["ma"]) for item in decided] == [("intake_mismatch", "Z72")]


@pytest.mark.parametrize("flag", FALSE_FLAGS)
def test_compile_negative_flag_keeps_gone_and_reclassifies(tmp_path, flag):
    cost = {
        "taobao_login_needed": flag,
        "persistent_new_unreachable": ["Z71"],
        "unreachable_mas": ["Z72"],
    }
    decided = _compile(tmp_path, cost)
    pairs = [(item["cat"], item["ma"]) for item in decided]
    assert ("gone_hold", "Z71") in pairs
    assert ("intake_unreachable", "Z72") in pairs
    assert ("intake_mismatch", "Z72") not in pairs


def test_streak_start_skips_signed_out_day(tmp_path):
    day1, day2, day3 = "2000-02-01", "2000-02-02", "2000-02-03"
    write_cost_summary(tmp_path, day1, {"unreachable_mas": ["Z71"]})
    write_cost_summary(tmp_path, day2, {
        "taobao_login_needed": True,
        "unreachable_mas": ["Z71", "Z72", "Z73"],
    })
    write_cost_summary(tmp_path, day3, {"unreachable_mas": ["Z71", "Z73"]})
    assert bd.streak_start(tmp_path, day3, "Z71") == day1
    assert bd.streak_start(tmp_path, day3, "Z72") is None
    assert bd.streak_start(tmp_path, day3, "Z73") == day3
    assert bd.streak_start(tmp_path, day2, "Z71") == day1
    assert bd.streak_start(tmp_path, day2, "Z72") is None


def test_streak_start_unblocked_run_begins_at_first_listed_day(tmp_path):
    day1, day2, day3 = "2000-03-01", "2000-03-02", "2000-03-03"
    write_cost_summary(tmp_path, day1, {"unreachable_mas": ["Z71"]})
    write_cost_summary(tmp_path, day2, {"unreachable_mas": ["Z71", "Z72"]})
    write_cost_summary(tmp_path, day3, {"unreachable_mas": ["Z71", "Z72"]})
    assert bd.streak_start(tmp_path, day3, "Z71") == day1
    assert bd.streak_start(tmp_path, day3, "Z72") == day2
