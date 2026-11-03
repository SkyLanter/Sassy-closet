"""Piece 33: rules folded from caption_gia_check.py into caption_lint.py, and the shim."""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import caption_gia_check as shim  # noqa: E402
import caption_lint as cl  # noqa: E402

LIVE = {"S13": 26.0, "S06": 25.0}
KNOWN = {"S13", "S06", "S15", "Z99"}


def lint(text, **kw):
    return cl.lint_post("u", "fb", text, LIVE, KNOWN, {"S15"}, {"S15": 30.0}, **kw)


def has(r, k):
    return any(x.startswith(k) for x in r.reasons)


def test_never_list_fails():
    r = lint("Mã Z99\nGiá $10", never={"Z99"})
    assert r.status == "FAIL" and has(r, "never_list")


def test_strict_first_line():
    t = "ÁO KIỂU\nMã S13\nGiá $26"
    assert lint(t).status == "WARN"
    r = lint(t, strict_first_line=True)
    assert r.status == "FAIL" and has(r, "malformed_ma:not_line_1")


def test_ig_wrapper_and_pipes():
    t = '0 likes, 0 comments - sassycloset.boutique on September 25, 2026: "Mã S13 | x | Giá $26". '
    assert lint(t).status == "PASS"


def test_loaders_txt_html_tsv_legacy_json(tmp_path):
    (tmp_path / "a.txt").write_text("Mã S13\nGiá $26\n---\nMã S06\nGiá $25\n", encoding="utf-8")
    (tmp_path / "raw-X.html").write_text(
        '<meta property="og:description" content="M\u00e3 S13\nGi\u00e1 $26" />', encoding="utf-8")
    (tmp_path / "m.tsv").write_text("S13\tabc\t26\tMã S13 Giá $26\n", encoding="utf-8")
    (tmp_path / "d.json").write_text(json.dumps({"k": "Mã S13\nGiá $26"}), encoding="utf-8")
    assert [p["url"] for p in cl.load_posts(tmp_path / "a.txt")] == ["a#1", "a#2"]
    assert cl.load_posts(tmp_path / "raw-X.html")[0]["url"] == "X"
    assert cl.load_posts(tmp_path / "m.tsv")[0]["url"] == "S13-abc"
    assert cl.load_posts(tmp_path / "d.json")[0]["url"] == "k"


def _files(tmp_path):
    (tmp_path / "live.json").write_text(json.dumps({"prices": {"S13": 26}}))
    (tmp_path / "held.json").write_text(json.dumps({"heldIncomplete": ["S15"], "neverList": ["Z99"]}))
    (tmp_path / "ap.json").write_text(json.dumps({"approvedGia": {"S15": 30}}))
    (tmp_path / "ok.txt").write_text("Mã S13\nGiá $26\n", encoding="utf-8")
    (tmp_path / "warn.txt").write_text("Mã S13\nGiá $ 26\n", encoding="utf-8")
    (tmp_path / "bad.txt").write_text("Mã Z99\nGiá $10\n", encoding="utf-8")
    return ["--live", str(tmp_path / "live.json"), "--held", str(tmp_path / "held.json"),
            "--approved", str(tmp_path / "ap.json")]


def test_linter_cli_live_multi_file_never(tmp_path):
    a = _files(tmp_path)
    assert cl.main([str(tmp_path / "ok.txt"), *a]) == 0
    assert cl.main([str(tmp_path / "ok.txt"), str(tmp_path / "warn.txt"), *a]) == 1
    assert cl.main([str(tmp_path / "ok.txt"), str(tmp_path / "warn.txt"), *a, "--warn-ok"]) == 0
    assert cl.main([str(tmp_path / "bad.txt"), *a]) == 2


def test_shim_old_exit_codes_and_flags(tmp_path):
    a = _files(tmp_path)
    assert shim.main([str(tmp_path / "ok.txt"), str(tmp_path / "warn.txt"), *a]) == 0  # old: never non-zero without a FAIL
    assert shim.main([str(tmp_path / "bad.txt"), *a]) == 1
    (tmp_path / "late.txt").write_text("ÁO\nMã S13\nGiá $26\n", encoding="utf-8")
    assert shim.main([str(tmp_path / "late.txt"), *a]) == 0
    out = tmp_path / "o.json"
    assert shim.main([str(tmp_path / "late.txt"), *a, "--strict-first-line", "--out-json", str(out),
                      "--out-md", str(tmp_path / "o.md")]) == 1
    assert json.loads(out.read_text())["posts"][0]["issues"] == ["ma_not_first_line"]
    assert "shim over scripts/caption_lint.py" in (tmp_path / "o.md").read_text(encoding="utf-8")


def test_shim_runs_as_script(tmp_path):
    a = _files(tmp_path)
    p = subprocess.run([sys.executable, str(ROOT / "scripts" / "caption_gia_check.py"),
                        str(tmp_path / "bad.txt"), *a], capture_output=True, text=True)
    assert p.returncode == 1 and "never_list" in p.stdout


def test_shim_canonical_old_names():
    from held_policy import HeldPolicy
    pol = HeldPolicy(held=("S15",), never_list=())
    r = shim.check_post("p", "Mã S13\nGiá $30", LIVE, pol, {})
    assert r.issues == ["price_mismatch"] and r.expected_usd == 26
    assert shim.check_post("p", "Ma S13\nGiá $ 26", LIVE, pol, {}).status == "PASS"  # old tolerated loose forms
