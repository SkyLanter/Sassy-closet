#!/usr/bin/env python3
"""caption_lint.py - lint Sassy Closet IG/FB caption text files (read-only).

Usage: python3 caption_lint.py --prices prices.json caption1.txt [caption2.txt ...]

A caption may be multi-line, or a single line using " / " as the line break
(the way captions are quoted in chat). Exit code 1 if any flag, else 0.
"""
import argparse
import json
import re
import sys
import unicodedata

# word (no accents, lowercase) -> correct Vietnamese
ACCENT_FIXES = {
    "mc": "mặc",
    "mu": "màu",
    "tnh": "tính",
    "khng": "không",
}
MA_OK = re.compile(r"^Mã\s+([A-Z]\d{2})\b")
MA_CODE = re.compile(r"\b([A-Z]\d{2})\b")
GIA_STRICT = re.compile(r"^Giá \$(\d+)\s*$")
GIA_ANY = re.compile(r"\bgi[aáàảãạ]\b", re.I)
SIZE_TOKENS = {"S", "M", "L", "XL", "XS", "XXL", "OS", "ONE"}


def split_lines(text):
    text = unicodedata.normalize("NFC", text).replace("\r\n", "\n").strip()
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    if len(lines) == 1 and " / " in lines[0]:
        segs = [s.strip() for s in lines[0].split(" / ")]
        merged = []
        for s in segs:
            # "Size S / M / L": re-attach bare size tokens to the Size line
            if merged and s.upper() in SIZE_TOKENS and re.match(r"^Size\b", merged[-1]):
                merged[-1] += " / " + s
            else:
                merged.append(s)
        lines = merged
    return lines


def lint_text(text, prices):
    """Return list of (code, message)."""
    flags = []
    lines = split_lines(text)
    if not lines:
        return [("EMPTY", "caption is empty")]
    first = lines[0]
    m = MA_OK.match(first)
    code = None
    if m:
        code = m.group(1)
    else:
        mc = MA_CODE.search(first)
        code = mc.group(1) if mc else None
        if re.match(r"^M\s+[A-Z]\d{2}\b", first):
            flags.append(("MA_MISSING_ACCENT", f'line 1 reads "{first[:20]}": "M" should be "Mã"'))
        elif re.match(r"^Ma\s+[A-Z]\d{2}\b", first):
            flags.append(("MA_MISSING_ACCENT", f'line 1 reads "{first[:20]}": "Ma" should be "Mã"'))
        else:
            flags.append(("NO_MA_LINE", 'line 1 is not "Mã XNN"'))
    # accents in common words (whole text, lowercase)
    lower = "\n".join(lines).lower()
    for bad, good in ACCENT_FIXES.items():
        if re.search(rf"(?<![\w]){bad}(?![\w])", lower):
            flags.append(("MISSING_ACCENT", f'"{bad}" should be "{good}"'))
    # Giá
    gia_lines = [l for l in lines if GIA_ANY.search(l) or re.match(r"^gi", l, re.I) and "$" in l]
    gia_val = None
    if not gia_lines:
        flags.append(("NO_GIA", 'no "Giá $NN" line'))
    else:
        gl = gia_lines[-1]
        gm = GIA_STRICT.match(gl)
        if not gm:
            flags.append(("GIA_MALFORMED", f'"{gl}" is not exactly "Giá $NN"'))
            nm = re.search(r"\$\s*(\d+)", gl)
            if nm:
                gia_val = int(nm.group(1))
        else:
            gia_val = int(gm.group(1))
    if gia_val is not None and code:
        if code not in prices:
            flags.append(("PRICE_UNKNOWN", f"{code} not in price list (Giá ${gia_val} on caption)"))
        elif int(prices[code]) != gia_val:
            flags.append(("GIA_MISMATCH", f"{code}: caption ${gia_val} vs price list ${prices[code]}"))
    elif gia_val is not None and not code:
        flags.append(("PRICE_UNCHECKED", "no mã code found, cannot compare Giá to price list"))
    # Size
    if not any(re.match(r"^Size\b", l) for l in lines):
        flags.append(("NO_SIZE", 'no "Size" line'))
    return flags


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--prices", required=True, help='JSON file like {"A09":26,"S06":25}')
    ap.add_argument("captions", nargs="+", help="plain-text caption files")
    a = ap.parse_args(argv)
    with open(a.prices, encoding="utf-8") as f:
        prices = json.load(f)
    total = 0
    for path in a.captions:
        with open(path, encoding="utf-8") as f:
            flags = lint_text(f.read(), prices)
        if flags:
            for c, msg in flags:
                print(f"{path}: FLAG {c}: {msg}")
            total += len(flags)
        else:
            print(f"{path}: OK")
    print(f"{total} flag(s) in {len(a.captions)} file(s)")
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main())
