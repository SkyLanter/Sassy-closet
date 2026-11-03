"""Photo-path extension flags from fixtures. Paths, prices, and held.json stay put."""

from __future__ import annotations
import re

import io
import json
import subprocess
import sys
from contextlib import redirect_stderr
from pathlib import Path

from photo_path_ext import (
    CatalogPhotoRow,
    PhotoExtFlag,
    flag_photo_extensions,
    image_extension,
    load_catalog,
    main,
)

ROOT = Path(__file__).resolve().parents[2]
HELD = ROOT / "data" / "held.json"
PRODUCTS = ROOT / "sassy-closet-shop" / "data" / "products.json"
FIXTURES = Path(__file__).resolve().parent / "fixtures"
CLEAN = FIXTURES / "photo_path_ext_ok.json"
BAD = FIXTURES / "photo_path_ext_bad.json"
HELD_BYTES = HELD.read_bytes()
PRODUCTS_BYTES = PRODUCTS.read_bytes()
CLEAN_BYTES = CLEAN.read_bytes()
BAD_BYTES = BAD.read_bytes()
COVER = "/products/S06/cover.jpg"
JPEG = "/products/S06/photo-2.jpeg"
PNG = "/products/S06/photo-3.png"
WEBP = "/products/S06/photo-4.webp"
BARE = "/products/A01/cover"
KIND = "no_image_extension"


def _bare_numbers(text: str) -> set[str]:
    """Standalone numbers in output, ignoring anything inside a path-like token (temp dirs carry digits)."""
    words = [w for w in text.split() if "/" not in w and "\\" not in w]
    return set(re.findall(r"(?<![\w.])\d+(?:\.\d+)?(?![\w.])", " ".join(words)))


def test_image_extensions_stay_quiet_and_a_bare_path_is_flagged() -> None:
    assert image_extension(COVER) == ".jpg"
    assert image_extension(JPEG) == ".jpeg"
    assert image_extension(PNG) == ".png"
    assert image_extension(WEBP) == ".webp"
    assert image_extension("/products/S06/cover.JPG") == ".jpg"
    assert image_extension("/products/S06/photo-2.JPEG") == ".jpeg"
    assert image_extension("/products/S06/photo-3.PNG") == ".png"
    assert image_extension("/products/S06/photo-4.WEBP") == ".webp"
    assert image_extension(BARE) is None
    assert image_extension("/products/A01/cover.") is None
    assert image_extension("/products/Z81/cover.gif") is None
    assert image_extension("/products/Z81/note.txt") is None
    assert image_extension("/products/Z81/scan.heic") is None
    assert image_extension("") is None
    assert image_extension("   ") is None
    assert image_extension(COVER + " ") is None
    assert image_extension(COVER + "/") is None
    assert image_extension("photo.jpeg") == ".jpeg"
    assert image_extension("photo.jpg") == ".jpg"
    assert image_extension("/products/jpg") is None


def test_s06_price_stays_25_and_its_photos_stay_quiet() -> None:
    photos = (COVER, JPEG, PNG, WEBP)
    row = CatalogPhotoRow("s06", photos, 25, False, "available")
    flags = flag_photo_extensions([row])
    assert flags == []
    assert row.photos is photos
    assert row.ma == "s06"
    assert row.price_usd == 25
    assert row.held is False
    assert row.status == "available"


def test_bare_path_is_flagged_and_the_jpg_beside_it_stays() -> None:
    photos = (BARE, "/products/A01/photo-2.jpg")
    row = CatalogPhotoRow("a01", photos, 27, False, "available")
    flags = flag_photo_extensions([row])
    assert row.photos is photos
    assert row.price_usd == 27
    assert flags == [PhotoExtFlag("A01", BARE, 0, KIND)]
    assert flags[0].as_json() == {"ma": "A01", "path": BARE, "index": 0, "kind": KIND}
    assert "priceUsd" not in flags[0].as_json()
    assert flags[0].path == "/products/A01/cover"


def test_other_suffixes_are_flagged_without_rewriting() -> None:
    gif = "/products/Z81/cover.gif"
    text = "/products/Z81/note.txt"
    heic = "/products/Z81/scan.heic"
    photos = (gif, text, heic, WEBP)
    row = CatalogPhotoRow("Z81", photos, 40, False, "available")
    flags = flag_photo_extensions([row])
    assert row.photos is photos
    assert flags == [
        PhotoExtFlag("Z81", gif, 0, KIND),
        PhotoExtFlag("Z81", text, 1, KIND),
        PhotoExtFlag("Z81", heic, 2, KIND),
    ]


def test_query_and_fragment_follow_the_path_extension() -> None:
    queried = COVER + "?v=2"
    fragment = PNG + "#top"
    hidden = "/products/S06/cover?v=2.jpg"
    photos = (queried, fragment, hidden, JPEG)
    row = CatalogPhotoRow("S06", photos, 25, False, "available")
    flags = flag_photo_extensions([row])
    assert row.price_usd == 25
    assert row.photos[0] == queried
    assert flags == [PhotoExtFlag("S06", hidden, 2, KIND)]
    assert image_extension(queried) == ".jpg"
    assert image_extension(fragment) == ".png"
    assert image_extension(WEBP + "#x") == ".webp"


def test_held_row_stays_held_and_held_json_is_unchanged() -> None:
    before = HELD.read_bytes()
    assert before == HELD_BYTES
    photos = ("/products/V05/look", "/products/V05/detail.JPG")
    row = CatalogPhotoRow("V05", photos, None, True, "hold")
    flags = flag_photo_extensions([row])
    assert row.held is True
    assert row.status == "hold"
    assert row.price_usd is None
    assert row.photos is photos
    assert flags == [PhotoExtFlag("V05", "/products/V05/look", 0, KIND)]
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
                            {"src": COVER, "url": BARE},
                            {"src": JPEG},
                            {"path": PNG},
                            {"src": None},
                        ],
                        "photos": [BARE, BARE],
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    rows = load_catalog(path)
    assert rows[0].price_usd == 25
    assert rows[0].photos == (COVER, JPEG, PNG, "")
    assert flag_photo_extensions(rows) == [PhotoExtFlag("S06", "", 3, KIND)]
    gallery = tmp_path / "gallery.json"
    gallery.write_text(
        json.dumps({"products": [{"ma": "B02", "gallery": [COVER, BARE, WEBP]}]}),
        encoding="utf-8",
    )
    gallery_rows = load_catalog(gallery)
    assert flag_photo_extensions(gallery_rows) == [PhotoExtFlag("B02", BARE, 1, KIND)]
    assert gallery_rows[0].photos[0] == COVER
    assert gallery_rows[0].photos[2] == WEBP


def test_bad_fixture_keeps_s06_at_25_and_the_four_extensions_quiet() -> None:
    raw = BAD.read_text(encoding="utf-8")
    rows = load_catalog(BAD)
    by_ma = {row.ma: row for row in rows}
    assert [row.ma for row in rows] == ["S06", "K06", "A01", "V05", "Z81"]
    assert by_ma["S06"].price_usd == 25
    assert by_ma["S06"].held is False
    assert by_ma["S06"].status == "available"
    assert by_ma["S06"].photos == (COVER, JPEG, PNG, WEBP)
    assert by_ma["K06"].held is True
    assert by_ma["K06"].status == "hold"
    assert by_ma["K06"].photos == ("/products/K06/cover.webp",)
    assert by_ma["V05"].held is True
    assert by_ma["A01"].photos[0] == BARE
    assert by_ma["A01"].photos[1] == "/products/A01/photo-2.jpg"
    flags = flag_photo_extensions(rows)
    assert [flag.as_json() for flag in flags] == [
        {"ma": "A01", "path": BARE, "index": 0, "kind": KIND},
        {"ma": "V05", "path": "/products/V05/look", "index": 0, "kind": KIND},
        {"ma": "Z81", "path": "/products/Z81/cover.gif", "index": 0, "kind": KIND},
        {"ma": "Z81", "path": "/products/Z81/note.txt", "index": 1, "kind": KIND},
        {"ma": "Z81", "path": "/products/Z81/scan.heic", "index": 2, "kind": KIND},
    ]
    quiet = {
        COVER,
        JPEG,
        PNG,
        WEBP,
        "/products/K06/cover.webp",
        "/products/A01/photo-2.jpg",
        "/products/V05/detail.JPG",
    }
    assert quiet.isdisjoint({flag.path for flag in flags})
    assert by_ma["S06"].price_usd == 25
    assert by_ma["S06"].photos[0] == COVER
    assert BAD.read_text(encoding="utf-8") == raw
    assert HELD.read_bytes() == HELD_BYTES
    assert PRODUCTS.read_bytes() == PRODUCTS_BYTES


def test_cli_bad_fixture_exits_1_and_writes_nothing() -> None:
    before = BAD.read_bytes()
    assert before == BAD_BYTES
    names_before = sorted(path.name for path in FIXTURES.iterdir())
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "photo_path_ext.py"), "--catalog", str(BAD)],
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
    assert report["flags"][0] == {"ma": "A01", "path": BARE, "index": 0, "kind": KIND}
    assert COVER not in {flag["path"] for flag in report["flags"]}
    assert JPEG not in {flag["path"] for flag in report["flags"]}
    assert PNG not in {flag["path"] for flag in report["flags"]}
    assert WEBP not in {flag["path"] for flag in report["flags"]}
    assert "priceUsd" not in result.stdout
    assert _bare_numbers(result.stdout).isdisjoint({"25"})
    assert BAD.read_bytes() == before == BAD_BYTES
    assert CLEAN.read_bytes() == CLEAN_BYTES
    assert HELD.read_bytes() == HELD_BYTES
    assert PRODUCTS.read_bytes() == PRODUCTS_BYTES
    assert sorted(path.name for path in FIXTURES.iterdir()) == names_before
    assert BARE in before.decode("utf-8")


def test_cli_clean_fixture_exits_0() -> None:
    before = CLEAN.read_bytes()
    assert before == CLEAN_BYTES
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "photo_path_ext.py"), "--catalog", str(CLEAN)],
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
    assert loaded[0].photos == (COVER, JPEG, PNG, WEBP)
    assert loaded[1].held is True
    assert loaded[1].photos == ("/products/K06/cover.webp",)
    assert loaded[2].photos[0].endswith(".JPG")
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
    bad.write_text(
        json.dumps({"products": [{"ma": "A01", "images": {"src": COVER}}]}),
        encoding="utf-8",
    )
    code, err = _run_main(["--catalog", str(bad)])
    assert code == 2
    assert "list" in err
    assert HELD.read_bytes() == HELD_BYTES
    assert PRODUCTS.read_bytes() == PRODUCTS_BYTES


def test_empty_photo_list_stays_quiet(tmp_path: Path) -> None:
    path = tmp_path / "empty.json"
    path.write_text(
        json.dumps({"products": [{"ma": "S06", "priceUsd": 25, "status": "available"}]}),
        encoding="utf-8",
    )
    rows = load_catalog(path)
    assert rows[0].price_usd == 25
    assert rows[0].photos == ()
    assert flag_photo_extensions(rows) == []


def test_non_integer_price_is_left_alone(tmp_path: Path) -> None:
    path = tmp_path / "price.json"
    path.write_text(
        json.dumps({"products": [{"ma": "S06", "priceUsd": True, "images": [COVER]}]}),
        encoding="utf-8",
    )
    before = path.read_bytes()
    rows = load_catalog(path)
    assert rows[0].price_usd is None
    assert rows[0].photos == (COVER,)
    assert flag_photo_extensions(rows) == []
    assert path.read_bytes() == before


def test_script_does_not_rename_or_write() -> None:
    text = (ROOT / "scripts" / "photo_path_ext.py").read_text(encoding="utf-8")
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
        "photo_path_ma",
        "photo_src_paths",
        "open(",
        "write_text",
        "write_bytes",
        "os.rename",
        ".rename(",
        "shutil",
        "unlink",
    ):
        assert banned not in lowered
    assert "products.json" in text
    assert "held.json" in text


def _run_main(argv: list[str]) -> tuple[int, str]:
    err = io.StringIO()
    with redirect_stderr(err):
        code = main(argv)
    return code, err.getvalue()
