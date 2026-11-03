"""Hex plus blank-name flags from fixtures. Stored names and prices stay as they were."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from held_policy import load_held_policy
from hex_blank_name import (
    CatalogRow,
    FixtureColor,
    flag_hex_blank_names,
    main,
    report_json,
    rows_from_payload,
)

ROOT = Path(__file__).resolve().parents[2]
FIXTURE = Path(__file__).resolve().parent / "fixtures" / "hex_blank_name.json"
HELD = ROOT / "data" / "held.json"
CATALOG = ROOT / "sassy-closet-shop" / "data" / "products.json"
EXTRAS = ROOT / "sassy-closet-shop" / "data" / "intake-extras.json"
SCRIPT = ROOT / "scripts" / "hex_blank_name.py"

EXPECTED = [
    ("S06", 0, "blank_name", "blank", "", "#F4F0E8", "cs0600"),
    ("V05", 0, "blank_name", "blank", "  ", "#111111", "den"),
    ("Z91", 0, "blank_name", "missing", "", "#fff", "cz9100"),
    ("Z92", 0, "blank_name", "null", "", "#C4A484", "cz9200"),
]

KEPT_OUT = (
    "Ivory",
    "Navy",
    "Black",
    "White",
    "Tan",
    "Kem",
    "Hoa",
    "Đen",
    "Yellow",
    "Purple",
    "Xanh",
    "Color 1",
    "Color 2",
    "suggested",
    "corrected",
    "#FFFFFF",
)


def _view(flags: list) -> list[tuple[str, int, str, str, str, str, str]]:
    return [
        (flag.ma, flag.index, flag.kind, flag.reason, flag.stored, flag.hex, flag.color_id)
        for flag in flags
    ]


def test_fixture_flags_a_hex_with_a_blank_name_and_leaves_rows() -> None:
    original = FIXTURE.read_text(encoding="utf-8")
    payload = json.loads(original)
    rows = rows_from_payload(payload)
    before = [
        (
            row.ma,
            row.price_usd,
            row.status,
            tuple((color.hex, color.name, color.name_set, color.color_id) for color in row.colors),
        )
        for row in rows
    ]
    flags = flag_hex_blank_names(rows)
    assert _view(flags) == EXPECTED
    assert before == [
        (
            row.ma,
            row.price_usd,
            row.status,
            tuple((color.hex, color.name, color.name_set, color.color_id) for color in row.colors),
        )
        for row in rows
    ]
    assert json.dumps(payload, ensure_ascii=False) == json.dumps(json.loads(original), ensure_ascii=False)
    assert FIXTURE.read_text(encoding="utf-8") == original
    s06 = rows[0]
    assert s06.ma == "S06"
    assert s06.price_usd == 25
    assert type(s06.price_usd) is int
    assert s06.status == "available"
    assert s06.colors[0].name == ""
    assert s06.colors[0].hex == "#F4F0E8"
    assert s06.colors[1].name == "Xanh"
    assert s06.colors[1].hex == "#1C2A4A"
    assert rows[1].status == "hold"
    assert rows[1].price_usd is None
    assert rows[1].colors[0].name == "  "
    assert rows[1].colors[0].color_id == "den"
    assert rows[3].ma == "K06"
    assert rows[3].status == "hold"
    assert rows[3].colors[0].name == ""
    assert rows[3].colors[0].hex == ""
    body = json.dumps(report_json(rows, flags), ensure_ascii=False)
    report = json.loads(body)
    assert report["readOnly"] is True
    assert report["s06"] == "stays $25"
    assert report["flagCount"] == len(EXPECTED)
    assert report["rows"][0] == {"ma": "S06", "priceUsd": 25, "status": "available"}
    assert report["rows"][1] == {"ma": "V05", "priceUsd": None, "status": "hold"}
    assert report["rows"][2] == {"ma": "A01", "priceUsd": 27, "status": "available"}
    assert report["rows"][3] == {"ma": "K06", "priceUsd": None, "status": "hold"}
    for word in KEPT_OUT:
        assert word not in body
    for flag in report["flags"]:
        assert set(flag) == {"ma", "index", "kind", "reason", "stored", "hex", "colorId"}
        assert "name" not in flag


def test_a_stored_name_is_not_replaced_from_the_hex() -> None:
    ivory = FixtureColor("#F4F0E8", "Ivory", True, "civory")
    hex_as_name = FixtureColor("#111111", "#111111", True, "den")
    labeled = FixtureColor("#FFFFFF", "Color 1", True, "c1")
    spaced = FixtureColor("  #7A8B6F  ", "", True, "cspace")
    bare = FixtureColor("F4F0E8", None, False, "cbare")
    rows = [
        CatalogRow("A02", (ivory, hex_as_name, labeled), 28, True, "available"),
        CatalogRow("s06", (spaced, bare), 25, True, "available"),
    ]
    flags = flag_hex_blank_names(rows)
    assert [(flag.ma, flag.index, flag.reason, flag.stored, flag.hex) for flag in flags] == [
        ("S06", 0, "blank", "", "  #7A8B6F  "),
        ("S06", 1, "missing", "", "F4F0E8"),
    ]
    assert ivory.name == "Ivory"
    assert hex_as_name.name == "#111111"
    assert labeled.name == "Color 1"
    assert rows[1].ma == "s06"
    assert rows[1].price_usd == 25
    assert type(rows[1].price_usd) is int
    assert rows[1].status == "available"
    text = json.dumps([flag.as_json() for flag in flags], ensure_ascii=False)
    for word in ("Ivory", "Black", "White", "Olive", "Navy", "Color 1", "Color 2", "suggested"):
        assert word not in text


def test_blank_name_without_a_hex_is_not_this_flag() -> None:
    rows = [
        CatalogRow(
            "K06",
            (
                FixtureColor("", "", True, "ck"),
                FixtureColor(None, "", True, "cnull"),
                FixtureColor("red", "  ", True, "cred"),
                FixtureColor("#12", None, False, "cshort"),
                FixtureColor(None, None, False, "kem"),
            ),
            None,
            True,
            "hold",
        ),
        CatalogRow("H01", (FixtureColor(None, "Đen", True, None),), 8, True, "available"),
        CatalogRow("S01", (), 39, True, "available"),
    ]
    assert flag_hex_blank_names(rows) == []
    assert rows[0].status == "hold"
    assert rows[0].price_usd is None
    assert rows[0].colors[4].color_id == "kem"
    assert rows[0].colors[4].name is None
    assert rows[1].colors[0].name == "Đen"
    assert rows[2].price_usd == 39


def test_same_ma_blank_hex_rows_stay_separate() -> None:
    rows = [
        CatalogRow("Z02", (FixtureColor("#fff", "", True, "a"),), 11, True, None),
        CatalogRow("Z02", (FixtureColor("#000000", " ", True, "b"),), 12, True, None),
    ]
    flags = flag_hex_blank_names(rows)
    assert [row.price_usd for row in rows] == [11, 12]
    assert [(flag.ma, flag.index, flag.stored, flag.hex) for flag in flags] == [
        ("Z02", 0, "", "#fff"),
        ("Z02", 0, " ", "#000000"),
    ]
    text = json.dumps([flag.as_json() for flag in flags], ensure_ascii=False)
    assert "White" not in text
    assert "Black" not in text
    assert "#FFFFFF" not in text


def test_note_and_color_id_are_not_copied_into_the_name() -> None:
    payload = {
        "products": [
            {
                "ma": "V05",
                "priceUsd": None,
                "status": "hold",
                "colors": [{"id": "den", "hex": "#111111", "name": "", "note": "Hoa"}],
            }
        ]
    }
    original = json.dumps(payload, ensure_ascii=False)
    rows = rows_from_payload(payload)
    flags = flag_hex_blank_names(rows)
    assert json.dumps(payload, ensure_ascii=False) == original
    assert rows[0].colors[0].name == ""
    assert rows[0].status == "hold"
    assert _view(flags) == [("V05", 0, "blank_name", "blank", "", "#111111", "den")]
    text = json.dumps([flag.as_json() for flag in flags], ensure_ascii=False)
    assert "Hoa" not in text
    assert "Black" not in text
    assert "Đen" not in text
    assert payload["products"][0]["colors"][0]["note"] == "Hoa"
    assert payload["products"][0]["colors"][0]["name"] == ""


def test_string_price_and_string_color_stay_stored() -> None:
    payload = [
        {"ma": "Z01", "priceUsd": "25", "colors": [{"hex": "#abc", "name": ""}]},
        {"ma": "H01", "priceUsd": 8, "colors": ["Đen"]},
    ]
    original = json.dumps(payload, ensure_ascii=False)
    rows = rows_from_payload(payload)
    flags = flag_hex_blank_names(rows)
    assert json.dumps(payload, ensure_ascii=False) == original
    assert rows[0].price_usd == "25"
    assert type(rows[0].price_usd) is str
    assert rows[1].colors[0].name == "Đen"
    assert _view(flags) == [("Z01", 0, "blank_name", "blank", "", "#abc", "")]
    text = json.dumps([flag.as_json() for flag in flags], ensure_ascii=False)
    assert "Đen" not in text


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
        CatalogRow("K06", (FixtureColor("#111111", "", True, "den"),), None, True, "hold"),
        CatalogRow("V05", (FixtureColor("#fff", " ", True, "cv"),), None, True, "hold"),
        CatalogRow("S06", (FixtureColor("#F4F0E8", "Xanh", True, "cs"),), 25, True, "available"),
    ]
    flags = flag_hex_blank_names(rows)
    assert [flag.ma for flag in flags] == ["K06", "V05"]
    assert rows[2].price_usd == 25
    assert type(rows[2].price_usd) is int
    assert rows[2].colors[0].name == "Xanh"
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
        (flag["ma"], flag["index"], flag["kind"], flag["reason"], flag["stored"], flag["hex"], flag["colorId"])
        for flag in report["flags"]
    ] == EXPECTED
    assert report["rows"][0] == {"ma": "S06", "priceUsd": 25, "status": "available"}
    assert report["rows"][1]["status"] == "hold"
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
                "colors": [{"id": "cs0601", "hex": "#1C2A4A", "name": "Xanh"}],
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
    assert report["rows"] == [{"ma": "S06", "priceUsd": 25, "status": "available"}]
    assert "Xanh" not in ran.stdout
    assert "Navy" not in ran.stdout
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


def test_script_is_read_only_and_does_not_invent_a_name() -> None:
    text = SCRIPT.read_text(encoding="utf-8")
    assert ".write_text(" not in text
    assert ".write_bytes(" not in text
    assert "open(" not in text
    assert "urlopen" not in text
    assert "requests" not in text
    assert "load_held_policy" not in text
    assert "COLOR_PRESETS" not in text
    assert "suggestedColorName" not in text
    assert "multi_color" not in text
    assert "color_flags" not in text
    assert "vercel" not in text.casefold()
    assert '["priceUsd"] = 25' not in text
    assert "price_usd = 25" not in text
