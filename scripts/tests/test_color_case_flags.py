"""Case-only color flags from fixtures. Stored names and prices stay as they were."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from color_case_flags import (
    CatalogColor,
    CatalogPiece,
    CatalogRow,
    ColorCaseFlag,
    flag_case_colors,
    rows_from_payload,
)
from held_policy import load_held_policy

ROOT = Path(__file__).resolve().parents[2]
HELD_PATH = ROOT / "data" / "held.json"
PRODUCTS_PATH = ROOT / "sassy-closet-shop" / "data" / "products.json"
PINK_NAMES = ("PINK", "Pink", "pink")
COMPOUND_NAMES = ("Pink + Off-white", "pink + off-white")
DEN_NAMES = ("Đen", "đen")


def _view(flags: list[ColorCaseFlag]) -> list[tuple[str, str, str, tuple[str, ...], int | None, str | None]]:
    return [
        (flag.ma, flag.kind, flag.stored, flag.names, flag.index, flag.piece)
        for flag in flags
    ]


def test_case_variants_are_flagged_and_not_renamed() -> None:
    rows = [
        CatalogRow("A01", (CatalogColor("Pink"), CatalogColor("Yellow"), CatalogColor("pink"))),
        CatalogRow("p02", (CatalogColor("Pink + Off-white"),)),
        CatalogRow("S01", (CatalogColor("pink + off-white"), CatalogColor("Blue"))),
        CatalogRow("A03", (CatalogColor("PINK"),)),
        CatalogRow("H01", (CatalogColor(" Yellow"),)),
        CatalogRow("A02", (CatalogColor("Yellow"),)),
        CatalogRow(
            "K06",
            (CatalogColor("Đen"),),
            pieces=(CatalogPiece("p1", "đen"), CatalogPiece("p2", "Hồng")),
            status="hold",
        ),
        CatalogRow("V05", (CatalogColor("  "),), status="hold"),
        CatalogRow("s06", (CatalogColor("Purple"),), price_usd=25, status="available"),
    ]
    flags = flag_case_colors(rows)
    assert _view(flags) == [
        ("A01", "case_color", "Pink", PINK_NAMES, 0, None),
        ("A01", "case_color", "pink", PINK_NAMES, 2, None),
        ("P02", "case_color", "Pink + Off-white", COMPOUND_NAMES, 0, None),
        ("S01", "case_color", "pink + off-white", COMPOUND_NAMES, 0, None),
        ("A03", "case_color", "PINK", PINK_NAMES, 0, None),
        ("K06", "case_color", "Đen", DEN_NAMES, 0, None),
        ("K06", "case_color", "đen", DEN_NAMES, 0, "p1"),
    ]
    assert rows[0].colors is not None
    assert rows[0].colors[0].name == "Pink"
    assert rows[0].colors[1].name == "Yellow"
    assert rows[0].colors[2].name == "pink"
    assert rows[1].ma == "p02"
    assert rows[1].colors is not None
    assert rows[1].colors[0].name == "Pink + Off-white"
    assert rows[2].colors is not None
    assert rows[2].colors[0].name == "pink + off-white"
    assert rows[2].colors[1].name == "Blue"
    assert rows[3].colors is not None
    assert rows[3].colors[0].name == "PINK"
    assert rows[4].colors is not None
    assert rows[4].colors[0].name == " Yellow"
    assert rows[5].colors is not None
    assert rows[5].colors[0].name == "Yellow"
    assert rows[6].status == "hold"
    assert rows[6].colors is not None
    assert rows[6].colors[0].name == "Đen"
    assert rows[6].pieces[0].color == "đen"
    assert rows[6].pieces[1].color == "Hồng"
    assert rows[7].status == "hold"
    assert rows[7].colors is not None
    assert rows[7].colors[0].name == "  "
    assert rows[8].ma == "s06"
    assert rows[8].price_usd == 25
    assert type(rows[8].price_usd) is int
    assert rows[8].status == "available"
    assert rows[8].colors is not None
    assert rows[8].colors[0].name == "Purple"
    dumped = json.dumps([flag.as_json() for flag in flags], ensure_ascii=False)
    assert "Yellow" not in dumped
    assert "Blue" not in dumped
    assert "Purple" not in dumped
    assert "Hồng" not in dumped
    assert "renamed" not in dumped
    assert "corrected" not in dumped
    assert "canonical" not in dumped
    assert all(flag.stored in flag.names for flag in flags)
    assert flag_case_colors(rows) == flags


def test_single_spelling_stays_quiet() -> None:
    rows = [
        CatalogRow("a01", (CatalogColor("Pink"), CatalogColor("Pink"))),
        CatalogRow("A02", (CatalogColor("Pink"),)),
        CatalogRow(
            "P01",
            (CatalogColor("Pink + Off-white"), CatalogColor("Dark pink"), CatalogColor("Light pink")),
        ),
        CatalogRow("S01", (CatalogColor(" Yellow"), CatalogColor("Yellow"))),
        CatalogRow("H01", (CatalogColor("  "), CatalogColor(None))),
        CatalogRow("S06", (), price_usd=25, status="available"),
        CatalogRow("K06", None, pieces=(CatalogPiece("p1", ""), CatalogPiece("p2", "Hồng")), status="hold"),
    ]
    assert flag_case_colors(rows) == []
    assert rows[0].ma == "a01"
    assert rows[0].colors is not None
    assert rows[0].colors[0].name == "Pink"
    assert rows[0].colors[1].name == "Pink"
    assert rows[2].colors is not None
    assert rows[2].colors[0].name == "Pink + Off-white"
    assert rows[2].colors[1].name == "Dark pink"
    assert rows[2].colors[2].name == "Light pink"
    assert rows[3].colors is not None
    assert rows[3].colors[0].name == " Yellow"
    assert rows[3].colors[1].name == "Yellow"
    assert rows[5].price_usd == 25
    assert rows[5].colors == ()
    assert rows[6].status == "hold"
    assert rows[6].pieces[1].color == "Hồng"


def test_leading_space_case_pair_is_flagged_without_a_rename() -> None:
    quiet = [
        CatalogRow("A01", (CatalogColor(" Yellow"),)),
        CatalogRow("A02", (CatalogColor("Yellow"),)),
    ]
    assert flag_case_colors(quiet) == []
    assert quiet[0].colors is not None
    assert quiet[0].colors[0].name == " Yellow"
    assert quiet[1].colors is not None
    assert quiet[1].colors[0].name == "Yellow"
    rows = [
        CatalogRow("A01", (CatalogColor(" Yellow"),)),
        CatalogRow("A02", (CatalogColor(" yellow"),)),
    ]
    flags = flag_case_colors(rows)
    assert _view(flags) == [
        ("A01", "case_color", " Yellow", (" Yellow", " yellow"), 0, None),
        ("A02", "case_color", " yellow", (" Yellow", " yellow"), 0, None),
    ]
    assert rows[0].colors is not None
    assert rows[0].colors[0].name == " Yellow"
    assert rows[1].colors is not None
    assert rows[1].colors[0].name == " yellow"


def test_fixture_json_keeps_s06_price_and_does_not_rename() -> None:
    payload = {
        "schema": "catalog.v1",
        "products": [
            {
                "ma": "S06",
                "priceUsd": 25,
                "status": "available",
                "colors": [{"id": "pink", "hex": "#FFC0CB", "name": "Pink", "note": "pink"}],
                "color": "pink",
            },
            {
                "ma": "A01",
                "priceUsd": 27,
                "status": "available",
                "colors": ["pink", "Blue"],
            },
            {
                "ma": "A08",
                "priceUsd": 32,
                "status": "available",
                "colors": [],
                "color": "apricot",
            },
            {
                "ma": "D03",
                "priceUsd": 34,
                "status": "available",
                "colors": [{"id": "den", "hex": "#111111", "name": "Yellow", "note": "Đỏ"}],
                "pieces": [
                    {"id": "p1", "photos": [], "suggested": ["yellow"], "color": "Blue", "note": ""},
                    {"id": "p2", "photos": [], "suggested": ["kem"], "color": "Kem", "note": ""},
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
                "pieces": [{"id": "p1", "color": "", "suggested": ["Pink"]}],
            },
            {"ma": "J02", "priceUsd": 14, "status": "available", "color": "Kem, Xanh"},
            {"ma": "J03", "priceUsd": 14, "status": "available", "color": "Wine"},
            {"ma": "J04", "priceUsd": 14, "status": "available", "color": "wine"},
        ],
    }
    original = json.dumps(payload, ensure_ascii=False)
    rows = rows_from_payload(payload)
    flags = flag_case_colors(rows)
    assert json.dumps(payload, ensure_ascii=False) == original
    assert rows[0].price_usd == 25
    assert type(rows[0].price_usd) is int
    assert rows[0].status == "available"
    assert rows[0].colors is not None
    assert rows[0].colors[0].name == "Pink"
    assert rows[0].colors[0].color_id == "pink"
    assert rows[1].colors is not None
    assert rows[1].colors[0].name == "pink"
    assert rows[1].colors[1].name == "Blue"
    assert rows[2].colors == ()
    assert rows[4].price_usd == "12"
    assert _view(flags) == [
        ("S06", "case_color", "Pink", ("Pink", "pink"), 0, None),
        ("A01", "case_color", "pink", ("Pink", "pink"), 0, None),
        ("J03", "case_color", "Wine", ("Wine", "wine"), 0, None),
        ("J04", "case_color", "wine", ("Wine", "wine"), 0, None),
    ]
    text = json.dumps([flag.as_json() for flag in flags], ensure_ascii=False)
    assert "Blue" not in text
    assert "Yellow" not in text
    assert "yellow" not in text
    assert "Kem" not in text
    assert "apricot" not in text
    assert "Đỏ" not in text
    assert "#FFC0CB" not in text
    assert "#111111" not in text
    assert "renamed" not in text
    assert payload["products"][0]["priceUsd"] == 25
    assert payload["products"][0]["colors"][0]["name"] == "Pink"
    assert payload["products"][0]["color"] == "pink"
    assert payload["products"][1]["colors"] == ["pink", "Blue"]
    assert payload["products"][2]["colors"] == []
    assert payload["products"][2]["color"] == "apricot"
    assert payload["products"][3]["pieces"][0]["suggested"] == ["yellow"]
    assert payload["products"][3]["pieces"][0]["color"] == "Blue"
    assert payload["products"][3]["pieces"][1]["color"] == "Kem"
    assert payload["products"][5]["pieces"][0]["color"] == ""
    assert payload["products"][5]["pieces"][0]["suggested"] == ["Pink"]
    assert payload["products"][6]["color"] == "Kem, Xanh"
    assert payload["products"][7]["color"] == "Wine"
    assert payload["products"][8]["color"] == "wine"


def test_held_file_and_catalog_file_stay_put() -> None:
    held_before = HELD_PATH.read_bytes()
    products_before = PRODUCTS_PATH.read_bytes()
    policy = load_held_policy()
    rows = [
        CatalogRow("K06", (CatalogColor("Đen"),), status="hold"),
        CatalogRow("V05", (CatalogColor("đen"),), status="hold"),
        CatalogRow("S06", (CatalogColor("Pink"),), price_usd=25, status="available"),
        CatalogRow("A01", (CatalogColor("pink"),), price_usd=27, status="available"),
    ]
    flags = flag_case_colors(rows)
    assert [flag.ma for flag in flags] == ["K06", "V05", "S06", "A01"]
    assert [flag.stored for flag in flags] == ["Đen", "đen", "Pink", "pink"]
    assert rows[0].status == "hold"
    assert rows[1].status == "hold"
    assert rows[2].price_usd == 25
    assert rows[2].status == "available"
    assert rows[2].colors is not None
    assert rows[2].colors[0].name == "Pink"
    assert rows[3].colors is not None
    assert rows[3].colors[0].name == "pink"
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
        [{"ma": "  ", "colors": [{"name": "Pink"}]}],
    ]
    for sample in samples:
        try:
            rows_from_payload(sample)
        except ValueError:
            continue
        raise AssertionError(f"accepted a bad catalog fixture: {sample!r}")
    try:
        flag_case_colors([CatalogRow("  ", (CatalogColor("Pink"),))])
    except ValueError:
        return
    raise AssertionError("a blank mã was accepted")


def test_cli_prints_flags_and_leaves_files(tmp_path: Path) -> None:
    held_before = HELD_PATH.read_bytes()
    products_before = PRODUCTS_PATH.read_bytes()
    payload = {
        "schema": "catalog.v1",
        "products": [
            {
                "ma": "S06",
                "priceUsd": 25,
                "status": "available",
                "colors": [{"name": "Pink", "hex": "#FFC0CB", "id": "ca"}],
            },
            {"ma": "A01", "priceUsd": 27, "status": "available", "colors": [{"name": "pink"}]},
            {"ma": "A02", "priceUsd": 20, "status": "available", "colors": [{"name": "Yellow"}]},
            {"ma": "V05", "priceUsd": None, "status": "hold", "colors": [{"name": ""}]},
            {
                "ma": "K06",
                "status": "hold",
                "colors": [{"name": "Đen"}],
                "pieces": [{"id": "p1", "color": "đen", "suggested": ["Hồng"]}],
            },
        ],
    }
    raw = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    fixture = tmp_path / "catalog.json"
    fixture.write_text(raw, encoding="utf-8")
    ran = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "color_case_flags.py"), "--fixture", str(fixture)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert ran.returncode == 0, ran.stderr
    assert json.loads(ran.stdout) == [
        {
            "ma": "S06",
            "kind": "case_color",
            "stored": "Pink",
            "names": ["Pink", "pink"],
            "index": 0,
            "piece": None,
        },
        {
            "ma": "A01",
            "kind": "case_color",
            "stored": "pink",
            "names": ["Pink", "pink"],
            "index": 0,
            "piece": None,
        },
        {
            "ma": "K06",
            "kind": "case_color",
            "stored": "Đen",
            "names": ["Đen", "đen"],
            "index": 0,
            "piece": None,
        },
        {
            "ma": "K06",
            "kind": "case_color",
            "stored": "đen",
            "names": ["Đen", "đen"],
            "index": 0,
            "piece": "p1",
        },
    ]
    assert "Yellow" not in ran.stdout
    assert "#FFC0CB" not in ran.stdout
    assert "Hồng" not in ran.stdout
    assert "renamed" not in ran.stdout
    assert fixture.read_text(encoding="utf-8") == raw
    reloaded = json.loads(raw)
    assert reloaded["products"][0]["priceUsd"] == 25
    assert reloaded["products"][0]["colors"][0]["name"] == "Pink"
    assert reloaded["products"][1]["colors"][0]["name"] == "pink"
    assert list(tmp_path.iterdir()) == [fixture]
    assert HELD_PATH.read_bytes() == held_before
    assert PRODUCTS_PATH.read_bytes() == products_before
    policy = load_held_policy()
    assert "V05" in policy.held
    assert "K06" in policy.held


def test_cli_refuses_held_json_and_live_urls() -> None:
    held_before = HELD_PATH.read_bytes()
    products_before = PRODUCTS_PATH.read_bytes()
    script = str(ROOT / "scripts" / "color_case_flags.py")
    refused = subprocess.run(
        [sys.executable, script, "--fixture", str(HELD_PATH)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert refused.returncode == 2
    assert refused.stdout == ""
    assert "held.json" in refused.stderr
    url = subprocess.run(
        [sys.executable, script, "--fixture", "https://example.invalid/catalog.v1.json"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert url.returncode == 2
    assert url.stdout == ""
    assert "live catalog URL" in url.stderr
    missing = subprocess.run(
        [sys.executable, script, "--fixture", str(ROOT / "scripts" / "no-such-fixture.json")],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert missing.returncode == 2
    assert missing.stdout == ""
    assert "fixture not found" in missing.stderr
    assert HELD_PATH.read_bytes() == held_before
    assert PRODUCTS_PATH.read_bytes() == products_before


def _stored_spellings(payload: dict[str, object]) -> dict[str, set[str]]:
    products = payload.get("products")
    if not isinstance(products, list):
        raise AssertionError("catalog fixture needs a product list")
    groups: dict[str, set[str]] = {}
    for product in products:
        if not isinstance(product, dict):
            raise AssertionError("catalog row must be an object")
        names: list[str] = []
        colors = product.get("colors")
        if isinstance(colors, list):
            for color in colors:
                if isinstance(color, str):
                    names.append(color)
                elif isinstance(color, dict) and isinstance(color.get("name"), str):
                    names.append(color["name"])
        elif isinstance(product.get("color"), str):
            names.append(product["color"])
        pieces = product.get("pieces")
        if isinstance(pieces, list):
            for piece in pieces:
                if isinstance(piece, dict) and isinstance(piece.get("color"), str):
                    names.append(piece["color"])
        for name in names:
            if name.strip() == "":
                continue
            groups.setdefault(name.casefold(), set()).add(name)
    return groups


def test_checked_in_catalog_single_spellings_stay_quiet() -> None:
    held_before = HELD_PATH.read_bytes()
    products_before = PRODUCTS_PATH.read_bytes()
    payload = json.loads(products_before)
    original = json.dumps(payload, ensure_ascii=False)
    prices = [(product["ma"], product["priceUsd"], product["status"]) for product in payload["products"]]
    groups = _stored_spellings(payload)
    assert groups["pink"] == {"Pink"}
    assert all(len(spellings) == 1 for spellings in groups.values())
    flags = flag_case_colors(rows_from_payload(payload))
    assert flags == []
    assert json.dumps(payload, ensure_ascii=False) == original
    ran = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "color_case_flags.py"), "--fixture", str(PRODUCTS_PATH)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert ran.returncode == 0, ran.stderr
    assert json.loads(ran.stdout) == []
    assert "renamed" not in ran.stdout
    assert PRODUCTS_PATH.read_bytes() == products_before
    assert HELD_PATH.read_bytes() == held_before
    reloaded = json.loads(products_before)
    assert [(product["ma"], product["priceUsd"], product["status"]) for product in reloaded["products"]] == prices
    for product in reloaded["products"]:
        if str(product["ma"]).strip().upper() == "S06":
            assert product["priceUsd"] == 25
            assert type(product["priceUsd"]) is int
    policy = load_held_policy()
    assert "K06" in policy.held
    assert "V05" in policy.held
    assert policy.held == load_held_policy().held
