"""Candidates ids are stored as #1, #2. The next id must not reuse 1."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
KIT = ROOT / "excel-kit"
if str(KIT) not in sys.path:
    sys.path.insert(0, str(KIT))

from sot.workbook import next_numeric_id


def test_hashed_candidate_ids_do_not_reuse_one() -> None:
    assert next_numeric_id(["#1", "#2"], prefix="", width=1) == "3"
    assert next_numeric_id(["1", "2"], prefix="", width=1) == "3"
    assert next_numeric_id([], prefix="", width=1) == "1"


def test_wishlist_and_order_ids_keep_their_prefix() -> None:
    assert next_numeric_id(["WISH001", "WISH002"], prefix="WISH", width=3) == "WISH003"
    assert next_numeric_id(["ORD-001"], prefix="ORD", width=3) == "ORD002"
    assert next_numeric_id([], prefix="WISH", width=3) == "WISH001"
