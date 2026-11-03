"""Read-only daily too-cheap check.

For each live mã, landed = intake ¥ / 6.723 + 10.52 * kg, and the target is
the tiered sell from autolist.price (35% at <= $25, sliding to 25% at $45,
flat 25% above). The cost is Nhung's intake ¥, never the public Taobao list ¥.

- S06 is locked at $25 and is never reported as under target.
- Held and never-list mãs are skipped. The list is resolved through
  sassy-closet-shop/lib/held-incomplete.ts, which imports data/held.json.
- A mã with no kg or no intake ¥ is skipped. No weight is guessed.
- "list-only" means the price passes at intake ¥ but would be under target
  at the public list ¥. It is reported separately and is never a raise.
- "no headroom" lists priced mãs (ok or list-only) whose live price equals
  the intake-¥ target exactly, so any cost rise puts them under.
- --headroom-pct N adds a warning band: live above target by at most N% of
  the target. Both are warnings only; they never change a decision or price.

Inputs are local files only. This script makes no network calls and writes
nothing except the --out-md and --out-json files you name. It does not
touch intake, Blob, the hub, Square, Meta, or any live price.
"""

from __future__ import annotations

import argparse
import csv
import math
import json
import re
from dataclasses import asdict, dataclass
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

from autolist import S06_LOCK_USD, price
from held_policy import HeldPolicy, load_held_policy, norm_ma

FX_CNY_PER_USD = Decimal("6.723")
SHIP_USD_PER_KG = Decimal("10.52")
ROOT = Path(__file__).resolve().parents[1]
HELD_TS = ROOT / "sassy-closet-shop" / "lib" / "held-incomplete.ts"
IMPORT_RE = re.compile(r"""import\s+\w+\s+from\s+["']([^"']+\.json)["']""")


def held_json_from_ts(ts_path: Path = HELD_TS) -> Path:
    """Return the JSON file that lib/held-incomplete.ts imports."""
    match = IMPORT_RE.search(ts_path.read_text(encoding="utf-8"))
    if not match:
        raise ValueError(f"{ts_path} does not import a held JSON file")
    return (ts_path.parent / match.group(1)).resolve()


def load_held_from_ts(ts_path: Path = HELD_TS) -> HeldPolicy:
    return load_held_policy(held_json_from_ts(ts_path))


def landed_usd(yen: Decimal, kg: Decimal) -> Decimal:
    return yen / FX_CNY_PER_USD + SHIP_USD_PER_KG * kg


def _num(value: object) -> Decimal | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    try:
        number = Decimal(text)
    except ArithmeticError:
        return None
    return number if number.is_finite() and number > 0 else None


@dataclass(frozen=True)
class Row:
    ma: str
    live_usd: float
    intake_cny: float | None
    list_cny: float | None
    kg: float | None
    landed_usd: float | None
    target_usd: int | None
    list_target_usd: int | None
    decision: str  # under | list-only | ok | locked | skip-held | skip-missing
    reason: str


def _f(value: Decimal | None, places: str = "0.0001") -> float | None:
    return None if value is None else float(value.quantize(Decimal(places), ROUND_HALF_UP))


def evaluate(
    live: dict[str, float],
    costs: dict[str, dict[str, str]],
    policy: HeldPolicy,
    weights: dict[str, Decimal] | None = None,
) -> list[Row]:
    weights = weights or {}
    rows: list[Row] = []
    for ma in sorted(live):
        code = norm_ma(ma)
        live_usd = float(live[ma])
        cost = costs.get(code, {})
        intake = _num(cost.get("intake_cny"))
        listed = _num(cost.get("list_cny"))
        kg = _num(cost.get("kg")) or weights.get(code)
        base = dict(ma=code, live_usd=live_usd, intake_cny=_f(intake, "0.01"),
                    list_cny=_f(listed, "0.01"), kg=_f(kg, "0.001"))

        held = policy.skip_reason(code)
        if not held and code != "S06" and not (math.isfinite(live_usd) and live_usd > 0):
            rows.append(Row(**base, landed_usd=None, target_usd=None, list_target_usd=None,
                            decision="skip-missing", reason=f"bad live price {live_usd!r}"))
            continue
        if held:
            rows.append(Row(**base, landed_usd=None, target_usd=None, list_target_usd=None,
                            decision="skip-held", reason=held))
            continue
        if code == "S06":
            ok = live_usd == S06_LOCK_USD
            rows.append(Row(**base, landed_usd=None, target_usd=S06_LOCK_USD, list_target_usd=None,
                            decision="locked" if ok else "lock-drift",
                            reason=f"S06 stays ${S06_LOCK_USD}" + ("" if ok else f"; live is ${live_usd:g}")))
            continue
        missing = [label for label, v in (("kg", kg), ("intake ¥", intake)) if v is None]
        if missing:
            rows.append(Row(**base, landed_usd=None, target_usd=None, list_target_usd=None,
                            decision="skip-missing", reason="missing " + " and ".join(missing)))
            continue

        landed = landed_usd(intake, kg)
        target = price(landed)
        list_target = price(landed_usd(listed, kg)) if listed is not None else None
        if live_usd < target:
            decision, reason = "under", f"live ${live_usd:g} < target ${target} at intake ¥"
        elif list_target is not None and live_usd < list_target:
            decision, reason = "list-only", f"under only at public list ¥ (needs ${list_target}); not a raise"
        else:
            decision, reason = "ok", ""
        rows.append(Row(**base, landed_usd=_f(landed), target_usd=target,
                        list_target_usd=list_target, decision=decision, reason=reason))
    return rows


PRICED = ("ok", "list-only")


def headroom(rows: list[Row], pct: float = 0.0) -> tuple[list[dict], list[dict]]:
    """Return (no_headroom, band). band: 0 < live - target <= pct% of target."""
    if pct < 0:
        raise ValueError("--headroom-pct must be >= 0")
    zero: list[dict] = []
    band: list[dict] = []
    limit = Decimal(str(pct)) / 100
    for r in rows:
        if r.decision not in PRICED or r.target_usd is None:
            continue
        gap = Decimal(str(r.live_usd)) - Decimal(r.target_usd)
        item = {"ma": r.ma, "live_usd": r.live_usd, "target_usd": r.target_usd,
                "headroom_usd": float(gap), "headroom_pct": float(
                    (gap / Decimal(r.target_usd) * 100).quantize(Decimal("0.01"), ROUND_HALF_UP)),
                "decision": r.decision}
        if gap == 0:
            zero.append(item)
        elif 0 < gap <= Decimal(r.target_usd) * limit:
            band.append(item)
    return zero, band


def summarize(rows: list[Row], headroom_pct: float = 0.0) -> dict:
    by = lambda d: [r.ma for r in rows if r.decision == d]  # noqa: E731
    zero, band = headroom(rows, headroom_pct)
    return {
        "live_count": len(rows),
        "outcome": "UNDER_FOUND" if by("under") else "QUIET_OK",
        "under_target": [asdict(r) for r in rows if r.decision == "under"],
        "list_only": [asdict(r) for r in rows if r.decision == "list-only"],
        "skipped": [asdict(r) for r in rows if r.decision.startswith("skip")],
        "counts": {d: len(by(d)) for d in
                   ("under", "list-only", "ok", "locked", "lock-drift", "skip-held", "skip-missing")},
        "no_headroom": zero,
        "headroom_pct": headroom_pct,
        "headroom_band": band,
        "rows": [asdict(r) for r in rows],
        "writes": "none",
    }


def markdown(summary: dict, title: str = "Too-cheap check") -> str:
    c = summary["counts"]
    out = [f"# {title}", "", f"**Outcome: {summary['outcome']}** ({summary['live_count']} live mãs)", "",
           f"- Under target at intake ¥: {c['under']}",
           f"- List-only (public list ¥, not a raise): {c['list-only']}",
           f"- OK: {c['ok']}; S06 locked: {c['locked']}; lock drift: {c['lock-drift']}",
           f"- Skipped: held {c['skip-held']}, missing data {c['skip-missing']}", ""]
    for key, head in (("under_target", "Under target"), ("list_only", "List-only"), ("skipped", "Skipped")):
        out += [f"## {head}", ""]
        if not summary[key]:
            out += ["None.", ""]
            continue
        out += ["| mã | live $ | intake ¥ | list ¥ | kg | landed $ | target $ | list target $ | note |",
                "|---|---|---|---|---|---|---|---|---|"]
        for r in summary[key]:
            cells = [r["ma"], r["live_usd"], r["intake_cny"], r["list_cny"], r["kg"], r["landed_usd"],
                     r["target_usd"], r["list_target_usd"], r["reason"]]
            out.append("| " + " | ".join("" if v is None else f"{v:g}" if isinstance(v, float) else str(v)
                                        for v in cells) + " |")
        out.append("")
    pct = summary.get("headroom_pct", 0)
    for key, head in (("no_headroom", "No headroom (live = target)"),
                      ("headroom_band", f"Headroom warning band (≤ {pct:g}% above target)")):
        if key == "headroom_band" and not pct:
            continue
        rows = summary.get(key, [])
        out += [f"## {head}", ""]
        if not rows:
            out += ["None.", ""]
            continue
        out += [" ".join(r["ma"] for r in rows), "",
                "| mã | live $ | target $ | headroom $ | headroom % | decision |", "|---|---|---|---|---|---|"]
        out += [f"| {r['ma']} | {r['live_usd']:g} | {r['target_usd']} | {r['headroom_usd']:g} | "
                f"{r['headroom_pct']:g} | {r['decision']} |" for r in rows]
        out += ["", "Warning only. Not a price change.", ""]
    out.append("Read-only. No intake, Blob, hub, Square, Meta, or price writes.")
    return "\n".join(out) + "\n"


def load_live(path: Path) -> dict[str, float]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, dict) and "products" in data:
        return {norm_ma(p["ma"]): float(p["priceUsd"]) for p in data["products"]}
    if isinstance(data, dict) and "prices" in data:
        return {norm_ma(k): float(v) for k, v in data["prices"].items()}
    raise ValueError(f"{path}: expected a catalog with products[] or a prices map")


def load_costs(path: Path) -> dict[str, dict[str, str]]:
    """CSV with ma plus intake ¥ (intake_cny or baseline_cny), list ¥ (list_cny or recheck_cny), kg."""
    out: dict[str, dict[str, str]] = {}
    with path.open(encoding="utf-8-sig", newline="") as f:
        for r in csv.DictReader(f):
            ma = norm_ma((r.get("ma") or ""))
            if ma:
                out[ma] = {"intake_cny": r.get("intake_cny") or r.get("baseline_cny") or "",
                           "list_cny": r.get("list_cny") or r.get("recheck_cny") or "",
                           "kg": r.get("kg") or ""}
    return out


def load_weights(paths: list[Path]) -> dict[str, Decimal]:
    """Fallback kg CSVs (ma + kg or weight_kg). Earlier files win."""
    out: dict[str, Decimal] = {}
    for path in paths:
        with path.open(encoding="utf-8-sig", newline="") as f:
            for r in csv.DictReader(f):
                ma = norm_ma((r.get("ma") or ""))
                kg = _num(r.get("weight_kg") or r.get("kg"))
                if ma and kg is not None and ma not in out:
                    out[ma] = kg
    return out


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Read-only too-cheap check from local snapshots.")
    p.add_argument("--live", required=True, type=Path, help="Live catalog snapshot JSON (local file).")
    p.add_argument("--costs", required=True, type=Path, help="Cost CSV with Nhung intake ¥ and kg.")
    p.add_argument("--weights", action="append", type=Path, default=[], help="Fallback kg CSV (repeatable).")
    p.add_argument("--held-ts", type=Path, default=HELD_TS)
    p.add_argument("--out-md", type=Path)
    p.add_argument("--out-json", type=Path)
    p.add_argument("--title", default="Too-cheap check")
    p.add_argument("--headroom-pct", type=float, default=0.0,
                   help="Warn on priced mãs at most this %% above target (default 0: exact-target only).")
    a = p.parse_args(argv)
    if a.headroom_pct < 0:
        p.error("--headroom-pct must be >= 0")
    summary = summarize(evaluate(load_live(a.live), load_costs(a.costs), load_held_from_ts(a.held_ts),
                                 load_weights(a.weights)), a.headroom_pct)
    md = markdown(summary, a.title)
    if a.out_md:
        a.out_md.write_text(md, encoding="utf-8")
    if a.out_json:
        a.out_json.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if not a.out_md:
        print(md, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
