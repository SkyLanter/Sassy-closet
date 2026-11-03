"""Color-name counts from fixtures. Stored colors and prices stay as they were."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from color_counts import CatalogColor, CatalogPiece, CatalogRow, count_color_names, rows_from_payload
from held_policy import load_held_policy

ROOT = Path(__file__).resolve().parents[2]
HELD_PATH = ROOT / "data" / "held.json"
PRODUCTS_PATH = ROOT / "sassy-closet-shop" / "data" / "products.json"


def _json_counts(rows: list[CatalogRow]) -> list[dict[str, object]]:
    return [item.as_json() for item in count_color_names(rows)]


def test_color_names_are_counted_once_per_ma() -> None:
    rows = [
        CatalogRow("A01", (CatalogColor("Yellow"), CatalogColor("Yellow"), CatalogColor("Purple"))),
        CatalogRow("a02", (CatalogColor("Yellow"),)),
        CatalogRow("S01", ()),
        CatalogRow("A07", None),
        CatalogRow("H01", (CatalogColor("  "),)),
        CatalogRow("O04", (CatalogColor(None), CatalogColor("Đen"))),
        CatalogRow("s06", (), price_usd=25, status="available"),
        CatalogRow("V05", (CatalogColor("", "den", "#111111"),), price_usd=None, status="hold"),
        CatalogRow(
            "K06",
            (CatalogColor("Đen"),),
            pieces=(
                CatalogPiece("p1", ""),
                CatalogPiece("p2", "Hồng"),
                CatalogPiece("p3", "Đen"),
            ),
            status="hold",
        ),
        CatalogRow("A01", (CatalogColor("Yellow"),)),
        CatalogRow("P01", (CatalogColor(" Yellow"),)),
    ]
    assert _json_counts(rows) == [
        {
            "name": "",
            "blank": True,
            "count": 7,
            "codes": ["A07", "H01", "K06", "O04", "S01", "S06", "V05"],
        },
        {"name": " Yellow", "blank": False, "count": 1, "codes": ["P01"]},
        {"name": "Hồng", "blank": False, "count": 1, "codes": ["K06"]},
        {"name": "Purple", "blank": False, "count": 1, "codes": ["A01"]},
        {"name": "Yellow", "blank": False, "count": 2, "codes": ["A01", "A02"]},
        {"name": "Đen", "blank": False, "count": 2, "codes": ["K06", "O04"]},
    ]
    assert rows[0].colors is not None
    assert rows[0].colors[0].name == "Yellow"
    assert rows[4].colors is not None
    assert rows[4].colors[0].name == "  "
    assert rows[5].colors is not None
    assert rows[5].colors[1].name == "Đen"
    assert rows[6].ma == "s06"
    assert rows[6].price_usd == 25
    assert type(rows[6].price_usd) is int
    assert rows[6].status == "available"
    assert rows[7].status == "hold"
    assert rows[7].price_usd is None
    assert rows[7].colors is not None
    assert rows[7].colors[0].name == ""
    assert rows[7].colors[0].color_id == "den"
    assert rows[7].colors[0].hex == "#111111"
    assert rows[8].status == "hold"
    assert rows[8].pieces[0].color == ""
    assert rows[8].pieces[1].color == "Hồng"
    assert rows[10].colors is not None
    assert rows[10].colors[0].name == " Yellow"
    dumped = json.dumps(_json_counts(rows), ensure_ascii=False)
    assert "#111111" not in dumped
    assert "den" not in dumped
    assert "Color 1" not in dumped
    assert "corrected" not in dumped


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
                "images": [{"src": "/products/S06/cover.jpg", "colorId": "den"}],
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
                "colors": [{"id": "den", "hex": "#111111", "name": "", "note": "Đỏ"}],
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
            {"ma": "J01", "priceUsd": 14, "status": "available", "color": "Hồng"},
            {"ma": "J02", "priceUsd": 14, "status": "available", "color": "Kem, Xanh"},
        ],
    }
    original = json.dumps(payload, ensure_ascii=False)
    rows = rows_from_payload(payload)
    counts = _json_counts(rows)
    assert json.dumps(payload, ensure_ascii=False) == original
    assert rows[0].price_usd == 25
    assert type(rows[0].price_usd) is int
    assert rows[0].status == "available"
    assert rows[0].colors == ()
    assert rows[3].price_usd == "12"
    assert counts == [
        {
            "name": "",
            "blank": True,
            "count": 4,
            "codes": ["D03", "H01", "P04", "S06"],
        },
        {"name": "Hồng", "blank": False, "count": 1, "codes": ["J01"]},
        {"name": "Kem", "blank": False, "count": 2, "codes": ["D03", "P04"]},
        {"name": "Kem, Xanh", "blank": False, "count": 1, "codes": ["J02"]},
        {"name": "Off-white", "blank": False, "count": 1, "codes": ["A08"]},
    ]
    text = json.dumps(counts, ensure_ascii=False)
    assert "Xanh" not in text.replace("Kem, Xanh", "")
    assert "Đỏ" not in text
    assert "Ivory" not in text
    assert "Black" not in text
    assert "#F4F0E8" not in text
    assert "#111111" not in text
    assert "Color 1" not in text
    assert payload["products"][0]["priceUsd"] == 25
    assert payload["products"][0]["colors"] == []
    assert payload["products"][0]["color"] == "Kem"
    assert payload["products"][2]["pieces"][0]["color"] == ""
    assert payload["products"][2]["pieces"][0]["suggested"] == ["Đỏ"]
    assert payload["products"][2]["colors"][0]["name"] == ""
    assert payload["products"][2]["colors"][0]["hex"] == "#111111"
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
    counts = _json_counts(rows)
    assert counts == [
        {"name": "", "blank": True, "count": 2, "codes": ["K06", "V05"]},
        {"name": "Đen", "blank": False, "count": 1, "codes": ["S06"]},
    ]
    assert rows[0].status == "hold"
    assert rows[1].status == "hold"
    assert rows[2].price_usd == 25
    assert rows[2].status == "available"
    assert rows[2].colors is not None
    assert rows[2].colors[0].name == "Đen"
    assert "K06" in policy.held
    assert "V05" in policy.held
    assert "S06" not in policy.held
    assert HELD_PATH.read_bytes() == held_before
    assert PRODUCTS_PATH.read_bytes() == products_before


def test_bad_color_shape_is_refused() -> None:
    samples: list[object] = [
        [{"ma": "A01", "colors": {"name": "Kem"}}],
        [{"ma": "A01", "colors": [{"name": 1}]}],
        [{"ma": "A01", "colors": [None]}],
        [{"ma": "A01", "color": ["Kem", "Xanh"]}],
        [{"ma": "A01", "pieces": {"color": "Kem"}}],
        [{"ma": "A01", "pieces": [{"color": ["Đỏ"]}]}],
        [{"ma": "A01", "priceUsd": True}],
        [{"ma": "A01", "status": 1}],
        {"rows": []},
        [{"priceUsd": 25}],
    ]
    for sample in samples:
        try:
            rows_from_payload(sample)
        except ValueError:
            continue
        raise AssertionError(f"accepted a bad catalog fixture: {sample!r}")


def test_cli_prints_counts_and_leaves_files(tmp_path: Path) -> None:
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
            {
                "ma": "A01",
                "priceUsd": 27,
                "status": "available",
                "colors": [{"name": "Yellow"}, {"name": "Purple"}],
            },
            {"ma": "A02", "priceUsd": 20, "status": "available", "colors": [{"name": "Yellow"}]},
            {
                "ma": "K06",
                "status": "hold",
                "colors": [{"name": "Đen"}],
                "pieces": [{"id": "p1", "color": "", "suggested": ["Đỏ"]}],
            },
        ],
    }
    raw = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    fixture = tmp_path / "catalog.json"
    fixture.write_text(raw, encoding="utf-8")
    ran = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "color_counts.py"), "--fixture", str(fixture)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert ran.returncode == 0, ran.stderr
    assert json.loads(ran.stdout) == [
        {"name": "", "blank": True, "count": 3, "codes": ["K06", "S06", "V05"]},
        {"name": "Purple", "blank": False, "count": 1, "codes": ["A01"]},
        {"name": "Yellow", "blank": False, "count": 2, "codes": ["A01", "A02"]},
        {"name": "Đen", "blank": False, "count": 1, "codes": ["K06"]},
    ]
    assert "Đỏ" not in ran.stdout
    assert "#111111" not in ran.stdout
    assert "Ivory" not in ran.stdout
    assert "Color 1" not in ran.stdout
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
        [sys.executable, str(ROOT / "scripts" / "color_counts.py"), "--fixture", str(HELD_PATH)],
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
            str(ROOT / "scripts" / "color_counts.py"),
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


def test_checked_in_catalog_is_only_read() -> None:
    held_before = HELD_PATH.read_bytes()
    products_before = PRODUCTS_PATH.read_bytes()
    payload = json.loads(products_before)
    original = json.dumps(payload, ensure_ascii=False)
    prices = [(product["ma"], product["priceUsd"], product["status"]) for product in payload["products"]]
    counts = _json_counts(rows_from_payload(payload))
    assert json.dumps(payload, ensure_ascii=False) == original
    ran = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "color_counts.py"), "--fixture", str(PRODUCTS_PATH)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert ran.returncode == 0, ran.stderr
    assert json.loads(ran.stdout) == counts
    assert PRODUCTS_PATH.read_bytes() == products_before
    assert HELD_PATH.read_bytes() == held_before
    reloaded = json.loads(products_before)
    assert [(product["ma"], product["priceUsd"], product["status"]) for product in reloaded["products"]] == prices
    assert not any(product["ma"].strip().upper() == "S06" and product["priceUsd"] != 25 for product in reloaded["products"])

    stored: dict[str, set[str]] = {}
    blank_codes: list[str] = []
    for product in reloaded["products"]:
        code = product["ma"].strip().upper()
        names: set[str] = set()
        saw_blank = not product["colors"]
        for color in product["colors"]:
            raw_name = color["name"]
            if isinstance(raw_name, str) and raw_name.strip():
                names.add(raw_name)
            else:
                saw_blank = True
        stored[code] = names
        if saw_blank:
            blank_codes.append(code)
    reported = {item["name"]: set(item["codes"]) for item in counts}
    for name, codes in reported.items():
        if name == "":
            continue
        assert not str(name).startswith("#")
        assert all(name in stored[code] for code in codes)
    for code, names in stored.items():
        for name in names:
            assert code in reported[name]
    assert reported[""] == set(blank_codes)
    assert reported["Pink + Off-white"] == {"P01"}
    assert "Color 1" not in reported
    assert "Ivory" not in reported
    policy = load_held_policy()
    assert "K06" in policy.held
    assert "V05" in policy.held
    assert policy.held == load_held_policy().held
