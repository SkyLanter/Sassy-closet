"""A boolean approved Giá is not $1, and one junk value does not drop the rest."""
import json

import pytest

import caption_gia_check as gia
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
