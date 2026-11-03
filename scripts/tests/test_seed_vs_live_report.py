import importlib.util, json
from pathlib import Path
spec = importlib.util.spec_from_file_location("r", Path(__file__).resolve().parents[1] / "seed_vs_live_report.py")
r = importlib.util.module_from_spec(spec); spec.loader.exec_module(r)

def test_kinds(tmp_path):
    s = tmp_path/"s.json"; l = tmp_path/"l.json"
    s.write_text(json.dumps({"products":[{"ma":"S006","priceUsd":25},{"ma":"A1","priceUsd":10},{"ma":"K03","priceUsd":5}]}))
    l.write_text(json.dumps({"products":[{"ma":"S06","priceUsd":25},{"ma":"A01","priceUsd":12},{"ma":"B01","priceUsd":9}]}))
    kinds = {m:k for m,_,_,k in r.compare(r.load(s), r.load(l))}
    assert kinds == {"S06":"match","A01":"price-diff","K03":"seed-only","B01":"live-only"}

def test_s06_live_25():
    assert r.load(r.LIVE)["S06"] == [25]


def test_later_lock_does_not_hide_an_earlier_live_spelling(tmp_path):
    seed = tmp_path / "s.json"
    live = tmp_path / "l.json"
    seed.write_text(json.dumps({"products": [{"ma": "S06", "priceUsd": 25}]}))
    live.write_text(json.dumps({"products": [
        {"ma": "S006", "priceUsd": 30},
        {"ma": "S06", "priceUsd": 25},
    ]}))
    row = {ma: (seed_prices, live_prices, kind) for ma, seed_prices, live_prices, kind in r.compare(r.load(seed), r.load(live))}
    assert row["S06"] == ([25], [30, 25], "price-diff")
    assert r._cell([30, 25]) == "$30, $25"


def test_later_lock_does_not_hide_an_earlier_seed_spelling(tmp_path):
    seed = tmp_path / "s.json"
    live = tmp_path / "l.json"
    seed.write_text(json.dumps({"products": [
        {"ma": "s006", "priceUsd": 30},
        {"ma": "S06", "priceUsd": 25},
    ]}))
    live.write_text(json.dumps({"products": [{"ma": "S06", "priceUsd": 25}]}))
    row = {ma: kind for ma, _seed, _live, kind in r.compare(r.load(seed), r.load(live))}
    assert row["S06"] == "price-diff"


def test_same_price_on_every_spelling_still_matches(tmp_path):
    seed = tmp_path / "s.json"
    live = tmp_path / "l.json"
    seed.write_text(json.dumps({"products": [{"ma": "S06", "priceUsd": 25.0}]}))
    live.write_text(json.dumps({"products": [
        {"ma": "S006", "priceUsd": 25},
        {"ma": "S06", "priceUsd": 25},
    ]}))
    row = {ma: kind for ma, _seed, _live, kind in r.compare(r.load(seed), r.load(live))}
    assert row["S06"] == "match"


def test_bool_price_does_not_match_one_dollar(tmp_path):
    seed = tmp_path / "s.json"
    live = tmp_path / "l.json"
    seed.write_text(json.dumps({"products": [{"ma": "A01", "priceUsd": True}]}))
    live.write_text(json.dumps({"products": [{"ma": "A01", "priceUsd": 1}]}))
    row = {ma: kind for ma, _seed, _live, kind in r.compare(r.load(seed), r.load(live))}
    assert row["A01"] == "price-diff"


def test_table_shows_every_disagreeing_spelling(tmp_path, capsys):
    seed = tmp_path / "s.json"
    live = tmp_path / "l.json"
    seed.write_text(json.dumps({"products": [{"ma": "S06", "priceUsd": 25}]}))
    live.write_text(json.dumps({"products": [
        {"ma": "S006", "priceUsd": 30},
        {"ma": "S06", "priceUsd": 25},
    ]}))
    before_seed = seed.read_bytes()
    before_live = live.read_bytes()
    assert r.main(["--seed", str(seed), "--live", str(live)]) == 0
    out = capsys.readouterr().out
    assert "| S06 | $25 | $30, $25 | price-diff |" in out
    assert seed.read_bytes() == before_seed
    assert live.read_bytes() == before_live

def test_writes_nothing(tmp_path, capsys):
    before = r.SEED.read_bytes()
    assert r.main([]) == 0
    assert r.SEED.read_bytes() == before
    assert "| mã |" in capsys.readouterr().out
