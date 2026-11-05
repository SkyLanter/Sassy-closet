"""Fixture-only customer copy voice. No live catalog and no row writes."""

from __future__ import annotations

import json
import math
import subprocess
import sys
from pathlib import Path

from customer_copy_voice import (
    CatalogRow,
    CopyField,
    flag_customer_copy,
    main,
    report_json,
    rows_from_payload,
)
from held_policy import load_held_policy

ROOT = Path(__file__).resolve().parents[2]
FIXTURE = Path(__file__).resolve().parent / "fixtures" / "customer_copy_voice.json"
HELD = ROOT / "data" / "held.json"
CATALOG = ROOT / "sassy-closet-shop" / "data" / "products.json"
EXTRAS = ROOT / "sassy-closet-shop" / "data" / "intake-extras.json"
SCRIPT = ROOT / "scripts" / "customer_copy_voice.py"

EXPECTED = [
    ("Z81", "titleEn", None, "stock_voice", "Available", "Available"),
    ("Z81", "descriptionEn", None, "stock_voice", "on hand", "on hand"),
    ("Z82", "descriptionEn", None, "ops_voice", "Taobao", "Taobao"),
    ("Z82", "descriptionEn", None, "ops_voice", "Zelle", "Zelle"),
    ("Z83", "descriptionEn", None, "filler_voice", "unique piece", "unique piece"),
    ("Z83", "descriptionEn", None, "filler_voice", "curated", "curated"),
    ("Z84", "descriptionVn", None, "stock_voice", "đang có", "đang có"),
    ("Z84", "descriptionVn", None, "filler_voice", "độc bản", "độc bản"),
    ("Z85", "descriptionEn", None, "invented_lead", "invented lead", "2-4 week"),
    ("Z85", "descriptionEn", None, "invented_lead", "invented lead", "flat $8"),
    ("Z85", "descriptionEn", None, "invented_lead", "invented lead", "$6.95"),
    ("Z85", "descriptionEn", None, "invented_lead", "invented lead", "porch date"),
    ("A01", "titleVn", None, "stock_voice", "Hold", "Hold"),
    ("A01", "colorName", 0, "stock_voice", "In stock", "In stock"),
    ("A01", "colorNote", 0, "stock_voice", "Status:", "Status: "),
]

KEPT_OUT = (
    "Puppy",
    "cardigan",
    "Soft knit",
    "Ready",
    "today",
    "Ask on",
    "Pay",
    "Received locally",
    "Pink",
    "studio",
    "Ships in",
    "Then",
    "Was",
    "Chiếc",
)


def _view(flags: list) -> list[tuple[str, str, int | None, str, str, str]]:
    return [
        (flag.ma, flag.field, flag.index, flag.kind, flag.label, flag.stored) for flag in flags
    ]


def _snapshot(rows: list[CatalogRow]) -> list[tuple[object, ...]]:
    return [
        (
            row.ma,
            row.price_usd,
            row.price_set,
            row.status,
            tuple((field.field, field.index, field.text) for field in row.fields),
        )
        for row in rows
    ]


def test_fixture_names_the_phrase_and_leaves_rows() -> None:
    original = FIXTURE.read_text(encoding="utf-8")
    payload = json.loads(original)
    rows = rows_from_payload(payload)
    before = _snapshot(rows)
    flags = flag_customer_copy(rows)
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
    assert by_ma["A01"]["priceUsd"] == 27
    assert "titleEn" not in by_ma["S06"]
    assert "Soft knit" not in text


def test_lowercase_available_and_message_first_stay_quiet() -> None:
    rows = rows_from_payload(
        [
            {
                "ma": " s06 ",
                "priceUsd": 25,
                "status": "available",
                "descriptionEn": "message-first. available tomorrow. Status:live.",
            }
        ]
    )
    before = _snapshot(rows)
    flags = flag_customer_copy(rows)
    assert _snapshot(rows) == before
    assert flags == []
    assert rows[0].ma == " s06 "
    assert rows[0].price_usd == 25
    assert rows[0].status == "available"
    report = report_json(rows, flags)
    assert report["rows"][0]["ma"] == "S06"
    assert "tomorrow" not in json.dumps(report)
    assert "message-first" not in json.dumps(report)


def test_shop_examples_and_overlap() -> None:
    rows = [
        CatalogRow(
            "K03",
            (
                CopyField("descriptionEn", None, "One unique top on hand."),
                CopyField("descriptionVn", None, "Áo độc bản — một chiếc đang có."),
                CopyField("descriptionEn", None, "Unique pieces only."),
            ),
            30,
            True,
            "hold",
        )
    ]
    flags = flag_customer_copy(rows)
    assert _view(flags) == [
        ("K03", "descriptionEn", None, "stock_voice", "on hand", "on hand"),
        ("K03", "descriptionEn", None, "filler_voice", "unique top", "unique top"),
        ("K03", "descriptionVn", None, "stock_voice", "đang có", "đang có"),
        ("K03", "descriptionVn", None, "filler_voice", "độc bản", "độc bản"),
        ("K03", "descriptionEn", None, "filler_voice", "unique pieces", "Unique pieces"),
    ]
    assert rows[0].status == "hold"
    assert rows[0].fields[0].text == "One unique top on hand."
    text = json.dumps(report_json(rows, flags), ensure_ascii=False)
    assert "One unique top on hand." not in text
    assert "một chiếc" not in text


def test_a_phrase_split_across_fields_is_named_once() -> None:
    rows = rows_from_payload(
        [
            {
                "ma": "Z92",
                "priceUsd": 25,
                "status": "hold",
                "titleEn": "Ready on",
                "titleVn": "hand wash",
                "descriptionEn": "A unique",
                "descriptionVn": "piece. Ships in 2-4",
            },
            {
                "ma": "Z93",
                "priceUsd": 25,
                "status": "available",
                "descriptionEn": "Ships in 2-4",
                "descriptionVn": "tuần nếu inbox",
            },
        ]
    )
    before = _snapshot(rows)
    flags = flag_customer_copy(rows)
    assert _snapshot(rows) == before
    assert rows[0].price_usd == 25
    assert rows[0].status == "hold"
    assert _view(flags) == [
        ("Z92", "joinedCopy", None, "stock_voice", "on hand", "on hand"),
        ("Z92", "joinedCopy", None, "filler_voice", "unique piece", "unique piece"),
        ("Z93", "joinedDescriptions", None, "invented_lead", "invented lead", "2-4\ntuần"),
    ]
    text = json.dumps(report_json(rows, flags), ensure_ascii=False)
    assert "hand wash" not in text
    assert "inbox" not in text
    assert "Ships in" not in text


def test_listed_uses_the_space_the_shop_inserts() -> None:
    rows = rows_from_payload(
        [{"ma": "Z97", "priceUsd": 25, "status": "hold", "descriptionEn": "A listed"}]
    )
    before = rows[0].fields[0].text
    flags = flag_customer_copy(rows)
    assert before == "A listed"
    assert rows[0].price_usd == 25
    assert rows[0].status == "hold"
    assert _view(flags) == [
        ("Z97", "joinedCopy", None, "filler_voice", "A listed", "A listed "),
    ]


def test_invented_lead_matches_the_shop_dollar_and_stays_on_descriptions() -> None:
    rows = rows_from_payload(
        [
            {"ma": "Z01", "descriptionEn": "Flat $8"},
            {"ma": "Z02", "descriptionEn": "FLAT $1"},
            {"ma": "Z03", "descriptionEn": "fLat $0"},
            {"ma": "Z04", "descriptionEn": "Flat $6"},
            {"ma": "Z05", "descriptionEn": "Flat $6.95"},
            {"ma": "Z06", "titleEn": "2-4 weeks"},
            {"ma": "Z07", "colors": [{"name": "flat $8", "note": "flat $8"}]},
            {"ma": "Z08", "titleEn": "on", "titleVn": "hand"},
        ]
    )
    assert _view(flag_customer_copy(rows)) == [
        ("Z01", "descriptionEn", None, "invented_lead", "invented lead", "Flat $8"),
        ("Z02", "descriptionEn", None, "invented_lead", "invented lead", "FLAT $1"),
        ("Z03", "descriptionEn", None, "invented_lead", "invented lead", "fLat $0"),
        ("Z04", "descriptionEn", None, "invented_lead", "invented lead", "Flat $6"),
        ("Z05", "descriptionEn", None, "invented_lead", "invented lead", "Flat $6"),
        ("Z08", "joinedCopy", None, "stock_voice", "on hand", "on hand"),
    ]


def test_a_split_phrase_keeps_the_spacing_the_shop_keeps() -> None:
    rows = rows_from_payload(
        [
            {"ma": "Z10", "titleEn": "on", "titleVn": " hand"},
            {"ma": "Z11", "titleEn": "on ", "titleVn": "hand"},
            {"ma": "Z12", "titleEn": "In", "titleVn": " stock"},
            {"ma": "Z13", "titleEn": "In ", "titleVn": "stock"},
            {"ma": "Z14", "titleEn": "In\u00a0", "titleVn": "stock"},
            {"ma": "Z15", "titleEn": "on\t", "titleVn": "hand"},
            {"ma": "Z16", "titleEn": "we", "titleVn": " order"},
            {"ma": "Z17", "titleEn": "we ", "titleVn": "order"},
            {"ma": "Z18", "titleEn": "flat", "titleVn": " rate"},
            {"ma": "Z19", "titleEn": "unique", "titleVn": " piece"},
            {"ma": "Z20", "titleEn": "unique", "titleVn": " pieces"},
            {"ma": "Z21", "titleEn": "not", "titleVn": " reserved"},
            {"ma": "Z22", "titleEn": "size Á", "titleVn": " châu"},
            {"ma": "Z23", "titleEn": "đang", "titleVn": " có"},
            {"ma": "Z24", "titleEn": "A listed\t", "titleVn": "x"},
            {"ma": "Z25", "titleEn": "A listed\u0085", "titleVn": "x"},
            {"ma": "Z26", "titleEn": "A listed\u001c", "titleVn": "x"},
            {"ma": "Z27", "titleEn": "A listed\u001d", "titleVn": "x"},
            {"ma": "Z28", "titleEn": "A listed\u001e", "titleVn": "x"},
            {"ma": "Z29", "titleEn": "A listed\u001f", "titleVn": "x"},
            {"ma": "Z30", "titleEn": "Status:\u0085", "titleVn": "x"},
            {"ma": "Z31", "titleEn": "Status:\u001c", "titleVn": "x"},
            {"ma": "Z32", "titleEn": "Status:\u001d", "titleVn": "x"},
            {"ma": "Z33", "titleEn": "Status:\u001e", "titleVn": "x"},
            {"ma": "Z34", "titleEn": "Status:\u001f", "titleVn": "x"},
            {"ma": "Z35", "titleEn": "on\u0085", "titleVn": "hand"},
            {"ma": "Z36", "titleEn": "on", "titleVn": "\u0085hand"},
            {"ma": "Z37", "titleEn": "on\u001c", "titleVn": "hand"},
            {"ma": "Z38", "titleEn": "on\u001d", "titleVn": "hand"},
            {"ma": "Z39", "titleEn": "on\u001e", "titleVn": "hand"},
            {"ma": "Z40", "titleEn": "on\u001f", "titleVn": "hand"},
            {"ma": "Z41", "titleEn": "on", "titleVn": "\u001chand"},
            {"ma": "Z42", "descriptionEn": "2-4\u0085", "descriptionVn": "weeks"},
            {"ma": "Z43", "descriptionEn": "2-4\u001c", "descriptionVn": "weeks"},
            {"ma": "Z44", "descriptionEn": "2-4\u001d", "descriptionVn": "weeks"},
            {"ma": "Z45", "descriptionEn": "2-4\u001e", "descriptionVn": "weeks"},
            {"ma": "Z46", "descriptionEn": "2-4\u001f", "descriptionVn": "weeks"},
            {"ma": "Z47", "descriptionEn": "2-4", "descriptionVn": "\u0085weeks"},
            {"ma": "Z48", "descriptionEn": "2-4", "descriptionVn": "\u001cweeks"},
            {"ma": "Z49", "descriptionEn": "2-4", "descriptionVn": "\u001dweeks"},
            {"ma": "Z50", "descriptionEn": "2-4", "descriptionVn": "\u001eweeks"},
            {"ma": "Z51", "descriptionEn": "2-4", "descriptionVn": "\u001fweeks"},
        ]
    )
    assert flag_customer_copy(rows) == []


def test_invented_lead_keeps_the_separator_the_shop_reads() -> None:
    rows = rows_from_payload(
        [
            {"ma": "Z52", "descriptionEn": "2-4\t", "descriptionVn": "weeks"},
            {"ma": "Z53", "descriptionEn": "2-4 ", "descriptionVn": "weeks"},
            {"ma": "Z54", "descriptionEn": "2-4", "descriptionVn": " tuần"},
        ]
    )
    assert [flag.stored for flag in flag_customer_copy(rows)] == [
        "2-4\t\nweek",
        "2-4 \nweek",
        "2-4\n tuần",
    ]


def test_javascript_word_edges_match_the_shop() -> None:
    hit = rows_from_payload(
        [
            {
                "ma": "Z94",
                "descriptionEn": "đHold. Holdở. ởon hand. on handở. Hold２.",
            }
        ]
    )
    flags = flag_customer_copy(hit)
    assert [flag.stored for flag in flags] == ["Hold", "Hold", "Hold", "on hand", "on hand"]
    quiet = rows_from_payload(
        [
            {
                "ma": "Z95",
                "descriptionEn": "Hold2. ın stock. In ſtock. flat $６. flat $٨.",
                "descriptionVn": "Status:\u0085live. 2-4\u0085weeks.",
            }
        ]
    )
    assert flag_customer_copy(quiet) == []
    folded = rows_from_payload(
        [{"ma": "Z96", "descriptionVn": "ĐANG CÓ. 2–4 TUẦN."}]
    )
    assert [flag.stored for flag in flag_customer_copy(folded)] == ["ĐANG CÓ", "2–4 TUẦN"]


def test_invented_lead_keeps_the_en_dash_and_does_not_round_a_price() -> None:
    promise = "2\u20134 tuần"
    rows = rows_from_payload(
        [
            {
                "ma": "Z90",
                "priceUsd": 25,
                "status": "hold",
                "descriptionEn": f"Window {promise}.",
            }
        ]
    )
    flags = flag_customer_copy(rows)
    assert _view(flags) == [
        ("Z90", "descriptionEn", None, "invented_lead", "invented lead", promise),
    ]
    assert rows[0].price_usd == 25
    assert rows[0].status == "hold"
    assert rows[0].fields[0].text == f"Window {promise}."


def test_supplier_host_is_not_copied_into_the_flag() -> None:
    host = "taobao" + ".com/item"
    payload = {
        "products": [
            {
                "ma": "Z91",
                "priceUsd": 40,
                "descriptionEn": f"See {host} today",
            }
        ]
    }
    rows = rows_from_payload(payload)
    flags = flag_customer_copy(rows)
    assert _view(flags) == [
        ("Z91", "descriptionEn", None, "ops_voice", "Taobao", "taobao"),
    ]
    text = json.dumps(report_json(rows, flags), ensure_ascii=False)
    assert host not in text
    assert "today" not in text
    assert payload["products"][0]["descriptionEn"] == f"See {host} today"


def test_on_hand_fulfillment_still_flags_customer_stock_words() -> None:
    rows = rows_from_payload(
        [
            {
                "ma": "K06",
                "status": "hold",
                "fulfillment": "on_hand",
                "descriptionEn": "Ready ON HAND for pickup.",
            }
        ]
    )
    flags = flag_customer_copy(rows)
    assert _view(flags) == [
        ("K06", "descriptionEn", None, "stock_voice", "on hand", "ON HAND"),
    ]
    assert rows[0].status == "hold"
    assert "fulfillment" not in report_json(rows, flags)["rows"][0]


def test_nonfinite_price_is_refused_and_not_rewritten() -> None:
    payload = [{"ma": "A01", "priceUsd": float("nan"), "descriptionEn": "Soft knit."}]
    try:
        rows_from_payload(payload)
    except ValueError as error:
        assert "finite" in str(error)
    else:
        raise AssertionError("a non-finite price was accepted")
    assert isinstance(payload[0]["priceUsd"], float)
    assert math.isnan(payload[0]["priceUsd"])


def test_bad_shapes_are_refused() -> None:
    samples = [
        [{"ma": "A01", "descriptionEn": 1}],
        [{"ma": "A01", "colors": {"name": "Pink"}}],
        [{"ma": "A01", "colors": [{"name": 1}]}],
        [{"ma": "A01", "priceUsd": True}],
        [{"ma": " ", "descriptionEn": ""}],
        [{"ma": "A01", "status": 1}],
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
        CatalogRow(
            "K06",
            (CopyField("descriptionEn", None, "Ready on hand."),),
            None,
            True,
            "hold",
        ),
        CatalogRow("V05", (), None, False, "hold"),
        CatalogRow(
            "S06",
            (CopyField("descriptionEn", None, "Soft knit."),),
            25,
            True,
            "available",
        ),
    ]
    flags = flag_customer_copy(rows)
    assert [flag.ma for flag in flags] == ["K06"]
    assert flags[0].stored == "on hand"
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
        (flag["ma"], flag["field"], flag["index"], flag["kind"], flag["label"], flag["stored"])
        for flag in report["flags"]
    ] == EXPECTED
    assert report["rows"][0]["priceUsd"] == 25
    assert report["rows"][1]["status"] == "hold"
    assert report["rows"][6]["status"] == "hold"
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
                "descriptionEn": "Soft knit.",
                "colors": [{"name": "Xanh", "note": ""}],
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
    assert "Xanh" not in ran.stdout
    assert "Soft knit" not in ran.stdout
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
    bad_raw = '{"products":[{"ma":"S06","priceUsd":25,"descriptionEn":1}]}\n'
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


def test_script_is_read_only_and_does_not_rewrite_copy() -> None:
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
