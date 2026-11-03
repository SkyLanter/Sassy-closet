"""Piece 228: classify an unmerged branch against a combined base (read-only on the repo).

Classes:
  A  new safety/check logic: production change whose own tests fail on base without it
     (and pass with it, or need a manual port when it does not apply) (tagged safety-critical when it touches mã/held/S06/never/privacy words)
  B  tests only: no production change; its tests pass on base as-is
  C  already redone: patch-id equivalent to base, or its tests already pass on base
  D  obsolete/conflicting: touches data/held.json, removes lock/guard words, or adds a privacy leak
  E  unclear: no test evidence, does not apply, or its tests fail even with the change

Trials run in throwaway detached worktrees under `scratch`, always removed. No refs,
branches or the main worktree are touched. `test_hook(tree, mode, files) -> bool` runs tests.
"""
from __future__ import annotations

import re
import shutil
import subprocess
import tempfile
from collections import Counter
from pathlib import Path
from typing import Callable, Optional

LOCK_WORDS = ("held", "neverlist", "never_list", "never-list", "s06", "publishblock", "reuse",
              "collision", "privacy", "lock", "guard", "blocked")
SAFETY_WORDS = LOCK_WORDS + ("normalizema", "norm_ma", "canonical", "mint")
FORBIDDEN_PATHS = ("data/held.json",)
LEAK = [re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+\.[A-Za-z]{2,}"),
        re.compile(r"(taobao|tmall|1688)\.com", re.I)]

TestHook = Callable[[Path, str, list], Optional[bool]]


def _git(repo, *args, check=True, input=None) -> str:
    r = subprocess.run(["git", *args], cwd=repo, capture_output=True, text=input is None or isinstance(input, str),
                       input=input)
    if check and r.returncode:
        raise RuntimeError(f"git {' '.join(args)}: {r.stderr}")
    return r.stdout


def is_test_path(path: str) -> bool:
    return bool(re.search(r"(^|/)tests?/|(^|/)testdata/|\.test\.[jt]sx?$|(^|/)test_[^/]*\.py$", path))


def changed_files(repo, base: str, branch: str) -> list[str]:
    mb = _git(repo, "merge-base", base, branch).strip()
    return [f for f in _git(repo, "diff", "--name-only", f"{mb}..{branch}").splitlines() if f]


def patch_equivalent(repo, base: str, branch: str) -> bool:
    lines = [l for l in _git(repo, "cherry", base, branch).splitlines() if l]
    return all(l.startswith("-") for l in lines)


def _added_removed(repo, base, branch, files):
    mb = _git(repo, "merge-base", base, branch).strip()
    diff = _git(repo, "diff", "-U0", f"{mb}..{branch}", "--", *files) if files else ""
    add = [l[1:] for l in diff.splitlines() if l.startswith("+") and not l.startswith("+++")]
    rem = [l[1:] for l in diff.splitlines() if l.startswith("-") and not l.startswith("---")]
    return add, rem


def _words(lines, words) -> Counter:
    c = Counter()
    for l in lines:
        low = l.lower()
        for w in words:
            c[w] += low.count(w)
    return c


def red_flags(repo, base: str, branch: str) -> list[str]:
    files = changed_files(repo, base, branch)
    flags = [f"touches {p}" for p in files if p in FORBIDDEN_PATHS]
    prod = [f for f in files if not is_test_path(f)]
    add, rem = _added_removed(repo, base, branch, prod)
    a, r = _words(add, LOCK_WORDS), _words(rem, LOCK_WORDS)
    flags += [f"removes '{w}' ({r[w]} out, {a[w]} in) in production code" for w in LOCK_WORDS if r[w] > a[w]]
    all_add, _ = _added_removed(repo, base, branch, files)
    for l in all_add:
        if any(p.search(l) for p in LEAK):
            flags.append("adds a possible privacy leak (email/supplier link)")
            break
    return flags


def trial(repo, base: str, branch: str, mode: str, hook: TestHook, scratch: Path) -> tuple[bool, Optional[bool]]:
    """Apply the branch diff (all, or tests only) to a detached worktree of base; run hook.
    Returns (applied, tests_passed). The worktree is always removed."""
    files = changed_files(repo, base, branch)
    pick = [f for f in files if is_test_path(f)] if mode == "tests-only" else files
    mb = _git(repo, "merge-base", base, branch).strip()
    scratch.mkdir(parents=True, exist_ok=True)
    tree = Path(tempfile.mkdtemp(prefix=f"{mode}-", dir=scratch))
    shutil.rmtree(tree)
    _git(repo, "worktree", "add", "-q", "--detach", str(tree), base)
    try:
        if pick:
            diff = subprocess.run(["git", "diff", "--binary", f"{mb}..{branch}", "--", *pick], cwd=repo,
                                  capture_output=True).stdout
            ok = subprocess.run(["git", "apply", "--whitespace=nowarn"], cwd=tree, input=diff,
                                capture_output=True).returncode == 0
            if not ok:
                ok = subprocess.run(["git", "apply", "--3way", "--whitespace=nowarn"], cwd=tree, input=diff,
                                    capture_output=True).returncode == 0
            if not ok:
                return False, None
        return True, hook(tree, mode, pick)
    finally:
        _git(repo, "worktree", "remove", "--force", str(tree), check=False)
        shutil.rmtree(tree, ignore_errors=True)
        _git(repo, "worktree", "prune", check=False)


def classify_branch(repo, branch: str, base: str, test_hook: Optional[TestHook] = None,
                    scratch: Optional[Path] = None) -> dict:
    repo = Path(repo)
    files = changed_files(repo, base, branch)
    prod = [f for f in files if not is_test_path(f)]
    tests = [f for f in files if is_test_path(f)]
    out = {"branch": branch, "files": files, "prod": prod, "tests": tests,
           "applies": None, "tests_only": None, "full": None, "reasons": [], "cls": "E"}
    if patch_equivalent(repo, base, branch):
        out.update(cls="C", reasons=["every commit is patch-id equivalent to one in base"])
        return out
    flags = red_flags(repo, base, branch)
    if flags:
        out.update(cls="D", reasons=flags)
        return out
    if test_hook is None:
        out["reasons"] = ["no test hook: no evidence"]
        return out
    scratch = Path(scratch or tempfile.mkdtemp(prefix="branch-triage-"))
    if tests:
        _, out["tests_only"] = trial(repo, base, branch, "tests-only", test_hook, scratch)
    out["applies"], out["full"] = trial(repo, base, branch, "full", test_hook, scratch)
    add, _ = _added_removed(repo, base, branch, prod)
    safety = sum(_words(add, SAFETY_WORDS).values()) > 0
    if not prod:
        if out["tests_only"]:
            out.update(cls="B", reasons=["tests only; they pass on base as-is"])
        else:
            out["reasons"] = ["tests only, but they fail on base: behaviour missing with no code to add it"]
    elif not tests:
        out["reasons"] = ["production change with no tests of its own"
                          + ("" if out["applies"] else "; does not apply on base (conflicts)")]
    elif out["tests_only"]:
        out.update(cls="C", reasons=["its tests already pass on base without its code: behaviour redone"])
    elif out["tests_only"] is False and (out["full"] or not out["applies"]):
        why = "its tests fail on base" + (" and pass with its code" if out["applies"]
                                          else "; code does not apply cleanly (manual port needed)")
        out.update(cls="A", reasons=[why + ("; safety-critical words in the change" if safety else "")])
        out["safety"] = safety
    elif not out["applies"]:
        out["reasons"] = ["does not apply on base (conflicts) and no test evidence"]
    else:
        out["reasons"] = ["its tests fail even with its code applied on base"]
    return out
