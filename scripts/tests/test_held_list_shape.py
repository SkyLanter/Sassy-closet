"""Flag a held-list fixture entry that is not one letter plus two digits.

The entry stays in the fixture. No file writes.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from held_list_shape import (
    ShapeFlag,
    flag_file,
    flag_held_entries,
    load_held_fixture,
    main,
)
from held_policy import MA_RE, default_held_path, load_held_policy

ROOT = Path(__file__).resolve().parents[2]
HELD_FIXTURE = ROOT / "scripts" / "fixtures" / "held-list-shape" / "held.json"
HELD = ROOT / "data" / "held.json"
SHOP_CATALOG = ROOT / "sassy-closet-shop" / "data" / "products.json"
SCRIPT = ROOT / "scripts" / "held_list_shape.py"
UNKNOWN_LETTER = ROOT / "scripts" / "unknown_letter.py"
HELD_POLICY = ROOT / "scripts" / "held_policy.py"
S06 = "S06"
BAD = "K6"
LIVE = (
    "S14",
    "A24",
    "A25",
    "S15",
    "A26",
    "K02",
    "K03",
    "K04",
    "K05",
    "V04",
    "K06",
    "V05",
)


def test_fixture_flags_k6_and_leaves_it() -> None:
    held_bytes = HELD_FIXTURE.read_bytes()
    live_held = HELD.read_bytes()
    policy_bytes = HELD_POLICY.read_bytes()
    fixture = json.loads(HELD_FIXTURE.read_text(encoding="utf-8"))
    before = json.dumps(fixture)
    held, never = load_held_fixture(HELD_FIXTURE)
    report = flag_held_entries(held, never)
    assert json.dumps(fixture) == before
    assert held == list(LIVE) + [BAD]
    assert never == []
    assert report.held == tuple(held)
    assert report.flags == (ShapeFlag(BAD, "heldIncomplete"),)
    assert report.flags[0].as_json() == {"entry": BAD, "kind": "held_shape", "list": "heldIncomplete"}
    assert BAD in report.as_json()["heldIncomplete"]
    assert S06 not in report.held
    assert S06 not in report.never
    assert report.as_json()["s06"] == {"onHeldList": False}
    policy = load_held_policy()
    assert policy.held == LIVE
    assert S06 not in policy.held
    assert S06 not in policy.never_list
    assert BAD not in policy.held
    try:
        load_held_policy(HELD_FIXTURE)
    except ValueError as error:
        assert BAD in str(error)
    else:
        raise AssertionError("strict loader accepted K6")
    assert MA_RE.pattern == r"^[A-Z][0-9]{2}$"
    assert HELD_FIXTURE.read_bytes() == held_bytes
    assert HELD.read_bytes() == live_held
    assert HELD_POLICY.read_bytes() == policy_bytes
    assert not UNKNOWN_LETTER.exists()
    assert default_held_path() == HELD


def test_s06_stays_off_the_held_list() -> None:
    live = json.loads(HELD.read_text(encoding="utf-8"))
    fixture = json.loads(HELD_FIXTURE.read_text(encoding="utf-8"))
    assert live["heldIncomplete"] == list(LIVE)
    assert live["neverList"] == []
    assert S06 not in live["heldIncomplete"]
    assert S06 not in live["neverList"]
    assert fixture["heldIncomplete"] == list(LIVE) + [BAD]
    assert S06 not in fixture["heldIncomplete"]
    assert S06 not in fixture["neverList"]
    assert BAD in fixture["heldIncomplete"]
    assert "K06" in fixture["heldIncomplete"]
    report = flag_file(HELD_FIXTURE)
    assert [flag.entry for flag in report.flags] == [BAD]
    assert S06 not in [flag.entry for flag in report.flags]
    body = json.dumps(report.as_json())
    assert '"entry": "K6"' in body
    assert '"onHeldList": false' in body
    assert '"writes": []' in body
    assert "corrected" not in body
    assert "K06" in body


def test_cli_prints_the_flag_and_writes_nothing() -> None:
    held_bytes = HELD_FIXTURE.read_bytes()
    live_held = HELD.read_bytes()
    shop_bytes = SHOP_CATALOG.read_bytes()
    policy_bytes = HELD_POLICY.read_bytes()
    data_names = sorted(path.name for path in (ROOT / "data").iterdir())
    completed = subprocess.run(
        [sys.executable, str(SCRIPT), "--held", str(HELD_FIXTURE)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert completed.returncode == 1, completed.stderr
    body = json.loads(completed.stdout)
    assert body["readOnly"] is True
    assert body["writes"] == []
    assert body["flags"] == [{"entry": BAD, "kind": "held_shape", "list": "heldIncomplete"}]
    assert body["s06"] == {"onHeldList": False}
    assert body["heldIncomplete"][-1] == BAD
    assert body["heldIncomplete"][:-1] == list(LIVE)
    assert body["neverList"] == []
    assert S06 not in body["heldIncomplete"]
    assert "K06" in body["heldIncomplete"]
    stored = json.loads(HELD_FIXTURE.read_text(encoding="utf-8"))
    assert stored["heldIncomplete"][-1] == BAD
    assert HELD_FIXTURE.read_bytes() == held_bytes
    assert HELD.read_bytes() == live_held
    assert SHOP_CATALOG.read_bytes() == shop_bytes
    assert HELD_POLICY.read_bytes() == policy_bytes
    assert sorted(path.name for path in (ROOT / "data").iterdir()) == data_names
    assert not UNKNOWN_LETTER.exists()


def test_clean_list_has_no_flags(tmp_path: Path) -> None:
    held_bytes = HELD_FIXTURE.read_bytes()
    live_held = HELD.read_bytes()
    clean = tmp_path / "held.json"
    payload = {"heldIncomplete": list(LIVE), "neverList": []}
    clean.write_text(json.dumps(payload), encoding="utf-8")
    clean_bytes = clean.read_bytes()
    report = flag_file(clean)
    assert report.flags == ()
    assert report.as_json()["s06"]["onHeldList"] is False
    assert S06 not in report.held
    completed = subprocess.run(
        [sys.executable, str(SCRIPT), "--held", str(clean)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert completed.returncode == 0, completed.stderr
    assert json.loads(completed.stdout)["flags"] == []
    assert json.loads(completed.stdout)["heldIncomplete"] == list(LIVE)
    assert clean.read_bytes() == clean_bytes
    assert HELD_FIXTURE.read_bytes() == held_bytes
    assert HELD.read_bytes() == live_held
    committed = json.loads(HELD_FIXTURE.read_text(encoding="utf-8"))
    assert committed["heldIncomplete"][-1] == BAD


def test_in_memory_flags_bad_shapes_and_keeps_them() -> None:
    good = ["K06", "v05", " A24 ", "A01"]
    bad = ["K6", "K006", "KK06", "06", "K6A", "", "K 06"]
    held = good + bad
    never = ["Z9"]
    before_held = list(held)
    before_never = list(never)
    report = flag_held_entries(held, never)
    assert [flag.entry for flag in report.flags] == bad + ["Z9"]
    assert report.flags[-1] == ShapeFlag("Z9", "neverList")
    assert held == before_held
    assert never == before_never
    assert report.held == tuple(held)
    assert report.never == ("Z9",)
    assert S06 not in [flag.entry for flag in report.flags]
    assert report.as_json()["s06"]["onHeldList"] is False

    padded = flag_held_entries([" K06 "], [])
    assert padded.flags == ()
    assert padded.held == (" K06 ",)
    lower = flag_held_entries(["v05"], [])
    assert lower.flags == ()
    assert lower.held == ("v05",)


def test_s06_on_the_held_list_is_refused(tmp_path: Path) -> None:
    held_bytes = HELD_FIXTURE.read_bytes()
    live_held = HELD.read_bytes()
    payload = {"heldIncomplete": ["K06", "s06", BAD], "neverList": []}
    text = json.dumps(payload)
    held_with_s06 = tmp_path / "held.json"
    held_with_s06.write_text(text, encoding="utf-8")
    try:
        flag_file(held_with_s06)
    except ValueError as error:
        assert str(error) == "S06 stays off the held list"
    else:
        raise AssertionError("S06 on the held list was accepted")
    assert held_with_s06.read_text(encoding="utf-8") == text
    stored = json.loads(held_with_s06.read_text(encoding="utf-8"))
    assert stored["heldIncomplete"] == ["K06", "s06", BAD]

    try:
        flag_held_entries(["K06"], ["S06"])
    except ValueError as error:
        assert str(error) == "S06 stays off the held list"
    else:
        raise AssertionError("S06 on the never list was accepted")

    spaced = [" S06 "]
    try:
        flag_held_entries(spaced, [])
    except ValueError as error:
        assert str(error) == "S06 stays off the held list"
    else:
        raise AssertionError("padded S06 was accepted")
    assert spaced == [" S06 "]
    assert HELD_FIXTURE.read_bytes() == held_bytes
    assert HELD.read_bytes() == live_held


def test_duplicate_valid_code_is_refused_and_kept() -> None:
    held = ["K06", "k06", BAD]
    try:
        flag_held_entries(held, [])
    except ValueError as error:
        assert str(error) == "heldIncomplete repeats K06"
    else:
        raise AssertionError("duplicate mã was accepted")
    assert held == ["K06", "k06", BAD]

    overlap_held = ["V05", BAD]
    overlap_never = ["v05"]
    try:
        flag_held_entries(overlap_held, overlap_never)
    except ValueError as error:
        assert "V05" in str(error)
        assert "both" in str(error)
    else:
        raise AssertionError("overlap was accepted")
    assert overlap_held == ["V05", BAD]
    assert overlap_never == ["v05"]


def test_cli_refuses_live_files_and_bad_fixtures(tmp_path: Path, capsys) -> None:
    held_bytes = HELD_FIXTURE.read_bytes()
    live_held = HELD.read_bytes()
    shop_bytes = SHOP_CATALOG.read_bytes()

    refused_held = main(["--held", str(HELD)])
    assert refused_held == 2
    assert "data/held.json" in capsys.readouterr().err
    assert HELD.read_bytes() == live_held

    remote = main(["--held", "https://example.invalid/held.json"])
    assert remote == 2
    assert "local fixtures only" in capsys.readouterr().err

    shop = main(["--held", str(SHOP_CATALOG)])
    assert shop == 2
    assert "Shop catalog files are not read." in capsys.readouterr().err
    assert SHOP_CATALOG.read_bytes() == shop_bytes

    missing = main(["--held", str(tmp_path / "missing.json")])
    assert missing == 2
    assert "missing held-list fixture" in capsys.readouterr().err

    broken = tmp_path / "broken.json"
    broken.write_text("{", encoding="utf-8")
    assert main(["--held", str(broken)]) == 2
    assert "not held-list JSON" in capsys.readouterr().err
    assert broken.read_text(encoding="utf-8") == "{"

    number = tmp_path / "number.json"
    number_text = json.dumps({"heldIncomplete": ["K06", 6], "neverList": []})
    number.write_text(number_text, encoding="utf-8")
    assert main(["--held", str(number)]) == 2
    assert "non-string" in capsys.readouterr().err
    assert number.read_text(encoding="utf-8") == number_text
    assert json.loads(number.read_text(encoding="utf-8"))["heldIncomplete"] == ["K06", 6]

    assert HELD_FIXTURE.read_bytes() == held_bytes
    assert HELD.read_bytes() == live_held


def test_lowercase_bad_entry_is_flagged_without_rewriting(tmp_path: Path) -> None:
    path = tmp_path / "held.json"
    payload = {"heldIncomplete": ["k6", "V05"], "neverList": ["  "]}
    text = json.dumps(payload)
    path.write_text(text, encoding="utf-8")
    report = flag_file(path)
    assert [flag.as_json() for flag in report.flags] == [
        {"entry": "k6", "kind": "held_shape", "list": "heldIncomplete"},
        {"entry": "  ", "kind": "held_shape", "list": "neverList"},
    ]
    assert path.read_text(encoding="utf-8") == text
    assert json.loads(path.read_text(encoding="utf-8"))["heldIncomplete"] == ["k6", "V05"]
    assert report.held == ("k6", "V05")


def test_script_has_no_write_or_network_calls() -> None:
    source = SCRIPT.read_text(encoding="utf-8")
    folded = source.casefold()
    for token in (
        "write_text",
        "write_bytes",
        "urlopen",
        "urllib",
        "urlretrieve",
        "mkdir",
        "requests",
        "open(",
        "unknown_letter",
    ):
        assert token not in source
    assert "tesla" not in folded
    assert "vercel.app" not in folded
    assert "load_held_policy" not in source
