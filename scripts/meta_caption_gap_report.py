"""Offline Meta caption-gap report for Sassy Closet (piece 53).

Scans local files under out/ and verify/ (no network, no Meta access, no
writes) and lists:

  * FB/IG posts or Reels with no mã         (no_ma)
  * FB/IG posts or Reels with no Giá line   (no_gia)
  * live mãs with no post on a platform     (live_no_post)

Sources:
  1. Structured Meta snapshots: .json ({"posts": [...]} or list) / .csv with
     id + platform + caption (+ media_type). Captions are checked with
     caption_lint.find_ma / find_gia.
  2. QC notes (.md/.txt): lines naming "FB|IG Reel|post <id or Mã Xnn>" and
     saying "no caption" / "no mã" / "no Giá".
  3. Live mãs: newest catalog.v1.json (products with status available/live).

live_no_post is computed only per platform that has a structured snapshot;
otherwise it is reported as "unknown". Output is counts plus post IDs (or a
mã key when a QC note gives no numeric ID). Caption text is never printed.

Exit: 0 no gaps, 1 gaps found, 2 usage error.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import caption_lint as cl  # noqa: E402
from held_policy import MA_RE, MA_TOKEN_TAIL, norm_ma  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DIRS = ("out", "verify")
SKIP_PARTS = {"pending-draft-prs", "node_modules", ".git", "lh"}
LIVE_STATUS = {"available", "live", "active"}
PLAT = {"fb": "fb", "facebook": "fb", "ig": "ig", "instagram": "ig"}

# One to four digits. A later letter or digit is a different token, so S06B,
# S06Đ, and K12345 are not S06 or K12. Zero-padding is collapsed later by norm_ma.
_MA_TOKEN = r"[A-Za-z]\s?[0-9]{1,4}" + MA_TOKEN_TAIL
_NOTE_HIT = re.compile(
    r"\b(?P<plat>FB|IG)\b"
    r"(?P<before>(?:\s+\"?M[ãa]\s*" + _MA_TOKEN + r"\"?)*)"
    r"\s*(?:hair-clip\s+)?"
    r"\b(?P<media>Reel|post)\b"
    r"(?P<after>.*?)(?=(?:\b(?:FB|IG)\b)|$)",
    re.IGNORECASE)
_LEAD_LABEL = re.compile(r"(?iu)^[ \t\"']*M[ãa][ \t]*(" + _MA_TOKEN + r")[ \t\"']*")
_LEAD_ID = re.compile(r"^[ \t]*(\d{8,})(?![0-9])")
IG_MA_CAP_RE = re.compile(
    r"\b(FB|IG)\s+(" + _MA_TOKEN + r")\s+caption\b",
    re.IGNORECASE)
NO_CAPTION = re.compile(r"\bno caption\b", re.IGNORECASE)
NO_MA = re.compile(r"\bno (?:caption, )?m[ãa]\b|\bno caption, m[ãa]\b", re.IGNORECASE)
NO_GIA = re.compile(r"\bno (?:caption, m[ãa], (?:or|and) )?gi[áa]\b|\bno gi[áa]\b", re.IGNORECASE)
NEGATED = re.compile(r"\?\s*$")  # questions in checklists are not findings


def iter_files(roots, exts):
    for r in roots:
        if not r.exists():
            continue
        for p in sorted(r.rglob("*")):
            if p.is_file() and p.suffix.lower() in exts and not (SKIP_PARTS & set(p.parts)):
                yield p


def _records(path: Path):
    try:
        if path.suffix.lower() == ".csv":
            with path.open(newline="", encoding="utf-8-sig") as f:
                return list(csv.DictReader(f))
        d = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError, UnicodeDecodeError):
        return []
    if isinstance(d, dict):
        d = d.get("posts")
    return d if isinstance(d, list) else []


SNAP_DIR = "meta-snapshot"


def newest_saved_snapshot(files):
    """Piece 60: only the newest out/meta-snapshot/*.json counts."""
    files = list(files)
    saved = [p for p in files if SNAP_DIR in p.parts and p.suffix.lower() == ".json"]
    rest = [p for p in files if SNAP_DIR not in p.parts]
    if saved:
        rest.append(max(saved, key=lambda p: (p.name, p.stat().st_mtime)))
    return rest


def load_snapshots(files):
    posts = []
    for p in newest_saved_snapshot(files):
        for r in _records(p):
            if not isinstance(r, dict):
                continue
            plat = PLAT.get(str(r.get("platform", "")).strip().lower())
            if plat and "caption" in r and r.get("id") not in (None, ""):
                posts.append({"id": str(r["id"]), "platform": plat,
                              "media": str(r.get("media_type") or "post").lower(),
                              "caption": r.get("caption") or "", "src": "snapshot"})
            elif plat and "has_gia" in r and r.get("id") not in (None, ""):
                # piece 60 structured row: no caption text, mã + has_gia only
                posts.append({"id": str(r["id"]), "platform": plat,
                              "media": str(r.get("media_type") or "post").lower(),
                              "ma": (norm_ma(str(r.get("ma") or "")) or None),
                              "has_gia": r.get("has_gia") is True
                              or str(r.get("has_gia")).lower() in ("true", "1", "yes"),
                              "src": "saved"})
    return posts


def lint_snapshot(posts):
    gaps, covered = [], {}
    for p in posts:
        if p["src"] == "saved":
            ma, gia_fatal = p["ma"], not p["has_gia"]
        else:
            text = cl.clean_caption(p["caption"]) if p["caption"] else ""
            ma, _ = cl.find_ma(text)
            _, _, gia_fatal = cl.find_gia(text)
        covered.setdefault(p["platform"], set())
        if ma:
            covered[p["platform"]].add(ma.upper())
        if ma is None:
            gaps.append(("no_ma", p["platform"], p["media"], p["id"]))
        if gia_fatal:
            gaps.append(("no_gia", p["platform"], p["media"], p["id"]))
    return gaps, covered


def _note_code(raw: str) -> str | None:
    """Shop mã key. A short or zero-padded token collapses. Anything else is skipped."""
    code = norm_ma(raw.replace(" ", ""))
    return code if MA_RE.fullmatch(code) else None


def _leading_code(text: str) -> tuple[str | None, str]:
    """First valid Mã label at the start of text, and the text after skipped labels."""
    rest = text
    while True:
        label = _LEAD_LABEL.match(rest)
        if not label:
            return None, rest
        rest = rest[label.end():]
        code = _note_code(label.group(1))
        if code:
            return code, rest


def parse_notes(files):
    gaps = set()
    for p in files:
        try:
            lines = p.read_text(encoding="utf-8").splitlines()
        except (OSError, UnicodeDecodeError):
            continue
        for line in (x for raw in lines for x in re.split(r"(?<=[.;])\s+", raw)):
            if NEGATED.search(line):
                continue
            nc, nm, ng = bool(NO_CAPTION.search(line)), bool(NO_MA.search(line)), bool(NO_GIA.search(line))
            if not (nc or nm or ng):
                continue
            hits = []
            for m in _NOTE_HIT.finditer(line):
                before_code, _ = _leading_code(m.group("before"))
                after_code, after_rest = _leading_code(m.group("after"))
                post_id = None
                id_match = _LEAD_ID.match(after_rest)
                if id_match:
                    post_id = id_match.group(1)
                code = before_code or after_code
                pid = post_id or (f"ma:{code}" if code else None)
                if pid:
                    hits.append((PLAT[m.group("plat").lower()], m.group("media").lower(), pid))
            for m in IG_MA_CAP_RE.finditer(line):
                code = _note_code(m.group(2))
                if not code:
                    continue
                hits.append((PLAT[m.group(1).lower()], "post", f"ma:{code}"))
            for plat, media, pid in hits:
                if nc or nm:
                    if not pid.startswith("ma:"):
                        gaps.add(("no_ma", plat, media, pid))
                if nc or ng:
                    gaps.add(("no_gia", plat, media, pid))
    return gaps


def load_live(roots, catalog: Path | None):
    if catalog is None:
        cands = [p for p in iter_files(roots, {".json"}) if p.name == "catalog.v1.json"]
        if not cands:
            return None
        catalog = max(cands, key=lambda p: (p.stat().st_mtime, str(p)))
    d = json.loads(catalog.read_text(encoding="utf-8"))
    prods = d.get("products", []) if isinstance(d, dict) else d
    return {norm_ma(str(x["ma"])) for x in prods
            if isinstance(x, dict) and x.get("ma") and str(x.get("status", "")).lower() in LIVE_STATUS}


def build(roots, catalog=None):
    snap = load_snapshots(iter_files(roots, {".json", ".csv"}))
    sgaps, covered = lint_snapshot(snap)
    ngaps = parse_notes(iter_files(roots, {".md", ".txt"}))
    gaps = sorted(set(sgaps) | ngaps)
    live = load_live(roots, catalog)
    live_no_post = {}
    for plat in ("fb", "ig"):
        if live is None or plat not in covered:
            live_no_post[plat] = None
        else:
            live_no_post[plat] = sorted(live - covered[plat])
    return {"piece": 53, "mode": "offline", "snapshot_posts": len(snap),
            "live_mas": None if live is None else len(live),
            "no_ma": [g[1:] for g in gaps if g[0] == "no_ma"],
            "no_gia": [g[1:] for g in gaps if g[0] == "no_gia"],
            "live_no_post": live_no_post}


def render(rep) -> str:
    out = [f"meta_caption_gap_report (offline, read-only) snapshot_posts={rep['snapshot_posts']} "
           f"live_mas={rep['live_mas'] if rep['live_mas'] is not None else 'unknown'}"]
    for k in ("no_ma", "no_gia"):
        out.append(f"{k}: {len(rep[k])}")
        out += [f"  {p} {m} {i}" for p, m, i in rep[k]]
    for plat, v in rep["live_no_post"].items():
        if v is None:
            out.append(f"live_no_post[{plat}]: unknown (no structured {plat} snapshot)")
        else:
            out.append(f"live_no_post[{plat}]: {len(v)}" + (f" {' '.join(v)}" if v else ""))
    return "\n".join(out)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", type=Path, default=ROOT)
    ap.add_argument("--dirs", nargs="*", default=list(DEFAULT_DIRS))
    ap.add_argument("--catalog", type=Path)
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    roots = [a.root / d for d in a.dirs]
    if not any(r.exists() for r in roots):
        print("usage: none of the scan dirs exist", file=sys.stderr)
        return 2
    rep = build(roots, a.catalog)
    print(json.dumps(rep, indent=1) if a.json else render(rep))
    gaps = rep["no_ma"] or rep["no_gia"] or any(rep["live_no_post"][p] for p in ("fb", "ig"))
    return 1 if gaps else 0


if __name__ == "__main__":
    sys.exit(main())
