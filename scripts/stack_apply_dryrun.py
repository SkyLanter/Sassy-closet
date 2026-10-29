#!/usr/bin/env python3
"""Stack apply dry-run (READ-ONLY).

Reads the suggested merge order from the newest REVIEW-GUIDE.md in the draft
bundle, applies each piece's patches in order with `git am --3way` onto a
temporary detached worktree of main, records clean / conflict / already
included, runs the tests on the final stack, writes a markdown report, and
removes the temp worktree. No branch is created or moved; nothing is sent.

Piece 68: when a bundle folder <NN>-rebased-*/rebased/<piece>.patch exists,
that rebased patch is used instead of the piece's own patches (newest folder
wins); --no-rebased uses the originals only.

Piece 97: --guide PATH picks the REVIEW-GUIDE.md explicitly. Without it the
newest guide in the bundle is used, but its highest piece is compared with the
newest INVENTORY.tsv piece; an older guide prints a WARNING and exits 3 unless
--allow-stale. The guide path and its piece range go in the report.
"""
import argparse
import os
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile

DEFAULT_BUNDLE = "/workspace/sassy-closet/out/pending-draft-prs.tgz"
DEFAULT_MAIN = "d13ec40"
DEFAULT_OUT = "out/review/STACK-DRYRUN.md"
GIT_ENV = {"GIT_AUTHOR_NAME": "dryrun", "GIT_AUTHOR_EMAIL": "",
           "GIT_COMMITTER_NAME": "dryrun", "GIT_COMMITTER_EMAIL": ""}

_ORDER = re.compile(r"^\s*\d+\.\s+(\d{2,}[\w-]*)")


def piece_key(name):
    """Piece 101: numeric sort so 100 comes after 99."""
    m = re.match(r"^(\d+)", name)
    return (int(m.group(1)) if m else -1, name)


def _lead_num(p):
    m = re.match(r"^(\d{2,})", p)
    return int(m.group(1)) if m else None


_NOT_LISTED = re.compile(r"^Not listed \(already included[^)]*\):(.*)$")


def _git(repo, *args, check=True):
    env = dict(os.environ, **GIT_ENV)
    return subprocess.run(["git", "-C", repo, *args], capture_output=True,
                          text=True, env=env, check=check)


def open_bundle(path, tmp):
    """Return the unpacked bundle directory (extracts a .tgz into tmp)."""
    if os.path.isdir(path):
        return path
    with tarfile.open(path) as tf:
        try:
            tf.extractall(tmp, filter="data")
        except TypeError:
            tf.extractall(tmp)
    for root, dirs, files in os.walk(tmp):
        if "INVENTORY.tsv" in files:
            return root
    raise SystemExit("bundle has no INVENTORY.tsv")


def find_guide(bundle):
    best = None
    for name in sorted(os.listdir(bundle), key=piece_key):
        g = os.path.join(bundle, name, "proof", "REVIEW-GUIDE.md")
        if os.path.isfile(g):
            best = g
    return best


STALE_EXIT = 3


def guide_range(order, included):
    """(lowest, highest) two-digit piece numbers named by a guide, or (None, None)."""
    nums = [n for n in (_lead_num(p) for p in list(order) + list(included)) if n is not None]
    return (min(nums), max(nums)) if nums else (None, None)


def inventory_max(bundle):
    """Highest two-digit piece number in the bundle's INVENTORY.tsv, or None."""
    path = os.path.join(bundle, "INVENTORY.tsv")
    best = None
    if os.path.isfile(path):
        with open(path, encoding="utf-8") as fh:
            for ln in fh:
                m = re.match(r"^(\d{2,})-", ln)
                if m:
                    best = max(best or 0, int(m.group(1)))
    return best


class StaleGuide(Exception):
    pass


def parse_guide(text):
    """(merge_order, already_included) from a REVIEW-GUIDE.md."""
    order, included, in_order = [], [], False
    for ln in text.splitlines():
        if ln.startswith("## "):
            in_order = ln.strip().lower() == "## suggested merge order"
            continue
        m = _NOT_LISTED.match(ln.strip())
        if m:
            included += re.findall(r"\b\d{2,}[\w-]*", m.group(1))
            continue
        if in_order:
            m = _ORDER.match(ln)
            if m:
                order.append(m.group(1))
    return order, included


# Piece 69: any <NN>-*/rebased/ folder counts (e.g. 69-guide-count-38-test), not only <NN>-rebased-*.
_REBASED_DIR = re.compile(r"^\d{2,}-[\w-]+$")


def rebased_patch(bundle, piece):
    """Newest <NN>-*/rebased/<piece>.patch in the bundle (highest NN wins), or None."""
    best = None
    for name in sorted(os.listdir(bundle), key=piece_key):
        if _REBASED_DIR.match(name):
            cand = os.path.join(bundle, name, "rebased", piece + ".patch")
            if os.path.isfile(cand):
                best = cand
    return best


def patches_for(bundle, piece, prefer_rebased=True):
    """Patches for a piece; a rebased patch (piece 68+) wins when present."""
    if prefer_rebased:
        rb = rebased_patch(bundle, piece)
        if rb:
            return [rb]
    pd = os.path.join(bundle, piece, "patches")
    if not os.path.isdir(pd):
        return []
    return [os.path.join(pd, n) for n in sorted(os.listdir(pd)) if n.endswith(".patch")]


def apply_piece(wt, patches):
    """Return ('clean'|'included'|'conflict'|'missing', detail)."""
    if not patches:
        return "missing", "no patches in bundle"
    before = _git(wt, "rev-parse", "HEAD").stdout.strip()
    r = _git(wt, "am", "--3way", "--keep-cr", *patches, check=False)
    if r.returncode != 0:
        out = (r.stdout + r.stderr)
        files = sorted(set(re.findall(r"CONFLICT \([^)]*\): (?:Merge conflict in )?(\S+)", out)))
        _git(wt, "am", "--abort", check=False)
        _git(wt, "reset", "--hard", before, check=False)
        return "conflict", ", ".join(files) or out.strip().splitlines()[-1][:160]
    after = _git(wt, "rev-parse", "HEAD").stdout.strip()
    if after == before:
        return "included", "patches already present (no change)"
    if not _git(wt, "diff", "--name-only", before, after).stdout.strip():
        _git(wt, "reset", "--hard", before, check=False)
        return "included", "patches applied empty (already present)"
    return "clean", "%d patch(es)" % len(patches)


def run_tests(wt, python):
    r = subprocess.run(["nice", "-n", "19", python, "-m", "pytest", "-q", "-p",
                        "no:cacheprovider", "scripts/tests"], cwd=wt,
                       capture_output=True, text=True)
    lines = [l for l in r.stdout.strip().splitlines() if l.strip()]
    return r.returncode, (lines[-1] if lines else r.stderr.strip()[-200:])


HEAD_WARNING = "WARNING: head may be wrong"


def dryrun(repo, bundle, main, python=sys.executable, tests=True, prefer_rebased=True, force=False,
           guide_path=None, allow_stale=False):
    tmp = tempfile.mkdtemp(prefix="stack-dryrun-")
    wt = os.path.join(tmp, "wt")
    res = {"main": main, "rows": [], "test": None}
    try:
        b = open_bundle(bundle, os.path.join(tmp, "bundle"))
        guide = os.path.abspath(guide_path) if guide_path else find_guide(b)
        if not guide or not os.path.isfile(guide):
            raise SystemExit("no REVIEW-GUIDE.md in bundle" if not guide_path
                             else "guide not found: %s" % guide_path)
        with open(guide, encoding="utf-8") as fh:
            gtext = fh.read()
        if HEAD_WARNING in gtext and not force:
            raise SystemExit("refusing: guide %s says '%s'; regenerate it or pass --force"
                             % (os.path.relpath(guide, b), HEAD_WARNING))
        order, included = parse_guide(gtext)
        lo, hi = guide_range(order, included)
        inv = inventory_max(b)
        res["guide"] = os.path.relpath(guide, b) if guide.startswith(os.path.abspath(b) + os.sep) else guide
        res["guide_range"] = "%02d-%02d" % (lo, hi) if hi is not None else "?"
        res["guide_source"] = "--guide" if guide_path else "newest in bundle"
        res["inventory_max"] = inv
        res["stale"] = None
        if hi is not None and inv is not None and hi < inv:
            res["stale"] = "WARNING: guide covers up to %02d but bundle has %02d" % (hi, inv)
            if not guide_path:
                print(res["stale"], file=sys.stderr)
                if not allow_stale:
                    raise StaleGuide(res["stale"])
        res["main_sha"] = _git(repo, "rev-parse", "--short", main).stdout.strip()
        _git(repo, "worktree", "add", "--detach", wt, main)
        for p in included:
            res["rows"].append((p, "included", "listed as already in the main chain"))
        for p in order:
            pats = patches_for(b, p, prefer_rebased)
            st, det = apply_piece(wt, pats)
            if pats and os.path.basename(os.path.dirname(pats[0])) == "rebased":
                det += " [rebased: %s]" % os.path.relpath(pats[0], b)
            res["rows"].append((p, st, det))
        res["final_sha"] = _git(wt, "rev-parse", "--short", "HEAD").stdout.strip()
        if tests:
            res["test"] = run_tests(wt, python)
    finally:
        _git(repo, "worktree", "remove", "--force", wt, check=False)
        _git(repo, "worktree", "prune", check=False)
        shutil.rmtree(tmp, ignore_errors=True)
    return res


def render(res):
    by = {}
    for p, st, _ in res["rows"]:
        by.setdefault(st, []).append(p)
    out = ["# Stack apply dry-run", "",
           "Read-only. Temp worktree only; removed after the run. Nothing pushed, merged or sent.", "",
           "- Main: %s (%s)" % (res["main"], res.get("main_sha", "?")),
           "- Merge order from: %s (%s)" % (res.get("guide", "?"), res.get("guide_source", "?")),
           "- Guide range: %s; newest INVENTORY piece: %s" % (
               res.get("guide_range", "?"),
               "%02d" % res["inventory_max"] if res.get("inventory_max") is not None else "?"),
           "- Final temp HEAD: %s" % res.get("final_sha", "?")]
    if res.get("stale"):
        out.append("- %s" % res["stale"])
    out.append("")
    for st in ("clean", "conflict", "included", "missing"):
        out.append("- %s (%d): %s" % (st.capitalize(), len(by.get(st, [])), ", ".join(by.get(st, [])) or "none"))
    if res["test"] is not None:
        out += ["", "Tests on final stack: %s (exit %d)" % (res["test"][1], res["test"][0])]
    out += ["", "| Piece | Result | Detail |", "|---|---|---|"]
    out += ["| %s | %s | %s |" % (p, st, d.replace("|", "/")) for p, st, d in res["rows"]]
    return "\n".join(out) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--repo", default=".")
    ap.add_argument("--bundle", default=DEFAULT_BUNDLE)
    ap.add_argument("--main", default=DEFAULT_MAIN)
    ap.add_argument("--out", default=DEFAULT_OUT)
    ap.add_argument("--no-tests", action="store_true")
    ap.add_argument("--no-rebased", action="store_true", help="ignore <NN>-rebased-* patches (original patches only)")
    ap.add_argument("--force", action="store_true", help="run even if the guide says the head may be wrong")
    ap.add_argument("--guide", help="REVIEW-GUIDE.md to use instead of the newest in the bundle")
    ap.add_argument("--allow-stale", action="store_true", help="run even if the newest guide is older than INVENTORY")
    a = ap.parse_args(argv)
    try:
        res = dryrun(os.path.abspath(a.repo), a.bundle, a.main, tests=not a.no_tests,
                     prefer_rebased=not a.no_rebased, force=a.force,
                     guide_path=a.guide, allow_stale=a.allow_stale)
    except StaleGuide:
        return STALE_EXIT
    text = render(res)
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    with open(a.out, "w", encoding="utf-8") as fh:
        fh.write(text)
    print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
