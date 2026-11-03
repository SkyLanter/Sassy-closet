"""Piece 82: guide head safety (placeholder data in a temp git repo)."""
import os
import subprocess

import pytest

import draft_review_guide as g
import stack_apply_dryrun as s

ENV = dict(os.environ, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="", GIT_COMMITTER_NAME="t",
           GIT_COMMITTER_EMAIL="", GIT_CONFIG_GLOBAL=os.devnull)


def git(repo, *a):
    return subprocess.run(["git", "-C", str(repo), *a], check=True, capture_output=True,
                          text=True, env=ENV).stdout.strip()


def commit(repo, name, text, msg):
    (repo / name).write_text(text)
    git(repo, "add", name)
    git(repo, "commit", "-q", "-m", msg)
    return git(repo, "rev-parse", "HEAD")


@pytest.fixture
def setup(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    git(repo, "init", "-q", "-b", "main")
    base = commit(repo, "a.txt", "base\n", "base")
    git(repo, "checkout", "-q", "-b", "side")
    side = commit(repo, "p1.txt", "one\n", "Piece 01: placeholder one\n\nside copy")
    git(repo, "checkout", "-q", "-b", "chain", base)
    commit(repo, "p1.txt", "one\n", "Piece 01: placeholder one\n\nchain copy")
    tip = commit(repo, "p2.txt", "two\n", "Piece 02: placeholder two")
    bundle = tmp_path / "bundle"
    for f in ("01-one", "02-two"):
        (bundle / f / "proof").mkdir(parents=True)
    (bundle / "INVENTORY.tsv").write_text(
        f"01-one\t{side}\tdraft/01-one\tmain\t1\n02-two\t{tip}\tdraft/02-two\tdraft/01-one\t1\n")
    return repo, bundle, base, tip


def test_default_head_is_newest_bundle_commit(setup):
    repo, bundle, base, tip = setup
    assert g.newest_bundle_commit(str(bundle), str(repo)) == tip


def test_newest_skips_commit_missing_from_repo(setup):
    repo, bundle, base, tip = setup
    with open(bundle / "INVENTORY.tsv", "a") as fh:
        fh.write("03-three\t" + "0" * 40 + "\tdraft/03\tdraft/02-two\t1\n")
    assert g.newest_bundle_commit(str(bundle), str(repo)) == tip


def test_wrong_head_warns_and_tip_does_not(setup):
    repo, bundle, base, tip = setup
    w = g.head_check(str(bundle), str(repo), base)
    assert w and w.startswith(g.HEAD_WARNING)
    assert g.head_check(str(bundle), str(repo), tip) is None


def test_main_default_head_detects_included(setup, tmp_path, capsys):
    repo, bundle, base, tip = setup
    out = tmp_path / "G.md"
    g.main(["--bundle", str(bundle), "--repo", str(repo), "--out", str(out)])
    assert "included: 1" in capsys.readouterr().out
    assert g.HEAD_WARNING not in out.read_text()


def test_main_wrong_head_marks_guide(setup, tmp_path):
    repo, bundle, base, tip = setup
    out = tmp_path / "G.md"
    g.main(["--bundle", str(bundle), "--repo", str(repo), "--head", base, "--out", str(out)])
    assert g.HEAD_WARNING in out.read_text()


def test_dryrun_refuses_warned_guide_unless_forced(setup, tmp_path):
    repo, bundle, base, tip = setup
    g.main(["--bundle", str(bundle), "--repo", str(repo), "--head", base,
            "--out", str(bundle / "02-two" / "proof" / "REVIEW-GUIDE.md")])
    with pytest.raises(SystemExit) as e:
        s.dryrun(str(repo), str(bundle), base, tests=False)
    assert "head may be wrong" in str(e.value)
    res = s.dryrun(str(repo), str(bundle), base, tests=False, force=True)
    assert res["main_sha"]
