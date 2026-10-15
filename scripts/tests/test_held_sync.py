"""Held sync uses a fixture and a temp held file. data/held.json stays as committed."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from held_sync import main, sync_held_file

ROOT = Path(__file__).resolve().parents[2]
HELD_PATH = ROOT / "data" / "held.json"
HELD_BYTES = HELD_PATH.read_bytes()
ORIGINAL = json.loads(HELD_BYTES.decode("utf-8"))
SCRIPT = ROOT / "scripts" / "held_sync.py"


def _copy_held(tmp_path: Path) -> Path:
    dest = tmp_path / "held.json"
    dest.write_bytes(HELD_BYTES)
    return dest


def _write_fixture(tmp_path: Path, payload: dict[str, object]) -> Path:
    path = tmp_path / "intake.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def _row(ma: str, cost: str, **extra: object) -> dict[str, object]:
    row: dict[str, object] = {
        "ma": ma,
        "cost_cny": cost,
        "sizes": ["S", "M"],
        "photo_count": 2,
    }
    row.update(extra)
    return row


def _tao(ma: str, public: str | None, **extra: object) -> dict[str, object]:
    row: dict[str, object] = {
        "ma": ma,
        "state": "ok" if public is not None else "skip",
        "public_cny": public,
        "sizes": ["S", "M"],
        "photo_count": 2,
    }
    row.update(extra)
    return row


def _live_catalog() -> dict[str, object]:
    rows = [{"ma": "S06"}, {"ma": "A07"}, {"ma": "S10"}]
    return {"blob": rows, "hub": rows}


def _assert_repo_held_untouched() -> None:
    assert HELD_PATH.read_bytes() == HELD_BYTES


def test_incomplete_taobao_appends_to_temp_held_and_leaves_repo_file(tmp_path: Path) -> None:
    held = _copy_held(tmp_path)
    fixture = _write_fixture(
        tmp_path,
        {
            **_live_catalog(),
            "intake": [
                _row("Z91", "88", sizes=[]),
                _row("Z92", "88", photo_count=0),
                _row("Z93", "88"),
                _row("Q02", "80", sizes=[]),
                _row("Z90", "50", sizes=[]),
                _row("Z89", "88"),
                _row("Z94", "80"),
                {
                    "ma": "Z96",
                    "cost_cny": "88",
                    "size": "S M",
                    "images": ["https://example.invalid/z96.jpg"],
                },
                _row("z91", "88", sizes=[]),
            ],
            "taobao": [
                _tao("Z91", "88", sizes=[]),
                _tao("Z92", "88", photo_count=0),
                _tao("Z93", None, state="ok", detail="no public ¥ on the page"),
                _tao("Q02", "80", sizes=[]),
                _tao("Z90", "80", sizes=[]),
                _tao("Z89", None, state="skip", detail=""),
                _tao(
                    "Z94",
                    None,
                    state="skip",
                    detail="login-walled or unreachable",
                ),
                {
                    "ma": "Z96",
                    "public_cny": "88",
                    "size": "S, M",
                    "gallery": ["https://example.invalid/z96-a.jpg", "https://example.invalid/z96-b.jpg"],
                },
            ],
        },
    )
    summary = sync_held_file(fixture, held)
    added = {item["ma"]: item["reasons"] for item in summary["added"]}
    assert added == {
        "Z91": ["missing_size"],
        "Z92": ["missing_photos"],
        "Z93": ["missing_yen"],
        "Q02": ["missing_size"],
        "Z90": ["missing_size", "cost_drift"],
        "Z89": ["missing_yen"],
    }
    assert "Z94" not in added
    assert "Z96" not in added
    assert summary["wrote"] is True
    assert summary["heldIncomplete"][: len(ORIGINAL["heldIncomplete"])] == ORIGINAL["heldIncomplete"]
    assert summary["heldIncomplete"][-6:] == ["Z91", "Z92", "Z93", "Q02", "Z90", "Z89"]
    assert summary["heldIncomplete"].count("Z91") == 1
    assert summary["neverList"] == ORIGINAL["neverList"]
    for code in ("S16", "A27", "A28", "S17", "S18", "S19"):
        assert code not in summary["heldIncomplete"]
    saved = json.loads(held.read_text(encoding="utf-8"))
    assert saved["heldIncomplete"] == summary["heldIncomplete"]
    assert saved["neverList"] == ORIGINAL["neverList"]
    assert "sell_usd" not in json.dumps(summary)
    assert "$" not in json.dumps(summary)
    _assert_repo_held_untouched()


def test_cost_drift_appends_and_live_or_matching_rows_stay_off_the_list(tmp_path: Path) -> None:
    held = _copy_held(tmp_path)
    fixture = _write_fixture(
        tmp_path,
        {
            "blob": {"state": "ok", "rows": [{"ma": "S06"}, {"ma": "A07"}, {"ma": "S10"}]},
            "hub": {"state": "ok", "rows": [{"ma": "S06"}, {"ma": "A07"}, {"ma": "S10"}, {"ma": "Z81"}]},
            "intake": [
                _row("Z95", "87.23", sell_usd="40"),
                _row("Z97", "110"),
                _row("Z98", "99.00"),
                _row("Z96", "88"),
                _row("Z07", "127;145"),
                _row("Z08", ""),
                _row("Z81", "10"),
                _row("S06", "60.39"),
                _row("A07", "87.23"),
                _row("V05", "87.23"),
                _row("Q02", "88"),
            ],
            "taobao": [
                _tao("Z95", "99"),
                _tao("Z97", "100"),
                _tao("Z98", "99"),
                _tao("Z96", "88"),
                _tao("Z07", "145"),
                _tao("Z08", "80"),
                _tao("Z81", "40", sizes=[]),
                _tao("S06", "59.9"),
                _tao("A07", "49.99"),
                _tao("V05", "99"),
                _tao("Q02", "88"),
            ],
        },
    )
    summary = sync_held_file(fixture, held)
    added = {item["ma"]: item for item in summary["added"]}
    assert set(added) == {"Z95", "Z97"}
    assert added["Z95"]["reasons"] == ["cost_drift"]
    assert added["Z95"]["intakeCny"] == "87.23"
    assert added["Z95"]["publicCny"] == "99"
    assert added["Z97"]["reasons"] == ["cost_drift"]
    assert added["Z97"]["intakeCny"] == "110"
    assert added["Z97"]["publicCny"] == "100"
    assert "sell_usd" not in json.dumps(summary)
    assert "$" not in json.dumps(summary)
    assert "40" not in held.read_text(encoding="utf-8")
    result = summary["heldIncomplete"]
    assert result[: len(ORIGINAL["heldIncomplete"])] == ORIGINAL["heldIncomplete"]
    assert result[-2:] == ["Z95", "Z97"]
    assert result.count("V05") == 1
    assert "S06" not in result
    assert "A07" not in result
    assert "S10" not in result
    assert "Z81" not in result
    assert "Q02" not in result
    for code in ("S16", "A27", "A28", "S17", "S18", "S19"):
        assert code not in result
    _assert_repo_held_untouched()


def test_never_list_is_not_copied_into_held_incomplete(tmp_path: Path) -> None:
    held = tmp_path / "held.json"
    held.write_text(
        json.dumps({"heldIncomplete": ["V05"], "neverList": ["Z02"]}) + "\n",
        encoding="utf-8",
    )
    fixture = _write_fixture(
        tmp_path,
        {
            **_live_catalog(),
            "intake": [_row("Z02", "10", sizes=[]), _row("Z95", "87.23")],
            "taobao": [_tao("Z02", "40", sizes=[]), _tao("Z95", "99")],
        },
    )
    summary = sync_held_file(fixture, held)
    assert [item["ma"] for item in summary["added"]] == ["Z95"]
    assert summary["heldIncomplete"] == ["V05", "Z95"]
    assert summary["neverList"] == ["Z02"]
    assert summary["heldIncomplete"].count("Z02") == 0
    _assert_repo_held_untouched()


def test_s06_drift_off_catalog_is_still_not_held(tmp_path: Path) -> None:
    held = _copy_held(tmp_path)
    fixture = _write_fixture(
        tmp_path,
        {
            "blob": [{"ma": "A07"}],
            "hub": [{"ma": "A07"}],
            "intake": [_row("S06", "60.39", sizes=[])],
            "taobao": [_tao("S06", "59.9", sizes=[], photo_count=0)],
        },
    )
    summary = sync_held_file(fixture, held)
    assert summary["added"] == []
    assert summary["wrote"] is False
    assert "S06" not in summary["heldIncomplete"]
    assert held.read_bytes() == HELD_BYTES
    _assert_repo_held_untouched()


def test_login_wall_with_a_missing_size_is_held_for_the_size(tmp_path: Path) -> None:
    held = _copy_held(tmp_path)
    fixture = _write_fixture(
        tmp_path,
        {
            **_live_catalog(),
            "intake": [_row("Z94", "80", sizes=[])],
            "taobao": [
                _tao(
                    "Z94",
                    None,
                    state="skip",
                    detail="login-walled or unreachable",
                    sizes=[],
                )
            ],
        },
    )
    summary = sync_held_file(fixture, held)
    assert summary["added"] == [
        {
            "ma": "Z94",
            "reasons": ["missing_size"],
            "intakeCny": "80",
            "publicCny": None,
        }
    ]
    _assert_repo_held_untouched()


def test_taobao_empty_size_wins_over_an_intake_size(tmp_path: Path) -> None:
    held = _copy_held(tmp_path)
    fixture = _write_fixture(
        tmp_path,
        {
            **_live_catalog(),
            "intake": [_row("Z91", "88")],
            "taobao": [_tao("Z91", "88", sizes=[])],
        },
    )
    summary = sync_held_file(fixture, held)
    assert summary["added"][0]["reasons"] == ["missing_size"]
    _assert_repo_held_untouched()


def test_second_run_does_not_duplicate(tmp_path: Path) -> None:
    held = _copy_held(tmp_path)
    fixture = _write_fixture(
        tmp_path,
        {
            **_live_catalog(),
            "intake": [_row("Z95", "87.23")],
            "taobao": [_tao("Z95", "99")],
        },
    )
    first = sync_held_file(fixture, held)
    after_first = held.read_bytes()
    second = sync_held_file(fixture, held)
    assert first["wrote"] is True
    assert second["added"] == []
    assert second["wrote"] is False
    assert second["heldIncomplete"] == first["heldIncomplete"]
    assert held.read_bytes() == after_first
    assert second["heldIncomplete"].count("Z95") == 1
    _assert_repo_held_untouched()


def test_skip_blob_refuses_and_leaves_both_held_files(tmp_path: Path) -> None:
    held = _copy_held(tmp_path)
    before = held.read_bytes()
    fixture = _write_fixture(
        tmp_path,
        {
            "blob": {"state": "skip", "rows": []},
            "intake": [_row("Z91", "88", sizes=[])],
            "taobao": [_tao("Z91", "88", sizes=[])],
        },
    )
    try:
        sync_held_file(fixture, held)
    except ValueError as error:
        assert "blob" in str(error)
    else:
        raise AssertionError("skip blob invented a held update")
    assert held.read_bytes() == before
    _assert_repo_held_untouched()


def test_cli_writes_temp_held_and_refuses_repo_file(tmp_path: Path) -> None:
    held = _copy_held(tmp_path)
    fixture = _write_fixture(
        tmp_path,
        {
            **_live_catalog(),
            "intake": [_row("Z95", "87.23"), _row("Z91", "88", sizes=[])],
            "taobao": [_tao("Z95", "99"), _tao("Z91", "88", sizes=[])],
        },
    )
    ran = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--fixture",
            str(fixture),
            "--held",
            str(held),
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert ran.returncode == 0, ran.stderr
    saved = json.loads(ran.stdout)
    assert [item["ma"] for item in saved["added"]] == ["Z95", "Z91"]
    assert saved["added"][0]["reasons"] == ["cost_drift"]
    assert saved["added"][1]["reasons"] == ["missing_size"]
    assert "sell_usd" not in ran.stdout
    assert "$" not in ran.stdout
    on_disk = json.loads(held.read_text(encoding="utf-8"))
    assert on_disk["heldIncomplete"][-2:] == ["Z95", "Z91"]
    _assert_repo_held_untouched()

    refused = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--fixture",
            str(fixture),
            "--held",
            str(HELD_PATH),
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert refused.returncode == 2
    assert "data/held.json" in refused.stderr
    _assert_repo_held_untouched()

    code = main(["--fixture", str(fixture), "--held", str(HELD_PATH)])
    assert code == 2
    _assert_repo_held_untouched()


def test_script_does_not_name_live_hosts_or_the_draft_list_edits() -> None:
    source = SCRIPT.read_text(encoding="utf-8")
    for banned in (
        "urllib",
        "requests",
        "vercel",
        "graph.facebook",
        "fetch_live",
        "S16",
        "A27",
        "A28",
        "S17",
        "S18",
        "S19",
        "tesla",
        "Tesla",
    ):
        assert banned not in source
    assert "data/held.json" in source
    assert HELD_PATH.read_bytes() == HELD_BYTES
