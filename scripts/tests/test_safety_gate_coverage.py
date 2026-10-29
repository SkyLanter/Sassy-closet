"""Piece 211 drift guard: the safety-gate coverage map must stay honest."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DOC = json.loads((ROOT / "scripts/testdata/safety-gate-coverage.json").read_text(encoding="utf-8"))
GATES = DOC["gates"]


def test_no_gate_uncovered():
    bad = [g["id"] for g in GATES if g["verdict"] not in ("COVERED", "PARTIAL")]
    assert not bad, f"UNCOVERED or unknown verdict: {bad}"


def test_every_gate_has_tests_and_they_exist():
    for g in GATES:
        assert g["tests"], g["id"]
        for t in g["tests"]:
            assert (ROOT / t).is_file(), f"{g['id']}: test file gone: {t}"


def test_gate_locations_exist():
    for g in GATES:
        path, _, line = g["location"].partition(":")
        file = ROOT / path
        assert file.is_file(), g["id"]
        if line:
            assert int(line) <= len(file.read_text(encoding="utf-8").splitlines()), g["id"]


def test_partial_gates_have_suggestions_and_ids_unique():
    ids = [g["id"] for g in GATES]
    assert len(ids) == len(set(ids))
    for g in GATES:
        if g["verdict"] == "PARTIAL":
            assert g["suggested_test"].strip(), g["id"]
        assert re.fullmatch(r"[A-Za-z0-9-]+", g["id"])
