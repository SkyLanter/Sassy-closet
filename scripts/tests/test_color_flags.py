"""Blank-color flags from fixtures. Stored colors and prices stay as they were."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from color_flags import CatalogColor, CatalogPiece, CatalogRow, flag_blank_colors, rows_from_payload
from held_policy import load_held_policy

ROOT = Path(__file__).resolve().parents[2]
HELD_PATH = ROOT / "data" / "held.json"
PRODUCTS_PATH = ROOT / "sassy-closet-shop" / "data" / "products.json"


def test_blank_colors_are_flagged_and_not_rewritten() -> None:
    rows = [
        CatalogRow("S01", ()),
        CatalogRow("A07", None),
        CatalogRow("H01", (CatalogColor("  "),)),
        CatalogRow("O04", (CatalogColor(None), CatalogColor("Đen"))),
        CatalogRow("A01", (CatalogColor("Yellow", "ca0100"), CatalogColor("Purple", "ca0101"))),
        CatalogRow("s06", (), price_usd=25, status="available"),
        CatalogRow("V05", (CatalogColor("", "den"),), price_usd=None, status="hold"),
        CatalogRow(
            "K06",
            (CatalogColor("Đen"),),
            pieces=(CatalogPiece("p1", ""), CatalogPiece("p2", "Hồng")),
            status="hold",
        ),
    ]
    flags = flag_blank_colors(rows)
    assert [(flag.ma, flag.kind, flag.stored, flag.index, flag.piece) for flag in flags] == [
        ("S01", "blank_color", "", None, None),
        ("A07", "blank_color", "", None, None),
        ("H01", "blank_color", "  ", 0, None),
        ("O04", "blank_color", "", 0, None),
        ("S06", "blank_color", "", None, None),
        ("V05", "blank_color", "", 0, None),
        ("K06", "blank_color", "", 0, "p1"),
    ]
    assert rows[0].colors == ()
    assert rows[1].colors is None
    assert rows[3].colors is not None
    assert rows[3].colors[1].name == "Đen"
    assert rows[4].colors is not None
    assert rows[4].colors[0].name == "Yellow"
    assert rows[5].ma == "s06"
    assert rows[5].price_usd == 25
    assert rows[5].status == "available"
    assert rows[6].status == "hold"
    assert rows[6].price_usd is None
    assert rows[6].colors is not None
    assert rows[6].colors[0].name == ""
    assert rows[6].colors[0].color_id == "den"
    assert rows[7].status == "hold"
    assert rows[7].pieces[0].color == ""
    assert rows[7].pieces[1].color == "Hồng"
    dumped = json.dumps([flag.as_json() for flag in flags], ensure_ascii=False)
    assert "suggested" not in dumped
    assert "corrected" not in dumped
    assert "Yellow" not in dumped
    assert "Đen" not in dumped
    assert "#111111" not in dumped


def test_fixture_json_keeps_s06_price_and_does_not_invent_a_color() -> None:
    payload = {
        "schema": "catalog.v1",
        "products": [
            {
                "ma": "S06",
                "priceUsd": 25,
                "status": "available",
                "colors": [],
                "color": "Kem",
            },
            {
                "ma": "A08",
                "priceUsd": 32,
                "status": "available",
                "colors": [{"id": "ca0800", "hex": "#F4F0E8", "name": "Off-white", "note": ""}],
            },
            {
                "ma": "D03",
                "priceUsd": 34,
                "status": "available",
                "colors": [{"id": "den", "hex": "#111111", "name": ""}],
                "pieces": [
                    {"id": "p1", "photos": [], "suggested": ["Đỏ"], "color": "", "note": ""},
                    {"id": "p2", "photos": [], "suggested": [], "color": "Kem", "note": ""},
                ],
            },
            {
                "ma": "H01",
                "price_usd": "12",
                "color": "  ",
            },
            {
                "ma": "P04",
                "priceUsd": 8,
                "colors": [],
                "pieces": [{"id": "p1", "color": "Kem", "suggested": ["Xanh"]}],
            },
        ],
    }
    original = json.dumps(payload, ensure_ascii=False)
    rows = rows_from_payload(payload)
    flags = flag_blank_colors(rows)
    assert json.dumps(payload, ensure_ascii=False) == original
    assert rows[0].price_usd == 25
    assert type(rows[0].price_usd) is int
    assert rows[0].status == "available"
    assert rows[0].colors == ()
    assert rows[3].price_usd == "12"
    assert [(flag.ma, flag.stored, flag.index, flag.piece) for flag in flags] == [
        ("S06", "", None, None),
        ("D03", "", 0, None),
        ("D03", "", 0, "p1"),
        ("H01", "  ", 0, None),
        ("P04", "", None, None),
    ]
    text = json.dumps([flag.as_json() for flag in flags], ensure_ascii=False)
    assert "Kem" not in text
    assert "Xanh" not in text
    assert "Đỏ" not in text
    assert "Off-white" not in text
    assert "#F4F0E8" not in text
    assert "#111111" not in text
    assert "Color 1" not in text
    assert payload["products"][0]["priceUsd"] == 25
    assert payload["products"][0]["colors"] == []
    assert payload["products"][0]["color"] == "Kem"
    assert payload["products"][2]["pieces"][0]["color"] == ""
    assert payload["products"][2]["pieces"][0]["suggested"] == ["Đỏ"]
    assert payload["products"][4]["colors"] == []
    assert payload["products"][4]["pieces"][0]["color"] == "Kem"


def test_held_file_and_catalog_file_stay_put() -> None:
    held_before = HELD_PATH.read_bytes()
    products_before = PRODUCTS_PATH.read_bytes()
    policy = load_held_policy()
    rows = [
        CatalogRow("K06", (), status="hold"),
        CatalogRow("V05", (CatalogColor(" "),), status="hold"),
        CatalogRow("S06", (CatalogColor("Đen"),), price_usd=25, status="available"),
    ]
    flags = flag_blank_colors(rows)
    assert [flag.ma for flag in flags] == ["K06", "V05"]
    assert rows[0].status == "hold"
    assert rows[1].status == "hold"
    assert rows[2].price_usd == 25
    assert rows[2].colors is not None
    assert rows[2].colors[0].name == "Đen"
    assert "K06" in policy.held
    assert "V05" in policy.held
    assert "S06" not in policy.held
    assert HELD_PATH.read_bytes() == held_before
    assert PRODUCTS_PATH.read_bytes() == products_before


def test_bad_color_shape_is_refused() -> None:
    try:
        rows_from_payload([{"ma": "A01", "colors": {"name": "Kem"}}])
    except ValueError:
        return
    raise AssertionError("a color object in place of the list was accepted")


def test_cli_prints_flags_and_leaves_files(tmp_path: Path) -> None:
    held_before = HELD_PATH.read_bytes()
    products_before = PRODUCTS_PATH.read_bytes()
    payload = {
        "schema": "catalog.v1",
        "products": [
            {"ma": "S06", "priceUsd": 25, "status": "available", "colors": []},
            {
                "ma": "V05",
                "priceUsd": None,
                "status": "hold",
                "colors": [{"id": "den", "hex": "#111111", "name": ""}],
            },
            {"ma": "A01", "priceUsd": 27, "status": "available", "colors": [{"name": "Yellow"}]},
        ],
    }
    raw = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    fixture = tmp_path / "catalog.json"
    fixture.write_text(raw, encoding="utf-8")
    ran = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "color_flags.py"), "--fixture", str(fixture)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert ran.returncode == 0, ran.stderr
    assert json.loads(ran.stdout) == [
        {"ma": "S06", "kind": "blank_color", "stored": "", "index": None, "piece": None},
        {"ma": "V05", "kind": "blank_color", "stored": "", "index": 0, "piece": None},
    ]
    assert "Yellow" not in ran.stdout
    assert "#111111" not in ran.stdout
    assert fixture.read_text(encoding="utf-8") == raw
    assert list(tmp_path.iterdir()) == [fixture]
    assert HELD_PATH.read_bytes() == held_before
    assert PRODUCTS_PATH.read_bytes() == products_before
    policy = load_held_policy()
    assert "V05" in policy.held
    assert "K06" in policy.held


def test_cli_refuses_held_json_and_live_urls() -> None:
    held_before = HELD_PATH.read_bytes()
    products_before = PRODUCTS_PATH.read_bytes()
    refused = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "color_flags.py"), "--fixture", str(HELD_PATH)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert refused.returncode == 2
    assert refused.stdout == ""
    assert "held.json" in refused.stderr
    url = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "color_flags.py"),
            "--fixture",
            "https://example.invalid/catalog.v1.json",
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert url.returncode == 2
    assert url.stdout == ""
    assert "live catalog URL" in url.stderr
    assert HELD_PATH.read_bytes() == held_before
    assert PRODUCTS_PATH.read_bytes() == products_before
