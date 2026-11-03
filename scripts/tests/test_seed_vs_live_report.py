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
    assert r.load(r.LIVE)["S06"] == 25

def test_writes_nothing(tmp_path, capsys):
    before = r.SEED.read_bytes()
    assert r.main([]) == 0
    assert r.SEED.read_bytes() == before
    assert "| mã |" in capsys.readouterr().out
