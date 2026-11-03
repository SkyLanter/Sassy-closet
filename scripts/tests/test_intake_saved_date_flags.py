"""Fixture-only saved-date flags. No invented dates and no live intake."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from held_policy import load_held_policy
from intake_saved_date_flags import flag_saved_dates, load_rows, main, report_json, render_markdown

ROOT = Path(__file__).resolve().parents[2]
FIXTURES = Path(__file__).resolve().parent / "fixtures"
GAPS = FIXTURES / "intake_saved_date_gaps.json"
CLEAN = FIXTURES / "intake_saved_date_clean.json"
HELD = ROOT / "data" / "held.json"
PRODUCTS = ROOT / "sassy-closet-shop" / "data" / "products.json"
SCRIPT = ROOT / "scripts" / "intake_saved_date_flags.py"

EXPECTED = (
    ("K06", "missing_saved_date", None, ""),
    ("V05", "missing_saved_date", "   ", "saved_at"),
    ("Z01", "missing_saved_date", None, "saved_at"),
    ("Z02", "unreadable_saved_date", "yesterday", "saved_at"),
    ("Z03", "unreadable_saved_date", "2026/10/01", "saved_at"),
    ("Z04", "unreadable_saved_date", "1760000000", "saved_at"),
    ("Z05", "missing_saved_date", "", "saved_at"),
    ("Z07", "unreadable_saved_date", "not-a-date", "saved_at"),
    ("Z08", "missing_saved_date", None, ""),
    ("Z10", "unreadable_saved_date", "2026-13-40", "saved_at"),
    ("Z11", "unreadable_saved_date", '{"date":"2026-10-01"}', "saved_at"),
)


def _rows(path: Path) -> list[dict[str, object]]:
    return load_rows(json.loads(path.read_text(encoding="utf-8")))


def test_gap_fixture_flags_missing_and_unreadable_dates() -> None:
    original = GAPS.read_text(encoding="utf-8")
    rows = _rows(GAPS)
    before = json.dumps(rows)
    report = flag_saved_dates(rows, load_held_policy())
    assert json.dumps(rows) == before
    assert GAPS.read_text(encoding="utf-8") == original
    assert [(flag.ma, flag.kind, flag.saved, flag.saved_field) for flag in report.flags] == list(EXPECTED)
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
        "Z07",
        "Z08",
        "Z09",
        "D05",
        "Z10",
        "Z11",
    ]
    by_ma = {row.ma: row for row in report.rows}
    s06 = by_ma["S06"]
    assert s06.sell_usd == "25"
    assert s06.held is False
    assert s06.kind is None
    assert s06.saved == "2026-10-05T00:00:00.000Z"
    assert report.s06_sell_usd == "25"
    assert by_ma["K06"].held is True and by_ma["K06"].kind == "missing_saved_date"
    assert by_ma["K06"].saved is None and by_ma["K06"].sell_usd == "48"
    assert by_ma["V05"].held is True and by_ma["V05"].saved == "   "
    assert by_ma["Z06"].kind is None and by_ma["Z06"].saved == "2026-10-14"
    assert by_ma["Z06"].saved_field == "saved_date"
    assert by_ma["Z07"].kind == "unreadable_saved_date" and by_ma["Z07"].saved == "not-a-date"
    assert by_ma["Z09"].kind is None and by_ma["Z09"].saved_field == "savedAt"
    assert by_ma["D05"].kind is None and by_ma["D05"].saved_field == "updatedAt"
    assert by_ma["A01"].kind is None and by_ma["A01"].saved_field == "updated_at"
    body = json.dumps(report_json(report))
    assert '"datesInvented": false' in body
    assert '"s06": "stays $25"' in body
    assert '"s06SellUsd": "25"' in body
    assert '"pricesChanged": false' in body
    assert '"heldMas": "stay held"' in body
    assert '"liveIntake": "refused"' in body
    assert "corrected" not in body
    assert "2026-09-01" not in body
    assert "2026-10-01T00:00:00" not in body
    markdown = render_markdown(report)
    assert "A date is not invented." in markdown
    assert "Prices are not changed." in markdown
    assert "S06 stays $25." in markdown
    assert "Held mãs stay held." in markdown
    assert "S06 sell USD: 25" in markdown
    assert "S06 | false | saved_at | `2026-10-05T00:00:00.000Z` | 25 | —" in markdown
    assert "K06 missing_saved_date saved — stays held" in markdown
    assert "V05 missing_saved_date saved `   ` stays held" in markdown
    assert "Z02 unreadable_saved_date saved `yesterday`" in markdown
    assert "Z03 unreadable_saved_date saved `2026/10/01`" in markdown
    assert "Z07 unreadable_saved_date saved `not-a-date`" in markdown
    assert "Flags: 11" in markdown
    assert "Rows: 16" in markdown


def test_clean_fixture_has_no_flags() -> None:
    report = flag_saved_dates(_rows(CLEAN), load_held_policy())
    assert report.flag_count == 0
    assert [row.ma for row in report.rows] == ["S06", "K06", "A01"]
    s06 = next(row for row in report.rows if row.ma == "S06")
    k06 = next(row for row in report.rows if row.ma == "K06")
    assert s06.sell_usd == "25" and s06.kind is None and s06.held is False
    assert k06.held is True and k06.kind is None and k06.saved == "2026-10-04T00:00:00Z"
    assert report.s06_sell_usd == "25"
    assert "None." in render_markdown(report)


def test_missing_s06_date_is_flagged_and_not_invented() -> None:
    rows = [{"ma": "s06", "sell_usd": "25", "created_at": "2026-10-01T00:00:00Z"}]
    before = json.dumps(rows)
    report = flag_saved_dates(rows, load_held_policy())
    assert json.dumps(rows) == before
    assert "saved_at" not in rows[0]
    assert report.flag_count == 1
    flag = report.flags[0]
    assert flag.ma == "S06"
    assert flag.kind == "missing_saved_date"
    assert flag.saved is None
    assert flag.saved_field == ""
    assert flag.sell_usd == "25"
    assert report.s06_sell_usd == "25"
    body = json.dumps(report_json(report))
    assert "2026-10-01" not in body
    assert "T00:00:00" not in body


def test_unreadable_date_is_copied_and_not_replaced() -> None:
    policy = load_held_policy()
    slash = flag_saved_dates([{"ma": "Z21", "saved_at": "2026/10/01", "sell_usd": "22"}], policy)
    assert slash.flags[0].kind == "unreadable_saved_date"
    assert slash.flags[0].saved == "2026/10/01"
    assert "2026-10-01" not in json.dumps(report_json(slash))
    padded = flag_saved_dates([{"ma": "Z20", "saved_at": " 2026-10-01 ", "sell_usd": "10"}], policy)
    assert padded.flag_count == 0
    assert padded.rows[0].saved == " 2026-10-01 "
    assert "T00:00:00" not in json.dumps(report_json(padded))
    date_only = flag_saved_dates([{"ma": "Z22", "saved_date": "2026-10-14"}], policy)
    assert date_only.flag_count == 0
    assert date_only.rows[0].saved == "2026-10-14"
    later = flag_saved_dates(
        [
            {
                "ma": "Z23",
                "saved_at": "not-a-date",
                "updated_at": "2026-10-14T00:00:00Z",
            }
        ],
        policy,
    )
    assert later.flags[0].saved == "not-a-date"
    assert later.flags[0].saved_field == "saved_at"
    assert "2026-10-14" not in json.dumps(report_json(later))
    shapes = flag_saved_dates(
        [
            {"ma": "Z24", "savedAt": "2026-10-15T00:00:00+00:00"},
            {"ma": "Z25", "saved_at": False},
            {"ma": "Z26", "saved_at": ["2026-10-01"]},
        ],
        policy,
    )
    assert shapes.rows[0].kind is None
    assert shapes.rows[1].kind == "unreadable_saved_date" and shapes.rows[1].saved == "false"
    assert shapes.rows[2].saved == '["2026-10-01"]'


def test_held_list_is_read_only() -> None:
    policy = load_held_policy()
    assert "K06" in policy.held
    assert "V05" in policy.held
    assert "S06" not in policy.held
    wrapped = load_rows({"submissions": [{"ma": "A01", "saved_at": "2026-10-02"}]})
    report = flag_saved_dates(wrapped, policy)
    assert report.flag_count == 0
    assert report.rows[0].saved == "2026-10-02"


def test_cli_writes_a_report_and_leaves_shop_files(tmp_path: Path) -> None:
    held_bytes = HELD.read_bytes()
    products_bytes = PRODUCTS.read_bytes()
    gaps_bytes = GAPS.read_bytes()
    clean_bytes = CLEAN.read_bytes()
    out = tmp_path / "out"
    gaps = subprocess.run(
        [sys.executable, str(SCRIPT), "--fixture", str(GAPS), "--out", str(out)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert gaps.returncode == 1, gaps.stderr
    assert "Saved-date flags: 11" in gaps.stdout
    markdown = (out / "intake-saved-date-flags.md").read_text(encoding="utf-8")
    saved = json.loads((out / "intake-saved-date-flags.json").read_text(encoding="utf-8"))
    assert "S06 stays $25." in markdown
    assert "A date is not invented." in markdown
    assert saved["flagCount"] == 11
    assert saved["datesInvented"] is False
    assert saved["s06SellUsd"] == "25"
    assert saved["rows"][0]["sellUsd"] == "25"
    assert saved["pricesChanged"] is False
    assert [flag["ma"] for flag in saved["flags"]] == [item[0] for item in EXPECTED]
    assert HELD.read_bytes() == held_bytes
    assert PRODUCTS.read_bytes() == products_bytes
    assert GAPS.read_bytes() == gaps_bytes
    assert "generatedAt" not in saved
    assert "corrected" not in json.dumps(saved)

    clean_out = tmp_path / "clean"
    clean = subprocess.run(
        [sys.executable, str(SCRIPT), "--fixture", str(CLEAN), "--out", str(clean_out)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert clean.returncode == 0, clean.stderr
    assert json.loads((clean_out / "intake-saved-date-flags.json").read_text(encoding="utf-8"))["flagCount"] == 0
    assert HELD.read_bytes() == held_bytes
    assert PRODUCTS.read_bytes() == products_bytes
    assert CLEAN.read_bytes() == clean_bytes
    held_text = HELD.read_text(encoding="utf-8")
    assert "K06" in held_text
    assert "V05" in held_text


def test_cli_refuses_live_intake_and_reserved_paths(tmp_path: Path) -> None:
    held_bytes = HELD.read_bytes()
    products_bytes = PRODUCTS.read_bytes()
    out = tmp_path / "out"
    refused = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--fixture",
            "https://sassy-closet.vercel.app/api/submissions",
            "--out",
            str(out),
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert refused.returncode == 2
    assert "Live intake is not read." in refused.stderr
    assert not out.exists()

    assert main(["--fixture", "//intake.example/rows.json", "--out", str(out)]) == 2
    assert not out.exists()

    remote = tmp_path / "remote.json"
    remote.write_text(
        json.dumps({"intakeUrl": "https://sassy-closet.vercel.app/api/submissions", "intake": []}),
        encoding="utf-8",
    )
    assert main(["--fixture", str(remote), "--out", str(out)]) == 2
    assert not out.exists()

    missing = main(["--fixture", str(tmp_path / "missing.json"), "--out", str(out)])
    assert missing == 2
    broken = tmp_path / "broken.json"
    broken.write_text("{", encoding="utf-8")
    assert main(["--fixture", str(broken), "--out", str(out)]) == 2
    reserved = main(["--fixture", str(GAPS), "--out", str(ROOT / "data")])
    assert reserved == 2
    assert HELD.read_bytes() == held_bytes
    assert PRODUCTS.read_bytes() == products_bytes
    assert not (ROOT / "data" / "intake-saved-date-flags.md").exists()
    assert not (ROOT / "data" / "intake-saved-date-flags.json").exists()


def test_script_has_no_live_client() -> None:
    text = SCRIPT.read_text(encoding="utf-8").casefold()
    assert "urllib" not in text
    assert "urlopen" not in text
    assert "requests" not in text
    assert "vercel.app" not in text
    assert "datetime.now" not in text
    assert "date.today" not in text
    assert "unlink" not in text
    assert "intake_stale_flags" not in text
