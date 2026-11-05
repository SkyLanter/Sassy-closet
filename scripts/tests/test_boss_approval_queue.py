"""Boss approval queue. Synthetic fixtures only. No network, no writes."""
from __future__ import annotations

import json
import subprocess
from decimal import Decimal
from pathlib import Path
from types import ModuleType

import pytest

import boss_approval_queue as q
from held_policy import default_held_path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "boss_approval_queue.py"
FX = q.DEFAULT_FX


@pytest.fixture(autouse=True)
def offline(monkeypatch):
    calls = {"net": 0, "gh": 0}

    def urlopen(*_args, **_kwargs):
        calls["net"] += 1
        raise OSError("offline")

    def run_gh(*_args, **_kwargs):
        calls["gh"] += 1
        raise OSError("offline")

    monkeypatch.setattr(q.urllib.request, "urlopen", urlopen)
    monkeypatch.setattr(q, "_run_gh", run_gh)
    return calls


def _write(path: Path, payload) -> Path:
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def _row(ma, **extra):
    row = {
        "ma": ma,
        "kind": ma[:1],
        "sell_usd": "",
        "sell_cny": "",
        "sell_currency": "USD",
        "cost_currency": "USD",
        "link": "https://example.invalid/secret-row",
        "blurb": "planted@example.com",
    }
    row.update(extra)
    return row


def run(capsys, args: list[str]) -> str:
    assert q.main(args) == 0
    return capsys.readouterr().out


def test_blank_hand_edited_and_at_quote_examples(tmp_path, capsys, offline):
    """S20 stays blank. A typed $19 and $30 with no calculator snapshot are hand-edited."""
    hidden_cost = "12.00"
    intake = _write(tmp_path / "intake.json", {"submissions": [
        _row("S20", cost_usd=hidden_cost),
        _row("Q02", kind="Q", sell_usd="30", cost_usd=hidden_cost, auto_price=None),
        _row("A30", kind="A", sell_usd="19", cost_usd=hidden_cost, auto_price=None),
        _row("Z26", sell_usd="26", cost_usd="16.26", auto_price={"sellUsd": 26}),
    ]})
    held = _write(tmp_path / "held.json", {"heldIncomplete": ["S14"], "neverList": []})
    prs = _write(tmp_path / "prs.json", [])
    summary = _write(tmp_path / "summary.json", {"taobao_login_needed": False})
    out = run(capsys, [
        "--intake", str(intake), "--held", str(held), "--prs-json", str(prs),
        "--cost-summary", str(summary),
    ])
    assert "No sell price on intake: S20." in out
    assert "Q02 is $30 on intake, hand-edited." in out
    assert "A30 is $19 on intake, hand-edited." in out
    assert "Z26" not in out
    assert hidden_cost not in out
    hidden_landed = "16.26"
    assert hidden_landed not in out
    assert "example.invalid" not in out
    assert "planted@example.com" not in out
    assert "$19" not in out.split("A30")[0]
    assert offline["net"] == 0 and offline["gh"] == 0


def test_under_floor_when_quote_or_caption_misses(tmp_path, capsys):
    intake = _write(tmp_path / "intake.json", [
        _row("Z20", sell_usd="20", cost_usd="16.26", auto_price={"sellUsd": 20}),
        _row("Z21", sell_usd="20", cost_usd="16.26", auto_price=None),
        _row("Z45", sell_usd="45", cost_usd="33", auto_price={"sellUsd": 45}),
    ])
    held = _write(tmp_path / "held.json", {"heldIncomplete": [], "neverList": []})
    prs = _write(tmp_path / "prs.json", [])
    summary = _write(tmp_path / "summary.json", {"taobao_login_needed": False})
    out = run(capsys, [
        "--intake", str(intake), "--held", str(held), "--prs-json", str(prs),
        "--cost-summary", str(summary),
    ])
    assert "Z20 is $20 on intake, under the price floor." in out
    assert "Z20 is $20 on intake, under the price floor and hand-edited." not in out
    assert "Z21 is $20 on intake, under the price floor and hand-edited." in out
    assert "Z45 is $45 on intake, under the price floor." in out
    assert "hand-edited" in out
    assert out.count("hand-edited") == 1


def test_s06_stays_25_and_blank_s06_is_not_a_price_task(tmp_path, capsys):
    wrong = "40"
    intake = _write(tmp_path / "intake.json", [
        _row("S06", sell_usd=wrong, cost_usd="12.00"),
        _row("s6", sell_usd="", cost_usd="12.00"),
        _row("S07", sell_usd="25", cost_usd="12.00", auto_price={"sellUsd": 25}),
    ])
    # Last S06 wins. The second row is blank, so the lock is not a change request.
    out = run(capsys, ["--intake", str(intake), "--held", str(_empty_held(tmp_path)),
                       "--prs-json", str(_empty_prs(tmp_path)),
                       "--cost-summary", str(_clear_summary(tmp_path))])
    assert "S06" not in out
    assert f"${wrong}" not in out
    assert "S07" not in out


def test_s06_off_lock_is_named_without_the_other_dollar(tmp_path, capsys):
    wrong = "40"
    intake = _write(tmp_path / "intake.json", [_row("S06", sell_usd=wrong, cost_usd="16.26")])
    out = run(capsys, ["--intake", str(intake), "--held", str(_empty_held(tmp_path)),
                       "--prs-json", str(_empty_prs(tmp_path)),
                       "--cost-summary", str(_clear_summary(tmp_path))])
    assert "S06 stays $25." in out
    assert wrong not in out
    hidden_landed = "16.26"
    assert hidden_landed not in out


def test_cny_sell_hides_the_amount(tmp_path, capsys):
    hidden = "134.46"
    intake = _write(tmp_path / "intake.json", [
        _row("Q09", sell_currency="CNY", sell_cny=hidden, sell_usd="", cost_usd="16.26"),
    ])
    out = run(capsys, ["--intake", str(intake), "--held", str(_empty_held(tmp_path)),
                       "--prs-json", str(_empty_prs(tmp_path)),
                       "--cost-summary", str(_clear_summary(tmp_path))])
    assert "Q09 has a CNY sell price under the price floor and it is hand-edited." in out
    assert hidden not in out


def test_junk_sell_is_no_price_and_last_row_wins(tmp_path, capsys):
    intake = _write(tmp_path / "intake.json", [
        _row("S20", sell_usd="30", cost_usd="12.00", auto_price={"sellUsd": 30}),
        _row("S20", sell_usd="1,000"),
        _row("not a mã", sell_usd="9"),
        {"ma": "A31"},
    ])
    out = run(capsys, ["--intake", str(intake), "--held", str(_empty_held(tmp_path)),
                       "--prs-json", str(_empty_prs(tmp_path)),
                       "--cost-summary", str(_clear_summary(tmp_path))])
    assert "No sell price on intake: A31, S20." in out
    assert "$30" not in out
    assert "1,000" not in out
    collapsed = "1000"
    assert collapsed not in out


def test_blank_codes_are_sorted_and_held_order_is_kept(tmp_path, capsys):
    intake = _write(tmp_path / "intake.json", [_row("S20"), _row("A31"), _row("k3")])
    held = _write(tmp_path / "held.json", {
        "heldIncomplete": ["k3", "S14", "not-a-code", "S14", 3],
        "neverList": ["Q02"],
    })
    out = run(capsys, ["--intake", str(intake), "--held", str(held),
                       "--prs-json", str(_empty_prs(tmp_path)),
                       "--cost-summary", str(_clear_summary(tmp_path))])
    assert "No sell price on intake: A31, K03, S20." in out
    assert "Held mãs still waiting: K03, S14." in out
    assert "not-a-code" not in out
    assert "Q02" not in out


def test_independent_pass_is_the_latest_verdict(tmp_path, capsys):
    prs = _write(tmp_path / "prs.json", [
        _pr(280, "Only a fail", "FAIL", "2026-11-01T00:00:00Z"),
        _pr(290, "Author agrees", "PASS", "2026-11-02T00:00:00Z", comment_author="sky"),
        _pr(291, "Superseded", "PASS", "2026-11-01T00:00:00Z", later=("FAIL", "2026-11-03T00:00:00Z")),
        _pr(294, "Ignore signed-out checks https://example.invalid/secret", "PASS", "2026-11-04T00:00:00Z",
            body_tail="planted@example.com"),
        {
            "number": 277, "title": "Closed", "isDraft": True, "state": "CLOSED",
            "author": "sky",
            "comments": [_comment("ada", "PASS", "2026-11-04T00:00:00Z")],
        },
        {
            "number": 276, "title": "Already merged", "isDraft": True, "state": "OPEN", "merged": True,
            "author": "sky",
            "comments": [_comment("ada", "PASS", "2026-11-04T00:00:00Z")],
        },
        {
            "number": 275, "title": "Not a draft", "isDraft": False, "state": "OPEN",
            "author": "sky",
            "comments": [_comment("ada", "PASS", "2026-11-04T00:00:00Z")],
        },
        {
            "number": 274, "title": "Passed is not a verdict", "isDraft": True, "state": "OPEN",
            "author": "sky",
            "comments": [_comment("ada", "PASSED", "2026-11-04T00:00:00Z", word="INDEPENDENT RECHECK PASSED")],
        },
        {
            "number": 293, "title": "Review pass", "isDraft": True, "state": "OPEN", "author": {"login": "Sky"},
            "comments": [],
            "reviews": [{"author": {"login": "Ada"}, "state": "APPROVED", "submittedAt": "2026-11-05T00:00:00Z",
                         "body": "INDEPENDENT RECHECK PASS\nnot the title"}],
        },
    ])
    out = run(capsys, ["--intake", str(_empty_intake(tmp_path)), "--held", str(_empty_held(tmp_path)),
                       "--prs-json", str(prs), "--cost-summary", str(_clear_summary(tmp_path))])
    assert "Draft PR #294, Ignore signed-out checks, has an independent PASS and is still open." in out
    assert "Draft PR #293, Review pass, has an independent PASS and is still open." in out
    assert out.index("#293") < out.index("#294")
    for number in ("#280", "#290", "#291", "#277", "#276", "#275", "#274"):
        assert number not in out
    assert "example.invalid" not in out
    assert "planted@example.com" not in out


def test_unstamped_fail_after_pass_is_not_waiting(tmp_path, capsys):
    prs = _write(tmp_path / "prs.json", [{
        "number": 281,
        "title": "Needs another look",
        "isDraft": True,
        "state": "OPEN",
        "author": "sky",
        "comments": [
            _comment("ada", "PASS", "2026-11-01T00:00:00Z"),
            {"author": "ada", "body": "INDEPENDENT RECHECK FAIL\n", "createdAt": ""},
        ],
    }])
    out = run(capsys, ["--intake", str(_empty_intake(tmp_path)), "--held", str(_empty_held(tmp_path)),
                       "--prs-json", str(prs), "--cost-summary", str(_clear_summary(tmp_path))])
    assert "#281" not in out


def test_title_drops_yen_host_and_phone(tmp_path, capsys):
    mark = "\u00a5"
    phone = "555" + "-010-" + "0199"
    host = "item." + "tao" + "bao.com/x"
    title = f"Keep the gate {mark}80 {host} {phone}"
    prs = _write(tmp_path / "prs.json", [_pr(10, title, "PASS", "2026-11-05T00:00:00Z")])
    out = run(capsys, ["--intake", str(_empty_intake(tmp_path)), "--held", str(_empty_held(tmp_path)),
                       "--prs-json", str(prs), "--cost-summary", str(_clear_summary(tmp_path))])
    assert "Draft PR #10, Keep the gate, has an independent PASS and is still open." in out
    assert mark not in out
    assert host not in out
    assert phone not in out


def test_s06_near_miss_is_not_rounded_into_the_lock(tmp_path, capsys):
    off = "24.995"
    intake = _write(tmp_path / "intake.json", [_row("S06", sell_usd=off)])
    out = run(capsys, ["--intake", str(intake), "--held", str(_empty_held(tmp_path)),
                       "--prs-json", str(_empty_prs(tmp_path)),
                       "--cost-summary", str(_clear_summary(tmp_path))])
    assert "S06 stays $25." in out
    assert off not in out


def test_broken_cost_module_does_not_drop_intake(tmp_path, monkeypatch, capsys):
    module = ModuleType("cost_recheck_block")

    def explode(_path):
        raise KeyError("summary")

    module.load_summary = explode
    module.login_blocked = explode
    monkeypatch.setattr(q, "cost_recheck_block", module)
    intake = _write(tmp_path / "intake.json", [_row("S20")])
    summary = _write(tmp_path / "summary.json", {"taobao_login_needed": True})
    out = run(capsys, ["--intake", str(intake), "--held", str(_empty_held(tmp_path)),
                       "--prs-json", str(_empty_prs(tmp_path)), "--cost-summary", str(summary)])
    assert "No sell price on intake: S20." in out
    assert q.BLOCKED in out


def test_fail_then_pass_is_waiting(tmp_path, capsys):
    prs = _write(tmp_path / "prs.json", [
        _pr(292, "Fixed", "FAIL", "2026-11-01T00:00:00Z", later=("PASS", "2026-11-02T00:00:00Z")),
    ])
    out = run(capsys, ["--intake", str(_empty_intake(tmp_path)), "--held", str(_empty_held(tmp_path)),
                       "--prs-json", str(prs), "--cost-summary", str(_clear_summary(tmp_path))])
    assert "Draft PR #292, Fixed, has an independent PASS and is still open." in out


def test_login_blocked_truth_table():
    assert q.defensive_login_blocked({"taobao_login_needed": True}) is True
    assert q.defensive_login_blocked({"taobao_login_needed": 1}) is True
    assert q.defensive_login_blocked({"taobao_login_needed": 1.0}) is True
    assert q.defensive_login_blocked({"taobao_login_needed": " true "}) is True
    assert q.defensive_login_blocked({"taobao_login_needed": "YES"}) is True
    assert q.defensive_login_blocked({"taobao_login_needed": "y"}) is True
    assert q.defensive_login_blocked({"taobao_login_needed": "1"}) is True
    assert q.defensive_login_blocked({"taobao_login_needed": False}) is False
    assert q.defensive_login_blocked({"taobao_login_needed": 0}) is False
    assert q.defensive_login_blocked({"taobao_login_needed": 0.0}) is False
    assert q.defensive_login_blocked({"taobao_login_needed": " false "}) is False
    assert q.defensive_login_blocked({"taobao_login_needed": "no"}) is False
    assert q.defensive_login_blocked({"taobao_login_needed": "1.0"}) is False
    assert q.defensive_login_blocked({"taobao_login_needed": "1e0"}) is False
    assert q.defensive_login_blocked({}) is False
    assert q.defensive_login_blocked([]) is False
    assert q.defensive_login_blocked(None) is False


def test_summary_file_states(tmp_path, capsys):
    blocked = tmp_path / "blocked.json"
    blocked.write_bytes(b"\xef\xbb\xbf" + b'{"taobao_login_needed": true}\n')
    out = run(capsys, ["--intake", str(_empty_intake(tmp_path)), "--held", str(_empty_held(tmp_path)),
                       "--prs-json", str(_empty_prs(tmp_path)), "--cost-summary", str(blocked)])
    assert q.BLOCKED in out
    assert "Nothing is waiting." not in out

    not_block = _write(tmp_path / "clear.json", {"taobao_login_needed": "1.0"})
    out = run(capsys, ["--intake", str(_empty_intake(tmp_path)), "--held", str(_empty_held(tmp_path)),
                       "--prs-json", str(_empty_prs(tmp_path)), "--cost-summary", str(not_block)])
    assert q.NOT_BLOCKED in out
    assert "Nothing is waiting." in out

    bad = tmp_path / "bad.json"
    bad.write_text("{", encoding="utf-8")
    out = run(capsys, ["--intake", str(_empty_intake(tmp_path)), "--held", str(_empty_held(tmp_path)),
                       "--prs-json", str(_empty_prs(tmp_path)), "--cost-summary", str(bad)])
    assert q.TAOBAO_UNREAD in out
    assert "Nothing is waiting." not in out

    missing = tmp_path / "missing.json"
    out = run(capsys, ["--intake", str(_empty_intake(tmp_path)), "--held", str(_empty_held(tmp_path)),
                       "--prs-json", str(_empty_prs(tmp_path)), "--cost-summary", str(missing)])
    assert q.TAOBAO_UNREAD in out


def test_latest_summary_in_a_directory(tmp_path, capsys):
    folder = tmp_path / "cost"
    folder.mkdir()
    _write(folder / "summary.2026-11-01.json", {"taobao_login_needed": True})
    _write(folder / "summary.2026-11-04.json", {"taobao_login_needed": False})
    (folder / "notes.json").write_text("{}", encoding="utf-8")
    out = run(capsys, ["--intake", str(_empty_intake(tmp_path)), "--held", str(_empty_held(tmp_path)),
                       "--prs-json", str(_empty_prs(tmp_path)), "--cost-dir", str(folder)])
    assert q.NOT_BLOCKED in out

    empty = tmp_path / "empty"
    empty.mkdir()
    out = run(capsys, ["--intake", str(_empty_intake(tmp_path)), "--held", str(_empty_held(tmp_path)),
                       "--prs-json", str(_empty_prs(tmp_path)), "--cost-dir", str(empty)])
    assert q.NO_SUMMARY in out
    assert "Nothing is waiting." in out


def test_prefers_cost_recheck_block_when_present(tmp_path, monkeypatch, capsys):
    module = ModuleType("cost_recheck_block")
    module.load_summary = lambda _path: ("blocked", {"taobao_login_needed": "1.0"})
    module.login_blocked = lambda _doc: False
    monkeypatch.setattr(q, "cost_recheck_block", module)
    summary = _write(tmp_path / "summary.json", {"taobao_login_needed": "1.0"})
    out = run(capsys, ["--intake", str(_empty_intake(tmp_path)), "--held", str(_empty_held(tmp_path)),
                       "--prs-json", str(_empty_prs(tmp_path)), "--cost-summary", str(summary)])
    assert q.BLOCKED in out


def test_network_and_gh_failures_do_not_crash(tmp_path, capsys, offline):
    out = run(capsys, ["--held", str(_empty_held(tmp_path)), "--cost-dir", str(tmp_path / "missing-dir"),
                       "--timeout", "1"])
    assert q.INTAKE_UNREAD in out
    assert q.DRAFTS_UNREAD in out
    assert q.NO_SUMMARY in out
    assert offline["net"] == 1
    assert offline["gh"] == 1
    assert "Traceback" not in out


def test_bad_local_fixtures_do_not_crash(tmp_path, capsys, offline):
    intake = tmp_path / "intake.json"
    intake.write_text("{", encoding="utf-8")
    held = tmp_path / "held.json"
    held.write_text("{", encoding="utf-8")
    prs = tmp_path / "prs.json"
    prs.write_text('{"number": 1}', encoding="utf-8")
    before = {path.name: path.read_bytes() for path in (intake, held, prs)}
    out = run(capsys, ["--intake", str(intake), "--held", str(held), "--prs-json", str(prs),
                       "--cost-dir", str(tmp_path / "none")])
    assert q.INTAKE_UNREAD in out
    assert q.HELD_UNREAD in out
    assert q.DRAFTS_UNREAD in out
    assert offline["net"] == 0 and offline["gh"] == 0
    assert {path.name: path.read_bytes() for path in (intake, held, prs)} == before


def test_refuses_a_non_http_intake_url(tmp_path, capsys, offline):
    out = run(capsys, ["--intake-url", "file:///etc/passwd", "--timeout", "5",
                       "--held", str(_empty_held(tmp_path)), "--prs-json", str(_empty_prs(tmp_path)),
                       "--cost-dir", str(tmp_path / "none")])
    assert q.INTAKE_UNREAD in out
    assert offline["net"] == 0
    assert "passwd" not in out


def test_gh_nonzero_and_bad_json(monkeypatch, tmp_path, capsys):
    def failed(*_args, **_kwargs):
        return subprocess.CompletedProcess(["gh"], 1, stdout="", stderr="nope")

    monkeypatch.setattr(q, "_run_gh", failed)
    out = run(capsys, ["--intake", str(_empty_intake(tmp_path)), "--held", str(_empty_held(tmp_path)),
                       "--cost-dir", str(tmp_path / "none")])
    assert q.DRAFTS_UNREAD in out
    assert "nope" not in out

    def garbage(*_args, **_kwargs):
        return subprocess.CompletedProcess(["gh"], 0, stdout="{", stderr="")

    monkeypatch.setattr(q, "_run_gh", garbage)
    out = run(capsys, ["--intake", str(_empty_intake(tmp_path)), "--held", str(_empty_held(tmp_path)),
                       "--cost-dir", str(tmp_path / "none")])
    assert q.DRAFTS_UNREAD in out


def test_gh_missing_does_not_spawn(monkeypatch, tmp_path, capsys, offline):
    monkeypatch.setattr(q.shutil, "which", lambda _name: None)
    out = run(capsys, ["--intake", str(_empty_intake(tmp_path)), "--held", str(_empty_held(tmp_path)),
                       "--cost-dir", str(tmp_path / "none")])
    assert q.DRAFTS_UNREAD in out
    assert offline["gh"] == 0


def test_gh_pass_fixture_is_parsed(monkeypatch, tmp_path, capsys):
    payload = [_pr(288, "Flag photo ids", "PASS", "2026-11-05T00:00:00Z")]

    def ok(args, cwd, timeout):
        assert args[0] == "gh" and "merge" not in args and "create" not in args
        assert timeout > 0
        return subprocess.CompletedProcess(args, 0, stdout=json.dumps(payload), stderr="")

    monkeypatch.setattr(q, "_run_gh", ok)
    out = run(capsys, ["--intake", str(_empty_intake(tmp_path)), "--held", str(_empty_held(tmp_path)),
                       "--cost-dir", str(tmp_path / "none")])
    assert "Draft PR #288, Flag photo ids, has an independent PASS and is still open." in out


def test_default_held_file_is_not_modified(tmp_path, capsys):
    path = default_held_path()
    before = path.read_bytes()
    codes = q.held_codes(json.loads(before))
    out = run(capsys, ["--intake", str(_empty_intake(tmp_path)), "--prs-json", str(_empty_prs(tmp_path)),
                       "--cost-dir", str(tmp_path / "none")])
    assert path.read_bytes() == before
    assert codes
    assert q.held_line(codes) in out


def test_rows_are_not_mutated():
    row = _row("A30", sell_usd="19", cost_usd="12.00")
    before = json.dumps(row)
    assert q.classify(row, FX) == "hand"
    assert json.dumps(row) == before
    assert q.classify(_row("S20", cost_usd="12.00"), FX) == "blank"
    assert q.classify(_row("Z26", sell_usd="26", cost_usd="16.26", auto_price={"sellUsd": 26}), FX) is None


def test_quote_spot_checks():
    assert q.classify(_row("Q02", kind="Q", sell_usd="30", cost_usd="12.00"), FX) == "hand"
    assert q.classify(_row("A30", kind="A", sell_usd="19", cost_usd="12.00"), FX) == "hand"
    landed = q.landed_usd(_row("Q02", kind="Q", cost_usd="12.00"), FX, "Q02")
    assert landed == Decimal("19.50")


def test_source_does_not_write_or_send():
    text = SCRIPT.read_text(encoding="utf-8")
    for bad in ("write_text", "write_bytes", "shell=True", "git push", "gh pr merge", "gh pr create",
                "requests.post", "blob.put"):
        assert bad not in text
    assert "could not read" in text
    assert "S06 stays $25" in text


def test_usage(capsys):
    assert q.main(["--not-a-flag"]) == 2
    assert "Traceback" not in capsys.readouterr().out


def _empty_intake(tmp_path: Path) -> Path:
    return _write(tmp_path / "intake-empty.json", {"submissions": []})


def _empty_held(tmp_path: Path) -> Path:
    return _write(tmp_path / "held-empty.json", {"heldIncomplete": [], "neverList": []})


def _empty_prs(tmp_path: Path) -> Path:
    return _write(tmp_path / "prs-empty.json", [])


def _clear_summary(tmp_path: Path) -> Path:
    return _write(tmp_path / "clear-summary.json", {"taobao_login_needed": False})


def _comment(author, verdict, when, word=None):
    line = word or f"INDEPENDENT RECHECK {verdict}"
    return {"author": author, "body": line + "\n", "createdAt": when}


def _pr(number, title, verdict, when, comment_author="ada", later=None, body_tail=""):
    comments = [_comment(comment_author, verdict, when)]
    if body_tail:
        comments[0]["body"] += body_tail + "\n"
    if later:
        comments.append(_comment("ada", later[0], later[1]))
    return {
        "number": number,
        "title": title,
        "isDraft": True,
        "state": "OPEN",
        "author": "sky",
        "comments": comments,
    }
