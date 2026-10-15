"""Fixture-only catalog photo counts. No photo uploads and no catalog writes."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from catalog_photo_count import MIN_PHOTOS, flag_catalog, main, photo_srcs, render_markdown, report_json
from held_policy import load_held_policy

ROOT = Path(__file__).resolve().parents[2]
FIXTURES = Path(__file__).resolve().parent / "fixtures"
THIN = FIXTURES / "catalog_photos_thin.json"
OK = FIXTURES / "catalog_photos_ok.json"
HELD = ROOT / "data" / "held.json"
CATALOG = ROOT / "sassy-closet-shop" / "data" / "products.json"
SCRIPT = ROOT / "scripts" / "catalog_photo_count.py"

THIN_FLAGS = [
    ("A01", 1, False, "27", "available"),
    ("K06", 1, True, "48", "hold"),
    ("V05", 0, True, "36", "hold"),
    ("Z81", 0, False, "40", "available"),
    ("Z83", 1, False, "21", "available"),
]


def test_minimum_is_two_photos() -> None:
    assert MIN_PHOTOS == 2


def test_photo_srcs_skip_blanks_and_keep_repeats() -> None:
    images = [
        {"src": "/products/Z82/cover.jpg", "colorId": None, "order": 1},
        {"src": "/products/Z82/cover.jpg", "colorId": None, "order": 2},
        {"src": "  ", "colorId": None, "order": 3},
        {"src": None, "order": 4},
        {"order": 5},
        "  /products/Z82/photo-2.jpg  ",
        "",
        3,
    ]
    assert photo_srcs(images) == (
        "/products/Z82/cover.jpg",
        "/products/Z82/cover.jpg",
        "/products/Z82/photo-2.jpg",
    )
    assert photo_srcs(None) == ()
    assert photo_srcs("/products/Z86/cover.jpg") == ()


def test_thin_fixture_flags_galleries_under_two_photos() -> None:
    original = THIN.read_text(encoding="utf-8")
    payload = json.loads(original)
    before = json.dumps(payload)
    report = flag_catalog(payload, load_held_policy())
    assert json.dumps(payload) == before
    assert THIN.read_text(encoding="utf-8") == original
    assert report.s06_usd == "25"
    found = [
        (row.ma, row.photo_count, row.held, row.price_usd, row.status) for row in report.flags
    ]
    assert found == THIN_FLAGS
    by_ma = {row.ma: row for row in report.rows}
    assert by_ma["S06"].photo_count == 2
    assert by_ma["S06"].price_usd == "25"
    assert by_ma["S06"].held is False
    assert by_ma["S06"].thin is False
    assert by_ma["Z82"].photos == ("/products/Z82/cover.jpg", "/products/Z82/cover.jpg")
    assert by_ma["Z82"].thin is False
    assert by_ma["Z83"].photos == ("/products/Z83/cover.jpg",)
    assert by_ma["D02"].photo_count == 3
    assert by_ma["K02"].held is True
    assert by_ma["K02"].status == "hold"
    assert by_ma["K02"].photo_count == 2
    assert by_ma["K06"].status == "hold"
    assert by_ma["V05"].photo_count == 0
    body = json.dumps(report_json(report))
    assert '"s06": "stays $25"' in body
    assert '"s06Usd": "25"' in body
    assert '"photoBytes": "untouched"' in body
    assert '"heldMas": "stay held"' in body
    assert '"writes": []' in body
    assert "tesla" not in body.casefold()
    markdown = render_markdown(report)
    assert "Photo files stay untouched." in markdown
    assert "S06 stays $25." in markdown
    assert "Held mãs stay held." in markdown
    assert "S06 | 2 | false | 25 | available | —" in markdown
    assert "K06 few_photos photos 1 price 48 status hold stays held" in markdown
    assert "V05 few_photos photos 0 price 36 status hold stays held" in markdown
    assert "K02 | 2 | true | 44 | hold | —" in markdown
    assert "Catalog rows, prices, and data/held.json were not written." in markdown
    assert "Photo files were not uploaded." in markdown


def test_ok_fixture_has_no_flags() -> None:
    report = flag_catalog(json.loads(OK.read_text(encoding="utf-8")), load_held_policy())
    assert report.flag_count == 0
    assert [row.ma for row in report.rows] == ["S06", "K06", "A01"]
    s06 = report.rows[0]
    k06 = report.rows[1]
    assert s06.price_usd == "25"
    assert s06.photo_count == 2
    assert s06.held is False
    assert k06.held is True
    assert k06.photo_count == 2
    assert k06.status == "hold"
    assert "S06 stays $25." in render_markdown(report)
    assert "None." in render_markdown(report)


def test_s06_with_one_photo_keeps_25() -> None:
    row = {
        "ma": "S06",
        "priceUsd": 25,
        "status": "available",
        "images": [{"src": "/products/S06/cover.jpg", "colorId": None, "order": 1}],
    }
    report = flag_catalog({"schema": "catalog.v1", "version": 1, "products": [row]}, load_held_policy())
    assert row["priceUsd"] == 25
    assert report.s06_usd == "25"
    assert report.flag_count == 1
    assert report.flags[0].ma == "S06"
    assert report.flags[0].photo_count == 1
    assert report.flags[0].held is False
    assert report.flags[0].price_usd == "25"


def test_null_images_are_thin_and_a_bool_price_is_rejected() -> None:
    policy = load_held_policy()
    report = flag_catalog(
        {"products": [{"ma": "Z84", "priceUsd": 10, "status": "available", "images": None}]},
        policy,
    )
    assert report.rows[0].photo_count == 0
    assert report.flag_count == 1
    try:
        flag_catalog({"products": [{"ma": "Z85", "priceUsd": True}]}, policy)
    except ValueError as error:
        assert "priceUsd" in str(error)
    else:
        raise AssertionError("bool price was accepted")


def test_repeated_ma_and_intake_shape_are_rejected() -> None:
    try:
        flag_catalog(
            {"products": [{"ma": "A01", "priceUsd": 27}, {"ma": "a01", "priceUsd": 27}]},
            load_held_policy(),
        )
    except ValueError as error:
        assert "A01" in str(error)
    else:
        raise AssertionError("repeat was accepted")
    try:
        flag_catalog({"submissions": [{"ma": "S06", "photo_paths": []}]}, load_held_policy())
    except ValueError as error:
        assert "products" in str(error)
    else:
        raise AssertionError("intake shape was accepted")


def test_cli_writes_a_report_and_leaves_shop_files(tmp_path: Path) -> None:
    held_bytes = HELD.read_bytes()
    catalog_bytes = CATALOG.read_bytes()
    thin_bytes = THIN.read_bytes()
    ok_bytes = OK.read_bytes()
    out = tmp_path / "out"
    thin = subprocess.run(
        [sys.executable, str(SCRIPT), "--fixture", str(THIN), "--out", str(out)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert thin.returncode == 1, thin.stderr
    assert "Catalog photo flags: 5" in thin.stdout
    markdown = (out / "catalog-photo-count.md").read_text(encoding="utf-8")
    saved = json.loads((out / "catalog-photo-count.json").read_text(encoding="utf-8"))
    assert "S06 stays $25." in markdown
    assert "Held mãs stay held." in markdown
    assert saved["flagCount"] == 5
    assert saved["s06Usd"] == "25"
    assert saved["writes"] == []
    assert saved["flags"][1]["ma"] == "K06"
    assert saved["flags"][1]["held"] is True
    assert HELD.read_bytes() == held_bytes
    assert CATALOG.read_bytes() == catalog_bytes
    assert THIN.read_bytes() == thin_bytes
    assert "K02" in HELD.read_text(encoding="utf-8")
    assert "K06" in HELD.read_text(encoding="utf-8")
    assert "V05" in HELD.read_text(encoding="utf-8")

    clean_out = tmp_path / "clean"
    clean = subprocess.run(
        [sys.executable, str(SCRIPT), "--fixture", str(OK), "--out", str(clean_out)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert clean.returncode == 0, clean.stderr
    clean_saved = json.loads((clean_out / "catalog-photo-count.json").read_text(encoding="utf-8"))
    assert clean_saved["flagCount"] == 0
    assert clean_saved["s06Usd"] == "25"
    assert clean_saved["catalog"][1]["ma"] == "K06"
    assert clean_saved["catalog"][1]["held"] is True
    assert HELD.read_bytes() == held_bytes
    assert CATALOG.read_bytes() == catalog_bytes
    assert OK.read_bytes() == ok_bytes


def test_cli_refuses_live_catalog_and_bad_files(tmp_path: Path) -> None:
    held_bytes = HELD.read_bytes()
    catalog_bytes = CATALOG.read_bytes()
    out = tmp_path / "out"
    refused = subprocess.run(
        [sys.executable, str(SCRIPT), "--fixture", "https://example.com/catalog.json", "--out", str(out)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert refused.returncode == 2
    assert "local fixtures only" in refused.stderr
    assert not out.exists()

    live = main(["--fixture", str(CATALOG), "--out", str(out)])
    assert live == 2
    assert not out.exists()
    assert CATALOG.read_bytes() == catalog_bytes

    held = main(["--fixture", str(HELD), "--out", str(out)])
    assert held == 2
    assert HELD.read_bytes() == held_bytes

    blocked = ROOT / "data" / "not-a-real-photo-report"
    assert main(["--fixture", str(OK), "--out", str(blocked)]) == 2
    assert not blocked.exists()
    assert HELD.read_bytes() == held_bytes

    assert main(["--fixture", str(tmp_path / "missing.json"), "--out", str(out)]) == 2
    broken = tmp_path / "broken.json"
    broken.write_text("{", encoding="utf-8")
    assert main(["--fixture", str(broken), "--out", str(out)]) == 2
    assert not (out / "catalog-photo-count.json").exists()
    intake = tmp_path / "intake.json"
    intake.write_text(json.dumps({"submissions": [{"ma": "S06"}]}), encoding="utf-8")
    assert main(["--fixture", str(intake), "--out", str(out)]) == 2
    assert intake.read_text(encoding="utf-8") == json.dumps({"submissions": [{"ma": "S06"}]})


def test_script_has_no_live_client() -> None:
    text = SCRIPT.read_text(encoding="utf-8").casefold()
    assert "urllib" not in text
    assert "requests" not in text
    assert "httpx" not in text
    assert "vercel.app" not in text
    assert "square.com" not in text
    assert "tesla" not in text
    assert "facebook" not in text
    assert "freshness_check" not in text
    assert "intake_photo_flags" not in text
    assert "open(" not in text
