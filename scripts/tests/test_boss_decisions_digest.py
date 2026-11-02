import json
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
    bdd.main(["--root", str(tmp_path), "--order", str(tmp_path / "missing-order.json"),
              "--held", str(tmp_path / "missing-held.json")])
    out = capsys.readouterr().out
    assert "X06" in out and "PLACEHOLDER_SECRET" not in out
    assert "[popular_order_held]" not in out
    assert "TOTAL 1" in out


def test_empty_root(tmp_path, capsys):
    bdd.main(["--root", str(tmp_path), "--order", str(tmp_path / "missing-order.json"),
              "--held", str(tmp_path / "missing-held.json")])
    out = capsys.readouterr().out
    assert "[popular_order_held]" not in out
    assert "TOTAL 0 (none)" in out


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
    o = tmp_path / "o.json"; h = tmp_path / "h.json"
    o.write_text(json.dumps({"order": ["X01", "X02", "X03"]}))
    h.write_text(json.dumps({"held": ["X02"], "neverList": ["X03"]}))
    mas = bdd.held_in_popular_order(o, h)
    assert mas == ["X02", "X03"]
    assert bdd.held_order_item(mas).startswith("Remove held mãs X02, X03 from popular order?")
    assert bdd.held_order_item([]) is None
    assert bdd.held_in_popular_order(tmp_path / "none.json", h) == []


def test_negated_closures_and_continuation_bullet(tmp_path):
    assert bdd.is_closed("X05 hold call not decided yet — Boss") is False
    assert bdd.is_closed("Boss: price not yet approved for X07") is False
    assert bdd.is_closed("Boss price no longer approved for X06") is False
    open_root = tmp_path / "open"
    _w(open_root, "out/muse/extras-2026-03-01.md",
       "X05 hold call not decided yet — Boss\n"
       "Boss: price not yet approved for X07\n"
       "Boss price no longer approved for X06\n"
       "- Boss hold call needed\n"
       "  for X99 keep or release? Boss\n")
    seen = bdd.scan(open_root)
    assert set(seen) == {
        ("hold_call", "X05"),
        ("price_approval", "X07"),
        ("price_approval", "X06"),
        ("hold_call", "X99"),
    }
    assert seen[("hold_call", "X99")][1] == "2026-03-01"
    noboss = tmp_path / "noboss"
    _w(noboss, "verify/cost-recheck/REPORT-2026-03-02.md",
       "Price not yet approved for X07 (held)\n")
    assert bdd.scan(noboss) == {}


def test_open_continuation_survives_closed_bullet_line(tmp_path):
    _w(tmp_path, "out/muse/extras-2026-03-01.md",
       "- X01 Boss price approved\n"
       "  X02 needs a Boss price\n")
    assert bdd.scan(tmp_path) == {("price_approval", "X02"): (
        "out/muse/extras-2026-03-01.md", "2026-03-01")}


def test_closed_line_still_skipped(tmp_path):
    assert bdd.is_closed("X05 Boss price approved") is True
    assert bdd.is_closed("No other issue. Boss price approved for X04") is True
    _w(tmp_path, "verify/cost-recheck/REPORT-2026-03-03.md",
       "X05 Boss price approved\n"
       "No other issue. Boss price approved for X04\n")
    assert bdd.scan(tmp_path) == {}


def test_repo_order_held_paths_exist():
    order, held = bdd.repo_order_held_paths()
    repo = Path(bdd.__file__).resolve().parents[1]
    assert order == repo / "sassy-closet-shop" / "data" / "popular-order.json"
    assert held == repo / "data" / "held.json"
    assert order.is_file() and held.is_file()


def test_main_explicit_order_prints_held_mas_only(tmp_path, capsys):
    root = tmp_path / "scanroot"
    root.mkdir()
    order = tmp_path / "order.json"
    held = tmp_path / "held.json"
    order.write_text(json.dumps({
        "updatedAt": "SECRET_UPDATED_AT",
        "method": "SECRET_METHOD_TEXT",
        "order": ["Z91", "Z92"],
    }))
    held.write_text(json.dumps({
        "held": ["Z91"],
        "neverList": [],
        "reason": "SECRET_HELD_REASON",
    }))
    assert bdd.main(["--root", str(root), "--order", str(order), "--held", str(held)]) == 0
    out = capsys.readouterr().out
    lines = [ln for ln in out.splitlines() if "[popular_order_held]" in ln]
    assert lines == [
        "- [popular_order_held] Remove held mãs Z91 from popular order? "
        "(no effect while they are 404; keeping lets them rank on return)"
    ]
    assert "Z92" not in out
    for secret in ("SECRET_UPDATED_AT", "SECRET_METHOD_TEXT", "SECRET_HELD_REASON", "heldIncomplete"):
        assert secret not in out
    assert "TOTAL 1 (popular_order_held=1)" in out
