#!/usr/bin/env python3
"""Piece 70: READ-ONLY cost-basis reconcile for live mãs.

Two checks priced the same mãs from different cost fields:
  - Midnight QC (out/midnight-qc/<date>/pass2.py) reads Nhung's intake export
    (/api/export CSV, column cost_cny; the largest number in the cell).
  - The daily too-cheap run (verify/too-cheap-<date>/run_check.py) reads the
    cost-recheck CSV (verify/cost-recheck/cost-recheck-<date>.csv, column
    baseline_cny = the "used" cost the live price was set on), falling back to
    the reprice report's yen column. scripts/too_cheap_check.py load_costs()
    also falls back from intake_cny to baseline_cny, so it can do the same.

For every live mã this lists each cost source, flags sources that disagree by
>= 10% (spread over the smallest), and flags mãs whose price verdict
(OK / UNDER vs the tier target) flips depending on the source. The public
Taobao list price (recheck_cny) is shown for reference only; it is never a
cost basis.

The report holds costs, so it is written only under out/ (gitignored, never
bundled). Stdout prints mã codes and verdicts only. No network, no writes
outside --out.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import re
import sys
import datetime as _dt
from zoneinfo import ZoneInfo
from decimal import Decimal
from pathlib import Path

from autolist import price
from too_cheap_check import landed_usd
from held_policy import norm_ma

# Source keys, in priority order. INTAKE is the one source both checks should use (Boss's rule).
INTAKE = "intake"
SOURCES = (
    (INTAKE, "Nhung intake export cost_cny (midnight QC)"),
    ("baseline", "cost-recheck baseline_cny (too-cheap run)"),
    ("reprice", "reprice report yen (too-cheap fallback)"),
)
LIST_REF = "list"
DISAGREE_PCT = Decimal("10")
_NUM = re.compile(r"\d+(?:\.\d+)?")


def num(v) -> Decimal | None:
    if v is None:
        return None
    found = _NUM.findall(str(v).replace(",", ""))
    if not found:
        return None
    d = max(Decimal(x) for x in found)
    return d if d > 0 else None


def _ma(v) -> str:
    """Mã key: trimmed, upper-case (' a01 ' and 'A01' are the same mã)."""
    return norm_ma(str(v or ""))


def _rows(path: Path | None) -> dict[str, dict]:
    if not path or not Path(path).exists():
        return {}
    with open(path, newline="", encoding="utf-8-sig") as fh:
        return {_ma(r.get("ma")): r for r in csv.DictReader(fh) if _ma(r.get("ma"))}


def load_live(path: Path) -> dict[str, float]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    prods = data.get("products", data) if isinstance(data, dict) else data
    return {_ma(p["ma"]): float(p["priceUsd"]) for p in prods
            if _ma(p.get("ma")) and p.get("priceUsd") is not None and math.isfinite(float(p["priceUsd"]))}


def gather(live: dict[str, float], intake: dict, recheck: dict, reprice: dict) -> dict[str, dict]:
    out = {}
    for ma in sorted(live):
        i, c, r = intake.get(ma, {}), recheck.get(ma, {}), reprice.get(ma, {})
        out[ma] = {
            "costs": {INTAKE: num(i.get("cost_cny")), "baseline": num(c.get("baseline_cny")),
                      "reprice": num(r.get("yen"))},
            "list": num(c.get("recheck_cny")),
            "kg": num(c.get("kg")) or num(r.get("kg")),
        }
    return out


def spread_pct(values: list[Decimal]) -> Decimal | None:
    if len(values) < 2:
        return None
    lo, hi = min(values), max(values)
    return (hi - lo) / lo * 100


def reconcile(live: dict[str, float], data: dict[str, dict]) -> list[dict]:
    rows = []
    for ma, d in data.items():
        costs = {k: v for k, v in d["costs"].items() if v is not None}
        kg = d["kg"]
        verdicts = {}
        targets = {}
        if kg is not None:
            for k, v in costs.items():
                t = price(landed_usd(v, kg))
                targets[k] = t
                verdicts[k] = "UNDER" if live[ma] < t else "OK"
        sp = spread_pct(list(costs.values()))
        disagree = sp is not None and sp >= DISAGREE_PCT
        flips = len(set(verdicts.values())) > 1
        if not costs:
            verdict = "NO_COST"
        elif kg is None:
            verdict = "NO_KG"
        elif flips:
            verdict = "FLIP"
        elif disagree:
            verdict = "DISAGREE"
        else:
            verdict = "AGREE"
        rows.append(dict(ma=ma, live=live[ma], costs=costs, list=d["list"], kg=kg, spread=sp,
                         disagree=disagree, flips=flips, verdicts=verdicts, targets=targets,
                         intake_verdict=verdicts.get(INTAKE), verdict=verdict))
    return rows


def _fmt(v, places=2):
    return "" if v is None else f"{float(v):.{places}f}"


def markdown(rows: list[dict], day: str) -> str:
    keys = [k for k, _ in SOURCES]
    out = [f"# Cost-basis reconcile {day}", "",
           "LOCAL ONLY (out/, gitignored, never bundled): this file holds costs.", "",
           "Sources: " + "; ".join(f"`{k}` = {label}" for k, label in SOURCES)
           + f"; `{LIST_REF}` = public list (reference only, not a cost basis).", "",
           f"- Live mãs: {len(rows)}",
           f"- Disagree >= {DISAGREE_PCT}%: {', '.join(r['ma'] for r in rows if r['disagree']) or 'none'}",
           f"- Verdict flips by source: {', '.join(r['ma'] for r in rows if r['flips']) or 'none'}",
           f"- Missing kg: {', '.join(r['ma'] for r in rows if r['verdict'] == 'NO_KG') or 'none'}",
           f"- No cost in any source: {', '.join(r['ma'] for r in rows if r['verdict'] == 'NO_COST') or 'none'}",
           "", "| mã | live $ | " + " | ".join(f"{k} ¥" for k in keys) + " | list ¥ | kg | spread % | "
           + " | ".join(f"{k} target $ / verdict" for k in keys) + " | result |",
           "|" + "---|" * (6 + 2 * len(keys))]
    for r in rows:
        cells = [r["ma"], f"{r['live']:g}"] + [_fmt(r["costs"].get(k)) for k in keys]
        cells += [_fmt(r["list"]), _fmt(r["kg"], 3), _fmt(r["spread"], 1)]
        cells += [f"{r['targets'][k]} / {r['verdicts'][k]}" if k in r["verdicts"] else "" for k in keys]
        cells.append(r["verdict"])
        out.append("| " + " | ".join(cells) + " |")
    out += ["", "Read-only. No intake, Blob, hub, Square, Meta or price writes. "
            "Any raise needs Boss's yes (see docs/proposals/cost-basis-one-source.md)."]
    return "\n".join(out) + "\n"


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--live", required=True, type=Path, help="live catalog JSON snapshot")
    p.add_argument("--intake", required=True, type=Path, help="Nhung intake export CSV (cost_cny)")
    p.add_argument("--recheck", type=Path, help="cost-recheck CSV (baseline_cny, recheck_cny, kg)")
    p.add_argument("--reprice", type=Path, help="reprice report CSV (yen, kg)")
    p.add_argument("--date", default=_dt.datetime.now(_dt.timezone.utc).astimezone(ZoneInfo("America/Los_Angeles")).date().isoformat())
    p.add_argument("--out", type=Path, help="default out/reports/<date>/COST-BASIS.md")
    a = p.parse_args(argv)
    live = load_live(a.live)
    rows = reconcile(live, gather(live, _rows(a.intake), _rows(a.recheck), _rows(a.reprice)))
    out = a.out or Path("out/reports") / a.date / "COST-BASIS.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(markdown(rows, a.date), encoding="utf-8")
    flagged = [r for r in rows if r["disagree"] or r["flips"]]
    print(f"wrote {out}: {len(rows)} live; flagged {len(flagged)}")
    for r in flagged:
        print(f"  {r['ma']}: {r['verdict']}" + (f" (intake says {r['intake_verdict']})" if r["intake_verdict"] else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
