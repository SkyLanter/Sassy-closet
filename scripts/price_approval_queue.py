#!/usr/bin/env python3
"""Price approval queue (piece 47): READ-ONLY, WARN-only.

Lists held/intake mãs waiting on a Boss price decision, with a reason
category per mã:
  missing_price          no sell price and no Boss-approved Giá
  needs_weight_approval  weight missing or not yet approved by Boss
  taobao_only            only a Taobao source; Boss must confirm the ¥
  flagged                intake row carries a flag (e.g. intake ¥ check)

Output is mã codes and reason categories ONLY. Cost figures (¥/$), sell
prices, supplier links and customer data are never copied into the report.
Reads: shared held list (held-incomplete.ts -> JSON, or --held), optional
--approved approved-held-gia.json, optional --intake JSON list of rows
{"ma", "sell_usd", "weight_kg", "weight_approved", "taobao_only", "flags"}.
Never writes prices, Blob, Square, Meta or intake. No network.
Exit: 0 queue empty, 1 WARN (mãs waiting), 2 usage/input error.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

from held_policy import norm_ma

ROOT = Path(__file__).resolve().parents[1]
REASONS = ("missing_price", "needs_weight_approval", "taobao_only", "flagged")
MA_RE = re.compile(r"^[A-Z]{1,2}\d{2,3}$")
FLAG_RE = re.compile(r"^[a-z][a-z0-9_]{0,40}$")


def load_held(path: Path | None) -> tuple[list[str], str]:
    if path is None:
        from too_cheap_check import held_json_from_ts
        path = held_json_from_ts()
    d = json.loads(Path(path).read_text(encoding="utf-8"))
    mas = d.get("heldIncomplete", []) if isinstance(d, dict) else d
    codes = [norm_ma(m) for m in mas if isinstance(m, str)]
    return [m for m in codes if MA_RE.match(m)], Path(path).name


def load_approved(path: Path | None) -> set[str]:
    if path is None:
        return set()
    d = json.loads(Path(path).read_text(encoding="utf-8"))
    return {c for c in (norm_ma(m) for m in (d.get("approvedGia") or {})) if MA_RE.match(c)}


def _has_price(v) -> bool:
    return isinstance(v, (int, float)) and not isinstance(v, bool) and v > 0


def reasons_for(row: dict | None, approved: bool) -> list[str]:
    row = row or {}
    out = []
    if not _has_price(row.get("sell_usd")) and not approved:
        out.append("missing_price")
    if not _has_price(row.get("weight_kg")) or row.get("weight_approved") is not True:
        if not approved:
            out.append("needs_weight_approval")
    if row.get("taobao_only") is True:
        out.append("taobao_only")
    if row.get("flags"):
        out.append("flagged")
    return out


def safe_flags(flags) -> list[str]:
    """Only short snake_case flag names survive; anything else (numbers, URLs, names) is dropped."""
    if not isinstance(flags, list):
        return []
    return sorted({f for f in flags if isinstance(f, str) and FLAG_RE.match(f)})


def run(held: list[str], intake: list[dict], approved: set[str], held_source: str = "") -> dict:
    rows = {}
    for r in intake:
        m = norm_ma(r.get("ma")) if isinstance(r, dict) and isinstance(r.get("ma"), str) else None
        if m and MA_RE.match(m):
            rows[m] = r
    queue = []
    for m in sorted(set(held) | set(rows)):
        rs = reasons_for(rows.get(m), m in approved)
        if rs:
            item = {"ma": m, "reasons": rs, "held": m in held}
            fl = safe_flags(rows.get(m, {}).get("flags"))
            if fl:
                item["flags"] = fl
            queue.append(item)
    by_reason = {k: [q["ma"] for q in queue if k in q["reasons"]] for k in REASONS}
    return {"schema": "price-approval-queue/v1", "piece": 47, "heldSource": held_source,
            "queue": queue, "byReason": by_reason, "waiting": [q["ma"] for q in queue],
            "writes": "none", "network": "none",
            "note": "WARN only; price decisions are Boss's call"}


def warn_lines(rep: dict) -> list[str]:
    return [f"{q['ma']}: {', '.join(q['reasons'])}" for q in rep["queue"]]


def markdown(rep: dict) -> str:
    out = [f"# Price approval queue: {'WARN' if rep['queue'] else 'PASS'}", ""]
    out += [f"- {k}: {', '.join(v) or 'none'}" for k, v in rep["byReason"].items()]
    out += ["", "Mã codes and reasons only. No costs, prices, links or customer data. Read-only."]
    return "\n".join(out) + "\n"


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--held", type=Path, help="held JSON (default shared held-incomplete.ts list)")
    p.add_argument("--approved", type=Path, help="approved-held-gia.json")
    p.add_argument("--intake", type=Path, help="intake JSON list of rows")
    p.add_argument("--json", action="store_true")
    a = p.parse_args(argv)
    try:
        held, src = load_held(a.held)
        intake = json.loads(a.intake.read_text(encoding="utf-8")) if a.intake else []
        if not isinstance(intake, list):
            raise ValueError("intake must be a JSON list")
        rep = run(held, intake, load_approved(a.approved), src)
    except Exception as e:  # noqa: BLE001
        print(f"error: {type(e).__name__}", file=sys.stderr)
        return 2
    print(json.dumps(rep, indent=2, ensure_ascii=False) if a.json else markdown(rep), end="" if not a.json else "\n")
    return 1 if rep["queue"] else 0


if __name__ == "__main__":
    sys.exit(main())
