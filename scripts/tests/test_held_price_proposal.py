"""held_price_proposal: fixtures only, no network, writes only tmp outputs."""

from __future__ import annotations

import json
from decimal import Decimal
from pathlib import Path

import held_price_proposal as hp
from autolist import price
from held_policy import HeldPolicy, default_held_path, load_held_policy

POLICY = HeldPolicy(held=("S14", "K03"), never_list=("Q01", "Q02"))
A29 = {"ma": "A29", "kind": "A", "cost_cny": "110"}
H02 = {"ma": "H02", "kind": "H", "cost_cny": ""}
G01 = {"ma": "G01", "kind": "G", "cost_cny": "99"}


def test_landed_formula() -> None:
    assert hp.landed_usd(Decimal("110"), Decimal("0.3")).quantize(Decimal("0.0001")) == Decimal("19.5177")


def test_a29_tier_vs_flat() -> None:
    p = hp.propose(A29, POLICY)
    assert (p.status, p.tiered_usd, p.flat25_usd, p.kg_source) == ("quote", 30, 27, "A category proxy")
    assert p.tiered_usd == price(Decimal(str(p.landed_usd)))


def test_flat_under_ten_bump() -> None:
    assert hp.flat_quote(Decimal("6")) == 10  # ceil(8) + 2
    assert hp.flat_quote(Decimal("7.5")) == 10
    assert hp.flat_quote(Decimal("30")) == 40


def test_missing_yen_no_quote() -> None:
    p = hp.propose(H02, POLICY)
    assert p.status == "needs-boss" and p.tiered_usd is None and p.flat25_usd is None
    assert "missing intake ¥" in p.flags


def test_unusable_yen_flagged() -> None:
    p = hp.propose({"ma": "S07", "kind": "S", "cost_cny": "127;145", "kg": "0.5"}, POLICY)
    assert p.status == "needs-boss" and any("not usable" in f for f in p.flags)


def test_g_shoe_weight_needs_boss() -> None:
    p = hp.propose(G01, POLICY)
    assert p.status == "needs-boss" and p.kg is None
    assert any("Boss must set kg" in f for f in p.flags)


def test_missing_kg_other_kind() -> None:
    p = hp.propose({"ma": "S14", "kind": "S", "cost_cny": "64.68"}, POLICY)
    assert p.status == "needs-boss" and "missing kg (no category proxy)" in p.flags
    assert "held incomplete" in p.flags


def test_weight_sources_priority() -> None:
    row = {"ma": "G01", "kind": "G", "cost_cny": "99", "kg": "0.8"}
    assert hp.propose(row, POLICY).kg_source == "intake"
    p = hp.propose(G01, POLICY, weights={"G01": Decimal("0.8")})
    assert p.kg_source == "weights csv" and p.status == "quote"
    p = hp.propose(G01, POLICY, kg_proxy={"G": Decimal("0.8")})
    assert p.kg_source == "G category proxy" and (p.tiered_usd, p.flat25_usd) == (34, 31)


def test_selection_held_or_unpriced_only() -> None:
    rows = [A29, H02, G01, {"ma": "A01", "cost_cny": "90"}, {"ma": "S14", "cost_cny": "64"},
            {"ma": "S06", "cost_cny": "60"}, {"ma": "A29", "cost_cny": "1"}]
    live = {"A01": 27, "S14": 30, "S06": 25}
    got = [r["ma"] for r in hp.select(rows, live, POLICY)]
    assert got == ["A29", "H02", "G01", "S14"]  # A01 priced, S06 locked, dup dropped


def test_never_list_q_excluded() -> None:
    rows = [{"ma": "Q01", "cost_cny": "74"}, {"ma": "q02", "cost_cny": "50"}, {"ma": "Q03", "cost_cny": "50"}]
    assert [r["ma"] for r in hp.select(rows, {}, POLICY)] == ["Q03"]


def test_uses_repo_held_source() -> None:
    # Same file lib/held-incomplete.ts imports.
    ts = (default_held_path().parents[1] / "sassy-closet" / "lib" / "held-incomplete.ts").read_text()
    assert "data/held.json" in ts
    pol = load_held_policy()
    rows = [{"ma": m, "cost_cny": "50"} for m in pol.never_list]
    assert hp.select(rows, {}, pol) == []


def test_cli_writes_only_named_outputs(tmp_path: Path) -> None:
    intake = tmp_path / "intake.json"
    live = tmp_path / "live.json"
    intake.write_text(json.dumps({"submissions": [A29, H02, G01]}), encoding="utf-8")
    live.write_text(json.dumps({"prices": {"A01": 27}}), encoding="utf-8")
    before = {p.name: p.read_bytes() for p in tmp_path.iterdir()}
    md, js = tmp_path / "sheet.md", tmp_path / "sheet.json"
    assert hp.main(["--intake", str(intake), "--live", str(live), "--out-md", str(md), "--out-json", str(js)]) == 0
    after = {p.name: p.read_bytes() for p in tmp_path.iterdir()}
    assert set(after) - set(before) == {"sheet.md", "sheet.json"}
    assert all(after[k] == v for k, v in before.items())
    sheet = json.loads(js.read_text(encoding="utf-8"))
    assert sheet["approved"] is False and sheet["needs_boss"] == ["H02", "G01"]
    assert "| A29 | 110 |" in md.read_text(encoding="utf-8")


def test_no_network_imports() -> None:
    src = Path(hp.__file__).read_text(encoding="utf-8")
    for bad in ("urllib", "requests", "http.client", "socket", "subprocess"):
        assert f"import {bad}" not in src


# --- piece 20: --live-catalog -------------------------------------------------

CATALOG = {"schema": "catalog.v1", "products": [
    {"ma": "A29", "priceUsd": 31, "status": "available"},
    {"ma": "S06", "priceUsd": 25, "status": "available"},
    {"ma": "K03", "priceUsd": 52, "status": "hidden"},
]}


def test_load_live_catalog_products_and_map(tmp_path: Path) -> None:
    f = tmp_path / "cat.json"
    f.write_text(json.dumps(CATALOG), encoding="utf-8")
    assert hp.load_live_catalog(f) == {"A29": Decimal("31"), "S06": Decimal("25")}
    g = tmp_path / "map.json"
    g.write_text(json.dumps({"prices": {"a29": "31", "x": ""}}), encoding="utf-8")
    assert hp.load_live_catalog(g) == {"A29": Decimal("31")}


def test_already_live_not_quoted() -> None:
    sheet = hp.build([A29, H02], {}, POLICY, live_catalog={"A29": Decimal("31")})
    a29 = next(p for p in sheet["proposals"] if p["ma"] == "A29")
    assert a29["status"] == "already-live" and a29["live_usd"] == 31.0
    assert a29["tiered_usd"] is None and a29["flat25_usd"] is None
    assert a29["flags"][0] == "already live $31"
    assert sheet["already_live"] == {"A29": 31.0} and sheet["needs_boss"] == ["H02"]
    assert "already live $31" in hp.markdown(sheet)


def test_without_catalog_unchanged() -> None:
    a = hp.build([A29, H02, G01], {}, POLICY)
    b = hp.build([A29, H02, G01], {}, POLICY, live_catalog={})
    strip = lambda s: [{k: v for k, v in p.items()} for p in s["proposals"]]  # noqa: E731
    assert strip(a) == strip(b) and a["live_catalog_used"] is False and b["already_live"] == {}


def test_cli_live_catalog(tmp_path: Path) -> None:
    intake = tmp_path / "intake.json"
    intake.write_text(json.dumps({"submissions": [A29, G01]}), encoding="utf-8")
    live = tmp_path / "live.json"
    live.write_text(json.dumps({"prices": {}}), encoding="utf-8")
    cat = tmp_path / "cat.json"
    cat.write_text(json.dumps(CATALOG), encoding="utf-8")
    held = tmp_path / "held.json"
    held.write_text(json.dumps({"heldIncomplete": ["S14"], "neverList": []}), encoding="utf-8")
    out = tmp_path / "s.json"
    before = cat.read_bytes()
    assert hp.main(["--intake", str(intake), "--live", str(live), "--held", str(held),
                    "--live-catalog", str(cat), "--out-json", str(out)]) == 0
    s = json.loads(out.read_text(encoding="utf-8"))
    assert s["already_live"] == {"A29": 31.0} and s["needs_boss"] == ["G01"]
    assert cat.read_bytes() == before


def test_piece55_verdicts_and_proposal_dir(tmp_path):
    rows = [
        {"ma": "A98", "kind": "A", "cost_cny": "100"},   # placeholder ¥
        {"ma": "H98", "kind": "H", "cost_cny": ""},      # blank ¥
        {"ma": "G98", "kind": "G", "cost_cny": "100"},   # no approved G weight
    ]
    intake = tmp_path / "intake.json"; intake.write_text(json.dumps(rows))
    live = tmp_path / "live.json"; live.write_text(json.dumps({"prices": {}}))
    held = tmp_path / "held.json"; held.write_text(json.dumps({"heldIncomplete": ["A98"], "neverList": []}))
    outdir = tmp_path / "out" / "proposals"
    assert hp.main(["--intake", str(intake), "--live", str(live), "--held", str(held),
                    "--proposal-dir", str(outdir), "--date", "2000-01-01"]) == 0
    sheet = json.loads((outdir / "held-price-proposal-2000-01-01.json").read_text())
    v = sheet["verdicts"]
    assert v["A98"].startswith("$") and v["H98"] == "NEEDS_INPUT" and v["G98"] == "NEEDS_INPUT"
    assert "Verdicts:" in (outdir / "held-price-proposal-2000-01-01.md").read_text()
