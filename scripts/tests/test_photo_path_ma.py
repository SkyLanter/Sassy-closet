"""Photo path mãs from fixtures. Lists, prices, and held.json stay put."""

from __future__ import annotations
import re

import io
import json
import subprocess
import sys
from contextlib import redirect_stderr
from pathlib import Path

from photo_path_ma import CatalogPhotoRow, PhotoPathMaFlag, flag_photo_path_mas, load_catalog, main

ROOT = Path(__file__).resolve().parents[2]
HELD = ROOT / "data" / "held.json"
PRODUCTS = ROOT / "sassy-closet-shop" / "data" / "products.json"
FIXTURES = Path(__file__).resolve().parent / "fixtures"
CLEAN = FIXTURES / "photo_path_ma_clean.json"
MISMATCH = FIXTURES / "photo_path_ma_mismatch.json"
HELD_BYTES = HELD.read_bytes()
PRODUCTS_BYTES = PRODUCTS.read_bytes()
CLEAN_BYTES = CLEAN.read_bytes()
MISMATCH_BYTES = MISMATCH.read_bytes()
S06_COVER = "/products/S06/cover.jpg"
A01_COVER = "/products/A01/cover.jpg"


def _bare_numbers(text: str) -> set[str]:
    """Standalone numbers in output, ignoring anything inside a path-like token (temp dirs carry digits)."""
    words = [w for w in text.split() if "/" not in w and "\\" not in w]
    return set(re.findall(r"(?<![\w.])\d+(?:\.\d+)?(?![\w.])", " ".join(words)))


def test_a01_pointing_at_s06_is_flagged_and_the_list_stays() -> None:
    photos = (S06_COVER, "/products/A01/photo-2.jpg")
    row = CatalogPhotoRow("a01", photos, 27, False, "available")
    flags = flag_photo_path_mas([row])
    assert row.photos is photos
    assert row.ma == "a01"
    assert row.price_usd == 27
    assert flags == [PhotoPathMaFlag("A01", S06_COVER, "S06", 0)]
    assert set(flags[0].as_json()) == {"ma", "url", "pathMa", "index"}
    assert flags[0].as_json()["pathMa"] == "S06"


def test_matching_blank_and_non_product_urls_are_not_path_mismatches() -> None:
    rows = [
        CatalogPhotoRow("A01", (A01_COVER, "/products/A01/photo-2.jpg"), 27, False, "available"),
        CatalogPhotoRow("A02", ("", "  ", "/products/shared/cover.jpg"), None, False, "available"),
        CatalogPhotoRow("A03", ("/uploads/S06/cover.jpg", "S06/cover.jpg"), None, False, "available"),
        CatalogPhotoRow("A04", ("https://photos.example.test/z81/a.jpg",), None, False, "available"),
        CatalogPhotoRow("A05", ("/products/not-a-ma/cover.jpg", "/products/S6/cover.jpg"), None, False, "available"),
        CatalogPhotoRow("B01", (), None, False, "available"),
        CatalogPhotoRow(
            "S06",
            ("/products/s06/cover.jpg", "/products/S06/photo-2.jpg"),
            25,
            False,
            "available",
        ),
    ]
    assert flag_photo_path_mas(rows) == []
    assert rows[1].photos == ("", "  ", "/products/shared/cover.jpg")
    assert rows[6].price_usd == 25


def test_query_and_fragment_do_not_invent_a_second_ma() -> None:
    own = CatalogPhotoRow(
        "A01",
        (
            "/products/A01/cover.jpg?next=/products/S06/cover.jpg",
            "/products/A01/cover.jpg#/products/S06/cover.jpg",
        ),
        27,
        False,
        "available",
    )
    foreign = CatalogPhotoRow(
        "A01",
        ("/products/S06/cover.jpg?next=/products/A01/cover.jpg",),
        27,
        False,
        "available",
    )
    host = "https://sassycloset.vercel.app/products/S06/cover.jpg"
    hosted = CatalogPhotoRow("A01", (host,), 27, False, "available")
    assert flag_photo_path_mas([own]) == []
    assert own.photos[0].endswith("/products/S06/cover.jpg")
    assert flag_photo_path_mas([foreign, hosted]) == [
        PhotoPathMaFlag("A01", "/products/S06/cover.jpg?next=/products/A01/cover.jpg", "S06", 0),
        PhotoPathMaFlag("A01", host, "S06", 0),
    ]


def test_two_wrong_copies_stay_in_the_list() -> None:
    photos = (S06_COVER, S06_COVER, "/products/K06/photo-2.jpg")
    row = CatalogPhotoRow("A01", photos, 27, False, "available")
    flags = flag_photo_path_mas([row])
    assert row.photos is photos
    assert len(row.photos) == 3
    assert flags == [
        PhotoPathMaFlag("A01", S06_COVER, "S06", 0),
        PhotoPathMaFlag("A01", S06_COVER, "S06", 1),
        PhotoPathMaFlag("A01", "/products/K06/photo-2.jpg", "K06", 2),
    ]


def test_s06_keeps_25_when_a01_points_at_its_cover() -> None:
    s06_photos = (S06_COVER, "/products/S06/photo-2.jpg")
    s06 = CatalogPhotoRow("S06", s06_photos, 25, False, "available")
    a01 = CatalogPhotoRow("A01", (S06_COVER,), 27, False, "available")
    flags = flag_photo_path_mas([s06, a01])
    assert s06.price_usd == 25
    assert s06.photos is s06_photos
    assert s06.held is False
    assert a01.photos == (S06_COVER,)
    assert flags == [PhotoPathMaFlag("A01", S06_COVER, "S06", 0)]
    assert "priceUsd" not in flags[0].as_json()


def test_same_url_on_two_mas_does_not_merge_rows() -> None:
    first = CatalogPhotoRow("D01", ("/products/D01/cover.jpg",), None, False, "available")
    second = CatalogPhotoRow("D02", ("/products/D01/cover.jpg",), None, False, "sold")
    rows = [first, second]
    flags = flag_photo_path_mas(rows)
    assert [row.ma for row in rows] == ["D01", "D02"]
    assert second.status == "sold"
    assert first.photos == ("/products/D01/cover.jpg",)
    assert flags == [PhotoPathMaFlag("D02", "/products/D01/cover.jpg", "D01", 0)]


def test_held_row_stays_held_and_held_json_is_unchanged() -> None:
    before = HELD.read_bytes()
    assert before == HELD_BYTES
    photos = ("/products/K06/cover.jpg",)
    row = CatalogPhotoRow("V05", photos, None, True, "hold")
    flags = flag_photo_path_mas([row])
    assert row.held is True
    assert row.status == "hold"
    assert row.price_usd is None
    assert row.photos == photos
    assert flags == [PhotoPathMaFlag("V05", "/products/K06/cover.jpg", "K06", 0)]
    assert b'"V05"' in before
    assert b'"K06"' in before
    assert HELD.read_bytes() == before


def test_spaced_row_and_lowercase_folder() -> None:
    photos = (" /products/s06/cover.jpg ", "/products/a01/photo-2.jpg")
    row = CatalogPhotoRow(" a01 ", photos, 27, False, "available")
    flags = flag_photo_path_mas([row])
    assert row.photos is photos
    assert flags == [PhotoPathMaFlag("A01", " /products/s06/cover.jpg ", "S06", 0)]


def test_color_does_not_decide_the_path_ma(tmp_path: Path) -> None:
    raw = json.dumps(
        {
            "products": [
                {
                    "ma": "A01",
                    "priceUsd": 27,
                    "status": "available",
                    "images": [
                        {"src": A01_COVER, "colorId": "ca0101", "order": 1},
                        {"src": S06_COVER, "colorId": "ca0100", "order": 2},
                    ],
                }
            ]
        }
    )
    path = tmp_path / "color.json"
    path.write_text(raw, encoding="utf-8")
    rows = load_catalog(path)
    flags = flag_photo_path_mas(rows)
    assert rows[0].photos == (A01_COVER, S06_COVER)
    assert rows[0].price_usd == 27
    assert flags == [PhotoPathMaFlag("A01", S06_COVER, "S06", 1)]
    assert path.read_text(encoding="utf-8") == raw


def test_images_are_the_photo_list_and_gallery_is_used_alone(tmp_path: Path) -> None:
    path = tmp_path / "both.json"
    path.write_text(
        json.dumps(
            {
                "products": [
                    {
                        "ma": "A01",
                        "priceUsd": 27,
                        "images": [A01_COVER, "/products/A01/photo-2.jpg"],
                        "photos": [S06_COVER, S06_COVER],
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    rows = load_catalog(path)
    assert rows[0].photos == (A01_COVER, "/products/A01/photo-2.jpg")
    assert flag_photo_path_mas(rows) == []
    gallery = tmp_path / "gallery.json"
    gallery.write_text(
        json.dumps({"products": [{"ma": "A01", "gallery": [S06_COVER, A01_COVER]}]}),
        encoding="utf-8",
    )
    gallery_rows = load_catalog(gallery)
    assert flag_photo_path_mas(gallery_rows) == [PhotoPathMaFlag("A01", S06_COVER, "S06", 0)]
    assert gallery_rows[0].photos == (S06_COVER, A01_COVER)


def test_url_and_path_keys_and_a_bare_list(tmp_path: Path) -> None:
    raw = json.dumps(
        [
            {"ma": "A01", "gallery_urls": [{"url": S06_COVER}, {"path": A01_COVER}]},
            {"ma": "B01", "photos": [{"src": "", "url": S06_COVER}]},
        ]
    )
    path = tmp_path / "keys.json"
    path.write_text(raw, encoding="utf-8")
    rows = load_catalog(path)
    assert rows[0].photos == (S06_COVER, A01_COVER)
    assert rows[1].photos == ("",)
    assert flag_photo_path_mas(rows) == [PhotoPathMaFlag("A01", S06_COVER, "S06", 0)]
    assert path.read_text(encoding="utf-8") == raw


def test_mismatch_fixture_keeps_s06_at_25_and_held_mas() -> None:
    raw = MISMATCH.read_text(encoding="utf-8")
    rows = load_catalog(MISMATCH)
    by_ma = {row.ma: row for row in rows}
    assert [row.ma for row in rows] == ["S06", "K06", "A01", "V05", "Z81"]
    assert by_ma["S06"].price_usd == 25
    assert by_ma["S06"].held is False
    assert by_ma["S06"].photos == (S06_COVER, "/products/S06/photo-2.jpg")
    assert by_ma["K06"].held is True
    assert by_ma["K06"].status == "hold"
    assert by_ma["K06"].photos == ("/products/K06/cover.jpg",)
    assert by_ma["V05"].held is True
    assert by_ma["V05"].status == "hold"
    assert by_ma["A01"].price_usd == 27
    assert by_ma["A01"].photos == (S06_COVER, "/products/A01/photo-2.jpg")
    assert by_ma["Z81"].photos == (
        "https://photos.example.test/z81/a.jpg",
        "/uploads/S06/cover.jpg",
        "/products/shared/cover.jpg",
    )
    flags = flag_photo_path_mas(rows)
    assert flags == [
        PhotoPathMaFlag("A01", S06_COVER, "S06", 0),
        PhotoPathMaFlag("V05", "/products/K06/cover.jpg", "K06", 0),
    ]
    assert MISMATCH.read_text(encoding="utf-8") == raw
    assert HELD.read_bytes() == HELD_BYTES
    assert PRODUCTS.read_bytes() == PRODUCTS_BYTES


def test_cli_mismatch_fixture_exits_1_and_writes_nothing() -> None:
    before = MISMATCH.read_bytes()
    assert before == MISMATCH_BYTES
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "photo_path_ma.py"), "--catalog", str(MISMATCH)],
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
        {"ma": "A01", "url": S06_COVER, "pathMa": "S06", "index": 0},
        {"ma": "V05", "url": "/products/K06/cover.jpg", "pathMa": "K06", "index": 0},
    ]
    assert "priceUsd" not in result.stdout
    assert _bare_numbers(result.stdout).isdisjoint({"25"})
    assert "tesla" not in result.stdout.casefold()
    assert MISMATCH.read_bytes() == before == MISMATCH_BYTES
    assert CLEAN.read_bytes() == CLEAN_BYTES
    assert HELD.read_bytes() == HELD_BYTES
    assert PRODUCTS.read_bytes() == PRODUCTS_BYTES


def test_cli_clean_fixture_exits_0() -> None:
    before = CLEAN.read_bytes()
    assert before == CLEAN_BYTES
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "photo_path_ma.py"), "--catalog", str(CLEAN)],
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
    assert loaded[0].photos == (S06_COVER, "/products/S06/photo-2.jpg")
    assert loaded[1].held is True
    assert loaded[2].photos == (A01_COVER, "/products/A01/photo-2.jpg")
    assert CLEAN.read_bytes() == before == CLEAN_BYTES
    assert HELD.read_bytes() == HELD_BYTES
    assert PRODUCTS.read_bytes() == PRODUCTS_BYTES


def test_cli_refuses_live_catalog_and_urls() -> None:
    products_before = PRODUCTS.read_bytes()
    held_before = HELD.read_bytes()
    for target in (
        str(PRODUCTS),
        str(HELD),
        "sassy-closet-shop/data/products.json",
        "data/held.json",
        "https://sassycloset.vercel.app/m/S06",
    ):
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
    bad.write_text(json.dumps({"products": [{"ma": "A01", "images": {"src": S06_COVER}}]}), encoding="utf-8")
    code, err = _run_main(["--catalog", str(bad)])
    assert code == 2
    assert "list" in err
    empty_ma = tmp_path / "empty.json"
    empty_ma.write_text(json.dumps({"products": [{"ma": "  "}]}), encoding="utf-8")
    code, err = _run_main(["--catalog", str(empty_ma)])
    assert code == 2
    assert "mã" in err
    assert HELD.read_bytes() == HELD_BYTES
    assert PRODUCTS.read_bytes() == PRODUCTS_BYTES


def test_script_is_fixture_only() -> None:
    text = (ROOT / "scripts" / "photo_path_ma.py").read_text(encoding="utf-8")
    lowered = text.casefold()
    for banned in (
        "urllib",
        "requests",
        "http.client",
        "freshness_check",
        "intake_photo_flags",
        "duplicate_photo_urls",
        "held_policy",
        "open(",
        "write_text",
        "write_bytes",
        "tesla",
    ):
        assert banned not in lowered
    assert "products.json" in text
    assert "held.json" in text


def _run_main(argv: list[str]) -> tuple[int, str]:
    err = io.StringIO()
    with redirect_stderr(err):
        code = main(argv)
    return code, err.getvalue()
