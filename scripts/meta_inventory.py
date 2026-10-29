"""Offline FB+IG post inventory reconciler for Sassy Closet (piece 35).

Reads an export of FB+IG posts (.json list / {"posts": [...]} or .csv with
id, url, platform, created_at, caption, media_type) plus data/held.json and a
cost-free daily-inputs/v1 snapshot (export_daily_inputs.py). Flags:

  * no_ma          post has no mã (e.g. an uncaptioned reel)
  * held_promoted  post's mã is on the held list
  * duplicate      more than one post for the same mã on the same platform
  * live_no_post   live mã with no post on a platform (per platform)
  * missing_gia    post with a mã but caption_lint says Giá missing/malformed
  * caption_lint   any other caption_lint FAIL/WARN reason, passed through

No network, no Meta access, no writes. It never suggests deleting or
reposting: every flag's action is 'edit original only / Boss decides'.

Exit code: 0 no flags, 1 flags found, 2 usage error.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import caption_lint as cl  # noqa: E402
from held_policy import norm_ma  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
ACTION = "edit original only / Boss decides"
PLATFORMS = ("fb", "ig")


def norm_platform(p: str) -> str:
    p = (p or "").strip().lower()
    return {"facebook": "fb", "instagram": "ig"}.get(p, p)


def load_export(path: Path) -> list[dict]:
    if path.suffix.lower() == ".csv":
        with path.open(encoding="utf-8-sig", newline="") as f:
            rows = list(csv.DictReader(f))
    else:
        data = json.loads(path.read_text(encoding="utf-8"))
        rows = data["posts"] if isinstance(data, dict) else data
    out = []
    for i, r in enumerate(rows):
        if not isinstance(r, dict):
            raise ValueError(f"row {i}: not an object")
        out.append({
            "id": str(r.get("id") or f"row-{i + 1}"),
            "url": str(r.get("url") or ""),
            "platform": norm_platform(str(r.get("platform") or "")),
            "created_at": str(r.get("created_at") or ""),
            "caption": str(r.get("caption") or r.get("text") or ""),
            "media_type": str(r.get("media_type") or r.get("media") or "").lower(),
        })
    return out


def load_held(path: Path) -> tuple[set[str], set[str]]:
    d = json.loads(path.read_text(encoding="utf-8"))
    return ({norm_ma(m) for m in d.get("heldIncomplete", [])},
            {norm_ma(m) for m in d.get("neverList", [])})


def load_approved(path: Path) -> dict[str, float]:
    if not path.exists():
        return {}
    d = json.loads(path.read_text(encoding="utf-8"))
    return {norm_ma(k): float(v) for k, v in d.get("approvedGia", {}).items() if math.isfinite(float(v))}


def reconcile(posts: list[dict], live: dict[str, float], known: set[str],
              held: set[str], approved: dict[str, float],
              never: set[str] = frozenset(), platforms=PLATFORMS) -> dict:
    flags: list[dict] = []
    by_key: dict[tuple[str, str], list[dict]] = defaultdict(list)

    def flag(kind, post=None, **kw):
        f = {"flag": kind, "action": ACTION}
        if post:
            f.update({k: post[k] for k in ("id", "url", "platform", "created_at", "media_type")})
        f.update(kw)
        flags.append(f)

    for p in posts:
        lint = cl.lint_post(p["url"] or p["id"], p["platform"], p["caption"], live,
                            known | held, held, approved, never)
        p["ma"] = lint.ma
        if lint.ma is None:
            flag("no_ma", p, detail="no mã in caption" + (" (uncaptioned)" if not p["caption"].strip() else ""))
            continue
        by_key[(lint.ma, p["platform"])].append(p)
        if lint.ma in held:
            flag("held_promoted", p, ma=lint.ma, detail="held mã is on a post")
        gia_reasons = [r for r in lint.reasons if r.startswith(("missing_gia", "malformed_gia"))]
        if gia_reasons:
            flag("missing_gia", p, ma=lint.ma, detail="; ".join(gia_reasons))
        other = [r for r in lint.reasons if r not in gia_reasons and not r.startswith("held_no_approved_gia")]
        if other:
            flag("caption_lint", p, ma=lint.ma, detail="; ".join(other))

    for (ma, plat), ps in sorted(by_key.items()):
        if len(ps) > 1:
            flags.append({"flag": "duplicate", "action": ACTION, "ma": ma, "platform": plat,
                          "ids": [x["id"] for x in ps], "urls": [x["url"] for x in ps],
                          "detail": f"{len(ps)} posts for {ma} on {plat}"})

    for ma in sorted(live):
        for plat in platforms:
            if (ma, plat) not in by_key:
                flags.append({"flag": "live_no_post", "action": ACTION, "ma": ma, "platform": plat,
                              "detail": f"live mã {ma} has no {plat} post in this export"})

    counts: dict[str, int] = defaultdict(int)
    for f in flags:
        counts[f["flag"]] += 1
    return {"schema": "meta-inventory/v1", "action": ACTION, "posts": len(posts),
            "counts": dict(sorted(counts.items())), "flags": flags}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("export", type=Path)
    ap.add_argument("--snapshot", type=Path, required=True, help="daily-inputs/v1 snapshot.json")
    ap.add_argument("--held", type=Path, default=ROOT / "data" / "held.json")
    ap.add_argument("--approved", type=Path, default=ROOT / "data" / "approved-held-gia.json")
    ap.add_argument("--platforms", default="fb,ig")
    ap.add_argument("--skip-live-no-post", action="store_true",
                    help="partial export: don't flag live mãs without posts")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    try:
        posts = load_export(a.export)
        live, known = cl.load_snapshot(a.snapshot)
        held, never = load_held(a.held)
        approved = load_approved(a.approved)
    except (OSError, ValueError, KeyError) as e:
        print(f"usage error: {e}", file=sys.stderr)
        return 2
    plats = tuple(x for x in a.platforms.split(",") if x)
    rep = reconcile(posts, live, known, held, approved, never, plats)
    if a.skip_live_no_post:
        rep["flags"] = [f for f in rep["flags"] if f["flag"] != "live_no_post"]
        rep["counts"].pop("live_no_post", None)
    if a.json:
        print(json.dumps(rep, ensure_ascii=False, indent=2))
    else:
        print(f"meta_inventory: {rep['posts']} posts, counts {rep['counts']}")
        for f in rep["flags"]:
            where = f.get("url") or ",".join(f.get("urls", [])) or f.get("platform", "")
            print(f"  {f['flag']:<14} {f.get('ma') or '-':<4} {where}  {f.get('detail', '')}  -> {f['action']}")
    return 1 if rep["flags"] else 0


if __name__ == "__main__":
    sys.exit(main())
