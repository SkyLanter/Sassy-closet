"""A catalog.v1 snapshot passed as --live must mark priced mãs as already live.

`daily_shop_check.py` hands `held_price_proposal` the catalog snapshot it
already loaded (`--live`), so a catalog-shaped file is the normal case, not an
edge case. Reading it as a `{mã: $}` price map found no mã at all and re-quoted
every live row: the Boss approval sheet then asked to approve a brand-new
sell price for a piece that is already on the shop at that price.
"""

from __future__ import annotations

import json
from pathlib import Path

import daily_shop_check as d
import held_price_proposal as hp

HELD = hp.HeldPolicy(held=("H02",), never_list=())
CATALOG = {"schema": "catalog.v1", "updatedAt": "2026-11-26T09:00:00Z", "products": [
    {"ma": "A01", "priceUsd": 23, "status": "available"},
    {"ma": "S06", "priceUsd": 25, "status": "available"},
    {"ma": "K03", "priceUsd": 52, "status": "hidden"},
]}
INTAKE = [{"ma": "A01", "kind": "A", "cost_cny": "95", "kg": "0.3"},
          {"ma": "H02", "kind": "H", "cost_cny": "60", "kg": "0.08"}]


def _write(tmp_path: Path, name: str, payload: object) -> Path:
    p = tmp_path / name
    p.write_text(json.dumps(payload), encoding="utf-8")
    return p


def test_catalog_snapshot_marks_live_mas_priced(tmp_path: Path) -> None:
    live = hp.load_live(_write(tmp_path, "catalog.json", CATALOG))
    assert live == {"A01": 23, "S06": 25}  # K03 is hidden, so it is not live


def test_live_row_is_not_requoted_from_a_catalog_snapshot(tmp_path: Path) -> None:
    sheet = hp.build(INTAKE, hp.load_live(_write(tmp_path, "catalog.json", CATALOG)), HELD)
    assert [p["ma"] for p in sheet["proposals"]] == ["H02"]
    assert sheet["verdicts"] == {"H02": "$16"}


def test_price_map_form_still_quotes_only_unpriced_mas(tmp_path: Path) -> None:
    live = hp.load_live(_write(tmp_path, "prices.json", {"prices": {"A01": "23"}}))
    assert live == {"A01": "23"}
    sheet = hp.build(INTAKE, live, HELD)
    assert [p["ma"] for p in sheet["proposals"]] == ["H02"]


def test_catalog_keys_never_become_mas(tmp_path: Path) -> None:
    """`schema`/`updatedAt` are not mãs, so they must not reach the sheet as rows."""
    sheet = hp.build([], hp.load_live(_write(tmp_path, "catalog.json", CATALOG)), HELD)
    assert sheet["proposals"] == [] and sheet["verdicts"] == {}


def test_daily_shop_check_held_sheet_does_not_requote_a_live_ma(tmp_path: Path) -> None:
    """The shipped caller passes the same catalog snapshot as --live."""
    live = _write(tmp_path, "live.json", {"products": [
        {"ma": "A01", "priceUsd": 23, "status": "available"},
        {"ma": "S06", "priceUsd": 25, "status": "available"}]})
    costs = tmp_path / "costs.csv"
    costs.write_text("ma,intake_cny,kg\nA01,95,0.3\nS06,100,0.5\n", encoding="utf-8")
    out = tmp_path / "r.json"
    d.main(["--live", str(live), "--costs", str(costs),
            "--intake", str(_write(tmp_path, "intake.json", {"submissions": INTAKE})),
            "--out-json", str(out), "--out-md", str(tmp_path / "r.md")])
    held = next(s for s in json.loads(out.read_text(encoding="utf-8"))["sections"]
                if s["name"] == "held_sheet")
    quoted = [line for line in held["info"] if line.startswith("1 quoted")]
    assert quoted and "H02" in quoted[0] and "A01" not in quoted[0]
