import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import boss_decisions_digest as bdd


def _w(root, rel, text):
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text)


def test_categories_and_dedupe(tmp_path):
    _w(tmp_path, "out/muse/extras-2026-01-02.md",
       "Held photos public on Blob: X01 cover. Boss's call.\n"
       "X02: needs a Boss price (held)\n"
       "Intake mismatch for X03 (PLACEHOLDER)\n")
    _w(tmp_path, "out/muse/extras-2026-01-03.md",
       "X02: awaiting Boss price\n"
       "Hold call for X04: keep or release? Boss\n")
    seen = bdd.scan(tmp_path, public_held={"X01"})
    assert seen[("blob_photo_delete", "X01")][1] == "2026-01-02"
    assert seen[("price_approval", "X02")][1] == "2026-01-02"
    assert ("intake_mismatch", "X03") in seen
    assert ("hold_call", "X04") in seen
    assert ("hold_call", "X01") in seen  # no longer shadowed by blob (piece 52)
    assert len(seen) == 5


def test_closed_lines_skipped(tmp_path):
    _w(tmp_path, "verify/cost-recheck/REPORT-2026-01-05.md",
       "X05 Boss price approved\n")
    assert bdd.scan(tmp_path) == {}


def test_output_has_no_line_text(tmp_path, capsys):
    _w(tmp_path, "out/midnight-qc/QC-2026-01-06.md",
       "X06 needs a Boss price PLACEHOLDER_SECRET\n")
    bdd.main(["--root", str(tmp_path)])
    out = capsys.readouterr().out
    assert "X06" in out and "PLACEHOLDER_SECRET" not in out
    assert "TOTAL 1" in out


def test_empty_root(tmp_path, capsys):
    bdd.main(["--root", str(tmp_path)])
    assert "TOTAL 0 (none)" in capsys.readouterr().out


def test_date_from_parent_dir(tmp_path):
    _w(tmp_path, "out/midnight-qc/2026-01-07/summary.md", "X07 needs a Boss price\n")
    assert bdd.scan(tmp_path)[("price_approval", "X07")][1] == "2026-01-07"


# ---- piece 52: proximity + public-held filter + --explain ----

def test_blob_far_from_ma_not_counted(tmp_path):
    _w(tmp_path, "verify/cost-recheck/REPORT-2026-02-01.md",
       "X11 intake check" + " filler" * 20 + " Boss: blob photo delete pending\n")
    seen = bdd.scan(tmp_path, public_held={"X11"})
    assert ("blob_photo_delete", "X11") not in seen


def test_blob_near_ma_same_line_counted(tmp_path):
    _w(tmp_path, "verify/cost-recheck/REPORT-2026-02-02.md",
       "X12 Blob photos still public, Boss to delete\n")
    ex = {}
    seen = bdd.scan(tmp_path, public_held={"X12"}, explain=ex)
    assert ("blob_photo_delete", "X12") in seen
    assert ex[("blob_photo_delete", "X12")] == "blob_near_ma_line"


def test_blob_same_bullet_counted(tmp_path):
    _w(tmp_path, "out/muse/extras-2026-02-03.md",
       "- X13 held\n  Blob photo still public; Boss delete call\n- X14 other note\n")
    ex = {}
    seen = bdd.scan(tmp_path, public_held={"X13", "X14"}, explain=ex)
    assert ex[("blob_photo_delete", "X13")] == "blob_near_ma_bullet"
    assert ("blob_photo_delete", "X14") not in seen


def test_blob_other_bullet_not_counted(tmp_path):
    _w(tmp_path, "out/muse/extras-2026-02-04.md",
       "- X15 Boss note\n- Blob photo delete pending\n")
    assert ("blob_photo_delete", "X15") not in bdd.scan(tmp_path, public_held={"X15"})


def test_only_public_held_counted(tmp_path):
    _w(tmp_path, "out/muse/extras-2026-02-05.md",
       "X16 Blob photo public, Boss delete\nX17 Blob photo public, Boss delete\n")
    seen = bdd.scan(tmp_path, public_held={"X16"})
    assert ("blob_photo_delete", "X16") in seen
    assert ("blob_photo_delete", "X17") not in seen


def test_public_held_file_schema(tmp_path):
    f = tmp_path / "hp.json"
    f.write_text('{"schema": "held-photos/v1", "exposedMas": ["X18"]}')
    assert bdd.load_public_held(str(f)) == {"X18"}
    f.write_text('["X19"]')
    assert bdd.load_public_held(str(f)) == {"X19"}


def test_explain_prints_rule_not_text(tmp_path, capsys):
    _w(tmp_path, "out/muse/extras-2026-02-06.md",
       "X20 Blob photo public PLACEHOLDER_SECRET, Boss delete\n")
    f = tmp_path / "hp.json"
    f.write_text('["X20"]')
    bdd.main(["--root", str(tmp_path), "--public-held", str(f), "--explain"])
    out = capsys.readouterr().out
    assert "rule=blob_near_ma_line" in out
    assert "PLACEHOLDER_SECRET" not in out and "Blob photo public" not in out


def test_held_popular_order_item_placeholder(tmp_path):
    import json as _j
    from boss_decisions_digest import held_in_popular_order, held_order_item
    o = tmp_path / "o.json"; h = tmp_path / "h.json"
    o.write_text(_j.dumps({"order": ["X01", "X02", "X03"]}))
    h.write_text(_j.dumps({"held": ["X02"], "neverList": ["X03"]}))
    mas = held_in_popular_order(o, h)
    assert mas == ["X02", "X03"]
    assert held_order_item(mas).startswith("Remove held mãs X02, X03 from popular order?")
    assert held_order_item([]) is None
    assert held_in_popular_order(tmp_path / "none.json", h) == []
