import os
import subprocess

import stack_apply_dryrun as sad

ENV = dict(os.environ, **sad.GIT_ENV)


def g(repo, *a):
    return subprocess.run(["git", "-C", str(repo), *a], check=True, capture_output=True,
                          text=True, env=ENV).stdout.strip()


def _repo(tmp_path):
    r = tmp_path / "repo"
    r.mkdir()
    g(r, "init", "-q", "-b", "main")
    (r / "a.txt").write_text("one\n")
    g(r, "add", ".")
    g(r, "commit", "-qm", "base")
    return r


def _patch(r, bundle, piece, fname, text, msg, base="main"):
    g(r, "checkout", "-q", "-B", "tmp-" + piece, base)
    (r / fname).write_text(text)
    g(r, "add", ".")
    g(r, "commit", "-qm", msg)
    pd = bundle / piece / "patches"
    pd.mkdir(parents=True)
    g(r, "format-patch", "-q", "-1", "-o", str(pd))
    g(r, "checkout", "-q", "main")


def _guide(bundle, order, included):
    pd = bundle / "99-guide" / "proof"
    pd.mkdir(parents=True)
    lines = ["# Draft review guide", "", "## Suggested merge order", ""]
    lines += ["%d. %s (base main)" % (i + 1, p) for i, p in enumerate(order)]
    lines += ["", "Not listed (already included in the main chain, no separate merge): " + ", ".join(included) + ".", ""]
    (pd / "REVIEW-GUIDE.md").write_text("\n".join(lines))
    (bundle / "INVENTORY.tsv").write_text("x\tx\tx\tx\t1\n")


def test_parse_guide():
    order, inc = sad.parse_guide("## Suggested merge order\n\n1. 17-a (base x)\n2. 19-b (after y)\n\n"
                                 "Not listed (already included in the main chain, no separate merge): 18-c, 20-d.\n")
    assert order == ["17-a", "19-b"] and inc == ["18-c", "20-d"]


def test_clean_conflict_included(tmp_path):
    r = _repo(tmp_path)
    b = tmp_path / "bundle"
    _patch(r, b, "01-new", "b.txt", "new\n", "Piece 01: add b")
    _patch(r, b, "02-edit", "a.txt", "two\n", "Piece 02: edit a")
    _patch(r, b, "03-clash", "a.txt", "three\n", "Piece 03: clash a")
    _patch(r, b, "04-dup", "b.txt", "new\n", "Piece 04: same as 01")
    _guide(b, ["01-new", "02-edit", "03-clash", "04-dup"], ["05-old"])
    res = sad.dryrun(str(r), str(b), "main", tests=False)
    st = {p: s for p, s, _ in res["rows"]}
    assert st == {"01-new": "clean", "02-edit": "clean", "03-clash": "conflict",
                  "04-dup": "included", "05-old": "included"}
    # temp worktree cleaned, main untouched
    assert len(g(r, "worktree", "list").splitlines()) == 1
    assert (r / "a.txt").read_text() == "one\n"
    md = sad.render(res)
    assert "Conflict (1): 03-clash" in md and "Clean (2)" in md


def test_missing_patches(tmp_path):
    r = _repo(tmp_path)
    b = tmp_path / "bundle"
    _guide(b, ["07-gone"], [])
    res = sad.dryrun(str(r), str(b), "main", tests=False)
    assert res["rows"] == [("07-gone", "missing", "no patches in bundle")]


def _rebased(r, bundle, folder, piece, fname, text, msg, base):
    """Write <folder>/patches/<piece>.patch made on top of `base` (placeholder content)."""
    g(r, "checkout", "-q", "-B", "tmp-rb-" + piece, base)
    (r / fname).write_text(text)
    g(r, "add", ".")
    g(r, "commit", "-qm", msg)
    pd = bundle / folder / "rebased"
    pd.mkdir(parents=True, exist_ok=True)
    (pd / (piece + ".patch")).write_text(g(r, "format-patch", "--stdout", "-1") + "\n")
    g(r, "checkout", "-q", "main")


def _clash_setup(tmp_path):
    r = _repo(tmp_path)
    b = tmp_path / "bundle"
    _patch(r, b, "02-edit", "a.txt", "two\n", "Piece 02: edit a")
    _patch(r, b, "03-clash", "a.txt", "three\n", "Piece 03: clash a")
    _guide(b, ["02-edit", "03-clash"], [])
    # stack branch with 02 applied, so the rebased 03 sits on it
    g(r, "checkout", "-q", "-B", "stack", "main")
    g(r, "am", "-q", *sorted(str(p) for p in (b / "02-edit" / "patches").iterdir()))
    g(r, "checkout", "-q", "main")
    _rebased(r, b, "68-rebased-conflicts", "03-clash", "a.txt", "three\n", "Piece 03 (rebased): clash a", "stack")
    return r, b


def test_prefers_rebased_patch(tmp_path):
    r, b = _clash_setup(tmp_path)
    assert sad.rebased_patch(str(b), "03-clash").endswith("68-rebased-conflicts/rebased/03-clash.patch")
    assert sad.rebased_patch(str(b), "02-edit") is None
    res = sad.dryrun(str(r), str(b), "main", tests=False)
    st = {p: (s, d) for p, s, d in res["rows"]}
    assert st["02-edit"][0] == "clean" and st["03-clash"][0] == "clean"
    assert "[rebased: 68-rebased-conflicts/rebased/03-clash.patch]" in st["03-clash"][1]
    assert "rebased" not in st["02-edit"][1]
    assert len(g(r, "worktree", "list").splitlines()) == 1
    assert (b / "03-clash" / "patches").is_dir()  # original folder untouched


def test_no_rebased_flag_uses_originals(tmp_path):
    r, b = _clash_setup(tmp_path)
    res = sad.dryrun(str(r), str(b), "main", tests=False, prefer_rebased=False)
    assert {p: s for p, s, _ in res["rows"]} == {"02-edit": "clean", "03-clash": "conflict"}


def test_newest_rebased_folder_wins(tmp_path):
    r, b = _clash_setup(tmp_path)
    _rebased(r, b, "70-rebased-again", "03-clash", "a.txt", "three\n", "Piece 03 (rebased again)", "stack")
    (b / "69-not-rebased" / "patches").mkdir(parents=True)
    assert "70-rebased-again" in sad.rebased_patch(str(b), "03-clash")
    res = sad.dryrun(str(r), str(b), "main", tests=False)
    assert "70-rebased-again" in dict((p, d) for p, _, d in res["rows"])["03-clash"]


def test_rebased_any_numbered_folder_newest_wins(tmp_path):
    # Piece 69: <NN>-*/rebased/ (not only <NN>-rebased-*) counts; highest NN wins.
    for f in ("68-rebased-conflicts", "69-guide-count-38-test"):
        d = tmp_path / f / "rebased"
        d.mkdir(parents=True)
        (d / "03-clash.patch").write_text("placeholder\n")
    assert sad.rebased_patch(str(tmp_path), "03-clash").endswith("69-guide-count-38-test/rebased/03-clash.patch")
