"""Piece 46 held_photo_public_watch: offline fixture / mocked HEAD only, no network."""
import json
import urllib.request

import pytest

import daily_shop_check as d
import held_photo_check as hpc
import held_photo_public_watch as w

BASE = "https://blob.example"


@pytest.fixture(autouse=True)
def no_network(monkeypatch):
    def boom(*a, **k):
        raise AssertionError("network used in test")
    monkeypatch.setattr(urllib.request, "urlopen", boom)


def held_file(tmp_path, mas=("S14", "A24", "A25", "G01")):
    p = tmp_path / "held.json"
    p.write_text(json.dumps({"heldIncomplete": list(mas), "neverList": []}))
    return p


def fixture_known():
    return {"products/S14/cover.jpg": 200, "products/A24/cover.jpg": 200,
            "products/A25/photo-2.jpg": 200, "products/A25/cover.jpg": 404,
            "products/S14/photo-2.jpg": 404, "products/A24/photo-2.jpg": 404,
            "products/G01/cover.jpg": 404, "products/G01/photo-2.jpg": 404}


def test_shared_held_list_from_ts():
    held, src = w.shared_held()
    assert {"S14", "A24", "A25"} <= set(held)
    assert src.endswith(".json")


def test_offline_known_case():
    rep = w.run(["S14", "A24", "A25", "G01"], {}, fixture=fixture_known(), blob_base=BASE)
    assert rep["schema"] == "held-photos/v1"
    assert rep["exposedMas"] == ["A24", "A25", "S14"]
    assert rep["watch"]["mode"] == "offline"
    assert rep["watch"]["stillExposedKnown"] == ["S14", "A24", "A25"]
    assert rep["watch"]["newlyExposed"] == []
    assert rep["method"] == "HEAD" and rep["writes"] == "none"


def test_newly_exposed_flagged():
    fx = fixture_known() | {"products/G01/cover.jpg": 200}
    rep = w.run(["S14", "A24", "A25", "G01"], {}, fixture=fx, blob_base=BASE)
    assert rep["watch"]["newlyExposed"] == ["G01"]
    assert "NEW: G01" in w.summary_line(rep)


def test_unknown_url_in_fixture_is_error_not_exposed():
    rep = w.run(["K03"], {}, fixture={}, blob_base=BASE)
    assert rep["exposed"] == [] and len(rep["errors"]) == 2
    assert all(e["status"] == "error: not-in-fixture" for e in rep["errors"])


def test_fixture_full_url_key():
    url = f"{BASE}/sassy-closet-shop/products/S14/cover.jpg"
    rep = w.run(["S14"], {}, fixture={url: 200}, blob_base=BASE)
    assert rep["exposedMas"] == ["S14"]


def test_non_held_never_checked():
    rep = w.run(["S14"], {"catalog": ["/products/A01/cover.jpg", "/products/S14/x.jpg"]},
                fixture={"products/S14/x.jpg": 200}, blob_base=BASE, probe_default=False)
    assert [r["url"].rsplit("/products/", 1)[1] for r in rep["rows"]] == ["S14/x.jpg"]


def test_live_mode_uses_head_only(monkeypatch):
    seen = []

    class R:
        status = 200
        def __enter__(self): return self
        def __exit__(self, *a): return False

    def fake(req, timeout=0):
        seen.append(req.get_method())
        return R()
    monkeypatch.setattr(urllib.request, "urlopen", fake)
    rep = w.run(["S14"], {}, blob_base=BASE, sleep=lambda s: None)
    assert seen == ["HEAD", "HEAD"] and rep["watch"]["mode"] == "live"


def test_rate_cap():
    with pytest.raises(ValueError):
        w.run(["S14"], {}, fixture={}, rate=5)


def test_cli_offline_exit_and_json(tmp_path, capsys):
    fx = tmp_path / "fx.json"
    fx.write_text(json.dumps(fixture_known()))
    out = tmp_path / "r.json"
    rc = w.main(["--held", str(held_file(tmp_path)), "--fixture", str(fx), "--blob-base", BASE, "--out-json", str(out)])
    assert rc == 1
    assert json.loads(out.read_text())["exposedMas"] == ["A24", "A25", "S14"]
    assert "offline" in capsys.readouterr().out


def test_cli_clean_exit_zero(tmp_path):
    fx = tmp_path / "fx.json"
    fx.write_text(json.dumps({k: 404 for k in fixture_known()}))
    assert w.main(["--held", str(held_file(tmp_path)), "--fixture", str(fx), "--blob-base", BASE]) == 0


def test_cli_bad_input(tmp_path):
    assert w.main(["--held", str(tmp_path / "missing.json"), "--fixture", str(tmp_path / "x")]) == 2
    bad = tmp_path / "fx.json"
    bad.write_text("[1]")
    assert w.main(["--held", str(held_file(tmp_path)), "--fixture", str(bad)]) == 2


def test_no_write_methods_in_source():
    src = open(w.__file__, encoding="utf-8").read() + open(hpc.__file__, encoding="utf-8").read()
    for bad in ('method="DELETE"', 'method="PUT"', 'method="POST"', "@vercel/blob", "del("):
        assert bad not in src


def test_daily_section_warn_never_fail(tmp_path):
    fx = tmp_path / "fx.json"
    fx.write_text(json.dumps(fixture_known()))
    a = d.argparse.Namespace(held_photo_watch_held=held_file(tmp_path), held_photo_watch_catalog=[],
                             held_photo_watch_health=[], held_photo_watch_files=[],
                             held_photo_watch_fixture=fx)
    sec = d.held_photo_watch_section(a)
    assert sec["name"] == "held_photo_watch" and sec["status"] == "WARN" and sec["fail"] == []
    assert sec["detail"]["exposedMas"] == ["A24", "A25", "S14"]
    assert any("Boss's call" in i for i in sec["info"])


def test_daily_section_error_is_warn(tmp_path):
    a = d.argparse.Namespace(held_photo_watch_held=tmp_path / "nope.json", held_photo_watch_catalog=[],
                             held_photo_watch_health=[], held_photo_watch_files=[],
                             held_photo_watch_fixture=None)
    sec = d.held_photo_watch_section(a)
    assert sec["status"] == "WARN" and sec["fail"] == []
