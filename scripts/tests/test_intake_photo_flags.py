"""Fixture-only intake photo flags. No live intake and no photo writes."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from held_policy import load_held_policy
from intake_photo_flags import flag_intake_photos, load_rows, main, report_json, render_markdown

ROOT = Path(__file__).resolve().parents[2]
FIXTURES = Path(__file__).resolve().parent / "fixtures"
GAPS = FIXTURES / "intake_photos_gaps.json"
CLEAN = FIXTURES / "intake_photos_clean.json"
HELD = ROOT / "data" / "held.json"
CATALOG = ROOT / "sassy-closet-shop" / "data" / "products.json"

EXPECTED: dict[str, list[tuple[str, str, str, str, bool]]] = {
    "S06": [],
    "K06": [],
    "V05": [("blank_photos", "photo_paths", "empty", "[]", True)],
    "Z81": [("blank_photos", "photo_paths", "missing", "", False)],
    "Z82": [("blank_photos", "photo_paths", "blank", '["  ","n/a",null]', False)],
    "Z83": [
        ("unusable_photo", "photo_paths[1]", "traversal", "Z83/../../secret.jpg", False),
        ("unusable_piece_photo", "pieces[0].photos[0]", "points_at_unusable", "1", False),
    ],
    "Z84": [("unusable_photo", "photo_paths[0]", "remote", "https://example.com/Z84/001.jpg", False)],
    "Z85": [("unusable_photo", "photo_paths[0]", "remote", "blob:http://localhost/1", False)],
    "Z86": [("unusable_photo", "photo_paths[0]", "not_image", "Z86/notes.txt", False)],
    "Z87": [("unusable_hash", "photo_hashes[0]", "not_sha256", "zzzz", False)],
    "Z88": [
        (
            "unusable_hash",
            "photo_hashes[0]",
            "empty_file",
            "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
            False,
        )
    ],
    "Z89": [("unusable_piece_photo", "pieces[1].photos[0]", "out_of_range", "3", False)],
    "Z90": [("unusable_photo", "photo_paths[0]", "not_a_string", "1", False)],
    "Z91": [],
    "Z92": [("unusable_photo", "photo_paths[0]", "spaced", " Z92/001.jpg", False)],
    "Z93": [("unusable_photo", "photo_paths[0]", "wrong_ma", "A01/001.jpg", False)],
    "Z94": [("unusable_photo", "photo_paths[0]", "remote", "data:image/jpeg;base64,aaaa", False)],
    "Z95": [("blank_hashes", "photo_hashes", "missing", "", False)],
    "Z96": [("unusable_hash", "photo_hashes", "length", "2 paths, 1 hashes", False)],
    "Z70": [("unusable_photo", "photo_paths[1]", "blank_entry", "", False)],
    "Z97": [("unusable_photo", "photo_paths", "not_a_list", "Z97/001.jpg", False)],
    "Z98": [("unusable_photo", "photo_paths[0]", "absolute", "/Z98/001.jpg", False)],
    "Z99": [("unusable_photo", "photo_paths[0]", "not_image", "Z99/001.gif", False)],
    "Z80": [("unusable_hash", "photo_hashes[1]", "blank_entry", "", False)],
    "Z79": [("unusable_piece_photo", "pieces[0].photos[0]", "not_an_index", "true", False)],
    "K02": [("unusable_photo", "photo_paths[0]", "not_image", "K02/001.gif", True)],
    "Z78": [],
}

USABLE = {
    "S06": 2,
    "K06": 1,
    "V05": 0,
    "Z81": 0,
    "Z82": 0,
    "Z83": 1,
    "Z84": 0,
    "Z85": 0,
    "Z86": 0,
    "Z87": 0,
    "Z88": 0,
    "Z89": 1,
    "Z90": 1,
    "Z91": 1,
    "Z92": 0,
    "Z93": 0,
    "Z94": 0,
    "Z95": 0,
    "Z96": 0,
    "Z70": 1,
    "Z97": 0,
    "Z98": 0,
    "Z99": 0,
    "Z80": 1,
    "Z79": 1,
    "K02": 0,
    "Z78": 1,
}


def _rows(path: Path) -> list[dict[str, object]]:
    return load_rows(json.loads(path.read_text(encoding="utf-8")))


def _report(path: Path):
    return flag_intake_photos(_rows(path), load_held_policy())


def test_gap_fixture_flags_blank_and_unusable_fields() -> None:
    original = GAPS.read_text(encoding="utf-8")
    rows = _rows(GAPS)
    before = json.dumps(rows)
    report = flag_intake_photos(rows, load_held_policy())
    assert json.dumps(rows) == before
    assert GAPS.read_text(encoding="utf-8") == original
    found = {
        row.ma: [(flag.kind, flag.field, flag.reason, flag.stored, flag.held) for flag in row.flags]
        for row in report.rows
    }
    assert found == EXPECTED
    assert {row.ma: row.usable_photos for row in report.rows} == USABLE
    s06 = next(row for row in report.rows if row.ma == "S06")
    z81 = next(row for row in report.rows if row.ma == "Z81")
    k06 = next(row for row in report.rows if row.ma == "K06")
    v05 = next(row for row in report.rows if row.ma == "V05")
    assert s06.sell_usd == "25"
    assert s06.held is False
    assert z81.sell_usd == "40"
    assert k06.held is True
    assert v05.held is True
    body = json.dumps(report_json(report))
    assert '"s06": "stays $25"' in body
    assert '"photoBytes": "untouched"' in body
    assert '"heldMas": "stay held"' in body
    assert "corrected" not in body
    assert "tesla" not in body.casefold()
    markdown = render_markdown(report)
    assert "Photo bytes stay untouched." in markdown
    assert "S06 stays $25." in markdown
    assert "Held mãs stay held." in markdown
    assert "S06 | false | 2 | 25 | —" in markdown
    assert "V05 blank_photos `photo_paths` empty: stored `[]` stays held" in markdown
    assert "K02 unusable_photo `photo_paths[0]` not_image: stored `K02/001.gif` stays held" in markdown
    assert "K06 | true | 1 | — | —" in markdown


def test_clean_fixture_has_no_flags() -> None:
    report = _report(CLEAN)
    assert report.flag_count == 0
    assert [row.ma for row in report.rows] == ["S06", "K06", "A01"]
    assert next(row for row in report.rows if row.ma == "S06").sell_usd == "25"
    assert next(row for row in report.rows if row.ma == "K06").held is True
    assert next(row for row in report.rows if row.ma == "A01").held is False


def test_cli_writes_a_report_and_leaves_shop_files(tmp_path: Path) -> None:
    held_bytes = HELD.read_bytes()
    catalog_bytes = CATALOG.read_bytes()
    gaps_bytes = GAPS.read_bytes()
    clean_bytes = CLEAN.read_bytes()
    out = tmp_path / "out"
    gaps = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "intake_photo_flags.py"), "--fixture", str(GAPS), "--out", str(out)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert gaps.returncode == 1, gaps.stderr
    assert "Intake photo flags:" in gaps.stdout
    markdown = (out / "intake-photo-flags.md").read_text(encoding="utf-8")
    saved = json.loads((out / "intake-photo-flags.json").read_text(encoding="utf-8"))
    assert "S06 stays $25." in markdown
    assert saved["flagCount"] == sum(len(flags) for flags in EXPECTED.values())
    assert saved["rows"][0]["sellUsd"] == "25"
    assert HELD.read_bytes() == held_bytes
    assert CATALOG.read_bytes() == catalog_bytes
    assert GAPS.read_bytes() == gaps_bytes

    clean_out = tmp_path / "clean"
    clean = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "intake_photo_flags.py"),
            "--fixture",
            str(CLEAN),
            "--out",
            str(clean_out),
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert clean.returncode == 0, clean.stderr
    assert json.loads((clean_out / "intake-photo-flags.json").read_text(encoding="utf-8"))["flagCount"] == 0
    assert HELD.read_bytes() == held_bytes
    assert CATALOG.read_bytes() == catalog_bytes
    assert CLEAN.read_bytes() == clean_bytes
    assert "K06" in HELD.read_text(encoding="utf-8")
    assert "V05" in HELD.read_text(encoding="utf-8")


def test_cli_refuses_live_intake_and_missing_files(tmp_path: Path) -> None:
    out = tmp_path / "out"
    refused = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "intake_photo_flags.py"),
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

    missing = main(["--fixture", str(tmp_path / "missing.json"), "--out", str(out)])
    assert missing == 2
    broken = tmp_path / "broken.json"
    broken.write_text("{", encoding="utf-8")
    assert main(["--fixture", str(broken), "--out", str(out)]) == 2


def test_script_has_no_live_client() -> None:
    text = (ROOT / "scripts" / "intake_photo_flags.py").read_text(encoding="utf-8").casefold()
    assert "urllib" not in text
    assert "requests" not in text
    assert "vercel.app" not in text
    assert "square.com" not in text
    assert "tesla" not in text
