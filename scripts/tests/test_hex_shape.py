"""Hex shape flags from fixtures. Stored hex text and prices stay as they were."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from held_policy import load_held_policy
from hex_shape import (
    CatalogRow,
    FixtureColor,
    flag_hex_shapes,
    main,
    report_json,
    rows_from_payload,
)

ROOT = Path(__file__).resolve().parents[2]
FIXTURE = Path(__file__).resolve().parent / "fixtures" / "hex_shape.json"
HELD = ROOT / "data" / "held.json"
CATALOG = ROOT / "sassy-closet-shop" / "data" / "products.json"
EXTRAS = ROOT / "sassy-closet-shop" / "data" / "intake-extras.json"
SCRIPT = ROOT / "scripts" / "hex_shape.py"

EXPECTED = [
    ("S06", 0, "bad_hex", "F4F0E8", "cs0600"),
    ("S06", 3, "bad_hex", "#12", "cs0603"),
    ("V05", 0, "bad_hex", " #7A8B6F", "den"),
    ("Z91", 0, "bad_hex", "#ffff", "cz9100"),
    ("Z92", 0, "bad_hex", "#ggg", "cz9200"),
    ("Z93", 0, "bad_hex", "red", "cz9300"),
    ("Z94", 0, "bad_hex", "#12345678", "cz9400"),
]

KEPT_OUT = (
    "#F4F0E8",
    "#FFFFFF",
    "#AABBCC",
    "#121212",
    "#111111",
    "corrected",
    "normalized",
    "suggested",
    "Kem",
    "Xanh",
    "Yellow",
    "Đen",
    "Hoa",
    "Ivory",
    "Navy",
    "Black",
    "White",
    "Color 1",
)


def _view(flags: list) -> list[tuple[str, int, str, str, str]]:
    return [(flag.ma, flag.index, flag.kind, flag.stored, flag.color_id) for flag in flags]


def _snapshot(rows: list[CatalogRow]) -> list[tuple[object, ...]]:
    return [
        (
            row.ma,
            row.price_usd,
            row.status,
            tuple((color.hex, color.hex_set, color.name, color.color_id) for color in row.colors),
        )
        for row in rows
    ]


def test_fixture_flags_a_bad_hex_and_leaves_rows() -> None:
    original = FIXTURE.read_text(encoding="utf-8")
    payload = json.loads(original)
    rows = rows_from_payload(payload)
    before = _snapshot(rows)
    flags = flag_hex_shapes(rows)
    assert _view(flags) == EXPECTED
    assert _snapshot(rows) == before
    assert json.dumps(payload, ensure_ascii=False) == json.dumps(json.loads(original), ensure_ascii=False)
    assert FIXTURE.read_text(encoding="utf-8") == original
    s06 = rows[0]
    assert s06.ma == "S06"
    assert s06.price_usd == 25
    assert type(s06.price_usd) is int
    assert s06.status == "available"
    assert s06.colors[0].hex == "F4F0E8"
    assert s06.colors[0].name == "Kem"
    assert s06.colors[1].hex == "#1C2A4A"
    assert s06.colors[1].name == "Xanh"
    assert s06.colors[2].hex == ""
    assert s06.colors[2].name == ""
    assert s06.colors[3].hex == "#12"
    assert rows[1].status == "hold"
    assert rows[1].price_usd is None
    assert rows[1].colors[0].hex == " #7A8B6F"
    assert rows[1].colors[0].name == "Đen"
    assert rows[3].ma == "K06"
    assert rows[3].status == "hold"
    assert rows[3].colors[0].hex == ""
    assert rows[3].colors[0].color_id == "den"
    assert rows[9].colors[0].hex is None
    assert rows[9].colors[0].hex_set is False
    assert rows[9].colors[0].color_id == "kem"
    assert rows[10].colors[0].hex is None
    assert rows[10].colors[0].hex_set is True
    assert rows[11].colors[0].hex == "   "
    body = json.dumps(report_json(rows, flags), ensure_ascii=False)
    report = json.loads(body)
    assert report["readOnly"] is True
    assert report["s06"] == "stays $25"
    assert report["flagCount"] == len(EXPECTED)
    assert report["rows"][0] == {
        "ma": "S06",
        "priceUsd": 25,
        "status": "available",
        "colors": [
            {"index": 0, "hex": "F4F0E8"},
            {"index": 1, "hex": "#1C2A4A"},
            {"index": 2, "hex": ""},
            {"index": 3, "hex": "#12"},
        ],
    }
    assert report["rows"][1] == {
        "ma": "V05",
        "priceUsd": None,
        "status": "hold",
        "colors": [{"index": 0, "hex": " #7A8B6F"}],
    }
    assert report["rows"][3] == {
        "ma": "K06",
        "priceUsd": None,
        "status": "hold",
        "colors": [{"index": 0, "hex": ""}],
    }
    for word in KEPT_OUT:
        assert word not in body
    for flag in report["flags"]:
        assert set(flag) == {"ma", "index", "kind", "stored", "colorId"}
        assert "normalized" not in flag
        assert "corrected" not in flag


def test_blank_hex_stays_blank_and_is_not_rewritten() -> None:
    blank = FixtureColor("", True, "", "den")
    spaces = FixtureColor("   ", True, "Space", "cspace")
    missing = FixtureColor(None, False, "Kem", "kem")
    null_hex = FixtureColor(None, True, "Null", "cnull")
    rows = [
        CatalogRow("K06", (blank,), None, True, "hold"),
        CatalogRow("s06", (spaces, missing, null_hex), 25, True, "available"),
    ]
    assert flag_hex_shapes(rows) == []
    assert blank.hex == ""
    assert spaces.hex == "   "
    assert missing.hex is None
    assert missing.hex_set is False
    assert null_hex.hex is None
    assert null_hex.hex_set is True
    assert rows[0].status == "hold"
    assert rows[0].colors[0].color_id == "den"
    assert rows[1].ma == "s06"
    assert rows[1].price_usd == 25
    assert type(rows[1].price_usd) is int
    text = json.dumps(report_json(rows, []), ensure_ascii=False)
    assert "#111111" not in text
    assert "#F4F0E8" not in text
    assert "Kem" not in text
    assert text.count('"hex": ""') == 1
    assert text.count('"hex": "   "') == 1


def test_bad_hex_is_flagged_and_not_rewritten() -> None:
    valid = ("#abc", "#ABC", "#aBc", "#000", "#fff", "#FFF", "#aabbcc", "#AABBCC", "#AbCdEf", "#F4F0E8")
    invalid = (
        "fff",
        "F4F0E8",
        "aabbcc",
        "#ab",
        "#abcd",
        "#abcde",
        "#abcdefg",
        "#aabbccdd",
        "#ggg",
        "#gggggg",
        "red",
        "#",
        "##abc",
        "#abc#",
        " #abc",
        "#abc ",
        "#abc\n",
    )
    kept = [FixtureColor(value, True, "Kept", f"c{index}") for index, value in enumerate(valid)]
    bad = [FixtureColor(value, True, "Kept", f"b{index}") for index, value in enumerate(invalid)]
    row = CatalogRow("S06", tuple(kept + bad), 25, True, "available")
    flags = flag_hex_shapes([row])
    assert [(flag.index, flag.stored) for flag in flags] == [
        (len(valid) + index, value) for index, value in enumerate(invalid)
    ]
    assert [color.hex for color in row.colors] == list(valid) + list(invalid)
    assert row.price_usd == 25
    assert type(row.price_usd) is int
    text = json.dumps([flag.as_json() for flag in flags], ensure_ascii=False)
    assert "#FFFFFF" not in text
    assert "#AABBCC" not in text
    assert "#F4F0E8" not in text
    assert "corrected" not in text


def test_same_ma_rows_stay_separate() -> None:
    rows = [
        CatalogRow("Z02", (FixtureColor("#ffff", True, "A", "a"),), 11, True, None),
        CatalogRow("Z02", (FixtureColor("", True, "B", "b"),), 12, True, None),
    ]
    flags = flag_hex_shapes(rows)
    assert [row.price_usd for row in rows] == [11, 12]
    assert rows[1].colors[0].hex == ""
    assert [(flag.ma, flag.index, flag.stored) for flag in flags] == [("Z02", 0, "#ffff")]
    text = json.dumps([flag.as_json() for flag in flags], ensure_ascii=False)
    assert "#FFFFFF" not in text
    assert "#FFFF" not in text


def test_note_and_color_id_are_not_copied_into_the_hex() -> None:
    payload = {
        "products": [
            {
                "ma": "K06",
                "priceUsd": None,
                "status": "hold",
                "colors": [{"id": "den", "hex": "", "name": "", "note": "#111111"}],
            },
            {
                "ma": "V05",
                "priceUsd": None,
                "status": "hold",
                "colors": [{"id": "den", "hex": "red", "name": "Đen", "note": "#111111"}],
            },
        ]
    }
    original = json.dumps(payload, ensure_ascii=False)
    rows = rows_from_payload(payload)
    flags = flag_hex_shapes(rows)
    assert json.dumps(payload, ensure_ascii=False) == original
    assert rows[0].colors[0].hex == ""
    assert rows[0].status == "hold"
    assert rows[1].colors[0].hex == "red"
    assert _view(flags) == [("V05", 0, "bad_hex", "red", "den")]
    text = json.dumps(report_json(rows, flags), ensure_ascii=False)
    assert "#111111" not in text
    assert "Đen" not in text
    assert payload["products"][0]["colors"][0]["hex"] == ""
    assert payload["products"][0]["colors"][0]["note"] == "#111111"
    assert payload["products"][1]["colors"][0]["hex"] == "red"


def test_string_price_and_string_color_stay_stored() -> None:
    payload = [
        {"ma": "Z01", "priceUsd": "25", "colors": [{"hex": "abc", "name": ""}]},
        {"ma": "H01", "priceUsd": 8, "colors": ["Đen"]},
        {"ma": "S06", "priceUsd": 25, "status": "available", "colors": [{"hex": "#fff", "name": "Xanh"}]},
    ]
    original = json.dumps(payload, ensure_ascii=False)
    rows = rows_from_payload(payload)
    flags = flag_hex_shapes(rows)
    assert json.dumps(payload, ensure_ascii=False) == original
    assert rows[0].price_usd == "25"
    assert type(rows[0].price_usd) is str
    assert rows[0].colors[0].hex == "abc"
    assert rows[1].colors[0].name == "Đen"
    assert rows[1].colors[0].hex is None
    assert rows[2].price_usd == 25
    assert type(rows[2].price_usd) is int
    assert rows[2].colors[0].hex == "#fff"
    assert _view(flags) == [("Z01", 0, "bad_hex", "abc", "")]
    text = json.dumps(report_json(rows, flags), ensure_ascii=False)
    assert "#ABC" not in text
    assert "#AABBCC" not in text
    assert "#FFFFFF" not in text
    assert "Đen" not in text
    assert "Xanh" not in text


def test_bad_color_shape_is_refused() -> None:
    samples = [
        [{"ma": "A01", "colors": {"hex": "#fff", "name": ""}}],
        [{"ma": "A01", "colors": [{"hex": 111111, "name": ""}]}],
        [{"ma": "A01", "colors": [{"hex": "#fff", "name": 1}]}],
        [{"ma": "A01", "colors": [{"hex": "#fff", "id": 1, "name": ""}]}],
        [{"ma": "A01", "priceUsd": True, "colors": []}],
        [{"ma": " ", "colors": []}],
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
        CatalogRow("K06", (FixtureColor("", True, "", "den"),), None, True, "hold"),
        CatalogRow("V05", (FixtureColor("#ggg", True, " ", "cv"),), None, True, "hold"),
        CatalogRow("S06", (FixtureColor("#F4F0E8", True, "Xanh", "cs"),), 25, True, "available"),
    ]
    flags = flag_hex_shapes(rows)
    assert [flag.ma for flag in flags] == ["V05"]
    assert flags[0].stored == "#ggg"
    assert rows[2].price_usd == 25
    assert type(rows[2].price_usd) is int
    assert rows[2].colors[0].hex == "#F4F0E8"
    assert rows[2].colors[0].name == "Xanh"
    assert rows[0].colors[0].hex == ""
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
    assert report["flagCount"] == len(EXPECTED)
    assert [
        (flag["ma"], flag["index"], flag["kind"], flag["stored"], flag["colorId"])
        for flag in report["flags"]
    ] == EXPECTED
    assert report["rows"][0]["priceUsd"] == 25
    assert report["rows"][0]["colors"][2]["hex"] == ""
    assert report["rows"][1]["status"] == "hold"
    assert report["rows"][3]["status"] == "hold"
    assert report["rows"][3]["colors"][0]["hex"] == ""
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
                "colors": [
                    {"id": "cs0601", "hex": "#1C2A4A", "name": "Xanh"},
                    {"id": "cs0602", "hex": "", "name": ""},
                ],
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
    assert report["rows"] == [
        {
            "ma": "S06",
            "priceUsd": 25,
            "status": "available",
            "colors": [
                {"index": 0, "hex": "#1C2A4A"},
                {"index": 1, "hex": ""},
            ],
        }
    ]
    assert "Xanh" not in ran.stdout
    assert "Navy" not in ran.stdout
    assert "#FFFFFF" not in ran.stdout
    assert fixture.read_text(encoding="utf-8") == raw


def test_cli_refuses_held_json_live_urls_and_bad_files(tmp_path: Path) -> None:
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
    bad_raw = '{"products":[{"ma":"S06","priceUsd":25,"colors":{"hex":"#fff"}}]}\n'
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


def test_script_is_read_only_and_does_not_rewrite_a_hex() -> None:
    text = SCRIPT.read_text(encoding="utf-8")
    assert ".write_text(" not in text
    assert ".write_bytes(" not in text
    assert "open(" not in text
    assert "urlopen" not in text
    assert "requests" not in text
    assert "load_held_policy" not in text
    assert "normalizeHex" not in text
    assert "hex_blank_name" not in text
    assert "COLOR_PRESETS" not in text
    assert "suggestedColorName" not in text
    assert "vercel" not in text.casefold()
    assert '["priceUsd"] = 25' not in text
    assert "price_usd = 25" not in text
