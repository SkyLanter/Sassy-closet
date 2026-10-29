"""Report-only list of intake mãs missing data needed to go live.

Reads an intake export (``{"submissions": [...]}``, ``{"items": [...]}``, or a bare list), the public catalog
snapshot (catalog.v1 ``{"products": [...]}`` or ``{"prices": {mã: $}}``),
data/held.json, and optional per-mã kg CSVs. It never writes intake, Blob,
Square, Meta, or a price, and it never "fixes" a Nhung intake value. Bad
values are copied into the report as stored (Boss rule: flag, don't fix).

Gap types (one row per mã, any number of gaps):
  cny       blank or garbled intake ¥ cost
  kg        no kg; shows a category proxy (A 0.3, H 0.08) or a CSV estimate
            when one exists. G shoes have no approved weight: "G needs Boss".
  size      clothing/shoe kind with no size, or a size token not allowed
            for the kind
  photos    no intake photo_paths (and, for live mãs, no catalog images)
  link      no Taobao link, or a link that is not Taobao/Tmall
  category  blank/unknown kind, or kind not matching the mã letter
Suspect costs (report only):
  sell_vs_live   intake sell $ differs from the live catalog $
  cny_label      a $ cost stored with cost_currency "CNY"
  no_usd_cost    blank $ cost
  usd_vs_cny     $ cost disagrees with ¥/6.723 by more than 5%
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from decimal import Decimal, InvalidOperation
from pathlib import Path

from held_policy import load_held_policy, norm_ma
from intake_flags import IntakeRow, flag_intake

FX_CNY_PER_USD = Decimal("6.723")
MA_RE = re.compile(r"^([A-Z])[0-9]{2}$")
# Approved category kg proxies (same as the held price sheet). G has none.
CATEGORY_KG_PROXY: dict[str, Decimal] = {"A": Decimal("0.3"), "H": Decimal("0.08")}
NEEDS_BOSS_KG = frozenset({"G"})
SIZED_KINDS = frozenset({"A", "Q", "V", "D", "K", "S", "G"})
DEFAULT_SIZES = ("2XS", "XS", "S", "M", "L", "XL", "2XL")
TAOBAO_RE = re.compile(r"^https?://([a-z0-9-]+\.)*(tb\.cn|taobao\.com|tmall\.com)(/|$)", re.I)
USD_TOLERANCE = Decimal("0.05")
GAP_TYPES = ("cny", "kg", "size", "photos", "link", "category")
SUSPECT_TYPES = ("sell_vs_live", "cny_label", "no_usd_cost", "usd_vs_cny")
GROUPS = ("held", "not live", "live")


def _num(value: object) -> Decimal | None:
    if value is None:
        return None
    text = str(value).strip().replace("$", "")
    if not text:
        return None
    try:
        n = Decimal(text)
    except InvalidOperation:
        return None
    return n if n.is_finite() else None


def _txt(d: Decimal) -> str:
    s = format(d.normalize(), "f")
    return s


def kind_sizes(intake_catalog: dict | None) -> dict[str, tuple[str, ...]]:
    out: dict[str, tuple[str, ...]] = {}
    for k in (intake_catalog or {}).get("kinds", []) or []:
        code = str(k.get("code", "")).strip().upper()
        if code:
            out[code] = tuple(str(s).upper() for s in k.get("sizes") or ())
    return out


def kg_gap(code: str, kind: str, row: dict, weights: dict[str, tuple[Decimal, str]]) -> dict | None:
    if _num(row.get("kg") or row.get("weight_kg")) is not None:
        return None
    w = weights.get(code)
    if w is not None and w[1] == "real":
        return None
    if kind in NEEDS_BOSS_KG:
        return {"type": "kg", "detail": f"no kg; no approved {kind} weight — {kind} needs Boss"}
    if w is not None:
        return {"type": "kg", "detail": f"no measured kg; estimate {_txt(w[0])} kg ({w[1]}) from weights csv"}
    if kind in CATEGORY_KG_PROXY:
        return {"type": "kg", "detail": f"no measured kg; {kind} category proxy {_txt(CATEGORY_KG_PROXY[kind])} kg"}
    return {"type": "kg", "detail": "no kg and no category proxy"}


def row_gaps(row: dict, live: dict[str, dict], weights, sizes_by_kind) -> tuple[list[dict], list[dict]]:
    code = norm_ma(str(row.get("ma", "")))
    kind = str(row.get("kind", "") or "").strip().upper()
    gaps: list[dict] = []
    sus: list[dict] = []

    stored_cny = row.get("cost_cny")
    for f in flag_intake([IntakeRow(code, None if stored_cny is None else str(stored_cny))]):
        gaps.append({"type": "cny", "detail": f"{f.kind.replace('_', ' ')} (stored {f.stored!r})"})

    m = MA_RE.fullmatch(code)
    if not kind:
        gaps.append({"type": "category", "detail": "blank kind"})
    elif sizes_by_kind and kind not in sizes_by_kind:
        gaps.append({"type": "category", "detail": f"unknown kind {kind!r}"})
    elif m and m.group(1) != kind:
        gaps.append({"type": "category", "detail": f"kind {kind} does not match mã letter {m.group(1)}"})

    kgg = kg_gap(code, kind, row, weights)
    if kgg:
        gaps.append(kgg)

    if kind in SIZED_KINDS:
        tokens = str(row.get("size") or "").replace(",", " ").split()
        if not tokens:
            gaps.append({"type": "size", "detail": "no size"})
        else:
            allowed = set(sizes_by_kind.get(kind) or DEFAULT_SIZES)
            bad = [t for t in tokens if t.upper() not in allowed]
            if bad:
                gaps.append({"type": "size", "detail": f"size not allowed for {kind}: {' '.join(bad)}"})

    photos = [p for p in (row.get("photo_paths") or []) if str(p).strip()]
    if not photos:
        detail = "no intake photos"
        if code in live and not live[code].get("images"):
            detail += "; no catalog images"
        gaps.append({"type": "photos", "detail": detail})

    link = str(row.get("link") or "").strip()
    if not link:
        gaps.append({"type": "link", "detail": "no Taobao link"})
    elif not TAOBAO_RE.match(link):
        gaps.append({"type": "link", "detail": f"not a Taobao/Tmall link: {link}"})

    # suspect costs
    sell = _num(row.get("sell_usd"))
    if code in live and sell is not None and live[code].get("price") is not None:
        lp = live[code]["price"]
        if sell != lp:
            sus.append({"type": "sell_vs_live", "detail": f"intake ${_txt(sell)} vs live ${_txt(lp)}"})
    usd = _num(row.get("cost_usd"))
    cur = str(row.get("cost_currency") or "").strip().upper()
    if usd is not None and cur == "CNY":
        sus.append({"type": "cny_label", "detail": f"$ cost {row.get('cost_usd')} labeled CNY"})
    if usd is None:
        sus.append({"type": "no_usd_cost", "detail": f"blank $ cost (stored {row.get('cost_usd')!r})"})
    cny = _num(stored_cny)
    if usd is not None and cny is not None and cny > 0:
        expect = cny / FX_CNY_PER_USD
        if abs(usd - expect) > expect * USD_TOLERANCE:
            sus.append({"type": "usd_vs_cny",
                        "detail": f"$ {row.get('cost_usd')} vs ¥{stored_cny}/6.723 = {expect.quantize(Decimal('0.01'))}"})
    return gaps, sus


def intake_rows(intake: object) -> tuple[list[dict], dict | None]:
    """Normalize intake to (rows, catalog). Accepts a bare list of rows or an
    object with a ``submissions`` (or ``items``) list. Non-dict rows are dropped;
    any other shape yields no rows (never crashes)."""
    catalog = None
    if isinstance(intake, list):
        raw = intake
    elif isinstance(intake, dict):
        cat = intake.get("catalog")
        catalog = cat if isinstance(cat, dict) else None
        raw = intake.get("submissions")
        if not isinstance(raw, list):
            raw = intake.get("items")
        if not isinstance(raw, list):
            raw = []
    else:
        raw = []
    return [r for r in raw if isinstance(r, dict)], catalog


def build(intake: dict | list, live: dict[str, dict], held: set[str], weights=None) -> dict:
    weights = weights or {}
    subs, catalog = intake_rows(intake)
    sizes = kind_sizes(catalog)
    rows = []
    for r in subs:
        code = norm_ma(str(r.get("ma", "")))
        if not code:
            continue
        gaps, sus = row_gaps(r, live, weights, sizes)
        group = "held" if code in held else ("live" if code in live else "not live")
        rows.append({"ma": code, "kind": str(r.get("kind") or "").upper(), "group": group,
                     "gaps": gaps, "suspect": sus})
    counts = {g: {"mas": 0, "with_gaps": 0, "with_suspect": 0} for g in GROUPS}
    by_type = {t: [] for t in GAP_TYPES + SUSPECT_TYPES}
    for x in rows:
        c = counts[x["group"]]
        c["mas"] += 1
        c["with_gaps"] += bool(x["gaps"])
        c["with_suspect"] += bool(x["suspect"])
        for g in x["gaps"] + x["suspect"]:
            if x["ma"] not in by_type[g["type"]]:
                by_type[g["type"]].append(x["ma"])
    return {"report_only": True, "writes": "none (named outputs only)",
            "intake_mas": len(rows), "counts": counts, "by_type": by_type, "rows": rows}


def markdown(rep: dict) -> str:
    out = ["# Intake gaps (report only — nothing fixed)", "",
           f"{rep['intake_mas']} intake mãs. Bad Nhung values are shown as stored; Boss decides.", "",
           "| type | count | mãs |", "|---|---|---|"]
    for t, mas in rep["by_type"].items():
        out.append(f"| {t} | {len(mas)} | {' '.join(mas) or '—'} |")
    for g in GROUPS:
        c = rep["counts"][g]
        out += ["", f"## {g} ({c['mas']} mãs, {c['with_gaps']} with gaps, {c['with_suspect']} suspect)", "",
                "| mã | gaps | suspect costs |", "|---|---|---|"]
        for x in rep["rows"]:
            if x["group"] != g or not (x["gaps"] or x["suspect"]):
                continue
            gs = "; ".join(f"{a['type']}: {a['detail']}" for a in x["gaps"]) or "—"
            ss = "; ".join(f"{a['type']}: {a['detail']}" for a in x["suspect"]) or "—"
            out.append(f"| {x['ma']} | {gs} | {ss} |")
    return "\n".join(out) + "\n"


def load_live(path: Path | None) -> dict[str, dict]:
    if path is None:
        return {}
    d = json.loads(path.read_text(encoding="utf-8"))
    out: dict[str, dict] = {}
    if isinstance(d.get("products"), list):
        for p in d["products"]:
            if str(p.get("status", "available")).lower() in {"hidden", "draft", "deleted"}:
                continue
            code = norm_ma(str(p.get("ma", "")))
            if code:
                out[code] = {"price": _num(p.get("priceUsd")), "images": p.get("images") or []}
    elif isinstance(d.get("prices"), dict):
        for k, v in d["prices"].items():
            out[norm_ma(k)] = {"price": _num(v), "images": None}
    return out


def load_weights(paths: list[Path]) -> dict[str, tuple[Decimal, str]]:
    out: dict[str, tuple[Decimal, str]] = {}
    for p in paths:
        with p.open(encoding="utf-8-sig", newline="") as f:
            for r in csv.DictReader(f):
                code = norm_ma(str(r.get("ma", "")))
                kg = _num(r.get("weight_kg") or r.get("kg"))
                if code and kg is not None and code not in out:
                    out[code] = (kg, str(r.get("kg_type") or "csv").strip() or "csv")
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--intake", type=Path, required=True)
    ap.add_argument("--live-catalog", type=Path)
    ap.add_argument("--held", type=Path, help="held.json (default data/held.json)")
    ap.add_argument("--weights", type=Path, action="append", default=[])
    ap.add_argument("--out-md", type=Path)
    ap.add_argument("--out-json", type=Path)
    a = ap.parse_args(argv)
    pol = load_held_policy(a.held)
    rep = build(json.loads(a.intake.read_text(encoding="utf-8")), load_live(a.live_catalog),
                set(pol.held) | set(pol.never_list), load_weights(a.weights))
    md = markdown(rep)
    if a.out_md:
        a.out_md.write_text(md, encoding="utf-8")
    if a.out_json:
        a.out_json.write_text(json.dumps(rep, ensure_ascii=False, indent=1, default=str) + "\n", encoding="utf-8")
    if not a.out_md and not a.out_json:
        sys.stdout.write(md)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
