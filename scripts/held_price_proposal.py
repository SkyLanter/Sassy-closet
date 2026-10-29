"""Boss approval sheet for held / unpriced mãs. Read-only.

For each intake mã that has no approved sell price (absent from the live
price map) or sits in data/held.json heldIncomplete, this builds a proposal:

    landed = intake ¥ / 6.723 + 10.52 * kg
    tiered = autolist.price(landed)          (main's tiered fixed point)
    flat   = ceil(landed / 0.75), +$2 under $10   (old flat 25% quote)

Both quotes are shown side by side. Nothing is approved here.
- Missing intake ¥, missing kg, or a kind with no approved weight proxy
  (G shoes) is flagged and gets no quote. No ¥ or kg is guessed.
- neverList mãs (data/held.json, same source as lib/held-incomplete.ts)
  are excluded. S06 is excluded (locked $25).
- It writes only the --out-md / --out-json files it is given. It does not
  touch intake, Blob, the hub, Square, Meta, or any price.
Standalone: does not import scripts/too_cheap_check.py (piece 17).

Each proposal carries a verdict: "$N" (tiered sell to approve), NEEDS_INPUT
(blank/unusable ¥ or no approved kg), or ALREADY_LIVE. --proposal-dir DIR
writes dated md+json there; use out/proposals/ (gitignored).

Optional --live-catalog FILE: a read-only snapshot of the public live catalog
(catalog.v1 {products: [{ma, priceUsd, status}]} or a {prices: {mã: $}} map).
A selected mã that is already priced in it is marked "already live $X" and
gets no new quote, so a stale --live map cannot re-quote a live item.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
from dataclasses import asdict, dataclass, field
from decimal import Decimal, InvalidOperation
from pathlib import Path

from autolist import S06_LOCK_USD, UNDER_TEN, UNDER_TEN_BUMP, price
from held_policy import HeldPolicy, load_held_policy, norm_ma

FX_CNY_PER_USD = Decimal("6.723")
SHIP_USD_PER_KG = Decimal("10.52")
FLAT_MARGIN = Decimal("0.25")

# Category kg proxies used by the Oct 20 midnight QC price suggestions.
# They are proxies, not measured weights. G (shoes) has no approved proxy:
# Boss must set one. Override with --kg-proxy KIND=KG.
DEFAULT_KG_PROXY: dict[str, Decimal] = {"A": Decimal("0.3"), "H": Decimal("0.08")}
NEEDS_BOSS_WEIGHT_KINDS = frozenset({"G"})


def landed_usd(yen: Decimal, kg: Decimal) -> Decimal:
    return yen / FX_CNY_PER_USD + SHIP_USD_PER_KG * kg


def flat_quote(landed: Decimal) -> int:
    q = math.ceil(landed / (1 - FLAT_MARGIN))
    return q + UNDER_TEN_BUMP if q < UNDER_TEN else q


def _num(value: object) -> Decimal | None:
    if value is None:
        return None
    text = str(value).strip().replace("¥", "").replace("$", "")
    if not text:
        return None
    try:
        n = Decimal(text)
    except InvalidOperation:
        return None
    return n if n.is_finite() and n > 0 else None


@dataclass
class Proposal:
    ma: str
    kind: str
    status: str  # "quote" | "needs-boss" | "already-live"
    intake_cny: str
    kg: float | None
    kg_source: str | None
    landed_usd: float | None
    tiered_usd: int | None
    flat25_usd: int | None
    flags: list[str] = field(default_factory=list)
    live_usd: float | None = None
    verdict: str = ""  # "$N" proposed tiered sell, NEEDS_INPUT, or ALREADY_LIVE


def select(rows: list[dict], live: dict[str, object], policy: HeldPolicy) -> list[dict]:
    """Held or unpriced intake rows; never-list and S06 excluded."""
    out, seen = [], set()
    for r in rows:
        code = norm_ma(str(r.get("ma", "")))
        if not code or code in seen:
            continue
        seen.add(code)
        reason = policy.skip_reason(code)
        if reason == "never-list" or code == "S06":
            continue
        if reason == "held" or code not in live:
            out.append(r)
    return out


def propose(
    row: dict,
    policy: HeldPolicy,
    weights: dict[str, Decimal] | None = None,
    kg_proxy: dict[str, Decimal] | None = None,
) -> Proposal:
    weights = weights or {}
    kg_proxy = DEFAULT_KG_PROXY if kg_proxy is None else kg_proxy
    code = norm_ma(str(row["ma"]))
    kind = str(row.get("kind") or code[:1]).strip().upper()
    raw_cny = str(row.get("cost_cny") or "").strip()
    flags: list[str] = []
    if policy.skip_reason(code) == "held":
        flags.append("held incomplete")
    yen = _num(raw_cny)
    if yen is None:
        flags.append("missing intake ¥" if not raw_cny else f"intake ¥ not usable ({raw_cny})")
    kg, src = _num(row.get("kg")), "intake"
    if kg is None and code in weights:
        kg, src = weights[code], "weights csv"
    if kg is None and kind in kg_proxy:
        kg, src = kg_proxy[kind], f"{kind} category proxy"
    if kg is None:
        src = None
        if kind in NEEDS_BOSS_WEIGHT_KINDS:
            flags.append(f"no approved {kind} weight; Boss must set kg")
        else:
            flags.append("missing kg (no category proxy)")
    if yen is None or kg is None:
        return Proposal(code, kind, "needs-boss", raw_cny, float(kg) if kg else None, src,
                        None, None, None, flags)
    landed = landed_usd(yen, kg)
    return Proposal(code, kind, "quote", raw_cny, float(kg), src,
                    float(landed.quantize(Decimal("0.0001"))), price(landed), flat_quote(landed), flags)


def mark_live(p: Proposal, live_catalog: dict[str, Decimal]) -> Proposal:
    """Replace the quote with 'already live $X' when the mã is priced live."""
    usd = live_catalog.get(p.ma)
    if usd is None:
        return p
    text = f"{usd:f}".rstrip("0").rstrip(".") if "." in f"{usd:f}" else f"{usd:f}"
    p.status, p.live_usd = "already-live", float(usd)
    p.tiered_usd = p.flat25_usd = None
    p.flags = [f"already live ${text}"] + [f for f in p.flags if not f.startswith("already live")]
    return p


def verdict(p: Proposal) -> str:
    """Boss-facing one-word status: proposed tiered $, NEEDS_INPUT, or ALREADY_LIVE."""
    if p.status == "already-live":
        return "ALREADY_LIVE"
    if p.status != "quote" or p.tiered_usd is None:
        return "NEEDS_INPUT"
    return f"${p.tiered_usd}"


def build(rows, live, policy, weights=None, kg_proxy=None, live_catalog=None) -> dict:
    props = [propose(r, policy, weights, kg_proxy) for r in select(rows, live, policy)]
    if live_catalog is not None:
        props = [mark_live(p, live_catalog) for p in props]
    for p in props:
        p.verdict = verdict(p)
    return {
        "method": "landed = ¥/6.723 + 10.52*kg; tiered = autolist.price (main); flat = ceil(landed/0.75), +$2 under $10",
        "approved": False,
        "s06_lock_usd": S06_LOCK_USD,
        "count": len(props),
        "live_catalog_used": live_catalog is not None,
        "needs_boss": [p.ma for p in props if p.status == "needs-boss"],
        "verdicts": {p.ma: p.verdict for p in props},
        "already_live": {p.ma: p.live_usd for p in props if p.status == "already-live"},
        "proposals": [asdict(p) for p in props],
    }


def markdown(sheet: dict) -> str:
    out = ["# Held price proposal: Boss approval sheet", "",
           "Proposal only. Nothing is priced, listed, or written live.", "",
           f"Method: {sheet['method']}", "",
           "| mã | intake ¥ | kg (source) | landed $ | tiered $ | flat 25% $ | flags | Boss OK? |",
           "|---|---|---|---|---|---|---|---|"]
    for p in sheet["proposals"]:
        kg = f"{p['kg']} ({p['kg_source']})" if p["kg"] is not None else "—"
        cells = [p["ma"], p["intake_cny"] or "—", kg,
                 f"{p['landed_usd']:.2f}" if p["landed_usd"] is not None else "—",
                 p["tiered_usd"] if p["tiered_usd"] is not None
                 else (f"already live ${p['live_usd']:g}" if p.get("live_usd") is not None else "—"),
                 p["flat25_usd"] if p["flat25_usd"] is not None else "—",
                 "; ".join(p["flags"]) or "—", "☐"]
        out.append("| " + " | ".join(str(c) for c in cells) + " |")
    out += ["", "Verdicts: " + (", ".join(f"{m} {v}" for m, v in sheet.get("verdicts", {}).items()) or "none")]
    out += [f"Needs Boss input before any quote: {', '.join(sheet['needs_boss']) or 'none'}"]
    if sheet.get("live_catalog_used"):
        live = sheet.get("already_live") or {}
        out.append("Already live (not quoted): " + (", ".join(f"{m} ${v:g}" for m, v in live.items()) or "none"))
    out.append("")
    return "\n".join(out)


def load_intake(path: Path) -> list[dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, dict):
        data = data.get("submissions", data.get("rows", []))
    if not isinstance(data, list):
        raise ValueError(f"{path}: expected a list of intake rows or {{submissions: [...]}}")
    return data


def load_live(path: Path) -> dict[str, object]:
    data = json.loads(path.read_text(encoding="utf-8"))
    prices = data.get("prices", data) if isinstance(data, dict) else {}
    return {norm_ma(str(k)): v for k, v in prices.items() if v not in (None, "")}


def load_live_catalog(path: Path) -> dict[str, Decimal]:
    """Priced mãs from a public catalog snapshot. Read-only; no network."""
    data = json.loads(path.read_text(encoding="utf-8"))
    out: dict[str, Decimal] = {}
    if isinstance(data, dict) and isinstance(data.get("products"), list):
        for prod in data["products"]:
            ma = norm_ma(str(prod.get("ma") or ""))
            if str(prod.get("status") or "available").lower() in {"hidden", "draft", "deleted"}:
                continue
            usd = _num(prod.get("priceUsd"))
            if ma and usd is not None:
                out[ma] = usd
        return out
    prices = data.get("prices", data) if isinstance(data, dict) else None
    if not isinstance(prices, dict):
        raise ValueError(f"{path}: expected catalog.v1 {{products: [...]}} or {{prices: {{...}}}}")
    for k, v in prices.items():
        usd = _num(v)
        if usd is not None:
            out[norm_ma(str(k))] = usd
    return out


def load_weights(paths: list[Path]) -> dict[str, Decimal]:
    out: dict[str, Decimal] = {}
    for p in paths:
        with p.open(encoding="utf-8-sig", newline="") as fh:
            for r in csv.DictReader(fh):
                ma = norm_ma((r.get("ma") or ""))
                kg = _num(r.get("weight_kg") or r.get("kg"))
                if ma and kg is not None and ma not in out:
                    out[ma] = kg
    return out


def parse_proxy(items: list[str]) -> dict[str, Decimal] | None:
    if not items:
        return None
    out = dict(DEFAULT_KG_PROXY)
    for item in items:
        kind, _, kg = item.partition("=")
        n = _num(kg)
        if not kind or n is None:
            raise SystemExit(f"bad --kg-proxy {item!r}; use KIND=KG")
        out[kind.strip().upper()] = n
    return out


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Read-only Boss approval sheet for held/unpriced mãs.")
    p.add_argument("--intake", required=True, type=Path, help="Intake export JSON (submissions list).")
    p.add_argument("--live", required=True, type=Path, help="Live price map JSON ({prices: {mã: $}}).")
    p.add_argument("--held", type=Path, default=None, help="held.json (default data/held.json).")
    p.add_argument("--weights", action="append", type=Path, default=[], help="Per-mã kg CSV.")
    p.add_argument("--kg-proxy", action="append", default=[], help="KIND=KG override, repeatable.")
    p.add_argument("--live-catalog", type=Path, default=None,
                   help="Optional public live catalog snapshot; priced mãs are marked 'already live $X'.")
    p.add_argument("--only", default="", help="Comma list of mãs to keep.")
    p.add_argument("--out-md", type=Path)
    p.add_argument("--out-json", type=Path)
    p.add_argument("--proposal-dir", type=Path, default=None,
                   help="Write held-price-proposal-<date>.md/.json here (use out/proposals, gitignored).")
    p.add_argument("--date", default=None, help="Date stamp for --proposal-dir files (default today).")
    a = p.parse_args(argv)
    if a.proposal_dir:
        import datetime as _dt
        from zoneinfo import ZoneInfo
        stamp = a.date or _dt.datetime.now(_dt.timezone.utc).astimezone(ZoneInfo("America/Los_Angeles")).date().isoformat()
        a.proposal_dir.mkdir(parents=True, exist_ok=True)
        a.out_md = a.out_md or a.proposal_dir / f"held-price-proposal-{stamp}.md"
        a.out_json = a.out_json or a.proposal_dir / f"held-price-proposal-{stamp}.json"
    rows = load_intake(a.intake)
    if a.only:
        keep = {norm_ma(m) for m in a.only.split(",") if m.strip()}
        rows = [r for r in rows if norm_ma(str(r.get("ma", ""))) in keep]
    sheet = build(rows, load_live(a.live), load_held_policy(a.held),
                  load_weights(a.weights), parse_proxy(a.kg_proxy),
                  load_live_catalog(a.live_catalog) if a.live_catalog else None)
    md = markdown(sheet)
    if a.out_md:
        a.out_md.write_text(md, encoding="utf-8")
    if a.out_json:
        a.out_json.write_text(json.dumps(sheet, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if not a.out_md and not a.out_json:
        print(md)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
