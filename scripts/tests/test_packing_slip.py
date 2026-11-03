"""Packing-slip preview from a fixture order. No order, Blob, intake, or held write."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from held_policy import HeldPolicy, load_held_policy
from packing_slip import main, preview_order, render_json, render_page, render_text, write_page

ROOT = Path(__file__).resolve().parents[2]
HELD = ROOT / "data" / "held.json"
SOURCE = (ROOT / "scripts" / "packing_slip.py").read_text(encoding="utf-8")


def _order() -> dict[str, object]:
    lines: list[dict[str, object]] = [
        {"ma": "S06", "title": "Satin skirt", "priceUsd": 25},
    ]
    for code in load_held_policy().held:
        lines.append({"ma": code, "title": f"Held {code}", "priceUsd": 40})
    lines.extend(
        [
            {"ma": "A01", "title": "Ivory blouse", "priceUsd": 28},
            {"ma": "Z99", "title": "Unpriced piece", "landedUsd": "33.75"},
        ]
    )
    return {"orderId": "FIX-S06", "lines": lines}


def test_s06_stays_25_and_held_mas_are_omitted() -> None:
    payload = _order()
    before = json.dumps(payload)
    slip = preview_order(payload)
    assert payload["lines"][0]["priceUsd"] == 25
    assert json.dumps(payload) == before
    assert [(line.ma, line.title, line.price_usd) for line in slip.lines] == [
        ("S06", "Satin skirt", "25"),
        ("A01", "Ivory blouse", "28"),
    ]
    held = {item.ma for item in slip.omitted if item.reason == "held"}
    assert held == set(load_held_policy().held)
    assert any(item.ma == "Z99" and item.reason == "no-price" for item in slip.omitted)
    text = render_text(slip)
    assert "Packing slip FIX-S06" in text
    assert "S06  Satin skirt  $25" in text
    assert "A01  Ivory blouse  $28" in text
    assert "$40" not in text
    assert "33.75" not in text
    assert "45" not in text
    assert "Z99" not in text
    for code in load_held_policy().held:
        assert code not in text
    page = render_page(slip)
    assert "<td>S06</td><td>Satin skirt</td><td>$25</td>" in page
    assert "<td>A01</td><td>Ivory blouse</td><td>$28</td>" in page
    assert "No order is written." in page
    for code in load_held_policy().held:
        assert code not in page
    body = render_json(slip)
    assert body["lines"] == [
        {"ma": "S06", "title": "Satin skirt", "priceUsd": "25"},
        {"ma": "A01", "title": "Ivory blouse", "priceUsd": "28"},
    ]
    assert "Z99" not in json.dumps(body["lines"])


def test_s06_string_dollar_stays_25_and_another_dollar_is_refused() -> None:
    same = {"lines": [{"ma": "s06", "title": "Satin skirt", "priceUsd": "25.00"}]}
    slip = preview_order(same)
    assert slip.lines[0].ma == "S06"
    assert slip.lines[0].price_usd == "25"
    assert same["lines"][0]["priceUsd"] == "25.00"
    other = {"lines": [{"ma": "S06", "title": "Satin skirt", "priceUsd": 30}]}
    with pytest.raises(ValueError, match=r"S06 stays \$25"):
        preview_order(other)
    assert other["lines"][0]["priceUsd"] == 30


def test_missing_s06_price_is_not_filled_in() -> None:
    payload = {"lines": [{"ma": "S06", "title": "Satin skirt"}]}
    slip = preview_order(payload)
    assert slip.lines == ()
    assert slip.omitted[0].reason == "no-price"
    assert "$25" not in render_text(slip)
    assert "priceUsd" not in payload["lines"][0]


def test_never_list_is_omitted_without_writing_held() -> None:
    before = HELD.read_bytes()
    policy = HeldPolicy(held=("K06",), never_list=("Z98",))
    payload = {
        "lines": [
            {"ma": "S06", "title": "Satin skirt", "priceUsd": 25},
            {"ma": "Z98", "title": "Skipped piece", "priceUsd": 30},
            {"ma": "K06", "title": "Held knit", "priceUsd": 41},
        ]
    }
    slip = preview_order(payload, policy)
    assert [line.ma for line in slip.lines] == ["S06"]
    assert slip.lines[0].price_usd == "25"
    assert [(item.ma, item.reason) for item in slip.omitted] == [
        ("Z98", "never-list"),
        ("K06", "held"),
    ]
    text = render_text(slip)
    assert "Z98" not in text
    assert "K06" not in text
    assert "$30" not in text
    assert "$41" not in text
    assert HELD.read_bytes() == before
    assert payload["lines"][0]["priceUsd"] == 25


def test_page_refuses_orders_held_and_shop_paths(tmp_path: Path) -> None:
    slip = preview_order(_order())
    before = HELD.read_bytes()
    with pytest.raises(ValueError, match="refusing to write"):
        write_page(slip, HELD)
    assert HELD.read_bytes() == before
    shop_page = ROOT / "sassy-closet-shop" / "slip.html"
    with pytest.raises(ValueError, match="sell catalog"):
        write_page(slip, shop_page)
    assert not shop_page.exists()
    orders = tmp_path / "orders.json"
    with pytest.raises(ValueError, match="refusing to write"):
        write_page(slip, orders)
    assert not orders.exists()
    live = slip.__class__(**{**slip.__dict__, "local": False})
    page = tmp_path / "slip.html"
    with pytest.raises(ValueError, match="fixture order"):
        write_page(live, page)
    assert not page.exists()


def test_cli_preview_writes_only_the_local_page(tmp_path: Path) -> None:
    payload = _order()
    fixture = tmp_path / "order.json"
    original = json.dumps(payload)
    fixture.write_text(original, encoding="utf-8")
    page = tmp_path / "slip.html"
    before = HELD.read_bytes()
    ran = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "packing_slip.py"),
            "--fixture",
            str(fixture),
            "--page",
            str(page),
            "--json",
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert ran.returncode == 0, ran.stderr
    saved = json.loads(ran.stdout)
    assert saved["lines"][0] == {"ma": "S06", "title": "Satin skirt", "priceUsd": "25"}
    assert saved["local"] is True
    held_codes = set(load_held_policy().held)
    assert held_codes.isdisjoint({line["ma"] for line in saved["lines"]})
    assert page.is_file()
    html = page.read_text(encoding="utf-8")
    assert "S06" in html and "$25" in html
    assert "No order is written." in html
    lowered = html.lower()
    assert "<script" not in lowered
    assert "fetch(" not in lowered
    assert "http" not in lowered
    for code in held_codes:
        assert code not in html
    assert fixture.read_text(encoding="utf-8") == original
    assert HELD.read_bytes() == before
    assert not (ROOT / "sassy-closet-shop" / "catalog.v1.json").exists()


def test_cli_refuses_other_s06_dollar_without_writing(tmp_path: Path) -> None:
    fixture = tmp_path / "order.json"
    fixture.write_text(
        json.dumps({"lines": [{"ma": "S06", "title": "Satin skirt", "priceUsd": 30}]}),
        encoding="utf-8",
    )
    page = tmp_path / "slip.html"
    before = HELD.read_bytes()
    ran = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "packing_slip.py"),
            "--fixture",
            str(fixture),
            "--page",
            str(page),
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert ran.returncode == 2
    assert "S06 stays $25" in ran.stderr
    assert not page.exists()
    assert '"priceUsd": 30' in fixture.read_text(encoding="utf-8")
    assert HELD.read_bytes() == before
    assert main(["--page", str(ROOT / "data" / "slip.html"), "--fixture", str(fixture)]) == 2
    assert not (ROOT / "data" / "slip.html").exists()


def test_source_does_not_invent_prices_or_write_shop_data() -> None:
    lowered = SOURCE.lower()
    assert "tesla" not in lowered
    assert "vercel" not in lowered
    assert "listing_quote" not in SOURCE
    assert "append_order" not in SOURCE
    assert "catalog.v1.json" in SOURCE
    assert "blob_read_write" not in lowered
    assert "urllib" not in lowered
    assert "import requests" not in lowered
    assert "data/held.json" in SOURCE
    assert "priceusd" in lowered
