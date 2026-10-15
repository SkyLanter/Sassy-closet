"""Restock notes on fixtures. No live Blob, intake, Meta, or held write."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from held_policy import load_held_policy
from restock_note import main, note_from_json, render_json, render_note, write_note

ROOT = Path(__file__).resolve().parents[2]
HELD = ROOT / "data" / "held.json"
CATALOG = ROOT / "sassy-closet-shop" / "data" / "products.json"
HELD_BYTES = HELD.read_bytes()
CATALOG_BYTES = CATALOG.read_bytes()
SOURCE = (ROOT / "scripts" / "restock_note.py").read_text(encoding="utf-8")


def _payload() -> dict[str, object]:
    return {
        "catalog": {
            "products": [
                {
                    "ma": "s06",
                    "status": "sold",
                    "priceUsd": 25,
                    "titleEn": "Locked dress",
                    "sourceLink": "https://example.test/s06",
                },
                {
                    "ma": "A02",
                    "status": "sold",
                    "priceUsd": 28,
                    "titleEn": "Cardigan",
                    "sourceLink": "https://example.test/a02",
                },
                {"ma": "A07", "status": "available", "priceUsd": 26, "titleEn": "Live top"},
                {"ma": "P05", "status": "hold", "priceUsd": None, "titleEn": "Paused look"},
                {"ma": "K06", "status": "sold", "priceUsd": 48, "titleEn": "Incomplete"},
                {"ma": "V05", "status": "available", "priceUsd": 30, "titleEn": "Also held"},
                {"ma": "Z09", "status": "sold", "price_usd": "21", "titleEn": "Never"},
            ]
        },
        "held": {"heldIncomplete": ["K06", "V05"], "neverList": ["Z09"]},
    }


def test_sold_list_keeps_stored_prices_and_holds_held_mas() -> None:
    payload = _payload()
    original = json.dumps(payload)
    note = note_from_json(payload)
    assert json.dumps(payload) == original
    assert [piece.ma for piece in note.sold] == ["A02", "K06", "S06", "Z09"]
    restock = [piece for piece in note.sold if piece.restock]
    assert [(piece.ma, piece.price_usd) for piece in restock] == [("A02", "28"), ("S06", "25")]
    held_sold = next(piece for piece in note.sold if piece.ma == "K06")
    assert held_sold.restock is False
    assert held_sold.reason == "held"
    assert held_sold.price_usd == "48"
    unlist = next(piece for piece in note.sold if piece.ma == "Z09")
    assert unlist.restock is False
    assert unlist.reason == "never-list"
    assert [piece.ma for piece in note.sold if piece.ma in {"A07", "P05", "V05"}] == []
    assert [(stay.ma, stay.status) for stay in note.stays] == [
        ("K06", "sold"),
        ("V05", "available"),
        ("Z09", "sold"),
    ]
    assert note.s06_usd == "25"
    text = render_note(note)
    assert "A02 — Cardigan — $28" in text
    assert "S06 — Locked dress — $25" in text
    assert "K06 — stays held, not a restock" in text
    assert "Z09 — stays unlist, not a restock" in text
    assert "V05 — status available — stays held, not a restock" in text
    assert "Held mãs stay held." in text
    assert "S06 stays $25." in text
    assert "does not post to Meta" in text
    assert "does not mark anything sold or available" in text
    assert "$48" not in text
    assert "$26" not in text
    assert "$30" not in text
    assert "example.test" not in text
    assert "http" not in text.lower()
    body = render_json(note)
    assert body["writes"] == []
    assert body["restockCount"] == 2
    assert body["s06Usd"] == "25"
    assert HELD.read_bytes() == HELD_BYTES
    assert CATALOG.read_bytes() == CATALOG_BYTES


def test_s06_other_than_25_is_refused_and_the_row_stays() -> None:
    payload = _payload()
    products = payload["catalog"]["products"]
    assert isinstance(products, list)
    products[0]["priceUsd"] = 24
    original = json.dumps(payload)
    with pytest.raises(ValueError, match=r"S06 stays \$25"):
        note_from_json(payload)
    assert json.dumps(payload) == original
    assert products[0]["priceUsd"] == 24
    assert products[0]["status"] == "sold"


def test_missing_s06_writes_no_price() -> None:
    payload = _payload()
    products = payload["catalog"]["products"]
    assert isinstance(products, list)
    payload["catalog"]["products"] = [row for row in products if str(row["ma"]).upper() != "S06"]
    note = note_from_json(payload)
    assert note.s06_usd is None
    assert "S06" not in [piece.ma for piece in note.sold]
    assert "S06 was not in this catalog. No price was written." in render_note(note)
    assert "S06 stays $25." not in render_note(note)


def test_sold_without_a_price_is_not_invented() -> None:
    payload = _payload()
    products = payload["catalog"]["products"]
    assert isinstance(products, list)
    products[1].pop("priceUsd")
    note = note_from_json(payload)
    cardigan = next(piece for piece in note.sold if piece.ma == "A02")
    assert cardigan.price_usd is None
    assert cardigan.restock is True
    assert "A02 — Cardigan — no stored price" in render_note(note)


def test_bad_status_and_duplicate_do_not_build_a_note() -> None:
    duplicate = _payload()
    products = duplicate["catalog"]["products"]
    assert isinstance(products, list)
    products.append({"ma": "A02", "status": "available", "priceUsd": 10})
    with pytest.raises(ValueError, match="duplicate mã A02"):
        note_from_json(duplicate)
    bad = _payload()
    bad_products = bad["catalog"]["products"]
    assert isinstance(bad_products, list)
    bad_products[1]["status"] = "Sold"
    with pytest.raises(ValueError, match="status must be available, hold, or sold"):
        note_from_json(bad)


def test_real_held_file_stays_off_the_restock_list() -> None:
    before = HELD.read_bytes()
    policy = load_held_policy()
    note = note_from_json(
        {
            "products": [
                {"ma": "A02", "status": "sold", "priceUsd": 28, "titleEn": "Cardigan"},
                {"ma": "S06", "status": "available", "priceUsd": 25, "titleEn": "Locked dress"},
            ]
        }
    )
    assert note.s06_usd == "25"
    assert [piece.ma for piece in note.sold if piece.restock] == ["A02"]
    assert [stay.ma for stay in note.stays] == list(policy.held)
    assert all(stay.detail == "not in this catalog — stays held" for stay in note.stays)
    restock = {piece.ma for piece in note.sold if piece.restock}
    assert restock.isdisjoint(policy.held)
    assert restock.isdisjoint(policy.never_list)
    assert "K06" in {stay.ma for stay in note.stays}
    assert "V05" in {stay.ma for stay in note.stays}
    assert HELD.read_bytes() == before
    assert CATALOG.read_bytes() == CATALOG_BYTES


def test_note_refuses_catalog_held_and_shop_paths(tmp_path: Path) -> None:
    note = note_from_json(_payload())
    fixture = tmp_path / "catalog.json"
    fixture.write_text("{}\n", encoding="utf-8")
    before_held = HELD.read_bytes()
    with pytest.raises(ValueError, match="refusing to write"):
        write_note(note, HELD, source=fixture)
    assert HELD.read_bytes() == before_held
    shop_note = ROOT / "sassy-closet-shop" / "restock-note.md"
    with pytest.raises(ValueError, match="shop app or data"):
        write_note(note, shop_note, source=fixture)
    assert not shop_note.exists()
    data_note = ROOT / "data" / "restock-note.md"
    with pytest.raises(ValueError, match="shop app or data"):
        write_note(note, data_note, source=fixture)
    assert not data_note.exists()
    named = tmp_path / "products.json"
    with pytest.raises(ValueError, match="refusing to write"):
        write_note(note, named, source=fixture)
    assert not named.exists()
    plain = tmp_path / "note.txt"
    with pytest.raises(ValueError, match="markdown"):
        write_note(note, plain, source=fixture)
    assert not plain.exists()
    with pytest.raises(ValueError, match="overwrite the catalog fixture"):
        write_note(note, fixture, source=fixture)


def test_cli_writes_the_note_and_leaves_fixture_bytes(tmp_path: Path) -> None:
    fixture = tmp_path / "catalog.json"
    raw = json.dumps(_payload())
    fixture.write_text(raw, encoding="utf-8")
    note_path = tmp_path / "restock-note.md"
    before_held = HELD.read_bytes()
    before_catalog = CATALOG.read_bytes()
    ran = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "restock_note.py"),
            "--fixture",
            str(fixture),
            "--note",
            str(note_path),
            "--json",
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert ran.returncode == 0, ran.stderr
    saved = json.loads(ran.stdout)
    assert saved["writes"] == []
    assert saved["s06Usd"] == "25"
    assert [row["ma"] for row in saved["sold"] if row["restock"]] == ["A02", "S06"]
    assert saved["sold"][0]["priceUsd"] == "28"
    text = note_path.read_text(encoding="utf-8")
    assert "does not mark anything sold or available" in text
    assert "does not post to Meta" in text
    assert "K06 — stays held, not a restock" in text
    assert fixture.read_text(encoding="utf-8") == raw
    assert HELD.read_bytes() == before_held
    assert CATALOG.read_bytes() == before_catalog


def test_cli_s06_mismatch_writes_nothing(tmp_path: Path) -> None:
    payload = _payload()
    products = payload["catalog"]["products"]
    assert isinstance(products, list)
    products[0]["priceUsd"] = 26
    fixture = tmp_path / "catalog.json"
    raw = json.dumps(payload)
    fixture.write_text(raw, encoding="utf-8")
    note_path = tmp_path / "nested" / "restock-note.md"
    note_path.parent.mkdir()
    note_path.write_text("old\n", encoding="utf-8")
    ran = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "restock_note.py"),
            "--fixture",
            str(fixture),
            "--note",
            str(note_path),
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert ran.returncode == 2
    assert "S06 stays $25" in ran.stderr
    assert note_path.read_text(encoding="utf-8") == "old\n"
    assert fixture.read_text(encoding="utf-8") == raw
    assert HELD.read_bytes() == HELD_BYTES
    assert CATALOG.read_bytes() == CATALOG_BYTES


def test_cli_refuses_a_url_and_a_shop_note(tmp_path: Path) -> None:
    note_path = tmp_path / "restock-note.md"
    ran = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "restock_note.py"),
            "--fixture",
            "https://example.test/catalog.v1.json",
            "--note",
            str(note_path),
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert ran.returncode == 2
    assert "local fixture" in ran.stderr
    assert not note_path.exists()
    assert main(["--fixture", str(HELD), "--note", str(ROOT / "data" / "restock-note.md")]) == 2
    assert not (ROOT / "data" / "restock-note.md").exists()
    assert HELD.read_bytes() == HELD_BYTES


def test_source_does_not_call_live_shops() -> None:
    lowered = SOURCE.lower()
    assert "tesla" not in lowered
    assert "urllib" not in SOURCE
    assert "import requests" not in SOURCE
    assert "vercel" not in lowered
    assert "blob.vercel" not in lowered
    assert "graph.facebook" not in lowered
    assert "blob_read_write" not in lowered
    assert "Q02" not in SOURCE
    assert '["status"] = "available"' not in SOURCE
    assert '["status"] = "sold"' not in SOURCE
    assert '["priceUsd"] =' not in SOURCE
    assert "data/held.json" in SOURCE
