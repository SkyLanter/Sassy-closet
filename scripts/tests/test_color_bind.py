"""Fixture-only photo colorId binds. No live catalog and no row writes."""

from __future__ import annotations

import json
import math
import re
import subprocess
import sys
from pathlib import Path

from color_bind import (
    _KNOWN_SEED_FOLDERS,
    CatalogRow,
    FixtureColor,
    FixtureImage,
    flag_color_binds,
    main,
    report_json,
    rows_from_payload,
)
from held_policy import load_held_policy

ROOT = Path(__file__).resolve().parents[2]
FIXTURE = Path(__file__).resolve().parent / "fixtures" / "color_bind.json"
HELD = ROOT / "data" / "held.json"
CATALOG = ROOT / "sassy-closet-shop" / "data" / "products.json"
EXTRAS = ROOT / "sassy-closet-shop" / "data" / "intake-extras.json"
SCRIPT = ROOT / "scripts" / "color_bind.py"

EXPECTED = [
    ("S06", "blank_color_id", 3, "", ()),
    ("S06", "duplicate_color_id", 4, "cs0600", ()),
    ("S06", "padded_bind", 1, " cs0601", ()),
    ("S06", "blank_bind", 2, "   ", ()),
    ("S06", "orphan_bind", 3, "no-such", ()),
    ("S06", "orphan_bind", 5, "cz8100", ("Z81",)),
    ("S06", "color_without_slide", 1, "cs0601", ()),
    ("S06", "color_without_slide", 2, " cs0602", ()),
    ("Z81", "color_without_slide", 1, "cz8101", ()),
    ("V05", "orphan_bind", 0, "den", ()),
    ("H01", "padded_bind", 1, "blue ", ()),
    ("H01", "color_without_slide", 1, "blue", ()),
    ("H01", "color_without_slide", 2, "wine", ()),
]

KEPT_OUT = (
    "Ink",
    "Slate",
    "Mist",
    "Blank",
    "Stone",
    "Clay",
    "Den",
    "Pearl",
    "Pink",
    "Blue",
    "Wine",
    "Yellow",
    "Kem",
    "Xanh",
    "#111111",
    "#222222",
    "#333333",
    "#444444",
    "#555555",
    "#666666",
    "#777777",
    "#888888",
    "#999999",
    "#AAAAAA",
    "#BBBBBB",
    "#CCCCCC",
    "#DDDDDD",
)


def _view(flags: list) -> list[tuple[str, str, int, str, tuple[str, ...]]]:
    return [(flag.ma, flag.kind, flag.index, flag.stored, flag.also_on) for flag in flags]


def _snapshot(rows: list[CatalogRow]) -> list[tuple[object, ...]]:
    return [
        (
            row.ma,
            row.price_usd,
            row.price_set,
            row.status,
            tuple(color.id for color in row.colors),
            tuple((image.src, image.color_id) for image in row.images),
        )
        for row in rows
    ]


def test_fixture_flags_broken_binds_and_leaves_rows() -> None:
    original = FIXTURE.read_text(encoding="utf-8")
    payload = json.loads(original)
    rows = rows_from_payload(payload)
    before = _snapshot(rows)
    flags = flag_color_binds(rows)
    assert _snapshot(rows) == before
    assert FIXTURE.read_text(encoding="utf-8") == original
    assert _view(flags) == EXPECTED
    text = json.dumps(report_json(rows, flags), ensure_ascii=False)
    for word in KEPT_OUT:
        assert word not in text
    by_ma = {row["ma"]: row for row in report_json(rows, flags)["rows"]}
    assert by_ma["S06"]["priceUsd"] == 25
    assert type(by_ma["S06"]["priceUsd"]) is int
    assert by_ma["S06"]["status"] == "available"
    assert by_ma["Z81"]["priceUsd"] is None
    assert by_ma["Z81"]["status"] == "hold"
    assert "priceUsd" not in by_ma["K06"]
    assert by_ma["K06"]["status"] == "hold"
    assert by_ma["V05"]["priceUsd"] == "40"
    assert type(by_ma["V05"]["priceUsd"]) is str
    assert by_ma["V05"]["status"] == "hold"
    assert by_ma["A01"]["priceUsd"] == 27
    assert by_ma["H01"]["colorIds"][2]["id"] == "wine"
    assert by_ma["H01"]["imageBinds"][1]["colorId"] == "blue "
    assert by_ma["K06"]["imageBinds"][0]["colorId"] is None
    assert by_ma["V05"]["colorIds"] == [{"index": 0, "id": None}]


def test_exact_bind_and_untagged_gallery_stay_quiet() -> None:
    rows = rows_from_payload(
        [
            {
                "ma": " k3 ",
                "priceUsd": 30,
                "status": "available",
                "colors": [{"id": " blue ", "name": "Blue"}],
                "images": [{"src": "/products/K03/cover.jpg", "colorId": " blue "}],
            },
            {
                "ma": "A01",
                "status": "available",
                "colors": [{"id": "ca0100"}, {"id": "ca0101"}],
                "images": ["/products/A01/cover.jpg", {"src": "/products/A01/photo-2.jpg", "colorId": None}],
            },
            {
                "ma": "S06",
                "priceUsd": 25,
                "status": "hold",
                "colors": [{"id": "cs0600"}, {"id": "cs0601"}],
                "images": [],
            },
        ]
    )
    before = _snapshot(rows)
    flags = flag_color_binds(rows)
    assert _snapshot(rows) == before
    assert flags == []
    assert rows[0].ma == " k3 "
    assert rows[0].price_usd == 30
    assert rows[2].price_usd == 25
    assert rows[2].status == "hold"
    report = report_json(rows, flags)
    assert report["rows"][0]["ma"] == "K03"
    assert report["rows"][2]["priceUsd"] == 25
    assert "Blue" not in json.dumps(report)


def test_case_mismatch_is_an_orphan_and_does_not_rewrite_the_id() -> None:
    payload = {
        "products": [
            {
                "ma": "H01",
                "priceUsd": 40,
                "status": "available",
                "colors": [{"id": "pink", "name": "Pink"}, {"id": "chip-b", "name": "Also"}],
                "images": [{"src": "/products/H01/cover.jpg", "colorId": "PINK"}],
            }
        ]
    }
    original = json.dumps(payload)
    rows = rows_from_payload(payload)
    flags = flag_color_binds(rows)
    assert json.dumps(payload) == original
    assert _view(flags) == [("H01", "orphan_bind", 0, "PINK", ())]
    assert rows[0].colors[0].id == "pink"
    assert rows[0].images[0].color_id == "PINK"
    text = json.dumps(report_json(rows, flags), ensure_ascii=False)
    assert "Pink" not in text
    assert "Also" not in text


def test_padded_foreign_id_names_the_other_ma() -> None:
    rows = rows_from_payload(
        [
            {
                "ma": "S06",
                "priceUsd": 25,
                "status": "available",
                "colors": [{"id": "cs0600"}],
                "images": [{"src": "/products/S06/cover.jpg", "colorId": " cz8100"}],
            },
            {
                "ma": " z81 ",
                "status": "hold",
                "colors": [{"id": "cz8100"}],
                "images": [{"src": "/products/Z81/cover.jpg", "colorId": "cz8100"}],
            },
        ]
    )
    flags = flag_color_binds(rows)
    assert _view(flags) == [("S06", "orphan_bind", 0, " cz8100", ("Z81",))]
    assert rows[0].price_usd == 25
    assert rows[1].ma == " z81 "
    assert rows[1].status == "hold"


def test_nonfinite_price_is_refused_and_not_rewritten() -> None:
    payload = [{"ma": "A01", "priceUsd": float("nan"), "colors": []}]
    try:
        rows_from_payload(payload)
    except ValueError as error:
        assert "finite" in str(error)
    else:
        raise AssertionError("a non-finite price was accepted")
    assert isinstance(payload[0]["priceUsd"], float)
    assert math.isnan(payload[0]["priceUsd"])


def test_seed_folders_match_the_shop_contract() -> None:
    text = (ROOT / "sassy-closet-shop" / "lib" / "catalog-contract.ts").read_text(encoding="utf-8")
    block = text.split("KNOWN_SEED_MAS = [", 1)[1].split("]", 1)[0]
    found = tuple(re.findall(r'"([A-Z][0-9]{2})"', block))
    assert found == _KNOWN_SEED_FOLDERS


def test_another_hub_folder_does_not_count_as_a_slide() -> None:
    rows = rows_from_payload(
        [
            {
                "ma": "A02",
                "priceUsd": 36,
                "status": "available",
                "colors": [{"id": "kem"}, {"id": "xanh"}],
                "images": [
                    {"src": "/products/A01/cover.jpg", "colorId": "kem"},
                    {"src": "/products/A02/cover.jpg", "colorId": "xanh"},
                ],
            },
            {
                "ma": "S06",
                "priceUsd": 25,
                "status": "available",
                "colors": [{"id": "cs0600"}, {"id": "cs0601"}],
                "images": [
                    {"src": " /products/H01/photo.jpg?v=2", "colorId": "cs0600"},
                    {"src": "/products/S06/cover.jpg", "colorId": "cs0601"},
                ],
            },
        ]
    )
    before = _snapshot(rows)
    flags = flag_color_binds(rows)
    assert _snapshot(rows) == before
    assert _view(flags) == [
        ("A02", "color_without_slide", 0, "kem", ()),
        ("S06", "color_without_slide", 0, "cs0600", ()),
    ]
    assert rows[1].price_usd == 25
    assert type(rows[1].price_usd) is int


def test_only_a_foreign_hub_photo_does_not_invent_a_covered_color() -> None:
    rows = rows_from_payload(
        [
            {
                "ma": "A02",
                "status": "available",
                "colors": [{"id": "cham-bi"}, {"id": "kem"}],
                "images": [{"src": "/products/A01/cover.jpg", "colorId": "cham-bi"}],
            }
        ]
    )
    assert flag_color_binds(rows) == []
    assert rows[0].images[0].color_id == "cham-bi"
    assert rows[0].images[0].src == "/products/A01/cover.jpg"


def test_foreign_file_with_a_bad_id_is_not_an_orphan() -> None:
    rows = rows_from_payload(
        [
            {
                "ma": "A02",
                "status": "hold",
                "colors": [{"id": "kem"}],
                "images": [{"src": "/products/H01/cover.jpg", "colorId": "missing"}],
            }
        ]
    )
    assert flag_color_binds(rows) == []
    assert rows[0].status == "hold"


def test_uploads_and_extra_folders_still_count() -> None:
    rows = rows_from_payload(
        [
            {
                "ma": "A02",
                "status": "available",
                "colors": [{"id": "kem"}, {"id": "xanh"}],
                "images": [
                    {"src": "/uploads/A02/cover.jpg", "colorId": "kem"},
                    {"src": "/products/Z81/cover.jpg", "colorId": "xanh"},
                ],
            }
        ]
    )
    assert flag_color_binds(rows) == []


def test_blank_src_does_not_count_as_a_slide() -> None:
    rows = [
        CatalogRow(
            "Z81",
            (FixtureColor("cz8100"), FixtureColor("cz8101")),
            (FixtureImage("  ", "cz8100"), FixtureImage("/products/Z81/photo-2.jpg", "cz8101")),
            None,
            True,
            "hold",
        )
    ]
    flags = flag_color_binds(rows)
    assert _view(flags) == [("Z81", "color_without_slide", 0, "cz8100", ())]
    assert rows[0].status == "hold"
    assert rows[0].images[0].src == "  "
    assert rows[0].images[0].color_id == "cz8100"


def test_bad_shapes_are_refused() -> None:
    samples = [
        [{"ma": "A01", "colors": {"id": "ca0100"}}],
        [{"ma": "A01", "colors": [{"id": 1}]}],
        [{"ma": "A01", "images": {"src": "/products/A01/cover.jpg"}}],
        [{"ma": "A01", "images": [{"src": 1, "colorId": None}]}],
        [{"ma": "A01", "images": [{"src": "/products/A01/cover.jpg", "colorId": 1}]}],
        [{"ma": "A01", "priceUsd": True, "colors": []}],
        [{"ma": " ", "colors": []}],
        [{"ma": "A01", "status": 1, "colors": []}],
        {"products": "nope"},
        {"nope": []},
    ]
    for payload in samples:
        try:
            rows_from_payload(payload)
        except ValueError:
            continue
        raise AssertionError(payload)


def test_held_file_and_price_files_stay_put() -> None:
    held_before = HELD.read_bytes()
    catalog_before = CATALOG.read_bytes()
    extras_before = EXTRAS.read_bytes()
    policy = load_held_policy()
    rows = [
        CatalogRow("K06", (FixtureColor("ck0600"),), (FixtureImage("/products/K06/cover.jpg", "missing"),), None, True, "hold"),
        CatalogRow("V05", (FixtureColor(None),), (), None, False, "hold"),
        CatalogRow("S06", (FixtureColor("cs0600"),), (FixtureImage("/products/S06/cover.jpg", "cs0600"),), 25, True, "available"),
    ]
    flags = flag_color_binds(rows)
    assert _view(flags) == [("K06", "orphan_bind", 0, "missing", ())]
    assert rows[2].price_usd == 25
    assert type(rows[2].price_usd) is int
    assert rows[0].status == "hold"
    assert rows[1].status == "hold"
    assert "K06" in policy.held
    assert "V05" in policy.held
    assert "S06" not in policy.held
    assert HELD.read_bytes() == held_before
    assert CATALOG.read_bytes() == catalog_before
    assert EXTRAS.read_bytes() == extras_before


def test_cli_prints_flags_and_leaves_files(tmp_path: Path) -> None:
    held_before = HELD.read_bytes()
    catalog_before = CATALOG.read_bytes()
    extras_before = EXTRAS.read_bytes()
    fixture_before = FIXTURE.read_bytes()
    ran = subprocess.run(
        [sys.executable, str(SCRIPT), "--fixture", str(FIXTURE)],
        cwd=tmp_path,
        text=True,
        capture_output=True,
        check=False,
    )
    assert ran.returncode == 0, ran.stderr
    assert ran.stderr == ""
    report = json.loads(ran.stdout)
    assert report["readOnly"] is True
    assert report["s06"] == "stays $25"
    assert report["held"] == "stay held"
    assert report["flagCount"] == len(EXPECTED)
    assert [
        (flag["ma"], flag["kind"], flag["index"], flag["stored"], tuple(flag["alsoOn"]))
        for flag in report["flags"]
    ] == EXPECTED
    assert report["rows"][0]["priceUsd"] == 25
    assert report["rows"][1]["status"] == "hold"
    assert report["rows"][2]["status"] == "hold"
    assert report["rows"][3]["status"] == "hold"
    for word in KEPT_OUT:
        assert word not in ran.stdout
    assert list(tmp_path.iterdir()) == []
    assert FIXTURE.read_bytes() == fixture_before
    assert HELD.read_bytes() == held_before
    assert CATALOG.read_bytes() == catalog_before
    assert EXTRAS.read_bytes() == extras_before
    policy = load_held_policy()
    assert "K06" in policy.held
    assert "V05" in policy.held


def test_cli_clean_fixture_prints_no_flags(tmp_path: Path) -> None:
    payload = {
        "products": [
            {
                "ma": "S06",
                "priceUsd": 25,
                "status": "available",
                "colors": [{"id": "cs0600", "name": "Xanh", "hex": "#1C2A4A"}],
                "images": [{"src": "/products/S06/cover.jpg", "colorId": "cs0600"}],
            }
        ]
    }
    raw = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    fixture = tmp_path / "clean.json"
    fixture.write_text(raw, encoding="utf-8")
    ran = subprocess.run(
        [sys.executable, str(SCRIPT), "--fixture", str(fixture)],
        cwd=tmp_path,
        text=True,
        capture_output=True,
        check=False,
    )
    assert ran.returncode == 0, ran.stderr
    report = json.loads(ran.stdout)
    assert report["flagCount"] == 0
    assert report["flags"] == []
    assert report["rows"][0]["priceUsd"] == 25
    assert report["rows"][0]["colorIds"] == [{"index": 0, "id": "cs0600"}]
    assert "Xanh" not in ran.stdout
    assert "#1C2A4A" not in ran.stdout
    assert fixture.read_text(encoding="utf-8") == raw


def test_cli_refuses_held_json_shop_catalog_and_bad_files(tmp_path: Path) -> None:
    held_before = HELD.read_bytes()
    catalog_before = CATALOG.read_bytes()
    extras_before = EXTRAS.read_bytes()
    refused = subprocess.run(
        [sys.executable, str(SCRIPT), "--fixture", str(HELD)],
        cwd=tmp_path,
        text=True,
        capture_output=True,
        check=False,
    )
    assert refused.returncode == 2
    assert refused.stdout == ""
    assert "held.json" in refused.stderr
    catalog = subprocess.run(
        [sys.executable, str(SCRIPT), "--fixture", str(CATALOG)],
        cwd=tmp_path,
        text=True,
        capture_output=True,
        check=False,
    )
    assert catalog.returncode == 2
    assert catalog.stdout == ""
    assert "shop catalog" in catalog.stderr
    url = subprocess.run(
        [sys.executable, str(SCRIPT), "--fixture", "https://example.invalid/catalog.json"],
        cwd=tmp_path,
        text=True,
        capture_output=True,
        check=False,
    )
    assert url.returncode == 2
    assert url.stdout == ""
    assert "live catalog URL" in url.stderr
    assert main(["--fixture", " http://example.invalid/catalog.json "]) == 2
    assert main(["--fixture", str(tmp_path / "missing.json")]) == 2
    broken = tmp_path / "broken.json"
    broken.write_text("{", encoding="utf-8")
    assert main(["--fixture", str(broken)]) == 2
    assert broken.read_text(encoding="utf-8") == "{"
    bad = tmp_path / "bad.json"
    bad_raw = '{"products":[{"ma":"S06","priceUsd":25,"colors":{"id":"cs0600"}}]}\n'
    bad.write_text(bad_raw, encoding="utf-8")
    bad_run = subprocess.run(
        [sys.executable, str(SCRIPT), "--fixture", str(bad)],
        cwd=tmp_path,
        text=True,
        capture_output=True,
        check=False,
    )
    assert bad_run.returncode == 2
    assert bad_run.stdout == ""
    assert bad.read_text(encoding="utf-8") == bad_raw
    try:
        main([])
    except SystemExit as error:
        assert error.code == 2
    else:
        raise AssertionError("a missing fixture argument was accepted")
    assert HELD.read_bytes() == held_before
    assert CATALOG.read_bytes() == catalog_before
    assert EXTRAS.read_bytes() == extras_before
    assert {path.name for path in tmp_path.iterdir()} == {"broken.json", "bad.json"}


def test_script_is_read_only_and_does_not_rewrite_a_bind() -> None:
    text = SCRIPT.read_text(encoding="utf-8")
    assert ".write_text(" not in text
    assert ".write_bytes(" not in text
    assert "open(" not in text
    assert "urlopen" not in text
    assert "requests" not in text
    assert "load_held_policy" not in text
    assert "vercel" not in text.casefold()
    assert '["priceUsd"] = 25' not in text
    assert "price_usd = 25" not in text
    assert "suggestedColorName" not in text
    assert "COLOR_PRESETS" not in text
