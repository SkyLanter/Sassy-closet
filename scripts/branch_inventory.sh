#!/usr/bin/env bash
# Read-only inventory of local piece-* branches and worktrees vs the combined branch.
#
# Usage: scripts/branch_inventory.sh [--base SHA] [--out PATH] [--since REF]
#   --base   combined commit to compare against (default: HEAD of the highest-numbered
#            local piece-*-combined-check* branch)
#   --out    markdown path (default: out/branch-inventory-<YYYY-MM-DD>.md in the repo)
#   --since  original base for the "ahead" count (default eb8a143 if present)
# Only reads git (no checkout, merge, reset or clean); writes only --out.
set -euo pipefail
case "${1:-}" in -h|--help) sed -n '2,10p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;; esac
PY="${BRANCH_INVENTORY_PYTHON:-python3}"
exec "$PY" - "$@" <<'PY'
import argparse, datetime, os, re, subprocess, sys, tempfile
from pathlib import Path

def git(*a, cwd=None, ok=False):
    r = subprocess.run(["git", *a], cwd=cwd, capture_output=True, text=True)
    if r.returncode and not ok:
        sys.exit(f"git {' '.join(a)} failed: {r.stderr.strip()}")
    out = r.stdout.rstrip("\n")  # keep porcelain leading spaces
    return out if not ok else (r.returncode, out)

ap = argparse.ArgumentParser()
ap.add_argument("--base"); ap.add_argument("--out"); ap.add_argument("--since")
a = ap.parse_args()
root = Path(git("rev-parse", "--show-toplevel"))
branches = [b for b in git("for-each-ref", "--format=%(refname:short)", "refs/heads/piece*").splitlines() if b]

def applies(base, mb, head):
    """Would mb..head apply cleanly on base? Uses a throwaway index file; repo state untouched."""
    with tempfile.TemporaryDirectory() as d:
        env = {**os.environ, "GIT_INDEX_FILE": os.path.join(d, "index")}
        subprocess.run(["git", "read-tree", base], env=env, check=True, capture_output=True)
        diff = subprocess.run(["git", "diff", "--binary", mb, head], capture_output=True).stdout
        return subprocess.run(["git", "apply", "--cached", "--check"], input=diff, env=env,
                              capture_output=True).returncode == 0

def num(b):
    m = re.match(r"piece-(\d+)", b)
    return int(m.group(1)) if m else -1

if a.base:
    base = git("rev-parse", a.base)
    base_name = a.base
else:
    combined = sorted((b for b in branches if "combined-check" in b), key=lambda b: (num(b), b))
    if not combined:
        sys.exit("no piece-*-combined-check branch; pass --base")
    base_name = combined[-1]
    base = git("rev-parse", base_name)
since = a.since
if since is None:
    since = "eb8a143" if git("rev-parse", "-q", "--verify", "eb8a143^{commit}", ok=True)[0] == 0 else None
today = datetime.date.today().isoformat()
out = Path(a.out) if a.out else root / "out" / f"branch-inventory-{today}.md"

rows, details = [], []
merged = unmerged = missing_n = 0
for b in sorted(branches, key=lambda b: (num(b), b)):
    head = git("rev-parse", b)
    mb = git("merge-base", base, head, ok=True)[1]
    ahead = git("rev-list", "--count", f"{since}..{head}") if since else "-"
    is_anc = git("merge-base", "--is-ancestor", head, base, ok=True)[0] == 0
    stat = git("diff", "--shortstat", f"{mb}..{head}") if mb else ""
    files = [f for f in git("diff", "--name-only", f"{mb}..{head}").splitlines() if f] if mb else []
    subjects = git("log", "--format=%s", "--no-merges", f"{mb}..{head}" if mb else head).splitlines()
    summary = (subjects[0] if subjects else git("log", "-1", "--format=%s", head)).replace("|", "/")[:90]
    uniq = git("rev-list", "--count", f"{base}..{head}")
    if is_anc:
        merged += 1
        state = "MERGED"
    else:
        unmerged += 1
        cherry = [l for l in git("cherry", base, head).splitlines() if l]
        plus = [l[2:] for l in cherry if l.startswith("+")]
        minus = [l[2:] for l in cherry if l.startswith("-")]
        # A "+" commit whose touched files already match the branch tip in base counts as present.
        still = []
        for c in plus:
            touched = [f for f in git("diff-tree", "--no-commit-id", "--name-only", "-r", c).splitlines() if f]
            same = all(git("rev-parse", f"{head}:{f}", ok=True)[1] == git("rev-parse", f"{base}:{f}", ok=True)[1]
                       for f in touched)
            if not same:
                still.append(c)
        if not cherry or not still:
            verdict = "already in combined (equivalent patch)"
        elif len(still) == len(cherry):
            verdict = "MISSING - needs merge"
        else:
            verdict = "partially present"
        if "MISSING" in verdict or "partially" in verdict:
            missing_n += 1
        state = f"UNMERGED: {verdict}"
        lines = [f"### {b} ({head[:7]}) - {verdict}", f"- full sha {head}; merge-base {mb[:7] if mb else 'none'}; {stat or 'no diff'}"]
        for c in cherry:
            sha = c[2:]
            mark = "missing" if sha in still else "present"
            lines.append(f"- {mark}: {sha[:7]} {git('log', '-1', '--format=%s', sha)}")
        absent = [f for f in files if git("cat-file", "-e", f"{base}:{f}", ok=True)[0] != 0
                  and git("cat-file", "-e", f"{head}:{f}", ok=True)[0] == 0]
        if still:
            lines.append(f"- files absent from combined: {len(absent)} of {len(files)}; "
                         f"applies cleanly on combined: {'yes' if applies(base, mb, head) else 'no (conflicts)'}")
        lines.append("- files: " + (", ".join(files) if files else "none"))
        details.append((num(b), b, verdict, "\n".join(lines), head))
    rows.append(f"| {b} | {head[:7]} | {state} | {uniq} | {len(files)} | {summary} |")

wts, dirty = [], 0
cur = {}
for line in git("worktree", "list", "--porcelain").splitlines() + [""]:
    if not line:
        if cur:
            p = cur.get("worktree"); br = cur.get("branch", "(detached)").replace("refs/heads/", "")
            rc, st = git("-C", p, "status", "--porcelain", ok=True) if Path(p).exists() else (1, "")
            ents = [e for e in st.splitlines() if e]
            real = [e for e in ents if not re.search(r"node_modules/?$", e)]
            if not Path(p).exists():
                state = "missing on disk"
            elif real:
                kind = "deleted out/ files only" if all(e.startswith(" D out/") for e in real) else "changes"
                state = f"DIRTY ({len(real)} {kind})"; dirty += 1
            elif ents:
                state = "clean (node_modules link only)"
            else:
                state = "clean"
            wts.append(f"| {p} | {br} | {cur.get('HEAD', '')[:7]} | {state} |")
        cur = {}
        continue
    k, _, v = line.partition(" ")
    cur[k] = v

md = [f"# Branch inventory {today}", "",
      f"Base (combined): {base_name} @ {base[:7]} ({base}). Ahead counts vs {since or 'n/a'}. Read-only; generated by scripts/branch_inventory.sh.", "",
      f"Summary: branches {len(branches)}, merged {merged}, unmerged {unmerged}, missing changes {missing_n}, dirty worktrees {dirty}", "",
      "| branch | sha | merged? | unique commits | files changed | summary |", "|---|---|---|---|---|---|", *rows, "",
      "## Unmerged / missing", ""]
md += [d[3] + "\n" for d in details] or ["none", ""]
md += ["## Worktrees", "", "| path | branch | HEAD | status |", "|---|---|---|---|", *wts, ""]
open_ = [d for d in sorted(details) if "MISSING" in d[2] or "partially" in d[2]]
cover = {}
for d in open_:
    for c in open_:
        if c is not d and "combined" in c[1] and git("merge-base", "--is-ancestor", d[4], c[4], ok=True)[0] == 0:
            cover[d[1]] = c[1]
            break
need = [d[1] for d in open_ if d[1] not in cover]
if cover:
    md += ["Covered by an unmerged combined branch (merge that instead): "
           + "; ".join(f"{k} -> {v}" for k, v in cover.items()), ""]
md += ["## Suggested next step", "",
       ("Suggested next step: merge into the combined branch, in order: " + ", ".join(need)) if need
       else "Suggested next step: nothing missing; every piece change is already in the combined branch.", ""]
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text("\n".join(md), encoding="utf-8")
print(f"wrote {out}")
print(md[4])
PY
