#!/usr/bin/env python3
"""Export a cost-free daily snapshot into data/daily-inputs/ for the reduced daily check.

Allow-list only. Each item keeps exactly: mã code, live yes/no, public $ sell
price (live mãs only), held flag. Check outcomes keep only section name and
status (no detail text). Nothing else from the inputs is copied: no Nhung ¥/$
buy prices, no source links, no titles, photos or buyer data. The output is
re-scanned for banned terms before it is written; any hit aborts with exit 2
and nothing is written.

Read-only on inputs. No network. Writes ONLY snapshot.json inside a folder
named daily-inputs (default data/daily-inputs/).

Exit: 0 written, 2 usage/input error or privacy guard tripped.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from held_policy import norm_ma

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT = ROOT / "data" / "daily-inputs"
MA_RE = re.compile(r"^[A-Z]{1,2}\d{2,3}$")
STATUS_OK = {"PASS", "WARN", "FAIL", "SKIP", "SKIP-NO-COSTS"}
SCHEMA = "daily-inputs/v1"
BANNED = re.compile("|".join([r"\u00a5", "cny", "cost", "taobao", "1688", "supplier",
                              "http", "phone", "email", "@", r"tb\.cn"]), re.I)
LIVE_STATUSES = {"available", "live", "active", "in_stock", "instock"}


class ExportError(Exception):
    pass


def _ma(v) -> str:
    m = norm_ma(str(v or ""))
    if not MA_RE.match(m):
        raise ExportError(f"bad mã code {v!r}")
    return m


def _price(v):
    try:
        x = float(v)
    except (TypeError, ValueError):
        return None
    if x != x or x <= 0 or x > 10000:
        return None
    return int(x) if x.is_integer() else round(x, 2)


def load_live(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or not isinstance(data.get("products"), list):
        raise ExportError(f"{path.name}: expected a catalog with products[]")
    out = {}
    for p in data["products"]:
        if str(p.get("status", "available")).lower() not in LIVE_STATUSES:
            continue
        out[_ma(p.get("ma"))] = _price(p.get("priceUsd"))
    return out


def load_held(path: Path) -> set:
    data = json.loads(path.read_text(encoding="utf-8"))
    return {_ma(m) for m in data.get("heldIncomplete", []) + data.get("neverList", [])}


def load_intake_mas(path) -> set:
    if not path:
        return set()
    data = json.loads(path.read_text(encoding="utf-8"))
    subs = data.get("submissions", []) if isinstance(data, dict) else data
    out = set()
    for r in subs:
        try:
            out.add(_ma(r.get("ma")))
        except ExportError:
            continue  # rows without a usable mã are not exported
    return out


def load_checks(path):
    if not path:
        return None, []
    data = json.loads(path.read_text(encoding="utf-8"))
    secs = data.get("sections", [])
    if isinstance(secs, dict):
        secs = [{"name": k, **(v if isinstance(v, dict) else {"status": v})} for k, v in secs.items()]
    checks = []
    for s in secs:
        name, st = str(s.get("name", "")), str(s.get("status", "")).upper()
        if not re.fullmatch(r"[a-z_]{1,40}", name) or st not in STATUS_OK:
            raise ExportError(f"bad check entry {name!r}/{st!r}")
        checks.append({"name": name, "status": st})
    overall = str(data.get("overall", "")).upper()
    if overall not in STATUS_OK:
        raise ExportError(f"bad overall {overall!r}")
    return overall, checks


def build(date, live, held, intake, overall, checks) -> dict:
    items = [{"ma": m, "live": m in live, "sellUsd": live.get(m) if m in live else None, "held": m in held}
             for m in sorted(set(live) | held | intake)]
    snap = {"schema": SCHEMA, "date": date, "items": items,
            "counts": {"mas": len(items), "live": sum(i["live"] for i in items),
                       "held": sum(i["held"] for i in items)}}
    if checks:
        snap["checks"] = checks
        snap["overall"] = overall
    return snap


def privacy_scan(text: str) -> list:
    return sorted({m.group(0).lower() for m in BANNED.finditer(text)})


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--live", required=True, type=Path, help="public catalog JSON (products[])")
    p.add_argument("--held", type=Path, default=ROOT / "data" / "held.json")
    p.add_argument("--intake", type=Path, help="intake export; ONLY mã codes are read")
    p.add_argument("--report", type=Path, help="daily_shop_check JSON; ONLY section name/status kept")
    p.add_argument("--date", required=True)
    p.add_argument("--out-dir", type=Path, default=DEFAULT_OUT)
    a = p.parse_args(argv)
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", a.date):
        p.error(f"bad --date {a.date}")
    if a.out_dir.name != "daily-inputs":
        p.error("--out-dir must be a folder named daily-inputs")
    try:
        overall, checks = load_checks(a.report)
        snap = build(a.date, load_live(a.live), load_held(a.held), load_intake_mas(a.intake), overall, checks)
    except (ExportError, OSError, ValueError, AttributeError) as e:
        print(f"export_daily_inputs: {e}", file=sys.stderr)
        return 2
    text = json.dumps(snap, indent=2, ensure_ascii=False) + "\n"
    hits = privacy_scan(text)
    if hits:
        print(f"export_daily_inputs: privacy guard tripped {hits}; nothing written", file=sys.stderr)
        return 2
    a.out_dir.mkdir(parents=True, exist_ok=True)
    out = a.out_dir / "snapshot.json"
    out.write_text(text, encoding="utf-8")
    c = snap["counts"]
    print(f"wrote {out} ({c['mas']} mã, {c['live']} live, {c['held']} held)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
