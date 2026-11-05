#!/usr/bin/env python3
"""Caption gap watch (piece 48): READ-ONLY, WARN-only.

Reads a SAVED export of FB/IG post captions (JSON list of
{"id", "platform", "caption"} or a text file with blocks separated by
lines "=== <post id>") and flags:
  missing_caption  post has no caption text at all
  missing_ma       caption has no "Mã XXX" line
  missing_gia      caption has no Giá
  gia_differs      Giá disagrees with the approved/live price list
Output is post id, mã and issue ONLY. It never suggests deleting or
reposting; fixes are edits of the original post, and Boss's call.
No Meta calls, no network, no writes.
Exit: 0 clean, 1 WARN, 2 usage/input error.
"""
from __future__ import annotations

import argparse
import json
import math
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import caption_lint as _cl  # noqa: E402
from held_policy import norm_ma  # noqa: E402

ISSUES = ("missing_caption", "missing_ma", "missing_gia", "gia_differs")
ID_RE = re.compile(r"^[A-Za-z0-9_.:-]{1,80}$")
MA_RE = re.compile(r"^[A-Z]{1,2}\d{2,3}$")
S06_LOCK = 25.0


def load_posts(path: Path) -> list[dict]:
    raw = Path(path).read_text(encoding="utf-8")
    if Path(path).suffix.lower() == ".json":
        d = json.loads(raw)
        d = d.get("posts", []) if isinstance(d, dict) else d
        if not isinstance(d, list):
            raise ValueError("posts must be a list")
        return [{"id": str(p.get("id", "")), "platform": str(p.get("platform", "")),
                 "caption": p.get("caption") or ""} for p in d if isinstance(p, dict)]
    posts, cur = [], None
    for ln in raw.splitlines():
        m = re.match(r"^===\s*(\S+)\s*(\S*)\s*$", ln)
        if m:
            cur = {"id": m.group(1), "platform": m.group(2), "caption": ""}
            posts.append(cur)
        elif cur is not None:
            cur["caption"] += ln + "\n"
    return posts


def _usd(value: object) -> float | None:
    """A finite dollar amount. A boolean, a blank, or junk text is absent."""
    if isinstance(value, bool) or value is None:
        return None
    if isinstance(value, str):
        text = value.strip()
        if not text:
            return None
        try:
            value = float(text)
        except ValueError:
            return None
    if isinstance(value, (int, float)) and math.isfinite(float(value)):
        return float(value)
    return None


def _key(raw: object) -> str | None:
    if not isinstance(raw, str):
        return None
    code = norm_ma(raw)
    return code if code and MA_RE.fullmatch(code) else None


def _price_items(data: object):
    if not isinstance(data, dict):
        raise ValueError("price file must be an object")
    approved = data.get("approvedGia")
    if isinstance(approved, dict):
        return list(approved.items())
    products = data.get("products")
    if isinstance(products, list):
        rows = []
        for row in products:
            if isinstance(row, dict):
                rows.append((row.get("ma"), row.get("priceUsd")))
        return rows
    prices = data.get("prices")
    if isinstance(prices, dict):
        return list(prices.items())
    return list(data.items())


def load_prices(*paths: Path | None) -> dict[str, float]:
    """Merge price files. Later files win. A short or padded mã uses the shop key. S06 stays $25."""
    out: dict[str, float] = {}
    for p in paths:
        if not p:
            continue
        data = json.loads(Path(p).read_text(encoding="utf-8"))
        for raw_key, raw_usd in _price_items(data):
            code = _key(raw_key)
            usd = _usd(raw_usd)
            if code and usd is not None:
                out[code] = usd
    out["S06"] = S06_LOCK
    return out


def check_post(post: dict, prices: dict[str, float]) -> list[dict]:
    pid = post["id"] if ID_RE.match(post.get("id", "")) else "invalid_id"
    text = _cl.clean_caption(post.get("caption", ""))
    if not text.strip():
        return [{"post": pid, "ma": None, "issue": "missing_caption"}]
    found, _ = _cl.find_ma(text)
    code = norm_ma(found) if found else ""
    ma = code if MA_RE.fullmatch(code) else None
    gia, _, _ = _cl.find_gia(text)
    out = []
    if ma is None:
        out.append({"post": pid, "ma": None, "issue": "missing_ma"})
    if gia is None:
        out.append({"post": pid, "ma": ma, "issue": "missing_gia"})
    elif ma and ma in prices and abs(gia - prices[ma]) > 0.005:
        out.append({"post": pid, "ma": ma, "issue": "gia_differs"})
    return out


def run(posts: list[dict], prices: dict[str, float]) -> dict:
    flags = [f for p in posts for f in check_post(p, prices)]
    return {"schema": "caption-gap-watch/v1", "piece": 48, "posts": len(posts),
            "flags": flags, "byIssue": {k: [f["post"] for f in flags if f["issue"] == k] for k in ISSUES},
            "writes": "none", "network": "none",
            "note": "WARN only; edit the original post only, Boss's call"}


def warn_lines(rep: dict) -> list[str]:
    return [f"{f['post']} {f['ma'] or '-'}: {f['issue']}" for f in rep["flags"]]


def markdown(rep: dict) -> str:
    out = [f"# Caption gap watch: {'WARN' if rep['flags'] else 'PASS'} ({rep['posts']} posts)", ""]
    out += [f"- {ln}" for ln in warn_lines(rep)] or ["- no gaps"]
    out += ["", "Post id, mã and issue only. Read-only; no Meta calls."]
    return "\n".join(out) + "\n"


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("export", type=Path, help="saved captions export (.json or text)")
    p.add_argument("--live", type=Path, help="live price list JSON {mã: usd}")
    p.add_argument("--approved", type=Path, help="approved-held-gia.json")
    p.add_argument("--json", action="store_true")
    a = p.parse_args(argv)
    try:
        rep = run(load_posts(a.export), load_prices(a.live, a.approved))
    except Exception as e:  # noqa: BLE001
        print(f"error: {type(e).__name__}", file=sys.stderr)
        return 2
    print(json.dumps(rep, indent=2, ensure_ascii=False) if a.json else markdown(rep), end="" if not a.json else "\n")
    return 1 if rep["flags"] else 0


if __name__ == "__main__":
    sys.exit(main())
