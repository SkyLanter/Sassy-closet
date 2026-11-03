#!/usr/bin/env python3
"""Piece 57: draft the 3:30 PM PT daily shop summary to Boss (read-only, sends nothing).

Inputs (all local files; nothing is fetched or sent):
  --qc            latest out/midnight-qc/<date>/summary.json
  --cost          verify/cost-recheck/summary.<date>.json
  --digest        saved boss_decisions_digest.py text output (else it is run locally)
  --gaps          saved meta_caption_gap_report.py --json output (else it is run locally)
  --proposal      out/proposals/held-price-proposal-<date>.json (verdicts only)
  --cost-basis    out/reports/<date>/COST-BASIS.md from cost_basis_reconcile.py (piece 77:
                  only mã + OK/UNDER verdict words are read; cost cells are never parsed)
  --order/--held  passed to boss_decisions_digest so popular_order_held shows (piece 77)
Piece 78: Meta status is read automatically from out/muse/meta-qc-<date>.json
({"ig": {"status": "pass|fail|unchecked", "reason": "..."}, "fb": {...}})
or a "qc" block in the latest out/meta-snapshot/meta-snapshot-*.json saved
that day. No record -> UNCHECKED. PASS is never shown without a record.
Piece 79: each side may hold "luxubu" and "miniboss" sub-entries (status, reason,
proof). PASS only when both pass; pass+fail -> DISAGREE (flag Boss); else
UNCHECKED naming who is missing. Old flat entries are single-source, never PASS.
Piece 80: the --meta-ig/--meta-fb CLI overrides are removed (nothing used them).
build()'s meta_ig/meta_fb args are single-source: they may set FAIL or UNCHECKED,
but a pass shows as UNCHECKED ('override pass needs Luxubu + Mini Boss record').

Piece 91: a 'Boss decisions (N open)' section reads out/reports/<date>/BOSS-DECISIONS.md
(boss_decisions.py). Items already listed under 'Waiting on you' are dropped (dedupe
by mã + question kind; exact repeats by mã + question). At most 12 shown, most days
open first, then the path to the full file. Missing file -> 'MISSING'.
Piece 98: a 'Luxubu' line reads out/muse/luxubu-status-<date>.json (last reply,
last activity, last check; 'no status record' when absent). Factual only.
Piece 85: git-tracked inputs show last commit time, others file time.
Piece 84: a 'Data freshness' section lists each input's file mtime in
America/Los_Angeles time (PT label) and marks it OK, STALE (> 24 h old) or
MISSING (file not there). Only the input label, file name and time are shown.

Writes out/summaries/daily-summary-<date>.md (gitignored). Only mã codes,
counts, statuses and sell $ are used: free-text fields from the inputs are
never copied, so no ¥ cost, links or customer data can leak. The word CLEAR is
only printed when both Meta checks pass.
"""
from __future__ import annotations

import argparse
import os
import datetime as dt
import json
import re
import subprocess
import sys
from pathlib import Path
from zoneinfo import ZoneInfo

HERE = Path(__file__).resolve().parent
ROOT = Path("/workspace/sassy-closet")
MA = re.compile(r"^[A-Z]\d{2}$")
SELL = re.compile(r"^\$\d+(\.\d{1,2})?$")
DIGEST_LINE = re.compile(r"^- \[(\w+)\] ([A-Z]\d{2})\b")
META_OK = {"pass", "fail", "unchecked"}
BANNED = re.compile(r"[¥]|https?://|www\.|tesla|@[\w.-]+\.\w+", re.I)


WHO = ("luxubu", "miniboss")
WHO_NAME = {"luxubu": "Luxubu", "miniboss": "Mini Boss"}


def _one(v):
    if isinstance(v, str):
        v = {"status": v}
    if not isinstance(v, dict):
        return None
    st = str(v.get("status", "")).strip().lower()
    if st not in META_OK:
        return None
    reason = re.sub(r"\s+", " ", str(v.get("reason") or "")).strip()[:60]
    return st, reason


def _side(v):
    """Piece 79: PASS only when Luxubu and Mini Boss both pass.

    Dual format: {"luxubu": {status, reason, proof}, "miniboss": {...}}.
    Old flat format is single-source: it can be FAIL/UNCHECKED, never PASS.
    """
    if isinstance(v, dict) and any(w in v for w in WHO):
        got = {w: _one(v.get(w)) for w in WHO}
        sts = {w: (g[0] if g else None) for w, g in got.items()}
        if all(s == "pass" for s in sts.values()):
            return "pass", "Luxubu + Mini Boss agree"
        if "pass" in sts.values() and "fail" in sts.values():
            f = next(w for w in WHO if sts[w] == "fail")
            why = got[f][1]
            return "disagree", (f"flag Boss: {WHO_NAME[f]} fail" + (f" - {why}" if why else ""))[:60]
        if "fail" in sts.values():
            w = next(w for w in WHO if sts[w] == "fail")
            return "fail", (got[w][1] or f"{WHO_NAME[w]} fail")
        missing = [WHO_NAME[w] for w in WHO if sts[w] != "pass"]
        return "unchecked", "missing " + " + ".join(missing)
    one = _one(v)
    if one is None:
        return None
    st, why = one
    if st == "pass":
        return "unchecked", "single-source pass; needs Luxubu + Mini Boss"
    return st, why


def read_meta_status(root, date):
    """Return ({"ig": (status, reason), "fb": ...}, source_label)."""
    cands = [(Path(root) / "out/muse" / f"meta-qc-{date}.json", "Muse QC record")]
    snaps = sorted((Path(root) / "out/meta-snapshot").glob(
        f"meta-snapshot-{date.replace('-', '')}T*.json"))
    if snaps:
        cands.append((snaps[-1], "Meta snapshot"))
    for path, label in cands:
        doc = load_json(path)
        if not isinstance(doc, dict):
            continue
        blk = doc.get("qc", doc) if label == "Meta snapshot" else doc
        if not isinstance(blk, dict):
            continue
        res = {k: _side(blk.get(k)) for k in ("ig", "fb")}
        if any(res.values()):
            for k in res:
                res[k] = res[k] or ("unchecked", "not in record")
            return res, f"{label} {path.name}"
    why = f"no Meta QC record for {date}"
    return {"ig": ("unchecked", why), "fb": ("unchecked", why)}, None


def meta_lines(status, source):
    def f(name, k):
        st, why = status[k]
        return f"- {name}: {st.upper()}" + (f" ({why})" if why else "")
    ok = all(status[k][0] == "pass" for k in ("ig", "fb"))
    bad = [n for n, k in (("Instagram", "ig"), ("Facebook", "fb")) if status[k][0] == "disagree"]
    tail = [f"FLAG BOSS: Luxubu and Mini Boss disagree on {', '.join(bad)}."] if bad else []
    return [f"Meta status ({'from ' + source if source else 'no record found'}):",
            f("Instagram", "ig"), f("Facebook", "fb"),
            "Meta verdict: CLEAR" if ok else "Meta verdict: NOT CLEAR (both sides must PASS)"] + tail


def mas(xs):
    return sorted({x for x in (xs or []) if isinstance(x, str) and MA.match(x)})


def load_json(p):
    if not p or not Path(p).exists():
        return None
    return json.loads(Path(p).read_text(encoding="utf-8"))


def warn_codes(warns):
    out = []
    for w in warns or []:
        tok = str(w).split()[0] if str(w).split() else ""
        if re.fullmatch(r"[A-Z0-9_]+", tok):
            out.append(tok)
    return out


UNDER_WARN = re.compile(r"under[- ]?pric|INTAKE_COST_VS_LIVE|vs live \$", re.I)
MA_TOKEN = re.compile(r"\b([A-Z]\d{2})\b")


def under_price_mas(warns):
    """Midnight QC WARN lines about under-price at intake cost -> mã codes only."""
    out = set()
    for w in warns or []:
        w = str(w)
        if UNDER_WARN.search(w):
            out.update(MA_TOKEN.findall(w))
    return sorted(out)


def gap_items(gaps, key):
    """Accept dict items or [platform, media, id] lists; return 'PLAT media id' labels."""
    res = []
    for g in (gaps or {}).get(key) or []:
        if isinstance(g, dict):
            plat, media, pid = g.get("platform", "?"), g.get("media", "post"), g.get("id", "?")
        elif isinstance(g, (list, tuple)) and len(g) == 3:
            plat, media, pid = g
        else:
            continue
        pid = str(pid)
        if pid.startswith("ma:"):
            pid = pid[3:]
        if not (pid.isdigit() or MA.match(pid)):
            continue
        res.append(f"{str(plat).upper()} {str(media).lower()} {pid}")
    return res


def parse_digest(text):
    cats = {}
    for line in (text or "").splitlines():
        m = DIGEST_LINE.match(line.strip())
        if m:
            cats.setdefault(m.group(1), set()).add(m.group(2))
    return {k: sorted(v) for k, v in cats.items()}


HELD_ORDER_LINE = re.compile(r"^- \[popular_order_held\] (.*)$")
VERDICT = re.compile(r"/\s*(OK|UNDER)\s*$")


def parse_held_order(text):
    """Piece 77: mã codes from the digest's popular_order_held item (codes only)."""
    out = set()
    for line in (text or "").splitlines():
        m = HELD_ORDER_LINE.match(line.strip())
        if m:
            out.update(x for x in MA_TOKEN.findall(m.group(1)) if MA.match(x))
    return sorted(out)


def parse_cost_basis(text):
    """Piece 77: FLIP rows from COST-BASIS.md -> {mã: (intake_verdict, baseline_verdict)}.
    Reads only the mã cell, the verdict word of the intake/baseline target cells and the
    result cell. Costs are never kept."""
    out = {}
    for line in (text or "").splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 5 or not MA.match(cells[0]) or cells[-1] != "FLIP":
            continue
        iv, bv = (VERDICT.search(c) for c in (cells[-4], cells[-3]))
        out[cells[0]] = (iv.group(1) if iv else "?", bv.group(1) if bv else "?")
    return out


def run_local(script, args):
    try:
        r = subprocess.run([sys.executable, str(HERE / script), *args],
                           capture_output=True, text=True, timeout=120)
        return r.stdout
    except Exception:
        return ""


PT = ZoneInfo("America/Los_Angeles")
STALE_AFTER = dt.timedelta(hours=24)


def freshness_inputs(root, date, catalog=None, intake=None, meta_qc=None, cost_basis=None,
                     order=None):
    """Piece 84: (label, path) per input. First existing candidate wins."""
    r = Path(root)

    def pick(*cands):
        cands = [Path(c) for c in cands if c]
        return next((c for c in cands if c.exists()), cands[0])
    return [
        ("Blob catalog snapshot", pick(catalog, r / "verify" / f"too-cheap-{date}" / "catalog.v1.live.json",
                                       r / "verify/cost-recheck/catalog.v1.live.json")),
        ("Intake", pick(intake, r / "auto-list/state/intake-status.v1.json")),
        ("Meta QC json", pick(meta_qc, r / "out/muse" / f"meta-qc-{date}.json")),
        ("Cost-basis report", pick(cost_basis, r / "out/reports" / date / "COST-BASIS.md")),
        ("Popular order", pick(order, r / "sassy-closet-shop/data/popular-order.json")),
    ]


def git_commit_time(path):
    """Piece 85: last commit time of a git-tracked file, else None (untracked/no git)."""
    path = Path(path).resolve()
    try:
        r = subprocess.run(["git", "log", "-1", "--format=%cI", "--", path.name],
                           cwd=path.parent, capture_output=True, text=True, timeout=30)
    except Exception:
        return None
    out = r.stdout.strip()
    if r.returncode != 0 or not out:
        return None
    try:
        return dt.datetime.fromisoformat(out)
    except ValueError:
        return None


def freshness_lines(inputs, now=None):
    """Piece 84/85: one line per input; git-tracked files use last commit time,
    untracked files use file mtime. Never reads file contents."""
    now = now or dt.datetime.now(dt.timezone.utc)
    L = ["Data freshness (times in PT; 'last commit' for git-tracked files, "
         "'file time' otherwise; STALE = older than 24 h):"]
    for label, path in inputs:
        path = Path(path)
        if not path.exists():
            L.append(f"- {label}: MISSING ({path.name})")
            continue
        m = git_commit_time(path)
        kind = "last commit"
        if m is None:
            m = dt.datetime.fromtimestamp(path.stat().st_mtime, dt.timezone.utc)
            kind = "file time"
        st = "STALE" if now - m > STALE_AFTER else "OK"
        L.append(f"- {label}: {st}, {path.name} {kind} {m.astimezone(PT):%Y-%m-%d %H:%M} PT")
    return L


OVERRIDE_PASS_REASON = "override pass needs Luxubu + Mini Boss record"


def single_source_override(value):
    """Piece 80: one person's word can set FAIL/UNCHECKED, never PASS."""
    v = (value or "unchecked").lower()
    if v == "pass":
        return ("unchecked", OVERRIDE_PASS_REASON)
    if v == "fail":
        return ("fail", "single-source override")
    return ("unchecked", "")


DEC_LINE = re.compile(r"^- (\S+(?: #\d+)?) \| (.+?) \| (.+?) \| (\d+d|\?)(?: \(since (\d{4}-\d{2}-\d{2})\))?"
                      r"(?: \| (new today|first raised (\d{4}-\d{2}-\d{2}) \((\d+)d open\)))?$")
DEC_KINDS = [("Newly gone on Taobao", "gone"), ("Under the price formula", "flip_under"),
             ("Needs a price", "price_approval"), ("public on Blob", "blob_photo_delete"),
             ("Hold call needed", "hold_call"), ("listing unreachable", "mismatch_gone"),
             ("doesn't match the public", "mismatch_public"), ("Under-priced", "mismatch_under"),
             ("Meta QC not PASS", "meta"), ("Held mã in popular order", "popular_order_held")]
# Piece 99: every per-mã decision kind that has a grouped 'Waiting on you' line.
# 'pr' has no grouped Waiting line, so PR decisions always stay in Boss decisions.
GROUPED_KINDS = {k for _, k in DEC_KINDS}
DEC_MAX = 12


def dec_kind(question):
    for key, kind in DEC_KINDS:
        if key in question:
            return kind
    return None


def parse_boss_decisions(text):
    """[(mã, question, evidence, days)] from BOSS-DECISIONS.md; days None for '?'."""
    return [r[:4] for r in parse_boss_decisions_aged(text)]


def parse_boss_decisions_aged(text):
    """Piece 107: [(mã, q, ev, days, raised, open_days, aged, since)]; aged False for
    pre-107 lines. Piece 109: since = the source's own date (None if absent)."""
    out = []
    for line in text.splitlines():
        m = DEC_LINE.match(line.strip())
        if m:
            d = m.group(4)
            out.append((m.group(1), m.group(2), m.group(3), None if d == "?" else int(d[:-1]),
                        m.group(7), int(m.group(8)) if m.group(8) else 0, m.group(6) is not None,
                        m.group(5)))
    return out


def merged_age(row):
    """Piece 109: one age per decision = the OLDER of the source's own age
    (days/since) and the first-raised age (raised/open). -> (days|None, since|None).
    Both today (0 days, or no raised and source 0d) -> (0, None) == 'new today'."""
    days, raised, od, since = row[3], row[4], row[5], row[7]
    cands = []
    if days is not None:
        cands.append((days, since))
    if raised is not None:
        cands.append((od, raised))
    if not cands:
        return None, None
    n, s = max(cands, key=lambda c: (c[0], c[1] is not None))
    return n, (s if n > 0 else None)


def age_text(n, since):
    if n is None:
        return "open ? days (no dated source)"
    if n == 0:
        return "new today"
    unit = "day" if n == 1 else "days"
    return f"open {n} {unit}" + (f" (since {since})" if since else "")


def decision_lines(path, shown, rel=None, limit=DEC_MAX):
    """'Boss decisions' section; shown = set of (mã or '-', kind) already in the summary."""
    label = rel or str(path)
    if path is None or not Path(path).exists():
        return ["Boss decisions: MISSING", f"- Full list: {label} (MISSING)"]
    seen, rows, dup = set(), [], 0
    for row in parse_boss_decisions_aged(Path(path).read_text(encoding="utf-8")):
        ma, q = row[0], row[1]
        if (ma, q) in seen:
            continue
        seen.add((ma, q))
        if (ma, dec_kind(q)) in shown:
            dup += 1
            continue
        rows.append(row)
    aged = any(r[6] for r in rows)
    if aged:  # piece 109: oldest merged age first, unknown last
        ages = [merged_age(r) for r in rows]
        order = sorted(range(len(rows)), key=lambda i: (ages[i][0] is None, -(ages[i][0] or 0), i))
    else:
        order = sorted(range(len(rows)), key=lambda i: (rows[i][3] is None, -(rows[i][3] or 0), i))
    L = [f"Boss decisions ({len(rows)} open{', oldest first' if aged else ''}):"]
    for i in order[:limit]:
        ma, q, ev, days, raised, od, has, _since = rows[i]
        if has:  # piece 109: single merged age
            L.append(f"- {ma} | {q} | {ev} | {age_text(*merged_age(rows[i]))}")
        else:  # pre-107 file: unchanged
            L.append(f"- {ma} | {q} | {ev} | {'?' if days is None else f'{days}d'}")
    if len(rows) > limit:
        L.append(f"- ...{len(rows) - limit} more")
    if not rows:
        L.append("- Nothing new beyond 'Waiting on you'.")
    if dup:
        L.append(f"- {dup} already listed above under 'Waiting on you'")
    L.append(f"- Full list: {label}")
    return L


def luxubu_line(root, date):
    sys.path.insert(0, str(HERE))
    import luxubu_status_record as lsr
    return lsr.summary_line(lsr.load(root, date))


def drafts_lines(tgz=None):
    """Piece 103: 'Draft work waiting' section; never raises."""
    sys.path.insert(0, str(HERE))
    import bundle_status as bs
    try:
        return bs.status_lines(tgz or bs.DEFAULT_TGZ)
    except Exception as e:  # noqa: BLE001
        return [bs.HEAD, f"- Bundle status unavailable ({type(e).__name__})."]


def build(qc, cost, digest, gaps, proposal, meta_ig, meta_fb, date, flips=None, held_order=None,
          meta_status=None, meta_source=None, freshness=None, decisions=None, decisions_rel=None, luxubu=None, drafts=None):
    L = [f"Sassy Closet daily summary {date} (DRAFT, not sent)", ""]
    if qc:
        c = qc.get("counts", {})
        fails, warns = qc.get("fails") or [], warn_codes(qc.get("warns"))
        overall = str(qc.get("overall", "?")).upper()
        if overall not in {"PASS", "WARN", "FAIL"}:
            overall = "UNKNOWN"
        p2 = (qc.get("pass2") or {}).get("agrees")
        s06 = (qc.get("s06") or {}).get("blob")
        L.append(f"Midnight QC: {overall}, {len(fails)} fail(s), {len(warns)} warning(s)"
                 + ("; second pass agreed." if p2 else "; second pass did not confirm."))
        bits = []
        if isinstance(c.get("live"), int):
            bits.append(f"{c['live']} items live")
        if isinstance(c.get("held"), int):
            bits.append(f"{c['held']} held")
        if isinstance(c.get("intake"), int):
            bits.append(f"intake {c['intake']} rows, {c.get('new_since_oct21', 0) if isinstance(c.get('new_since_oct21', 0), int) else '?'} new")
        if isinstance(s06, (int, float)):
            bits.append(f"S06 ${s06:g}")
        if bits:
            L.append("Shop: " + ", ".join(bits) + ".")
    else:
        L.append("Midnight QC: not found for today.")
    if cost:
        cc = cost.get("counts") or {}
        L.append(f"Taobao cost recheck: {cc.get('unreachable', '?')} listings unreachable"
                 f" ({', '.join(mas(cost.get('unreachable_mas')))}); "
                 f"{len(mas(cost.get('live_price_changed')))} live price change(s); "
                 f"{len(mas(cost.get('new_under_or_loss')))} new under-price/loss.")
        new = mas(cost.get("persistent_new_unreachable"))
        if new:
            L.append(f"Newly gone on Taobao and still live: {', '.join(new)}.")
        if cost.get("taobao_login_needed"):
            L.append("Taobao still needs your sign-in.")
    else:
        L.append("Taobao cost recheck: not found for today.")
    L.append("")

    # Meta
    if meta_status is None:
        meta_status = {"ig": single_source_override(meta_ig),
                       "fb": single_source_override(meta_fb)}
        meta_source = meta_source or "single-source override"
    ig, fb = meta_status["ig"][0], meta_status["fb"][0]
    snap = gaps is not None and (gaps.get("snapshot_posts") or 0) > 0
    no_ma, no_gia = gap_items(gaps, "no_ma"), gap_items(gaps, "no_gia")
    L += meta_lines(meta_status, meta_source)
    if luxubu is not None:
        L.append(luxubu)
    if gaps is None:
        L.append("Caption gaps: gap report unavailable, so not counted by script.")
    else:
        src = "Meta snapshot" if snap else "QC notes (no Meta snapshot saved)"
        L.append(f"Caption gaps from {src}: {len(no_ma)} post(s) with no mã, {len(no_gia)} with no Giá.")
        if no_ma:
            L.append(f"- No mã: {', '.join(no_ma)}")
        if no_gia:
            L.append(f"- No Giá: {', '.join(no_gia)}")
    L.append("")

    # Decisions
    L.append("Waiting on you:")
    cats = {k: list(v) for k, v in (digest or {}).items()}
    gone = mas((cost or {}).get("persistent_new_unreachable"))
    under = under_price_mas((qc or {}).get("warns"))
    unreach = set(mas((cost or {}).get("unreachable_mas")))
    pool = set(cats.pop("intake_mismatch", [])) | set(under)
    pool -= set(gone)  # already asked directly in the hold question
    flips = flips or {}
    flip_under = sorted(m for m, (iv, _bv) in flips.items() if iv == "UNDER")
    pool -= set(flip_under)  # piece 77: asked once, in the intake-cost line below
    flip_other = sorted(set(flips) - set(flip_under))
    split = {
        "mismatch_under": sorted(m for m in pool if m in set(under)),
        "mismatch_gone": sorted(m for m in pool if m in unreach and m not in set(under)),
    }
    split["mismatch_public"] = sorted(pool - set(split["mismatch_under"]) - set(split["mismatch_gone"]))
    cats.update({k: v for k, v in split.items() if v})
    if gone:
        L.append(f"- Should {' and '.join(gone) if len(gone) < 3 else ', '.join(gone)} go on hold? "
                 "Newly gone on Taobao and still live."); n_hold = 1
    else:
        n_hold = 0
    if flip_under:
        L.append(f"- Under the price formula at Nhung's intake cost (OK at baseline cost): "
                 f"{', '.join(flip_under)}"); n_hold += 1
    if flip_other:
        L.append(f"- Price verdict depends on cost source: {', '.join(flip_other)}"); n_hold += 1
    held_order = mas(held_order)
    cats.pop("popular_order_held", None)
    if held_order:
        L.append(f"- Remove held mãs from popular order? {', '.join(held_order)}"); n_hold += 1
    labels = [("hold_call", "Hold call"), ("price_approval", "Price approval (held)"),
              ("blob_photo_delete", "Delete public Blob photos of held items"),
              ("mismatch_under", "Under-priced at intake cost (midnight QC)"),
              ("mismatch_gone", "Taobao listing unreachable or gone"),
              ("mismatch_public", "Intake cost doesn't match public Taobao price")]
    n = n_hold
    for key, lab in labels:
        if cats.get(key):
            L.append(f"- {lab}: {', '.join(cats[key])}"); n += 1
    for key in sorted(set(cats) - {k for k, _ in labels}):
        L.append(f"- {key}: {', '.join(cats[key])}"); n += 1
    if proposal:
        v = proposal.get("verdicts") or {}
        props = [f"{m} {s}" for m, s in sorted(v.items()) if MA.match(m) and SELL.match(str(s))]
        need = [m for m, s in sorted(v.items()) if MA.match(m) and s == "NEEDS_INPUT"]
        if props:
            L.append(f"- Suggested sell prices to approve: {', '.join(props)}"); n += 1
        if need:
            L.append(f"- No price suggestion possible yet (missing input): {', '.join(need)}"); n += 1
    if ig != "pass" or fb != "pass":
        L.append("- Meta sign-in/recheck for the side not at PASS"); n += 1
    if n == 0:
        L.append("- Nothing.")
    if decisions is not False:
        shown = {(m, "gone") for m in gone} | {(m, "flip_under") for m in flip_under}
        # piece 99: grouped held-in-popular-order line covers each listed mã
        shown |= {(m, "popular_order_held") for m in held_order}
        # piece 99 audit: cost-source price line asks the same price question
        shown |= {(m, "flip_under") for m in flip_other}
        # piece 99 audit: suggested/missing-input price lines cover 'Needs a price'
        if proposal:
            shown |= {(m, "price_approval") for m in [p.split()[0] for p in props] + need}
        for key, _lab in labels:
            shown |= {(m, key) for m in cats.get(key, [])}
        if ig != "pass" or fb != "pass":
            shown.add(("-", "meta"))
        L += [""] + decision_lines(decisions, shown, decisions_rel)
    if drafts:
        L += [""] + list(drafts)
    if freshness:
        L += [""] + list(freshness)
    L += ["", "Nothing was posted, edited or deleted on Facebook or Instagram.", "- Mini Boss"]
    text = "\n".join(L) + "\n"
    if BANNED.search(text):
        raise SystemExit("refusing to write: banned content in draft")
    return text


REPO = HERE.parent
DEFAULT_SHOP_OUT = "/workspace/sassy-closet/out"


def shop_out():
    """Piece 110: the one shop out folder (SASSY_OUT, default /workspace/sassy-closet/out),
    so runs from any worktree write to the same place, never <worktree>/out."""
    return Path(os.environ.get("SASSY_OUT") or DEFAULT_SHOP_OUT)
PT = ZoneInfo("America/Los_Angeles")
PATH_FLAGS = ("root", "qc", "cost", "digest", "gaps", "proposal", "cost_basis",
              "order", "held", "catalog", "intake", "bundle", "out_dir")


def today_pt(now=None):
    """Today's date in America/Los_Angeles as YYYY-MM-DD."""
    now = now or dt.datetime.now(dt.timezone.utc)
    return now.astimezone(PT).date().isoformat()


def default_paths(repo=REPO):
    return {"order": repo / "sassy-closet-shop/data/popular-order.json",
            "held": repo / "data/held.json"}


def apply_defaults(a, argv=None, repo=REPO, now=None):
    """Fill only flags the caller did not pass explicitly."""
    given = set(argv if argv is not None else sys.argv[1:])
    if not any(x == "--date" or x.startswith("--date=") for x in given):
        a.date = today_pt(now)
    for k, v in default_paths(repo).items():
        if getattr(a, k) is None:
            setattr(a, k, v)
    return a


def generated_with(a):
    """Exact equivalent command: script path, date and path flags only."""
    parts = [str(Path(__file__).resolve()), "--date", str(a.date)]
    for k in PATH_FLAGS:
        v = getattr(a, k, None)
        if v is not None:
            parts += ["--" + k.replace("_", "-"), str(Path(v).resolve())]
    return " ".join(parts)


def add_footer(text, cmd):
    line = f"Generated with: {cmd}"
    if BANNED.search(line):
        raise SystemExit("refusing to write: banned content in footer")
    return text.rstrip("\n") + "\n\n" + line + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--date", default=today_pt())
    ap.add_argument("--root", type=Path, default=ROOT)
    ap.add_argument("--qc", type=Path)
    ap.add_argument("--cost", type=Path)
    ap.add_argument("--digest", type=Path)
    ap.add_argument("--gaps", type=Path)
    ap.add_argument("--proposal", type=Path)
    ap.add_argument("--cost-basis", type=Path)
    ap.add_argument("--order", type=Path)
    ap.add_argument("--held", type=Path)
    ap.add_argument("--catalog", type=Path, help="saved Blob catalog.v1.json (freshness only)")
    ap.add_argument("--intake", type=Path, help="intake status json (freshness only)")
    ap.add_argument("--bundle", type=Path, help="pending-draft-prs.tgz (piece 103)")
    ap.add_argument("--out-dir", type=Path, default=None,
                    help="override; default $SASSY_OUT/summaries (piece 110)")
    ap.add_argument("--stdout", action="store_true")
    ap.add_argument("--defaults", action="store_true",
                    help="resolve --order/--held from this script's repo and --date to today in PT")
    a = ap.parse_args(argv)
    if a.defaults:
        apply_defaults(a, argv)
    if a.out_dir is None:
        a.out_dir = shop_out() / "summaries"
    r, d = a.root, a.date
    qc = load_json(a.qc or r / "out/midnight-qc" / d / "summary.json")
    cost = load_json(a.cost or r / "verify/cost-recheck" / f"summary.{d}.json")
    dargs = ["--root", str(r)]
    if a.order:
        dargs += ["--order", str(a.order)]
    if a.held:
        dargs += ["--held", str(a.held)]
    dtext = a.digest.read_text(encoding="utf-8") if a.digest else run_local(
        "boss_decisions_digest.py", dargs)
    cbp = a.cost_basis or r / "out/reports" / d / "COST-BASIS.md"
    flips = parse_cost_basis(cbp.read_text(encoding="utf-8")) if cbp.exists() else {}
    gtext = a.gaps.read_text(encoding="utf-8") if a.gaps else run_local(
        "meta_caption_gap_report.py", ["--root", str(r), "--json"])
    try:
        gaps = json.loads(gtext) if gtext.strip() else None
    except json.JSONDecodeError:
        gaps = None
    prop = load_json(a.proposal or shop_out() / "proposals" / f"held-price-proposal-{d}.json")
    mst, msrc = read_meta_status(r, d)
    text = build(qc, cost, parse_digest(dtext), gaps, prop, None, None, d,
                 flips=flips, held_order=parse_held_order(dtext),
                 meta_status=mst, meta_source=msrc,
                 luxubu=luxubu_line(r, d),
                 drafts=drafts_lines(a.bundle),
                 decisions=r / "out/reports" / d / "BOSS-DECISIONS.md",
                 decisions_rel=f"out/reports/{d}/BOSS-DECISIONS.md",
                 freshness=freshness_lines(freshness_inputs(
                     r, d, a.catalog, a.intake, None, cbp, a.order)))
    text = add_footer(text, generated_with(a))
    a.out_dir.mkdir(parents=True, exist_ok=True)
    out = a.out_dir / f"daily-summary-{d}.md"
    out.write_text(text, encoding="utf-8")
    print(text if a.stdout else f"wrote {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
