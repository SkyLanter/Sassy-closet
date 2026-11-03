# out/local-tools

Local, read-only helper tools. No network, no pushes, no live/Meta/Blob/hub/OneDrive/price changes, no messages.
Python 3.13 stdlib only; tests need pytest (installed in a throwaway venv at /tmp/venv because system pip is locked: `python3 -m venv /tmp/venv && /tmp/venv/bin/pip install pytest`).

Run all tests: `cd /workspace/sassy-closet/out/local-tools && /tmp/venv/bin/pytest -q`

## 1. caption_lint.py
Lints caption text files against a price list JSON. Exit 1 if any flag.
```
python3 caption_lint.py --prices fixtures/captions/prices.json fixtures/captions/*.txt
```
Flags: NO_MA_LINE, MA_MISSING_ACCENT ("M A09", "Ma D06"), MISSING_ACCENT (mc/mu/tnh/khng), NO_GIA, GIA_MALFORMED (e.g. "Giá $ 32"), GIA_MISMATCH, PRICE_UNKNOWN (mã not in list), PRICE_UNCHECKED (no mã to compare), NO_SIZE.
A caption can be multi-line or one line split by " / " (bare S/M/L after "Size" are kept on the Size line).
Fixtures: a09.txt (A09-style, flagged), s06_clean.txt (clean, S06 $25), a08_no_gia.txt, plus malformed/mismatch/no-size/no-mã cases. prices.json keeps S06 = 25.

## 2. muse_pace.py
```
python3 muse_pace.py --used-pct 0 --reset-date 2026-10-19 --now 2026-10-15T02:49Z --week-days 7
```
Prints window, expected % (straight line), points behind/ahead, and the next not-done item from ../muse/muse-backlog.md (override with --backlog). [PARTIAL...] counts as open; [DONE...] / [x] counts as done. Real run: expected 44.5%, BEHIND by 44.5 points, next = #1 IG full sweep table (partial).

## 3. shop_health.py
```
python3 shop_health.py [--root /workspace/sassy-closet] [--s06-price 25]
```
Real data files found (no network used): auto-list/state/live-catalog-latest.json (local copy of the live Blob catalog), auto-list/state/held.json, auto-list/state/last_check.json. Prints live count, S06 price, held list, held-vs-live overlap, last auto-list check. Exit 1 if S06 != 25, a held mã is in the live catalog, or a file is unreadable. Fixtures (fixtures/health/ok and /bad) are used by the tests only.
Real run: live 62, S06 $25, held 18 (S14 A24 A25 S15 A26 K02 K03 K04 V04 K05 K06 V05 S16 A27 A28 S17 S18 S19), STATUS: OK.

## Test output
```
....................                                                     [100%]
20 passed in 0.21s
```

## Could not verify
- The live site/Blob itself: shop_health reads the local snapshot only. The catalog file's own updatedAt is 2026-09-30 (matches the Blob updatedAt in out/muse/TODAY.md), but file mtime is fresher (auto-list rewrites it), so "live" = last snapshot, not a fresh fetch.
- data/held.json on main: /workspace/sassy-closet has no data/ dir and is not a git repo, so the 12-vs-18 held mismatch noted in TODAY.md can't be checked here; held list comes from auto-list/state/held.json (18).
- verify/_audit_blob_catalog.v1.json is an older Oct 12 snapshot and shows S06 $19, so do not use it as the live source.
- Muse reset time: Muse shows only a date; muse_pace assumes 00:00 UTC (--reset-time overrides). Week start Oct 12 is itself an assumption.
- caption_lint accent list is small (mc, mu, tnh, khng); it cannot catch every dropped letter. Nothing was run against real Meta captions (no access).

## Not the same as scripts/caption_lint.py
`out/local-tools/caption_lint.py` (piece 01) is a standalone text-file tool: a
`--prices` JSON, accent/dropped-letter hints and Size-line checks, exit 1 on
any flag. The repo checker is `scripts/caption_lint.py` (pieces 31 + 33): mã and
Giá format, catalog/held/never-list/S06 price rules on a daily snapshot or
catalog JSON, exit 0/1/2. The old `scripts/caption_gia_check.py` is now a thin
shim over `scripts/caption_lint.py` (same CLI flags and exit codes) used by
`daily_shop_check.py`. The two caption_lint files are not merged.
