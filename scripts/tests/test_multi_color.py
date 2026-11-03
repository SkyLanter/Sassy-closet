"""Multi-color catalog list from a fixture. No catalog or held.json writes."""

from __future__ import annotations

import copy
import json
import subprocess
import sys
from pathlib import Path

from multi_color import list_multi_color

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "multi_color.py"
FIXTURE = ROOT / "scripts" / "tests" / "fixtures" / "multi_color_catalog.json"
HELD = ROOT / "data" / "held.json"
PRODUCTS = ROOT / "sassy-closet-shop" / "data" / "products.json"


def _document() -> dict:
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def test_lists_only_mas_with_more_than_one_stored_color() -> None:
    listed = list_multi_color(_document())
    assert [row.ma for row in listed] == ["S06", "K06", "Z99", "B01", "D01"]
    by_ma = {row.ma: row for row in listed}
    assert [(color.id, color.name) for color in by_ma["S06"].colors] == [
        ("cs0600", "Kem"),
        ("cs0601", "Xanh"),
    ]
    assert [(color.id, color.name) for color in by_ma["B01"].colors] == [
        ("", "Pink"),
        ("", "Blue"),
    ]
    assert [(color.id, color.name) for color in by_ma["D01"].colors] == [
        ("cd0100", "Pink"),
        ("cd0101", "Pink"),
    ]
    omitted = {"A07", "S01", "P02", "H01", "A02", "O04", "J01", "Q01", "AO001"}
    assert omitted.isdisjoint(by_ma)


def test_does_not_invent_colors_from_hex_images_or_commas() -> None:
    listed = list_multi_color(_document())
    z99 = next(row for row in listed if row.ma == "Z99")
    assert [color.name for color in z99.colors] == ["", ""]
    assert [color.id for color in z99.colors] == ["cz9900", "cz9901"]
    rendered = json.dumps([row.as_json() for row in listed], ensure_ascii=False)
    assert "Ivory" not in rendered
    assert "Black" not in rendered
    assert "Kem, Xanh" not in rendered
    assert "Chấm bi" not in rendered
    assert "kem" not in rendered


def test_s06_stays_25_and_held_status_stays_hold() -> None:
    document = _document()
    original = copy.deepcopy(document)
    listed = list_multi_color(document)
    assert document == original
    s06 = next(row for row in listed if row.ma == "S06")
    assert s06.price_usd == 25
    assert s06.status == "available"
    assert s06.as_json()["priceUsd"] == 25
    k06 = next(row for row in listed if row.ma == "K06")
    assert k06.status == "hold"
    assert k06.price_usd is None
    assert [(color.name) for color in k06.colors] == ["Đen", "Kem"]
    stored_s06 = next(row for row in document["products"] if row["ma"] == "S06")
    stored_k06 = next(row for row in document["products"] if row["ma"] == "K06")
    assert stored_s06["priceUsd"] == 25
    assert stored_k06["status"] == "hold"
    assert stored_k06["priceUsd"] is None


def test_cli_reads_the_fixture_and_writes_nothing() -> None:
    before_fixture = FIXTURE.read_bytes()
    before_held = HELD.read_bytes()
    before_products = PRODUCTS.read_bytes()
    ran = subprocess.run(
        [sys.executable, str(SCRIPT), "--catalog", str(FIXTURE)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert ran.returncode == 0, ran.stderr
    payload = json.loads(ran.stdout)
    assert [row["ma"] for row in payload] == ["S06", "K06", "Z99", "B01", "D01"]
    assert payload[0]["priceUsd"] == 25
    assert payload[0]["status"] == "available"
    assert payload[1]["ma"] == "K06"
    assert payload[1]["status"] == "hold"
    assert payload[1]["priceUsd"] is None
    assert payload[2]["colors"] == [
        {"id": "cz9900", "name": ""},
        {"id": "cz9901", "name": ""},
    ]
    assert "Ivory" not in ran.stdout
    assert "Black" not in ran.stdout
    assert FIXTURE.read_bytes() == before_fixture
    assert HELD.read_bytes() == before_held
    assert PRODUCTS.read_bytes() == before_products


def test_cli_can_read_held_json_without_changing_it() -> None:
    before_held = HELD.read_bytes()
    ran = subprocess.run(
        [sys.executable, str(SCRIPT), "--catalog", str(HELD)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert ran.returncode == 0, ran.stderr
    assert json.loads(ran.stdout) == []
    assert HELD.read_bytes() == before_held


def test_cli_rejects_an_unreadable_catalog(tmp_path: Path) -> None:
    missing = subprocess.run(
        [sys.executable, str(SCRIPT), "--catalog", str(tmp_path / "missing.json")],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert missing.returncode == 2
    assert missing.stdout == ""
    assert "Cannot read catalog" in missing.stderr

    bad = tmp_path / "bad.json"
    bad.write_text("{", encoding="utf-8")
    rejected = subprocess.run(
        [sys.executable, str(SCRIPT), "--catalog", str(bad)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert rejected.returncode == 2
    assert rejected.stdout == ""

    listed = tmp_path / "list.json"
    listed.write_text("[]", encoding="utf-8")
    not_object = subprocess.run(
        [sys.executable, str(SCRIPT), "--catalog", str(listed)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert not_object.returncode == 2
    assert "JSON object" in not_object.stderr
