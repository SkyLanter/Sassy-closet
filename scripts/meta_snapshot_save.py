#!/usr/bin/env python3
"""Piece 60: offline Meta snapshot saver for Sassy Closet.

Turns a hand/Muse/QC-filled caption-check sheet (CSV or JSON, one row per
post) into the structured snapshot that meta_caption_gap_report reads.

Input columns: platform, media_type, post_id, ma, has_gia, checked_at
(post_id may also be given as "id"). Caption text is never read or stored:
any "caption" column is dropped. Output goes to
    out/meta-snapshot/meta-snapshot-<UTC stamp>.json (out/ is gitignored).

No network, no Meta calls. A stale sheet still saves; staleness is a report
line. Exit: 0 saved or dry-run with no bad rows, 1 bad rows or nothing valid,
2 usage, unreadable input, or bad --as-of.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from dataclasses import dataclass
from datetime import date, datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "out" / "meta-snapshot"
PT = ZoneInfo("America/Los_Angeles")
PLAT = {"fb": "fb", "facebook": "fb", "ig": "ig", "instagram": "ig"}
MEDIA = {"post", "reel", "story", "carousel", "photo", "video"}
MA_RE = re.compile(r"^[A-Z][0-9]{2}$")
_AS_OF_RE = re.compile(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}$")
_BAD_AS_OF = "bad --as-of, want YYYY-MM-DD"
TRUE = {"1", "true", "yes", "y", "t"}
FALSE = {"0", "false", "no", "n", "f", ""}
FIELDS = ("platform", "media_type", "id", "ma", "has_gia", "checked_at")


@dataclass
class Sheet:
    """Kept posts, rejected rows, and how many kept stamps had no timezone."""

    posts: list[dict]
    bad: list[tuple[int, str]]
    assumed_zone: int


def today_pt(now: datetime | None = None) -> date:
    """Calendar date in America/Los_Angeles. A naive now is read in that zone."""
    if now is None:
        now = datetime.now(PT)
    elif now.tzinfo is None:
        now = now.replace(tzinfo=PT)
    else:
        now = now.astimezone(PT)
    return now.date()


def parse_as_of(raw: str | None) -> tuple[date | None, str | None]:
    """Return (date, None) or (None, error). None raw means today in Los Angeles."""
    if raw is None:
        return today_pt(), None
    if isinstance(raw, str) and _AS_OF_RE.fullmatch(raw):
        try:
            return date.fromisoformat(raw), None
        except ValueError:
            return None, _BAD_AS_OF
    return None, _BAD_AS_OF


def read_rows(path: Path):
    if path.suffix.lower() == ".csv":
        with path.open(newline="", encoding="utf-8-sig") as f:
            return list(csv.DictReader(f))
    d = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(d, dict):
        d = d.get("posts", [])
    if not isinstance(d, list):
        raise ValueError("JSON must be a list or {\"posts\": [...]}")
    return d


def _parse_checked_at(raw: str) -> tuple[str | None, bool]:
    """Return (stored isoformat, original had no timezone). Invalid -> (None, False)."""
    text = raw.strip()
    try:
        dt = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError:
        return None, False
    naive = dt.tzinfo is None
    if naive:
        dt = dt.replace(tzinfo=PT)
    return dt.isoformat(), naive


def _aware(iso: str) -> datetime:
    """Stored checked_at as an aware instant. A naive stamp is Los Angeles."""
    dt = datetime.fromisoformat(iso.strip().replace("Z", "+00:00"))
    if dt.tzinfo is None:
        return dt.replace(tzinfo=PT)
    return dt


def checked_on(iso: str) -> date:
    """Calendar date of a stored checked_at, read in America/Los_Angeles."""
    return _aware(iso).astimezone(PT).date()


def normalize_sheet(rows) -> Sheet:
    good: list[tuple[dict, bool]] = []
    bad: list[tuple[int, str]] = []
    for n, r in enumerate(rows, 1):
        if not isinstance(r, dict):
            bad.append((n, "not_an_object"))
            continue
        r = {str(k).strip().lower(): ("" if v is None else str(v).strip()) for k, v in r.items()}
        plat = PLAT.get(r.get("platform", "").lower())
        media = (r.get("media_type") or "post").lower()
        pid = r.get("post_id") or r.get("id") or ""
        ma = r.get("ma", "").upper()
        hg = r.get("has_gia", "").lower()
        ts, naive = _parse_checked_at(r.get("checked_at", ""))
        errs = []
        if not plat:
            errs.append("platform")
        if media not in MEDIA:
            errs.append("media_type")
        if not pid:
            errs.append("post_id")
        if ma and not MA_RE.match(ma):
            errs.append("ma")
        if hg not in TRUE | FALSE:
            errs.append("has_gia")
        if ts is None:
            errs.append("checked_at")
        if errs:
            bad.append((n, ",".join(errs)))
            continue
        good.append(({"platform": plat, "media_type": media, "id": pid,
                      "ma": ma or None, "has_gia": hg in TRUE, "checked_at": ts}, naive))
    # de-dup by (platform, id): keep the later instant. Offset strings do not
    # sort in time order, so a later clock-text can be an earlier check.
    # Equal instants keep the first row. assumed_zone counts survivors only.
    best: dict[tuple[str, str], tuple[dict, bool]] = {}
    for post, naive in good:
        key = (post["platform"], post["id"])
        if key not in best or _aware(post["checked_at"]) > _aware(best[key][0]["checked_at"]):
            best[key] = (post, naive)
    kept = sorted(best.values(), key=lambda item: (item[0]["platform"], item[0]["id"]))
    posts = [item[0] for item in kept]
    assumed_zone = sum(1 for item in kept if item[1])
    return Sheet(posts, bad, assumed_zone)


def normalize(rows):
    sheet = normalize_sheet(rows)
    return sheet.posts, sheet.bad


def _freshness_lines(posts, as_of: date, assumed_zone: int) -> list[str]:
    lines: list[str] = []
    if assumed_zone == 1:
        lines.append("NOTE 1 checked_at value had no timezone; read as America/Los_Angeles")
    elif assumed_zone > 1:
        lines.append(
            f"NOTE {assumed_zone} checked_at values had no timezone; read as America/Los_Angeles")
    dates = [checked_on(p["checked_at"]) for p in posts]
    latest = max(dates)
    older = sum(1 for d in dates if d < as_of)
    latest_s = latest.isoformat()
    as_of_s = as_of.isoformat()
    if latest < as_of:
        lines.append(f"STALE latest checked_at {latest_s} America/Los_Angeles is before {as_of_s}")
    elif latest > as_of:
        lines.append(f"NOTE latest checked_at {latest_s} America/Los_Angeles is after {as_of_s}")
    else:
        lines.append(f"OK checked_at {latest_s} America/Los_Angeles")
    if older > 0 and latest >= as_of:
        if older == 1:
            lines.append(f"NOTE 1 post checked before {as_of_s}")
        else:
            lines.append(f"NOTE {older} posts checked before {as_of_s}")
    return lines


def render_status(posts, bad, *, as_of: date, assumed_zone: int = 0, outcome: str) -> str:
    lines = [f"REJECT row {n}: {why}" for n, why in bad]
    if outcome == "saved":
        lines.extend(_freshness_lines(posts, as_of, assumed_zone))
        lines.append(f"saved posts={len(posts)}")
    elif outcome == "dry-run":
        lines.extend(_freshness_lines(posts, as_of, assumed_zone))
        lines.append(f"dry-run OK posts={len(posts)}")
    elif outcome == "not-saved":
        if bad:
            lines.append(f"not saved: {len(bad)} bad row(s)")
        else:
            lines.append("MISSING no meta snapshot rows")
            lines.append("not saved")
    else:
        raise ValueError("unknown outcome")
    return "\n".join(lines) + "\n"


def save(posts, out_dir: Path, now=None, *, as_of: date | None = None,
         latest_checked_on: date | None = None, stale: bool | None = None) -> Path:
    now = now or datetime.now(timezone.utc)
    out_dir.mkdir(parents=True, exist_ok=True)
    stamp = now.strftime("%Y%m%dT%H%M%SZ")
    path = out_dir / f"meta-snapshot-{stamp}.json"
    doc = {"kind": "meta-snapshot", "version": 1, "saved_at": now.isoformat()}
    if as_of is not None:
        doc["as_of"] = as_of.isoformat()
        doc["latest_checked_on"] = latest_checked_on.isoformat()
        doc["stale"] = bool(stale)
    doc["platforms"] = sorted({p["platform"] for p in posts})
    doc["posts"] = posts
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(doc, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    tmp.replace(path)
    return path


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("input", type=Path)
    ap.add_argument("--out-dir", type=Path, default=OUT_DIR)
    ap.add_argument("--allow-partial", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--as-of", default=None, help="YYYY-MM-DD in America/Los_Angeles (default: today)")
    a = ap.parse_args(argv)
    as_of, err = parse_as_of(a.as_of)
    if err is not None or as_of is None:
        print(_BAD_AS_OF, file=sys.stderr)
        return 2
    try:
        rows = read_rows(a.input)
    except FileNotFoundError:
        print("MISSING meta snapshot input", file=sys.stderr)
        return 2
    except (OSError, ValueError, UnicodeDecodeError, json.JSONDecodeError) as e:
        print(f"usage: cannot read input: {type(e).__name__}", file=sys.stderr)
        return 2
    sheet = normalize_sheet(rows)
    posts, bad = sheet.posts, sheet.bad
    status = {"as_of": as_of, "assumed_zone": sheet.assumed_zone}
    if bad and not a.allow_partial:
        print(render_status(posts, bad, outcome="not-saved", **status), end="")
        return 1
    if not posts:
        print(render_status(posts, bad, outcome="not-saved", **status), end="")
        return 1
    if a.dry_run:
        print(render_status(posts, bad, outcome="dry-run", **status), end="")
        return 1 if bad else 0
    latest = max(checked_on(p["checked_at"]) for p in posts)
    path = save(posts, a.out_dir, as_of=as_of, latest_checked_on=latest, stale=latest < as_of)
    text = render_status(posts, bad, outcome="saved", **status)
    lines = text.splitlines()
    lines[-1] = f"{lines[-1]} -> {path}"
    print("\n".join(lines) + "\n", end="")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
