"""Size-text flags from fixtures. Stored strings stay as they were."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from size_text import SizeText, flag_sizes, load_fixture, main, rows_from_fixture

ROOT = Path(__file__).resolve().parents[2]
FIXTURE = Path(__file__).resolve().parent / "fixtures" / "size_text.json"
HELD = ROOT / "data" / "held.json"
CATALOG = ROOT / "sassy-closet-shop" / "data" / "products.json"


def test_fixture_flags_blank_and_free_and_keeps_the_stored_text() -> None:
    raw = json.loads(FIXTURE.read_text(encoding="utf-8"))
    rows = rows_from_fixture(raw)
    before = [(row.ma, row.source, row.size_text) for row in rows]
    flags = flag_sizes(rows)
    found = {(flag.ma, flag.source, flag.kind, flag.stored) for flag in flags}
    assert ("A90", "catalog", "blank_size", "") in found
    assert ("A91", "catalog", "blank_size", "   ") in found
    assert ("A92", "catalog", "no_number", "free") in found
    assert ("A93", "catalog", "no_number", "均码") in found
    assert ("A94", "catalog", "blank_size", "") in found
    assert ("A95", "catalog", "no_number", "S") in found
    assert ("A96", "catalog", "no_number", "free") in found
    assert ("A97", "catalog", "no_number", "onesize/均码") in found
    assert ("D90", "intake", "no_number", "Freesize") in found
    assert ("D91", "intake", "no_number", "free size") in found
    assert ("D92", "intake", "no_number", "FREE") in found
    assert ("D93", "intake", "blank_size", "") in found
    assert ("H90", "intake", "blank_size", "") in found
    assert not any(flag.ma in {"A01", "A15", "G01", "S06", "D94", "D95", "Q90"} for flag in flags)
    assert not any(flag.stored == "M 90cm" for flag in flags)
    assert [(row.ma, row.source, row.size_text) for row in rows] == before
    for flag in flags:
        body = flag.as_json()
        assert "suggested" not in body
        assert "corrected" not in body
        assert set(body) == {"ma", "source", "kind", "stored"}


def test_free_with_a_measurement_is_not_rewritten() -> None:
    rows = [
        SizeText("D94", "intake", "free 80cm"),
        SizeText("D95", "intake", "Freesize 88 cm"),
        SizeText("Q90", "intake", "M 88cm"),
        SizeText("G01", "catalog", "36"),
        SizeText("A15", "catalog", "均码(建议95-150斤)"),
        SizeText("S06", "catalog", "S 84cm"),
    ]
    assert flag_sizes(rows) == []
    assert rows[0].size_text == "free 80cm"
    assert rows[5].size_text == "S 84cm"


def test_cli_prints_the_fixture_report_and_writes_nothing() -> None:
    held_before = HELD.read_bytes()
    catalog_before = CATALOG.read_bytes()
    script = ROOT / "scripts" / "size_text.py"
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
    assert any(flag["stored"] == "free" and flag["kind"] == "no_number" for flag in flags)
    assert any(flag["kind"] == "blank_size" and flag["source"] == "catalog" for flag in flags)
    assert any(flag["kind"] == "blank_size" and flag["source"] == "intake" for flag in flags)
    assert all("suggested" not in flag for flag in flags)
    assert HELD.read_bytes() == held_before
    assert CATALOG.read_bytes() == catalog_before
    assert load_fixture(FIXTURE)[0].size_text == ""


def test_missing_fixture_does_not_open_the_live_catalog() -> None:
    held_before = HELD.read_bytes()
    catalog_before = CATALOG.read_bytes()
    assert main([]) == 2
    assert HELD.read_bytes() == held_before
    assert CATALOG.read_bytes() == catalog_before


def test_held_file_is_not_a_size_fixture_and_stays_unchanged() -> None:
    before = HELD.read_bytes()
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "size_text.py"), "--fixture", str(HELD)],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 2
    assert "catalog and intake" in result.stderr
    assert HELD.read_bytes() == before


def test_checker_does_not_name_a_price_or_the_held_file() -> None:
    text = (ROOT / "scripts" / "size_text.py").read_text(encoding="utf-8")
    assert "held.json" not in text
    assert "priceUsd" not in text
    assert "vercel" not in text.lower()
