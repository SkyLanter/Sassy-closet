"""Piece 198: Python norm_ma agrees with the shared golden vector (also used by both TS apps)."""
import json
import re
from pathlib import Path

import pytest

from held_policy import norm_ma

ROOT = Path(__file__).resolve().parents[2]
VECTOR = json.loads((ROOT / "scripts/testdata/ma-normalization-vectors.json").read_text(encoding="utf-8"))["rows"]


def test_vector_is_substantial():
    assert len(VECTOR) >= 40
    assert {r["expected"] for r in VECTOR} >= {"K03", "S06", "A01", "Q09", "A100"}


@pytest.mark.parametrize("row", VECTOR, ids=lambda r: repr(r["input"]))
def test_norm_ma_matches_vector(row):
    assert norm_ma(row["input"]) == row["expected"]


# --- drift guard: Python mã keys go through norm_ma only -------------------------
# Lines allowed to call .strip().upper() because they are NOT mã keys (kind, currency,
# kind letter) or are norm_ma itself. Keyed by file + exact stripped source line.
ALLOWED = {
    ("held_policy.py", 'code = "" if value is None else str(value).strip().upper()'),
    ("held_price_proposal.py", 'kind = str(row.get("kind") or code[:1]).strip().upper()'),
    ("held_price_proposal.py", "out[kind.strip().upper()] = n"),
    ("intake_gaps.py", 'code = str(k.get("code", "")).strip().upper()'),
    ("intake_gaps.py", 'kind = str(row.get("kind", "") or "").strip().upper()'),
    ("intake_gaps.py", 'cur = str(row.get("cost_currency") or "").strip().upper()'),
}


def test_no_raw_strip_upper_outside_norm_ma():
    hits = []
    for p in sorted((ROOT / "scripts").glob("*.py")):
        for n, line in enumerate(p.read_text(encoding="utf-8").splitlines(), 1):
            if ".strip().upper()" in line and (p.name, line.strip()) not in ALLOWED:
                hits.append(f"{p.name}:{n}: {line.strip()}  -> use held_policy.norm_ma()")
    assert hits == []


def test_single_python_helper():
    defs = [f"{p.name}" for p in (ROOT / "scripts").glob("*.py")
            if re.search(r"^def norm_ma\b", p.read_text(encoding="utf-8"), re.M)]
    assert defs == ["held_policy.py"]


# TS: only the pinned helpers may hand-roll zero-padding of a mã.
TS_PAD_ALLOWED = {"sassy-closet/lib/mint.ts", "sassy-closet/lib/held-incomplete.ts", "sassy-closet-shop/lib/ma.ts"}


def test_ts_does_not_reimplement_ma_padding():
    hits = []
    for app in ("sassy-closet", "sassy-closet-shop"):
        for sub in ("lib", "app", "components"):
            base = ROOT / app / sub
            for p in sorted(base.rglob("*.ts*")) if base.exists() else []:
                rel = p.relative_to(ROOT).as_posix()
                if "node_modules" in rel or rel in TS_PAD_ALLOWED:
                    continue
                if re.search(r"padStart\(\s*2\s*,\s*[\"']0[\"']\s*\)", p.read_text(encoding="utf-8")):
                    hits.append(f"{rel}: hand-rolled zero padding -> use canonicalMaSpelling / normalizeMa")
    assert hits == []
