"""Fixture-only saved dates after the fixture as-of date. The clock is not used."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest
from held_policy import load_held_policy
from intake_future_saved_date_flags import flag_saved_after_as_of, main, report_json, render_markdown

ROOT = Path(__file__).resolve().parents[2]
FIXTURES = Path(__file__).resolve().parent / "fixtures"
GAPS = FIXTURES / "intake_future_saved_date_gaps.json"
CLEAN = FIXTURES / "intake_future_saved_date_clean.json"
HELD = ROOT / "data" / "held.json"
PRODUCTS = ROOT / "sassy-closet-shop" / "data" / "products.json"
SCRIPT = ROOT / "scripts" / "intake_future_saved_date_flags.py"
AS_OF = "2026-10-15T00:00:00Z"

EXPECTED = (
    ("K06", "saved_after_as_of", "2026-10-16T00:00:00Z", "saved_at", True, "48"),
    ("Z01", "saved_after_as_of", "2026-10-15T00:00:01Z", "saved_at", False, "30"),
    ("Z03", "saved_after_as_of", "2026-10-16", "saved_at", False, "32"),
    ("D05", "saved_after_as_of", "2026-10-20T00:00:00Z", "updated_at", False, "26"),
    ("Z13", "saved_after_as_of", "2026-10-14T20:00:00-05:00", "saved_at", False, "28"),
    ("Z14", "saved_after_as_of", " 2026-10-16T00:00:00Z ", "saved_at", False, "29"),
)


def _payload(path: Path) -> dict[str, object]:
    loaded = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(loaded, dict)
    return loaded


def _run(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def test_gap_fixture_flags_saved_dates_after_as_of() -> None:
    original = GAPS.read_text(encoding="utf-8")
    payload = _payload(GAPS)
    rows = payload["submissions"]
    assert isinstance(rows, list)
    before = json.dumps(rows)
    report = flag_saved_after_as_of(payload, load_held_policy())
    assert json.dumps(rows) == before
    assert GAPS.read_text(encoding="utf-8") == original
    assert report.as_of == AS_OF
    found = [
        (flag.ma, flag.kind, flag.saved, flag.saved_field, flag.held, flag.sell_usd) for flag in report.flags
    ]
    assert found == list(EXPECTED)
    assert [row.ma for row in report.rows] == [
        "S06",
        "A01",
        "K06",
        "V05",
        "Z01",
        "Z02",
        "Z03",
        "Z04",
        "Z05",
        "Z06",
        "D05",
        "Z07",
        "Z08",
        "Z09",
        "Z10",
        "Z11",
        "Z12",
        "Z13",
        "Z14",
        "Z15",
        "Z16",
    ]
    by_ma = {row.ma: row for row in report.rows}
    s06 = by_ma["S06"]
    assert s06.sell_usd == "25"
    assert s06.held is False
    assert s06.kind is None
    assert s06.saved == "2026-10-05T00:00:00.000Z"
    assert report.s06_sell_usd == "25"
    assert by_ma["A01"].kind is None and by_ma["A01"].saved == AS_OF
    assert by_ma["K06"].held is True and by_ma["K06"].kind == "saved_after_as_of"
    assert by_ma["V05"].held is True and by_ma["V05"].kind is None and by_ma["V05"].saved == AS_OF
    assert by_ma["Z01"].kind == "saved_after_as_of"
    assert by_ma["Z02"].kind is None and by_ma["Z02"].saved == "2026-10-14T23:59:59Z"
    assert by_ma["Z04"].kind is None and by_ma["Z04"].saved == "2026-10-15"
    assert by_ma["Z05"].kind is None and by_ma["Z05"].saved is None and by_ma["Z05"].saved_field == ""
    assert by_ma["Z06"].kind is None and by_ma["Z06"].saved == "tomorrow"
    assert by_ma["Z07"].kind is None and by_ma["Z07"].saved is None and by_ma["Z07"].saved_field == ""
    assert by_ma["Z08"].kind is None and by_ma["Z08"].saved == "not-a-date" and by_ma["Z08"].saved_field == "saved_at"
    assert by_ma["Z09"].kind is None and by_ma["Z09"].saved_field == "savedAt"
    assert by_ma["Z11"].kind is None and by_ma["Z11"].saved_field == "saved_at"
    assert by_ma["Z12"].kind is None and by_ma["Z12"].saved == "2026-10-15T01:00:00+02:00"
    assert by_ma["Z15"].kind is None and by_ma["Z15"].saved == "false"
    assert by_ma["Z16"].kind is None and by_ma["Z16"].saved == '{"date":"2026-10-20"}'
    assert rows[19]["saved_at"] is False
    assert rows[20]["saved_at"] == {"date": "2026-10-20"}
    body = report_json(report)
    encoded = json.dumps(body)
    assert body["clockUsed"] is False
    assert body["asOf"] == AS_OF
    assert body["asOfSource"] == "fixture"
    assert body["datesChanged"] is False
    assert body["pricesChanged"] is False
    assert body["s06"] == "stays $25"
    assert body["s06SellUsd"] == "25"
    assert body["heldMas"] == "stay held"
    assert body["liveIntake"] == "refused"
    assert body["flagCount"] == 6
    assert "corrected" not in encoded
    assert "2026-12-01" not in encoded
    assert "2026-11-01" not in encoded
    assert "2026-10-15T01:00:00Z" not in encoded
    assert "2026-10-14T23:00:00Z" not in encoded
    markdown = render_markdown(report)
    assert "The as-of date comes from the fixture." in markdown
    assert "The clock is not used." in markdown
    assert "The saved date is not changed." in markdown
    assert "Prices are not changed." in markdown
    assert "S06 stays $25." in markdown
    assert "Held mãs stay held." in markdown
    assert f"As of: `{AS_OF}`" in markdown
    assert "S06 sell USD: 25" in markdown
    assert "S06 | false | saved_at | `2026-10-05T00:00:00.000Z` | 25 | —" in markdown
    assert "K06 saved_after_as_of saved `2026-10-16T00:00:00Z` stays held" in markdown
    assert "Z01 saved_after_as_of saved `2026-10-15T00:00:01Z`" in markdown
    assert "Z12 | false | saved_at | `2026-10-15T01:00:00+02:00` | 24 | —" in markdown
    assert "Z13 saved_after_as_of saved `2026-10-14T20:00:00-05:00`" in markdown
    assert "Z14 saved_after_as_of saved ` 2026-10-16T00:00:00Z `" in markdown
    assert "Flags: 6" in markdown
    assert "Rows: 21" in markdown


def test_clean_fixture_has_no_flags() -> None:
    report = flag_saved_after_as_of(_payload(CLEAN), load_held_policy())
    assert report.flag_count == 0
    assert report.as_of == AS_OF
    assert [row.ma for row in report.rows] == ["S06", "K06", "A01"]
    s06 = next(row for row in report.rows if row.ma == "S06")
    k06 = next(row for row in report.rows if row.ma == "K06")
    assert s06.sell_usd == "25" and s06.kind is None and s06.held is False
    assert k06.held is True and k06.kind is None and k06.saved == "2026-10-14T00:00:00Z"
    assert report.s06_sell_usd == "25"
    assert "None." in render_markdown(report)


def test_boundary_follows_the_fixture_as_of() -> None:
    policy = load_held_policy()
    # 2026-11-01 is after 2026-10-15 and before 2026-12-31. The fixture as-of decides.
    later_than_clock = flag_saved_after_as_of(
        {
            "asOf": "2026-12-31T00:00:00Z",
            "submissions": [{"ma": "S06", "saved_at": "2026-11-01T00:00:00Z", "sell_usd": "25"}],
        },
        policy,
    )
    assert later_than_clock.flag_count == 0
    assert later_than_clock.as_of == "2026-12-31T00:00:00Z"
    assert later_than_clock.s06_sell_usd == "25"
    assert later_than_clock.rows[0].saved == "2026-11-01T00:00:00Z"

    # 2026-01-02 is before 2026-10-15 and after 2026-01-01. The fixture as-of decides.
    earlier_than_clock = flag_saved_after_as_of(
        {
            "asOf": "2026-01-01T00:00:00Z",
            "submissions": [{"ma": "S06", "saved_at": "2026-01-02T00:00:00Z", "sell_usd": "25"}],
        },
        policy,
    )
    assert earlier_than_clock.flag_count == 1
    assert earlier_than_clock.flags[0].saved == "2026-01-02T00:00:00Z"
    assert earlier_than_clock.flags[0].sell_usd == "25"
    assert earlier_than_clock.s06_sell_usd == "25"

    equal = flag_saved_after_as_of(
        {
            "asOf": AS_OF,
            "submissions": [{"ma": "A01", "saved_at": AS_OF, "sell_usd": "27"}],
        },
        policy,
    )
    assert equal.flag_count == 0
    one_second = flag_saved_after_as_of(
        {
            "asOf": AS_OF,
            "submissions": [{"ma": "A01", "saved_at": "2026-10-15T00:00:01Z", "sell_usd": "27"}],
        },
        policy,
    )
    assert one_second.flag_count == 1
    assert one_second.flags[0].saved == "2026-10-15T00:00:01Z"
    fraction = flag_saved_after_as_of(
        {
            "asOf": AS_OF,
            "submissions": [{"ma": "A01", "saved_at": "2026-10-15T00:00:00.000001Z", "sell_usd": "27"}],
        },
        policy,
    )
    assert fraction.flag_count == 1
    same_day = flag_saved_after_as_of(
        {
            "asOf": "2026-10-15T18:00:00Z",
            "submissions": [{"ma": "A01", "saved_at": "2026-10-15", "sell_usd": "27"}],
        },
        policy,
    )
    assert same_day.flag_count == 0
    next_day = flag_saved_after_as_of(
        {
            "asOf": "2026-10-15T18:00:00Z",
            "submissions": [{"ma": "A01", "saved_at": "2026-10-16", "sell_usd": "27"}],
        },
        policy,
    )
    assert next_day.flag_count == 1
    assert next_day.flags[0].saved == "2026-10-16"

    agreed = flag_saved_after_as_of(
        {
            "asOf": "2026-10-15",
            "as_of": AS_OF,
            "submissions": [{"ma": "A01", "saved_at": "2026-10-15T00:00:01Z", "sell_usd": "10"}],
        },
        policy,
    )
    assert agreed.as_of == "2026-10-15"
    assert agreed.flag_count == 1
    only_snake = flag_saved_after_as_of(
        {
            "as_of": "2026-01-01",
            "intake": [{"ma": "k06", "saved_at": "2026-01-02", "sell_usd": "48"}],
        },
        policy,
    )
    assert only_snake.as_of == "2026-01-01"
    assert only_snake.flag_count == 1
    assert only_snake.rows[0].ma == "K06" and only_snake.rows[0].held is True
    padded = flag_saved_after_as_of(
        {
            "asOf": " 2026-10-15T00:00:00Z ",
            "submissions": [{"ma": "A01", "saved_at": "2026-10-15T00:00:01Z", "sell_usd": "10"}],
        },
        policy,
    )
    assert padded.as_of == " 2026-10-15T00:00:00Z "
    assert padded.flag_count == 1
    assert padded.flags[0].as_of == " 2026-10-15T00:00:00Z "

    with pytest.raises(ValueError, match="Fixture as-of dates disagree"):
        flag_saved_after_as_of(
            {
                "asOf": AS_OF,
                "as_of": "2026-10-16T00:00:00Z",
                "submissions": [{"ma": "A01", "saved_at": "2026-10-15T12:00:00Z", "sell_usd": "10"}],
            },
            policy,
        )
    with pytest.raises(ValueError, match="Fixture as-of date is required"):
        flag_saved_after_as_of(
            {
                "asOf": None,
                "as_of": "2026-01-01",
                "submissions": [{"ma": "A01", "saved_at": "2026-10-16T00:00:00Z", "sell_usd": "10"}],
            },
            policy,
        )
    with pytest.raises(ValueError, match="Fixture as-of date is required"):
        flag_saved_after_as_of(
            {"submissions": [{"ma": "S06", "saved_at": "2026-10-16T00:00:00Z", "sell_usd": "25"}]},
            policy,
        )
    with pytest.raises(ValueError, match="not an ISO-8601 date"):
        flag_saved_after_as_of(
            {"asOf": "tomorrow", "submissions": [{"ma": "A01", "saved_at": "2026-10-01", "sell_usd": "10"}]},
            policy,
        )
    with pytest.raises(ValueError, match="Live intake is not read"):
        flag_saved_after_as_of(
            {
                "asOf": "https://sassy-closet.vercel.app/api/submissions",
                "submissions": [],
            },
            policy,
        )


def test_s06_future_date_is_flagged_and_stays_25() -> None:
    rows = [{"ma": "s06", "saved_at": "2026-10-16T00:00:00Z", "sell_usd": "25"}]
    payload = {"asOf": AS_OF, "submissions": rows}
    before = json.dumps(payload)
    report = flag_saved_after_as_of(payload, load_held_policy())
    assert json.dumps(payload) == before
    assert rows[0]["saved_at"] == "2026-10-16T00:00:00Z"
    assert rows[0]["sell_usd"] == "25"
    assert report.flag_count == 1
    assert report.flags[0].ma == "S06"
    assert report.flags[0].kind == "saved_after_as_of"
    assert report.flags[0].saved == "2026-10-16T00:00:00Z"
    assert report.flags[0].sell_usd == "25"
    assert report.s06_sell_usd == "25"
    body = report_json(report)
    assert body["s06"] == "stays $25"
    assert body["s06SellUsd"] == "25"
    assert body["datesChanged"] is False
    assert '"sellUsd": "26"' not in json.dumps(body)
    assert '"sellUsd": "30"' not in json.dumps(body)

    numbered = [{"ma": "S06", "saved_at": "2026-10-05", "sell_usd": 25}]
    numbered_payload = {"asOf": AS_OF, "submissions": numbered}
    numbered_before = json.dumps(numbered_payload)
    numbered_report = flag_saved_after_as_of(numbered_payload, load_held_policy())
    assert json.dumps(numbered_payload) == numbered_before
    assert numbered[0]["sell_usd"] == 25
    assert numbered_report.flag_count == 0
    assert numbered_report.s06_sell_usd == "25"


def test_unreadable_date_is_copied_and_not_replaced() -> None:
    policy = load_held_policy()
    blocked = flag_saved_after_as_of(
        {
            "asOf": AS_OF,
            "submissions": [
                {
                    "ma": "Z08",
                    "saved_at": "not-a-date",
                    "updated_at": "2026-11-01T00:00:00Z",
                    "sell_usd": "21",
                }
            ],
        },
        policy,
    )
    assert blocked.flag_count == 0
    assert blocked.rows[0].saved == "not-a-date"
    assert blocked.rows[0].saved_field == "saved_at"
    assert "2026-11-01" not in json.dumps(report_json(blocked))
    invented = flag_saved_after_as_of(
        {
            "asOf": AS_OF,
            "submissions": [{"ma": "Z07", "created_at": "2026-12-01T00:00:00Z", "sell_usd": "19"}],
        },
        policy,
    )
    assert invented.flag_count == 0
    assert invented.rows[0].saved is None
    assert invented.rows[0].saved_field == ""
    assert "2026-12-01" not in json.dumps(report_json(invented))
    blank = flag_saved_after_as_of(
        {"asOf": AS_OF, "submissions": [{"ma": "V05", "saved_at": "   ", "sell_usd": "41"}]},
        policy,
    )
    assert blank.flag_count == 0
    assert blank.rows[0].saved == "   "
    assert blank.rows[0].held is True
    padded = flag_saved_after_as_of(
        {
            "asOf": AS_OF,
            "submissions": [{"ma": "Z14", "saved_at": " 2026-10-16T00:00:00Z ", "sell_usd": "29"}],
        },
        policy,
    )
    assert padded.flag_count == 1
    assert padded.flags[0].saved == " 2026-10-16T00:00:00Z "
    assert "T00:00:00Z`" not in padded.flags[0].saved


def test_held_list_is_read_only() -> None:
    policy = load_held_policy()
    assert "K06" in policy.held
    assert "V05" in policy.held
    assert "S06" not in policy.held
    report = flag_saved_after_as_of(
        {"asOf": AS_OF, "submissions": [{"ma": "A01", "saved_at": "2026-10-14", "sell_usd": "27"}]},
        policy,
    )
    assert report.flag_count == 0
    assert report.rows[0].saved == "2026-10-14"
    empty = flag_saved_after_as_of({"asOf": AS_OF, "submissions": []}, policy)
    assert empty.flag_count == 0
    assert empty.rows == ()
    assert empty.s06_sell_usd is None
    with pytest.raises(ValueError, match="mã"):
        flag_saved_after_as_of({"asOf": AS_OF, "submissions": [{"saved_at": AS_OF}]}, policy)


def test_cli_writes_a_report_and_leaves_shop_files(tmp_path: Path) -> None:
    held_bytes = HELD.read_bytes()
    products_bytes = PRODUCTS.read_bytes()
    gaps_bytes = GAPS.read_bytes()
    clean_bytes = CLEAN.read_bytes()
    held_copy = tmp_path / "held.json"
    held_copy.write_bytes(held_bytes)
    out = tmp_path / "out"
    gaps = _run(["--fixture", str(GAPS), "--held", str(held_copy), "--out", str(out)])
    assert gaps.returncode == 1, gaps.stderr
    assert "Saved dates after as-of: 6" in gaps.stdout
    markdown = (out / "intake-future-saved-date-flags.md").read_text(encoding="utf-8")
    saved = json.loads((out / "intake-future-saved-date-flags.json").read_text(encoding="utf-8"))
    assert "S06 stays $25." in markdown
    assert "The clock is not used." in markdown
    assert "The saved date is not changed." in markdown
    assert saved["flagCount"] == 6
    assert saved["clockUsed"] is False
    assert saved["asOf"] == AS_OF
    assert saved["asOfSource"] == "fixture"
    assert saved["datesChanged"] is False
    assert saved["s06SellUsd"] == "25"
    assert saved["rows"][0]["sellUsd"] == "25"
    assert saved["rows"][0]["saved"] == "2026-10-05T00:00:00.000Z"
    assert saved["pricesChanged"] is False
    assert [flag["ma"] for flag in saved["flags"]] == [item[0] for item in EXPECTED]
    assert HELD.read_bytes() == held_bytes
    assert held_copy.read_bytes() == held_bytes
    assert PRODUCTS.read_bytes() == products_bytes
    assert GAPS.read_bytes() == gaps_bytes
    assert "generatedAt" not in saved
    assert "corrected" not in json.dumps(saved)

    clean_out = tmp_path / "clean"
    clean = _run(["--fixture", str(CLEAN), "--out", str(clean_out)])
    assert clean.returncode == 0, clean.stderr
    assert json.loads((clean_out / "intake-future-saved-date-flags.json").read_text(encoding="utf-8"))["flagCount"] == 0
    assert HELD.read_bytes() == held_bytes
    assert PRODUCTS.read_bytes() == products_bytes
    assert CLEAN.read_bytes() == clean_bytes
    held_text = HELD.read_text(encoding="utf-8")
    assert "K06" in held_text
    assert "V05" in held_text


def test_cli_uses_the_fixture_as_of_not_the_clock(tmp_path: Path) -> None:
    held_bytes = HELD.read_bytes()
    products_bytes = PRODUCTS.read_bytes()
    later = tmp_path / "later.json"
    later_text = json.dumps(
        {
            "asOf": "2026-12-31T00:00:00Z",
            "submissions": [{"ma": "S06", "saved_at": "2026-11-01T00:00:00Z", "sell_usd": "25"}],
        }
    )
    later.write_text(later_text, encoding="utf-8")
    later_out = tmp_path / "later-out"
    later_run = _run(["--fixture", str(later), "--out", str(later_out)])
    assert later_run.returncode == 0, later_run.stderr
    later_saved = json.loads((later_out / "intake-future-saved-date-flags.json").read_text(encoding="utf-8"))
    assert later_saved["flagCount"] == 0
    assert later_saved["asOf"] == "2026-12-31T00:00:00Z"
    assert later_saved["clockUsed"] is False
    assert later_saved["s06SellUsd"] == "25"
    assert later_saved["rows"][0]["saved"] == "2026-11-01T00:00:00Z"
    assert later.read_text(encoding="utf-8") == later_text

    earlier = tmp_path / "earlier.json"
    earlier_text = json.dumps(
        {
            "asOf": "2026-01-01T00:00:00Z",
            "submissions": [{"ma": "S06", "saved_at": "2026-01-02T00:00:00Z", "sell_usd": "25"}],
        }
    )
    earlier.write_text(earlier_text, encoding="utf-8")
    earlier_out = tmp_path / "earlier-out"
    earlier_run = _run(["--fixture", str(earlier), "--out", str(earlier_out)])
    assert earlier_run.returncode == 1, earlier_run.stderr
    earlier_saved = json.loads((earlier_out / "intake-future-saved-date-flags.json").read_text(encoding="utf-8"))
    assert earlier_saved["flagCount"] == 1
    assert earlier_saved["asOf"] == "2026-01-01T00:00:00Z"
    assert earlier_saved["flags"][0]["saved"] == "2026-01-02T00:00:00Z"
    assert earlier_saved["flags"][0]["sellUsd"] == "25"
    assert earlier_saved["datesChanged"] is False
    assert earlier.read_text(encoding="utf-8") == earlier_text
    assert HELD.read_bytes() == held_bytes
    assert PRODUCTS.read_bytes() == products_bytes


def test_cli_refuses_live_intake_and_reserved_paths(tmp_path: Path) -> None:
    held_bytes = HELD.read_bytes()
    products_bytes = PRODUCTS.read_bytes()
    out = tmp_path / "out"
    refused = _run(
        [
            "--fixture",
            "https://sassy-closet.vercel.app/api/submissions",
            "--out",
            str(out),
        ]
    )
    assert refused.returncode == 2
    assert "Live intake is not read." in refused.stderr
    assert not out.exists()

    assert main(["--fixture", "//intake.example/rows.json", "--out", str(out)]) == 2
    assert not out.exists()

    clock_flag = _run(["--fixture", str(GAPS), "--as-of", "2099-01-01T00:00:00Z", "--out", str(out)])
    assert clock_flag.returncode == 2
    assert not out.exists()

    remote = tmp_path / "remote.json"
    remote.write_text(
        json.dumps({"intakeUrl": "https://sassy-closet.vercel.app/api/submissions", "intake": []}),
        encoding="utf-8",
    )
    assert main(["--fixture", str(remote), "--out", str(out)]) == 2
    assert not out.exists()

    missing_as_of = tmp_path / "missing-as-of.json"
    missing_as_of.write_text(
        json.dumps({"submissions": [{"ma": "S06", "saved_at": "2026-10-16T00:00:00Z", "sell_usd": "25"}]}),
        encoding="utf-8",
    )
    assert main(["--fixture", str(missing_as_of), "--out", str(out)]) == 2
    assert not out.exists()

    bad_as_of = tmp_path / "bad-as-of.json"
    bad_as_of.write_text(
        json.dumps({"asOf": "tomorrow", "submissions": [{"ma": "A01", "saved_at": "2026-10-01", "sell_usd": "10"}]}),
        encoding="utf-8",
    )
    assert main(["--fixture", str(bad_as_of), "--out", str(out)]) == 2
    assert not out.exists()

    disagree = tmp_path / "disagree.json"
    disagree.write_text(
        json.dumps(
            {
                "asOf": AS_OF,
                "as_of": "2026-10-16T00:00:00Z",
                "submissions": [{"ma": "A01", "saved_at": "2026-10-15T12:00:00Z", "sell_usd": "10"}],
            }
        ),
        encoding="utf-8",
    )
    assert main(["--fixture", str(disagree), "--out", str(out)]) == 2
    assert not out.exists()

    missing = main(["--fixture", str(tmp_path / "missing.json"), "--out", str(out)])
    assert missing == 2
    broken = tmp_path / "broken.json"
    broken.write_text("{", encoding="utf-8")
    assert main(["--fixture", str(broken), "--out", str(out)]) == 2
    reserved = main(["--fixture", str(GAPS), "--out", str(ROOT / "data")])
    assert reserved == 2
    shop_reserved = main(["--fixture", str(GAPS), "--out", str(ROOT / "sassy-closet-shop" / "data")])
    assert shop_reserved == 2
    assert HELD.read_bytes() == held_bytes
    assert PRODUCTS.read_bytes() == products_bytes
    assert not (ROOT / "data" / "intake-future-saved-date-flags.md").exists()
    assert not (ROOT / "data" / "intake-future-saved-date-flags.json").exists()
    assert not (ROOT / "sassy-closet-shop" / "data" / "intake-future-saved-date-flags.md").exists()
    assert not (ROOT / "sassy-closet-shop" / "data" / "intake-future-saved-date-flags.json").exists()


def test_script_has_no_live_client() -> None:
    text = SCRIPT.read_text(encoding="utf-8").casefold()
    assert "urllib" not in text
    assert "urlopen" not in text
    assert "requests" not in text
    assert "vercel.app" not in text
    assert "datetime.now" not in text
    assert "datetime.utcnow" not in text
    assert "date.today" not in text
    assert ".now(" not in text
    assert ".today(" not in text
    assert ".utcnow(" not in text
    assert "time.time" not in text
    assert "unlink" not in text
    assert "intake_saved_date_flags" not in text
    assert "--as-of" not in text
