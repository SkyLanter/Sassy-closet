"""Held-list fixture diff. No held.json write and no live catalog write."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from held_diff import diff_held_files, diff_held_lists, load_held_list, main
from held_policy import HeldPolicy, default_held_path, load_held_policy

ROOT = Path(__file__).resolve().parents[2]
BEFORE = ROOT / "scripts" / "fixtures" / "held-diff" / "before.json"
AFTER = ROOT / "scripts" / "fixtures" / "held-diff" / "after.json"
HELD = ROOT / "data" / "held.json"
S06 = "S06"


def test_fixture_diff_reports_added_and_removed() -> None:
    policy = load_held_policy()
    before = load_held_list(BEFORE)
    after = load_held_list(AFTER)
    before_order = before.held
    after_order = after.held
    report = diff_held_lists(before, after)
    assert report.added == ("Z02",)
    assert report.removed == ("Z01",)
    assert report.held == tuple(sorted(policy.held))
    assert report.never_added == ()
    assert report.never_removed == ()
    assert report.s06_on_held_before is False
    assert report.s06_on_held_after is False
    assert before.held == before_order
    assert after.held == after_order
    for code in policy.held:
        assert code in before.held
        assert code in after.held
        assert code not in report.added
        assert code not in report.removed
        assert code in report.held
    assert S06 not in before.held
    assert S06 not in after.held
    assert S06 not in before.never_list
    assert S06 not in after.never_list
    assert S06 not in report.added
    assert S06 not in report.removed
    assert S06 not in report.held


def test_fixture_files_keep_s06_off_and_held_mas_stay() -> None:
    policy = load_held_policy()
    for path in (BEFORE, AFTER):
        payload = json.loads(path.read_text(encoding="utf-8"))
        held = [code.strip().upper() for code in payload["heldIncomplete"]]
        never = [code.strip().upper() for code in payload["neverList"]]
        assert payload["neverList"] == []
        assert S06 not in held
        assert S06 not in never
        for code in policy.held:
            assert code in held
    before = load_held_list(BEFORE)
    after = load_held_list(AFTER)
    assert set(policy.held) <= set(before.held)
    assert set(policy.held) <= set(after.held)
    assert before.never_list == ()
    assert after.never_list == ()


def test_cli_prints_the_diff_and_writes_nothing() -> None:
    held_before = HELD.read_bytes()
    before_bytes = BEFORE.read_bytes()
    after_bytes = AFTER.read_bytes()
    completed = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "held_diff.py"),
            "--before",
            str(BEFORE),
            "--after",
            str(AFTER),
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert completed.returncode == 0, completed.stderr
    body = json.loads(completed.stdout)
    assert body["added"] == ["Z02"]
    assert body["removed"] == ["Z01"]
    assert body["held"] == sorted(load_held_policy().held)
    assert body["neverAdded"] == []
    assert body["neverRemoved"] == []
    assert body["s06"] == {"onHeldBefore": False, "onHeldAfter": False}
    assert S06 not in body["added"]
    assert S06 not in body["removed"]
    assert S06 not in body["held"]
    assert HELD.read_bytes() == held_before
    assert BEFORE.read_bytes() == before_bytes
    assert AFTER.read_bytes() == after_bytes
    assert default_held_path() == HELD


def test_identical_fixtures_report_no_changes() -> None:
    before_bytes = BEFORE.read_bytes()
    held_before = HELD.read_bytes()
    report = diff_held_files(BEFORE, BEFORE)
    assert report.added == ()
    assert report.removed == ()
    assert report.never_added == ()
    assert report.never_removed == ()
    assert report.s06_on_held_before is False
    assert report.s06_on_held_after is False
    assert set(load_held_policy().held) <= set(report.held)
    assert S06 not in report.held
    assert BEFORE.read_bytes() == before_bytes
    assert HELD.read_bytes() == held_before


def test_in_memory_diff_leaves_the_lists_and_held_file() -> None:
    before = HeldPolicy(held=("K06", "Z01"), never_list=())
    after = HeldPolicy(held=("K06", "Z02"), never_list=("Z09",))
    held_before = HELD.read_bytes()
    report = diff_held_lists(before, after)
    assert report.added == ("Z02",)
    assert report.removed == ("Z01",)
    assert report.held == ("K06",)
    assert report.never_added == ("Z09",)
    assert report.never_removed == ()
    assert report.s06_on_held_before is False
    assert report.s06_on_held_after is False
    assert before.held == ("K06", "Z01")
    assert after.held == ("K06", "Z02")
    assert after.never_list == ("Z09",)
    assert HELD.read_bytes() == held_before


def test_a_dropped_held_ma_is_reported_and_the_file_stays(tmp_path: Path) -> None:
    before = tmp_path / "before.json"
    after = tmp_path / "after.json"
    before.write_text(_document(["K06", "V05", "Z01"]), encoding="utf-8")
    after.write_text(_document(["V05", "Z02"]), encoding="utf-8")
    after_bytes = after.read_bytes()
    held_before = HELD.read_bytes()
    report = diff_held_files(before, after)
    assert report.added == ("Z02",)
    assert report.removed == ("K06", "Z01")
    assert report.held == ("V05",)
    assert "K06" not in report.held
    assert json.loads(after.read_text(encoding="utf-8"))["heldIncomplete"] == ["V05", "Z02"]
    assert after.read_bytes() == after_bytes
    assert HELD.read_bytes() == held_before


def test_s06_on_a_temp_list_is_reported_and_not_rewritten(tmp_path: Path) -> None:
    before = tmp_path / "before.json"
    after = tmp_path / "after.json"
    before.write_text(_document(["K06"]), encoding="utf-8")
    after.write_text(_document(["K06", "s06"]), encoding="utf-8")
    after_bytes = after.read_bytes()
    held_before = HELD.read_bytes()
    report = diff_held_files(before, after)
    assert report.added == (S06,)
    assert report.removed == ()
    assert report.held == ("K06",)
    assert report.s06_on_held_before is False
    assert report.s06_on_held_after is True
    assert json.loads(after.read_text(encoding="utf-8"))["heldIncomplete"] == ["K06", "s06"]
    assert after.read_bytes() == after_bytes
    assert HELD.read_bytes() == held_before
    checked_in = load_held_list(AFTER)
    assert S06 not in checked_in.held
    assert S06 not in checked_in.never_list


def test_lowercase_ma_matches_the_same_code(tmp_path: Path) -> None:
    before = tmp_path / "before.json"
    after = tmp_path / "after.json"
    before.write_text(_document(["z01", "k06"]), encoding="utf-8")
    after.write_text(_document(["Z02", "k06"]), encoding="utf-8")
    report = diff_held_files(before, after)
    assert report.added == ("Z02",)
    assert report.removed == ("Z01",)
    assert report.held == ("K06",)
    assert load_held_list(before).held == ("Z01", "K06")


def test_duplicate_and_invalid_lists_are_refused(tmp_path: Path) -> None:
    duplicate = tmp_path / "duplicate.json"
    duplicate.write_text(_document(["Z01", "z01"]), encoding="utf-8")
    try:
        load_held_list(duplicate)
    except ValueError as error:
        assert "Z01" in str(error)
    else:
        raise AssertionError("duplicate mã was accepted")

    invalid = tmp_path / "invalid.json"
    invalid.write_text(_document(["S6"]), encoding="utf-8")
    try:
        load_held_list(invalid)
    except ValueError as error:
        assert "invalid" in str(error)
    else:
        raise AssertionError("invalid mã was accepted")

    overlap = tmp_path / "overlap.json"
    overlap.write_text(
        json.dumps({"heldIncomplete": ["Z01"], "neverList": ["z01"]}),
        encoding="utf-8",
    )
    try:
        load_held_list(overlap)
    except ValueError as error:
        assert "Z01" in str(error)
    else:
        raise AssertionError("overlap was accepted")

    broken = tmp_path / "broken.json"
    broken.write_text("{", encoding="utf-8")
    try:
        load_held_list(broken)
    except ValueError as error:
        assert "not held-list JSON" in str(error)
    else:
        raise AssertionError("broken JSON was accepted")


def test_main_refuses_held_json_a_url_and_a_missing_file(capsys) -> None:
    held_before = HELD.read_bytes()
    refused = main(["--before", str(HELD), "--after", str(AFTER)])
    assert refused == 2
    assert "data/held.json" in capsys.readouterr().err
    remote = main(["--before", "https://example.com/held.json", "--after", str(AFTER)])
    assert remote == 2
    assert "local held-list fixtures" in capsys.readouterr().err
    missing = main(["--before", "scripts/fixtures/held-diff/missing.json", "--after", str(AFTER)])
    assert missing == 2
    assert "missing held-list fixture" in capsys.readouterr().err
    assert HELD.read_bytes() == held_before


def test_script_has_no_write_or_network_calls() -> None:
    source = (ROOT / "scripts" / "held_diff.py").read_text(encoding="utf-8")
    for token in (
        "write_text",
        "write_bytes",
        "urlopen",
        "urllib",
        "urlretrieve",
        "mkdir",
        "requests",
        "open(",
        "catalog_diff",
    ):
        assert token not in source


def _document(codes: list[str]) -> str:
    return json.dumps({"heldIncomplete": codes, "neverList": []})
