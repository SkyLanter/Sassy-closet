#!/usr/bin/env python3
"""Piece 89/90: compile Boss's open decisions into one file (READ-ONLY inputs).

Reads only local reports/inputs under <root> (default /workspace/sassy-closet):
  verify/cost-recheck/summary.<date>.json   newly gone on Taobao (hold?), unreachable streaks
  out/reports/<date>/COST-BASIS.md          FLIP rows: only mã + OK/UNDER verdict words
  boss_decisions_digest.py output           held-in-order, price approvals, public held
                                            photos, hold calls, intake mismatches
  out/muse/meta-qc-<date>.json / snapshot   Meta QC status (via daily_summary_draft)
  out/meta-popular/cycle-<date>/SUMMARY.txt open Boss-gated PR numbers
  out/reports/<date>/HELD-PHOTOS.md         piece 95: evidence for public held photos

Writes out/reports/<date>/BOSS-DECISIONS.md (gitignored, never in the repo):
one line per decision: mã | question | evidence path | days open.
Days open = <date> minus the earliest dated source showing it; '?' when a
source carries no date. Free text is never copied: only mã codes, category
questions written here, relative paths, dates and PR numbers. No network,
no sends, no live writes.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import daily_summary_draft as ds  # noqa: E402

ROOT = Path("/workspace/sassy-closet")
MA = re.compile(r"^[A-Z]\d{2}$")
DIG = re.compile(r"^- \[(\w+)\] ([A-Z]\d{2})\s+first_seen=(\d{4}-\d{2}-\d{2}|\?)\s+source=(\S+)")
DATE_IN = re.compile(r"(\d{4}-\d{2}-\d{2})")
PR_LINE = re.compile(r"PR #(\d+)\b(.*)", re.I)
PR_OPEN = re.compile(r"\b(open|unmerged|boss-gated)\b", re.I)
BANNED = ds.BANNED

QUESTIONS = {
    "gone_hold": "Hold it? Newly gone on Taobao and still live.",
    "flip_under": "Under the price formula at Nhung's intake cost (OK at baseline cost). Flag/decide price?",
    "price_approval": "Needs a price (held). Approve one?",
    "popular_order_held": "Held mã in popular order. Remove it?",
    "blob_photo_delete": "Held item photo is public on Blob. Delete it?",
    "hold_call": "Hold call needed.",
    "intake_unreachable": "Intake mismatch; Taobao listing unreachable. Hold call?",
    "intake_mismatch": "Intake cost doesn't match the public Taobao price. Check intake?",
    "meta": "Meta QC not PASS on both sides. Sign-in/recheck needed?",
    "pr": "Boss-gated PR still open. Merge or close?",
}
ORDER = list(QUESTIONS)

# Piece 90: name a recorded sign-in blocker (person + platform) instead of the
# generic Meta line. Only fixed words are emitted (person, platform, path, days).
SIGNIN_GLOBS = ("out/muse/*.md", "out/muse/*.txt", "out/muse/meta-qc-*.json",
                "out/luxubu*/**/*", "out/luxubu*", "out/midnight-qc/*/summary.md",
                "out/midnight-qc/*/summary.json")
PERSON = re.compile(r"\b(Luxubu|Mini Boss)\b")
PLATFORM = re.compile(r"\b(Facebook|FB|Instagram|IG)\b")
PLAT_NAME = {"facebook": "Facebook", "fb": "Facebook", "instagram": "Instagram", "ig": "Instagram"}
BLOCKER = re.compile(
    r"(sign[- ]?in|log[- ]?in)\s*(is\s+)?(needed|required|blocked|wall|expired|failed|gate[d]?)"
    r"|(can'?t|cannot|could not|couldn'?t|unable to)\s+(sign|log)\s*[- ]?in"
    r"|(signed|logged)\s+out|needs?\s+(to\s+)?(sign|log)\s*[- ]?in"
    r"|(sign|log)[- ]?in\s+blocker", re.I)
NOT_BLOCKER = re.compile(r"\bsigned in as\b", re.I)


def find_signin_blockers(root, date):
    """-> {(person, platform): (since_date_or_None, evidence_relpath)} from local sources.

    A line counts only when it names a person, a platform and a sign-in blocker
    phrase itself ('signed in as the Page' instructions are ignored). Sources
    dated after <date> are skipped; earliest dated source wins for days open."""
    root = Path(root)
    found = {}
    seen = set()
    for g in SIGNIN_GLOBS:
        for f in sorted(root.glob(g)):
            if f in seen or not f.is_file() or ".bak" in f.name:
                continue
            seen.add(f)
            m = DATE_IN.search(str(f.relative_to(root)))
            fdate = m.group(1) if m else None
            if fdate and fdate > date:
                continue
            try:
                text = f.read_text(encoding="utf-8")
            except (UnicodeDecodeError, OSError):
                continue
            for line in text.splitlines():
                if not BLOCKER.search(line) or NOT_BLOCKER.search(line) and not BLOCKER.search(NOT_BLOCKER.sub("", line)):
                    continue
                pm, fm = PERSON.search(line), PLATFORM.search(line)
                if not (pm and fm):
                    continue
                key = (pm.group(1), PLAT_NAME[fm.group(1).lower()])
                prev = found.get(key)
                if prev is None or (fdate and (prev[0] is None or fdate < prev[0])):
                    found[key] = (fdate, str(f.relative_to(root)))
    return found


def days(date, since):
    try:
        return (dt.date.fromisoformat(date) - dt.date.fromisoformat(since)).days
    except (TypeError, ValueError):
        return None


def rel(root, p):
    try:
        return str(Path(p).resolve().relative_to(Path(root).resolve()))
    except ValueError:
        return str(p)


def parse_digest(text):
    """-> list of (cat, mã, first_seen, source) from boss_decisions_digest output."""
    out = []
    for line in (text or "").splitlines():
        m = DIG.match(line.strip())
        if m:
            out.append((m.group(1), m.group(2), None if m.group(3) == "?" else m.group(3), m.group(4)))
    return out


def streak_start(root, date, ma):
    """Earliest date of the unbroken run of cost summaries (up to <date>) listing mã unreachable."""
    files = sorted((Path(root) / "verify/cost-recheck").glob("summary.????-??-??.json"))
    start = None
    for f in reversed(files):
        d = DATE_IN.search(f.name).group(1)
        if d > date:
            continue
        doc = ds.load_json(f) or {}
        if ma in (doc.get("unreachable_mas") or []):
            start = d
        else:
            break
    return start


def first_cost_basis(root, date, ma):
    best = None
    root = Path(root)
    files = list((root / "out/reports").glob("????-??-??/COST-BASIS.md"))
    files += list((root / "out/archive").glob("????-??-??/COST-BASIS.md"))  # piece 92
    for f in files:
        d = f.parent.name
        if d <= date and ma in ds.parse_cost_basis(f.read_text(encoding="utf-8")):
            best = d if best is None or d < best else best
    return best


# Piece 92: dated copies kept by archive_daily_inputs.py give each decision a
# first-seen date: earliest out/archive/<d>/BOSS-DECISIONS.md (d <= date) listing
# the same mã + question. Only days BEFORE <date> count: today's archive is a
# copy of today's own output and adds no history.
ARCH_LINE = re.compile(r"^- (.+?) \| (.+?) \| ")


def archive_first_seen(root, date):
    """-> {(mã, question): earliest archive date}"""
    seen = {}
    for f in sorted((Path(root) / "out/archive").glob("????-??-??/BOSS-DECISIONS.md")):
        d = f.parent.name
        if d >= date:
            continue
        for line in f.read_text(encoding="utf-8").splitlines():
            m = ARCH_LINE.match(line)
            if m:
                seen.setdefault((m.group(1), m.group(2)), d)
    return seen


def apply_archive(D, root, date):
    seen = archive_first_seen(root, date)
    for d in D:
        a = seen.get((d["ma"], d["q"]))
        if a and (d["since"] is None or a < d["since"]):
            d["since"], d["days"] = a, days(date, a)
    return D


# Piece 107: first-raised date per decision key (mã, question) = earliest
# out/reports/<d>/BOSS-DECISIONS.md or out/archive/<d>/BOSS-DECISIONS.md
# (d <= date) listing that key. None found, or only today -> 'new today'.
def first_raised_map(root, date):
    """-> {(mã, question): earliest dated report/archive date <= date}. Read-only."""
    seen = {}
    root = Path(root)
    files = list(root.glob("out/reports/????-??-??/BOSS-DECISIONS.md"))
    files += list(root.glob("out/archive/????-??-??/BOSS-DECISIONS.md"))
    for f in files:
        d = f.parent.name
        if d > date:
            continue
        try:
            text = f.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        for line in text.splitlines():
            m = ARCH_LINE.match(line)
            if m:
                k = (m.group(1), m.group(2))
                if k not in seen or d < seen[k]:
                    seen[k] = d
    return seen


def apply_first_raised(D, root, date):
    fr = first_raised_map(root, date)
    for d in D:
        f = fr.get((d["ma"], d["q"]))
        if f is None or f >= date:
            d["raised"], d["open"] = None, 0
        else:
            d["raised"], d["open"] = f, days(date, f)
    return D


def raised_text(d):
    if d.get("raised") is None:
        return "new today"
    return f"first raised {d['raised']} ({d['open']}d open)"


def open_prs(text):
    """PR numbers on lines saying open/unmerged/Boss-gated, with first date on that line."""
    out = {}
    for line in (text or "").splitlines():
        for m in PR_LINE.finditer(line):
            if PR_OPEN.search(line):
                dm = DATE_IN.search(m.group(2))
                out.setdefault(m.group(1), dm.group(1) if dm else None)
    return out


def apply_held_photos(D, root, date, add):
    """Piece 95: when out/reports/<date>/HELD-PHOTOS.md exists it is the evidence
    for blob_photo_delete (replaces muse-notes evidence); exposed mãs missing a
    line get one. Only mã codes and the relative path are used (no URLs)."""
    import held_photo_exposure as hpe
    rp = Path(root) / "out/reports" / date / hpe.REPORT
    exp = hpe.exposed_from_report(rp)
    if exp is None:
        return
    ev = rel(root, rp)
    have = set()
    for d in D:
        if d["cat"] == "blob_photo_delete":
            d["ev"] = ev
            have.add(d["ma"])
    for m in exp:
        if m not in have:
            add("blob_photo_delete", m, ev, date)


def compile_decisions(root, date, digest_text, cost=None, cost_path=None, cb_path=None,
                      meta_status=None, meta_src=None, pr_path=None, order_path=None):
    root = Path(root)
    D = []

    def add(cat, ma, ev, since, q=None):
        D.append({"cat": cat, "ma": ma, "q": q or QUESTIONS[cat], "ev": ev,
                  "since": since, "days": days(date, since) if since else None})

    gone = ds.mas((cost or {}).get("persistent_new_unreachable"))
    for m in gone:
        add("gone_hold", m, rel(root, cost_path), streak_start(root, date, m))
    flips = {}
    if cb_path and Path(cb_path).exists():
        flips = ds.parse_cost_basis(Path(cb_path).read_text(encoding="utf-8"))
    flip_under = sorted(m for m, (iv, _b) in flips.items() if iv == "UNDER")
    for m in flip_under:
        add("flip_under", m, rel(root, cb_path), first_cost_basis(root, date, m))
    unreach = set(ds.mas((cost or {}).get("unreachable_mas")))
    skip_mismatch = set(gone) | set(flip_under)
    for cat, m, seen, src in parse_digest(digest_text):
        if cat == "intake_mismatch":
            if m in skip_mismatch:
                continue
            cat = "intake_unreachable" if m in unreach else "intake_mismatch"
        if cat not in QUESTIONS:
            continue
        add(cat, m, src, seen)
    for m in ds.parse_held_order(digest_text):
        add("popular_order_held", m, neutral_path(root, order_path) if order_path
            else "sassy-closet-shop/data/popular-order.json", None)
    if meta_status is not None:
        bad = [k.upper() for k in ("ig", "fb") if (meta_status.get(k) or ("unchecked",))[0] != "pass"]
        blockers = find_signin_blockers(root, date) if bad else {}
        for (person, plat), (since, ev) in sorted(blockers.items()):
            add("meta", "-", ev, since, q=f"{person} {plat} sign-in needed. Sign in so Meta QC can finish?")
        if bad and not blockers:
            st = ", ".join(f"{k.upper()} {meta_status[k][0].upper()}" for k in ("ig", "fb"))
            add("meta", "-", meta_src or f"out/muse/meta-qc-{date}.json (missing)", None,
                q=f"Meta QC not PASS on both sides ({st}). Sign-in/recheck needed?")
    if pr_path and Path(pr_path).exists():
        for n, since in open_prs(Path(pr_path).read_text(encoding="utf-8")).items():
            add("pr", f"PR #{n}", rel(root, pr_path), since)
    apply_held_photos(D, root, date, add)
    apply_archive(D, root, date)
    apply_first_raised(D, root, date)
    # piece 107: oldest first-raised first; 'new today' last; ties by category, mã
    D.sort(key=lambda d: (d["raised"] is None, d["raised"] or "", ORDER.index(d["cat"]), d["ma"]))
    return D


INPUTS_LINE = re.compile(r"^Inputs: (.*) \| total=(\d+)$", re.M)


def repo_top(p):
    """Nearest enclosing git worktree/repo dir (has .git file or dir), else None."""
    for d in Path(p).resolve().parents:
        if (d / ".git").exists():
            return d
    return None


def sha12(p):
    import hashlib
    try:
        return hashlib.sha256(Path(p).read_bytes()).hexdigest()[:12]
    except OSError:
        return "missing"


def neutral_path(root, v):
    """Piece 94: worktree-neutral path. Under <root> -> root-relative (out/ inputs);
    inside a git worktree -> repo-relative; else the plain path."""
    if v is None:
        return "-"
    rp = Path(v).resolve()
    try:
        return str(rp.relative_to(Path(root).resolve()))
    except ValueError:
        pass
    top = repo_top(rp)
    return str(rp.relative_to(top)) if top else str(v)


def inputs_desc(a):
    """Piece 93/94: stable, worktree-neutral description of the inputs.
    Repo inputs: repo-relative path + content sha256[:12]; <root> inputs: root-relative."""
    def p(v):
        if v is None:
            return "-"
        n = neutral_path(a.root, v)
        return n if Path(v).resolve().is_relative_to(Path(a.root).resolve()) else f"{n}@{sha12(v)}"
    return f"date={a.date} root={a.root.name} order={p(a.order)} held={p(a.held)} digest={p(a.digest)}"


def existing_inputs(path):
    """-> inputs string recorded in an existing file, '' for pre-93 files, None if absent."""
    path = Path(path)
    if not path.exists():
        return None
    m = INPUTS_LINE.search(path.read_text(encoding="utf-8"))
    if not m or "=/" in m.group(1):  # piece 94: old absolute-path header == unrecorded
        return ""
    return m.group(1)


def render(D, date, inputs=None):
    L = [f"# Boss decisions {date} (DRAFT, local only, not sent)", ""]
    if inputs is not None:
        L += [f"Inputs: {inputs} | total={len(D)}", ""]
    L += [
         "One line per open decision: mã | question | evidence | days open "
         "('?' = no dated source) | first raised (earliest daily report/archive "
         "listing it; 'new today' if none). Oldest first.", ""]
    for d in D:
        n = "?" if d["days"] is None else f"{d['days']}d (since {d['since']})"
        r = raised_text(d) if "raised" in d else None
        L.append(f"- {d['ma']} | {d['q']} | {d['ev']} | {n}" + (f" | {r}" if r else ""))
    L += ["", f"TOTAL {len(D)}", "Read-only: nothing was sent, posted, priced or deleted.", ""]
    text = "\n".join(L)
    if BANNED.search(text):
        raise SystemExit("refusing to write: banned content (¥, link or email) in output")
    return text


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--date", default=ds.today_pt())
    ap.add_argument("--root", type=Path, default=ROOT)
    ap.add_argument("--digest", type=Path, help="saved boss_decisions_digest.py output")
    ap.add_argument("--order", type=Path)
    ap.add_argument("--held", type=Path)
    ap.add_argument("--out-dir", type=Path, help="default <root>/out/reports/<date>")
    ap.add_argument("--stdout", action="store_true")
    ap.add_argument("--no-defaults", action="store_true",
                    help="do not resolve --order/--held from the repo (piece 93)")
    ap.add_argument("--force", action="store_true",
                    help="overwrite a file for this date made with different inputs")
    a = ap.parse_args(argv)
    if not a.no_defaults:  # piece 93: same defaults as daily_summary_draft --defaults
        for k, v in ds.default_paths().items():
            if getattr(a, k) is None:
                setattr(a, k, v)
    r, d = a.root, a.date
    if a.digest:
        dtext = a.digest.read_text(encoding="utf-8")
    else:
        dargs = ["--root", str(r)]
        if a.order:
            dargs += ["--order", str(a.order)]
        if a.held:
            dargs += ["--held", str(a.held)]
        dtext = ds.run_local("boss_decisions_digest.py", dargs)
    cp = r / "verify/cost-recheck" / f"summary.{d}.json"
    ms, msrc = ds.read_meta_status(r, d)
    D = compile_decisions(r, d, dtext, ds.load_json(cp), cp,
                          r / "out/reports" / d / "COST-BASIS.md", ms, msrc,
                          r / "out/meta-popular" / f"cycle-{d}" / "SUMMARY.txt", a.order)
    inputs = inputs_desc(a)
    text = render(D, d, inputs)
    out_dir = a.out_dir or r / "out/reports" / d
    out = out_dir / "BOSS-DECISIONS.md"
    prev = existing_inputs(out)
    if prev is not None and prev != inputs and not a.force:
        print(f"refusing to overwrite {out}: made with different inputs "
              f"({prev or 'unrecorded or old absolute-path header'}); pass --force", file=sys.stderr)
        return 2
    out_dir.mkdir(parents=True, exist_ok=True)
    out.write_text(text, encoding="utf-8")
    print(text if a.stdout else f"wrote {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
