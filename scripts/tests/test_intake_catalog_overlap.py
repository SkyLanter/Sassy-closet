"""Fixture-only flags for intake mãs already in the catalog. No row deletes."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from held_policy import load_held_policy
from intake_catalog_overlap import (
    catalog_index,
    flag_catalog_overlap,
    load_rows,
    main,
    report_json,
    render_markdown,
)

ROOT = Path(__file__).resolve().parents[2]
FIXTURES = Path(__file__).resolve().parent / "fixtures"
OVERLAP = FIXTURES / "intake_catalog_overlap.json"
CLEAN = FIXTURES / "intake_catalog_overlap_clean.json"
CATALOG = FIXTURES / "intake_catalog_overlap_catalog.json"
HELD = ROOT / "data" / "held.json"
PRODUCTS = ROOT / "sassy-closet-shop" / "data" / "products.json"

EXPECTED = ("S06", "A01")
KEPT = ("S06", "A01", "K06", "V05", "Z01")


def _rows(path: Path) -> list[dict[str, object]]:
    return load_rows(json.loads(path.read_text(encoding="utf-8")))


def _catalog() -> dict[str, str | None]:
    return catalog_index(json.loads(CATALOG.read_text(encoding="utf-8")))


def _report(path: Path):
    return flag_catalog_overlap(_rows(path), _catalog(), load_held_policy())


def test_overlap_fixture_flags_cataloged_mas_and_keeps_every_row() -> None:
    original = OVERLAP.read_text(encoding="utf-8")
    catalog_original = CATALOG.read_text(encoding="utf-8")
    rows = _rows(OVERLAP)
    before = json.dumps(rows)
    report = flag_catalog_overlap(rows, _catalog(), load_held_policy())
    assert json.dumps(rows) == before
    assert len(rows) == len(report.rows) == len(KEPT)
    assert OVERLAP.read_text(encoding="utf-8") == original
    assert CATALOG.read_text(encoding="utf-8") == catalog_original
    assert [flag.ma for flag in report.flags] == list(EXPECTED)
    assert all(flag.kind == "already_cataloged" and flag.as_json()["deleted"] is False for flag in report.flags)
    assert [row.ma for row in report.rows] == list(KEPT)
    assert "D05" not in {row.ma for row in report.rows}
    by_ma = {row.ma: row for row in report.rows}
    s06 = by_ma["S06"]
    assert s06.sell_usd == "25"
    assert s06.catalog_usd == "25"
    assert s06.held is False
    assert s06.in_catalog is True
    assert s06.flagged is True
    assert report.s06_catalog_usd == "25"
    assert report.s06_intake_usd == "25"
    assert report.s06_kind == "already_cataloged"
    assert by_ma["A01"].flagged is True
    assert by_ma["A01"].sell_usd == "27"
    assert by_ma["A01"].catalog_usd == "27"
    assert by_ma["K06"].held is True and by_ma["K06"].flagged is False and by_ma["K06"].sell_usd == "48"
    assert by_ma["V05"].held is True and by_ma["V05"].flagged is False and by_ma["V05"].in_catalog is False
    assert by_ma["Z01"].flagged is False and by_ma["Z01"].sell_usd == "30"
    body = json.dumps(report_json(report))
    assert '"s06": "stays $25"' in body
    assert '"s06CatalogUsd": "25"' in body
    assert '"s06IntakeUsd": "25"' in body
    assert '"s06Kind": "already_cataloged"' in body
    assert '"rowsDeleted": false' in body
    assert '"pricesChanged": false' in body
    assert '"deleted": true' not in body
    assert '"heldMas": "stay held"' in body
    assert '"liveIntake": "refused"' in body
    assert "corrected" not in body
    markdown = render_markdown(report)
    assert "Intake rows are not deleted." in markdown
    assert "Prices are not changed." in markdown
    assert "S06 stays $25 and may be flagged as already cataloged." in markdown
    assert "Held mãs stay held." in markdown
    assert "S06 catalog USD: 25" in markdown
    assert "S06 intake USD: 25" in markdown
    assert "- S06 already_cataloged sell `25` catalog `25`" in markdown
    assert "S06 | false | true | 25 | 25 | already_cataloged" in markdown
    assert "K06 | true | false | 48 | — | —" in markdown
    assert "V05 | true | false | — | — | —" in markdown
    assert "Z01 | false | false | 30 | — | —" in markdown
    catalog = json.loads(catalog_original)
    stored = next(row for row in catalog["products"] if row["ma"] == "S06")
    assert stored["priceUsd"] == 25 and isinstance(stored["priceUsd"], int)
    intake = json.loads(original)
    intake_s06 = next(row for row in intake["submissions"] if row["ma"] == "S06")
    assert intake_s06["sell_usd"] == "25" and isinstance(intake_s06["sell_usd"], str)


def test_clean_fixture_has_no_flags() -> None:
    report = _report(CLEAN)
    assert report.flag_count == 0
    assert [row.ma for row in report.rows] == ["K06", "V05", "Z01", "Z02"]
    assert all(row.flagged is False and row.in_catalog is False for row in report.rows)
    k06 = next(row for row in report.rows if row.ma == "K06")
    assert k06.held is True and k06.sell_usd == "48"
    assert report.s06_catalog_usd == "25"
    assert report.s06_intake_usd is None
    assert report.s06_kind is None
    assert "None." in render_markdown(report)


def test_s06_match_keeps_duplicate_rows_and_the_stored_price() -> None:
    catalog = catalog_index(
        {
            "products": [
                {"ma": " S06 ", "priceUsd": 25},
                {"ma": "s06", "priceUsd": 30},
                {"ma": "A01", "price_usd": "27"},
            ]
        }
    )
    assert catalog["S06"] == "25"
    assert catalog["A01"] == "27"
    rows = [
        {"ma": "s06", "sell_usd": "25"},
        {"ma": "S06", "sellUsd": "25"},
        {"ma": "Z09", "sell_usd": "18"},
    ]
    before = json.dumps(rows)
    report = flag_catalog_overlap(rows, catalog, load_held_policy())
    assert json.dumps(rows) == before
    assert [row.ma for row in report.rows] == ["S06", "S06", "Z09"]
    assert [flag.ma for flag in report.flags] == ["S06", "S06"]
    assert all(flag.sell_usd == "25" and flag.catalog_usd == "25" for flag in report.flags)
    assert report.rows[2].flagged is False
    assert report.s06_intake_usd == "25"
    assert report.s06_catalog_usd == "25"
    bare = load_rows([{"ma": "Z09", "sell_usd": "18"}])
    wrapped = load_rows({"intake": [{"ma": "Z09", "sell_usd": "18"}]})
    assert bare == wrapped
    assert flag_catalog_overlap(bare, catalog, load_held_policy()).flag_count == 0


def test_held_overlap_is_flagged_and_the_intake_row_stays() -> None:
    policy = load_held_policy()
    assert "K06" in policy.held
    assert "V05" in policy.held
    assert "S06" not in policy.held
    rows = [
        {"ma": "V05", "sell_usd": "40"},
        {"ma": "Z01", "sell_usd": "30"},
    ]
    before = json.dumps(rows)
    report = flag_catalog_overlap(rows, {"V05": "40", "S06": "25"}, policy)
    assert json.dumps(rows) == before
    assert [row.ma for row in report.rows] == ["V05", "Z01"]
    assert report.flag_count == 1
    assert report.flags[0].ma == "V05"
    assert report.flags[0].held is True
    assert report.flags[0].kind == "already_cataloged"
    assert report.rows[1].flagged is False
    assert "V05 already_cataloged sell `40` catalog `40` stays held" in render_markdown(report)
    assert report.s06_catalog_usd == "25"
    assert report.s06_intake_usd is None


def test_cli_writes_a_report_and_leaves_shop_files(tmp_path: Path) -> None:
    held_bytes = HELD.read_bytes()
    products_bytes = PRODUCTS.read_bytes()
    overlap_bytes = OVERLAP.read_bytes()
    clean_bytes = CLEAN.read_bytes()
    catalog_bytes = CATALOG.read_bytes()
    out = tmp_path / "out"
    script = ROOT / "scripts" / "intake_catalog_overlap.py"
    overlap = subprocess.run(
        [
            sys.executable,
            str(script),
            "--fixture",
            str(OVERLAP),
            "--catalog",
            str(CATALOG),
            "--out",
            str(out),
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert overlap.returncode == 1, overlap.stderr
    assert "Already cataloged intake flags: 2" in overlap.stdout
    assert "Intake rows kept: 5" in overlap.stdout
    markdown = (out / "intake-catalog-overlap.md").read_text(encoding="utf-8")
    saved = json.loads((out / "intake-catalog-overlap.json").read_text(encoding="utf-8"))
    assert "S06 stays $25 and may be flagged as already cataloged." in markdown
    assert "Intake rows are not deleted." in markdown
    assert saved["flagCount"] == 2
    assert saved["rowCount"] == 5
    assert saved["s06CatalogUsd"] == "25"
    assert saved["s06IntakeUsd"] == "25"
    assert saved["s06Kind"] == "already_cataloged"
    assert saved["rows"][0]["sellUsd"] == "25"
    assert saved["rows"][0]["deleted"] is False
    assert saved["pricesChanged"] is False
    assert saved["rowsDeleted"] is False
    assert [flag["ma"] for flag in saved["flags"]] == list(EXPECTED)
    assert [row["ma"] for row in saved["rows"]] == list(KEPT)
    assert HELD.read_bytes() == held_bytes
    assert PRODUCTS.read_bytes() == products_bytes
    assert OVERLAP.read_bytes() == overlap_bytes
    assert CATALOG.read_bytes() == catalog_bytes
    catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
    s06 = next(row for row in catalog["products"] if row["ma"] == "S06")
    assert s06["priceUsd"] == 25 and isinstance(s06["priceUsd"], int)
    intake = json.loads(OVERLAP.read_text(encoding="utf-8"))
    intake_s06 = next(row for row in intake["submissions"] if row["ma"] == "S06")
    assert intake_s06["sell_usd"] == "25"

    clean_out = tmp_path / "clean"
    clean = subprocess.run(
        [
            sys.executable,
            str(script),
            "--fixture",
            str(CLEAN),
            "--catalog",
            str(CATALOG),
            "--out",
            str(clean_out),
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert clean.returncode == 0, clean.stderr
    assert "Intake rows kept: 4" in clean.stdout
    clean_saved = json.loads((clean_out / "intake-catalog-overlap.json").read_text(encoding="utf-8"))
    assert clean_saved["flagCount"] == 0
    assert clean_saved["s06CatalogUsd"] == "25"
    assert clean_saved["rowsDeleted"] is False
    assert HELD.read_bytes() == held_bytes
    assert PRODUCTS.read_bytes() == products_bytes
    assert CLEAN.read_bytes() == clean_bytes
    held_text = HELD.read_text(encoding="utf-8")
    assert "K06" in held_text
    assert "V05" in held_text
    assert "A27" in held_text
    assert "S16" in held_text
    assert "Q02" not in held_text
    assert "S06" not in json.loads(held_text)["heldIncomplete"]


def test_cli_refuses_live_intake_and_reserved_paths(tmp_path: Path) -> None:
    held_bytes = HELD.read_bytes()
    products_bytes = PRODUCTS.read_bytes()
    out = tmp_path / "out"
    script = str(ROOT / "scripts" / "intake_catalog_overlap.py")
    refused = subprocess.run(
        [
            sys.executable,
            script,
            "--fixture",
            "https://sassy-closet.vercel.app/api/submissions",
            "--catalog",
            str(CATALOG),
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
            str(OVERLAP),
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
    assert main(["--fixture", str(remote), "--catalog", str(CATALOG), "--out", str(out)]) == 2
    assert not out.exists()

    missing = main(["--fixture", str(tmp_path / "missing.json"), "--catalog", str(CATALOG), "--out", str(out)])
    assert missing == 2
    broken = tmp_path / "broken.json"
    broken.write_text("{", encoding="utf-8")
    assert main(["--fixture", str(broken), "--catalog", str(CATALOG), "--out", str(out)]) == 2
    blank = tmp_path / "blank.json"
    blank.write_text(json.dumps([{"ma": " "}]), encoding="utf-8")
    assert main(["--fixture", str(blank), "--catalog", str(CATALOG), "--out", str(out)]) == 2
    reserved = main(["--fixture", str(OVERLAP), "--catalog", str(CATALOG), "--out", str(ROOT / "data")])
    assert reserved == 2
    shop_data = main(
        ["--fixture", str(OVERLAP), "--catalog", str(CATALOG), "--out", str(ROOT / "sassy-closet-shop" / "data")]
    )
    assert shop_data == 2
    assert HELD.read_bytes() == held_bytes
    assert PRODUCTS.read_bytes() == products_bytes
    assert not (ROOT / "data" / "intake-catalog-overlap.md").exists()
    assert not (ROOT / "sassy-closet-shop" / "data" / "intake-catalog-overlap.md").exists()


def test_script_has_no_live_client() -> None:
    text = (ROOT / "scripts" / "intake_catalog_overlap.py").read_text(encoding="utf-8").casefold()
    assert "urllib" not in text
    assert "urlopen" not in text
    assert "requests" not in text
    assert "vercel.app" not in text
    assert "square.com" not in text
    assert "unlink" not in text
    assert "next_ma_skip_intake" not in text
    assert "held.json" in text
