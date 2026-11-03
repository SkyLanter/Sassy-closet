"""Synthetic-caption tests for scripts/caption_lint.py (piece 31)."""
import csv
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import caption_lint as cl  # noqa: E402

FX = ROOT / "data" / "fixtures" / "caption-lint"
LIVE = {"A09": 30.0, "D06": 28.0, "S06": 25.0}
KNOWN = {"A09", "D06", "S06", "B01", "S15", "K06", "C07"}
HELD = {"S15", "K06"}
APPROVED = {"S15": 30.0}


def lint(text):
    return cl.lint_post("u", "fb", text, LIVE, KNOWN, HELD, APPROVED)


def has(r, reason):
    return any(x.startswith(reason) for x in r.reasons)


def test_clean_pass():
    r = lint("Mã A09\nÁo croptop\nGiá $30")
    assert r.status == "PASS" and r.reasons == []


def test_missing_ma():
    r = lint("Áo xinh lắm nè, mãi yêu\nGiá $30")
    assert r.status == "FAIL" and has(r, "missing_ma")


@pytest.mark.parametrize("line", ["Ma D06", "ma D06", "MÃ D06", "Mã: D06", "Mã D 06", "M D06", "Mã d06"])
def test_malformed_ma_normalized(line):
    r = lint(f"{line}\nGiá $28")
    assert r.ma == "D06" and r.status == "WARN" and has(r, "malformed_ma")


def test_ma_not_line_1():
    r = lint("Hàng mới về\nMã A09\nGiá $30")
    assert r.status == "WARN" and has(r, "malformed_ma:not_line_1")


def test_unknown_ma_typo():
    r = lint("Mã A90\nGiá $30")
    assert r.status == "FAIL" and has(r, "unknown_ma")


def test_extra_intake_codes_known():
    r = cl.lint_post("u", "fb", "Mã C07\nGiá $20", LIVE, KNOWN, HELD, APPROVED)
    assert not has(r, "unknown_ma") and has(r, "not_live") and r.status == "WARN"


def test_missing_gia():
    r = lint("Mã A09\nInbox nha")
    assert r.status == "FAIL" and has(r, "missing_gia")


@pytest.mark.parametrize("g", ["Giá $ 30", "Gia $30", "giá: 30$", "Giá 30 đô", "GIÁ $30", "Giá 30 USD"])
def test_malformed_gia(g):
    r = lint(f"Mã A09\n{g}")
    assert r.gia_usd == 30.0 and r.status == "WARN" and has(r, "malformed_gia")


def test_gia_word_without_amount_fails():
    r = lint("Mã A09\nGiá inbox")
    assert r.status == "FAIL" and has(r, "malformed_gia")


def test_live_price_differs():
    r = lint("Mã D06\nGiá $31")
    assert r.status == "FAIL" and has(r, "gia_differs_live") and r.expected_usd == 28.0


def test_s06_must_be_25():
    assert lint("Mã S06\nGiá $25").status == "PASS"
    r = lint("Mã S06\nGiá $27")
    assert r.status == "FAIL" and has(r, "s06_not_25")


def test_s06_locked_even_if_snapshot_says_otherwise():
    r = cl.lint_post("u", "ig", "Mã S06\nGiá $30", {"S06": 30.0}, {"S06"}, set(), {})
    assert has(r, "s06_not_25")


def test_held_gia_differs_and_ok():
    assert lint("Mã S15\nGiá $30").status == "PASS"
    r = lint("Mã S15\nGiá $35")
    assert r.status == "FAIL" and has(r, "held_gia_differs")


def test_held_without_approved_warns():
    r = lint("Mã K06\nGiá $40")
    assert r.status == "WARN" and has(r, "held_no_approved_gia")


def _cli(tmp_path, posts_path, *extra):
    return cl.main([str(posts_path), "--snapshot", str(FX / "snapshot.json"),
                    "--held", str(FX / "held.json"), "--approved", str(FX / "approved.json"), *extra])


def test_cli_json_fixture(tmp_path, capsys):
    rc = _cli(tmp_path, FX / "captions.json", "--json")
    out = json.loads(capsys.readouterr().out)
    assert rc == 2
    assert out["counts"] == {"PASS": 2, "WARN": 2, "FAIL": 6}
    by = {p["url"]: p["status"] for p in out["posts"]}
    assert by["fb/ok"] == "PASS" and by["ig/ma-typo"] == "FAIL"


def test_cli_csv_and_exit_codes(tmp_path, capsys):
    p = tmp_path / "c.csv"
    with p.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["url", "platform", "text"])
        w.writeheader()
        w.writerow({"url": "a", "platform": "FB", "text": "Mã A09\nGiá $30"})
    assert _cli(tmp_path, p) == 0
    w2 = tmp_path / "w.csv"
    w2.write_text('url,platform,text\nb,ig,"Ma A09\nGiá $30"\n', encoding="utf-8")
    assert _cli(tmp_path, w2) == 1
    assert _cli(tmp_path, w2, "--warn-ok") == 0
    capsys.readouterr()


def test_cli_bad_input_exit_2(tmp_path, capsys):
    p = tmp_path / "bad.json"
    p.write_text('[{"url": "x"}]', encoding="utf-8")
    assert _cli(tmp_path, p) == 2


def test_no_private_fields_in_fixtures_or_output(capsys):
    for f in FX.iterdir():
        assert not cl.PRIVATE.search(f.read_text(encoding="utf-8")), f
    _cli(None, FX / "captions.json")
    assert not cl.PRIVATE.search(capsys.readouterr().out)
