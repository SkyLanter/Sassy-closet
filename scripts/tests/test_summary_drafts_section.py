"""Piece 103: 'Draft work waiting' section. Placeholder data built at runtime."""
import os
import sys
import tarfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import bundle_status as bs  # noqa: E402
import daily_summary_draft as dsd  # noqa: E402


def make_bundle(tmp, rows=(("01-alpha", "aaaaaaa1"), ("09-beta", "bbbbbbb2"), ("10-gamma", "ccccccc3"))):
    d = tmp / "pending-draft-prs"
    d.mkdir()
    for f, _ in rows:
        (d / f / "proof").mkdir(parents=True)
        (d / f / "proof" / "PROOF.md").write_text("placeholder\n")
    (d / "INVENTORY.tsv").write_text(
        "".join(f"{f}\t{c}\tdraft/{f}\tmain\t1\n" for f, c in rows))
    tgz = tmp / "pending-draft-prs.tgz"
    with tarfile.open(tgz, "w:gz") as t:
        t.add(d, arcname=d.name)
    return tgz


def test_lists_count_newest_sha_and_age(tmp_path):
    tgz = make_bundle(tmp_path)
    os.utime(tgz, (1000, 1000))
    L = bs.status_lines(tgz, now=1000 + 3 * 3600)
    text = "\n".join(L)
    assert L[0] == bs.HEAD
    assert "3 draft pieces" in text
    assert "Highest-numbered piece: 10-gamma (commit ccccccc)" in text  # numeric, not text sort
    assert "Bundle fingerprint: " in text and "…" in text
    assert "3 hours old" in text
    assert "Inventory check: " in text


def test_missing_bundle_one_line(tmp_path):
    L = bs.status_lines(tmp_path / "nope.tgz")
    assert len(L) == 2 and "missing or unreadable" in L[1]


def test_unreadable_inventory_one_line(tmp_path):
    tgz = make_bundle(tmp_path)
    (tmp_path / "pending-draft-prs" / "INVENTORY.tsv").unlink()
    L = bs.status_lines(tgz)
    assert len(L) == 2 and "missing or unreadable" in L[1]


def test_inventory_problem_reported(tmp_path):
    tgz = make_bundle(tmp_path)
    with open(tmp_path / "pending-draft-prs" / "INVENTORY.tsv", "a") as f:
        f.write("11-ghost\tddddddd\tdraft/11\tmain\t1\n")
    text = "\n".join(bs.status_lines(tgz))
    assert "4 draft pieces" in text and "Highest-numbered piece: 11-ghost" in text


def test_age_words():
    assert bs.age_words(30) == "under 2 minutes old"
    assert bs.age_words(600) == "10 minutes old"
    assert bs.age_words(5 * 86400) == "5 days old"


def test_build_includes_section_and_no_banned(tmp_path):
    lines = dsd.drafts_lines(make_bundle(tmp_path))
    text = dsd.build(None, None, {}, None, None, None, None, "2026-01-01", drafts=lines)
    assert bs.HEAD in text
    assert not dsd.BANNED.search("\n".join(lines))


def test_drafts_lines_never_raises(tmp_path):
    lines = dsd.drafts_lines(tmp_path / "missing.tgz")
    assert lines[0] == bs.HEAD and len(lines) == 2
