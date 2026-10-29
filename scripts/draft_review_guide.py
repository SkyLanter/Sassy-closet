#!/usr/bin/env python3
"""Piece 63: READ-ONLY draft review guide.

Reads an unpacked pending-draft-prs bundle (INVENTORY.tsv + each piece's
PROOF.md / recheck.txt / proof/*) and writes a plain-English review guide
(default out/review/REVIEW-GUIDE.md, gitignored). Per piece: what it does and
why it helps, base branch, test count and privacy result from its proof, a
live-behaviour check of its patches, and a suggested merge order that respects
stacking. No network, no git writes, sends nothing.
"""
import argparse
import os
import re
import subprocess
import sys

DEFAULT_BUNDLE = "/workspace/sassy-closet/out/pending-draft-prs"
DEFAULT_OUT = "out/review/REVIEW-GUIDE.md"

# Plain-English notes: (what it does, why it helps the shop)
NOTES = {
    49: ("Counts how many recheck runs in a row each item's Taobao listing has been unreachable.",
         "Shows which live items may have lost their supplier, so Boss can decide on holds."),
    50: ("Checks that the draft bundle folders match INVENTORY.tsv.",
         "Catches a missing or extra draft piece before review."),
    51: ("Gathers every open decision waiting on Boss into one list.",
         "Boss sees all pending calls in one place instead of scattered messages."),
    52: ("Makes the decisions list count Blob photo deletes accurately and show hidden hold/intake items.",
         "Fewer false alarms and no missed decisions."),
    53: ("Reports Facebook/Instagram posts or Reels missing a mã or Giá, and live items with no post.",
         "Customers can always see the code and price on each post."),
    54: ("Flags intake codes reused for different items.",
         "Stops two products sharing one mã and getting the wrong price or photo."),
    55: ("Suggests sell prices for held items waiting on price approval, written to a local file.",
         "Speeds up Boss's price approvals; nothing goes live."),
    56: ("Adds auto-filled sections (decisions, caption gaps, reused codes) to the local Muse pack files.",
         "Luxubu's daily pack stays complete without hand edits; sends nothing."),
    57: ("Drafts the 3:30 PM daily summary to a local file.",
         "A consistent summary is ready to review; sends nothing."),
    58: ("Adds caption gaps, the direct hold question and price mismatches to the summary draft.",
         "Boss's summary no longer misses open items."),
    59: ("Splits the summary's mismatch list by reason.",
         "Each item that needs Boss says clearly what is wrong."),
    60: ("Saves a structured list of Meta posts (no caption text) so reports can count live items with no post.",
         "Makes missing-post checks possible without logging in again."),
    61: ("Runs all of today's local reports with one command and writes an index.",
         "One step to refresh every report."),
    62: ("Labels 'gaps found' results as GAPS instead of FAILED in the runner index.",
         "Real failures stand out from known gaps."),
    63: ("Writes this review guide for the pending draft pieces.",
         "Boss can review and merge drafts in the right order quickly."),
    64: ("Teaches the review guide to spot cherry-picked pieces (patch-id or 'Piece NN:' subject) and backfills missing proof facts.",
         "Boss is not asked to merge work that is already in the main chain."),
    82: ("Works out the review guide's chain head from the newest bundle piece and warns when a given head looks wrong.",
         "Stops a wrong head (like main) hiding included pieces and causing false conflicts."),
    65: ("Stops the review guide flagging its own pattern list and test fixtures as live writes; real writes still flagged.",
         "Boss sees fewer false CHECK warnings, so real ones stand out."),
}

LIVE_PATTERNS = [
    (re.compile(r"requests\.(post|put|patch|delete)\("), "HTTP write call"),
    (re.compile(r"urlopen\("), "network call"),
    (re.compile(r"git\s+push|gh\s+pr\s+(merge|create)"), "git push/merge"),
    (re.compile(r"--execute"), "--execute flag"),
    (re.compile(r"graph\.facebook|instagram\.com/api", re.I), "Meta API"),
    (re.compile(r"squareup|vercel\s+(deploy|--prod)|blob\.(put|del)\(", re.I), "live service write"),
]


# Piece 71: fill 'What it does' from the commit subject or PROOF.md first line.
_PIECE_PREFIX = re.compile(r"^\s*(?:(?:fixup|squash)!\s*)*(?:#+\s*)?(?:piece\s*\d+\w*\s*(?:[:\-\u2014\u2013]|proof\b)?\s*)?", re.I)
_REDACT = [re.compile(r"https?://\S+|www\.\S+", re.I),
           re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.-]+\b"),
           re.compile(r"[\u00a5$\uffe5]\s*\d[\d.,]*|\d[\d.,]*\s*(?:\u00a5|\uffe5|usd|cny|rmb)\b", re.I)]
DESC_MAX = 160


def clean_description(text, max_len=DESC_MAX):
    """One plain sentence (<= max_len chars) from a subject/proof line; '' if nothing useful.
    Drops the 'Piece NN:' / fixup! prefix, markdown, links, emails and money amounts."""
    if not text:
        return ""
    t = text.strip().splitlines()[0] if text.strip() else ""
    t = _PIECE_PREFIX.sub("", t)
    for rx in _REDACT:
        t = rx.sub("", t)
    t = re.sub(r"[`*]+", "", t)
    t = re.sub(r"\(\s*[,;]?\s*\)", "", t)
    t = re.sub(r"\s+", " ", t).strip(" -:;,\u2014\u2013")
    if not t or re.fullmatch(r"(?i)proof|draft|\(?draft[^)]*\)?", t):
        return ""
    if len(t) > max_len:
        cut = t[:max_len - 1]
        cut = cut[:cut.rfind(" ")] if " " in cut else cut
        t = cut.rstrip(" ,;:-(\u2014\u2013") + "\u2026"
    t = t[0].upper() + t[1:]
    if not t.endswith((".", "!", "?", "\u2026")):
        t += "."
    return t


def proof_first_line(folder):
    for p in (os.path.join(folder, "PROOF.md"), os.path.join(folder, "proof", "PROOF.md")):
        if os.path.isfile(p):
            with open(p, encoding="utf-8", errors="replace") as fh:
                for ln in fh:
                    if ln.strip():
                        return ln.strip()
    return ""


def describe(n, subject, folder):
    """NOTES first, then commit subject, then PROOF.md first line."""
    if n in NOTES:
        return NOTES[n][0]
    for src in (subject, proof_first_line(folder) if folder else ""):
        d = clean_description(src)
        if d:
            return d
    return None


def piece_num(name):
    m = re.match(r"^(\d{2,})", name)
    return int(m.group(1)) if m else None


def read_inventory(bundle):
    rows = []
    with open(os.path.join(bundle, "INVENTORY.tsv"), encoding="utf-8") as fh:
        for ln in fh:
            p = ln.rstrip("\n").split("\t")
            if len(p) >= 4 and p[0].strip():
                rows.append({"folder": p[0], "commit": p[1], "branch": p[2], "base": p[3]})
    return rows


def proof_texts(folder):
    paths = [os.path.join(folder, n) for n in ("PROOF.md", "recheck.txt")]
    pd = os.path.join(folder, "proof")
    if os.path.isdir(pd):
        names = sorted(os.listdir(pd))
        # Piece 69: PROOF.md first; skip copied guides / stack dry-run reports (other pieces' counts).
        names.sort(key=lambda n: (n != "PROOF.md",))
        paths += [os.path.join(pd, n) for n in names if not _SKIP_PROOF.match(n)]
    out = []
    for p in paths:
        if os.path.isfile(p):
            with open(p, encoding="utf-8", errors="replace") as fh:
                out.append(fh.read())
    return "\n".join(out)


_SKIP_PROOF = re.compile(r"^(REVIEW-GUIDE|STACK-DRYRUN)[\w.-]*\.md$", re.I)
_PASSED = re.compile(r"(\d+)\s+passed")
_REPO_LABEL = re.compile(r"pytest[^\n]*scripts/tests|repo[- ](?:suite|tests?)", re.I)
_NOT_REPO = re.compile(r"dry[- ]?run|\bstack\b|final stack|full stack", re.I)


def repo_test_count(text):
    """Piece 69: the piece's own repo-suite count, not a dry-run/stack number.

    1) a line labelled as the repo tests (pytest ... scripts/tests, "repo suite"/"repo tests");
    2) else the first pytest summary line; lines naming a dry run or stack are ignored.
    """
    lines = [ln for ln in text.splitlines() if _PASSED.search(ln) and not _NOT_REPO.search(ln)]
    for ln in lines:
        if _REPO_LABEL.search(ln):
            return int(_PASSED.search(ln).group(1))
    return int(_PASSED.search(lines[0]).group(1)) if lines else None


def parse_proof(text):
    tests = repo_test_count(text)
    privacy = "not recorded in proof"
    for ln in text.splitlines():
        if "privacy" in ln.lower():
            if re.search(r"\bCLEAN\b", ln):
                privacy = "CLEAN"
                break
            if re.search(r"FAIL|HIT|LEAK", ln):
                privacy = "FLAGGED"
                break
    return tests, privacy


GUIDE_SELF = "scripts/draft_review_guide.py"
GUIDE_TEST = "scripts/tests/test_draft_review_guide.py"
_PATTERN_DEF = re.compile(r"""^\+\s*\(re\.compile\(r?["'].*["'](,\s*re\.\w+)?\),\s*["'][^"']+["']\),?\s*$""")
# diff-line fixtures in the guide's own tests: patch="..." args or literals starting with "+
_FIXTURE = re.compile(r"""patch=("(?:\\.|[^"\\])*"|'(?:\\.|[^'\\])*')|"\+(?:\\.|[^"\\])*"|'\+(?:\\.|[^'\\])*'""")


def _is_self_definition(path, ln):
    """True only for the guide's own LIVE_PATTERNS entries, or fixture strings
    (patch="...") in the guide's own tests, when nothing else on the line matches."""
    if path == GUIDE_SELF:
        return bool(_PATTERN_DEF.match(ln.rstrip("\n")))
    if path == GUIDE_TEST:
        rest = _FIXTURE.sub("", ln[1:])
        return rest != ln[1:] and not any(rx.search(rest) for rx, _ in LIVE_PATTERNS)
    return False


_NET = "network call"
_WRITE_SIGNAL = re.compile(r"""method\s*=\s*["'](POST|PUT|PATCH|DELETE)["']|\bdata\s*=\s*[^N\s)]""", re.I)
_DENY_LIST = re.compile(r"^\+\s*(for\s+\w+\s+in\s*[\(\[]|assert\b.*\bnot\s+in\b)")


def _is_deny_list(path, ln):
    """Test lines that list forbidden strings to assert they are absent (false alarm)."""
    return "tests/" in path and bool(_DENY_LIST.match(ln))


def live_check(folder, detail=False):
    """Live-write labels for a bundle folder. A urlopen with no write signal
    (POST/PUT/PATCH/DELETE method or a data= body) in the same patch is a
    read-only network GET/HEAD and is reported separately, not as a live write."""
    pd = os.path.join(folder, "patches")
    hits, readonly = set(), set()
    if os.path.isdir(pd):
        for n in sorted(os.listdir(pd)):
            if not n.endswith(".patch"):
                continue
            with open(os.path.join(pd, n), encoding="utf-8", errors="replace") as fh:
                cur, added, fhits = "", [], set()
                for ln in fh:
                    if ln.startswith("+++ "):
                        cur = ln[4:].strip()
                        cur = cur[2:] if cur.startswith("b/") else cur
                        continue
                    if ln.startswith("+") and not ln.startswith("+++"):
                        if _is_self_definition(cur, ln) or _is_deny_list(cur, ln):
                            continue
                        added.append(ln)
                        for rx, label in LIVE_PATTERNS:
                            if rx.search(ln):
                                fhits.add(label)
                if _NET in fhits and not any(_WRITE_SIGNAL.search(a) for a in added):
                    fhits.discard(_NET)
                    readonly.add("read-only network")
                hits |= fhits
    return (sorted(hits), sorted(readonly)) if detail else sorted(hits)


def _git(repo, *args, stdin=None):
    try:
        r = subprocess.run(["git", "-C", repo] + list(args), input=stdin, capture_output=True,
                           text=True, timeout=60)
    except (OSError, subprocess.TimeoutExpired):
        return None
    return r.stdout if r.returncode == 0 else None


def _patch_ids(repo, text):
    out = _git(repo, "patch-id", "--stable", stdin=text) or ""
    return [ln.split()[0] for ln in out.splitlines() if ln.split()]


def chain_index(repo, head):
    """Map patch-id -> sha and 'Piece NN' -> sha for commits reachable from head."""
    log = _git(repo, "log", "--format=%H%x09%s", head)
    if log is None:
        return None
    subj = {}
    for ln in log.splitlines():
        sha, _, s = ln.partition("\t")
        m = re.match(r"Piece (\d+):", s)
        if m:
            subj.setdefault(int(m.group(1)), []).append(sha)
    pid = {}
    out = _git(repo, "log", "-p", "--format=commit %H", head) or ""
    for ln in (_git(repo, "patch-id", "--stable", stdin=out) or "").splitlines():
        a = ln.split()
        if len(a) == 2:
            pid[a[0]] = a[1]
    return {"subj": subj, "pid": pid, "head": head}


def cherry_status(repo, idx, row, folder):
    """Return list of chain shas carrying this piece's commits if the piece's own commit is
    not an ancestor of head but its patches (patch-id) or 'Piece NN:' subject are in the chain."""
    if idx is None:
        return None
    if _git(repo, "merge-base", "--is-ancestor", row["commit"], idx["head"]) is not None:
        return None  # already in chain directly (normal stacking)
    found = []
    pd = os.path.join(folder, "patches")
    if os.path.isdir(pd):
        for n in sorted(os.listdir(pd)):
            if n.endswith(".patch"):
                with open(os.path.join(pd, n), encoding="utf-8", errors="replace") as fh:
                    for i in _patch_ids(repo, fh.read()):
                        if i in idx["pid"]:
                            found.append(idx["pid"][i])
    if not found:
        found = list(idx["subj"].get(piece_num(row["folder"]), []))
    found = list(dict.fromkeys(found))
    return found or None


HEAD_WARNING = "WARNING: head may be wrong"


def newest_bundle_commit(bundle, repo):
    """Piece 82: commit of the highest-numbered INVENTORY row that exists in repo, or None."""
    rows = sorted(read_inventory(bundle), key=lambda r: (piece_num(r["folder"]) or -1, r["folder"]))
    for r in reversed(rows):
        if r["commit"] and _git(repo, "cat-file", "-e", r["commit"] + "^{commit}") is not None:
            return r["commit"]
    return None


def _included_count(bundle, rows, repo, head):
    idx = chain_index(repo, head)
    n = 0
    for r in rows:
        folder = os.path.join(bundle, r["folder"])
        if os.path.isdir(folder) and cherry_status(repo, idx, r, folder):
            n += 1
    return n


def head_check(bundle, repo, head, rows=None):
    """Piece 82: (warning or None). Warns when head finds no cherry-picked pieces but the chain tip does."""
    tip = newest_bundle_commit(bundle, repo)
    if not tip or not head:
        return None
    rows = read_inventory(bundle) if rows is None else rows
    if _included_count(bundle, rows, repo, head) > 0:
        return None
    tip_n = _included_count(bundle, rows, repo, tip)
    if tip_n == 0:
        return None
    return (f"{HEAD_WARNING}: --head {head} contains none of the known cherry-picked pieces, "
            f"but the chain tip {tip[:7]} contains {tip_n}. Rerun without --head or with the chain tip.")


def merge_order(rows):
    by_branch = {r["branch"]: r for r in rows}
    done, order = set(), []

    def visit(r, stack=()):
        if r["folder"] in done or r["folder"] in stack:
            return
        dep = by_branch.get(r["base"])
        if dep:
            visit(dep, stack + (r["folder"],))
        done.add(r["folder"])
        order.append(r)

    for r in sorted(rows, key=lambda x: (piece_num(x["folder"]) or 0, x["folder"])):
        visit(r)
    return order


def build(bundle, lo=None, hi=None, repo=None, head=None):
    rows = read_inventory(bundle)
    idx = chain_index(repo, head) if repo and head else None
    if lo is not None or hi is not None:
        rows = [r for r in rows if piece_num(r["folder"]) is not None
                and (lo is None or piece_num(r["folder"]) >= lo)
                and (hi is None or piece_num(r["folder"]) <= hi)]
    pieces = []
    for r in rows:
        folder = os.path.join(bundle, r["folder"])
        tests, privacy = parse_proof(proof_texts(folder)) if os.path.isdir(folder) else (None, "folder missing")
        hits, ro = live_check(folder, detail=True)
        cp = cherry_status(repo, idx, r, folder) if os.path.isdir(folder) else None
        subj = (_git(repo, "log", "-1", "--format=%s", r["commit"]) or "").strip() if repo else ""
        desc = describe(piece_num(r["folder"]), subj, folder if os.path.isdir(folder) else None)
        pieces.append(dict(r, tests=tests, privacy=privacy, live=hits, readonly=ro, included=cp, desc=desc))
    inc = {p["folder"] for p in pieces if p["included"]}
    return pieces, [r for r in merge_order(rows) if r["folder"] not in inc]


def render(pieces, order, title="Draft review guide", warning=None):
    in_set = {p["branch"] for p in pieces}
    L = [f"# {title}", "",
         "Read-only guide. Nothing here pushes, merges, or changes the live shop.", ""]
    if warning:
        L += [warning, ""]
    L.append("## Pieces")
    for p in pieces:
        n = piece_num(p["folder"])
        what, why = NOTES.get(n, (None, "(see proof)"))
        what = p.get("desc") or what or "(no description recorded)"
        live = (("Read-only network (GET/HEAD only, no live write)." if p.get("readonly")
                 else "Read-only: no live-write patterns in its patches.")
                if not p["live"] else "CHECK: patches contain " + ", ".join(p["live"]) + ".")
        L += ["", f"### {p['folder']}",
              f"- What it does: {what}",
              f"- Why it helps: {why}",
              f"- Commit {p['commit']} on {p['branch']}; base {p['base']}",
              f"- Tests: {str(p['tests']) + ' passed' if p['tests'] is not None else 'not recorded'}; privacy: {p['privacy']}",
              f"- Live behaviour: {live}"]
        if p.get("included"):
            shas = ", ".join(x[:7] for x in p["included"])
            L.append(f"- Included in the main chain as {shas} (cherry-picked); no separate merge needed.")
    L += ["", "## Suggested merge order", ""]
    for i, r in enumerate(order, 1):
        dep = f"after {r['base']}" if r["base"] in in_set else f"base {r['base']} (outside this set)"
        L.append(f"{i}. {r['folder']} ({dep})")
    inc = [p for p in pieces if p.get("included")]
    if inc:
        L += ["", "Not listed (already included in the main chain, no separate merge): "
              + ", ".join(p["folder"] for p in inc) + "."]
    L += ["", "Merge only with Boss's yes. Rebase each piece onto main after its base merges."]
    return "\n".join(L) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--bundle", default=DEFAULT_BUNDLE)
    ap.add_argument("--out", default=DEFAULT_OUT)
    ap.add_argument("--from", dest="lo", type=int)
    ap.add_argument("--to", dest="hi", type=int)
    ap.add_argument("--repo", help="git repo for cherry-pick detection (read-only)")
    ap.add_argument("--head", help="chain head commit/branch (default: newest bundle piece's commit)")
    a = ap.parse_args(argv)
    warning = None
    if a.repo and not a.head:
        a.head = newest_bundle_commit(a.bundle, a.repo)
        print(f"head: {a.head or 'none found'} (newest bundle piece)")
    elif a.repo and a.head:
        warning = head_check(a.bundle, a.repo, a.head)
        if warning:
            print(warning, file=sys.stderr)
    pieces, order = build(a.bundle, a.lo, a.hi, a.repo, a.head)
    text = render(pieces, order, warning=warning)
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    with open(a.out, "w", encoding="utf-8") as fh:
        fh.write(text)
    flagged = [p["folder"] for p in pieces if p["live"] or p["privacy"] == "FLAGGED"]
    print(f"wrote {a.out}: {len(pieces)} pieces; flagged: {', '.join(flagged) or 'none'}; "
          f"included: {sum(1 for p in pieces if p['included'])}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
