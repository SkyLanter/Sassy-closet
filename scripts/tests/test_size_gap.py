"""Size-list gap flags from fixtures. Stored lists stay as they were."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
KIT = ROOT / "excel-kit"
if str(KIT) not in sys.path:
    sys.path.insert(0, str(KIT))

from schema import INTAKE_CLOTHING_SIZES
from size_gap import CLOTHING_STEPS, SizeList, flag_size_lists, load_fixture, main, rows_from_fixture

FIXTURE = Path(__file__).resolve().parent / "fixtures" / "size_gap.json"
HELD = ROOT / "data" / "held.json"
CATALOG = ROOT / "sassy-closet-shop" / "data" / "products.json"
EXTRAS = ROOT / "sassy-closet-shop" / "data" / "intake-extras.json"


def test_ladder_matches_existing_intake_clothing_steps() -> None:
    assert CLOTHING_STEPS == INTAKE_CLOTHING_SIZES


def test_fixture_flags_a_skipped_step_and_keeps_the_stored_list() -> None:
    raw = json.loads(FIXTURE.read_text(encoding="utf-8"))
    rows = rows_from_fixture(raw)
    before = [(row.ma, row.source, row.stored, row.parts) for row in rows]
    flags = flag_size_lists(rows)
    found = {(flag.ma, flag.source, flag.kind, flag.stored, flag.skipped) for flag in flags}
    assert ("Z01", "catalog", "skipped_step", "S, L", "M") in found
    assert ("Z02", "catalog", "skipped_step", "L, S", "M") in found
    assert ("Z08", "catalog", "skipped_step", "S 84cm, L 90cm", "M") in found
    assert ("Z09", "catalog", "skipped_step", "S / L", "M") in found
    assert ("Z11", "catalog", "skipped_step", "S, XL", "M, L") in found
    assert ("Z14", "catalog", "skipped_step", "2XS, S", "XS") in found
    assert ("Z16", "intake", "skipped_step", "S, L", "M") in found
    assert ("Z19", "intake", "skipped_step", "XS, M", "S") in found
    assert ("Z23", "intake", "skipped_step", "S, M, XL", "L") in found
    quiet = {"Z03", "Z04", "Z05", "Z06", "Z07", "S06", "Z10", "Z12", "Z13", "Z15", "Z17", "Z18", "Z20", "Z21", "Z22"}
    assert not any(flag.ma in quiet for flag in flags)
    assert [(row.ma, row.source, row.stored, row.parts) for row in rows] == before
    for flag in flags:
        body = flag.as_json()
        assert "suggested" not in body
        assert "corrected" not in body
        assert set(body) == {"ma", "source", "kind", "stored", "skipped"}


def test_single_size_shoe_number_and_free_measurement_stay_quiet() -> None:
    rows = [
        SizeList("Z04", "catalog", "M", ("M",)),
        SizeList("Z05", "catalog", "36", ("36",)),
        SizeList("Z06", "catalog", "36, 38", ("36", "38")),
        SizeList("Z07", "intake", "free 80cm", ("free 80cm",)),
        SizeList("Z15", "intake", "Freesize 88 cm", ("Freesize 88 cm",)),
        SizeList("Z12", "catalog", "均码(建议95-150斤)", ("均码(建议95-150斤)",)),
        SizeList("S06", "catalog", "S 84cm", ("S 84cm",)),
        SizeList("Z18", "intake", "M 88cm", ("M 88cm",)),
        SizeList("Z30", "catalog", "s, l", ("s", "l")),
        SizeList("Z31", "intake", "XXS, M", ("XXS", "M")),
        SizeList("Z32", "catalog", "L, 3XL", ("L", "3XL")),
    ]
    flags = flag_size_lists(rows)
    found = {(flag.ma, flag.skipped, flag.stored) for flag in flags}
    assert found == {("Z30", "M", "s, l"), ("Z31", "XS, S", "XXS, M"), ("Z32", "XL", "L, 3XL")}
    assert rows[6].stored == "S 84cm"
    assert rows[2].parts == ("36", "38")


def test_cli_prints_the_fixture_report_and_writes_nothing() -> None:
    held_before = HELD.read_bytes()
    catalog_before = CATALOG.read_bytes()
    extras_before = EXTRAS.read_bytes()
    fixture_before = FIXTURE.read_bytes()
    script = ROOT / "scripts" / "size_gap.py"
    result = subprocess.run(
        [sys.executable, str(script), "--fixture", str(FIXTURE)],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    report = json.loads(result.stdout)
    flags = report["flags"]
    assert any(flag["stored"] == "S, L" and flag["skipped"] == "M" for flag in flags)
    assert any(flag["ma"] == "Z11" and flag["skipped"] == "M, L" for flag in flags)
    assert all(flag["ma"] != "S06" for flag in flags)
    assert all("priceUsd" not in flag for flag in flags)
    assert all("suggested" not in flag and "corrected" not in flag for flag in flags)
    assert HELD.read_bytes() == held_before
    assert CATALOG.read_bytes() == catalog_before
    assert EXTRAS.read_bytes() == extras_before
    assert FIXTURE.read_bytes() == fixture_before
    assert load_fixture(FIXTURE)[0].parts == ("S", "L")


def test_missing_fixture_does_not_open_the_live_catalog() -> None:
    held_before = HELD.read_bytes()
    catalog_before = CATALOG.read_bytes()
    extras_before = EXTRAS.read_bytes()
    assert main([]) == 2
    assert HELD.read_bytes() == held_before
    assert CATALOG.read_bytes() == catalog_before
    assert EXTRAS.read_bytes() == extras_before


def test_held_file_is_not_a_size_fixture_and_stays_unchanged() -> None:
    before = HELD.read_bytes()
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "size_gap.py"), "--fixture", str(HELD)],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 2
    assert "catalog and intake" in result.stderr
    assert HELD.read_bytes() == before


def test_checker_does_not_name_a_price_or_invent_a_size() -> None:
    text = (ROOT / "scripts" / "size_gap.py").read_text(encoding="utf-8")
    assert "held.json" not in text
    assert "priceUsd" not in text
    assert "vercel" not in text.lower()
    assert "suggested" not in text
    assert "corrected" not in text
    assert "3XL" not in CLOTHING_STEPS
    assert "XXS" not in CLOTHING_STEPS


def test_s06_dollar_lock_stays_25() -> None:
    assert "S06_LOCK_USD = 25" in (ROOT / "scripts" / "autolist.py").read_text(encoding="utf-8")
    assert "S06_LOCK = 25" in (ROOT / "scripts" / "pickup.py").read_text(encoding="utf-8")
    shop = (ROOT / "sassy-closet" / "lib" / "shop-catalog.ts").read_text(encoding="utf-8")
    admin = (ROOT / "sassy-closet-shop" / "lib" / "admin-ops.ts").read_text(encoding="utf-8")
    assert 'error: "S06 stays $25."' in shop
    assert 'error: "S06 stays $25."' in admin
    extras = json.loads(EXTRAS.read_text(encoding="utf-8"))
    s06 = next(row for row in extras["products"] if row["ma"] == "S06")
    assert s06["sizes"] == ["S", "M", "L"]
