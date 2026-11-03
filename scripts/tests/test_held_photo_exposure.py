"""Placeholder tests for piece 95: held_photo_exposure.py (mocked fetch, no network)."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import held_photo_exposure as hpe  # noqa: E402
import boss_decisions as bd  # noqa: E402

B = "https://blob.example.invalid"
DATE = "2000-01-05"


def _root(tmp_path, day=DATE):
    dd = tmp_path / "data"; dd.mkdir(parents=True)
    (dd / "held.json").write_text(json.dumps({"heldIncomplete": ["X01", "X02", "X03"], "neverList": []}))
    q = tmp_path / "out/midnight-qc" / day; (q / "raw").mkdir(parents=True)
    (q / "pass1-raw.json").write_text(json.dumps({"heldblob": [
        [f"{B}/p/products/X01/cover.jpg", 200, "image/jpeg"],
        [f"{B}/p/products/X01/photo-2.jpg", 404, "text/plain"],
        [f"{B}/p/products/X02/cover.jpg", 404, "text/plain"],
        [f"{B}/p/products/Y09/cover.jpg", 200, "image/jpeg"]]}))
    (q / "raw/health-a.json").write_text(json.dumps({"blob": {"listed": ["p/products/X01/extra.jpg"]}}))
    return tmp_path


def _fetch(u):
    return 200 if u.endswith(("X01/cover.jpg", "X01/extra.jpg")) else 404


def test_collect_held_only_and_health_join(tmp_path):
    r = _root(tmp_path)
    urls, srcs = hpe.collect(r, DATE, hpe.load_held(r))
    assert sorted(urls) == ["X01", "X02"]
    assert f"{B}/p/products/X01/extra.jpg" in urls["X01"] and len(urls["X01"]) == 3
    assert any("pass1-raw.json" in s for s in srcs)


def test_main_writes_report_with_counts(tmp_path):
    r = _root(tmp_path)
    assert hpe.main(["--root", str(r), "--date", DATE], fetch=_fetch) == 1
    t = (r / "out/reports" / DATE / "HELD-PHOTOS.md").read_text()
    rows = hpe.parse_report(t)
    assert rows == {"X01": (3, 2), "X02": (1, 0), "X03": (0, 0)}
    assert "Exposed: X01" in t
    assert hpe.exposed_from_report(r / "out/reports" / DATE / "HELD-PHOTOS.md") == ["X01"]


def test_falls_back_to_earlier_midnight_day(tmp_path):
    r = _root(tmp_path, "2000-01-04")
    urls, _ = hpe.collect(r, DATE, ["X01"])
    assert "X01" in urls


def test_no_network_none_exposed(tmp_path):
    r = _root(tmp_path)
    assert hpe.main(["--root", str(r), "--date", DATE], fetch=lambda u: 404) == 0


def test_boss_decisions_uses_report_evidence(tmp_path):
    r = _root(tmp_path)
    hpe.main(["--root", str(r), "--date", DATE], fetch=_fetch)
    dig = "- [blob_photo_delete] X02  first_seen=?  source=out/muse/notes.md\n"
    D = bd.compile_decisions(r, DATE, dig)
    bp = {d["ma"]: d["ev"] for d in D if d["cat"] == "blob_photo_delete"}
    assert bp == {"X01": f"out/reports/{DATE}/HELD-PHOTOS.md", "X02": f"out/reports/{DATE}/HELD-PHOTOS.md"}


def test_boss_decisions_keeps_muse_without_report(tmp_path):
    dig = "- [blob_photo_delete] X02  first_seen=?  source=out/muse/notes.md\n"
    D = bd.compile_decisions(tmp_path, DATE, dig)
    assert [d["ev"] for d in D if d["cat"] == "blob_photo_delete"] == ["out/muse/notes.md"]
