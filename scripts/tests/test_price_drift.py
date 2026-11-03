"""Public sell-price drift. Fixtures only — no catalog write and no network."""

from __future__ import annotations

import json
from pathlib import Path

from price_drift import (
    compare,
    diff_prices,
    read_catalog_seed,
    read_observation,
    render,
    repo_root,
)

ROOT = repo_root()
INTAKE_GAPS = {
    "A01": (25, 27),
    "A02": (22, 23),
    "A03": (19, 22),
    "A04": (20, 21),
    "B01": (41, 46),
    "B02": (30, 31),
    "J01": (30, 29),
    "J02": (35, 40),
    "K01": (37, 36),
    "P03": (18, 11),
    "P04": (13, 10),
    "P05": (23, 25),
    "S01": (28, 39),
}


def test_real_fixtures_flag_intake_gaps_and_leave_prices_alone() -> None:
    seed_path = ROOT / "sassy-closet-shop" / "data" / "products.json"
    before = seed_path.read_bytes()
    report = compare(ROOT)
    assert seed_path.read_bytes() == before
    assert report.exit_code == 1
    assert report.s06_live == 25
    assert report.s06_problems == ()
    assert report.problems == ()
    assert "S06" in report.seed_missing

    intake = {row.ma: (row.fixture_usd, row.live_usd) for row in report.drifts if row.source == "intake"}
    assert intake == INTAKE_GAPS
    seed = {row.ma: (row.fixture_usd, row.live_usd) for row in report.drifts if row.source == "catalog-seed"}
    assert "P03" not in seed
    assert "S01" not in seed
    assert seed["A03"] == (25, 22)
    assert seed["B02"] == (25, 31)
    assert "P03" not in {row.ma for row in report.drifts if row.source == "boss-price-lock"}
    assert read_catalog_seed(seed_path)["P03"] == 11
    assert read_catalog_seed(seed_path)["S01"] == 39
    assert "S06" not in read_catalog_seed(seed_path)

    text = render(report)
    assert text == (ROOT / "data" / "price-drift" / "REPORT.md").read_text(encoding="utf-8")
    assert "S01 live $39 vs intake $28" in text
    assert "P03 live $11 vs intake $18" in text
    assert "S06 stays **$25**" in text
    assert "costCny" not in text
    assert "landedUsd" not in text


def test_observation_is_public_sell_dollars_only(tmp_path: Path) -> None:
    path = ROOT / "data" / "price-drift" / "observed-public-sell.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["readOnly"] is True
    assert payload["writesPrices"] is False
    assert payload["liveUsd"]["S06"] == 25
    assert payload["liveUsd"]["P03"] == 11
    assert payload["intakeSellUsd"]["P03"] == 18
    assert "S06" not in payload["intakeSellUsd"]
    for key in payload:
        assert "cost" not in key.lower()
        assert "landed" not in key.lower()
    read_observation(path)
    payload["costCny"] = {"A01": 1}
    dirty = tmp_path / "observed.json"
    dirty.write_text(json.dumps(payload), encoding="utf-8")
    try:
        read_observation(dirty)
    except ValueError as error:
        assert "cost" in str(error).lower()
    else:
        raise AssertionError("a cost field was accepted")
    assert "costCny" not in path.read_text(encoding="utf-8")


def test_diff_does_not_rewrite_the_fixture_map() -> None:
    fixture = {"S06": 30, "A01": 27}
    live = {"S06": 25, "A01": 27}
    before = dict(fixture)
    rows = diff_prices("intake", fixture, live)
    assert fixture == before
    assert len(rows) == 1
    assert rows[0].ma == "S06"
    assert rows[0].fixture_usd == 30
    assert rows[0].live_usd == 25


def test_script_does_not_fetch_or_write() -> None:
    source = (ROOT / "scripts" / "price_drift.py").read_text(encoding="utf-8")
    assert "urlopen" not in source
    assert "urlretrieve" not in source
    assert "BLOB_READ_WRITE" not in source
    assert "write_text" not in source
    assert "products.json" in source
