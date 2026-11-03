"""Piece 79 placeholder tests: Meta PASS needs Luxubu + Mini Boss to agree."""
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import daily_summary_draft as d  # noqa: E402
import meta_qc_record as r  # noqa: E402

DATE = "2026-01-02"


def rec(tmp_path, side, who, st, why="placeholder"):
    r.record(tmp_path, DATE, side, who, st, why, "out/proof/placeholder.png")


def test_both_pass_is_clear(tmp_path):
    for s in ("ig", "fb"):
        rec(tmp_path, s, "luxubu", "pass"); rec(tmp_path, s, "miniboss", "pass")
    st, src = d.read_meta_status(tmp_path, DATE)
    assert st["ig"][0] == st["fb"][0] == "pass"
    assert d.meta_lines(st, src)[-1] == "Meta verdict: CLEAR"


def test_disagree_flags_boss(tmp_path):
    rec(tmp_path, "ig", "luxubu", "pass"); rec(tmp_path, "ig", "miniboss", "fail", "no Gia")
    st, src = d.read_meta_status(tmp_path, DATE)
    assert st["ig"][0] == "disagree" and "Mini Boss" in st["ig"][1]
    lines = d.meta_lines(st, src)
    assert any(x.startswith("FLAG BOSS") and "Instagram" in x for x in lines)
    assert "NOT CLEAR" in "".join(lines)


def test_one_missing_is_unchecked(tmp_path):
    rec(tmp_path, "fb", "luxubu", "pass")
    st, _ = d.read_meta_status(tmp_path, DATE)
    assert st["fb"] == ("unchecked", "missing Mini Boss")
    assert st["ig"] == ("unchecked", "not in record")


def test_both_fail_is_fail(tmp_path):
    rec(tmp_path, "fb", "luxubu", "fail", "dup"); rec(tmp_path, "fb", "miniboss", "fail", "dup")
    st, _ = d.read_meta_status(tmp_path, DATE)
    assert st["fb"][0] == "fail"


def test_update_keeps_other_and_legacy(tmp_path):
    p = tmp_path / "out/muse"; p.mkdir(parents=True)
    (p / f"meta-qc-{DATE}.json").write_text(json.dumps({"ig": {"status": "pass"}}))
    rec(tmp_path, "ig", "miniboss", "pass")
    doc = json.loads((p / f"meta-qc-{DATE}.json").read_text())
    assert doc["ig"]["legacy"] == {"status": "pass"}
    assert doc["ig"]["miniboss"]["proof"] == "out/proof/placeholder.png"
    st, _ = d.read_meta_status(tmp_path, DATE)
    assert st["ig"] == ("unchecked", "missing Luxubu")
    assert not list(p.glob(".meta-qc-*"))


@pytest.mark.parametrize("why,proof", [("see https://x.invalid", None), ("ok", "/abs/p.png"),
                                       ("ok", "../up.png"), ("see www dot example", "p/www.x.png")])
def test_rejects_bad_input(tmp_path, why, proof):
    with pytest.raises(ValueError):
        r.record(tmp_path, DATE, "ig", "luxubu", "pass", why, proof)


def test_cli(tmp_path):
    assert r.main(["--date", DATE, "--side", "fb", "--who", "luxubu", "--status", "unchecked",
                   "--reason", "signed out", "--root", str(tmp_path)]) == 0
    assert r.main(["--date", "bad", "--side", "fb", "--who", "luxubu", "--status", "pass",
                   "--root", str(tmp_path)]) == 2
