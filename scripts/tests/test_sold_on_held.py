"""Fixture-only sold rows that are also on the held list. No live catalog and no status writes."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from held_policy import HeldPolicy, load_held_policy
from sold_on_held import flag_sold_on_held, load_rows, main, report_json, render_markdown

ROOT = Path(__file__).resolve().parents[2]
FIXTURES = Path(__file__).resolve().parent / "fixtures"
GAPS = FIXTURES / "sold_on_held_gaps.json"
CLEAN = FIXTURES / "sold_on_held_clean.json"
HELD_FIXTURE = FIXTURES / "sold_on_held_held.json"
HELD = ROOT / "data" / "held.json"
CATALOG = ROOT / "sassy-closet-shop" / "data" / "products.json"
SCRIPT = ROOT / "scripts" / "sold_on_held.py"


def _rows(path: Path) -> list[dict[str, object]]:
    return load_rows(json.loads(path.read_text(encoding="utf-8")))


def _policy() -> HeldPolicy:
    return load_held_policy(HELD_FIXTURE)


def test_gap_fixture_flags_sold_row_that_is_also_held() -> None:
    original_catalog = GAPS.read_text(encoding="utf-8")
    original_held = HELD_FIXTURE.read_text(encoding="utf-8")
    rows = _rows(GAPS)
    before_rows = json.dumps(rows)
    policy = _policy()
    before_held = policy.held
    before_never = policy.never_list
    report = flag_sold_on_held(rows, policy)
    assert json.dumps(rows) == before_rows
    assert policy.held == before_held
    assert policy.never_list == before_never
    assert report.held == ("K06", "V05", "Z96", "Z98")
    assert report.never_list == ("Z97",)
    assert GAPS.read_text(encoding="utf-8") == original_catalog
    assert HELD_FIXTURE.read_text(encoding="utf-8") == original_held
    found = {flag.ma: flag.stored for flag in report.flags}
    assert found == {"Z96": "sold"}
    assert "Z96" in report.held
    assert "Z96" in original_held
    by_ma = {row.ma: row for row in report.rows}
    assert by_ma["S06"].status == "available"
    assert by_ma["S06"].price_usd == "25"
    assert by_ma["S06"].on_held_list is False
    assert by_ma["S06"].flags == ()
    assert by_ma["D05"].status == "sold"
    assert by_ma["D05"].on_held_list is False
    assert by_ma["D05"].flags == ()
    assert by_ma["K06"].status == "held"
    assert by_ma["K06"].on_held_list is True
    assert by_ma["K06"].flags == ()
    assert by_ma["V05"].status == "hold"
    assert by_ma["V05"].on_held_list is True
    assert by_ma["V05"].flags == ()
    assert by_ma["Z96"].status == "sold"
    assert by_ma["Z96"].price_usd == "48"
    assert by_ma["Z96"].on_held_list is True
    assert by_ma["Z96"].flags[0].stored == "sold"
    assert by_ma["Z98"].status == "available"
    assert by_ma["Z98"].price_usd == "30"
    assert by_ma["Z98"].on_held_list is True
    assert by_ma["Z98"].flags == ()
    assert by_ma["Z97"].status == "sold"
    assert by_ma["Z97"].on_held_list is False
    assert by_ma["Z97"].flags == ()
    assert by_ma["Z92"].status == "SOLD"
    assert by_ma["Z92"].flags == ()
    stored = {str(row["ma"]): row for row in rows}
    assert stored["S06"]["status"] == "available"
    assert stored["S06"]["priceUsd"] == 25
    assert stored["S06"]["titleEn"] == "Washed distressed overalls"
    assert stored["Z96"]["status"] == "sold"
    assert stored["Z96"]["priceUsd"] == 48
    assert stored["Z98"]["status"] == "available"
    assert stored["D05"]["status"] == "sold"
    assert stored["K06"]["status"] == "held"
    assert stored["V05"]["status"] == "hold"
    body = json.dumps(report_json(report))
    assert '"s06": "stays $25"' in body
    assert '"s06PriceUsd": "25"' in body
    assert '"removedFromHeldList": []' in body
    assert '"statusRewrites": []' in body
    assert '"heldList": ["K06", "V05", "Z96", "Z98"]' in body
    assert '"writes": []' in body
    assert "corrected" not in body
    markdown = render_markdown(report)
    assert 'Status "sold" is flagged when that mã is also on the held list.' in markdown
    assert "The catalog status is not changed." in markdown
    assert "The mã is not removed from the held list." in markdown
    assert "S06 stays $25." in markdown
    assert "S06 | no | available | 25 | —" in markdown
    assert "D05 | no | sold | 26 | —" in markdown
    assert "K06 | yes | held | — | —" in markdown
    assert "V05 | yes | hold | — | —" in markdown
    assert "Z98 | yes | available | 30 | —" in markdown
    assert "Z96 sold_on_held stored `sold` stayed sold and stayed on the held list" in markdown
    assert "Z96 | yes | sold | 48 | sold_on_held" in markdown
    assert "Catalog rows, prices, and data/held.json were not written." in markdown


def test_clean_fixture_has_no_flags_and_s06_stays_25() -> None:
    report = flag_sold_on_held(_rows(CLEAN), _policy())
    assert report.flag_count == 0
    assert report.held == ("K06", "V05", "Z96", "Z98")
    assert report.never_list == ("Z97",)
    assert [row.ma for row in report.rows] == ["S06", "A01", "D05", "K06", "V05"]
    assert "Z96" not in [row.ma for row in report.rows]
    assert report.price_for("S06") == "25"
    s06 = next(row for row in report.rows if row.ma == "S06")
    assert s06.status == "available"
    assert s06.flags == ()
    assert s06.on_held_list is False
    d05 = next(row for row in report.rows if row.ma == "D05")
    assert d05.status == "sold"
    assert d05.flags == ()
    assert d05.on_held_list is False
    assert next(row for row in report.rows if row.ma == "K06").on_held_list is True
    assert next(row for row in report.rows if row.ma == "V05").status == "hold"


def test_other_spellings_and_statuses_are_not_rewritten() -> None:
    rows = [
        {"ma": "S06", "status": "available", "priceUsd": 25},
        {"ma": " z96 ", "status": "sold", "priceUsd": 48},
        {"ma": "Z98", "status": "available", "priceUsd": 30},
        {"ma": "K06", "status": "held", "priceUsd": None},
        {"ma": "V05", "status": "hold", "priceUsd": None},
        {"ma": "D05", "status": "sold", "priceUsd": 26},
        {"ma": "Z92", "status": "SOLD", "priceUsd": 34},
        {"ma": "Z93", "status": " sold ", "priceUsd": 33},
        {"ma": "Z91", "priceUsd": 32},
        {"ma": "Z90", "status": None, "priceUsd": 31},
        {"ma": "Z97", "status": "sold", "priceUsd": 41},
    ]
    before = json.dumps(rows)
    policy = HeldPolicy(held=("K06", "V05", "Z96", "Z98", "Z92", "Z93", "Z91", "Z90"), never_list=("Z97",))
    report = flag_sold_on_held(rows, policy)
    assert json.dumps(rows) == before
    assert policy.held == ("K06", "V05", "Z96", "Z98", "Z92", "Z93", "Z91", "Z90")
    assert policy.never_list == ("Z97",)
    assert report.held == policy.held
    assert {(flag.ma, flag.stored) for flag in report.flags} == {("Z96", "sold")}
    assert rows[0]["status"] == "available"
    assert rows[0]["priceUsd"] == 25
    assert rows[1]["status"] == "sold"
    assert rows[1]["priceUsd"] == 48
    assert rows[6]["status"] == "SOLD"
    assert rows[7]["status"] == " sold "
    assert "Z96" in policy.held
    assert "Z97" not in policy.held
    assert "D05" not in policy.held


def test_missing_s06_is_not_invented() -> None:
    rows = [{"ma": "Z96", "status": "sold", "priceUsd": 48}]
    before = json.dumps(rows)
    policy = HeldPolicy(held=("Z96",), never_list=())
    report = flag_sold_on_held(rows, policy)
    assert json.dumps(rows) == before
    assert policy.held == ("Z96",)
    assert report.price_for("S06") is None
    assert [row.ma for row in report.rows] == ["Z96"]
    assert rows[0]["status"] == "sold"
    assert rows[0]["priceUsd"] == 48
    assert report.flags[0].stored == "sold"
    assert report.flags[0].as_json()["onHeldList"] is True
    blank = [{"ma": " ", "status": "sold", "priceUsd": 25}]
    blank_before = json.dumps(blank)
    failed = False
    try:
        flag_sold_on_held(blank, policy)
    except ValueError as error:
        failed = True
        assert "mã" in str(error)
    assert failed
    assert json.dumps(blank) == blank_before
    assert policy.held == ("Z96",)


def test_cli_writes_a_report_and_does_not_change_either_status(tmp_path: Path) -> None:
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
    assert "Sold on held flags: 1" in gaps.stdout
    markdown = (out / "sold-on-held.md").read_text(encoding="utf-8")
    saved = json.loads((out / "sold-on-held.json").read_text(encoding="utf-8"))
    assert "S06 stays $25." in markdown
    assert "stayed sold and stayed on the held list" in markdown
    assert "The catalog status is not changed." in markdown
    assert saved["flagCount"] == 1
    assert saved["s06PriceUsd"] == "25"
    assert saved["removedFromHeldList"] == []
    assert saved["statusRewrites"] == []
    assert saved["heldList"] == ["K06", "V05", "Z96", "Z98"]
    assert saved["neverList"] == ["Z97"]
    assert saved["writes"] == []
    assert saved["rows"][0]["ma"] == "S06"
    assert saved["rows"][0]["status"] == "available"
    assert saved["rows"][0]["priceUsd"] == "25"
    assert saved["rows"][0]["flags"] == []
    flagged = {flag["ma"]: flag["stored"] for flag in saved["flags"]}
    assert flagged == {"Z96": "sold"}
    assert all(flag["onHeldList"] is True for flag in saved["flags"])
    catalog_after = json.loads(GAPS.read_text(encoding="utf-8"))
    stored = {row["ma"]: row for row in catalog_after["products"]}
    assert stored["Z96"]["status"] == "sold"
    assert stored["Z96"]["priceUsd"] == 48
    assert stored["S06"]["status"] == "available"
    assert stored["S06"]["priceUsd"] == 25
    assert stored["Z98"]["status"] == "available"
    assert stored["D05"]["status"] == "sold"
    held_after = json.loads(HELD_FIXTURE.read_text(encoding="utf-8"))
    assert held_after["heldIncomplete"] == ["K06", "V05", "Z96", "Z98"]
    assert held_after["neverList"] == ["Z97"]
    assert "Z96" in held_after["heldIncomplete"]
    assert HELD.read_bytes() == held_bytes
    assert CATALOG.read_bytes() == catalog_bytes
    assert GAPS.read_bytes() == gaps_bytes
    assert HELD_FIXTURE.read_bytes() == held_fixture_bytes
    assert sorted(path.name for path in (ROOT / "data").iterdir()) == data_names
    assert "Z96" not in HELD.read_text(encoding="utf-8")

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
    clean_saved = json.loads((clean_out / "sold-on-held.json").read_text(encoding="utf-8"))
    assert clean_saved["flagCount"] == 0
    assert clean_saved["s06PriceUsd"] == "25"
    assert clean_saved["removedFromHeldList"] == []
    assert clean_saved["statusRewrites"] == []
    assert "Z96" not in [row["ma"] for row in clean_saved["rows"]]
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
        ["--fixture", str(CLEAN), "--held", str(HELD_FIXTURE), "--out", str(ROOT / "data" / "sold-out")]
    )
    assert protected_out == 2
    assert not (ROOT / "data" / "sold-out").exists()
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
    nameless.write_text('{"products": [{"status": "sold", "priceUsd": 48}]}', encoding="utf-8")
    assert main(["--fixture", str(nameless), "--held", str(HELD_FIXTURE), "--out", str(out)]) == 2
    assert nameless.read_text(encoding="utf-8") == '{"products": [{"status": "sold", "priceUsd": 48}]}'
    shape = tmp_path / "shape.json"
    shape.write_text('{"schema": "catalog.v1"}', encoding="utf-8")
    assert main(["--fixture", str(shape), "--held", str(HELD_FIXTURE), "--out", str(out)]) == 2
    assert shape.read_text(encoding="utf-8") == '{"schema": "catalog.v1"}'
    dup = tmp_path / "dup-held.json"
    dup_text = '{"heldIncomplete": ["Z96", "Z96"], "neverList": []}'
    dup.write_text(dup_text, encoding="utf-8")
    assert main(["--fixture", str(CLEAN), "--held", str(dup), "--out", str(out)]) == 2
    assert dup.read_text(encoding="utf-8") == dup_text
    assert not out.exists()
    out_file = tmp_path / "out-file"
    out_file.write_text("keep", encoding="utf-8")
    assert main(["--fixture", str(CLEAN), "--held", str(HELD_FIXTURE), "--out", str(out_file)]) == 2
    assert out_file.read_text(encoding="utf-8") == "keep"
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
    assert "hold_off_list" not in folded
    assert "default_held_path" not in text
