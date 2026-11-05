#!/usr/bin/env python3
"""Read-only: OneDrive mirror sell USD vs live Blob sell USD from a committed fixture.
Prints a markdown table. Writes nothing; never touches OneDrive/Blob. Sell dollars only.

Every spelling of a mã is kept. A later S06 at $25 does not hide an earlier
S006 at another price. No price is rewritten.
"""
import argparse, json, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from held_policy import norm_ma  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "docs/fixtures/onedrive-mirror/mirror-vs-live-2026-10-28.json"


def _equal(left, right):
    """25.0 matches 25. A boolean does not match a dollar."""
    if isinstance(left, bool) or isinstance(right, bool):
        return isinstance(left, bool) and isinstance(right, bool) and left is right
    return left == right


def _group(mapping):
    grouped = {}
    for key, value in mapping.items():
        grouped.setdefault(norm_ma(key), []).append(value)
    return grouped


def _agreed(values):
    return all(_equal(value, values[-1]) for value in values)


def compare(mirror, live):
    grouped_mirror = _group(mirror)
    grouped_live = _group(live)
    rows = []
    for ma in sorted(grouped_mirror):
        mirror_prices = grouped_mirror[ma]
        live_prices = grouped_live.get(ma)
        if live_prices is None or (_agreed(live_prices) and live_prices[-1] is None):
            status = "NO_LIVE"
        elif (
            not _agreed(mirror_prices)
            or not _agreed(live_prices)
            or not _equal(mirror_prices[-1], live_prices[-1])
        ):
            status = "DRIFT"
        else:
            status = "MATCH"
        rows.append((ma, mirror_prices, live_prices, status))
    return rows


def _one(value):
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return f"{value:g}"
    return str(value)


def _cell(values):
    if not values:
        return "—"
    if _agreed(values):
        value = values[-1]
        return "—" if value is None else _one(value)
    return ", ".join(_one(value) for value in values)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--fixture", default=str(FIXTURE))
    ap.add_argument("--strict", action="store_true", help="exit 1 if any drift")
    a = ap.parse_args(argv)
    d = json.loads(Path(a.fixture).read_text())
    rows = compare(d.get("od_mirror", {}), d.get("live", {}))
    print("| mã | OneDrive mirror | live | status |\n|---|---|---|---|")
    for ma, mirror_prices, live_prices, status in rows:
        print(f"| {ma} | {_cell(mirror_prices)} | {_cell(live_prices)} | {status} |")
    n = sum(status != "MATCH" for _ma, _mirror, _live, status in rows)
    print(f"\n{n} mismatch(es). Read-only; mirror refresh needs Boss OK.")
    return 1 if (a.strict and n) else 0


if __name__ == "__main__":
    sys.exit(main())
