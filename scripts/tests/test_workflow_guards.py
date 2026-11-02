"""Regression guards for Pacific dates, intake days, sizes, photo counts, and heartbeats.

Hermetic: fixtures live under tmp_path. Nothing here writes /workspace/out or held.json.
"""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

import boss_decisions_digest as bdd
import freshness_check
import hung_run_watch
import midnight_qc
import muse_pack_sections as muse
import run_gap_check
from autolist import SHOE_KINDS
from held_policy import HeldPolicy, load_held_policy
from pickup import events_from_json, photo_count_or_none, plan_pickups
from test_midnight_qc import _passing_payload

ROOT = Path(__file__).resolve().parents[2]
HELD_PATH = ROOT / "data" / "held.json"

# Same landed cost as test_pipeline: a complete letter-size row quotes $25.
LANDED = "16.25"
QUOTED = 25

PT_INSTANT = datetime(2026, 10, 29, 1, 30, tzinfo=timezone.utc)  # 18:30 PDT on 2026-10-28
PT_DAY = "2026-10-28"
HEARTBEAT_AT = "2026-10-21T18:00:00+00:00"
HEARTBEAT_NOW = "2026-10-21T18:30:00+00:00"

REUSE_ROWS = [
    {"ma": "Z01", "created_at": "2000-01-01", "title": "dress"},
    {"ma": "Z01", "created_at": "2000-02-01", "title": "skirt"},
    {"ma": "Z02", "created_at": "2000-01-01", "title": "top"},
]


def _fake_now(instant: datetime):
    class FakeDatetime(datetime):
        @classmethod
        def now(cls, tz=None):
            return instant if tz is None else instant.astimezone(tz)

    return FakeDatetime


def _qc_intake(root: Path, day: str, rows: list[dict] | None = None) -> Path:
    path = root / "out" / "midnight-qc" / day / "raw" / "intake-submissions.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"submissions": rows or []}), encoding="utf-8")
    return path


def _pair(ma: str) -> list[dict]:
    return [
        {"ma": ma, "created_at": "2000-01-01", "title": "one"},
        {"ma": ma, "created_at": "2000-02-01", "title": "two"},
    ]


def _reuse_section(markdown: str) -> str:
    return markdown.split("### Reused intake codes", 1)[1]


def _pickup(ma: str, sizes: list[str], *, boss_approved: bool, sell_usd: str | None = None) -> dict:
    row = {
        "ma": ma,
        "sizes": sizes,
        "photo_count": 2,
        "public_cny": "59.9",
        "landed_usd": LANDED,
        "boss_approved": boss_approved,
    }
    if sell_usd is not None:
        row["sell_usd"] = sell_usd
    return row


def _write(root: Path, rel: str, text: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _last_check(root: Path, at: str) -> None:
    state = root / "state"
    state.mkdir(parents=True, exist_ok=True)
    (state / "last_check.json").write_text(json.dumps({"at": at, "result": "noop"}), encoding="utf-8")


def _gap_config(tmp_path: Path) -> Path:
    path = tmp_path / "rg.json"
    path.write_text(
        json.dumps(
            {
                "schema": "run-gaps/v1",
                "jobs": [
                    {
                        "name": "al",
                        "kind": "state",
                        "pattern": "state/last_check.json",
                        "timezone": "UTC",
                        "active_window": {
                            "timezone": "America/Los_Angeles",
                            "start": "08:09",
                            "end": "22:54",
                            "max_age_minutes": 45,
                        },
                        "json_files": ["state/last_check.json"],
                        "zero_byte_ok": ["*.lock"],
                        "scan_dir": "state",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    return path


def test_midnight_qc_default_date_is_pacific_not_utc(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(midnight_qc, "datetime", _fake_now(PT_INSTANT))
    assert midnight_qc.today_pt() == PT_DAY
    fixture = tmp_path / "pass.json"
    fixture.write_text(json.dumps(_passing_payload()), encoding="utf-8")
    out = tmp_path / "qc"
    assert midnight_qc.main(["--fixture", str(fixture), "--out", str(out)]) == 0
    summary = json.loads((out / "summary.json").read_text(encoding="utf-8"))
    markdown = (out / "data-ok.md").read_text(encoding="utf-8")
    assert summary["date"] == PT_DAY
    assert f"Midnight QC {PT_DAY}" in markdown
    assert summary["date"] != "2026-10-29"


def test_default_intake_ignores_latest_backup_and_impossible_days(tmp_path) -> None:
    newest = _qc_intake(tmp_path, "2026-10-28", REUSE_ROWS)
    older = _qc_intake(tmp_path, "2026-10-27", _pair("Z44"))
    for name, ma in (
        ("latest", "Z88"),
        ("backup", "Z77"),
        ("2026-99-99", "Z66"),
        ("2026-02-31", "Z55"),
    ):
        _qc_intake(tmp_path, name, _pair(ma))
    assert muse.default_intake(tmp_path) == [newest]
    assert muse.default_intake(tmp_path, "2026-10-27") == [older]
    assert muse.default_intake(tmp_path, "2026-99-99") == []
    assert muse.default_intake(tmp_path, "2026-02-31") == []
    section = muse.build(tmp_path)
    reuse = _reuse_section(muse.render_md(section))
    assert "- 1 reused of 3 rows (2026-10-28): Z01×2" in reuse.splitlines()
    assert "Reused intake codes: Z01 (2026-10-28)" in muse.render_msg(section).splitlines()
    for ma in ("Z88", "Z77", "Z66", "Z55", "Z44"):
        assert ma not in reuse


def test_dated_build_does_not_reuse_an_older_day(tmp_path) -> None:
    _qc_intake(tmp_path, "2026-10-26", REUSE_ROWS)
    assert muse.default_intake(tmp_path, "2026-10-27") == []
    section = muse.build(tmp_path, date="2026-10-27")
    reuse = _reuse_section(muse.render_md(section))
    assert "unavailable (FileNotFoundError)" in reuse
    assert "Z01" not in reuse
    assert "2026-10-26" not in reuse


def test_explicit_intake_outside_dated_raw_has_no_date_suffix(tmp_path) -> None:
    _qc_intake(tmp_path, "2026-10-28", _pair("Z88"))
    plain = tmp_path / "intake.json"
    plain.write_text(json.dumps({"submissions": REUSE_ROWS}), encoding="utf-8")
    section = muse.build(tmp_path, [plain])
    reuse = _reuse_section(muse.render_md(section))
    message = muse.render_msg(section)
    assert "- 1 reused of 3 rows: Z01×2" in reuse.splitlines()
    assert "(2026-10-28)" not in reuse
    assert "Reused intake codes: Z01" in message.splitlines()
    assert "(2026-10-28)" not in message


def test_cli_date_selects_that_day(tmp_path, capsys) -> None:
    _qc_intake(tmp_path, "2026-10-29", _pair("Z88"))
    _qc_intake(tmp_path, "2026-10-28", REUSE_ROWS)
    assert muse.main(["--root", str(tmp_path), "--date", "2026-10-28"]) == 0
    out = capsys.readouterr().out
    assert "- 1 reused of 3 rows (2026-10-28): Z01×2" in out
    assert "Reused intake codes: Z01 (2026-10-28)" in out
    assert "Z88" not in out
    assert "(2026-10-29)" not in out


@pytest.mark.parametrize("day", ["2026-99-99", "2026-02-31"])
def test_cli_date_rejects_impossible_day(tmp_path, capsys, day: str) -> None:
    with pytest.raises(SystemExit) as caught:
        muse.main(["--root", str(tmp_path), "--date", day])
    assert caught.value.code not in (0, None)
    assert "YYYY-MM-DD" in capsys.readouterr().err


@pytest.mark.parametrize("sizes", (["FREE"], ["S", "38"]))
def test_non_shoe_invalid_size_is_held_and_not_quoted(sizes: list[str]) -> None:
    policy = HeldPolicy(held=(), never_list=())
    decision = plan_pickups(events_from_json([_pickup("Z91", sizes, boss_approved=True)]), policy)[0]
    assert decision.held is True
    assert decision.publish is False
    assert decision.live is False
    assert decision.quoted_usd is None
    assert decision.flags == ("invalid_size",)
    assert decision.detail == "incomplete Taobao; not quoted live"


@pytest.mark.parametrize(
    ("approved", "flags", "held"),
    [(False, ("boss_approval",), True), (True, (), False)],
)
def test_letter_size_is_not_invalid(approved: bool, flags: tuple[str, ...], held: bool) -> None:
    policy = HeldPolicy(held=(), never_list=())
    decision = plan_pickups(events_from_json([_pickup("Z99", ["S"], boss_approved=approved)]), policy)[0]
    assert "invalid_size" not in decision.flags
    assert decision.flags == flags
    assert decision.held is held
    assert decision.quoted_usd == QUOTED
    assert decision.publish is False
    assert decision.live is False


@pytest.mark.parametrize(
    ("ma", "size"),
    [("G01", "38"), ("G02", "40"), ("O01", "38"), ("O02", "40")],
)
def test_shoe_eu_size_stays_quotable(ma: str, size: str) -> None:
    assert ma[:1] in SHOE_KINDS
    policy = HeldPolicy(held=(), never_list=())
    decision = plan_pickups(events_from_json([_pickup(ma, [size], boss_approved=True)]), policy)[0]
    assert "invalid_size" not in decision.flags
    assert decision.flags == ()
    assert decision.held is False
    assert decision.quoted_usd == QUOTED
    assert decision.publish is False
    assert decision.live is False


def test_held_ma_stays_held_not_invalid_size() -> None:
    policy = load_held_policy()
    held = next(code for code in policy.held if len(code) == 3 and code[1] == "0")
    before = HELD_PATH.read_bytes()
    for sizes in (["FREE"], ["S", "38"]):
        decision = plan_pickups(events_from_json([_pickup(held, sizes, boss_approved=True)]), policy)[0]
        assert decision.ma == held
        assert decision.flags == ("held",)
        assert "invalid_size" not in decision.flags
        assert decision.held is True
        assert decision.publish is False
        assert decision.live is False
        assert decision.quoted_usd is None
    assert HELD_PATH.read_bytes() == before


def test_s06_lock_stays_25() -> None:
    policy = HeldPolicy(held=(), never_list=())
    locked = plan_pickups(
        events_from_json([_pickup("S06", ["S"], boss_approved=True, sell_usd="25")]),
        policy,
    )[0]
    assert locked.quoted_usd == 25
    assert locked.flags == ()
    assert "invalid_size" not in locked.flags
    assert locked.publish is False
    assert locked.live is False
    blocked = plan_pickups(
        events_from_json([_pickup("S06", ["S"], boss_approved=True, sell_usd="30")]),
        policy,
    )[0]
    assert blocked.quoted_usd is None
    assert blocked.flags == ("s06_lock",)
    assert blocked.publish is False
    assert blocked.live is False


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        (2, 2),
        (2.0, 2),
        ("2.0", 2),
        ("2", 2),
        ("", None),
        ("none", None),
        (True, None),
        (False, None),
        (-1, None),
        (2.5, None),
        (None, None),
    ],
)
def test_photo_count_or_none_and_events(raw: object, expected: int | None) -> None:
    assert photo_count_or_none(raw) == expected
    assert freshness_check._photo_field({"photo_count": raw}) == expected
    event = events_from_json([{"ma": "Z91", "sizes": ["S"], "photo_count": raw}])[0]
    assert event.photo_count == expected


def test_missing_photo_count_falls_back_to_list_length() -> None:
    assert freshness_check._photo_field({"gallery": ["a.jpg", "b.jpg"]}) == 2
    assert freshness_check._photo_field({"photos": ["a.jpg", "b.jpg"]}) == 2
    assert freshness_check._photo_field({"images": ["a.jpg"]}) == 1
    assert freshness_check._photo_field({"gallery_urls": ["a.jpg", "b.jpg", "c.jpg"]}) == 3
    assert freshness_check._photo_field({"gallery": ["a.jpg", " ", ""]}) == 1
    assert freshness_check._photo_field({"photo_count": None, "photos": ["a.jpg", "b.jpg"]}) == 2
    assert freshness_check._photo_field({"photo_count": "", "photos": ["a.jpg", "b.jpg"]}) is None
    assert freshness_check._photo_field({}) is None


@pytest.mark.parametrize(
    ("text", "closed"),
    [
        ("X02 needs a Boss price, not decided", False),
        ("Hold call for X04 is with Boss, not done", False),
        ("X05 Boss price approved", True),
        ("X06 Boss price approved but not done", True),
        ("X07 Boss price not yet decided", True),
        ("X03 Boss price never decided", False),
    ],
)
def test_line_is_closed_only_for_adjacent_not_or_never(text: str, closed: bool) -> None:
    assert bdd.line_is_closed(text) is closed


def test_open_lines_stay_and_closed_lines_drop(tmp_path) -> None:
    _write(
        tmp_path,
        "out/muse/extras-2026-04-01.md",
        "X02 needs a Boss price, not decided\n"
        "Hold call for X04 is with Boss, not done\n"
        "X05 Boss price approved\n"
        "X06 Boss price approved but not done\n",
    )
    seen = bdd.scan(tmp_path)
    assert ("price_approval", "X02") in seen
    assert ("hold_call", "X04") in seen
    assert all(ma not in {"X05", "X06"} for _cat, ma in seen)


def test_nested_raw_note_uses_the_date_directory(tmp_path) -> None:
    rel = "out/midnight-qc/2026-03-04/raw/note.md"
    _write(tmp_path, rel, "X08 needs a Boss price\n")
    assert bdd.file_date(tmp_path / rel) == "2026-03-04"
    src, first_seen = bdd.scan(tmp_path)[("price_approval", "X08")]
    assert first_seen == "2026-03-04"
    assert src == rel


def test_filename_date_beats_a_different_directory(tmp_path) -> None:
    rel = "out/midnight-qc/2026-09-09/extras-2026-01-02.md"
    _write(tmp_path, rel, "X09 needs a Boss price\n")
    assert bdd.file_date(tmp_path / rel) == "2026-01-02"
    src, first_seen = bdd.scan(tmp_path)[("price_approval", "X09")]
    assert first_seen == "2026-01-02"
    assert src == rel


def test_date_above_the_scan_root_does_not_outrank_the_filename(tmp_path) -> None:
    root = tmp_path / "2020-01-01" / "shop"
    _write(root, "out/muse/extras-notes.md", "X02 needs a Boss price\n")
    _write(root, "out/muse/extras-2026-04-01.md", "X02 needs a Boss price\n")
    assert bdd.file_date(root / "out/muse/extras-notes.md", root) is None
    src, first_seen = bdd.scan(root)[("price_approval", "X02")]
    assert first_seen == "2026-04-01"
    assert src == "out/muse/extras-2026-04-01.md"


def test_scan_root_that_is_itself_a_date_still_counts(tmp_path) -> None:
    root = tmp_path / "2026-03-04"
    note = root / "raw" / "note.md"
    note.parent.mkdir(parents=True)
    note.write_text("x\n", encoding="utf-8")
    assert bdd.file_date(note, root) == "2026-03-04"


@pytest.mark.parametrize("day", ["2026-99-99", "2026-02-31"])
def test_impossible_date_directory_is_not_first_seen(tmp_path, day: str) -> None:
    rel = f"out/midnight-qc/{day}/raw/note.md"
    _write(tmp_path, rel, "X11 needs a Boss price\n")
    assert bdd.file_date(tmp_path / rel, tmp_path) is None
    _src, first_seen = bdd.scan(tmp_path)[("price_approval", "X11")]
    assert first_seen == "unknown"


def test_default_public_held_is_unchanged() -> None:
    assert bdd.DEFAULT_PUBLIC_HELD == ("S14", "A24", "A25")


def test_aware_utc_keeps_naive_as_utc_and_does_not_shift_aware() -> None:
    naive = run_gap_check.aware_utc(datetime.fromisoformat("2026-10-21T18:00:00"))
    assert naive.tzinfo is not None
    assert naive.astimezone(timezone.utc) == datetime(2026, 10, 21, 18, 0, tzinfo=timezone.utc)
    now = datetime.fromisoformat(HEARTBEAT_NOW)
    assert now - naive == timedelta(minutes=30)
    utc = datetime.fromisoformat("2026-10-21T18:00:00+00:00")
    pdt = datetime.fromisoformat("2026-10-21T11:00:00-07:00")
    pst = datetime.fromisoformat("2026-10-21T10:00:00-08:00")
    assert run_gap_check.aware_utc(utc).astimezone(timezone.utc) == utc
    assert run_gap_check.aware_utc(pdt).astimezone(timezone.utc) == utc
    assert run_gap_check.aware_utc(pst).astimezone(timezone.utc) == utc


@pytest.mark.parametrize(
    "stamp",
    [
        "2026-10-21T18:00:00",
        "2026-10-21T18:00:00+00:00",
        "2026-10-21T11:00:00-07:00",
        "2026-10-21T10:00:00-08:00",
    ],
)
def test_naive_and_aware_heartbeats_stay_18_utc(tmp_path, stamp: str) -> None:
    _last_check(tmp_path, stamp)
    now = datetime.fromisoformat(HEARTBEAT_NOW)
    report = hung_run_watch.run(tmp_path, now, held=set())
    assert report["heartbeat"] == HEARTBEAT_AT
    assert report["slots"]["in_active_window"] is True


@pytest.mark.parametrize(
    "stamp",
    [
        "2026-10-21T18:00:00",
        "2026-10-21T18:00:00+00:00",
        "2026-10-21T11:00:00-07:00",
        "2026-10-21T10:00:00-08:00",
    ],
)
def test_run_gap_check_heartbeat_is_utc_and_not_usage(tmp_path, capsys, stamp: str) -> None:
    root = tmp_path / "shop"
    _last_check(root, stamp)
    rc = run_gap_check.main(
        ["--root", str(root), "--config", str(_gap_config(tmp_path)), "--now", HEARTBEAT_NOW, "--json"]
    )
    captured = capsys.readouterr()
    assert rc != 2
    assert rc == 0
    assert "TypeError" not in captured.err
    job = json.loads(captured.out)["jobs"][0]
    assert job["last_at"] == HEARTBEAT_AT
    assert job["in_active_window"] is True
    assert job["stale"] is False


def test_hung_run_watch_main_accepts_naive_last_check(tmp_path) -> None:
    _last_check(tmp_path, "2026-10-21T18:00:00")
    rc = hung_run_watch.main(["--autolist", str(tmp_path), "--now", HEARTBEAT_NOW, "--json"])
    assert rc != 2
