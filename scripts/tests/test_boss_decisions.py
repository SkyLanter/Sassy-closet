"""Placeholder tests for piece 89: boss_decisions.py (no real data)."""
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import boss_decisions as bd  # noqa: E402

DIGEST = """Open Boss-only decisions (read-only digest)
- [price_approval] X01  first_seen=2000-01-01  source=out/qc/a.md
- [intake_mismatch] X02  first_seen=2000-01-03  source=out/qc/b.md
- [intake_mismatch] X03  first_seen=2000-01-03  source=out/qc/b.md
- [intake_mismatch] X09  first_seen=2000-01-03  source=out/qc/b.md
- [blob_photo_delete] X04  first_seen=?  source=out/qc/c.md
- [popular_order_held] Remove held mãs X05, X06 from popular order? (note)
"""
CB = "| mã | a | b | c | d | result |\n|---|---|---|---|---|---|\n| X07 | 1 | 1 / UNDER | 1 / OK | 1 / OK | FLIP |\n"


def _root(tmp_path):
    cr = tmp_path / "verify/cost-recheck"; cr.mkdir(parents=True, exist_ok=True)
    for d, u in (("2000-01-03", ["X02"]), ("2000-01-04", ["X08", "X02"]), ("2000-01-05", ["X08", "X02"])):
        (cr / f"summary.{d}.json").write_text(json.dumps({"unreachable_mas": u}))
    rp = tmp_path / "out/reports/2000-01-05"; rp.mkdir(parents=True, exist_ok=True)
    (rp / "COST-BASIS.md").write_text(CB)
    pr = tmp_path / "out/meta-popular/cycle-2000-01-05"; pr.mkdir(parents=True, exist_ok=True)
    (pr / "SUMMARY.txt").write_text("Deploy: PR #7 (2000-01-02 blend) still open, Boss-gated.\nPR #8 merged.\n")
    return tmp_path


def _run(tmp_path, meta=None):
    r = _root(tmp_path)
    cost = {"persistent_new_unreachable": ["X08", "X09"], "unreachable_mas": ["X08", "X02"]}
    return bd.compile_decisions(r, "2000-01-05", DIGEST, cost, r / "verify/cost-recheck/summary.2000-01-05.json",
                                r / "out/reports/2000-01-05/COST-BASIS.md",
                                meta or {"ig": ("pass", ""), "fb": ("unchecked", "")}, None,
                                r / "out/meta-popular/cycle-2000-01-05/SUMMARY.txt")


def _by(D, cat):
    return {d["ma"]: d for d in D if d["cat"] == cat}


def test_gone_hold_days_from_streak(tmp_path):
    g = _by(_run(tmp_path), "gone_hold")
    assert g["X08"]["since"] == "2000-01-04" and g["X08"]["days"] == 1


def test_flip_under_and_dedupe(tmp_path):
    D = _run(tmp_path)
    assert set(_by(D, "flip_under")) == {"X07"}
    assert "X09" not in _by(D, "intake_mismatch")  # asked as gone_hold already


def test_mismatch_split_by_unreachable(tmp_path):
    D = _run(tmp_path)
    assert set(_by(D, "intake_unreachable")) == {"X02"}
    assert set(_by(D, "intake_mismatch")) == {"X03"}


def test_unknown_date_is_question_mark(tmp_path):
    D = _run(tmp_path)
    assert _by(D, "blob_photo_delete")["X04"]["days"] is None
    assert set(_by(D, "popular_order_held")) == {"X05", "X06"}
    assert "| ?" in bd.render(D, "2000-01-05")


def test_meta_and_pr(tmp_path):
    D = _run(tmp_path)
    assert len(_by(D, "meta")) == 1
    assert set(_by(D, "pr")) == {"PR #7"} and _by(D, "pr")["PR #7"]["days"] == 3
    assert not _by(_run(tmp_path, {"ig": ("pass", ""), "fb": ("pass", "")}), "meta")


def test_render_refuses_banned(tmp_path):
    D = [{"cat": "hold_call", "ma": "X01", "q": "see http://x", "ev": "a", "since": None, "days": None}]
    with pytest.raises(SystemExit):
        bd.render(D, "2000-01-05")


def test_main_writes_report(tmp_path):
    r = _root(tmp_path)
    dg = tmp_path / "dg.txt"; dg.write_text(DIGEST)
    assert bd.main(["--date", "2000-01-05", "--root", str(r), "--digest", str(dg)]) == 0
    out = (r / "out/reports/2000-01-05/BOSS-DECISIONS.md").read_text()
    assert "X07 |" in out and "TOTAL" in out


# --- piece 90: named sign-in blocker (placeholder text only) ---
def _meta_root(tmp_path, files):
    r = _root(tmp_path)
    for rel, txt in files.items():
        p = r / rel; p.parent.mkdir(parents=True, exist_ok=True); p.write_text(txt)
    return r


def test_signin_blocker_named(tmp_path):
    r = _meta_root(tmp_path, {"out/muse/notes-2000-01-03.md": "Luxubu: Facebook sign-in needed before QC.\n",
                              "out/midnight-qc/2000-01-04/summary.md": "Luxubu FB login wall again.\n"})
    m = _by(_run(tmp_path), "meta")
    assert len(m) == 1
    d = m["-"]
    assert d["q"].startswith("Luxubu Facebook sign-in needed")
    assert d["ev"] == "out/muse/notes-2000-01-03.md" and d["days"] == 2


def test_signed_in_as_instruction_is_not_blocker(tmp_path):
    _meta_root(tmp_path, {"out/muse/TODAY.md": "Luxubu, Meta FB QC (signed in as the Page).\n"})
    assert _by(_run(tmp_path), "meta")["-"]["q"].startswith("Meta QC not PASS")


def test_blocker_needs_person_and_platform(tmp_path):
    _meta_root(tmp_path, {"out/muse/x-2000-01-05.md": "Taobao login-gated; sign-in needed.\nLuxubu sign-in needed.\n"})
    assert _by(_run(tmp_path), "meta")["-"]["q"].startswith("Meta QC not PASS")


def test_blocker_ignored_when_meta_pass_or_future(tmp_path):
    _meta_root(tmp_path, {"out/muse/n-2000-01-09.md": "Luxubu Facebook sign-in needed.\n"})
    assert _by(_run(tmp_path), "meta")["-"]["q"].startswith("Meta QC not PASS")
    assert not _by(_run(tmp_path, {"ig": ("pass", ""), "fb": ("pass", "")}), "meta")
