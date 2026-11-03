#!/usr/bin/env python3
"""Read-only: OneDrive mirror sell USD vs live Blob sell USD from a committed fixture.
Prints a markdown table. Writes nothing; never touches OneDrive/Blob. Sell dollars only."""
import argparse, json, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from held_policy import norm_ma  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "docs/fixtures/onedrive-mirror/mirror-vs-live-2026-10-28.json"


def compare(mirror, live):
    m = {norm_ma(k): v for k, v in mirror.items()}
    l = {norm_ma(k): v for k, v in live.items()}
    rows = []
    for ma in sorted(m):
        lv = l.get(ma)
        status = "NO_LIVE" if lv is None else ("MATCH" if lv == m[ma] else "DRIFT")
        rows.append((ma, m[ma], lv, status))
    return rows


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--fixture", default=str(FIXTURE))
    ap.add_argument("--strict", action="store_true", help="exit 1 if any drift")
    a = ap.parse_args(argv)
    d = json.loads(Path(a.fixture).read_text())
    rows = compare(d.get("od_mirror", {}), d.get("live", {}))
    print("| mã | OneDrive mirror | live | status |\n|---|---|---|---|")
    for ma, mv, lv, st in rows:
        print(f"| {ma} | {mv:g} | {'—' if lv is None else f'{lv:g}'} | {st} |")
    n = sum(r[3] != "MATCH" for r in rows)
    print(f"\n{n} mismatch(es). Read-only; mirror refresh needs Boss OK.")
    return 1 if (a.strict and n) else 0


if __name__ == "__main__":
    sys.exit(main())
