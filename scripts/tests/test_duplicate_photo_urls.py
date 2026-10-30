"""Duplicate photo URLs from fixtures. Lists, prices, and held.json stay put."""

from __future__ import annotations

import io
import json
import subprocess
import sys
from contextlib import redirect_stderr
from pathlib import Path

from duplicate_photo_urls import (
    CatalogPhotoRow,
    DuplicatePhotoFlag,
    flag_duplicate_photo_urls,
    load_catalog,
    main,
)

ROOT = Path(__file__).resolve().parents[2]
HELD = ROOT / "data" / "held.json"
PRODUCTS = ROOT / "sassy-closet-shop" / "data" / "products.json"
FIXTURES = Path(__file__).resolve().parent / "fixtures"
CLEAN = FIXTURES / "duplicate_photo_urls_clean.json"
DUPES = FIXTURES / "duplicate_photo_urls_dupes.json"
HELD_BYTES = HELD.read_bytes()
PRODUCTS_BYTES = PRODUCTS.read_bytes()
CLEAN_BYTES = CLEAN.read_bytes()
DUPES_BYTES = DUPES.read_bytes()
COVER = "/products/A01/cover.jpg"


def test_repeated_url_is_flagged_and_the_list_stays() -> None:
    photos = (COVER, "/products/A01/photo-2.jpg", COVER)
    row = CatalogPhotoRow("a01", photos, None, False, "available")
    flags = flag_duplicate_photo_urls([row])
    assert row.photos is photos
    assert len(row.photos) == 3
    assert row.ma == "a01"
    assert flags == [DuplicatePhotoFlag("A01", COVER, 2, (0, 2))]
    assert set(flags[0].as_json()) == {"ma", "url", "count", "indexes"}


def test_unique_blank_and_near_strings_are_not_repeated_urls() -> None:
    rows = [
        CatalogPhotoRow("A01", (COVER, "/products/A01/photo-2.jpg"), None, False, "available"),
        CatalogPhotoRow("A02", ("", "", "  "), None, False, "available"),
        CatalogPhotoRow("A03", (COVER + " ", COVER), None, False, "available"),
        CatalogPhotoRow("A04", (COVER, COVER + "?v=2"), None, False, "available"),
        CatalogPhotoRow("A05", (COVER, "cover.jpg"), None, False, "available"),
        CatalogPhotoRow("B01", (COVER,), None, False, "available"),
        CatalogPhotoRow("B02", (), None, False, "available"),
    ]
    assert flag_duplicate_photo_urls(rows) == []
    assert rows[1].photos == ("", "", "  ")
    assert rows[2].photos[0] == COVER + " "


def test_three_copies_and_two_urls_flag_without_dropping_slots() -> None:
    triple = CatalogPhotoRow("P01", ("/products/P01/cover.jpg",) * 3, None, False, "available")
    both = CatalogPhotoRow(
        "P02",
        (
            "/products/P02/cover.jpg",
            "/products/P02/photo-2.jpg",
            "/products/P02/cover.jpg",
            "/products/P02/photo-2.jpg",
        ),
        None,
        False,
        "available",
    )
    flags = flag_duplicate_photo_urls([both, triple])
    assert triple.photos == ("/products/P01/cover.jpg",) * 3
    assert len(both.photos) == 4
    assert flags == [
        DuplicatePhotoFlag("P01", "/products/P01/cover.jpg", 3, (0, 1, 2)),
        DuplicatePhotoFlag("P02", "/products/P02/cover.jpg", 2, (0, 2)),
        DuplicatePhotoFlag("P02", "/products/P02/photo-2.jpg", 2, (1, 3)),
    ]


def test_same_url_on_two_mas_does_not_merge_rows() -> None:
    shared = "/products/shared/cover.jpg"
    first = CatalogPhotoRow("D01", (shared, "/products/D01/photo-2.jpg"), None, False, "available")
    second = CatalogPhotoRow("D02", (shared,), None, False, "sold")
    again = CatalogPhotoRow("D01", (shared, shared), None, False, "available")
    rows = [first, second, again]
    flags = flag_duplicate_photo_urls(rows)
    assert [row.ma for row in rows] == ["D01", "D02", "D01"]
    assert second.status == "sold"
    assert flags == [DuplicatePhotoFlag("D01", shared, 2, (0, 1))]


def test_s06_repeated_photo_keeps_25_and_both_copies() -> None:
    photos = ("/products/S06/cover.jpg", "/products/S06/cover.jpg")
    row = CatalogPhotoRow("S06", photos, 25, False, "available")
    flags = flag_duplicate_photo_urls([row])
    assert row.price_usd == 25
    assert row.photos is photos
    assert flags == [DuplicatePhotoFlag("S06", "/products/S06/cover.jpg", 2, (0, 1))]
    assert "priceUsd" not in flags[0].as_json()


def test_held_row_stays_held_and_held_json_is_unchanged() -> None:
    before = HELD.read_bytes()
    assert before == HELD_BYTES
    photos = ("/products/V05/cover.jpg", "/products/V05/cover.jpg")
    row = CatalogPhotoRow("V05", photos, None, True, "hold")
    flags = flag_duplicate_photo_urls([row])
    assert row.held is True
    assert row.status == "hold"
    assert row.price_usd is None
    assert row.photos == photos
    assert flags == [DuplicatePhotoFlag("V05", "/products/V05/cover.jpg", 2, (0, 1))]
    assert b'"V05"' in before
    assert b'"K06"' in before
    assert HELD.read_bytes() == before


def test_same_src_with_different_color_is_still_the_same_url(tmp_path: Path) -> None:
    raw = json.dumps(
        {
            "products": [
                {
                    "ma": "A09",
                    "priceUsd": None,
                    "status": "available",
                    "images": [
                        {"src": "/products/A09/cover.jpg", "colorId": "ca0900", "order": 1},
                        {"src": "/products/A09/photo-3.jpg", "colorId": "ca0900", "order": 2},
                        {"src": "/products/A09/cover.jpg", "colorId": "ca0901", "order": 3},
                    ],
                }
            ]
        }
    )
    path = tmp_path / "color.json"
    path.write_text(raw, encoding="utf-8")
    rows = load_catalog(path)
    flags = flag_duplicate_photo_urls(rows)
    assert rows[0].photos == (
        "/products/A09/cover.jpg",
        "/products/A09/photo-3.jpg",
        "/products/A09/cover.jpg",
    )
    assert flags == [DuplicatePhotoFlag("A09", "/products/A09/cover.jpg", 2, (0, 2))]
    assert path.read_text(encoding="utf-8") == raw


def test_images_are_the_photo_list_and_gallery_is_used_alone(tmp_path: Path) -> None:
    path = tmp_path / "both.json"
    path.write_text(
        json.dumps(
            {
                "products": [
                    {
                        "ma": "B01",
                        "priceUsd": None,
                        "images": [
                            {"src": "/products/B01/cover.jpg"},
                            {"src": "/products/B01/photo-2.jpg"},
                        ],
                        "photos": ["/products/B01/cover.jpg", "/products/B01/cover.jpg"],
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    rows = load_catalog(path)
    assert rows[0].photos == ("/products/B01/cover.jpg", "/products/B01/photo-2.jpg")
    assert flag_duplicate_photo_urls(rows) == []
    gallery = tmp_path / "gallery.json"
    gallery.write_text(
        json.dumps(
            {
                "products": [
                    {
                        "ma": "B02",
                        "gallery": [
                            "/products/B02/cover.jpg",
                            "/products/B02/photo-2.jpg",
                            "/products/B02/cover.jpg",
                        ],
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    gallery_rows = load_catalog(gallery)
    assert flag_duplicate_photo_urls(gallery_rows) == [
        DuplicatePhotoFlag("B02", "/products/B02/cover.jpg", 2, (0, 2))
    ]
    assert len(gallery_rows[0].photos) == 3


def test_dup_fixture_keeps_s06_at_25_and_held_mas() -> None:
    raw = DUPES.read_text(encoding="utf-8")
    rows = load_catalog(DUPES)
    by_ma = {row.ma: row for row in rows}
    assert [row.ma for row in rows] == ["S06", "K06", "A01", "V05", "Z81"]
    assert by_ma["S06"].price_usd == 25
    assert by_ma["S06"].held is False
    assert by_ma["S06"].photos == ("/products/S06/cover.jpg", "/products/S06/photo-2.jpg")
    assert by_ma["K06"].held is True
    assert by_ma["K06"].status == "hold"
    assert by_ma["K06"].photos == ("/products/K06/cover.jpg",)
    assert by_ma["V05"].held is True
    assert by_ma["V05"].status == "hold"
    assert by_ma["A01"].photos == (COVER, "/products/A01/photo-2.jpg", COVER)
    flags = flag_duplicate_photo_urls(rows)
    assert [flag.ma for flag in flags] == ["A01", "V05", "Z81"]
    assert all(flag.count >= 2 and flag.count == len(flag.indexes) for flag in flags)
    assert DUPES.read_text(encoding="utf-8") == raw
    assert HELD.read_bytes() == HELD_BYTES


def test_cli_dup_fixture_exits_1_and_writes_nothing() -> None:
    before = DUPES.read_bytes()
    assert before == DUPES_BYTES
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "duplicate_photo_urls.py"), "--catalog", str(DUPES)],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 1, result.stderr
    assert result.stderr == ""
    report = json.loads(result.stdout)
    assert report["readOnly"] is True
    assert report["rows"] == 5
    assert report["flags"] == [
        {"ma": "A01", "url": COVER, "count": 2, "indexes": [0, 2]},
        {
            "ma": "V05",
            "url": "/products/V05/cover.jpg",
            "count": 2,
            "indexes": [0, 1],
        },
        {
            "ma": "Z81",
            "url": "https://photos.example.test/z81/a.jpg",
            "count": 2,
            "indexes": [0, 2],
        },
    ]
    assert "priceUsd" not in result.stdout
    assert "25" not in result.stdout
    assert DUPES.read_bytes() == before == DUPES_BYTES
    assert CLEAN.read_bytes() == CLEAN_BYTES
    assert HELD.read_bytes() == HELD_BYTES
    assert PRODUCTS.read_bytes() == PRODUCTS_BYTES


def test_cli_clean_fixture_exits_0() -> None:
    before = CLEAN.read_bytes()
    assert before == CLEAN_BYTES
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "duplicate_photo_urls.py"), "--catalog", str(CLEAN)],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    report = json.loads(result.stdout)
    assert report == {"readOnly": True, "rows": 3, "flags": []}
    loaded = load_catalog(CLEAN)
    assert loaded[0].ma == "S06"
    assert loaded[0].price_usd == 25
    assert loaded[1].held is True
    assert CLEAN.read_bytes() == before == CLEAN_BYTES
    assert HELD.read_bytes() == HELD_BYTES
    assert PRODUCTS.read_bytes() == PRODUCTS_BYTES


def test_cli_refuses_live_catalog_and_urls() -> None:
    products_before = PRODUCTS.read_bytes()
    held_before = HELD.read_bytes()
    for target in (str(PRODUCTS), str(HELD), "https://sassycloset.vercel.app/m/S06"):
        code, err = _run_main(["--catalog", target])
        assert code == 2
        assert "fixtures only" in err
    assert PRODUCTS.read_bytes() == products_before == PRODUCTS_BYTES
    assert HELD.read_bytes() == held_before == HELD_BYTES


def test_cli_rejects_bad_and_missing_files(tmp_path: Path) -> None:
    path = tmp_path / "catalog.json"
    path.write_text("{", encoding="utf-8")
    code, err = _run_main(["--catalog", str(path)])
    assert code == 2
    assert err
    assert path.read_text(encoding="utf-8") == "{"
    missing = tmp_path / "missing.json"
    code, err = _run_main(["--catalog", str(missing)])
    assert code == 2
    assert err
    assert not missing.exists()
    bad = tmp_path / "shape.json"
    bad.write_text(json.dumps({"products": [{"ma": "A01", "images": {"src": COVER}}]}), encoding="utf-8")
    code, err = _run_main(["--catalog", str(bad)])
    assert code == 2
    assert "list" in err
    assert HELD.read_bytes() == HELD_BYTES


def test_script_is_fixture_only() -> None:
    text = (ROOT / "scripts" / "duplicate_photo_urls.py").read_text(encoding="utf-8")
    lowered = text.lower()
    for banned in (
        "urllib",
        "requests",
        "http.client",
        "freshness_check",
        "intake_photo_flags",
        "held_policy",
        "open(",
    ):
        assert banned not in lowered
    assert "products.json" in text


def _run_main(argv: list[str]) -> tuple[int, str]:
    err = io.StringIO()
    with redirect_stderr(err):
        code = main(argv)
    return code, err.getvalue()
