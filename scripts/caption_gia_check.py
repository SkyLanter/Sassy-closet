"""Compatibility shim: the caption Giá check now lives in caption_lint.py (piece 33).

Old CLI kept: captions... --live --held --approved --strict-first-line
--out-md --out-json, and old exit codes (1 if any post FAILs, else 0; a WARN
never fails here). Old issue names are kept (no_ma, ma_not_first_line, no_gia,
gia_unparsed, price_mismatch, s06_not_25, held_gia_differs,
held_no_approved_gia, never_list, not_in_live_catalog) by translating the
linter's reasons. Read-only: no Meta, Blob, intake, Square or price writes.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import caption_lint as _cl  # noqa: E402
from held_policy import HeldPolicy, load_held_policy, norm_ma  # noqa: E402

ROOT = _cl.ROOT
S06_LOCK = _cl.S06_LOCK
clean_caption = _cl.clean_caption
load_live = _cl.load_live

# linter reason prefix -> (old issue, old severity); None = old checker ignored it
_MAP = {
    "missing_ma": ("no_ma", "W"),
    "malformed_ma:not_line_1": ("ma_not_first_line", None),  # severity from the linter (strict)
    "malformed_ma": None,
    "missing_gia": ("no_gia", "W"),
    "malformed_gia (Giá with no readable": ("gia_unparsed", "W"),
    "malformed_gia": None,
    "unknown_ma": ("not_in_live_catalog", "W"),
    "not_live": ("not_in_live_catalog", "W"),
    "gia_differs_live": ("price_mismatch", "F"),
    "s06_not_25": ("s06_not_25", "F"),
    "held_gia_differs": ("held_gia_differs", "F"),
    "held_no_approved_gia": ("held_no_approved_gia", "W"),
    "never_list": ("never_list", "F"),
}
_ORDER = sorted(_MAP, key=len, reverse=True)


@dataclass
class Result:
    post: str
    ma: str | None
    gia_usd: float | None
    expected_usd: float | None
    status: str  # PASS / WARN / FAIL
    issues: list[str] = field(default_factory=list)


def find_ma(text: str) -> tuple[str | None, bool]:
    lines = [ln for ln in clean_caption(text).split("\n") if ln.strip()]
    ma, r = _cl.find_ma("\n".join(lines))
    return ma, ma is not None and not any(x.startswith("malformed_ma:not_line_1") for x in r)


def parse_gia(text: str) -> tuple[float | None, bool]:
    t = clean_caption(text)
    v, _, _ = _cl.find_gia(t)
    return v, v is not None or bool(_cl.GIA_WORD.search(t))


def check_post(post: str, text: str, live: dict[str, float], policy: HeldPolicy,
               approved: dict[str, float], strict_first_line: bool = False) -> Result:
    held, never = set(policy.held), set(policy.never_list)
    lint = _cl.lint_post(post, "", text, live, set(live) | held | never, held, approved,
                         never, strict_first_line)
    fails: list[str] = []
    warns: list[str] = []
    for reason in lint.reasons:
        key = next((k for k in _ORDER if reason.startswith(k)), None)
        tr = _MAP.get(key) if key else None
        if tr is None:
            continue
        name, sev = tr
        if sev is None:
            sev = "F" if strict_first_line else "W"
        tgt = fails if sev == "F" else warns
        if name not in tgt:
            tgt.append(name)
    expected = lint.expected_usd
    if lint.ma and lint.ma not in held and lint.ma != "S06" and lint.ma not in never:
        expected = live.get(lint.ma)
    status = "FAIL" if fails else "WARN" if warns else "PASS"
    return Result(post, lint.ma, lint.gia_usd, expected, status, fails + warns)


def load_posts(path: Path) -> list[tuple[str, str]]:
    return [(p["url"], p["text"]) for p in _cl.load_posts(path)]


def load_approved(path: Path) -> dict[str, float]:
    data = json.loads(path.read_text(encoding="utf-8"))
    return {norm_ma(k): float(v) for k, v in data.get("approvedGia", {}).items() if math.isfinite(float(v))}


def summarize(results: list[Result]) -> dict:
    counts = {s: sum(r.status == s for r in results) for s in ("PASS", "WARN", "FAIL")}
    return {"overall": "FAIL" if counts["FAIL"] else "PASS", "counts": counts,
            "posts": [asdict(r) for r in results]}


def to_md(summary: dict) -> str:
    c = summary["counts"]
    out = [f"# Caption Giá check: {summary['overall']}", "",
           f"PASS {c['PASS']} · WARN {c['WARN']} · FAIL {c['FAIL']}", "",
           "| post | mã | Giá $ | expected $ | status | issues |", "|---|---|---|---|---|---|"]
    fmt = lambda v: "" if v is None else f"{v:g}"  # noqa: E731
    for p in summary["posts"]:
        out.append(f"| {p['post']} | {p['ma'] or ''} | {fmt(p['gia_usd'])} | {fmt(p['expected_usd'])} "
                   f"| {p['status']} | {', '.join(p['issues'])} |")
    out += ["", "Read-only. No Meta, Blob, intake, Square, or price writes.",
            "(caption_gia_check is a shim over scripts/caption_lint.py)"]
    return "\n".join(out) + "\n"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("captions", nargs="+", type=Path)
    ap.add_argument("--live", required=True, type=Path, help="local catalog snapshot JSON")
    ap.add_argument("--held", type=Path, default=ROOT / "data" / "held.json")
    ap.add_argument("--approved", type=Path, default=ROOT / "data" / "approved-held-gia.json")
    ap.add_argument("--strict-first-line", action="store_true")
    ap.add_argument("--out-md", type=Path)
    ap.add_argument("--out-json", type=Path)
    a = ap.parse_args(argv)
    live, policy, approved = load_live(a.live), load_held_policy(a.held), load_approved(a.approved)
    results = [check_post(pid, txt, live, policy, approved, a.strict_first_line)
               for f in a.captions for pid, txt in load_posts(f)]
    summary = summarize(results)
    if a.out_json:
        a.out_json.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if a.out_md:
        a.out_md.write_text(to_md(summary), encoding="utf-8")
    print(to_md(summary))
    return 1 if summary["overall"] == "FAIL" else 0


if __name__ == "__main__":
    sys.exit(main())
