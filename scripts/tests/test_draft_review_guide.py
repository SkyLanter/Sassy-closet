import os
import draft_review_guide as g


def mk(tmp, name, proof, patch="+print('x')\n"):
    d = tmp / name
    (d / "patches").mkdir(parents=True)
    (d / "proof").mkdir()
    (d / "patches" / "0001-x.patch").write_text(patch)
    (d / "proof" / "PROOF.md").write_text(proof)


def setup(tmp):
    mk(tmp, "90-alpha", "Tests: 10 passed\nprivacy_scan: CLEAN\n")
    mk(tmp, "91-beta", "12 passed in 1s\n", patch="+requests.post(url)\n")
    mk(tmp, "92-gamma", "privacy scan FAIL\n")
    (tmp / "INVENTORY.tsv").write_text(
        "92-gamma\tccc\tdraft/92-gamma\tdraft/90-alpha\t1\n"
        "91-beta\tbbb\tdraft/91-beta\tdraft/92-gamma\t1\n"
        "90-alpha\taaa\tdraft/90-alpha\tmain\t1\n")


def test_parse_and_order(tmp_path):
    setup(tmp_path)
    pieces, order = g.build(str(tmp_path))
    by = {p["folder"]: p for p in pieces}
    assert by["90-alpha"]["tests"] == 10 and by["90-alpha"]["privacy"] == "CLEAN"
    assert by["91-beta"]["privacy"] == "not recorded in proof"
    assert by["91-beta"]["live"] == ["HTTP write call"]
    assert by["92-gamma"]["privacy"] == "FLAGGED" and by["92-gamma"]["tests"] is None
    assert [r["folder"] for r in order] == ["90-alpha", "92-gamma", "91-beta"]


def test_range_and_render(tmp_path):
    setup(tmp_path)
    out = tmp_path / "o" / "R.md"
    assert g.main(["--bundle", str(tmp_path), "--out", str(out), "--from", "90", "--to", "90"]) == 0
    t = out.read_text()
    assert "90-alpha" in t and "91-beta" not in t
    assert "Read-only" in t and "outside this set" in t


import subprocess


def _g(repo, *a):
    return subprocess.run(["git", "-C", str(repo)] + list(a), check=True,
                          capture_output=True, text=True).stdout.strip()


def _cherry_setup(tmp):
    repo = tmp / "repo"
    repo.mkdir()
    _g(repo, "init", "-q", "-b", "main")
    _g(repo, "config", "user.email", "placeholder")
    _g(repo, "config", "user.name", "t")
    (repo / "a.txt").write_text("base\n")
    _g(repo, "add", ".")
    _g(repo, "commit", "-qm", "Piece 90: base")
    _g(repo, "checkout", "-qb", "side")
    (repo / "b.txt").write_text("placeholder side\n")
    _g(repo, "add", ".")
    _g(repo, "commit", "-qm", "Piece 91: side")
    side = _g(repo, "rev-parse", "HEAD")
    patch = _g(repo, "format-patch", "-1", "--stdout", "HEAD") + "\n"
    _g(repo, "checkout", "-q", "main")
    (repo / "c.txt").write_text("placeholder main\n")
    _g(repo, "add", ".")
    _g(repo, "commit", "-qm", "Piece 92: main")
    _g(repo, "cherry-pick", side)
    head = _g(repo, "rev-parse", "HEAD")
    b = tmp / "bundle"
    b.mkdir()
    for name, commit, br, base, pt in [
            ("90-a", "x", "draft/90-a", "main", "+print('x')\n"),
            ("91-b", side, "draft/91-b", "draft/90-a", patch),
            ("92-c", head, "draft/92-c", "draft/90-a", "+print('y')\n")]:
        mk(b, name, "1 passed\n", patch=pt)
    (b / "INVENTORY.tsv").write_text(
        "90-a\tx\tdraft/90-a\tmain\t1\n"
        f"91-b\t{side}\tdraft/91-b\tdraft/90-a\t1\n"
        f"92-c\t{head}\tdraft/92-c\tdraft/90-a\t1\n")
    return repo, b, head


def test_cherry_pick_detected_by_patch_id(tmp_path):
    repo, b, head = _cherry_setup(tmp_path)
    pieces, order = g.build(str(b), repo=str(repo), head=head)
    by = {p["folder"]: p for p in pieces}
    assert by["91-b"]["included"] and by["91-b"]["included"][0] == head
    assert not by["92-c"]["included"]
    assert "91-b" not in [r["folder"] for r in order]
    t = g.render(pieces, order)
    assert "included in the main chain" in t and "no separate merge" in t


def test_cherry_pick_subject_fallback(tmp_path):
    repo, b, head = _cherry_setup(tmp_path)
    (b / "91-b" / "patches" / "0001-x.patch").write_text("not a patch\n")
    pieces, _ = g.build(str(b), repo=str(repo), head=head)
    assert {p["folder"]: p for p in pieces}["91-b"]["included"]


def test_no_repo_no_detection(tmp_path):
    setup(tmp_path)
    pieces, _ = g.build(str(tmp_path))
    assert all(p["included"] is None for p in pieces)


def _livepatch(tmp, name, body):
    d = os.path.join(tmp, name, "patches"); os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, "0001-x.patch"), "w") as fh:
        fh.write(body)
    return os.path.join(tmp, name)


def test_live_check_ignores_guide_pattern_definitions(tmp_path):
    from draft_review_guide import live_check
    body = ("+++ b/scripts/draft_review_guide.py\n"
            '+    (re.compile(r"git\\s+push|gh\\s+pr\\s+(merge|create)"), "git push/merge"),\n'
            '+    (re.compile(r"--execute"), "--execute flag"),\n'
            '+    (re.compile(r"squareup|blob\\.(put|del)\\(", re.I), "live service write"),\n'
            "+++ b/scripts/tests/test_draft_review_guide.py\n"
            '+    mk(tmp, "91-beta", "1 passed\\n", patch="+requests.post(url)\\n")\n')
    assert live_check(_livepatch(str(tmp_path), "95-self", body)) == []


def test_live_check_still_flags_real_writes(tmp_path):
    from draft_review_guide import live_check
    body = ("+++ b/scripts/draft_review_guide.py\n"
            "+    requests.post(url)\n"
            "+++ b/scripts/tests/test_draft_review_guide.py\n"
            '+    mk(tmp, "x", "1\\n", patch="+a\\n"); subprocess.run("git push")\n'
            "+++ b/scripts/other_tool.py\n"
            '+    (re.compile(r"--execute"), "--execute flag"),\n')
    hits = live_check(_livepatch(str(tmp_path), "96-real", body))
    labels = [lb for _, lb in g.LIVE_PATTERNS]
    assert hits == sorted([labels[0], labels[2], labels[3]])


def test_live_check_ignores_plus_fixture_literals_in_guide_tests(tmp_path):
    from draft_review_guide import live_check
    body = ("+++ b/scripts/tests/test_draft_review_guide.py\n"
            '+            "+    requests.post(url)\\n"\n'
            "+            '+    (re.compile(r\"--execute\"), \"x\"),\\n')\n")
    assert live_check(_livepatch(str(tmp_path), "97-lit", body)) == []


def test_live_check_readonly_get_is_not_live_write(tmp_path):
    from draft_review_guide import live_check
    body = ("+++ b/scripts/placeholder_health.py\n"
            "+    req = urllib.request.Request(url, method=\"HEAD\")\n"
            "+    with urllib.request.urlopen(req, timeout=5) as r:\n")
    d = _livepatch(str(tmp_path), "98-get", body)
    assert live_check(d) == []
    assert live_check(d, detail=True) == ([], ["read-only network"])


def test_live_check_flags_urlopen_post_and_other_writes(tmp_path):
    from draft_review_guide import live_check, LIVE_PATTERNS
    body = ("+++ b/scripts/placeholder_writer.py\n"
            "+    req = urllib.request.Request(url, data=payload, method=\"POST\")\n"
            "+    urllib.request.urlopen(req)\n"
            "+    requests.delete(url)\n"
            "+subprocess.run(['git', 'push'])  # git push\n"
            "+run('placeholder.sh --execute')\n")
    hits, ro = live_check(_livepatch(str(tmp_path), "99-post", body), detail=True)
    assert set(hits) == {lbl for _, lbl in LIVE_PATTERNS[:4]}
    assert ro == []


def test_live_check_ignores_test_deny_lists(tmp_path):
    from draft_review_guide import live_check
    body = ("+++ b/scripts/tests/test_placeholder.py\n"
            "+    for bad in (\"git push\", \"gh pr\"):\n"
            "+        assert bad not in w, bad\n")
    assert live_check(_livepatch(str(tmp_path), "97-deny", body)) == []


# Piece 69: repo-suite count wins over dry-run / stack numbers (placeholder text only).
def test_count_prefers_labelled_repo_line():
    t = ("Tests on final stack: 900 passed\n"
         "pytest -q scripts/tests: 12 passed in 1.0s\n"
         "Real dry-run: 950 passed\n")
    assert g.repo_test_count(t) == 12


def test_count_first_summary_when_unlabelled():
    assert g.repo_test_count("7 passed in 0.1s\nlater 99 passed\n") == 7


def test_count_ignores_only_stack_lines():
    assert g.repo_test_count("full stack: 40 passed\ndry run 41 passed\n") is None


def test_count_repo_suite_label():
    assert g.repo_test_count("dry-run 70 passed\nrepo suite: 5 passed\n") == 5


def test_proof_texts_skip_copied_guide(tmp_path):
    pd = tmp_path / "proof"
    pd.mkdir()
    (pd / "REVIEW-GUIDE.md").write_text("- Tests: 800 passed\n")
    (pd / "STACK-DRYRUN.md").write_text("801 passed\n")
    (pd / "PROOF.md").write_text("pytest -q scripts/tests: 3 passed\n")
    assert g.parse_proof(g.proof_texts(str(tmp_path)))[0] == 3
