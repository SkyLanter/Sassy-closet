"""Piece 101: 2+ digit piece numbers, numeric order (100 after 99)."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import bundle_inventory_check as bic  # noqa: E402
import draft_review_guide as drg  # noqa: E402
import stack_apply_dryrun as sad  # noqa: E402

NAMES = ["99-held-order-dedupe", "100-checkpoint-start-here", "101-three-digit-pieces"]


def _bundle(tmp_path, names=NAMES, rows=True):
    for n in names:
        d = tmp_path / n
        (d / "patches").mkdir(parents=True)
        (d / "patches" / "0001-x.patch").write_text("x\n")
        (d / "proof").mkdir()
        (d / "proof" / "PROOF.md").write_text("ok\n")
    if rows:
        (tmp_path / "INVENTORY.tsv").write_text(
            "".join("%s\tabc1234\tdraft/%s\tmain\t1\n" % (n, n) for n in names))
    return tmp_path


def test_inventory_check_accepts_three_digits(tmp_path):
    r = bic.check(str(_bundle(tmp_path)))
    assert r["folders"] == 3 and r["rows"] == 3 and r["issues"] == []


def test_inventory_check_flags_missing_three_digit_row(tmp_path):
    b = _bundle(tmp_path, rows=False)
    (b / "INVENTORY.tsv").write_text("99-held-order-dedupe\tabc\tb\tm\t1\n")
    r = bic.check(str(b))
    assert r["unallowed_missing_rows"] == ["100-checkpoint-start-here", "101-three-digit-pieces"]


def test_two_digit_still_ok(tmp_path):
    r = bic.check(str(_bundle(tmp_path, names=["08-a", "09-b"])))
    assert r["issues"] == [] and r["folders"] == 2


def test_piece_num():
    assert drg.piece_num("99-x") == 99
    assert drg.piece_num("100-x") == 100
    assert drg.piece_num("101-x") == 101
    assert drg.piece_num("x-1") is None


def test_numeric_sort():
    assert sorted(NAMES[::-1], key=sad.piece_key) == NAMES
    assert sorted(NAMES[::-1], key=bic.piece_key) == NAMES


def test_inventory_max_three_digit(tmp_path):
    assert sad.inventory_max(str(_bundle(tmp_path))) == 101


def test_guide_range_and_parse():
    text = ("## Suggested merge order\n1. 99-held-order-dedupe\n2. 100-checkpoint-start-here\n"
            "3. 101-three-digit-pieces\n\nNot listed (already included): 17-a, 18-b\n")
    order, inc = sad.parse_guide(text)
    assert order == NAMES and inc == ["17-a", "18-b"]
    assert sad.guide_range(order, inc) == (17, 101)


def test_find_guide_and_rebased_prefer_highest(tmp_path):
    b = _bundle(tmp_path)
    for n in NAMES:
        (b / n / "proof" / "REVIEW-GUIDE.md").write_text(n)
        (b / n / "rebased").mkdir()
        (b / n / "rebased" / "50-p.patch").write_text(n)
    assert open(sad.find_guide(str(b))).read() == "101-three-digit-pieces"
    assert open(sad.rebased_patch(str(b), "50-p")).read() == "101-three-digit-pieces"
