#!/usr/bin/env python3
"""Piece 61: run today's local draft reports in order (READ-ONLY).

Runs taobao_unreachable_streak, boss_decisions_digest, meta_caption_gap_report,
intake_code_reuse_check, held_price_proposal (--proposal-dir) and
daily_summary_draft as subprocesses. Each tool's stdout+stderr goes to
out/reports/<date>/<NN-tool>.txt, and one INDEX.md lists exit code, status and
output path per tool. A failing tool never stops the rest; it is marked FAILED.
Piece 62: per-tool status mapping. For report tools where exit 1 means
"findings" (meta_caption_gap_report), exit 1 is GAPS, not FAILED. Real errors
(exit 2+, 124 timeout, 127 missing/crash) stay FAILED. Overall is FAILED > GAPS > OK.
No network, no live writes, sends nothing. Output under out/ (gitignored).
"""
from __future__ import annotations

import argparse
import datetime as dt
from zoneinfo import ZoneInfo
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SCRIPTS = REPO / "scripts"
DATA_ROOT = Path("/workspace/sassy-closet")
POPULAR_ORDER = REPO / "sassy-closet-shop" / "data" / "popular-order.json"
HELD_JSON = REPO / "data" / "held.json"


# tool -> {exit code: status}; codes not listed: 0 -> OK, else FAILED.
STATUS_MAP = {
    "meta_caption_gap_report": {0: "OK", 1: "GAPS"},
}


def status_for(tool: str, code: int, status_map=None) -> str:
    m = STATUS_MAP if status_map is None else status_map
    if code in (124, 127):
        return "FAILED"
    st = m.get(tool, {}).get(code)
    if st:
        return st
    return "OK" if code == 0 else "FAILED"


def overall(rows) -> str:
    failed = [r[0] for r in rows if r[2] == "FAILED"]
    gaps = [r[0] for r in rows if r[2] == "GAPS"]
    if failed:
        return "FAILED (" + ", ".join(failed) + ")"
    if gaps:
        return "GAPS (" + ", ".join(gaps) + ")"
    return "OK"


def _newest(paths):
    paths = sorted(p for p in paths if p.exists())
    return paths[-1] if paths else None


def build_steps(data_root: Path, report_dir: Path, date: str):
    cost_dir = data_root / "verify" / "cost-recheck"
    intake_json = data_root / "verify" / "_audit_intake_submissions.json"
    intake_csv = data_root / "verify" / "_audit_intake_export.csv"
    reuse_files = [p for p in (
        _newest(cost_dir.glob("cost-recheck-????-??-??.csv")) if cost_dir.exists() else None,
        intake_json, intake_csv,
    ) if p is not None and p.exists()]
    reuse_files += sorted((data_root / "inventory").glob("intake-*.md")) if (data_root / "inventory").exists() else []
    live = _newest((data_root / "verify").glob("too-cheap-????-??-??/live-prices.json")) if (data_root / "verify").exists() else None
    return [
        ("taobao_unreachable_streak", ["--dir", str(cost_dir)]),
        ("boss_decisions_digest", ["--root", str(data_root), "--order", str(POPULAR_ORDER), "--held", str(HELD_JSON)]),
        ("meta_caption_gap_report", ["--root", str(data_root)]),
        ("intake_code_reuse_check", [str(p) for p in reuse_files] or [str(intake_json)]),
        ("held_price_proposal", ["--intake", str(intake_json), "--live", str(live or data_root / "MISSING-live-prices.json"),
                                 "--proposal-dir", str(report_dir / "proposals"), "--date", date]),
        ("daily_summary_draft", ["--root", str(data_root), "--date", date, "--out-dir", str(report_dir / "summary"),
                                 "--order", str(POPULAR_ORDER), "--held", str(HELD_JSON)]),
    ]


def run_all(steps, report_dir: Path, scripts: Path = SCRIPTS, python: str = sys.executable, timeout: int = 300,
            status_map=None):
    report_dir.mkdir(parents=True, exist_ok=True)
    rows = []
    for i, (tool, args) in enumerate(steps, 1):
        out = report_dir / f"{i:02d}-{tool}.txt"
        script = scripts / f"{tool}.py"
        try:
            if not script.exists():
                raise FileNotFoundError(f"missing script {script.name}")
            cp = subprocess.run([python, str(script), *args], cwd=str(scripts.parent),
                                capture_output=True, text=True, timeout=timeout)
            code, text = cp.returncode, cp.stdout + (("\n--- stderr ---\n" + cp.stderr) if cp.stderr else "")
        except subprocess.TimeoutExpired:
            code, text = 124, f"TIMEOUT after {timeout}s\n"
        except Exception as e:  # keep going
            code, text = 127, f"ERROR {type(e).__name__}: {e}\n"
        out.write_text(text, encoding="utf-8")
        rows.append((tool, code, status_for(tool, code, status_map), out))
    return rows


def write_index(rows, report_dir: Path, date: str) -> Path:
    lines = [f"# Shop draft reports {date}", "", "Read-only local run. Nothing sent, nothing written live.", "",
             "| # | tool | exit | status | output |", "|---|---|---|---|---|"]
    for i, (tool, code, status, out) in enumerate(rows, 1):
        lines.append(f"| {i} | {tool} | {code} | {status} | {out.relative_to(report_dir)} |")
    lines += ["", f"Overall: {overall(rows)}", ""]
    for tool, _code, _status, out in rows:
        if tool == "boss_decisions_digest" and out.exists():
            tags = sorted(set(re.findall(r"^- \[([a-z0-9_]+)\]", out.read_text(encoding="utf-8"), re.M)))
            lines += [f"Digest items: {', '.join(tags) if tags else '(none)'}", ""]
    idx = report_dir / "INDEX.md"
    idx.write_text("\n".join(lines), encoding="utf-8")
    return idx


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--date", default=dt.datetime.now(dt.timezone.utc).astimezone(ZoneInfo("America/Los_Angeles")).date().isoformat())
    ap.add_argument("--data-root", type=Path, default=DATA_ROOT)
    ap.add_argument("--out-root", type=Path, default=REPO / "out" / "reports")
    a = ap.parse_args(argv)
    report_dir = a.out_root / a.date
    rows = run_all(build_steps(a.data_root, report_dir, a.date), report_dir)
    idx = write_index(rows, report_dir, a.date)
    for tool, code, status, _ in rows:
        print(f"{status:6} {code:3} {tool}")
    print(f"INDEX {idx}")
    print(f"Overall: {overall(rows)}")
    return 1 if any(r[2] == "FAILED" for r in rows) else 0


if __name__ == "__main__":
    sys.exit(main())
