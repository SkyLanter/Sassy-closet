"""Read-only check for intake mã codes reused for different items.

Reads intake exports (``{"submissions": [...]}`` JSON, CSV with a ``ma``
column, or markdown tables with a ``Mã`` column) and flags any mã that has
more than one row where the date, title or Taobao item ID differ.

Output is only: mã, row count, dates. Costs, links, item IDs, titles and
customer data are never printed. Nothing is written anywhere.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from held_policy import norm_ma

MA_RE = re.compile(r"^[A-Z]\d{2}$")
ITEM_ID_RE = re.compile(r"[?&]id=(\d+)")
DATE_RE = re.compile(r"(\d{4}-\d{2}-\d{2})")
TITLE_KEYS = ("title", "name")
LINK_KEYS = ("link", "source_link", "taobao_link", "url")
DATE_KEYS = ("created_at", "date", "intake_date")


@dataclass(frozen=True)
class Row:
    ma: str
    date: str
    title: str
    item_id: str


def _date(v) -> str:
    m = DATE_RE.search(str(v or ""))
    return m.group(1) if m else ""


def _item_id(v) -> str:
    m = ITEM_ID_RE.search(str(v or ""))
    return m.group(1) if m else ""


def _first(d: dict, keys) -> str:
    for k in keys:
        if d.get(k):
            return str(d[k]).strip()
    return ""


def row_from_dict(d: dict, default_date: str = "") -> Row | None:
    norm = {str(k).strip().lower().replace("ã", "a"): v for k, v in d.items()}
    ma = norm_ma(str(norm.get("ma") or norm.get("code") or ""))
    if not MA_RE.match(ma):
        return None
    return Row(ma, _date(_first(norm, DATE_KEYS)) or default_date,
               _first(norm, TITLE_KEYS).lower(), (str(norm.get("item_id") or "").strip() or _item_id(_first(norm, LINK_KEYS))))


def load_rows(path: Path) -> list[Row]:
    text = path.read_text(encoding="utf-8-sig")
    suf = path.suffix.lower()
    if suf == ".json":
        data = json.loads(text)
        items = data.get("submissions", []) if isinstance(data, dict) else data
        return [r for r in (row_from_dict(x) for x in items if isinstance(x, dict)) if r]
    if suf == ".csv":
        return [r for r in (row_from_dict(x) for x in csv.DictReader(text.splitlines())) if r]
    if suf == ".md":
        return _md_rows(text, _date(path.name))
    raise ValueError(f"unsupported file type: {path.name}")


def _md_rows(text: str, default_date: str) -> list[Row]:
    rows: list[Row] = []
    header: list[str] | None = None
    for line in text.splitlines():
        s = line.strip()
        if not s.startswith("|"):
            header = None
            continue
        cells = [c.strip() for c in s.strip("|").split("|")]
        if header is None:
            header = cells
            continue
        if all(set(c) <= set("-: ") for c in cells):
            continue
        d = dict(zip(header, cells))
        r = row_from_dict(d, default_date)
        if r:
            rows.append(r)
    return rows


def find_reuse(rows: list[Row]) -> list[dict]:
    by: dict[str, list[Row]] = {}
    for r in rows:
        by.setdefault(r.ma, []).append(r)
    out = []
    for ma in sorted(by):
        rs = by[ma]
        if len(rs) < 2:
            continue
        differ = any(len({getattr(r, f) for r in rs if getattr(r, f)}) > 1
                     for f in ("date", "title", "item_id"))
        if differ:
            out.append({"ma": ma, "rows": len(rs),
                        "dates": sorted({r.date for r in rs if r.date})})
    return out


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("files", nargs="+", type=Path)
    p.add_argument("--json", action="store_true")
    a = p.parse_args(argv)
    rows: list[Row] = []
    for f in a.files:
        rows.extend(load_rows(f))
    flags = find_reuse(rows)
    if a.json:
        print(json.dumps({"rows_read": len(rows), "reused": flags}))
    else:
        for f in flags:
            print(f"REUSED {f['ma']} rows={f['rows']} dates={','.join(f['dates']) or '-'}")
        if not flags:
            print(f"OK no reused codes ({len(rows)} rows)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
