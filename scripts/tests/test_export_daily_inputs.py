import json
from pathlib import Path

import pytest

import daily_shop_check as d
import export_daily_inputs as x

ROOT = Path(__file__).resolve().parents[2]
FIXTURE = ROOT / "data" / "fixtures" / "daily-inputs-synthetic.json"
ALLOWED_ITEM_KEYS = {"ma", "live", "sellUsd", "held"}


def dirty_inputs(tmp_path):
    """Synthetic inputs full of private fields the export must drop."""
    cat = {"products": [
        {"ma": "Z01", "priceUsd": 30, "status": "available", "titleVn": "Ao", "sourceLink": "https://e.tb.cn/x",
         "costCny": 88, "supplier": "shop 1688", "buyer": {"phone": "555-0100", "email": "a@b.c"}},
        {"ma": "z02", "priceUsd": "41.5", "status": "available", "link": "http://item.taobao.com/1"},
        {"ma": "S06", "priceUsd": 25, "status": "available"},
        {"ma": "Z03", "priceUsd": 19, "status": "sold"},
    ]}
    intake = {"submissions": [
        {"ma": "Z90", "cost_cny": 120, "cost_usd": 17, "link": "https://detail.1688.com/9", "customer": "Lan"},
        {"ma": "", "cost_cny": 1}]}
    held = {"heldIncomplete": ["Z90"], "neverList": []}
    report = {"overall": "WARN", "sections": [
        {"name": "too_cheap", "status": "WARN", "warn": ["4 skipped (missing kg/\u00a5)"], "info": ["cost 88"]},
        {"name": "captions", "status": "PASS", "info": ["https://x"]}]}
    paths = {}
    for k, v in {"live": cat, "intake": intake, "held": held, "report": report}.items():
        paths[k] = tmp_path / f"{k}.json"
        paths[k].write_text(json.dumps(v, ensure_ascii=False), encoding="utf-8")
    return paths


def export(tmp_path, report=True):
    p = dirty_inputs(tmp_path)
    out = tmp_path / "daily-inputs"
    argv = ["--live", str(p["live"]), "--held", str(p["held"]), "--intake", str(p["intake"]),
            "--date", "2026-01-02", "--out-dir", str(out)]
    if report:
        argv += ["--report", str(p["report"])]
    rc = x.main(argv)
    return rc, out


def test_export_keeps_only_allow_list_and_matches_fixture(tmp_path):
    rc, out = export(tmp_path, report=False)
    assert rc == 0 and [f.name for f in out.iterdir()] == ["snapshot.json"]
    snap = json.loads((out / "snapshot.json").read_text(encoding="utf-8"))
    fix = json.loads(FIXTURE.read_text(encoding="utf-8"))
    assert sorted(snap["items"], key=lambda i: i["ma"]) == sorted(fix["items"], key=lambda i: i["ma"])
    assert all(set(i) == ALLOWED_ITEM_KEYS for i in snap["items"])
    assert set(snap) == {"schema", "date", "items", "counts"}


def test_export_has_no_private_terms(tmp_path):
    rc, out = export(tmp_path)
    text = (out / "snapshot.json").read_text(encoding="utf-8")
    assert rc == 0 and x.privacy_scan(text) == []
    snap = json.loads(text)
    assert snap["checks"] == [{"name": "too_cheap", "status": "WARN"}, {"name": "captions", "status": "PASS"}]
    for bad in ("Lan", "555", "88", "120", "Ao", "kg"):
        assert bad not in text


def test_sold_item_not_live_and_not_exported(tmp_path):
    rc, out = export(tmp_path)
    mas = [i["ma"] for i in json.loads((out / "snapshot.json").read_text())["items"]]
    assert "Z03" not in mas and "Z02" in mas


def test_privacy_guard_blocks_write(tmp_path, monkeypatch):
    real = x.build

    def leaky(*a, **k):
        s = real(*a, **k)
        s["date"] = "https://leak"
        return s
    monkeypatch.setattr(x, "build", leaky)
    rc, out = export(tmp_path)
    assert rc == 2 and not out.exists()


def test_out_dir_must_be_daily_inputs(tmp_path):
    p = dirty_inputs(tmp_path)
    with pytest.raises(SystemExit) as e:
        x.main(["--live", str(p["live"]), "--date", "2026-01-02", "--out-dir", str(tmp_path / "elsewhere")])
    assert e.value.code == 2


def test_bad_ma_in_catalog_is_error(tmp_path):
    cat = tmp_path / "c.json"
    cat.write_text(json.dumps({"products": [{"ma": "../etc", "priceUsd": 1}]}))
    assert x.main(["--live", str(cat), "--held", str(dirty_inputs(tmp_path)["held"]), "--date", "2026-01-02",
                   "--out-dir", str(tmp_path / "daily-inputs")]) == 2


def reduced(snap_path, *extra):
    return d.main(["--reduced", "--snapshot", str(snap_path), *extra])


def write_snap(tmp_path, **mut):
    s = json.loads(FIXTURE.read_text(encoding="utf-8"))
    for ma, fields in mut.items():
        next(i for i in s["items"] if i["ma"] == ma).update(fields)
    p = tmp_path / "snap.json"
    p.write_text(json.dumps(s))
    return p


def test_reduced_fixture_passes_and_cost_checks_skip(tmp_path, capsys):
    out = tmp_path / "r.json"
    assert reduced(FIXTURE, "--out-json", str(out)) == 0
    r = json.loads(out.read_text())
    st = {s["name"]: s["status"] for s in r["sections"]}
    assert st == {"too_cheap": "SKIP-NO-COSTS", "held_sheet": "SKIP-NO-COSTS",
                  "intake_gaps": "SKIP-NO-COSTS", "snapshot_rules": "PASS",
                  "held_photos": "SKIP"}
    assert r["overall"] == "PASS" and r["mode"] == "reduced"


def test_reduced_held_live_fails(tmp_path):
    assert reduced(write_snap(tmp_path, Z90={"live": True, "sellUsd": 30})) == 2


def test_reduced_s06_drift_fails(tmp_path):
    assert reduced(write_snap(tmp_path, S06={"sellUsd": 27})) == 2


def test_reduced_missing_price_warns_and_warn_ok(tmp_path):
    p = write_snap(tmp_path, Z01={"sellUsd": None})
    assert reduced(p) == 1
    assert reduced(p, "--warn-ok") == 0


def test_reduced_bad_snapshot_fails_but_cost_checks_never_fail(tmp_path):
    bad = tmp_path / "bad.json"
    bad.write_text("{}")
    out = tmp_path / "r.json"
    assert reduced(bad, "--out-json", str(out)) == 2
    r = json.loads(out.read_text())
    assert [s["status"] for s in r["sections"][:3]] == ["SKIP-NO-COSTS"] * 3


@pytest.mark.parametrize("argv", [["--reduced"], ["--reduced", "--snapshot", "s", "--costs", "c"], ["--live", "x"]])
def test_reduced_usage_errors_exit_2(argv):
    with pytest.raises(SystemExit) as e:
        d.main(argv)
    assert e.value.code == 2
