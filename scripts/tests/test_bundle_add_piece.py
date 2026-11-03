"""Piece 102: atomic bundle writes (placeholder data only)."""
import fcntl, os, subprocess, sys, tarfile
from types import SimpleNamespace

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import bundle_add_piece as bap  # noqa: E402

OK = [("ok", [sys.executable, "-c", "pass"])]
BAD = [("bad", [sys.executable, "-c", "import sys; sys.exit(1)"])]


def _setup(tmp):
    d = tmp / "bundle"
    (d / "01-old" / "proof").mkdir(parents=True)
    (d / "01-old" / "proof" / "PROOF.md").write_text("old\n")
    (d / "INVENTORY.tsv").write_text("01-old\taaa1111\tdraft/01-old\tmain\t1\n")
    tgz = tmp / "bundle.tgz"
    bap.repack(str(tgz), str(d))
    src = tmp / "src"
    (src / "proof").mkdir(parents=True)
    (src / "proof" / "PROOF.md").write_text("new\n")
    return d, tgz, src


def _args(tmp, tgz, src, folder="02-new", **kw):
    a = dict(folder=folder, src=str(src), commit="bbb2222", branch="draft/" + folder,
             base="main", tgz=str(tgz), lock=str(tmp / "b.lock"), dry_run=False, no_wait=True)
    a.update(kw)
    return SimpleNamespace(**a)


def test_success_adds_and_repacks(tmp_path):
    d, tgz, src = _setup(tmp_path)
    assert bap.run(_args(tmp_path, tgz, src), checks=OK, log=lambda *_: None) == 0
    assert (d / "02-new" / "proof" / "PROOF.md").read_text() == "new\n"
    assert "02-new\tbbb2222" in (d / "INVENTORY.tsv").read_text()
    with tarfile.open(tgz) as t:
        assert "bundle/02-new/proof/PROOF.md" in t.getnames()


def test_rollback_on_failed_check(tmp_path):
    d, tgz, src = _setup(tmp_path)
    before = bap.sha256(str(tgz))
    assert bap.run(_args(tmp_path, tgz, src), checks=BAD, log=lambda *_: None) == 1
    assert bap.sha256(str(tgz)) == before
    assert not (d / "02-new").exists()
    assert "02-new" not in (d / "INVENTORY.tsv").read_text()


def test_replace_existing_row(tmp_path):
    d, tgz, src = _setup(tmp_path)
    assert bap.run(_args(tmp_path, tgz, src, folder="01-old"), checks=OK, log=lambda *_: None) == 0
    rows = (d / "INVENTORY.tsv").read_text().splitlines()
    assert rows == ["01-old\tbbb2222\tdraft/01-old\tmain\t1"]
    assert (d / "01-old" / "proof" / "PROOF.md").read_text() == "new\n"


def test_dry_run_changes_nothing(tmp_path):
    d, tgz, src = _setup(tmp_path)
    before = bap.sha256(str(tgz))
    assert bap.run(_args(tmp_path, tgz, src, dry_run=True), checks=BAD, log=lambda *_: None) == 0
    assert bap.sha256(str(tgz)) == before and not (d / "02-new").exists()


def test_lock_held_by_other_process(tmp_path):
    d, tgz, src = _setup(tmp_path)
    lock = tmp_path / "b.lock"
    holder = subprocess.Popen([sys.executable, "-c",
        "import fcntl,sys,time;f=open(sys.argv[1],'a');fcntl.flock(f,fcntl.LOCK_EX);"
        "print('held',flush=True);time.sleep(30)", str(lock)], stdout=subprocess.PIPE, text=True)
    try:
        assert holder.stdout.readline().strip() == "held"
        assert bap.run(_args(tmp_path, tgz, src), checks=OK, log=lambda *_: None) == 3
        assert not (d / "02-new").exists()
    finally:
        holder.kill(); holder.wait()
    assert bap.run(_args(tmp_path, tgz, src), checks=OK, log=lambda *_: None) == 0
