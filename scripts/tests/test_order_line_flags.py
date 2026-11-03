"""Fixture-order duplicate mã flags. Lines stay separate. No price is invented."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from held_policy import HeldPolicy, load_held_policy
from order_line_flags import flag_order, main, render_json, render_text, write_report

ROOT = Path(__file__).resolve().parents[2]
HELD = ROOT / "data" / "held.json"
PRODUCTS = ROOT / "sassy-closet-shop" / "data" / "products.json"
SOURCE = (ROOT / "scripts" / "order_line_flags.py").read_text(encoding="utf-8")


def _order() -> dict[str, object]:
    lines: list[dict[str, object]] = [
        {"ma": "S06", "title": "Satin skirt", "priceUsd": 25},
        {"ma": "s06", "title": "Satin skirt", "priceUsd": "25.00"},
    ]
    for code in load_held_policy().held:
        lines.append({"ma": code, "title": f"Held {code}", "priceUsd": 40})
    lines.append({"ma": "K06", "title": "Held knit again", "priceUsd": 48})
    lines.extend(
        [
            {"ma": "A01", "title": "Ivory blouse", "priceUsd": 28},
            {"ma": "A01", "title": "Ivory blouse", "priceUsd": 30},
            {"ma": "Z99", "title": "Unpriced piece", "landedUsd": "33.75"},
        ]
    )
    return {"orderId": "FIX-DUP", "lines": lines}


def test_repeated_mas_are_flagged_and_lines_stay_separate() -> None:
    payload = _order()
    before = json.dumps(payload)
    held_before = HELD.read_bytes()
    report = flag_order(payload)
    assert json.dumps(payload) == before
    assert payload["lines"][0]["priceUsd"] == 25
    assert payload["lines"][1]["priceUsd"] == "25.00"
    assert HELD.read_bytes() == held_before
    assert report.merged is False
    assert [(line.ma, line.title, line.price_usd) for line in report.lines] == [
        ("S06", "Satin skirt", "25"),
        ("S06", "Satin skirt", "25"),
        ("A01", "Ivory blouse", "28"),
        ("A01", "Ivory blouse", "30"),
    ]
    by_ma = {flag.ma: flag for flag in report.flags}
    assert set(by_ma) == {"S06", "A01"}
    assert by_ma["S06"].kind == "repeated"
    assert by_ma["S06"].count == 2
    assert by_ma["S06"].on_order == 2
    assert by_ma["S06"].prices == ("25", "25")
    assert by_ma["A01"].prices == ("28", "30")
    assert by_ma["A01"].on_order == 2
    held = [item for item in report.omitted if item.reason == "held"]
    assert [item.ma for item in held].count("K06") == 2
    assert {item.ma for item in held} == set(load_held_policy().held)
    assert any(item.ma == "Z99" and item.reason == "no-price" for item in report.omitted)
    text = render_text(report)
    on_order = text.split("## Flags", 1)[0]
    assert on_order.count("S06 — Satin skirt — $25") == 2
    assert "A01 — Ivory blouse — $28" in on_order
    assert "A01 — Ivory blouse — $30" in on_order
    assert "$50" not in text
    assert "$58" not in text
    assert "$29" not in text
    assert "$40" not in text
    assert "$48" not in text
    assert "33.75" not in text
    assert "Lines were not merged." in text
    assert "S06 stays $25." in text
    for code in load_held_policy().held:
        assert code not in on_order
    assert "Z99" not in on_order
    body = render_json(report)
    assert body["merged"] is False
    assert body["lines"][0] == {"ma": "S06", "title": "Satin skirt", "priceUsd": "25"}
    assert body["lines"][1]["priceUsd"] == "25"
    assert body["flags"][0]["prices"] == ["25", "25"]
    assert "Z99" not in json.dumps(body["lines"])
    assert "K06" not in json.dumps(body["lines"])


def test_missing_price_is_not_invented_or_merged() -> None:
    payload = {
        "lines": [
            {"ma": "S06", "title": "Satin skirt", "priceUsd": 25},
            {"ma": "S06", "title": "Satin skirt"},
        ]
    }
    before = json.dumps(payload)
    report = flag_order(payload)
    assert json.dumps(payload) == before
    assert "priceUsd" not in payload["lines"][1]
    assert [(line.ma, line.price_usd) for line in report.lines] == [("S06", "25")]
    assert len(report.flags) == 1
    flag = report.flags[0]
    assert flag.ma == "S06"
    assert flag.count == 2
    assert flag.on_order == 1
    assert flag.prices == ("25", None)
    assert report.omitted[0].reason == "no-price"
    text = render_text(report)
    assert "Prices stay $25, no price." in text
    assert text.split("## Flags", 1)[0].count("S06 — Satin skirt — $25") == 1
    body = render_json(report)
    assert body["flags"][0]["prices"] == ["25", None]
    assert body["merged"] is False


def test_s06_other_dollar_is_refused_and_not_rewritten() -> None:
    other = {
        "lines": [
            {"ma": "S06", "title": "Satin skirt", "priceUsd": 25},
            {"ma": "S06", "title": "Satin skirt", "priceUsd": 30},
        ]
    }
    with pytest.raises(ValueError, match=r"S06 stays \$25"):
        flag_order(other)
    assert other["lines"][0]["priceUsd"] == 25
    assert other["lines"][1]["priceUsd"] == 30
    single = {"lines": [{"ma": "S06", "title": "Satin skirt", "priceUsd": 24}]}
    with pytest.raises(ValueError, match=r"S06 stays \$25"):
        flag_order(single)
    assert single["lines"][0]["priceUsd"] == 24


def test_held_and_never_list_stay_off_without_writing_held() -> None:
    before = HELD.read_bytes()
    policy = HeldPolicy(held=("K06",), never_list=("Z98",))
    payload = {
        "lines": [
            {"ma": "S06", "title": "Satin skirt", "priceUsd": 25},
            {"ma": "Z98", "title": "Skipped piece", "priceUsd": 30},
            {"ma": "Z98", "title": "Skipped piece again", "priceUsd": 31},
            {"ma": "K06", "title": "Held knit", "priceUsd": 41},
            {"ma": "K06", "title": "Held knit again", "priceUsd": 42},
        ]
    }
    report = flag_order(payload, policy)
    assert [line.ma for line in report.lines] == ["S06"]
    assert report.lines[0].price_usd == "25"
    assert report.flags == ()
    assert [(item.ma, item.reason) for item in report.omitted] == [
        ("Z98", "never-list"),
        ("Z98", "never-list"),
        ("K06", "held"),
        ("K06", "held"),
    ]
    text = render_text(report)
    on_order = text.split("## Flags", 1)[0]
    assert "Z98" not in on_order
    assert "K06" not in on_order
    assert "$30" not in text
    assert "$31" not in text
    assert "$41" not in text
    assert "$42" not in text
    assert HELD.read_bytes() == before
    assert payload["lines"][0]["priceUsd"] == 25


def test_report_refuses_orders_held_and_shop_paths(tmp_path: Path) -> None:
    report = flag_order(_order())
    before = HELD.read_bytes()
    with pytest.raises(ValueError, match="refusing to write"):
        write_report(report, HELD)
    assert HELD.read_bytes() == before
    shop_report = ROOT / "sassy-closet-shop" / "flags.md"
    with pytest.raises(ValueError, match="sell catalog"):
        write_report(report, shop_report)
    assert not shop_report.exists()
    orders = tmp_path / "orders.json"
    with pytest.raises(ValueError, match="refusing to write"):
        write_report(report, orders)
    assert not orders.exists()
    fixture = tmp_path / "order.json"
    fixture.write_text("{}\n", encoding="utf-8")
    with pytest.raises(ValueError, match="overwrite the fixture"):
        write_report(report, fixture, source=fixture)
    assert fixture.read_text(encoding="utf-8") == "{}\n"
    live = report.__class__(**{**report.__dict__, "local": False})
    page = tmp_path / "flags.md"
    with pytest.raises(ValueError, match="fixture order"):
        write_report(live, page)
    assert not page.exists()


def test_cli_report_writes_only_the_local_file(tmp_path: Path) -> None:
    payload = _order()
    fixture = tmp_path / "order.json"
    original = json.dumps(payload)
    fixture.write_text(original, encoding="utf-8")
    report_path = tmp_path / "flags.md"
    held_before = HELD.read_bytes()
    products_before = PRODUCTS.read_bytes()
    ran = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "order_line_flags.py"),
            "--fixture",
            str(fixture),
            "--report",
            str(report_path),
            "--json",
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert ran.returncode == 0, ran.stderr
    saved = json.loads(ran.stdout)
    assert saved["merged"] is False
    assert saved["lines"][0] == {"ma": "S06", "title": "Satin skirt", "priceUsd": "25"}
    assert saved["lines"][1]["priceUsd"] == "25"
    s06 = next(flag for flag in saved["flags"] if flag["ma"] == "S06")
    assert s06["kind"] == "repeated"
    assert s06["count"] == 2
    assert s06["onOrder"] == 2
    assert s06["prices"] == ["25", "25"]
    held_codes = set(load_held_policy().held)
    assert held_codes.isdisjoint({line["ma"] for line in saved["lines"]})
    assert report_path.is_file()
    text = report_path.read_text(encoding="utf-8")
    assert "S06 — Satin skirt — $25" in text
    assert "Lines were not merged." in text
    assert "data/held.json was not written." in text
    assert "$50" not in text
    assert fixture.read_text(encoding="utf-8") == original
    assert HELD.read_bytes() == held_before
    assert PRODUCTS.read_bytes() == products_before


def test_cli_refuses_other_s06_dollar_without_writing(tmp_path: Path) -> None:
    fixture = tmp_path / "order.json"
    fixture.write_text(
        json.dumps(
            {
                "lines": [
                    {"ma": "S06", "title": "Satin skirt", "priceUsd": 25},
                    {"ma": "S06", "title": "Satin skirt", "priceUsd": 26},
                ]
            }
        ),
        encoding="utf-8",
    )
    report_path = tmp_path / "flags.md"
    report_path.write_text("keep\n", encoding="utf-8")
    held_before = HELD.read_bytes()
    ran = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "order_line_flags.py"),
            "--fixture",
            str(fixture),
            "--report",
            str(report_path),
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert ran.returncode == 2
    assert "S06 stays $25" in ran.stderr
    assert report_path.read_text(encoding="utf-8") == "keep\n"
    assert '"priceUsd": 26' in fixture.read_text(encoding="utf-8")
    assert HELD.read_bytes() == held_before
    assert main(["--report", str(ROOT / "data" / "flags.md"), "--fixture", str(fixture)]) == 2
    assert not (ROOT / "data" / "flags.md").exists()


def test_source_does_not_invent_prices_or_write_shop_data() -> None:
    lowered = SOURCE.lower()
    assert "tesla" not in lowered
    assert "vercel" not in lowered
    assert "listing_quote" not in SOURCE
    assert "append_order" not in SOURCE
    assert "packing_slip" not in SOURCE
    assert "catalog.v1.json" in SOURCE
    assert "blob_read_write" not in lowered
    assert "urllib" not in lowered
    assert "import requests" not in lowered
    assert "data/held.json" in SOURCE
    assert "priceusd" in lowered
    assert "merged" in lowered
