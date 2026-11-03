"""Desk status on fixtures. No live intake, Blob, Meta, or held write."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from desk_status import (
    main,
    read_open_pr_numbers,
    render_json,
    render_page,
    render_text,
    status_from_json,
    write_page,
)
from held_policy import default_held_path, load_held_policy, policy_from_mapping

ROOT = Path(__file__).resolve().parents[2]
HELD = ROOT / "data" / "held.json"
SOURCE = (ROOT / "scripts" / "desk_status.py").read_text(encoding="utf-8")


def _payload() -> dict[str, object]:
    return {
        "intake": {
            "submissions": [
                {"ma": "S06"},
                {"ma": "A07"},
                {"ma": "Z99"},
            ]
        },
        "catalog": {
            "products": [
                {"ma": "S06", "priceUsd": 25},
                {"ma": "A07", "priceUsd": 26},
            ]
        },
        "held": {"heldIncomplete": ["S14", "K06"], "neverList": []},
        "pullRequests": [
            {"number": 104, "title": "S06 shop-save lock", "waitingOnBoss": True},
            87,
            {"number": 104, "title": "duplicate", "waitingOnBoss": True},
        ],
        "freshness": {
            "day": "2026-10-14",
            "guardsPass": True,
            "pickup": [
                {
                    "ma": "Z99",
                    "flags": ["boss_approval"],
                    "detail": "no Boss yes; quoted and held; not live",
                },
                {"ma": "S14", "flags": ["held"], "detail": "held mã stays off live"},
            ],
        },
    }


def test_fixture_counts_prs_freshness_and_boss_wait() -> None:
    status = status_from_json(_payload())
    assert status.intake.value == 3
    assert status.catalog.value == 2
    assert status.held.value == 2
    assert status.open_prs == (87, 104)
    assert status.freshness.state == "pass"
    assert status.freshness.day == "2026-10-14"
    assert status.s06_usd == "25"
    assert [(item.kind, item.ref) for item in status.waiting or ()] == [
        ("pull_request", "104"),
        ("ma", "Z99"),
    ]
    text = render_text(status)
    assert "intake: 3" in text
    assert "catalog: 2" in text
    assert "held: 2" in text
    assert "open PRs: 87, 104" in text
    assert "freshness: 2026-10-14 PASS" in text
    assert "PR 104 (S06 shop-save lock)" in text
    assert "Z99 (no Boss yes; quoted and held; not live)" in text
    assert "S06: $25" in text
    assert "S14" not in text.split("waiting on Boss:", maxsplit=1)[1]
    body = json.dumps(render_json(status))
    assert "A07" not in text
    assert "A07" not in body


def test_failed_freshness_and_explicit_boss_wait() -> None:
    payload = _payload()
    payload["freshness"] = {"day": "2026-10-14", "guardsPass": False}
    payload["pullRequests"] = [95]
    payload["waitingOnBoss"] = [
        {"kind": "ma", "ma": "z99", "detail": "quoted and held"},
    ]
    status = status_from_json(payload)
    assert status.freshness.state == "fail"
    assert "freshness: 2026-10-14 FAIL" in render_text(status)
    assert status.waiting is not None
    assert status.waiting[0].ref == "Z99"
    assert "PR 95" not in render_text(status)


def test_missing_sources_are_unread_not_zero() -> None:
    status = status_from_json({"held": {"heldIncomplete": ["S14"], "neverList": []}})
    assert status.intake.state == "unread"
    assert status.intake.value is None
    assert status.catalog.value is None
    assert status.open_prs is None
    assert status.freshness.state == "unread"
    assert status.waiting_state == "unread"
    assert status.s06_usd is None
    text = render_text(status)
    assert "intake: unread" in text
    assert "catalog: unread" in text
    assert "open PRs: unread" in text
    assert "freshness: unread" in text
    assert "waiting on Boss: unread" in text
    assert "S06:" not in text


def test_empty_pr_list_is_none_and_not_unread() -> None:
    status = status_from_json(
        {
            "pullRequests": [],
            "freshness": {"guardsPass": True, "pickup": []},
        }
    )
    assert status.open_prs == ()
    assert "open PRs: none" in render_text(status)
    assert "waiting on Boss: none" in render_text(status)


def test_local_page_uses_the_snapshot_and_does_not_fetch() -> None:
    status = status_from_json(_payload())
    page = render_page(status)
    assert "Local snapshot. No live fetch." in page
    assert "Intake" in page and ">3<" in page
    assert "Catalog" in page and ">2<" in page
    assert "Held" in page
    assert "87, 104" in page
    assert "2026-10-14 PASS" in page
    assert "Waiting on Boss" in page
    assert "PR 104" in page
    lowered = page.lower()
    assert "<script" not in lowered
    assert "fetch(" not in lowered
    assert "http" not in lowered
    assert "tesla" not in lowered


def test_page_refuses_live_read_and_forbidden_paths(tmp_path: Path) -> None:
    status = status_from_json(_payload())
    live = status.__class__(**{**status.__dict__, "local": False})
    page = tmp_path / "desk.html"
    with pytest.raises(ValueError, match="local data"):
        write_page(live, page)
    assert not page.exists()
    before = HELD.read_bytes()
    with pytest.raises(ValueError, match="refusing to write"):
        write_page(status, HELD)
    assert HELD.read_bytes() == before
    shop_page = ROOT / "sassy-closet" / "desk.html"
    with pytest.raises(ValueError, match="shop app"):
        write_page(status, shop_page)
    assert not shop_page.exists()


def test_cli_fixture_writes_only_the_local_page(tmp_path: Path) -> None:
    fixture = tmp_path / "desk.json"
    fixture.write_text(json.dumps(_payload()), encoding="utf-8")
    page = tmp_path / "desk.html"
    before = HELD.read_bytes()
    ran = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "desk_status.py"),
            "--fixture",
            str(fixture),
            "--page",
            str(page),
            "--json",
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert ran.returncode == 0, ran.stderr
    saved = json.loads(ran.stdout)
    assert saved["intakeCount"] == 3
    assert saved["catalogCount"] == 2
    assert saved["heldCount"] == 2
    assert saved["openPullRequests"] == [87, 104]
    assert saved["freshness"]["state"] == "pass"
    assert saved["s06Usd"] == "25"
    assert saved["local"] is True
    assert page.is_file()
    assert "No live fetch." in page.read_text(encoding="utf-8")
    assert HELD.read_bytes() == before
    assert fixture.read_text(encoding="utf-8") == json.dumps(_payload())


def test_cli_bad_fixture_exits_without_writing_held(tmp_path: Path) -> None:
    fixture = tmp_path / "bad.json"
    fixture.write_text("{", encoding="utf-8")
    before = HELD.read_bytes()
    ran = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "desk_status.py"), "--fixture", str(fixture)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert ran.returncode == 2
    assert HELD.read_bytes() == before


def test_default_cli_reads_held_file_and_leaves_it(tmp_path: Path) -> None:
    before = HELD.read_bytes()
    ran = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "desk_status.py"), "--json"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert ran.returncode == 0, ran.stderr
    saved = json.loads(ran.stdout)
    assert saved["heldCount"] == len(load_held_policy().held)
    assert saved["heldState"] == "ok"
    assert saved["intakeState"] == "unread"
    assert saved["catalogState"] == "unread"
    assert saved["openPullRequestsState"] == "unread"
    assert saved["freshness"]["state"] == "unread"
    assert saved["waitingOnBossState"] == "unread"
    assert saved["s06Usd"] is None
    assert HELD.read_bytes() == before
    assert main(["--page", str(ROOT / "data" / "desk.html")]) == 2
    assert not (ROOT / "data" / "desk.html").exists()


def test_gh_reader_returns_numbers_and_does_not_mutate() -> None:
    def runner(args: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        assert args[:3] == ["gh", "pr", "list"]
        assert "merge" not in args
        assert "comment" not in args
        assert "ready" not in args
        assert "--state" in args and "open" in args
        assert kwargs["check"] is False
        return subprocess.CompletedProcess(
            args,
            0,
            stdout=json.dumps([{"number": 104}, {"number": 87}, {"number": 104}]),
            stderr="",
        )

    numbers, state, detail = read_open_pr_numbers("SkyLanter/Sassy-closet", runner)
    assert numbers == (87, 104)
    assert state == "ok"
    assert detail == "2 open"

    def failed(args: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        return subprocess.CompletedProcess(args, 1, stdout="", stderr="auth missing")

    unread, state, detail = read_open_pr_numbers("SkyLanter/Sassy-closet", failed)
    assert unread is None
    assert state == "unread"
    assert detail == "auth missing"

    def missing(args: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        raise OSError("gh missing")

    unread, state, detail = read_open_pr_numbers("SkyLanter/Sassy-closet", missing)
    assert unread is None
    assert state == "unread"
    assert "gh missing" in detail


def test_live_pr_numbers_do_not_write_a_page(tmp_path: Path) -> None:
    page = tmp_path / "desk.html"

    def runner(args: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        return subprocess.CompletedProcess(args, 0, stdout="[]", stderr="")

    status = status_from_json({"held": {"heldIncomplete": ["S14"], "neverList": []}})
    numbers, state, _detail = read_open_pr_numbers("SkyLanter/Sassy-closet", runner)
    live = status.__class__(
        **{
            **status.__dict__,
            "open_prs": numbers,
            "open_prs_state": state,
            "local": False,
        }
    )
    with pytest.raises(ValueError, match="local data"):
        write_page(live, page)
    assert not page.exists()
    assert live.open_prs == ()


def test_policy_mapping_matches_the_file_and_rejects_overlap() -> None:
    before = HELD.read_bytes()
    assert policy_from_mapping(json.loads(before), source=str(HELD)) == load_held_policy()
    assert HELD.read_bytes() == before
    with pytest.raises(ValueError, match="both heldIncomplete and neverList"):
        policy_from_mapping({"heldIncomplete": ["Z01"], "neverList": ["Z01"]})


def test_source_does_not_add_prices_or_live_writes() -> None:
    lowered = SOURCE.lower()
    assert "tesla" not in lowered
    assert "urllib" not in lowered
    assert "import requests" not in lowered
    assert "blob_read_write" not in lowered
    assert "listing_quote" not in SOURCE
    assert "vercel deploy" not in lowered
    assert "data/held.json" in SOURCE
