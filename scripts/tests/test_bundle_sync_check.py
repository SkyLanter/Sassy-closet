import os
import sys
import tarfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import bundle_sync_check as bsc  # noqa: E402


def _make(tmp_path):
    d = tmp_path / "pending-draft-prs"
    (d / "99-placeholder" / "patches").mkdir(parents=True)
    (d / "99-placeholder" / "proof").mkdir()
    (d / "99-placeholder" / "patches" / "0001-x.patch").write_text("placeholder\n")
    (d / "99-placeholder" / "proof" / "p.txt").write_text("ok\n")
    (d / "INVENTORY.tsv").write_text("99-placeholder\tabc1234\tdraft/99\tmain\t1\n")
    tgz = tmp_path / "pending-draft-prs.tgz"
    with tarfile.open(tgz, "w:gz") as tf:
        tf.add(d, arcname="pending-draft-prs")
    return str(tgz), d


def test_in_sync(tmp_path):
    tgz, _ = _make(tmp_path)
    assert bsc.main(["--tgz", tgz]) == 0


def test_different_and_extra(tmp_path):
    tgz, d = _make(tmp_path)
    (d / "INVENTORY.tsv").write_text("changed\n")
    (d / "new.txt").write_text("x\n")
    codes = {c for _, c in bsc.compare(tgz, str(d))["issues"]}
    assert codes == {"different", "extra"}
    assert bsc.main(["--tgz", tgz]) == 1


def test_missing(tmp_path):
    tgz, d = _make(tmp_path)
    os.remove(d / "99-placeholder" / "proof" / "p.txt")
    assert bsc.compare(tgz, str(d))["issues"] == [("99-placeholder/proof/p.txt", "missing")]


def test_inventory_ok_and_warn(tmp_path):
    tgz, d = _make(tmp_path)
    assert bsc.main(["--tgz", tgz, "--inventory"]) == 0
    (d / "INVENTORY.tsv").write_text("")
    assert bsc.main(["--tgz", tgz, "--dir", str(d), "--inventory"]) == 1


# Piece 87: --inventory lists gaps and fails on unallowlisted folder
def test_p87_inventory_gap_fails(tmp_path, capsys):
    import tarfile as _tf
    root = tmp_path / "pending-draft-prs"
    for n in ("17-a", "18-b"):
        (root / n / "patches").mkdir(parents=True)
        (root / n / "patches" / "0001-x.patch").write_text("x")
        (root / n / "proof").mkdir()
        (root / n / "proof" / "p.txt").write_text("ok")
    (root / "INVENTORY.tsv").write_text("17-a\tabc\tdraft/17-a\tbase\t1\n")
    tgz = tmp_path / "pending-draft-prs.tgz"
    with _tf.open(tgz, "w:gz") as tf:
        tf.add(root, arcname="pending-draft-prs")
    assert bsc.main(["--tgz", str(tgz), "--inventory"]) == 1
    out = capsys.readouterr().out
    assert "INVENTORY GAP folder_without_row 18-b NOT_ALLOWLISTED" in out
