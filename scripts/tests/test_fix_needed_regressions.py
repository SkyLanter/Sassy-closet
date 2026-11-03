"""Locks the failure modes from the fix-needed script PRs.

Held checks follow data/held.json. S06 copy matches the current shop and
admin sources. Nothing pins a hash of data/held.json. The README keeps
desk status and the restock note.
"""

from __future__ import annotations

import json
import re
from decimal import Decimal
from pathlib import Path

from catalog_diff import CatalogRow, diff_catalogs
from held_policy import HeldPolicy, load_held_policy

ROOT = Path(__file__).resolve().parents[2]
HELD = ROOT / "data" / "held.json"
STALE_HELD = (
    "S14",
    "A24",
    "A25",
    "S15",
    "A26",
    "K02",
    "K03",
    "K04",
    "K05",
    "V04",
    "K06",
    "V05",
)


def test_live_held_json_is_not_the_stale_thirteen() -> None:
    policy = load_held_policy()
    raw = json.loads(HELD.read_text(encoding="utf-8"))
    assert list(policy.held) == raw["heldIncomplete"]
    assert policy.held != STALE_HELD
    assert set(STALE_HELD) < set(policy.held)
    for code in ("S16", "K06", "A27", "G01"):
        assert code in policy.held
    assert "S06" not in policy.held
    assert "Q02" not in policy.held
    assert raw["neverList"] == []


def test_catalog_diff_follows_the_passed_policy() -> None:
    policy = HeldPolicy(held=("Z90",), never_list=())
    held = CatalogRow("Z90", None, "hold")
    s06 = CatalogRow("S06", Decimal("25"), "available")
    rows = {"Z90": held, "S06": s06}
    report = diff_catalogs(rows, rows, policy)
    assert [row.ma for row in report.held] == ["Z90"]
    assert report.held[0].stays_held is True
    assert report.s06_before == report.s06_after == "25"


def test_s06_lock_copy_matches_current_shop_and_admin() -> None:
    shop = (ROOT / "sassy-closet" / "lib" / "shop-catalog.ts").read_text(encoding="utf-8")
    admin = (ROOT / "sassy-closet-shop" / "lib" / "admin-ops.ts").read_text(encoding="utf-8")
    assert "S06 stays available at $25." in shop
    assert 'error: "S06 stays $25."' not in shop
    assert "const S06_AVAILABLE_USD = 25" in shop
    assert 'error: "S06 stays $25."' in admin
    assert 'canonicalMaSpelling(ma) === "S06" && input.priceUsd !== 25' in admin


def test_no_test_pins_a_held_json_sha() -> None:
    hits: list[str] = []
    needle = "HELD" + "_SHA"
    pinned = re.compile(r"sha256\([^\n]*held\.json")
    for path in sorted((ROOT / "scripts" / "tests").glob("test_*.py")):
        if path.name == "test_fix_needed_regressions.py":
            continue
        text = path.read_text(encoding="utf-8")
        if needle in text or pinned.search(text):
            hits.append(path.name)
    assert hits == []


def test_readme_keeps_desk_status_and_the_restock_note() -> None:
    text = (ROOT / "README.md").read_text(encoding="utf-8")
    assert "## Desk status" in text
    assert "scripts/desk_status.py" in text
    assert "## Restock note" in text
    assert "scripts/restock_note.py" in text
    assert "ADMIN_PASSWORD" not in text
    assert "There is no intake password." in text
    assert "S16" in text and "A27" in text and "G01" in text
