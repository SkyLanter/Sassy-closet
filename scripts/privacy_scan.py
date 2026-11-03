#!/usr/bin/env python3
"""Piece 32: privacy scan for anything that ships (draft branches, pending-draft-prs bundle).

Flags Nhung's costs (¥ / CNY / intake_cny), supplier links (taobao, tb.cn, 1688, supplier),
phone numbers and email addresses.

Usage:
  privacy_scan.py PATH [PATH ...]            # directory, single file, or .tgz/.tar.gz
  privacy_scan.py --git-diff BASE..HEAD [--repo DIR]   # only *added* lines of the diff
  options: --allowlist FILE (default: data/privacy-allowlist.json next to repo root)
           --json   machine-readable output

Exit: 0 clean, 1 hits, 2 usage error.

Allowlist file (JSON list): {"path": "<glob>", "rules": ["cny", ...] (optional, default all),
"reason": "<why this is synthetic/safe>"}. Every entry MUST have a reason.
Paths are matched against the path relative to the scan root (fnmatch, '*' crosses '/').
"""
from __future__ import annotations

import argparse
import fnmatch
import json
import os
import re
import subprocess
import sys
import tarfile
from dataclasses import dataclass, asdict

NUM = r"\d[\d,]*(?:\.\d+)?"
# Default rules match *values and links*, not bare words: code may name the field intake_cny,
# docs may say "Taobao sign-in"; neither leaks a cost or a supplier. --strict adds bare tokens.
RULES: dict[str, re.Pattern] = {
    "yen": re.compile(r"[¥￥]\s?" + NUM + r"|" + NUM + r"\s?[¥￥]"),
    "cny": re.compile(r"(?<![A-Za-z])(?:CNY|RMB)\s?" + NUM + r"|(?<![A-Za-z\d.])" + NUM + r"\s?(?:CNY|RMB)(?![A-Za-z])"),
    "intake_cny": re.compile(r"intake_cny[\"']?\s*[:=]\s*[\"']?[1-9]", re.I),
    "taobao": re.compile(r"taobao\.com|(?:item|detail|m)\.tmall\.com", re.I),
    "tb_cn": re.compile(r"(?<![\w-])(?:m\.)?tb\.cn/\w", re.I),
    "1688": re.compile(r"1688\.com", re.I),
    "supplier": re.compile(r"supplier[_ -]?(?:url|link|name|shop|contact|wechat)?[\"']?\s*[:=]\s*[\"']?(?:https?://|[A-Za-z0-9\u4e00-\u9fff])", re.I),
    "phone": re.compile(
        r"(?<![\w.:/+-])(?:\+\d{1,3}[ .-]?\(?\d{1,4}\)?[ .-]?\d{3,4}[ .-]?\d{3,4}"
        r"|\(\d{3}\)[ .-]?\d{3}[ .-]?\d{4}"
        r"|\d{3}[.-]\d{3}[.-]\d{4}"
        r"|0\d{2,3}[ .-]?\d{3}[ .-]?\d{3,4})(?![\w.:/-])"
    ),
    "cost": re.compile(r"(?<![A-Za-z])(?:intake_|landed_)?cost(?:[_ ]?(?:usd|cny|rmb))?[\"']?\s*[:=]?\s*[\"']?[¥￥$]?\s?[1-9](?![\d.]*\s+(?:mã|m\\u00e3))", re.I),
    "email": re.compile(r"(?<![\w.%+-])[A-Za-z0-9][A-Za-z0-9._%+-]*@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)*\.[A-Za-z]{2,}"),
}
RULES["cost_table"] = None  # markdown table cell under a ¥/cny/cost/landed header (see table_cost_cols)
STRICT_RULES: dict[str, re.Pattern] = {
    "yen_any": re.compile(r"[¥￥]"),
    "cny_word": re.compile(r"(?<![A-Za-z])(?:CNY|RMB)(?![A-Za-z])"),
    "intake_cny_word": re.compile(r"intake_cny", re.I),
    "taobao_word": re.compile(r"taobao", re.I),
    "tb_cn_word": re.compile(r"(?<![\w-])tb\.cn\b", re.I),
    "1688_word": re.compile(r"(?<![\w.])1688(?![\w])"),
    "supplier_word": re.compile(r"supplier", re.I),
}
ACTIVE = dict(RULES)
SKIP_DIRS = {".git", "node_modules", ".next", "__pycache__", ".pytest_cache", ".venv", "venv"}
MAX_BYTES = 5 * 1024 * 1024


@dataclass
class Hit:
    path: str
    line: int
    rule: str
    text: str


def load_allowlist(path: str | None) -> list[dict]:
    if not path:
        return []
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, list):
        raise ValueError("allowlist must be a JSON list")
    for e in data:
        if not isinstance(e, dict) or not e.get("path") or not str(e.get("reason", "")).strip():
            raise ValueError(f"allowlist entry needs path + reason: {e!r}")
    return data


def allowed(rel: str, rule: str, allow: list[dict], whole_file_only: bool = False) -> bool:
    rel = rel[2:] if rel.startswith("./") else rel
    for e in allow:
        if fnmatch.fnmatchcase(rel, e["path"]) or fnmatch.fnmatchcase(rel, "*/" + e["path"]):
            rules = e.get("rules")
            if whole_file_only:
                if not rules:
                    return True
                continue
            if not rules or rule in rules:
                return True
    return False


def _redact(s: str) -> str:
    # never echo the leaked value itself into logs: digits -> '#', emails/links masked
    s = RULES["email"].sub("[email]", s.strip())
    s = re.sub(r"https?://\S+", "[link]", s)
    s = re.sub(r"\d", "#", s)
    return s if len(s) <= 160 else s[:157] + "..."


COST_COL = re.compile(r"[¥￥]|cny|rmb|landed|cost", re.I)
NUM_CELL = re.compile(r"^\s*[¥￥$]?\s?" + NUM + r"\s*$")


def _cells(line: str) -> list[str] | None:
    t = line.strip()
    if not (t.startswith("|") and t.endswith("|")):
        return None
    return [c.strip() for c in t[1:-1].split("|")]


def table_cost_cols(lines: list[str]):
    """Yield (index, cost-column indexes) for markdown table body rows whose header names a cost column."""
    cols: list[int] = []
    for i, line in enumerate(lines):
        c = _cells(line)
        if c is None:
            cols = []
            continue
        if all(re.fullmatch(r":?-{3,}:?", x or "---") for x in c):
            continue
        if not cols and i + 1 < len(lines) and (_cells(lines[i + 1]) or [""])[0].startswith("---"):
            cols = [k for k, x in enumerate(c) if COST_COL.search(x)]
            continue
        if cols:
            yield i, cols, c


def scan_text(rel: str, text: str, allow: list[dict], line_numbers=None) -> list[Hit]:
    hits = []
    lines = text.splitlines()
    if line_numbers is None and "cost_table" in ACTIVE:
        for i, cols, c in table_cost_cols(lines):
            if any(k < len(c) and NUM_CELL.match(c[k]) for k in cols) and not allowed(rel, "cost_table", allow):
                hits.append(Hit(rel, i + 1, "cost_table", _redact(lines[i])))
    for i, line in enumerate(lines, 1):
        ln = line_numbers[i - 1] if line_numbers else i
        for rule, rx in ACTIVE.items():
            if rx is None:
                continue
            if rx.search(line) and not allowed(rel, rule, allow):
                hits.append(Hit(rel, ln, rule, _redact(line)))
    return hits


PATCH_EXT = (".patch", ".diff")


ARCHIVE_PATH = re.compile(r"(?:^|/)out/archive(?:/|$)")


def archive_hit(rel: str) -> list[Hit]:
    """Piece 92: out/archive/ may hold costs; any such path in a repo diff or bundle is a hit."""
    return [Hit(rel, 0, "archive_path", "out/archive must never enter repo or bundle")] if ARCHIVE_PATH.search(rel) else []


def scan_file_text(rel: str, txt: str, allow: list[dict]) -> list[Hit]:
    """Patches are scanned as diffs: only added lines, allowlisted by the path *inside* the patch."""
    if archive_hit(rel):
        return archive_hit(rel)
    if rel.endswith(PATCH_EXT):
        return [Hit(f"{rel}::{h.path}", h.line, h.rule, h.text)
                for h in scan_diff_text(txt, allow, outer=rel)]
    return scan_text(rel, txt, allow)


def _decode(b: bytes) -> str | None:
    if b"\x00" in b[:8192]:
        return None  # binary
    return b.decode("utf-8", errors="replace")


def scan_path(root: str, allow: list[dict]) -> list[Hit]:
    hits: list[Hit] = []
    if os.path.isfile(root) and tarfile.is_tarfile(root):  # by content, so foo.tgz.bak-* is scanned too
        with tarfile.open(root) as tf:
            for m in tf.getmembers():
                if not m.isfile() or m.size > MAX_BYTES:
                    continue
                if any(part in SKIP_DIRS for part in m.name.split("/")):
                    continue
                f = tf.extractfile(m)
                txt = _decode(f.read()) if f else None
                if txt is not None:
                    hits += scan_file_text(m.name, txt, allow)
        return hits
    if os.path.isfile(root):
        with open(root, "rb") as f:
            txt = _decode(f.read(MAX_BYTES))
        return scan_file_text(os.path.basename(root), txt, allow) if txt is not None else []
    for d, dirs, files in os.walk(root):
        dirs[:] = sorted(x for x in dirs if x not in SKIP_DIRS)
        for fn in sorted(files):
            p = os.path.join(d, fn)
            if os.path.islink(p) or os.path.getsize(p) > MAX_BYTES:
                continue
            with open(p, "rb") as f:
                txt = _decode(f.read())
            if txt is not None:
                hits += scan_file_text(os.path.relpath(p, root), txt, allow)
    return hits


def scan_git_diff(rng: str, repo: str, allow: list[dict]) -> list[Hit]:
    out = subprocess.run(["git", "-C", repo, "diff", "--no-color", "--unified=0", rng],
                         capture_output=True, check=True).stdout.decode("utf-8", "replace")
    return scan_diff_text(out, allow)


def scan_diff_text(diff: str, allow: list[dict], outer: str | None = None) -> list[Hit]:
    hits: list[Hit] = []
    cur, ln = None, 0
    for line in diff.splitlines():
        if line.startswith("+++ "):
            cur = line[4:]
            cur = cur[2:] if cur.startswith("b/") else (None if cur == "/dev/null" else cur)
            if cur:
                hits += archive_hit(cur)
        elif line.startswith("@@"):
            m = re.search(r"\+(\d+)", line)
            ln = int(m.group(1)) if m else 0
        elif line.startswith("+") and cur:
            if outer and allowed(outer, "*", allow, whole_file_only=True):
                pass
            else:
                hits += scan_text(cur, line[1:], allow, [ln])
            ln += 1
    return hits


# ---- redaction (for proof files that captured real shop data) ----
R = "[redacted]"
_KEY = r"(?:\w*(?:cny|Cny|CNY|rmb|cost|Cost|landed|Landed)\w*)"
REDACTIONS: list[tuple[re.Pattern, str]] = [
    (re.compile(r"https?://\S*(?:taobao\.com|tmall\.com|tb\.cn|1688\.com)[^\s\"'<>)]*", re.I), "[redacted-link]"),
    (re.compile(r"(?<![\w-])(?:m\.|e\.)?tb\.cn/[^\s\"'<>)]*", re.I), "[redacted-link]"),
    # JSON / dict / kwarg forms: "intake_cny": 123  |  "cost_cny": "45.6"  |  cost_usd=12
    (re.compile(r"([\"']?" + _KEY + r"[\"']?\s*:\s*)\"?-?" + NUM + r"(?:;" + NUM + r")*\"?(?=\s*(?:[,}\]]|$))", re.M), r'\1"' + R + '"'),
    (re.compile(r"(\b" + _KEY + r"\s*=\s*)[\"']?" + NUM + r"[\"']?"), r"\1" + R),
    (re.compile(r"([¥￥]\s?)" + NUM), r"\1" + R),
    (re.compile(r"(?<![A-Za-z\d.])" + NUM + r"(\s?[¥￥])"), R + r"\1"),
    (re.compile(r"(?<![A-Za-z\d.])" + NUM + r"(\s?(?:CNY|RMB)\b)"), R + r"\1"),
    (re.compile(r"(\b(?:CNY|RMB)\s?)" + NUM), r"\1" + R),
    # prose: "$ cost 1.23", "Cost $12", "landed $4.56", "cost ¥12 / $5.10"
    (re.compile(r"((?<![A-Za-z])(?:cost|landed)(?:_[a-z]+)?\s*(?:\$\s?)?)" + NUM, re.I), r"\1" + R),
    (re.compile(r"([¥￥]\[redacted\]\s*/\s*\$\s?)" + NUM), r"\1" + R),
    (re.compile(r"(?<![\w.%+-])[A-Za-z0-9][A-Za-z0-9._%+-]*@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)*\.[A-Za-z]{2,}"), "[redacted-email]"),
    (re.compile(RULES["phone"].pattern), "[redacted-phone]"),
]


_CEIL = re.compile(r"ceil\(\(?[^\n]*?\[redacted\][^\n]*?\)\s*=\s*ceil\(" + NUM + r"\)")


def redact_text(text: str) -> str:
    lines = text.split("\n")
    for i, cols, c in list(table_cost_cols(lines)):
        for k in cols:
            if k < len(c) and NUM_CELL.match(c[k]):
                c[k] = R
        lines[i] = "| " + " | ".join(c) + " |"
    text = "\n".join(lines)
    for rx, rep in REDACTIONS:
        text = rx.sub(rep, text)
    # a worked formula ending in ceil(4.56) still reveals the cost: drop the whole formula
    return _CEIL.sub("ceil([redacted])", text)


def default_allowlist() -> str | None:
    p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "privacy-allowlist.json")
    return os.path.normpath(p) if os.path.exists(p) else None


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("paths", nargs="*")
    ap.add_argument("--git-diff", action="append", default=[], metavar="BASE..HEAD")
    ap.add_argument("--repo", default=".")
    ap.add_argument("--allowlist")
    ap.add_argument("--no-allowlist", action="store_true")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--redact", nargs=2, metavar=("SRC", "DST"), help="write a redacted copy of SRC to DST and exit")
    ap.add_argument("--strict", action="store_true", help="also flag bare tokens (¥, CNY, taobao, supplier, ...)")
    try:
        a = ap.parse_args(argv)
    except SystemExit as e:
        return 2 if e.code else 0
    if not a.paths and not a.git_diff and not a.redact:
        print("usage: give a PATH or --git-diff BASE..HEAD", file=sys.stderr)
        return 2
    if a.redact:
        src, dst = a.redact
        if not os.path.isfile(src):
            print(f"no such file: {src}", file=sys.stderr)
            return 2
        with open(src, encoding="utf-8", errors="replace") as f:
            out = redact_text(f.read())
        os.makedirs(os.path.dirname(os.path.abspath(dst)), exist_ok=True)
        with open(dst, "w", encoding="utf-8") as f:
            f.write(out)
        print(f"redacted {src} -> {dst}")
        return 0
    ACTIVE.clear(); ACTIVE.update(RULES)
    if a.strict:
        ACTIVE.update(STRICT_RULES)
    try:
        allow = [] if a.no_allowlist else load_allowlist(a.allowlist or default_allowlist())
        hits: list[Hit] = []
        for p in a.paths:
            if not os.path.exists(p):
                print(f"no such path: {p}", file=sys.stderr)
                return 2
            hits += scan_path(p, allow)
        for r in a.git_diff:
            if ".." not in r:
                print(f"bad range: {r}", file=sys.stderr)
                return 2
            hits += scan_git_diff(r, a.repo, allow)
    except (ValueError, OSError, json.JSONDecodeError, subprocess.CalledProcessError, tarfile.TarError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 2
    if a.json:
        print(json.dumps({"hits": [asdict(h) for h in hits], "count": len(hits)}, ensure_ascii=False, indent=1))
    else:
        for h in hits:
            print(f"{h.path}:{h.line}: [{h.rule}] {h.text}")
        print(f"privacy_scan: {'CLEAN' if not hits else f'{len(hits)} HIT(S)'}")
    return 1 if hits else 0


if __name__ == "__main__":
    sys.exit(main())
