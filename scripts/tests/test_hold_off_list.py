"""Fixture-only hold/held rows missing from the held list. No live catalog and no list writes."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from held_policy import HeldPolicy, load_held_policy
from hold_off_list import flag_hold_off_list, load_rows, main, report_json, render_markdown

ROOT = Path(__file__).resolve().parents[2]
FIXTURES = Path(__file__).resolve().parent / "fixtures"
GAPS = FIXTURES / "hold_off_list_gaps.json"
CLEAN = FIXTURES / "hold_off_list_clean.json"
HELD_FIXTURE = FIXTURES / "hold_off_list_held.json"
HELD = ROOT / "data" / "held.json"
CATALOG = ROOT / "sassy-closet-shop" / "data" / "products.json"
SCRIPT = ROOT / "scripts" / "hold_off_list.py"


def _rows(path: Path) -> list[dict[str, object]]:
    return load_rows(json.loads(path.read_text(encoding="utf-8")))


def _policy() -> HeldPolicy:
    return load_held_policy(HELD_FIXTURE)


def test_gap_fixture_flags_hold_and_held_absent_from_the_list() -> None:
    original_catalog = GAPS.read_text(encoding="utf-8")
    original_held = HELD_FIXTURE.read_text(encoding="utf-8")
    rows = _rows(GAPS)
    before_rows = json.dumps(rows)
    policy = _policy()
    before_held = policy.held
    report = flag_hold_off_list(rows, policy)
    assert json.dumps(rows) == before_rows
    assert policy.held == before_held
    assert report.held == ("K06", "V05")
    assert GAPS.read_text(encoding="utf-8") == original_catalog
    assert HELD_FIXTURE.read_text(encoding="utf-8") == original_held
    found = {flag.ma: flag.stored for flag in report.flags}
    assert found == {"Z94": "held", "Z95": "hold"}
    assert "Z94" not in report.held
    assert "Z95" not in report.held
    assert "Z94" not in original_held
    assert "Z95" not in original_held
    by_ma = {row.ma: row for row in report.rows}
    assert by_ma["S06"].status == "available"
    assert by_ma["S06"].price_usd == "25"
    assert by_ma["S06"].on_held_list is False
    assert by_ma["S06"].flags == ()
    assert by_ma["K06"].status == "held"
    assert by_ma["K06"].on_held_list is True
    assert by_ma["K06"].flags == ()
    assert by_ma["V05"].status == "hold"
    assert by_ma["V05"].on_held_list is True
    assert by_ma["V05"].flags == ()
    assert by_ma["D05"].status == "sold"
    assert by_ma["D05"].flags == ()
    assert by_ma["Z81"].status == "reserved"
    assert by_ma["Z81"].flags == ()
    assert by_ma["Z94"].price_usd == "36"
    stored = {str(row["ma"]): row for row in rows}
    assert stored["S06"]["status"] == "available"
    assert stored["S06"]["priceUsd"] == 25
    assert stored["S06"]["titleEn"] == "Washed distressed overalls"
    assert stored["Z94"]["status"] == "held"
    assert stored["Z94"]["priceUsd"] == 36
    assert stored["Z95"]["status"] == "hold"
    assert stored["K06"]["status"] == "held"
    assert stored["V05"]["status"] == "hold"
    body = json.dumps(report_json(report))
    assert '"s06": "stays $25"' in body
    assert '"s06PriceUsd": "25"' in body
    assert '"addedToHeldList": []' in body
    assert '"heldList": ["K06", "V05"]' in body
    assert '"writes": []' in body
    assert "corrected" not in body
    markdown = render_markdown(report)
    assert 'Status "hold" or "held" is flagged when that mã is absent from the held list.' in markdown
    assert "The mã is not added to the held list." in markdown
    assert "S06 stays $25." in markdown
    assert "S06 | no | available | 25 | —" in markdown
    assert "K06 | yes | held | — | —" in markdown
    assert "V05 | yes | hold | — | —" in markdown
    assert "Z94 hold_off_list stored `held` was not added to the held list" in markdown
    assert "Z95 hold_off_list stored `hold` was not added to the held list" in markdown
    assert "Catalog rows, prices, and data/held.json were not written." in markdown


def test_clean_fixture_has_no_flags_and_s06_stays_25() -> None:
    report = flag_hold_off_list(_rows(CLEAN), _policy())
    assert report.flag_count == 0
    assert report.held == ("K06", "V05")
    assert [row.ma for row in report.rows] == ["S06", "A01", "D05", "K06", "V05"]
    assert report.price_for("S06") == "25"
    s06 = next(row for row in report.rows if row.ma == "S06")
    assert s06.status == "available"
    assert s06.flags == ()
    assert next(row for row in report.rows if row.ma == "K06").on_held_list is True
    assert next(row for row in report.rows if row.ma == "V05").status == "hold"
    assert next(row for row in report.rows if row.ma == "D05").status == "sold"


def test_other_spellings_and_listed_rows_are_not_rewritten() -> None:
    rows = [
        {"ma": "S06", "status": "available", "priceUsd": 25},
        {"ma": " z94 ", "status": "held", "priceUsd": 36},
        {"ma": "Z95", "status": "hold", "priceUsd": None},
        {"ma": "K06", "status": "held", "priceUsd": None},
        {"ma": "V05", "status": "hold", "priceUsd": None},
        {"ma": "Z92", "status": "HOLD", "priceUsd": 34},
        {"ma": "D05", "status": "sold", "priceUsd": 26},
    ]
    before = json.dumps(rows)
    policy = HeldPolicy(held=("K06", "V05"), never_list=())
    report = flag_hold_off_list(rows, policy)
    assert json.dumps(rows) == before
    assert policy.held == ("K06", "V05")
    assert report.held == ("K06", "V05")
    assert {(flag.ma, flag.stored) for flag in report.flags} == {("Z94", "held"), ("Z95", "hold")}
    assert rows[0]["status"] == "available"
    assert rows[0]["priceUsd"] == 25
    assert "Z94" not in policy.held
    assert "Z95" not in policy.held


def test_cli_writes_a_report_and_does_not_add_the_ma(tmp_path: Path) -> None:
    held_bytes = HELD.read_bytes()
    catalog_bytes = CATALOG.read_bytes()
    gaps_bytes = GAPS.read_bytes()
    clean_bytes = CLEAN.read_bytes()
    held_fixture_bytes = HELD_FIXTURE.read_bytes()
    data_names = sorted(path.name for path in (ROOT / "data").iterdir())
    out = tmp_path / "out"
    gaps = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--fixture",
            str(GAPS),
            "--held",
            str(HELD_FIXTURE),
            "--out",
            str(out),
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert gaps.returncode == 1, gaps.stderr
    assert "Hold off list flags: 2" in gaps.stdout
    markdown = (out / "hold-off-list.md").read_text(encoding="utf-8")
    saved = json.loads((out / "hold-off-list.json").read_text(encoding="utf-8"))
    assert "S06 stays $25." in markdown
    assert "was not added to the held list" in markdown
    assert saved["flagCount"] == 2
    assert saved["s06PriceUsd"] == "25"
    assert saved["addedToHeldList"] == []
    assert saved["heldList"] == ["K06", "V05"]
    assert saved["writes"] == []
    assert saved["rows"][0]["ma"] == "S06"
    assert saved["rows"][0]["status"] == "available"
    assert saved["rows"][0]["priceUsd"] == "25"
    assert saved["rows"][0]["flags"] == []
    flagged = {flag["ma"]: flag["stored"] for flag in saved["flags"]}
    assert flagged == {"Z94": "held", "Z95": "hold"}
    assert all(flag["onHeldList"] is False for flag in saved["flags"])
    held_after = json.loads(HELD_FIXTURE.read_text(encoding="utf-8"))
    assert held_after["heldIncomplete"] == ["K06", "V05"]
    assert "Z94" not in held_after["heldIncomplete"]
    assert "Z95" not in held_after["heldIncomplete"]
    assert HELD.read_bytes() == held_bytes
    assert CATALOG.read_bytes() == catalog_bytes
    assert GAPS.read_bytes() == gaps_bytes
    assert HELD_FIXTURE.read_bytes() == held_fixture_bytes
    assert sorted(path.name for path in (ROOT / "data").iterdir()) == data_names
    assert "Z94" not in HELD.read_text(encoding="utf-8")
    assert "Z95" not in HELD.read_text(encoding="utf-8")

    clean_out = tmp_path / "clean"
    clean = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--fixture",
            str(CLEAN),
            "--held",
            str(HELD_FIXTURE),
            "--out",
            str(clean_out),
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert clean.returncode == 0, clean.stderr
    clean_saved = json.loads((clean_out / "hold-off-list.json").read_text(encoding="utf-8"))
    assert clean_saved["flagCount"] == 0
    assert clean_saved["s06PriceUsd"] == "25"
    assert clean_saved["addedToHeldList"] == []
    assert HELD.read_bytes() == held_bytes
    assert CATALOG.read_bytes() == catalog_bytes
    assert CLEAN.read_bytes() == clean_bytes
    assert HELD_FIXTURE.read_bytes() == held_fixture_bytes


def test_cli_refuses_live_catalogs_shop_files_and_bad_fixtures(tmp_path: Path) -> None:
    held_bytes = HELD.read_bytes()
    catalog_bytes = CATALOG.read_bytes()
    held_fixture_bytes = HELD_FIXTURE.read_bytes()
    out = tmp_path / "out"
    refused = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--fixture",
            "https://sassycloset.vercel.app/sassy-closet-shop/catalog.v1.json",
            "--held",
            str(HELD_FIXTURE),
            "--out",
            str(out),
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert refused.returncode == 2
    assert "Live catalogs are not read." in refused.stderr
    assert not out.exists()

    shop = main(["--fixture", str(CATALOG), "--held", str(HELD_FIXTURE), "--out", str(out)])
    assert shop == 2
    assert CATALOG.read_bytes() == catalog_bytes
    assert not out.exists()

    live_held = main(["--fixture", str(CLEAN), "--held", str(HELD), "--out", str(out)])
    assert live_held == 2
    assert HELD.read_bytes() == held_bytes
    assert not out.exists()

    live_held_url = main(
        ["--fixture", str(CLEAN), "--held", "https://example.invalid/held.json", "--out", str(out)]
    )
    assert live_held_url == 2
    assert HELD.read_bytes() == held_bytes

    protected_out = main(
        ["--fixture", str(CLEAN), "--held", str(HELD_FIXTURE), "--out", str(ROOT / "data" / "hold-out")]
    )
    assert protected_out == 2
    assert not (ROOT / "data" / "hold-out").exists()
    assert HELD.read_bytes() == held_bytes

    missing = main(["--fixture", str(tmp_path / "missing.json"), "--held", str(HELD_FIXTURE), "--out", str(out)])
    assert missing == 2
    missing_held = main(["--fixture", str(CLEAN), "--held", str(tmp_path / "missing-held.json"), "--out", str(out)])
    assert missing_held == 2
    assert not (tmp_path / "missing-held.json").exists()
    broken = tmp_path / "broken.json"
    broken.write_text("{", encoding="utf-8")
    assert main(["--fixture", str(broken), "--held", str(HELD_FIXTURE), "--out", str(out)]) == 2
    assert broken.read_text(encoding="utf-8") == "{"
    nameless = tmp_path / "nameless.json"
    nameless.write_text('{"products": [{"status": "hold", "priceUsd": 25}]}', encoding="utf-8")
    assert main(["--fixture", str(nameless), "--held", str(HELD_FIXTURE), "--out", str(out)]) == 2
    assert nameless.read_text(encoding="utf-8") == '{"products": [{"status": "hold", "priceUsd": 25}]}'
    assert HELD.read_bytes() == held_bytes
    assert HELD_FIXTURE.read_bytes() == held_fixture_bytes
    assert CATALOG.read_bytes() == catalog_bytes


def test_script_has_no_live_client() -> None:
    text = SCRIPT.read_text(encoding="utf-8")
    folded = text.casefold()
    assert "urllib" not in folded
    assert "requests" not in folded
    assert "http.client" not in folded
    assert "vercel.app" not in folded
    assert "square.com" not in folded
    assert "catalog_status" not in folded
    assert "default_held_path" not in text
