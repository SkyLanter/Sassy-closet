"""Piece 105: highest-numbered vs most-recently-added piece; read-only backup count.
Placeholder temp data only, built at runtime."""
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import bundle_status as bs  # noqa: E402
from test_summary_drafts_section import make_bundle  # noqa: E402


def _touch_proof(tmp, folder, t):
    p = tmp / "pending-draft-prs" / folder / "proof" / "PROOF.md"
    os.utime(p, (t, t))


def test_lower_number_added_later_is_shown(tmp_path):
    tgz = make_bundle(tmp_path)
    _touch_proof(tmp_path, "01-alpha", 5000)
    _touch_proof(tmp_path, "09-beta", 3000)
    _touch_proof(tmp_path, "10-gamma", 1000)
    text = "\n".join(bs.status_lines(tgz))
    assert "Highest-numbered piece: 10-gamma (commit ccccccc)." in text
    assert "Most recently added piece: 01-alpha (commit aaaaaaa)." in text


def test_same_piece_marked(tmp_path):
    tgz = make_bundle(tmp_path)
    for f, t in (("01-alpha", 1000), ("09-beta", 2000), ("10-gamma", 9000)):
        _touch_proof(tmp_path, f, t)
    text = "\n".join(bs.status_lines(tgz))
    assert "Most recently added piece: 10-gamma (commit ccccccc) (same piece)." in text


def test_folder_mtime_fallback_without_proof(tmp_path):
    tgz = make_bundle(tmp_path)
    d = tmp_path / "pending-draft-prs"
    for f, t in (("01-alpha", 1000), ("09-beta", 8000), ("10-gamma", 2000)):
        (d / f / "proof" / "PROOF.md").unlink()
        (d / f / "proof").rmdir()
        os.utime(d / f, (t, t))
    text = "\n".join(bs.status_lines(tgz))
    assert "Most recently added piece: 09-beta" in text


def test_backup_count_and_size_read_only(tmp_path):
    tgz = make_bundle(tmp_path)
    (tmp_path / "pending-draft-prs.tgz.bak-1").write_bytes(b"x" * 2048)
    bd = tmp_path / "pending-draft-prs.bak-2"
    bd.mkdir()
    (bd / "f").write_bytes(b"y" * 1024)
    (tmp_path / "unrelated.bak-3").write_bytes(b"z" * 10)
    before = sorted(p.name for p in tmp_path.iterdir())
    n, sz = bs.backup_stats(tgz, tmp_path / "pending-draft-prs")
    assert (n, sz) == (2, 3072)
    text = "\n".join(bs.status_lines(tgz))
    assert "Bundle backups (.bak-*): 2, 3.0 KB total (count only, nothing deleted)." in text
    assert sorted(p.name for p in tmp_path.iterdir()) == before


def test_no_backups(tmp_path):
    tgz = make_bundle(tmp_path)
    assert "Bundle backups (.bak-*): 0, 0 bytes total" in "\n".join(bs.status_lines(tgz))


def test_size_words():
    assert bs.size_words(500) == "500 bytes"
    assert bs.size_words(3 * (1 << 20)) == "3.0 MB"
