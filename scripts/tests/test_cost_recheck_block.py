"""Signed-out Taobao cost recheck is not price evidence and not gone evidence."""
import json

import pytest

import boss_decisions as bd
import cost_recheck_block
import daily_summary_draft as d

_NO_FLAG = object()
# Blocked: JSON true, int 1, float 1.0, and true/yes/y/1 with any case or whitespace.
TRUE_FLAGS = [True, 1, 1.0, "true", "TRUE", " true ", " yes ", "Y", "y", "1", " 1 ", "\nYes\t"]
# Not a block, and must not print the sign-in line. false/no ignore case and whitespace.
# Float 0.0 is not 1.0. The string "1.0" is not the float 1.0.
FALSE_FLAGS = [
    False, 0, 0.0, "false", "FALSE", " False ", "no", "NO", " no ", "\nNo\t", "", None, "1.0",
]
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
    assert SIGNIN_LINE not in text


@pytest.mark.parametrize("raw", ["1.0", "1e0", "1E0"])
def test_json_float_one_is_blocked_everywhere(tmp_path, raw):
    flag = json.loads(raw)
    assert type(flag) is float and flag == 1.0
    doc = recheck_doc(flag)
    assert cost_recheck_block.login_blocked(doc) is True
    assert cost_recheck_block.evidence(doc) == {}
    text = summary_text(doc)
    assert f"{BLOCKED_LINE}\n{SIGNIN_LINE}" in text
    assert text.count(SIGNIN_LINE) == 1
    assert "go on hold?" not in text
    decided = _compile(tmp_path, doc)
    assert [(item["cat"], item["ma"]) for item in decided] == [("intake_mismatch", "Z72")]


@pytest.mark.parametrize("flag", [1.5, 2.0, "1e0", "yes.", "on"])
def test_near_miss_flags_are_not_blocked(flag):
    doc = recheck_doc(flag)
    assert cost_recheck_block.login_blocked(doc) is False
    text = summary_text(doc)
    assert SIGNIN_LINE not in text
    assert BLOCKED_LINE not in text
    assert "- Should Z71 go on hold?" in text


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


@pytest.mark.parametrize("flag", [" false ", "\nNO\t", "No"])
def test_streak_start_false_and_no_strings_still_count(tmp_path, flag):
    day = "2000-05-01"
    write_cost_summary(tmp_path, day, {
        "taobao_login_needed": flag,
        "unreachable_mas": ["Z71"],
    })
    assert bd.streak_start(tmp_path, day, "Z71") == day


def test_streak_start_float_one_skips_the_day(tmp_path):
    day1, day2 = "2000-05-02", "2000-05-03"
    write_cost_summary(tmp_path, day1, {"unreachable_mas": ["Z71"]})
    write_cost_summary(tmp_path, day2, {
        "taobao_login_needed": 1.0,
        "unreachable_mas": ["Z71", "Z72"],
    })
    assert bd.streak_start(tmp_path, day2, "Z71") == day1
    assert bd.streak_start(tmp_path, day2, "Z72") is None


def test_streak_start_reads_utf8_bom_summary(tmp_path):
    day1, day2 = "2000-04-01", "2000-04-02"
    folder = tmp_path / "verify" / "cost-recheck"
    folder.mkdir(parents=True)

    def write(date, doc):
        raw = b"\xef\xbb\xbf" + json.dumps(doc).encode("utf-8")
        (folder / f"summary.{date}.json").write_bytes(raw)

    write(day1, {"unreachable_mas": ["Z71"]})
    write(day2, {
        "taobao_login_needed": True,
        "unreachable_mas": ["Z71", "Z72"],
    })
    assert d.load_json(folder / f"summary.{day2}.json")["taobao_login_needed"] is True
    assert bd.streak_start(tmp_path, day2, "Z71") == day1
    assert bd.streak_start(tmp_path, day2, "Z72") is None


def test_streak_start_unblocked_run_begins_at_first_listed_day(tmp_path):
    day1, day2, day3 = "2000-03-01", "2000-03-02", "2000-03-03"
    write_cost_summary(tmp_path, day1, {"unreachable_mas": ["Z71"]})
    write_cost_summary(tmp_path, day2, {"unreachable_mas": ["Z71", "Z72"]})
    write_cost_summary(tmp_path, day3, {"unreachable_mas": ["Z71", "Z72"]})
    assert bd.streak_start(tmp_path, day3, "Z71") == day1
    assert bd.streak_start(tmp_path, day3, "Z72") == day2


def _summary_file(root, date):
    folder = root / "verify" / "cost-recheck"
    folder.mkdir(parents=True, exist_ok=True)
    return folder / f"summary.{date}.json"


def test_load_summary_missing_path(tmp_path):
    path = tmp_path / "verify" / "cost-recheck" / "summary.2000-06-01.json"
    assert cost_recheck_block.load_summary(path) == ("missing", None)
    with pytest.raises(FileNotFoundError):
        cost_recheck_block.read_json(path)


def test_load_summary_lone_brace_is_bad(tmp_path):
    path = _summary_file(tmp_path, "2000-06-02")
    path.write_text("{", encoding="utf-8")
    assert cost_recheck_block.load_summary(path) == ("bad", None)
    with pytest.raises(json.JSONDecodeError):
        cost_recheck_block.read_json(path)


def test_load_summary_empty_file_is_bad(tmp_path):
    path = _summary_file(tmp_path, "2000-06-03")
    path.write_text("", encoding="utf-8")
    assert cost_recheck_block.load_summary(path) == ("bad", None)


def test_load_summary_truncated_object_is_bad(tmp_path):
    path = _summary_file(tmp_path, "2000-06-04")
    path.write_text('{"unreachable_mas":', encoding="utf-8")
    assert cost_recheck_block.load_summary(path) == ("bad", None)


def test_load_summary_invalid_utf8_is_bad(tmp_path):
    path = _summary_file(tmp_path, "2000-06-05")
    path.write_bytes(b"\xff\xfe{")
    assert cost_recheck_block.load_summary(path) == ("bad", None)


def test_load_summary_bom_plus_brace_is_bad(tmp_path):
    path = _summary_file(tmp_path, "2000-06-06")
    path.write_bytes(b"\xef\xbb\xbf{")
    assert cost_recheck_block.load_summary(path) == ("bad", None)


def test_load_summary_bom_login_needed_is_blocked(tmp_path):
    doc = {"taobao_login_needed": True, "unreachable_mas": ["Z71"]}
    path = _summary_file(tmp_path, "2000-06-07")
    path.write_bytes(b"\xef\xbb\xbf" + json.dumps(doc).encode("utf-8"))
    state, loaded = cost_recheck_block.load_summary(path)
    assert state == "blocked"
    assert loaded == doc
    assert loaded["taobao_login_needed"] is True


def test_load_summary_bom_without_flag_is_ok(tmp_path):
    doc = {"unreachable_mas": ["Z71"]}
    path = _summary_file(tmp_path, "2000-06-08")
    path.write_bytes(b"\xef\xbb\xbf" + json.dumps(doc).encode("utf-8"))
    assert cost_recheck_block.load_summary(path) == ("ok", doc)


@pytest.mark.parametrize("body", ["null", "[]", "true"])
def test_load_summary_non_dict_json_is_bad(tmp_path, body):
    path = _summary_file(tmp_path, "2000-06-09")
    path.write_text(body, encoding="utf-8")
    assert cost_recheck_block.load_summary(path) == ("bad", None)


def test_load_summary_whitespace_false_string_is_ok(tmp_path):
    doc = {"taobao_login_needed": " false ", "unreachable_mas": ["Z71"]}
    write_cost_summary(tmp_path, "2000-06-10", doc)
    path = tmp_path / "verify" / "cost-recheck" / "summary.2000-06-10.json"
    state, loaded = cost_recheck_block.load_summary(path)
    assert state == "ok"
    assert loaded == doc
    assert cost_recheck_block.login_blocked(loaded) is False


def test_streak_start_skips_brace_between_real_days(tmp_path):
    day1, day2, day3 = "2000-07-01", "2000-07-02", "2000-07-03"
    write_cost_summary(tmp_path, day1, {"unreachable_mas": ["Z71"]})
    (tmp_path / "verify" / "cost-recheck" / f"summary.{day2}.json").write_text("{", encoding="utf-8")
    write_cost_summary(tmp_path, day3, {"unreachable_mas": ["Z71"]})
    assert bd.streak_start(tmp_path, day3, "Z71") == day1
    assert bd.streak_start(tmp_path, day3, "Z72") is None


def test_streak_start_only_brace_is_not_a_streak_day(tmp_path):
    day = "2000-07-04"
    path = _summary_file(tmp_path, day)
    path.write_text("{", encoding="utf-8")
    assert bd.streak_start(tmp_path, day, "Z71") is None


def test_streak_start_newest_brace_is_not_the_start(tmp_path):
    day1, day2 = "2000-07-05", "2000-07-06"
    write_cost_summary(tmp_path, day1, {"unreachable_mas": ["Z71"]})
    (tmp_path / "verify" / "cost-recheck" / f"summary.{day2}.json").write_text("{", encoding="utf-8")
    assert bd.streak_start(tmp_path, day2, "Z71") == day1


@pytest.mark.parametrize("body", ["null", "[]", "true"])
def test_streak_start_non_dict_json_does_not_break(tmp_path, body):
    day1, day2 = "2000-07-07", "2000-07-08"
    write_cost_summary(tmp_path, day1, {"unreachable_mas": ["Z71"]})
    (tmp_path / "verify" / "cost-recheck" / f"summary.{day2}.json").write_text(body, encoding="utf-8")
    assert bd.streak_start(tmp_path, day2, "Z71") == day1
