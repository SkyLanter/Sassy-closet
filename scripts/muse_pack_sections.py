#!/usr/bin/env python3
"""Piece 56: add short generated sections to the Muse pack (TODAY.md + pack message).

Sections come from three read-only tools:
  * boss_decisions_digest   -> open Boss decisions (category + mã)
  * meta_caption_gap_report -> caption gaps (platform + post ID + mã only)
  * intake_code_reuse_check -> reused intake codes (mã + row count)

Output uses mãs, post IDs and counts only: never costs, links or caption text.
If a tool fails, the pack still builds and that section says "unavailable".
Only local files are written (and only with --write); nothing is sent anywhere.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from held_policy import norm_ma

sys.path.insert(0, str(Path(__file__).resolve().parent))

MA_OK = re.compile(r"^[A-Z]{1,2}\d{2,3}$")
ID_OK = re.compile(r"^[A-Za-z0-9_-]{1,40}$")
START = "<!-- muse-pack-sections:start -->"
END = "<!-- muse-pack-sections:end -->"
MSG_START = "[auto sections]"
MSG_END = "[/auto sections]"
UNAVAILABLE = "unavailable"


def _ma(x) -> str:
    s = norm_ma(str(x or ""))
    return s if MA_OK.match(s) else "?"


def _pid(x) -> str:
    s = str(x or "").strip()
    return s if ID_OK.match(s) else "?"


def section_decisions(root: Path):
    import boss_decisions_digest as bd
    seen = bd.scan(root)
    by: dict[str, list[str]] = {}
    for cat, ma in seen:
        by.setdefault(str(cat), []).append(_ma(ma))
    return {"total": len(seen), "by_cat": {k: sorted(set(v)) for k, v in sorted(by.items())}}


def section_captions(root: Path):
    import meta_caption_gap_report as mc
    rep = mc.build([root / d for d in mc.DEFAULT_DIRS])
    def one(p, media, i):
        i = str(i or "")
        ref = f"mã {_ma(i[3:])}" if i.lower().startswith("ma:") else _pid(i)
        return (str(p).upper()[:2], str(media).lower() if str(media).isalpha() else "post", ref)

    def rows(k):
        return [one(*g) for g in rep[k]]
    lnp = {p: (None if v is None else len(v)) for p, v in rep["live_no_post"].items()}
    return {"no_ma": rows("no_ma"), "no_gia": rows("no_gia"), "live_no_post": lnp}


def default_intake(root: Path):
    c = sorted(root.glob("out/midnight-qc/*/raw/intake-submissions.json"))
    return [c[-1]] if c else []


def section_reuse(files):
    import intake_code_reuse_check as ir
    if not files:
        raise FileNotFoundError("no intake file")
    rows = []
    for f in files:
        rows.extend(ir.load_rows(Path(f)))
    return {"rows_read": len(rows),
            "reused": [(_ma(f["ma"]), int(f["rows"])) for f in ir.find_reuse(rows)]}


def build(root: Path, intake=None):
    out = {}
    for name, fn in (("decisions", lambda: section_decisions(root)),
                     ("captions", lambda: section_captions(root)),
                     ("reuse", lambda: section_reuse(default_intake(root) if intake is None else intake))):
        try:
            out[name] = fn()
        except Exception as e:  # noqa: BLE001 - any tool failure => section unavailable
            out[name] = {"error": type(e).__name__}
    return out


def render_md(s) -> str:
    L = [START, "## Auto sections (generated, read-only)"]
    d = s["decisions"]
    L.append("### Open Boss decisions")
    if "error" in d:
        L.append(f"- {UNAVAILABLE} ({d['error']})")
    else:
        L.append(f"- Total: {d['total']}")
        L += [f"- {cat} ({len(m)}): {' '.join(m)}" for cat, m in d["by_cat"].items()]
    c = s["captions"]
    L.append("### Caption gaps (post IDs only)")
    if "error" in c:
        L.append(f"- {UNAVAILABLE} ({c['error']})")
    else:
        for k, label in (("no_ma", "No mã"), ("no_gia", "No Giá")):
            L.append(f"- {label}: {len(c[k])}")
            L += [f"  - {p} {media} {ref}" for p, media, ref in c[k]]
        for p, n in c["live_no_post"].items():
            L.append(f"- Live mã with no {p.upper()} post: {'unknown' if n is None else n}")
    r = s["reuse"]
    L.append("### Reused intake codes")
    if "error" in r:
        L.append(f"- {UNAVAILABLE} ({r['error']})")
    else:
        L.append(f"- {len(r['reused'])} reused of {r['rows_read']} rows"
                 + (": " + " ".join(f"{m}×{n}" for m, n in r["reused"]) if r["reused"] else ""))
    L.append(END)
    return "\n".join(L)


def render_msg(s) -> str:
    d, c, r = s["decisions"], s["captions"], s["reuse"]
    L = [MSG_START]
    L.append("Boss decisions: " + (UNAVAILABLE if "error" in d else
             f"{d['total']} open" + "".join(f"; {k} {' '.join(v)}" for k, v in d["by_cat"].items())))
    L.append("Caption gaps: " + (UNAVAILABLE if "error" in c else
             f"no mã {len(c['no_ma'])}, no Giá {len(c['no_gia'])}"))
    L.append("Reused intake codes: " + (UNAVAILABLE if "error" in r else
             (" ".join(m for m, _ in r["reused"]) or "none")))
    L.append(MSG_END)
    return "\n".join(L)


def _splice(text: str, block: str, a: str, b: str, before_sig: bool) -> str:
    if a in text and b in text:
        i, j = text.index(a), text.index(b) + len(b)
        return text[:i] + block + text[j:]
    if before_sig:
        lines = text.rstrip("\n").split("\n")
        if lines and lines[-1].strip().startswith("- Mini Boss"):
            return "\n".join(lines[:-1] + [block, lines[-1]]) + "\n"
    return text.rstrip("\n") + "\n\n" + block + "\n"


def apply(today: Path, message: Path | None, s) -> None:
    for path, block, a, b, sig in ((today, render_md(s), START, END, False),
                                   (message, render_msg(s), MSG_START, MSG_END, True)):
        if path is None:
            continue
        old = path.read_text(encoding="utf-8") if path.exists() else ""
        path.write_text(_splice(old, block, a, b, sig), encoding="utf-8")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", type=Path, default=Path("/workspace/sassy-closet"))
    ap.add_argument("--intake", type=Path, nargs="*")
    ap.add_argument("--today", type=Path)
    ap.add_argument("--message", type=Path)
    ap.add_argument("--write", action="store_true", help="splice into --today/--message (local files only)")
    a = ap.parse_args(argv)
    s = build(a.root, a.intake)
    if a.write:
        if not a.today:
            ap.error("--write needs --today")
        apply(a.today, a.message, s)
    print(render_md(s))
    print(render_msg(s))
    return 0


if __name__ == "__main__":
    sys.exit(main())
