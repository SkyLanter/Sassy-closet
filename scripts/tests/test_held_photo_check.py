"""held_photo_check + held_photos section. Mocked HTTP only: no network."""
import json
import urllib.request

import pytest

import daily_shop_check as d
import held_photo_check as h

BASE = "https://blob.example"


@pytest.fixture(autouse=True)
def no_network(monkeypatch):
    def boom(*a, **k):
        raise AssertionError("network used in test")
    monkeypatch.setattr(urllib.request, "urlopen", boom)


def held_file(tmp_path, mas=("S14", "A25", "G01")):
    p = tmp_path / "held.json"
    p.write_text(json.dumps({"heldIncomplete": list(mas), "neverList": []}))
    return p


def test_ma_of_paths():
    assert h.ma_of("sassy-closet-shop/products/S14/cover.jpg") == "S14"
    assert h.ma_of("/products/A25/photo-2.jpg") == "A25"
    assert h.ma_of("A01/cover.jpg") == "A01"
    assert h.ma_of("sassy-closet-shop/catalog.json") is None


def test_to_url_normalises_all_path_styles():
    p = "sassy-closet-shop/"
    want = BASE + "/sassy-closet-shop/products/S14/cover.jpg"
    assert h.to_url("sassy-closet-shop/products/S14/cover.jpg", BASE, p) == want
    assert h.to_url("/products/S14/cover.jpg", BASE, p) == want
    assert h.to_url("S14/cover.jpg", BASE, p) == want
    assert h.to_url("https://x/y.jpg", BASE, p) == "https://x/y.jpg"


def test_collect_keeps_only_held_and_dedupes_sources():
    src = {"health-listing": ["sassy-closet-shop/products/S14/cover.jpg", "sassy-closet-shop/products/A01/cover.jpg",
                              "sassy-closet-shop/catalog.json"],
           "catalog": ["/products/S14/cover.jpg", "/products/A01/photo-2.jpg"]}
    urls = h.collect(["S14", "A25"], src, BASE, "sassy-closet-shop/", False)
    assert list(urls) == [BASE + "/sassy-closet-shop/products/S14/cover.jpg"]
    assert urls[BASE + "/sassy-closet-shop/products/S14/cover.jpg"]["sources"] == ["health-listing", "catalog"]


def test_probe_default_adds_cover_and_photo2_per_held():
    urls = h.collect(["G01"], {}, BASE, "sassy-closet-shop/", True)
    assert sorted(u.rsplit("/", 1)[1] for u in urls) == ["cover.jpg", "photo-2.jpg"]


def test_check_uses_head_status_and_rate_limits():
    calls, sleeps = [], []
    urls = h.collect(["S14", "A25"], {"x": ["S14/cover.jpg", "A25/cover.jpg", "A25/photo-2.jpg"]}, BASE, "sassy-closet-shop/", False)
    rows = h.check(urls, head=lambda u: calls.append(u) or (200 if "S14" in u else 404), rate=2.0, sleep=sleeps.append)
    assert len(calls) == 3 and sleeps == [0.5, 0.5]
    assert [r["ma"] for r in rows if r["exposed"]] == ["S14"]


def test_head_status_sends_head_only(monkeypatch):
    seen = []

    class R:
        status = 200
        def __enter__(self): return self
        def __exit__(self, *a): return False

    monkeypatch.setattr(urllib.request, "urlopen", lambda req, timeout: seen.append(req.get_method()) or R())
    assert h.head_status(BASE + "/a.jpg") == 200 and seen == ["HEAD"]


def test_head_status_maps_http_error_and_failures(monkeypatch):
    import urllib.error

    def e404(req, timeout):
        raise urllib.error.HTTPError(req.full_url, 404, "nf", {}, None)
    monkeypatch.setattr(urllib.request, "urlopen", e404)
    assert h.head_status(BASE + "/a.jpg") == 404

    def eto(req, timeout):
        raise TimeoutError()
    monkeypatch.setattr(urllib.request, "urlopen", eto)
    assert h.head_status(BASE + "/a.jpg") == "error: TimeoutError"


def test_main_end_to_end_mocked(tmp_path, monkeypatch):
    health = tmp_path / "health.json"
    health.write_text(json.dumps({"blob": {"listed": ["sassy-closet-shop/products/S14/cover.jpg",
                                                      "sassy-closet-shop/products/A01/cover.jpg"]}}))
    monkeypatch.setattr(h, "head_status", lambda u: 200)
    monkeypatch.setattr(h.time, "sleep", lambda s: None)
    out = tmp_path / "rep.json"
    rc = h.main(["--held", str(held_file(tmp_path)), "--health", str(health), "--blob-base", BASE,
                 "--out-json", str(out)])
    rep = json.loads(out.read_text())
    assert rc == 1 and rep["exposedMas"] == ["S14"] and rep["method"] == "HEAD" and rep["writes"] == "none"


def test_main_rejects_fast_rate_and_bad_held(tmp_path):
    with pytest.raises(SystemExit):
        h.main(["--held", str(held_file(tmp_path)), "--rate", "5"])
    bad = tmp_path / "bad.json"
    bad.write_text("{}")
    assert h.main(["--held", str(bad)]) == 2


def rep(exposed=(), errors=()):
    return {"schema": "held-photos/v1", "held": ["S14"], "checked": 2, "checkedAt": "t",
            "exposed": [{"ma": m, "url": f"{BASE}/x/products/{m}/cover.jpg"} for m in exposed],
            "exposedMas": sorted(set(exposed)),
            "errors": [{"ma": m, "url": f"{BASE}/x/products/{m}/cover.jpg", "status": "error: X"} for m in errors]}


def test_section_exposed_is_warn_never_fail():
    sec = d.judge_held_photos(rep(exposed=["S14", "A24"]))
    assert sec["status"] == "WARN" and not sec["fail"] and "S14/cover.jpg" in sec["warn"][0]


def test_section_clean_is_pass_and_errors_are_info():
    sec = d.judge_held_photos(rep(errors=["S14"]))
    assert sec["status"] == "PASS" and any("not checked cleanly" in i for i in sec["info"])


def test_section_bad_report_raises():
    with pytest.raises(ValueError):
        d.judge_held_photos({"schema": "nope"})


def test_reduced_mode_held_photos_is_skip():
    snap = {"schema": "daily-inputs/v1", "date": "x", "items": [{"ma": "S06", "live": True, "sellUsd": 25}]}
    secs = {s["name"]: s["status"] for s in d.reduced_sections(snap)}
    assert secs["held_photos"] == "SKIP"
    assert d.combine(d.reduced_sections(snap))["overall"] == "PASS"


def _e2e(tmp_path, report_text):
    live = tmp_path / "live.json"
    live.write_text(json.dumps({"products": [{"ma": "S06", "priceUsd": 25, "status": "available"}]}))
    costs = tmp_path / "costs.csv"
    costs.write_text("ma,intake_cny,kg\nS06,100,0.5\n")
    hp = tmp_path / "hp.json"
    hp.write_text(report_text)
    out = tmp_path / "r.json"
    rc = d.main(["--live", str(live), "--costs", str(costs), "--held-photos", str(hp), "--out-json", str(out)])
    s = json.loads(out.read_text())
    return rc, {x["name"]: x for x in s["sections"]}, s


def test_e2e_exposed_report_is_warn_section(tmp_path):
    rc, secs, s = _e2e(tmp_path, json.dumps(rep(exposed=["S14"])))
    assert secs["held_photos"]["status"] == "WARN" and s["overall"] in ("WARN", "FAIL")
    assert s["overall"] != "FAIL" or secs["too_cheap"]["status"] == "FAIL"


def test_e2e_broken_report_is_warn_not_fail(tmp_path):
    _, secs, _ = _e2e(tmp_path, "not json")
    assert secs["held_photos"]["status"] == "WARN" and not secs["held_photos"]["fail"]
