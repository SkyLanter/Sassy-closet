import subprocess
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "overnight_tip_status.sh"


def _git(repo, *a):
    return subprocess.run(["git", "-C", str(repo), *a], check=True, capture_output=True, text=True).stdout.strip()


def _run(repo, proofs):
    return subprocess.run(["bash", str(SCRIPT), "--repo", str(repo), "--proof-root", str(proofs)],
                          check=True, capture_output=True, text=True).stdout


def test_recommends_newest_pass(tmp_path):
    repo, proofs = tmp_path / "r", tmp_path / "p"
    repo.mkdir(); proofs.mkdir()
    _git(repo, "init", "-q", "-b", "main")
    _git(repo, "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-q", "--allow-empty", "-m", "x")
    sha = _git(repo, "rev-parse", "--short=7", "HEAD")
    for b in ("piece-9-a", "piece-10-b", "piece-11-c", "other"):
        _git(repo, "branch", b)
    (proofs / "proof-9").mkdir(); (proofs / "proof-9" / "SUMMARY.md").write_text(f"{sha} PASS")
    (proofs / "proof-10").mkdir(); (proofs / "proof-10" / "SUMMARY.md").write_text(f"{sha} PASS")
    (proofs / "proof-11").mkdir(); (proofs / "proof-11" / "SUMMARY.md").write_text(f"{sha} FAIL")
    out = _run(repo, proofs)
    assert f"Recommended tip (merge-stack head with PASS proof): piece-10-b @ {sha}" in out
    assert "| 11 | `piece-11-c`" in out and "FAIL" in out
    assert "other" not in out
    assert out.index("| 11 ") < out.index("| 10 ") < out.index("| 9 ")


def test_no_pass(tmp_path):
    _git(tmp_path, "init", "-q", "-b", "main")
    _git(tmp_path, "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-q", "--allow-empty", "-m", "x")
    _git(tmp_path, "branch", "piece-1-a")
    out = _run(tmp_path, tmp_path / "none")
    assert "no-summary" in out and "none found" in out


def test_no_writes_in_script():
    src = SCRIPT.read_text()
    for bad in ("git push", "git commit", "git branch -", "curl", "vercel", "> \"$", ">>"):
        assert bad not in src


def test_prefers_stack_head_over_newer_side_branch(tmp_path):
    repo, proofs = tmp_path / "r", tmp_path / "p"
    repo.mkdir(); proofs.mkdir()
    g = lambda *a: _git(repo, *a)
    c = ("-c", "user.email=t@t", "-c", "user.name=t", "commit", "-q", "--allow-empty", "-m")
    g("init", "-q", "-b", "main"); g(*c, "base"); g("branch", "piece-1-base")
    g(*c, "s2"); g("branch", "piece-2-stack")
    g(*c, "s3"); g("branch", "piece-3-stack")
    g("checkout", "-q", "-b", "tmp", "piece-1-base"); g(*c, "side"); g("branch", "piece-4-side")
    for n in (1, 2, 3, 4):
        sha = g("rev-parse", "--short=7", f"refs/heads/piece-{n}-" + {1: "base", 2: "stack", 3: "stack", 4: "side"}[n])
        (proofs / f"proof-{n}").mkdir(); (proofs / f"proof-{n}" / "SUMMARY.md").write_text(f"{sha} PASS")
    s3 = g("rev-parse", "--short=7", "piece-3-stack"); s4 = g("rev-parse", "--short=7", "piece-4-side")
    out = _run(repo, proofs)
    assert f"Recommended tip (merge-stack head with PASS proof): piece-3-stack @ {s3}" in out
    assert f"Newest PASS (side branch, not stack head): piece-4-side @ {s4}" in out


def test_recheck_verdict_line_wins_over_unrelated_fail(tmp_path):
    repo, proofs = tmp_path / "r", tmp_path / "p"
    repo.mkdir(); proofs.mkdir()
    _git(repo, "init", "-q", "-b", "main")
    _git(repo, "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-q", "--allow-empty", "-m", "x")
    sha = _git(repo, "rev-parse", "--short=7", "HEAD")
    _git(repo, "branch", "piece-5-a"); _git(repo, "branch", "piece-6-b")
    (proofs / "proof-5").mkdir()
    (proofs / "proof-5" / "SUMMARY.md").write_text(f"{sha}\nhard_recheck.sh: PASS\nLive privacy FAIL until deploy\n")
    (proofs / "proof-6").mkdir()
    (proofs / "proof-6" / "SUMMARY.md").write_text(f"{sha}\nhard_recheck.sh: FAIL\nother PASS\n")
    out = _run(repo, proofs)
    assert "| 5 | `piece-5-a` | `" + sha + "` | PASS |" in out
    assert "| 6 | `piece-6-b` | `" + sha + "` | FAIL |" in out


def test_last_verdict_and_first_token_win(tmp_path):
    repo, proofs = tmp_path / "r", tmp_path / "p"
    repo.mkdir(); proofs.mkdir()
    _git(repo, "init", "-q", "-b", "main")
    _git(repo, "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-q", "--allow-empty", "-m", "x")
    sha = _git(repo, "rev-parse", "--short=7", "HEAD")
    for n in (7, 8, 9):
        _git(repo, "branch", f"piece-{n}-x")
        (proofs / f"proof-{n}").mkdir()
    (proofs / "proof-7" / "SUMMARY.md").write_text(f"{sha}\nhard_recheck.sh: PASS (earlier FAIL fixed)\n")
    (proofs / "proof-8" / "SUMMARY.md").write_text(f"{sha}\nhard_recheck run1: FAIL\nhard_recheck run2: PASS\n")
    (proofs / "proof-9" / "SUMMARY.md").write_text(f"{sha}\nhard_recheck run1: PASS\nhard_recheck run2: FAIL\n")
    out = _run(repo, proofs)
    assert "| 7 | `piece-7-x` | `" + sha + "` | PASS |" in out
    assert "| 8 | `piece-8-x` | `" + sha + "` | PASS |" in out
    assert "| 9 | `piece-9-x` | `" + sha + "` | FAIL |" in out


def test_verdict_case_insensitive_and_markdown(tmp_path):
    repo, proofs = tmp_path / "r", tmp_path / "p"
    repo.mkdir(); proofs.mkdir()
    _git(repo, "init", "-q", "-b", "main")
    _git(repo, "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-q", "--allow-empty", "-m", "x")
    sha = _git(repo, "rev-parse", "--short=7", "HEAD")
    for n in (10, 11):
        _git(repo, "branch", f"piece-{n}-x")
        (proofs / f"proof-{n}").mkdir()
    (proofs / "proof-10" / "SUMMARY.md").write_text(f"{sha}\nHard recheck: **pass**\nLive privacy FAIL until deploy\n")
    (proofs / "proof-11" / "SUMMARY.md").write_text(f"{sha}\nhard_recheck: Fail\nother PASS\n")
    out = _run(repo, proofs)
    assert "| 10 | `piece-10-x` | `" + sha + "` | PASS |" in out
    assert "| 11 | `piece-11-x` | `" + sha + "` | FAIL |" in out


def test_newer_no_summary_piece_not_recommended(tmp_path):
    repo, proofs = tmp_path / "r", tmp_path / "p"
    repo.mkdir(); proofs.mkdir()
    _git(repo, "init", "-q", "-b", "main")
    _git(repo, "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-q", "--allow-empty", "-m", "x")
    sha = _git(repo, "rev-parse", "--short=7", "HEAD")
    for n in (12, 13):
        _git(repo, "branch", f"piece-{n}-x")
    (proofs / "proof-12").mkdir()
    (proofs / "proof-12" / "SUMMARY.md").write_text(f"{sha}\nhard_recheck.sh: PASS\n")
    out = _run(repo, proofs)
    assert "| 13 | `piece-13-x` | `" + sha + "` | no-summary |" in out
    assert "Recommended tip (merge-stack head with PASS proof): piece-12-x @ " + sha in out


def test_newer_proof_dir_without_summary_not_recommended(tmp_path):
    repo, proofs = tmp_path / "r", tmp_path / "p"
    repo.mkdir(); proofs.mkdir()
    _git(repo, "init", "-q", "-b", "main")
    _git(repo, "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-q", "--allow-empty", "-m", "x")
    sha = _git(repo, "rev-parse", "--short=7", "HEAD")
    for n in (12, 13):
        _git(repo, "branch", f"piece-{n}-x")
    for n in (12, 13):
        (proofs / f"proof-{n}").mkdir()
    (proofs / "proof-12" / "SUMMARY.md").write_text(f"{sha}\nhard_recheck.sh: PASS\n")
    (proofs / "proof-13" / "notes.txt").write_text("hard_recheck PASS\n")
    out = _run(repo, proofs)
    assert "| 13 | `piece-13-x` | `" + sha + "` | no-summary |" in out
    assert "Recommended tip (merge-stack head with PASS proof): piece-12-x @ " + sha in out


def test_newer_empty_summary_not_recommended(tmp_path):
    repo, proofs = tmp_path / "r", tmp_path / "p"
    repo.mkdir(); proofs.mkdir()
    _git(repo, "init", "-q", "-b", "main")
    _git(repo, "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-q", "--allow-empty", "-m", "x")
    sha = _git(repo, "rev-parse", "--short=7", "HEAD")
    for n in (14, 15):
        _git(repo, "branch", f"piece-{n}-x")
        (proofs / f"proof-{n}").mkdir()
    (proofs / "proof-14" / "SUMMARY.md").write_text(f"{sha}\nhard_recheck.sh: PASS\n")
    (proofs / "proof-15" / "SUMMARY.md").write_text("")
    out = _run(repo, proofs)
    assert "Recommended tip (merge-stack head with PASS proof): piece-14-x @ " + sha in out
    assert "piece-15-x @" not in out.split("Recommended tip")[-1]


def test_newer_whitespace_only_summary_not_recommended(tmp_path):
    repo, proofs = tmp_path / "r", tmp_path / "p"
    repo.mkdir(); proofs.mkdir()
    _git(repo, "init", "-q", "-b", "main")
    _git(repo, "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-q", "--allow-empty", "-m", "x")
    sha = _git(repo, "rev-parse", "--short=7", "HEAD")
    for n in (16, 17):
        _git(repo, "branch", f"piece-{n}-x")
        (proofs / f"proof-{n}").mkdir()
    (proofs / "proof-16" / "SUMMARY.md").write_text(f"{sha}\nhard_recheck.sh: PASS\n")
    (proofs / "proof-17" / "SUMMARY.md").write_text("  \n\t\n\n")
    out = _run(repo, proofs)
    assert "Recommended tip (merge-stack head with PASS proof): piece-16-x @ " + sha in out
    assert "piece-17-x @" not in out.split("Recommended tip")[-1]


def test_newer_summary_without_verdict_not_recommended(tmp_path):
    repo, proofs = tmp_path / "r", tmp_path / "p"
    repo.mkdir(); proofs.mkdir()
    _git(repo, "init", "-q", "-b", "main")
    _git(repo, "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-q", "--allow-empty", "-m", "x")
    sha = _git(repo, "rev-parse", "--short=7", "HEAD")
    for n in (18, 19):
        _git(repo, "branch", f"piece-{n}-x")
        (proofs / f"proof-{n}").mkdir()
    (proofs / "proof-18" / "SUMMARY.md").write_text(f"{sha}\nhard_recheck.sh: PASS\n")
    (proofs / "proof-19" / "SUMMARY.md").write_text(f"{sha}\nhard_recheck.sh: still running\n")
    out = _run(repo, proofs)
    assert "Recommended tip (merge-stack head with PASS proof): piece-18-x @ " + sha in out
    assert "piece-19-x @" not in out.split("Recommended tip")[-1]


def test_newer_summary_with_fail_verdict_not_recommended(tmp_path):
    repo, proofs = tmp_path / "r", tmp_path / "p"
    repo.mkdir(); proofs.mkdir()
    _git(repo, "init", "-q", "-b", "main")
    _git(repo, "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-q", "--allow-empty", "-m", "x")
    sha = _git(repo, "rev-parse", "--short=7", "HEAD")
    for n in (20, 21):
        _git(repo, "branch", f"piece-{n}-x")
        (proofs / f"proof-{n}").mkdir()
    (proofs / "proof-20" / "SUMMARY.md").write_text(f"{sha}\nhard_recheck.sh: PASS\n")
    (proofs / "proof-21" / "SUMMARY.md").write_text(f"{sha}\nhard_recheck.sh: FAIL\n")
    out = _run(repo, proofs)
    assert "Recommended tip (merge-stack head with PASS proof): piece-20-x @ " + sha in out
    assert "piece-21-x @" not in out.split("Recommended tip")[-1]


def test_newer_summary_pass_then_fail_not_recommended(tmp_path):
    repo, proofs = tmp_path / "r", tmp_path / "p"
    repo.mkdir(); proofs.mkdir()
    _git(repo, "init", "-q", "-b", "main")
    _git(repo, "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-q", "--allow-empty", "-m", "x")
    sha = _git(repo, "rev-parse", "--short=7", "HEAD")
    for n in (22, 23):
        _git(repo, "branch", f"piece-{n}-x")
        (proofs / f"proof-{n}").mkdir()
    (proofs / "proof-22" / "SUMMARY.md").write_text(f"{sha}\nhard_recheck.sh: PASS\n")
    (proofs / "proof-23" / "SUMMARY.md").write_text(f"{sha}\nhard_recheck.sh: PASS\nre-run hard_recheck.sh: FAIL\n")
    out = _run(repo, proofs)
    assert "Recommended tip (merge-stack head with PASS proof): piece-22-x @ " + sha in out
    assert "piece-23-x @" not in out.split("Recommended tip")[-1]


def test_newer_summary_fail_then_pass_recommended(tmp_path):
    repo, proofs = tmp_path / "r", tmp_path / "p"
    repo.mkdir(); proofs.mkdir()
    _git(repo, "init", "-q", "-b", "main")
    _git(repo, "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-q", "--allow-empty", "-m", "x")
    sha = _git(repo, "rev-parse", "--short=7", "HEAD")
    for n in (24, 25):
        _git(repo, "branch", f"piece-{n}-x")
        (proofs / f"proof-{n}").mkdir()
    (proofs / "proof-24" / "SUMMARY.md").write_text(f"{sha}\nhard_recheck.sh: PASS\n")
    (proofs / "proof-25" / "SUMMARY.md").write_text(f"{sha}\nhard_recheck.sh: FAIL\nre-run hard_recheck.sh: PASS\n")
    out = _run(repo, proofs)
    assert "Recommended tip (merge-stack head with PASS proof): piece-25-x @ " + sha in out


def test_newer_summary_fail_pass_fail_not_recommended(tmp_path):
    repo, proofs = tmp_path / "r", tmp_path / "p"
    repo.mkdir(); proofs.mkdir()
    _git(repo, "init", "-q", "-b", "main")
    _git(repo, "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-q", "--allow-empty", "-m", "x")
    sha = _git(repo, "rev-parse", "--short=7", "HEAD")
    for n in (26, 27):
        _git(repo, "branch", f"piece-{n}-x")
        (proofs / f"proof-{n}").mkdir()
    (proofs / "proof-26" / "SUMMARY.md").write_text(f"{sha}\nhard_recheck.sh: PASS\n")
    (proofs / "proof-27" / "SUMMARY.md").write_text(
        f"{sha}\nhard_recheck.sh: FAIL\nre-run hard_recheck.sh: PASS\nfinal hard_recheck.sh: FAIL\n")
    out = _run(repo, proofs)
    assert "Recommended tip (merge-stack head with PASS proof): piece-26-x @ " + sha in out
    assert "piece-27-x @" not in out.split("Recommended tip")[-1]


def test_newer_summary_pass_fail_pass_recommended(tmp_path):
    repo, proofs = tmp_path / "r", tmp_path / "p"
    repo.mkdir(); proofs.mkdir()
    _git(repo, "init", "-q", "-b", "main")
    _git(repo, "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-q", "--allow-empty", "-m", "x")
    sha = _git(repo, "rev-parse", "--short=7", "HEAD")
    for n in (28, 29):
        _git(repo, "branch", f"piece-{n}-x")
        (proofs / f"proof-{n}").mkdir()
    (proofs / "proof-28" / "SUMMARY.md").write_text(f"{sha}\nhard_recheck.sh: PASS\n")
    (proofs / "proof-29" / "SUMMARY.md").write_text(
        f"{sha}\nhard_recheck.sh: PASS\nre-run hard_recheck.sh: FAIL\nfinal hard_recheck.sh: PASS\n")
    out = _run(repo, proofs)
    assert "Recommended tip (merge-stack head with PASS proof): piece-29-x @ " + sha in out


def test_newer_summary_pass_fail_pass_fail_not_recommended(tmp_path):
    repo, proofs = tmp_path / "r", tmp_path / "p"
    repo.mkdir(); proofs.mkdir()
    _git(repo, "init", "-q", "-b", "main")
    _git(repo, "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-q", "--allow-empty", "-m", "x")
    sha = _git(repo, "rev-parse", "--short=7", "HEAD")
    for n in (30, 31):
        _git(repo, "branch", f"piece-{n}-x")
        (proofs / f"proof-{n}").mkdir()
    (proofs / "proof-30" / "SUMMARY.md").write_text(f"{sha}\nhard_recheck.sh: PASS\n")
    (proofs / "proof-31" / "SUMMARY.md").write_text(
        f"{sha}\nhard_recheck.sh: PASS\nre-run hard_recheck.sh: FAIL\n"
        "again hard_recheck.sh: PASS\nfinal hard_recheck.sh: FAIL\n")
    out = _run(repo, proofs)
    assert "Recommended tip (merge-stack head with PASS proof): piece-30-x @ " + sha in out
    assert "piece-31-x @" not in out.split("Recommended tip")[-1]


def test_newer_summary_fail_pass_fail_pass_recommended(tmp_path):
    repo, proofs = tmp_path / "r", tmp_path / "p"
    repo.mkdir(); proofs.mkdir()
    _git(repo, "init", "-q", "-b", "main")
    _git(repo, "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-q", "--allow-empty", "-m", "x")
    sha = _git(repo, "rev-parse", "--short=7", "HEAD")
    for n in (32, 33):
        _git(repo, "branch", f"piece-{n}-x")
        (proofs / f"proof-{n}").mkdir()
    (proofs / "proof-32" / "SUMMARY.md").write_text(f"{sha}\nhard_recheck.sh: PASS\n")
    (proofs / "proof-33" / "SUMMARY.md").write_text(
        f"{sha}\nhard_recheck.sh: FAIL\nre-run hard_recheck.sh: PASS\n"
        "again hard_recheck.sh: FAIL\nfinal hard_recheck.sh: PASS\n")
    out = _run(repo, proofs)
    assert "Recommended tip (merge-stack head with PASS proof): piece-33-x @ " + sha in out


def test_newer_summary_pass_fail_pass_fail_pass_recommended(tmp_path):
    repo, proofs = tmp_path / "r", tmp_path / "p"
    repo.mkdir(); proofs.mkdir()
    _git(repo, "init", "-q", "-b", "main")
    _git(repo, "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-q", "--allow-empty", "-m", "x")
    sha = _git(repo, "rev-parse", "--short=7", "HEAD")
    for n in (34, 35):
        _git(repo, "branch", f"piece-{n}-x")
        (proofs / f"proof-{n}").mkdir()
    (proofs / "proof-34" / "SUMMARY.md").write_text(f"{sha}\nhard_recheck.sh: PASS\n")
    (proofs / "proof-35" / "SUMMARY.md").write_text(
        f"{sha}\nhard_recheck.sh: PASS\nre-run hard_recheck.sh: FAIL\n"
        "again hard_recheck.sh: PASS\nonce more hard_recheck.sh: FAIL\nfinal hard_recheck.sh: PASS\n")
    out = _run(repo, proofs)
    assert "Recommended tip (merge-stack head with PASS proof): piece-35-x @ " + sha in out


def test_newer_summary_fail_pass_fail_pass_fail_not_recommended(tmp_path):
    repo, proofs = tmp_path / "r", tmp_path / "p"
    repo.mkdir(); proofs.mkdir()
    _git(repo, "init", "-q", "-b", "main")
    _git(repo, "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-q", "--allow-empty", "-m", "x")
    sha = _git(repo, "rev-parse", "--short=7", "HEAD")
    for n in (36, 37):
        _git(repo, "branch", f"piece-{n}-x")
        (proofs / f"proof-{n}").mkdir()
    (proofs / "proof-36" / "SUMMARY.md").write_text(f"{sha}\nhard_recheck.sh: PASS\n")
    (proofs / "proof-37" / "SUMMARY.md").write_text(
        f"{sha}\nhard_recheck.sh: FAIL\nre-run hard_recheck.sh: PASS\n"
        "again hard_recheck.sh: FAIL\nonce more hard_recheck.sh: PASS\nfinal hard_recheck.sh: FAIL\n")
    out = _run(repo, proofs)
    assert "Recommended tip (merge-stack head with PASS proof): piece-36-x @ " + sha in out
    assert "piece-37-x @" not in out.split("Recommended tip")[-1]


def test_newer_summary_pass_fail_pass_fail_pass_fail_not_recommended(tmp_path):
    repo, proofs = tmp_path / "r", tmp_path / "p"
    repo.mkdir(); proofs.mkdir()
    _git(repo, "init", "-q", "-b", "main")
    _git(repo, "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-q", "--allow-empty", "-m", "x")
    sha = _git(repo, "rev-parse", "--short=7", "HEAD")
    for n in (38, 39):
        _git(repo, "branch", f"piece-{n}-x")
        (proofs / f"proof-{n}").mkdir()
    (proofs / "proof-38" / "SUMMARY.md").write_text(f"{sha}\nhard_recheck.sh: PASS\n")
    (proofs / "proof-39" / "SUMMARY.md").write_text(
        f"{sha}\nhard_recheck.sh: PASS\nre-run hard_recheck.sh: FAIL\n"
        "again hard_recheck.sh: PASS\nonce more hard_recheck.sh: FAIL\n"
        "yet again hard_recheck.sh: PASS\nfinal hard_recheck.sh: FAIL\n")
    out = _run(repo, proofs)
    assert "Recommended tip (merge-stack head with PASS proof): piece-38-x @ " + sha in out
    assert "piece-39-x @" not in out.split("Recommended tip")[-1]


def test_newer_summary_fail_pass_fail_pass_fail_pass_recommended(tmp_path):
    repo, proofs = tmp_path / "r", tmp_path / "p"
    repo.mkdir(); proofs.mkdir()
    _git(repo, "init", "-q", "-b", "main")
    _git(repo, "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-q", "--allow-empty", "-m", "x")
    sha = _git(repo, "rev-parse", "--short=7", "HEAD")
    for n in (40, 41):
        _git(repo, "branch", f"piece-{n}-x")
        (proofs / f"proof-{n}").mkdir()
    (proofs / "proof-40" / "SUMMARY.md").write_text(f"{sha}\nhard_recheck.sh: PASS\n")
    (proofs / "proof-41" / "SUMMARY.md").write_text(
        f"{sha}\nhard_recheck.sh: FAIL\nre-run hard_recheck.sh: PASS\n"
        "again hard_recheck.sh: FAIL\nonce more hard_recheck.sh: PASS\n"
        "yet again hard_recheck.sh: FAIL\nfinal hard_recheck.sh: PASS\n")
    out = _run(repo, proofs)
    assert "Recommended tip (merge-stack head with PASS proof): piece-41-x @ " + sha in out


def test_header_comment_says_run_after_summary():
    from pathlib import Path
    script = Path(__file__).resolve().parents[1] / "overnight_tip_status.sh"
    head = script.read_text().splitlines()[:3]
    assert any("AFTER" in l and "SUMMARY.md" in l for l in head)
    assert "overnight-tip-status-lag.md" in "\n".join(head)
