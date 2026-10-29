"""Offline Vietnamese caption linter for Sassy Closet FB/IG posts (piece 31).

Reads captions from a .json or .csv file (fields: url, platform, text) and
prints PASS / WARN / FAIL per post with reasons. No Meta access, no network,
no posting, no price writes. Inputs are mã codes and public $ prices only
(a daily-inputs/v1 snapshot from export_daily_inputs.py); it never reads
costs or supplier links.

Rules (Boss):
  * line 1 is the mã, exactly 'Mã X00'
      - none anywhere            -> FAIL missing_ma
      - 'Ma'/'ma'/'MÃ'/'Mã:'/'M A09' style, or not on line 1
                                 -> WARN malformed_ma (normalized code used)
      - code not in catalog+intake+held list -> FAIL unknown_ma
  * the post shows 'Giá $NN'
      - none                     -> FAIL missing_gia
      - 'Giá $ 32', 'Gia $32', 'Giá: 32$', '32 đô' ... -> WARN malformed_gia
      - 'Giá' word with no readable amount -> FAIL malformed_gia
  * price
      - S06 must be $25          -> FAIL s06_not_25
      - held mã: Giá must equal data/approved-held-gia.json -> FAIL held_gia_differs
        (held mã without an approved Giá -> WARN held_no_approved_gia)
      - live mã: Giá must equal the live public $ -> FAIL gia_differs_live
      - known but not live and not held -> WARN not_live
      - never-list mã (data/held.json neverList) -> FAIL never_list
  * --strict-first-line: a mã found only below line 1 -> FAIL (not WARN)

Captions: .json/.csv (url, platform, text); also, folded in from the old
caption_gia_check.py (piece 33): .txt (posts split by '---'), saved post
.html (og:description), minicheck .tsv. The IG og:description wrapper
('N likes, ... : "...".') is stripped and ' | ' is read as a line break.
Prices: --snapshot (daily-inputs/v1) or --live (products[] or prices map).

Exit code: 0 all PASS (or only WARN with --warn-ok), 1 any WARN, 2 any FAIL
or a usage error.
"""

from __future__ import annotations

import argparse
import csv
import html
import json
import math
import re
import sys
import unicodedata
from dataclasses import asdict, dataclass, field
from pathlib import Path
from held_policy import norm_ma

ROOT = Path(__file__).resolve().parents[1]
S06_LOCK = 25.0

CANON_MA_LINE = re.compile(r"^Mã ([A-Z][0-9]{2})$")
# loose mã: Mã/Ma/ma/MÃ/Mả/Má/M, optional : # . -, optional space, code
LOOSE_MA = re.compile(r"(?<![0-9A-Za-zÀ-ỹ])m(?:ã|a|ả|á|à|ạ)?\s*[:#.\-]?\s*([A-Za-z]\s?[0-9]{2})(?![0-9])",
                      re.IGNORECASE)
CANON_GIA = re.compile(r"(?<![A-Za-zÀ-ỹ])Giá \$(\d+(?:\.\d{1,2})?)(?![\d.])")
LOOSE_GIA = re.compile(
    r"(?<![A-Za-zÀ-ỹ])gi[áa]\s*[:\-–]?\s*(?:\$\s*(\d+(?:[.,]\d{1,2})?)"
    r"|(\d+(?:[.,]\d{1,2})?)\s*(?:\$|đô\b|do\b|usd\b))",
    re.IGNORECASE,
)
GIA_WORD = re.compile(r"(?<![A-Za-zÀ-ỹ])gi[áa](?![A-Za-zÀ-ỹ])", re.IGNORECASE)
OG_DESC_RE = re.compile(r'<meta[^>]+property="og:description"[^>]+content="([^"]*)"')
IG_PREFIX_RE = re.compile(r'^\s*\d+\s+likes?,.*?:\s*"', re.DOTALL)
PRIVATE = re.compile(r"[¥￥]|taobao|tmall|1688|\bcost\b|giá vốn", re.IGNORECASE)


@dataclass
class Lint:
    url: str
    platform: str
    ma: str | None
    gia_usd: float | None
    expected_usd: float | None
    status: str
    reasons: list[str] = field(default_factory=list)


def nfc(s: str) -> str:
    return unicodedata.normalize("NFC", s or "")


def clean_caption(text: str) -> str:
    """Strip the IG og:description wrapper and turn ' | ' back into lines."""
    t = nfc(text).strip()
    m = IG_PREFIX_RE.match(t)
    if m:
        t = re.sub(r'"\.?\s*$', "", t[m.end():])
    return "\n".join(part.strip() for part in re.split(r"\s\|\s|\n", t))


def find_ma(text: str) -> tuple[str | None, list[str]]:
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    first = lines[0] if lines else ""
    m = CANON_MA_LINE.match(first)
    if m:
        return m.group(1), []
    for i, ln in enumerate(lines):
        lm = LOOSE_MA.search(ln)
        if lm:
            code = lm.group(1).replace(" ", "").upper()
            why = "malformed_ma" if i == 0 else "malformed_ma:not_line_1"
            return code, [f"{why} (saw {lm.group(0).strip()!r}, want 'Mã {code}' on line 1)"]
    return None, ["missing_ma"]


def find_gia(text: str) -> tuple[float | None, list[str], bool]:
    """Return (usd, reasons, fatal)."""
    m = CANON_GIA.search(text)
    if m:
        return float(m.group(1)), [], False
    lm = LOOSE_GIA.search(text)
    if lm:
        raw = (lm.group(1) or lm.group(2)).replace(",", ".")
        v = float(raw)
        return v, [f"malformed_gia (saw {lm.group(0).strip()!r}, want 'Giá ${raw}')"], False
    if GIA_WORD.search(text):
        return None, ["malformed_gia (Giá with no readable $ amount)"], True
    return None, ["missing_gia"], True


def lint_post(url: str, platform: str, text: str, live: dict[str, float],
              known: set[str], held: set[str], approved: dict[str, float],
              never: set[str] | frozenset = frozenset(), strict_first_line: bool = False) -> Lint:
    text = clean_caption(text)
    fails: list[str] = []
    warns: list[str] = []
    ma, r = find_ma(text)
    if ma is None:
        fails.extend(r)
    else:
        for x in r:
            (fails if strict_first_line and x.startswith("malformed_ma:not_line_1") else warns).append(x)
    gia, r, fatal = find_gia(text)
    (fails if fatal else warns).extend(r)
    expected = None
    if ma is not None:
        if ma in never:
            fails.append("never_list")
        elif ma not in known:
            fails.append(f"unknown_ma ({ma} not in catalog/intake codes)")
        elif ma == "S06":
            expected = S06_LOCK
            if gia is not None and gia != S06_LOCK:
                fails.append(f"s06_not_25 (Giá ${gia:g})")
        elif ma in held:
            expected = approved.get(ma)
            if expected is None:
                warns.append("held_no_approved_gia")
            elif gia is not None and gia != expected:
                fails.append(f"held_gia_differs (Giá ${gia:g}, approved ${expected:g})")
        elif ma in live:
            expected = live[ma]
            if gia is not None and gia != expected:
                fails.append(f"gia_differs_live (Giá ${gia:g}, live ${expected:g})")
        else:
            warns.append("not_live")
    status = "FAIL" if fails else "WARN" if warns else "PASS"
    return Lint(url, platform, ma, gia, expected, status, fails + warns)


def _row(url: str, text: str) -> dict:
    return {"url": url, "platform": "", "text": text}


def load_posts(path: Path) -> list[dict]:
    suf = path.suffix.lower()
    if suf in (".html", ".htm"):
        m = OG_DESC_RE.search(path.read_text(encoding="utf-8"))
        return [_row(path.stem.removeprefix("raw-"), html.unescape(m.group(1)) if m else "")]
    if suf == ".tsv":
        return [_row(f"{c[0]}-{c[1]}", c[3]) for c in
                (ln.split("\t") for ln in path.read_text(encoding="utf-8").splitlines()) if len(c) >= 4]
    if suf == ".txt":
        raw = path.read_text(encoding="utf-8")
        chunks = [c.strip() for c in re.split(r"^\s*---\s*$", raw, flags=re.M) if c.strip()]
        if len(chunks) == 1:
            return [_row(path.stem, chunks[0])]
        return [_row(f"{path.stem}#{i + 1}", c) for i, c in enumerate(chunks)]
    if suf == ".csv":
        with path.open(encoding="utf-8-sig", newline="") as f:
            rows = list(csv.DictReader(f))
    else:
        data = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(data, dict) and "posts" in data:
            data = data["posts"]
        if isinstance(data, dict):  # legacy id -> text map
            return [_row(str(k), str(v)) for k, v in data.items()]
        rows = data
    out = []
    for i, r in enumerate(rows):
        if not isinstance(r, dict) or not ("text" in r or "caption" in r):
            raise ValueError(f"row {i}: needs url, platform, text")
        out.append({"url": str(r.get("url") or r.get("id") or r.get("post") or f"row-{i + 1}"),
                    "platform": str(r.get("platform") or "").lower(),
                    "text": str(r.get("text") or r.get("caption") or "")})
    return out


def load_snapshot(path: Path) -> tuple[dict[str, float], set[str]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    live, known = {}, set()
    for it in data.get("items", []):
        ma = norm_ma(str(it.get("ma", "")))
        if not ma:
            continue
        known.add(ma)
        if it.get("live") and it.get("sellUsd") is not None:
            usd = float(it["sellUsd"])
            if math.isfinite(usd):
                live[ma] = usd
    return live, known


def _finite(pairs) -> dict[str, float]:
    """float() accepts "NaN"/"Infinity"; no price check can catch those, so drop them."""
    out = {}
    for k, v in pairs:
        usd = float(v)
        if math.isfinite(usd):
            out[k] = usd
    return out


def load_live(path: Path) -> dict[str, float]:
    """Legacy catalog snapshot: {products: [{ma, priceUsd}]} or {prices: {ma: usd}}."""
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, dict) and "products" in data:
        return _finite((norm_ma(p["ma"]), p["priceUsd"]) for p in data["products"])
    if isinstance(data, dict) and "prices" in data:
        return _finite((norm_ma(k), v) for k, v in data["prices"].items())
    raise ValueError(f"{path}: expected products[] or a prices map")


def load_codes(path: Path | None) -> set[str]:
    if not path:
        return set()
    txt = path.read_text(encoding="utf-8")
    try:
        data = json.loads(txt)
        items = data if isinstance(data, list) else data.get("mas", data.get("codes", []))
    except json.JSONDecodeError:
        items = re.split(r"[\s,]+", txt)
    return {norm_ma(str(x)) for x in items if str(x).strip()}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("captions", nargs="+", type=Path,
                    help=".json/.csv (url, platform, text) or .txt/.html/.tsv")
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--snapshot", type=Path,
                     help="daily-inputs/v1 snapshot (mã, live, public sellUsd, held)")
    src.add_argument("--live", type=Path, help="legacy catalog JSON (products[] or prices map)")
    ap.add_argument("--strict-first-line", action="store_true")
    ap.add_argument("--codes", type=Path, help="extra intake mã codes (json list or text)")
    ap.add_argument("--held", type=Path, default=ROOT / "data" / "held.json")
    ap.add_argument("--approved", type=Path, default=ROOT / "data" / "approved-held-gia.json")
    ap.add_argument("--json", action="store_true", help="print JSON instead of text")
    ap.add_argument("--warn-ok", action="store_true")
    a = ap.parse_args(argv)
    try:
        posts = [p for f in a.captions for p in load_posts(f)]
        if a.snapshot:
            live, known = load_snapshot(a.snapshot)
        else:
            live = load_live(a.live)
            known = set(live)
        known |= load_codes(a.codes)
        hj = json.loads(a.held.read_text(encoding="utf-8"))
        held = {norm_ma(m) for m in hj.get("heldIncomplete", [])}
        never = {norm_ma(m) for m in hj.get("neverList", [])}
        known |= held | never
        approved = {norm_ma(k): float(v) for k, v in
                    json.loads(a.approved.read_text(encoding="utf-8")).get("approvedGia", {}).items()}
    except (OSError, ValueError, json.JSONDecodeError) as e:
        print(f"caption_lint: {e}", file=sys.stderr)
        return 2
    res = [lint_post(p["url"], p["platform"], p["text"], live, known, held, approved,
                     never, a.strict_first_line) for p in posts]
    counts = {s: sum(r.status == s for r in res) for s in ("PASS", "WARN", "FAIL")}
    if a.json:
        out = json.dumps({"counts": counts, "posts": [asdict(r) for r in res]},
                         ensure_ascii=False, indent=2)
    else:
        lines = [f"{r.status:4} {r.platform or '-':3} {r.ma or '---':3} {r.url}"
                 + (f"  | {'; '.join(r.reasons)}" if r.reasons else "") for r in res]
        lines.append(f"TOTAL {len(res)}: PASS {counts['PASS']} WARN {counts['WARN']} FAIL {counts['FAIL']}")
        out = "\n".join(lines)
    if PRIVATE.search(out):
        print("caption_lint: refusing output with private cost/supplier text", file=sys.stderr)
        return 2
    print(out)
    if counts["FAIL"]:
        return 2
    if counts["WARN"] and not a.warn_ok:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
