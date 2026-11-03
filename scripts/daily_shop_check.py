#!/usr/bin/env python3
"""Read-only daily shop check: too-cheap + headroom, held price sheet, caption Giá, intake gaps.

Runs the three existing read-only checks (scripts/too_cheap_check.py,
scripts/held_price_proposal.py, scripts/caption_gia_check.py [a shim over
caption_lint.py since piece 33]) plus the intake
gaps report (scripts/intake_gaps.py) on LOCAL input
files only and writes ONE combined markdown + JSON summary with an overall
PASS / WARN / FAIL. No network unless --hosts. No Blob, Square, intake, Meta or price writes.

Overall rules
  FAIL  too-cheap finds a live mã under target, S06 drifts off its $25 lock,
        any caption post FAILs, or a section cannot run (bad/missing input).
  WARN  any skipped mã (missing kg/¥), headroom band hits (--headroom-pct > 0),
        held mãs that need Boss (missing ¥/kg), caption posts with WARN, or any
        intake gap / suspect Nhung cost. Intake gaps are WARN only, never FAIL
        (even if that section cannot run); suspect costs are listed for Boss
        exactly as stored and are never fixed.
  PASS  none of the above.
  hosts (opt-in --hosts): vercel.app host down/TLS/held-live/S06-off -> FAIL.
  The no-headroom list (mãs priced exactly at their formula target) is shown
  for information only; formula-priced mãs are expected to sit there.

Reduced mode (--reduced --snapshot data/daily-inputs/snapshot.json) runs on the
cost-free export from scripts/export_daily_inputs.py. Cost-based sections
(too_cheap, held_sheet, intake_gaps) report SKIP-NO-COSTS and never FAIL. The
snapshot_rules section still checks: held mã live -> FAIL, S06 off $25 -> FAIL,
live mã without a $ price -> WARN.

held_photos (--held-photos report.json from scripts/held_photo_check.py): WARN
when any held mã photo URL still answers 200, never FAIL (a bad/missing report
is WARN too). Omitted -> SKIP; reduced mode -> SKIP. This script itself still
makes no network calls; the HEAD probing happens in held_photo_check.py.

run_gaps (--run-gaps ROOT, piece 38): scripts/run_gap_check.py over local
output folders; missing days, stale jobs or half-written outputs are WARN,
never FAIL (a bad config is WARN too). Omitted -> no section. Works in reduced mode.

held_photo_watch (--held-photo-watch, piece 46): scripts/held_photo_public_watch.py,
    shared held list, HEAD-only or --held-photo-watch-fixture offline; WARN only, no Blob writes.
hung_runs (--hung-runs AUTOLIST_DIR, piece 45): scripts/hung_run_watch.py over
the auto-list state/ and runs/ folders; missed 15-min slots, stale held locks or
half-written runs are WARN, never FAIL (an error is WARN too). Read-only:
nothing is killed, unlocked or deleted. Omitted -> no section. Works in reduced mode.

price_queue (--price-queue, piece 47): scripts/price_approval_queue.py, WARN-only
caption_gaps (--caption-gaps EXPORT, piece 48): scripts/caption_gap_watch.py, WARN-only
list of mãs waiting on a Boss price decision (mã + reason only).

Exit codes: 0 PASS, 1 WARN, 2 FAIL (argparse usage errors also exit 2).
With --warn-ok, WARN exits 0.
"""
from __future__ import annotations

import argparse
import contextlib
import io
import json
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import caption_gia_check  # noqa: E402
import host_health_check  # noqa: E402
import held_price_proposal  # noqa: E402
import intake_gaps  # noqa: E402
import too_cheap_check  # noqa: E402
from held_policy import norm_ma  # noqa: E402

EXIT = {"PASS": 0, "WARN": 1, "FAIL": 2}
RANK = {"PASS": 0, "SKIP": 0, "SKIP-NO-COSTS": 0, "WARN": 1, "FAIL": 2}
COST_SECTIONS = ("too_cheap", "held_sheet", "intake_gaps")
S06_LOCK = 25


def _run(fn, argv: list[str]) -> dict:
    """Call a check's main() writing JSON to a temp file; return parsed JSON."""
    with tempfile.TemporaryDirectory() as td:
        out = Path(td) / "out.json"
        with contextlib.redirect_stdout(io.StringIO()):
            rc = fn(argv + ["--out-json", str(out), "--out-md", str(Path(td) / "out.md")])
        data = json.loads(out.read_text(encoding="utf-8"))
        data["_rc"] = rc
        return data


def judge_too_cheap(s: dict) -> dict:
    c = s["counts"]
    fail, warn, info = [], [], []
    if c.get("under"):
        fail.append(f"{c['under']} live mã under target: " + ", ".join(r["ma"] for r in s["under_target"]))
    if c.get("lock-drift"):
        fail.append(f"S06 lock drift ({c['lock-drift']})")
    if c.get("skip-missing"):
        warn.append(f"{c['skip-missing']} skipped (missing kg/¥): "
                    + ", ".join(r["ma"] for r in s["skipped"] if r["decision"] == "skip-missing"))
    if s.get("headroom_band"):
        warn.append(f"{len(s['headroom_band'])} within {s['headroom_pct']:g}% of target: "
                    + ", ".join(r["ma"] for r in s["headroom_band"]))
    info.append(f"{len(s.get('no_headroom', []))} priced exactly at target (no headroom)")
    info.append(f"{c.get('list-only', 0)} list-only (held, never raised)")
    return _section("too_cheap", fail, warn, info, {
        "outcome": s["outcome"], "live_count": s["live_count"], "counts": c,
        "no_headroom": [r["ma"] for r in s.get("no_headroom", [])],
        "headroom_band": [r["ma"] for r in s.get("headroom_band", [])]})


def judge_held(s: dict) -> dict:
    warn, info = [], []
    if s.get("needs_boss"):
        warn.append(f"{len(s['needs_boss'])} held mã need Boss (missing ¥/kg): " + ", ".join(s["needs_boss"]))
    quotes = [p for p in s.get("proposals", []) if p.get("status") == "quote"]
    info.append(f"{len(quotes)} quoted (tiered / flat): " + ", ".join(
        f"{p['ma']} ${p.get('tiered_usd')}/${p.get('flat25_usd')}" for p in quotes))
    if s.get("already_live"):
        info.append("already live: " + ", ".join(sorted(s["already_live"])))
    info.append("quotes are proposals only; nothing approved or priced")
    return _section("held_sheet", [], warn, info, {
        "count": s.get("count"), "needs_boss": s.get("needs_boss", []),
        "already_live": s.get("already_live", {}), "approved": s.get("approved", False)})


def judge_captions(s: dict) -> dict:
    c = s["counts"]
    fail = [f"{p['post']} {p.get('ma') or '?'}: {', '.join(p['issues'])}" for p in s["posts"] if p["status"] == "FAIL"]
    warn = [f"{p['post']} {p.get('ma') or '?'}: {', '.join(p['issues'])}" for p in s["posts"] if p["status"] == "WARN"]
    return _section("captions", fail, warn, [f"PASS {c['PASS']} · WARN {c['WARN']} · FAIL {c['FAIL']}"],
                    {"counts": c})


def judge_intake_gaps(s: dict) -> dict:
    """Intake gaps never FAIL. Gaps and suspect costs are WARN for Boss; nothing is fixed."""
    warn, info = [], []
    by = s.get("by_type", {})
    for t, mas in by.items():
        if mas:
            warn.append(f"{t}: {len(mas)} mã: " + ", ".join(mas))
    sus = [(r["ma"], a) for r in s.get("rows", []) for a in r.get("suspect", [])]
    for ma, a in sus:
        info.append(f"suspect for Boss (as stored, not fixed): {ma} {a['type']}: {a['detail']}")
    c = s.get("counts", {})
    info.append(f"{s.get('intake_mas', 0)} intake mãs; " + "; ".join(
        f"{g} {v['mas']} ({v['with_gaps']} gaps, {v['with_suspect']} suspect)" for g, v in c.items()))
    info.append("report only: Nhung values never fixed")
    return _section("intake_gaps", [], warn, info, {
        "intake_mas": s.get("intake_mas"), "counts": c,
        "by_type": by, "suspect": [{"ma": m, **a} for m, a in sus]})


def warn_errored(name: str, err: BaseException) -> dict:
    return _section(name, [], [f"could not run: {type(err).__name__}: {err}"], [], {})


def _section(name, fail, warn, info, detail) -> dict:
    status = "FAIL" if fail else "WARN" if warn else "PASS"
    return {"name": name, "status": status, "fail": fail, "warn": warn, "info": info, "detail": detail}


def skipped(name: str, why: str) -> dict:
    return {"name": name, "status": "SKIP", "fail": [], "warn": [], "info": [why], "detail": {}}


def errored(name: str, err: BaseException) -> dict:
    return _section(name, [f"could not run: {type(err).__name__}: {err}"], [], [], {})


def skip_no_costs(name: str) -> dict:
    return {"name": name, "status": "SKIP-NO-COSTS", "fail": [], "warn": [],
            "info": ["reduced mode: needs Nhung costs, not in the cost-free snapshot"], "detail": {}}


def load_snapshot(path: Path) -> dict:
    snap = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(snap, dict) or snap.get("schema") != "daily-inputs/v1" or not isinstance(snap.get("items"), list):
        raise ValueError(f"{path.name}: not a daily-inputs/v1 snapshot")
    return snap


def judge_snapshot(snap: dict) -> dict:
    fail, warn = [], []
    items = [{**i, "ma": norm_ma(i.get("ma"))} for i in snap["items"]]
    held_live = [i["ma"] for i in items if i.get("held") and i.get("live")]
    if held_live:
        fail.append("held mã live: " + ", ".join(held_live))
    s06 = next((i for i in items if i["ma"] == "S06" and i.get("live")), None)
    if s06 and s06.get("sellUsd") != S06_LOCK:
        fail.append(f"S06 off ${S06_LOCK} lock: {s06.get('sellUsd')}")
    nop = [i["ma"] for i in items if i.get("live") and not i.get("sellUsd")]
    if nop:
        warn.append("live mã without $ price: " + ", ".join(nop))
    live = sum(1 for i in items if i.get("live"))
    held = sum(1 for i in items if i.get("held"))
    return _section("snapshot_rules", fail, warn,
                    [f"snapshot {snap.get('date')}: {len(items)} mã, {live} live, {held} held"],
                    {"live": live, "held": held, "mas": len(items)})


def judge_hosts(hh: dict) -> dict:
    """hosts section: any vercel.app host problem -> FAIL."""
    info = [f"{r['host']}: DNS {r['dns']}; TLS {r['tls']}; GET / {r.get('status', '-')}" for r in hh["hosts"]]
    return _section("hosts", list(hh["fail"]), list(hh["warn"]), info, {"hosts": hh["hosts"]})


def hosts_section(enabled: bool, runner=None) -> dict:
    if not enabled:
        return skipped("hosts", "no --hosts given (network check is opt-in)")
    try:
        return judge_hosts((runner or host_health_check.run)())
    except Exception as e:  # noqa: BLE001
        return errored("hosts", e)


def reduced_sections(snap: dict) -> list[dict]:
    return [skip_no_costs(n) for n in COST_SECTIONS] + [judge_snapshot(snap), held_photos_reduced()]


def held_photos_reduced() -> dict:
    return skipped("held_photos", "reduced mode: held photo exposure not checked")


def judge_held_photos(rep: dict) -> dict:
    """Held photos never FAIL. Exposed URLs are WARN for Boss; nothing is deleted."""
    if not isinstance(rep, dict) or rep.get("schema") != "held-photos/v1":
        raise ValueError("not a held-photos/v1 report")
    warn, info = [], []
    exp = rep.get("exposed", [])
    if exp:
        warn.append(f"{len(exp)} held photo URL(s) still public (200): "
                    + ", ".join(e["url"].split("/products/", 1)[-1] for e in exp))
    if rep.get("errors"):
        info.append(f"{len(rep['errors'])} URL(s) not checked cleanly: "
                    + ", ".join(f"{e['url'].split('/products/', 1)[-1]} {e['status']}" for e in rep["errors"]))
    info.append(f"{len(rep.get('held', []))} held mã, {rep.get('checked', 0)} URLs HEAD-checked at {rep.get('checkedAt')}")
    info.append("report only: deleting Blob objects is Boss's call")
    return _section("held_photos", [], warn, info,
                    {"exposedMas": rep.get("exposedMas", []), "exposed": exp, "checked": rep.get("checked", 0)})


def run_gaps_section(a) -> dict:
    """Run gaps never FAIL. Read-only; paths and dates only."""
    if not getattr(a, "run_gaps", None):
        return skipped("run_gaps", "no --run-gaps root given")
    try:
        import run_gap_check
        from datetime import datetime, timezone
        now = datetime.fromisoformat(a.run_gaps_now) if a.run_gaps_now else datetime.now(timezone.utc)
        rep = run_gap_check.run(a.run_gaps, a.run_gaps_config or run_gap_check.DEFAULT_CONFIG, now, a.run_gaps_days)
    except Exception as e:  # noqa: BLE001
        return warn_errored("run_gaps", e)
    warn, info = [], []
    for r in rep["jobs"]:
        bits = []
        if r["missing"]:
            bits.append(f"{len(r['missing'])} missing day(s): " + ", ".join(r["missing"]))
        if r["stale"]:
            bits.append("stale (no output today past expected hour)")
        for d, v in r["half_written"].items():
            bits.append(f"half-written {d}: " + ", ".join(v))
        (warn if bits else info).append(f"{r['job']} (last {r['last_output'] or 'never'}): " + ("; ".join(bits) or "OK"))
    info.append("report only: nothing re-run or deleted")
    return _section("run_gaps", [], warn, info, {"jobs": rep["jobs"], "days": rep["days"]})


def hung_runs_section(a) -> dict:
    """Hung-run watch never FAILs. Read-only; paths and times only."""
    try:
        import hung_run_watch
        from datetime import datetime, timezone
        now = datetime.fromisoformat(a.hung_runs_now) if a.hung_runs_now else datetime.now(timezone.utc)
        window = None if a.hung_runs_no_window else hung_run_watch.DEFAULT_WINDOW
        rep = hung_run_watch.run(Path(a.hung_runs), now, window=window)
    except Exception as e:  # noqa: BLE001
        return warn_errored("hung_runs", e)
    info = [f"heartbeat {rep['heartbeat'] or 'none'}; run in progress: {rep['run_in_progress']}",
            "report only: nothing killed, unlocked or deleted"]
    return _section("hung_runs", [], list(rep["warn"]), info,
                    {"slots": rep["slots"], "stale_locks": rep["stale_locks"], "half_written": rep["half_written"]})


def held_photo_watch_section(a) -> dict:
    """Held photo public watch (piece 46) never FAILs. HEAD-only or offline fixture; no Blob writes."""
    try:
        import held_photo_public_watch as w
        held, src = w.shared_held(a.held_photo_watch_held)
        sources = w.load_sources(a.held_photo_watch_catalog, a.held_photo_watch_health, a.held_photo_watch_files)
        fx = a.held_photo_watch_fixture
        fixture = json.loads(Path(fx).read_text(encoding="utf-8")) if fx else None
        rep = w.run(held, sources, fixture=fixture, held_source=src)
    except Exception as e:  # noqa: BLE001
        return warn_errored("held_photo_watch", e)
    sec = judge_held_photos(rep)
    wt = rep["watch"]
    info = [f"mode {wt['mode']}; held list {wt['heldSource']}"] + sec["info"]
    if wt["newlyExposed"]:
        info.insert(0, "newly exposed (not in known S14/A24/A25): " + ", ".join(wt["newlyExposed"]))
    return _section("held_photo_watch", [], sec["warn"], info, dict(sec["detail"], watch=wt))


def price_queue_section(a) -> dict:
    """Price approval queue (piece 47) never FAILs. Mã codes + reasons only; no writes, no network."""
    try:
        import price_approval_queue as q
        held, src = q.load_held(a.price_queue_held)
        intake = json.loads(Path(a.price_queue_intake).read_text(encoding="utf-8")) if a.price_queue_intake else []
        rep = q.run(held, intake, q.load_approved(a.price_queue_approved), src)
    except Exception as e:  # noqa: BLE001
        return warn_errored("price_queue", e)
    info = [f"held list {rep['heldSource']}", "report only: price decisions are Boss's call"]
    return _section("price_queue", [], q.warn_lines(rep), info,
                    {"byReason": rep["byReason"], "waiting": rep["waiting"]})


def caption_gaps_section(a) -> dict:
    """Caption gap watch (piece 48) never FAILs. Saved export only; no Meta calls."""
    try:
        import caption_gap_watch as g
        rep = g.run(g.load_posts(a.caption_gaps), g.load_prices(a.caption_gaps_live, a.caption_gaps_approved))
    except Exception as e:  # noqa: BLE001
        return warn_errored("caption_gaps", e)
    info = [f"{rep['posts']} posts in saved export", "report only: edit the original post, Boss's call"]
    return _section("caption_gaps", [], g.warn_lines(rep), info, {"byIssue": rep["byIssue"]})


def combine(sections: list[dict]) -> dict:
    overall = "PASS"
    for s in sections:
        if RANK[s["status"]] > RANK[overall]:
            overall = s["status"]
    return {"overall": overall, "sections": sections, "writes": "none", "network": "none"}


def markdown(summary: dict, title: str) -> str:
    out = [f"# {title}: {summary['overall']}", ""]
    out += ["| check | status |", "|---|---|"] + [f"| {s['name']} | {s['status']} |" for s in summary["sections"]]
    for s in summary["sections"]:
        out += ["", f"## {s['name']}: {s['status']}"]
        out += [f"- FAIL: {x}" for x in s["fail"]] + [f"- WARN: {x}" for x in s["warn"]] + [f"- {x}" for x in s["info"]]
    out += ["", "Read-only. " + ("No network." if summary.get("network") == "none" else "Network: read-only GETs (hosts).") + " No Blob, Square, intake, Meta or price writes."]
    return "\n".join(out) + "\n"


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--live", type=Path, help="catalog snapshot JSON (too-cheap + captions)")
    p.add_argument("--costs", type=Path, help="intake ¥ cost CSV (too-cheap; required unless --reduced)")
    p.add_argument("--reduced", action="store_true", help="cost-free mode on --snapshot; cost checks SKIP-NO-COSTS")
    p.add_argument("--snapshot", type=Path, help="data/daily-inputs/snapshot.json (with --reduced)")
    p.add_argument("--weights", action="append", type=Path, default=[], help="fallback kg CSV, repeatable")
    p.add_argument("--headroom-pct", type=float, default=0.0)
    p.add_argument("--intake", type=Path, help="intake submissions JSON (held sheet; omit to skip)")
    p.add_argument("--held-live", type=Path, help="price map for held sheet (default --live)")
    p.add_argument("--held-live-catalog", type=Path, help="catalog for 'already live' marking")
    p.add_argument("--captions", nargs="*", type=Path, default=[], help="saved caption files (omit to skip)")
    p.add_argument("--gaps-intake", type=Path, help="intake JSON for intake gaps (default --intake; omit both to skip)")
    p.add_argument("--gaps-live-catalog", type=Path, help="catalog for intake gaps (default --held-live-catalog or --live)")
    p.add_argument("--held-policy", type=Path, help="held.json for intake gaps (default data/held.json)")
    p.add_argument("--gaps-weights", action="append", type=Path, default=[], help="kg CSV for intake gaps, repeatable")
    p.add_argument("--no-intake-gaps", action="store_true", help="skip the intake gaps section")
    p.add_argument("--held-photos", type=Path, help="held_photo_check.py report JSON (omit to skip)")
    p.add_argument("--strict-first-line", action="store_true")
    p.add_argument("--title", default="Daily shop check")
    p.add_argument("--out-md", type=Path)
    p.add_argument("--out-json", type=Path)
    p.add_argument("--hosts", action="store_true",
                   help="add the read-only sell-host health section (network GETs to the two vercel.app hosts; problem = FAIL)")
    p.add_argument("--run-gaps", type=Path, metavar="ROOT", help="add WARN-only run_gaps section over this shop work dir")
    p.add_argument("--run-gaps-config", type=Path, help="run-gaps.json (default data/run-gaps.json)")
    p.add_argument("--run-gaps-days", type=int, default=14)
    p.add_argument("--hung-runs", type=Path, metavar="AUTOLIST_DIR", help="add WARN-only hung_runs section (scripts/hung_run_watch.py)")
    p.add_argument("--hung-runs-now", help="ISO time for hung_runs (tests/replays)")
    p.add_argument("--hung-runs-no-window", action="store_true", help="hung_runs: treat every slot as owed (24h)")
    p.add_argument("--held-photo-watch", action="store_true", help="add WARN-only held_photo_watch section (piece 46, HEAD-only)")
    p.add_argument("--held-photo-watch-fixture", type=Path, help="held_photo_watch offline status JSON (no network)")
    p.add_argument("--held-photo-watch-held", type=Path, help="held JSON override (default shared held-incomplete.ts list)")
    p.add_argument("--held-photo-watch-catalog", type=Path, action="append", default=[])
    p.add_argument("--held-photo-watch-health", type=Path, action="append", default=[])
    p.add_argument("--held-photo-watch-files", type=Path, action="append", default=[])
    p.add_argument("--price-queue", action="store_true", help="add WARN-only price_queue section (piece 47)")
    p.add_argument("--price-queue-held", type=Path, help="held JSON override for price_queue")
    p.add_argument("--price-queue-approved", type=Path, help="approved-held-gia.json for price_queue")
    p.add_argument("--caption-gaps", type=Path, help="saved FB/IG captions export: WARN-only caption_gaps section (piece 48)")
    p.add_argument("--caption-gaps-live", type=Path, help="live price list JSON for caption_gaps")
    p.add_argument("--caption-gaps-approved", type=Path, help="approved-held-gia.json for caption_gaps")
    p.add_argument("--price-queue-intake", type=Path, help="intake rows JSON for price_queue")
    p.add_argument("--run-gaps-now", help="ISO time for run_gaps (tests/replays)")
    p.add_argument("--warn-ok", action="store_true", help="exit 0 on WARN")
    a = p.parse_args(argv)
    if a.reduced:
        if not a.snapshot:
            p.error("--reduced needs --snapshot")
        if a.costs or a.intake or a.captions:
            p.error("--reduced takes only --snapshot (no --costs/--intake/--captions)")
    elif not (a.live and a.costs):
        p.error("--live and --costs are required (or use --reduced --snapshot)")

    if a.reduced:
        try:
            sections = reduced_sections(load_snapshot(a.snapshot))
        except (Exception, SystemExit) as e:  # noqa: BLE001
            sections = [skip_no_costs(n) for n in COST_SECTIONS] + [errored("snapshot_rules", e), held_photos_reduced()]
        return _finish(sections, a)

    sections = []
    try:
        tc_argv = ["--live", str(a.live), "--costs", str(a.costs), "--headroom-pct", str(a.headroom_pct)]
        for w in a.weights:
            tc_argv += ["--weights", str(w)]
        sections.append(judge_too_cheap(_run(too_cheap_check.main, tc_argv)))
    except (Exception, SystemExit) as e:  # noqa: BLE001
        sections.append(errored("too_cheap", e))
    if a.intake:
        try:
            h = ["--intake", str(a.intake), "--live", str(a.held_live or a.live)]
            if a.held_live_catalog:
                h += ["--live-catalog", str(a.held_live_catalog)]
            sections.append(judge_held(_run(held_price_proposal.main, h)))
        except (Exception, SystemExit) as e:  # noqa: BLE001
            sections.append(errored("held_sheet", e))
    else:
        sections.append(skipped("held_sheet", "no --intake given"))
    if a.captions:
        try:
            c = [str(x) for x in a.captions] + ["--live", str(a.live)]
            if a.strict_first_line:
                c.append("--strict-first-line")
            sections.append(judge_captions(_run(caption_gia_check.main, c)))
        except (Exception, SystemExit) as e:  # noqa: BLE001
            sections.append(errored("captions", e))
    else:
        sections.append(skipped("captions", "no caption files given"))

    gi = a.gaps_intake or a.intake
    if a.no_intake_gaps or not gi:
        sections.append(skipped("intake_gaps", "skipped (--no-intake-gaps)" if a.no_intake_gaps else "no intake given"))
    else:
        try:
            g = ["--intake", str(gi), "--live-catalog", str(a.gaps_live_catalog or a.held_live_catalog or a.live)]
            if a.held_policy:
                g += ["--held", str(a.held_policy)]
            for w in a.gaps_weights:
                g += ["--weights", str(w)]
            sections.append(judge_intake_gaps(_run(intake_gaps.main, g)))
        except (Exception, SystemExit) as e:  # noqa: BLE001
            sections.append(warn_errored("intake_gaps", e))

    if a.held_photos:
        try:
            sections.append(judge_held_photos(json.loads(a.held_photos.read_text(encoding="utf-8"))))
        except (Exception, SystemExit) as e:  # noqa: BLE001
            sections.append(warn_errored("held_photos", e))
    else:
        sections.append(skipped("held_photos", "no --held-photos report given"))

    return _finish(sections, a)


def _finish(sections: list[dict], a) -> int:
    if getattr(a, "run_gaps", None):
        sections = sections + [run_gaps_section(a)]
    if getattr(a, "hung_runs", None):
        sections = sections + [hung_runs_section(a)]
    if getattr(a, "held_photo_watch", False):
        sections = sections + [held_photo_watch_section(a)]
    if getattr(a, "price_queue", False):
        sections = sections + [price_queue_section(a)]
    if getattr(a, "caption_gaps", None):
        sections = sections + [caption_gaps_section(a)]
    if getattr(a, "hosts", False):
        sections = sections + [hosts_section(True)]
    summary = combine(sections)
    if getattr(a, "hosts", False):
        summary["network"] = "read-only GET (hosts section only)"
    if a.reduced:
        summary["mode"] = "reduced"
    md = markdown(summary, a.title)
    if a.out_json:
        a.out_json.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if a.out_md:
        a.out_md.write_text(md, encoding="utf-8")
    print(md, end="")
    rc = EXIT[summary["overall"]]
    return 0 if (rc == 1 and a.warn_ok) else rc


if __name__ == "__main__":
    sys.exit(main())
