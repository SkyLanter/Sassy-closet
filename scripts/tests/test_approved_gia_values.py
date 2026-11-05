"""A boolean approved Giá is not $1, and one junk value does not drop the rest."""
import json
from pathlib import Path

import pytest

import caption_gia_check as gia
import caption_lint
import meta_inventory as meta
from held_policy import HeldPolicy


def write_approved(tmp_path, gia_map):
    path = tmp_path / "approved.json"
    path.write_text(json.dumps({"approvedGia": gia_map}), encoding="utf-8")
    return path


def test_bool_and_junk_keep_the_real_price(tmp_path):
    path = write_approved(tmp_path, {
        "Z90": True,
        "A01": 20,
        "B01": "nope",
        "B02": "NaN",
        "B03": "",
        "A02": "20.5",
        "A03": False,
    })
    want = {"A01": 20.0, "A02": 20.5}
    assert gia.load_approved(path) == want
    assert meta.load_approved(path) == want


def test_bool_approved_does_not_fail_a_held_caption(tmp_path):
    path = write_approved(tmp_path, {"Z90": True, "A01": 20})
    approved = gia.load_approved(path)
    policy = HeldPolicy(held=("Z90",), never_list=())
    result = gia.check_post("p", "Mã Z90\nGiá $30", {}, policy, approved)
    assert "held_gia_differs" not in " ".join(result.issues)
    assert "held_no_approved_gia" in result.issues
    assert result.status == "WARN"


def test_huge_integer_does_not_drop_a_real_price(tmp_path):
    path = write_approved(tmp_path, {"A01": 20, "B01": 10**309})
    assert gia.load_approved(path) == {"A01": 20.0}
    assert meta.load_approved(path) == {"A01": 20.0}


def test_later_junk_does_not_erase_an_earlier_price(tmp_path):
    path = write_approved(tmp_path, {"A01": 20, "a01": "nope"})
    assert gia.load_approved(path) == {"A01": 20.0}
    assert meta.load_approved(path) == {"A01": 20.0}


def test_wrong_shape_still_fails(tmp_path):
    path = tmp_path / "approved.json"
    path.write_text(json.dumps({"approvedGia": ["A01"]}), encoding="utf-8")
    with pytest.raises(ValueError):
        gia.load_approved(path)
    with pytest.raises(ValueError):
        meta.load_approved(path)


def test_missing_approved_file_is_empty_for_inventory(tmp_path):
    assert meta.load_approved(tmp_path / "missing.json") == {}


def test_integer_one_stays_one_dollar(tmp_path):
    path = write_approved(tmp_path, {"A01": 1, "Z90": True})
    assert gia.load_approved(path) == {"A01": 1.0}
    assert meta.load_approved(path) == {"A01": 1.0}


def test_stored_approved_prices_stay():
    path = Path(__file__).resolve().parents[2] / "data" / "approved-held-gia.json"
    loaded = gia.load_approved(path)
    assert loaded == {"S15": 30.0, "A26": 32.0, "K03": 52.0, "K04": 101.0, "K05": 52.0, "V04": 17.0}
    assert meta.load_approved(path) == loaded
    assert caption_lint._approved_usd(True) is None
    assert caption_lint._approved_usd(1) == 1.0


def test_caption_lint_skips_bool_and_keeps_one_dollar(tmp_path, capsys):
    approved = write_approved(tmp_path, {"Z90": True, "A01": 1, "B01": "nope", "A02": 1})
    held = tmp_path / "held.json"
    held.write_text(json.dumps({"heldIncomplete": ["Z90", "A01"], "neverList": []}), encoding="utf-8")
    snap = tmp_path / "snap.json"
    snap.write_text(json.dumps({"items": [
        {"ma": "Z90", "live": False},
        {"ma": "A01", "live": False},
    ]}), encoding="utf-8")
    posts = tmp_path / "posts.json"
    posts.write_text(json.dumps([
        {"url": "z", "platform": "fb", "text": "Mã Z90\nGiá $30"},
        {"url": "a", "platform": "fb", "text": "Mã A01\nGiá $1"},
    ]), encoding="utf-8")
    rc = caption_lint.main([
        str(posts), "--snapshot", str(snap),
        "--held", str(held), "--approved", str(approved), "--json",
    ])
    out = json.loads(capsys.readouterr().out)
    by = {row["url"]: row for row in out["posts"]}
    assert rc == 1
    assert by["z"]["status"] == "WARN"
    assert any(reason.startswith("held_no_approved_gia") for reason in by["z"]["reasons"])
    assert not any(reason.startswith("held_gia_differs") for reason in by["z"]["reasons"])
    assert by["a"]["status"] == "PASS"
    assert by["a"]["expected_usd"] == 1.0
