"""Fixture-only stale intake flags. No live intake and no row deletes."""

from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

from held_policy import load_held_policy
from intake_stale_flags import (
    STALE_DAYS,
    catalog_index,
    flag_stale_intake,
    load_rows,
    main,
    report_json,
    render_markdown,
)

ROOT = Path(__file__).resolve().parents[2]
FIXTURES = Path(__file__).resolve().parent / "fixtures"
GAPS = FIXTURES / "intake_stale_gaps.json"
CLEAN = FIXTURES / "intake_stale_clean.json"
CATALOG = FIXTURES / "intake_stale_catalog.json"
HELD = ROOT / "data" / "held.json"
PRODUCTS = ROOT / "sassy-closet-shop" / "data" / "products.json"
AS_OF = "2026-10-15T00:00:00Z"
CLOCK = datetime(2026, 10, 15, tzinfo=timezone.utc)
WEEK = 7 * 24 * 60 * 60

EXPECTED = ("K06", "Z02", "Z04", "Z10")


def _rows(path: Path) -> list[dict[str, object]]:
    return load_rows(json.loads(path.read_text(encoding="utf-8")))


def _catalog() -> dict[str, str | None]:
    return catalog_index(json.loads(CATALOG.read_text(encoding="utf-8")))


def _report(path: Path):
    return flag_stale_intake(_rows(path), _catalog(), load_held_policy(), CLOCK)


def test_gap_fixture_flags_only_old_rows_missing_from_catalog() -> None:
    original = GAPS.read_text(encoding="utf-8")
    catalog_original = CATALOG.read_text(encoding="utf-8")
    rows = _rows(GAPS)
    before = json.dumps(rows)
    report = flag_stale_intake(rows, _catalog(), load_held_policy(), CLOCK)
    assert json.dumps(rows) == before
    assert GAPS.read_text(encoding="utf-8") == original
    assert CATALOG.read_text(encoding="utf-8") == catalog_original
    assert [flag.ma for flag in report.flags] == list(EXPECTED)
    assert all(flag.kind == "stale_absent" and flag.as_json()["inCatalog"] is False for flag in report.flags)
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
        "Z10",
    ]
    by_ma = {row.ma: row for row in report.rows}
    s06 = by_ma["S06"]
    assert s06.sell_usd == "25"
    assert s06.held is False
    assert s06.in_catalog is True
    assert s06.flagged is False
    assert report.s06_catalog_usd == "25"
    k06 = by_ma["K06"]
    v05 = by_ma["V05"]
    z01 = by_ma["Z01"]
    z02 = by_ma["Z02"]
    assert k06.held is True and k06.flagged is True and k06.sell_usd == "48"
    assert v05.held is True and v05.flagged is False and v05.in_catalog is False
    assert z01.flagged is False and z01.age_seconds == WEEK
    assert z02.flagged is True and z02.age_seconds == WEEK + 1
    assert by_ma["Z03"].flagged is False
    assert by_ma["Z04"].flagged is True and by_ma["Z04"].saved == "2026-10-07"
    assert by_ma["Z05"].flagged is False and by_ma["Z05"].age_seconds is None
    assert by_ma["Z06"].flagged is False and by_ma["Z06"].saved == "yesterday"
    assert by_ma["D05"].in_catalog is True and by_ma["D05"].flagged is False
    assert by_ma["D05"].saved_field == "updated_at"
    assert by_ma["Z07"].flagged is False and by_ma["Z07"].saved is None
    assert by_ma["Z08"].flagged is False and by_ma["Z08"].saved_field == "saved_at"
    assert by_ma["Z10"].flagged is True and by_ma["Z10"].saved_field == "saved_date"
    assert by_ma["A01"].in_catalog is True and by_ma["A01"].flagged is False
    body = json.dumps(report_json(report))
    assert '"s06": "stays $25"' in body
    assert '"s06CatalogUsd": "25"' in body
    assert '"rowsDeleted": false' in body
    assert '"pricesChanged": false' in body
    assert '"heldMas": "stay held"' in body
    assert '"liveIntake": "refused"' in body
    assert "corrected" not in body
    markdown = render_markdown(report)
    assert "Rows are not deleted." in markdown
    assert "Prices are not changed." in markdown
    assert "S06 stays $25." in markdown
    assert "Held mãs stay held." in markdown
    assert "S06 catalog USD: 25" in markdown
    assert "S06 | false | true | 2026-09-01T00:00:00Z | 25 | —" in markdown
    assert "K06 stale_absent saved `2026-09-20T00:00:00Z` age 2160000s stays held" in markdown
    assert "V05 | true | false | 2026-10-14T00:00:00Z | — | —" in markdown
    assert "Z01 | false | false | 2026-10-08T00:00:00Z | 30 | —" in markdown
    assert STALE_DAYS == 7


def test_clean_fixture_has_no_flags() -> None:
    report = _report(CLEAN)
    assert report.flag_count == 0
    assert [row.ma for row in report.rows] == ["S06", "K06", "A01"]
    s06 = next(row for row in report.rows if row.ma == "S06")
    k06 = next(row for row in report.rows if row.ma == "K06")
    assert s06.sell_usd == "25" and s06.in_catalog is True and s06.flagged is False
    assert k06.held is True and k06.flagged is False
    assert report.s06_catalog_usd == "25"


def test_catalog_match_is_case_insensitive_and_saved_at_wins() -> None:
    catalog = catalog_index({"products": [{"ma": " s06 ", "priceUsd": 25}]})
    assert catalog["S06"] == "25"
    rows = [
        {"ma": "s06", "saved_at": "2026-01-01T00:00:00Z", "sell_usd": "25"},
        {
            "ma": "Z11",
            "saved_at": "2026-10-14T12:00:00Z",
            "updated_at": "2026-01-01T00:00:00Z",
            "sell_usd": "18",
        },
    ]
    before = json.dumps(rows)
    report = flag_stale_intake(rows, catalog, load_held_policy(), CLOCK)
    assert json.dumps(rows) == before
    assert report.flag_count == 0
    assert report.rows[0].sell_usd == "25"
    assert report.rows[1].saved == "2026-10-14T12:00:00Z"
    absent = flag_stale_intake(
        [{"ma": "S06", "updated_at": "2026-09-01T00:00:00Z", "sell_usd": "25"}],
        {},
        load_held_policy(),
        CLOCK,
    )
    assert [flag.ma for flag in absent.flags] == ["S06"]
    assert absent.flags[0].sell_usd == "25"
    assert absent.s06_catalog_usd is None


def test_one_second_past_seven_days_is_the_boundary() -> None:
    clock = datetime(2026, 10, 15, 12, 0, tzinfo=timezone.utc)
    exact = (clock - timedelta(days=7)).isoformat().replace("+00:00", "Z")
    late = (clock - timedelta(days=7, seconds=1)).isoformat().replace("+00:00", "Z")
    rows = [
        {"ma": "Z20", "saved_at": exact, "sell_usd": "11"},
        {"ma": "Z21", "saved_at": late, "sell_usd": "12"},
    ]
    report = flag_stale_intake(rows, {}, load_held_policy(), clock)
    assert [row.flagged for row in report.rows] == [False, True]
    assert report.rows[0].age_seconds == WEEK
    assert report.rows[1].age_seconds == WEEK + 1


def test_rows_catalog_shape_and_held_list_are_read_only() -> None:
    policy = load_held_policy()
    assert "K06" in policy.held
    assert "V05" in policy.held
    assert "S06" not in policy.held
    catalog = catalog_index({"rows": [{"ma": "A01", "price_usd": "27"}]})
    report = flag_stale_intake(
        [{"ma": "A01", "saved_at": "2026-01-01", "sell_usd": "27"}],
        catalog,
        policy,
        CLOCK,
    )
    assert report.flag_count == 0
    assert report.rows[0].in_catalog is True


def test_cli_writes_a_report_and_leaves_shop_files(tmp_path: Path) -> None:
    held_bytes = HELD.read_bytes()
    products_bytes = PRODUCTS.read_bytes()
    gaps_bytes = GAPS.read_bytes()
    clean_bytes = CLEAN.read_bytes()
    catalog_bytes = CATALOG.read_bytes()
    out = tmp_path / "out"
    gaps = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "intake_stale_flags.py"),
            "--fixture",
            str(GAPS),
            "--catalog",
            str(CATALOG),
            "--as-of",
            AS_OF,
            "--out",
            str(out),
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert gaps.returncode == 1, gaps.stderr
    assert "Stale intake flags: 4" in gaps.stdout
    markdown = (out / "intake-stale-flags.md").read_text(encoding="utf-8")
    saved = json.loads((out / "intake-stale-flags.json").read_text(encoding="utf-8"))
    assert "S06 stays $25." in markdown
    assert saved["flagCount"] == 4
    assert saved["s06CatalogUsd"] == "25"
    assert saved["rows"][0]["sellUsd"] == "25"
    assert saved["pricesChanged"] is False
    assert saved["rowsDeleted"] is False
    assert [flag["ma"] for flag in saved["flags"]] == list(EXPECTED)
    assert HELD.read_bytes() == held_bytes
    assert PRODUCTS.read_bytes() == products_bytes
    assert GAPS.read_bytes() == gaps_bytes
    assert CATALOG.read_bytes() == catalog_bytes
    catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
    s06 = next(row for row in catalog["products"] if row["ma"] == "S06")
    assert s06["priceUsd"] == 25 and isinstance(s06["priceUsd"], int)

    clean_out = tmp_path / "clean"
    clean = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "intake_stale_flags.py"),
            "--fixture",
            str(CLEAN),
            "--catalog",
            str(CATALOG),
            "--as-of",
            AS_OF,
            "--out",
            str(clean_out),
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert clean.returncode == 0, clean.stderr
    assert json.loads((clean_out / "intake-stale-flags.json").read_text(encoding="utf-8"))["flagCount"] == 0
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
    script = str(ROOT / "scripts" / "intake_stale_flags.py")
    refused = subprocess.run(
        [
            sys.executable,
            script,
            "--fixture",
            "https://sassy-closet.vercel.app/api/submissions",
            "--catalog",
            str(CATALOG),
            "--as-of",
            AS_OF,
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

    catalog_url = subprocess.run(
        [
            sys.executable,
            script,
            "--fixture",
            str(GAPS),
            "--catalog",
            "https://sassy-closet.vercel.app/api/submissions",
            "--out",
            str(out),
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert catalog_url.returncode == 2
    assert "Live intake is not read." in catalog_url.stderr
    assert not out.exists()

    remote = tmp_path / "remote.json"
    remote.write_text(
        json.dumps({"intakeUrl": "https://sassy-closet.vercel.app/api/submissions", "intake": []}),
        encoding="utf-8",
    )
    assert main(["--fixture", str(remote), "--catalog", str(CATALOG), "--as-of", AS_OF, "--out", str(out)]) == 2
    assert not out.exists()

    missing = main(["--fixture", str(tmp_path / "missing.json"), "--catalog", str(CATALOG), "--out", str(out)])
    assert missing == 2
    broken = tmp_path / "broken.json"
    broken.write_text("{", encoding="utf-8")
    assert main(["--fixture", str(broken), "--catalog", str(CATALOG), "--out", str(out)]) == 2
    assert main(["--fixture", str(GAPS), "--catalog", str(CATALOG), "--as-of", "2026-13-40", "--out", str(out)]) == 2
    reserved = main(["--fixture", str(GAPS), "--catalog", str(CATALOG), "--as-of", AS_OF, "--out", str(ROOT / "data")])
    assert reserved == 2
    assert HELD.read_bytes() == held_bytes
    assert PRODUCTS.read_bytes() == products_bytes
    assert not (ROOT / "data" / "intake-stale-flags.md").exists()


def test_script_has_no_live_client() -> None:
    text = (ROOT / "scripts" / "intake_stale_flags.py").read_text(encoding="utf-8").casefold()
    assert "urllib" not in text
    assert "urlopen" not in text
    assert "requests" not in text
    assert "vercel.app" not in text
    assert "square.com" not in text
    assert "unlink" not in text
    assert "intake_photo_flags" not in text
