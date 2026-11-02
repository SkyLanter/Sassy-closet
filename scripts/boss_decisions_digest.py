#!/usr/bin/env python3
"""Boss decisions digest (READ-ONLY).

Scans local QC/verify outputs and prints one deduped plain list of open
Boss-only decisions: price approvals, hold calls, Blob photo deletes,
intake mismatches. Output carries only category, ma code, source file and
first-seen date -- never the line text, so no costs/links leak.
No network, no writes.
"""
import argparse
import json
import re
import sys
from datetime import date
from pathlib import Path

from held_policy import norm_ma

GLOBS = [
    "out/muse/extras-*.md",
    "verify/cost-recheck/REPORT-*.md",
    "out/midnight-qc/*.md",
    "out/midnight-qc/**/*.md",
]
MA_RE = re.compile(r"\b([A-Z]\d{2})\b")
DATE_RE = re.compile(r"(\d{4}-\d{2}-\d{2})")
CLOSED_RE = re.compile(r"\b(approved|resolved|done|closed|decided)\b", re.I)
# Negation has to sit on the closure word: "not", "not yet", "never",
# "no longer", or a contraction that ends in n't.
_NEG_BEFORE = re.compile(
    r"(?:(?<![A-Za-z])(?:not yet|no longer|not|never)|n't)\s+$",
    re.I,
)
BOSS_RE = re.compile(r"\bboss\b", re.I)
# Piece 52: blob/photo/delete must sit NEAR the ma (same line or same bullet).
BLOB_KW = re.compile(r"\b(blob|photos?|cover)\b", re.I)
ACT_KW = re.compile(r"\b(delete|deletion|public|exposed)\b", re.I)
NEAR = 60  # chars either side of the ma
BULLET_RE = re.compile(r"^\s*(?:[-*+]|\d+[.)])\s+")
# Known held mas with public Blob photos (mirrors held_photo_public_watch).
DEFAULT_PUBLIC_HELD = ("S14", "A24", "A25")
# order matters: first match wins (blob handled separately, proximity-based)
CATEGORIES = [
    ("intake_mismatch", re.compile(r"intake.*(mismatch|>|wrong|incorrect|bad|too cheap|above|below)|nhung.*(price|cost)", re.I)),
    ("price_approval", re.compile(r"(boss price|price approv|approve|needs? (a )?price|awaiting boss price)", re.I)),
    ("hold_call", re.compile(r"\b(hold|held)\b.*(call|keep|release|decide|\?)", re.I)),
]


def _calendar_day(value: str) -> bool:
    try:
        date.fromisoformat(value)
    except ValueError:
        return False
    return True


def file_date(p: Path, stop: Path | None = None):
    """Date in the file name, else the nearest real YYYY-MM-DD directory.

    The walk includes ``stop`` itself and stops there, so a date-named
    directory above the scan root cannot become first_seen.
    """
    named = DATE_RE.search(p.name)
    if named and _calendar_day(named.group(1)):
        return named.group(1)
    halt = None if stop is None else Path(stop).resolve()
    for parent in p.parents:
        if DATE_RE.fullmatch(parent.name) and _calendar_day(parent.name):
            return parent.name
        if halt is not None and parent.resolve() == halt:
            break
    return None


def classify(line):
    for name, rx in CATEGORIES:
        if rx.search(line):
            return name
    return None


RULES = {"intake_mismatch": "intake_keyword_line", "price_approval": "price_keyword_line",
         "hold_call": "hold_keyword_line"}


def is_closed(text) -> bool:
    """True when a closure word is not immediately negated.

    Immediate negation is not, not yet, never, no longer, or a contraction
    ending in n't. A not earlier in the sentence does not reopen a later approval.
    """
    src = text or ""
    for match in CLOSED_RE.finditer(src):
        if _NEG_BEFORE.search(src[:match.start()]):
            continue
        return True
    return False


def units(text):
    """Yield (kind, text): each bullet incl. continuation lines, else one line."""
    cur = None
    for line in text.splitlines():
        if BULLET_RE.match(line):
            if cur is not None:
                yield ("bullet", "\n".join(cur))
            cur = [line]
        elif cur is not None and line.strip() and line[:1].isspace():
            cur.append(line)
        else:
            if cur is not None:
                yield ("bullet", "\n".join(cur))
                cur = None
            if line.strip():
                yield ("line", line)
    if cur is not None:
        yield ("bullet", "\n".join(cur))


def blob_hits(kind, unit):
    """Mas whose nearby window (same line/bullet) has blob-word AND delete/public-word."""
    out = []
    if is_closed(unit) or not BOSS_RE.search(unit):
        return out
    for m in MA_RE.finditer(unit):
        win = unit[max(0, m.start() - NEAR): m.end() + NEAR]
        if BLOB_KW.search(win) and ACT_KW.search(win):
            # Label from the unit shape. Keep the backslash out of the f-string so Python 3.11 can parse it.
            where = "line" if "\n" not in unit else "bullet"
            out.append((m.group(1), f"blob_near_ma_{where}"))
    return out


def load_public_held(path):
    """Codes from held-photos/v1 JSON (exposedMas) or a plain JSON list."""
    if path is None:
        return set(DEFAULT_PUBLIC_HELD)
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if isinstance(data, dict):
        data = data.get("exposedMas", [])
    return {norm_ma(x) for x in data} - {""}


def _note_open(seen, rules, text, src, d, skip_mas=()):
    """Record price/hold/intake mãs in text. skip_mas were already decided on their own line."""
    flat = " ".join(text.split())
    if is_closed(flat):
        return
    cat = classify(flat)
    if not cat:
        return
    if cat != "intake_mismatch" and not BOSS_RE.search(flat):
        return
    for ma in sorted(set(MA_RE.findall(flat))):
        if ma in skip_mas:
            continue
        key = (cat, ma)
        if key not in seen:
            seen[key] = (src, d)
            rules[key] = RULES[cat]


def _blob_from_unit(unit):
    """Whole bullet when it is still open; otherwise only the lines that are open."""
    if not is_closed(unit):
        return blob_hits("bullet", unit)
    hits = []
    for line in unit.splitlines():
        if is_closed(line):
            continue
        hits.extend(blob_hits("line", line))
    return hits


def scan(root: Path, public_held=None, explain=None):
    public_held = set(DEFAULT_PUBLIC_HELD) if public_held is None else set(public_held)
    seen = {}
    rules = {} if explain is None else explain
    files = set()
    for g in GLOBS:
        files.update(root.glob(g))
    for p in sorted(files, key=lambda x: (file_date(x, root) or "9999", str(x))):
        d = file_date(p, root) or "unknown"
        src = str(p.relative_to(root))
        try:
            text = p.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for _kind, unit in units(text):
            for ma, rule in _blob_from_unit(unit):
                if ma not in public_held:
                    continue
                key = ("blob_photo_delete", ma)
                if key not in seen:
                    seen[key] = (src, d)
                    rules[key] = rule
            lines = unit.splitlines() or [unit]
            before = set(seen)
            for line in lines:
                _note_open(seen, rules, line, src, d)
            # A mã that only becomes a decision once continuation lines are joined.
            # A closed line stays closed: the join uses the open lines only.
            if len(lines) < 2:
                continue
            noted = {ma for _cat, ma in set(seen) - before}
            if not is_closed(unit):
                _note_open(seen, rules, unit, src, d, skip_mas=noted)
                continue
            open_lines = [line for line in lines if not is_closed(line)]
            if len(open_lines) >= 2:
                _note_open(seen, rules, "\n".join(open_lines), src, d, skip_mas=noted)
    return seen


def repo_order_held_paths():
    """Repo copies of popular-order.json and held.json."""
    repo = Path(__file__).resolve().parents[1]
    return (repo / "sassy-closet-shop" / "data" / "popular-order.json",
            repo / "data" / "held.json")


def held_in_popular_order(order_path, held_path):
    """Piece 75: held mãs in popular-order.json (read-only; never edits it)."""
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from popular_carryover import _codes, load_held
    op, hp = Path(order_path), Path(held_path)
    if not op.is_file() or not hp.is_file():
        return []
    order = _codes(json.loads(op.read_text(encoding="utf-8")).get("order"))
    held = load_held(hp)
    return [m for m in order if m in held]


def held_order_item(mas):
    if not mas:
        return None
    return (f"Remove held mãs {', '.join(mas)} from popular order? "
            "(no effect while they are 404; keeping lets them rank on return)")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root", default="/workspace/sassy-closet")
    ap.add_argument("--public-held", default=None,
                    help="held-photos/v1 JSON (exposedMas) or JSON list of held mas with public photos")
    ap.add_argument("--explain", action="store_true",
                    help="print the matched rule name per item (never line text)")
    ap.add_argument("--order", default=None,
                    help="popular-order.json (default: <repo>/sassy-closet-shop/data/popular-order.json)")
    ap.add_argument("--held", default=None,
                    help="held.json (default: <repo>/data/held.json)")
    a = ap.parse_args(argv)
    root = Path(a.root)
    rules = {}
    seen = scan(root, load_public_held(a.public_held), rules)
    print("Open Boss-only decisions (read-only digest)")
    for (cat, ma), (src, d) in sorted(seen.items()):
        extra = f"  rule={rules[(cat, ma)]}" if a.explain else ""
        print(f"- [{cat}] {ma}  first_seen={d}  source={src}{extra}")
    counts = {}
    for cat, _ in seen:
        counts[cat] = counts.get(cat, 0) + 1
    order_default, held_default = repo_order_held_paths()
    held_mas = held_in_popular_order(a.order or order_default, a.held or held_default)
    item = held_order_item(held_mas)
    if item:
        print(f"- [popular_order_held] {item}")
        counts["popular_order_held"] = 1
    total = len(seen) + (1 if item else 0)
    summary = ", ".join(f"{k}={v}" for k, v in sorted(counts.items())) or "none"
    print(f"TOTAL {total} ({summary})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
