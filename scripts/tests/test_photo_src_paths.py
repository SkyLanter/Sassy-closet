"""Photo src site-path flags from fixtures. Srcs, prices, and held.json stay put."""

from __future__ import annotations
import re

import io
import json
import subprocess
import sys
from contextlib import redirect_stderr
from pathlib import Path

from photo_src_paths import (
    CatalogPhotoRow,
    PhotoSrcFlag,
    flag_photo_src_paths,
    load_catalog,
    main,
    src_kind,
)

ROOT = Path(__file__).resolve().parents[2]
HELD = ROOT / "data" / "held.json"
PRODUCTS = ROOT / "sassy-closet-shop" / "data" / "products.json"
FIXTURES = Path(__file__).resolve().parent / "fixtures"
CLEAN = FIXTURES / "photo_src_paths_ok.json"
BAD = FIXTURES / "photo_src_paths_bad.json"
HELD_BYTES = HELD.read_bytes()
PRODUCTS_BYTES = PRODUCTS.read_bytes()
CLEAN_BYTES = CLEAN.read_bytes()
BAD_BYTES = BAD.read_bytes()
COVER = "/products/S06/cover.jpg"
HTTP_SRC = "https://cdn.example.test/s06/photo-2.jpg"
DATA_SRC = "data:image/jpeg;base64,aaaa"
TRAVERSAL = "/products/../etc/passwd"


def _bare_numbers(text: str) -> set[str]:
    """Standalone numbers in output, ignoring anything inside a path-like token (temp dirs carry digits)."""
    words = [w for w in text.split() if "/" not in w and "\\" not in w]
    return set(re.findall(r"(?<![\w.])\d+(?:\.\d+)?(?![\w.])", " ".join(words)))


def test_site_path_stays_quiet_and_http_data_blank_are_flagged() -> None:
    assert src_kind(COVER) is None
    assert src_kind("/products/S06/photo-2.jpg") is None
    assert src_kind("/products/A01/cover.jpg?v=2") is None
    assert src_kind("https://cdn.example.test/a.jpg") == "http_url"
    assert src_kind("HTTP://cdn.example.test/a.jpg") == "http_url"
    assert src_kind(" http://cdn.example.test/a.jpg") == "http_url"
    assert src_kind(DATA_SRC) == "data_url"
    assert src_kind("Data:text/plain,hi") == "data_url"
    assert src_kind("") == "blank"
    assert src_kind("   ") == "blank"
    assert src_kind("\n") == "blank"
    assert src_kind("products/S06/cover.jpg") == "not_site_path"
    assert src_kind("images/a01.jpg") == "not_site_path"
    assert src_kind("/etc/passwd") == "not_site_path"
    assert src_kind("/products") == "not_site_path"
    assert src_kind("/Products/S06/cover.jpg") == "not_site_path"
    assert src_kind("//cdn.example.test/a.jpg") == "not_site_path"
    assert src_kind(COVER + " ") == "not_site_path"
    assert src_kind("/products/S06/../cover.jpg") == "not_site_path"
    assert src_kind(TRAVERSAL) == "not_site_path"


def test_s06_cover_stays_quiet_while_a_full_url_on_the_same_row_is_flagged() -> None:
    photos = (COVER, HTTP_SRC)
    row = CatalogPhotoRow("s06", photos, 25, False, "available")
    flags = flag_photo_src_paths([row])
    assert row.photos is photos
    assert row.ma == "s06"
    assert row.price_usd == 25
    assert row.held is False
    assert flags == [PhotoSrcFlag("S06", HTTP_SRC, 1, "http_url")]
    assert flags[0].as_json() == {"ma": "S06", "src": HTTP_SRC, "index": 1, "kind": "http_url"}
    assert "priceUsd" not in flags[0].as_json()
    assert COVER not in {flag.src for flag in flags}


def test_blank_data_and_relative_srcs_are_flagged_without_rewriting() -> None:
    blank = ""
    spaced = "  "
    relative = "products/Z81/cover.jpg"
    photos = (blank, spaced, DATA_SRC, relative, COVER)
    row = CatalogPhotoRow("Z81", photos, 40, False, "available")
    flags = flag_photo_src_paths([row])
    assert row.photos is photos
    assert row.photos[0] == ""
    assert row.photos[1] == "  "
    assert flags == [
        PhotoSrcFlag("Z81", blank, 0, "blank"),
        PhotoSrcFlag("Z81", spaced, 1, "blank"),
        PhotoSrcFlag("Z81", DATA_SRC, 2, "data_url"),
        PhotoSrcFlag("Z81", relative, 3, "not_site_path"),
    ]


def test_src_outside_products_is_flagged_without_rewriting() -> None:
    outside = ("images/a01.jpg", "/etc/passwd")
    photos = (COVER, *outside)
    row = CatalogPhotoRow("S06", photos, 25, False, "available")
    flags = flag_photo_src_paths([row])
    assert row.photos is photos
    assert row.photos[1:] == outside
    assert row.price_usd == 25
    assert flags == [
        PhotoSrcFlag("S06", "images/a01.jpg", 1, "not_site_path"),
        PhotoSrcFlag("S06", "/etc/passwd", 2, "not_site_path"),
    ]
    assert COVER not in {flag.src for flag in flags}


def test_products_src_with_parent_dir_is_flagged_without_rewriting() -> None:
    photos = (COVER, TRAVERSAL)
    row = CatalogPhotoRow("S06", photos, 25, False, "available")
    flags = flag_photo_src_paths([row])
    assert row.photos is photos
    assert row.photos[1] == TRAVERSAL
    assert row.price_usd == 25
    assert flags == [PhotoSrcFlag("S06", TRAVERSAL, 1, "not_site_path")]
    assert COVER not in {flag.src for flag in flags}


def test_full_url_containing_the_cover_path_is_still_a_flag() -> None:
    remote = "https://cdn.example.test/products/S06/cover.jpg"
    photos = (COVER, remote)
    row = CatalogPhotoRow("S06", photos, 25, False, "available")
    flags = flag_photo_src_paths([row])
    assert row.price_usd == 25
    assert row.photos[0] == COVER
    assert flags == [PhotoSrcFlag("S06", remote, 1, "http_url")]


def test_held_row_stays_held_and_held_json_is_unchanged() -> None:
    before = HELD.read_bytes()
    assert before == HELD_BYTES
    photos = ("", "/products/V05/cover.jpg")
    row = CatalogPhotoRow("V05", photos, None, True, "hold")
    flags = flag_photo_src_paths([row])
    assert row.held is True
    assert row.status == "hold"
    assert row.price_usd is None
    assert row.photos is photos
    assert flags == [PhotoSrcFlag("V05", "", 0, "blank")]
    assert b'"V05"' in before
    assert b'"K06"' in before
    assert HELD.read_bytes() == before


def test_src_field_wins_and_gallery_strings_are_read(tmp_path: Path) -> None:
    path = tmp_path / "both.json"
    path.write_text(
        json.dumps(
            {
                "products": [
                    {
                        "ma": "S06",
                        "priceUsd": 25,
                        "status": "available",
                        "images": [
                            {"src": COVER, "url": HTTP_SRC},
                            {"src": "/products/S06/photo-2.jpg"},
                        ],
                        "photos": [HTTP_SRC, HTTP_SRC],
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    rows = load_catalog(path)
    assert rows[0].price_usd == 25
    assert rows[0].photos == (COVER, "/products/S06/photo-2.jpg")
    assert flag_photo_src_paths(rows) == []
    gallery = tmp_path / "gallery.json"
    gallery.write_text(
        json.dumps(
            {
                "products": [
                    {
                        "ma": "B02",
                        "gallery": [COVER, DATA_SRC, ""],
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    gallery_rows = load_catalog(gallery)
    assert flag_photo_src_paths(gallery_rows) == [
        PhotoSrcFlag("B02", DATA_SRC, 1, "data_url"),
        PhotoSrcFlag("B02", "", 2, "blank"),
    ]
    assert gallery_rows[0].photos[0] == COVER


def test_bad_fixture_keeps_s06_at_25_and_the_cover_quiet() -> None:
    raw = BAD.read_text(encoding="utf-8")
    rows = load_catalog(BAD)
    by_ma = {row.ma: row for row in rows}
    assert [row.ma for row in rows] == ["S06", "K06", "A01", "V05", "Z81"]
    assert by_ma["S06"].price_usd == 25
    assert by_ma["S06"].held is False
    assert by_ma["S06"].status == "available"
    assert by_ma["S06"].photos == (COVER, HTTP_SRC, TRAVERSAL)
    assert by_ma["K06"].held is True
    assert by_ma["K06"].status == "hold"
    assert by_ma["K06"].photos == ("/products/K06/cover.jpg",)
    assert by_ma["A01"].photos[1] == "/products/A01/photo-2.jpg"
    assert by_ma["A01"].photos[2:] == ("images/a01.jpg", "/etc/passwd")
    assert by_ma["V05"].held is True
    assert by_ma["V05"].photos == ("", "  ", "")
    flags = flag_photo_src_paths(rows)
    assert [flag.as_json() for flag in flags] == [
        {"ma": "A01", "src": "http://photos.example.test/a01/cover.jpg", "index": 0, "kind": "http_url"},
        {"ma": "A01", "src": "images/a01.jpg", "index": 2, "kind": "not_site_path"},
        {"ma": "A01", "src": "/etc/passwd", "index": 3, "kind": "not_site_path"},
        {"ma": "S06", "src": HTTP_SRC, "index": 1, "kind": "http_url"},
        {"ma": "S06", "src": TRAVERSAL, "index": 2, "kind": "not_site_path"},
        {"ma": "V05", "src": "", "index": 0, "kind": "blank"},
        {"ma": "V05", "src": "  ", "index": 1, "kind": "blank"},
        {"ma": "V05", "src": "", "index": 2, "kind": "blank"},
        {"ma": "Z81", "src": DATA_SRC, "index": 0, "kind": "data_url"},
        {"ma": "Z81", "src": "products/Z81/cover.jpg", "index": 1, "kind": "not_site_path"},
        {"ma": "Z81", "src": "//cdn.example.test/z81.jpg", "index": 2, "kind": "not_site_path"},
    ]
    assert COVER not in {flag.src for flag in flags}
    assert by_ma["S06"].price_usd == 25
    assert BAD.read_text(encoding="utf-8") == raw
    assert HELD.read_bytes() == HELD_BYTES


def test_cli_bad_fixture_exits_1_and_writes_nothing() -> None:
    before = BAD.read_bytes()
    assert before == BAD_BYTES
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "photo_src_paths.py"), "--catalog", str(BAD)],
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
    assert {"ma": "S06", "src": HTTP_SRC, "index": 1, "kind": "http_url"} in report["flags"]
    assert {"ma": "S06", "src": TRAVERSAL, "index": 2, "kind": "not_site_path"} in report["flags"]
    assert {"ma": "A01", "src": "images/a01.jpg", "index": 2, "kind": "not_site_path"} in report["flags"]
    assert {"ma": "A01", "src": "/etc/passwd", "index": 3, "kind": "not_site_path"} in report["flags"]
    assert COVER not in result.stdout
    assert "priceUsd" not in result.stdout
    assert _bare_numbers(result.stdout).isdisjoint({"25"})
    assert BAD.read_bytes() == before == BAD_BYTES
    assert CLEAN.read_bytes() == CLEAN_BYTES
    assert HELD.read_bytes() == HELD_BYTES
    assert PRODUCTS.read_bytes() == PRODUCTS_BYTES


def test_cli_clean_fixture_exits_0() -> None:
    before = CLEAN.read_bytes()
    assert before == CLEAN_BYTES
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "photo_src_paths.py"), "--catalog", str(CLEAN)],
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
    assert loaded[0].photos[0] == COVER
    assert loaded[1].held is True
    assert CLEAN.read_bytes() == before == CLEAN_BYTES
    assert HELD.read_bytes() == HELD_BYTES
    assert PRODUCTS.read_bytes() == PRODUCTS_BYTES


def test_cli_refuses_live_catalog_and_urls() -> None:
    products_before = PRODUCTS.read_bytes()
    held_before = HELD.read_bytes()
    for target in (str(PRODUCTS), str(HELD), "https://example.test/products/S06/cover.jpg"):
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
    assert PRODUCTS.read_bytes() == PRODUCTS_BYTES


def test_script_is_fixture_only() -> None:
    text = (ROOT / "scripts" / "photo_src_paths.py").read_text(encoding="utf-8")
    lowered = text.lower()
    for banned in (
        "urllib",
        "requests",
        "http.client",
        "freshness_check",
        "intake_photo_flags",
        "catalog_photo_count",
        "duplicate_photo_urls",
        "held_policy",
        "open(",
        "write_text",
        "write_bytes",
    ):
        assert banned not in lowered
    assert "products.json" in text
    assert "held.json" in text


def _run_main(argv: list[str]) -> tuple[int, str]:
    err = io.StringIO()
    with redirect_stderr(err):
        code = main(argv)
    return code, err.getvalue()
