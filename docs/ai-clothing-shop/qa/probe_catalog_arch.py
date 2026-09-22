#!/usr/bin/env python3
"""Read-only architecture probe for intake + sell-test.

Does not POST, does not invent mã, does not write Blob.
Exit 0 = laws hold. Exit 1 = a law broke. Exit 2 = network / parse failure.
"""

from __future__ import annotations

import json
import re
import sys
import urllib.error
import urllib.request
from html.parser import HTMLParser

INTAKE = "https://sassy-closet.vercel.app"
SHOP = "https://sassy-closet-shop.vercel.app"

ALLOWLIST = ("A01", "S01", "P01", "P02", "P03", "P04", "P05", "K01", "H01", "A02")
HOLD = ("P02", "P05")
BOSS_USD = {
    "A01": 25,
    "S01": 28,
    "P01": 5,
    "P03": 18,
    "P04": 13,
    "K01": 37,
    "H01": 8,
    "A02": 22,
}
INVENTED = "A03"


class _TextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self._skip = False
        self.parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in {"script", "style"}:
            self._skip = True

    def handle_endtag(self, tag: str) -> None:
        if tag in {"script", "style"}:
            self._skip = False

    def handle_data(self, data: str) -> None:
        if not self._skip:
            self.parts.append(data)


def visible_text(html: str) -> str:
    parser = _TextExtractor()
    parser.feed(html)
    return re.sub(r"\s+", " ", "".join(parser.parts))


def fetch(url: str) -> tuple[int, dict[str, str], bytes]:
    req = urllib.request.Request(url, method="GET", headers={"User-Agent": "sassy-catalog-arch-probe"})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            headers = {k.lower(): v for k, v in resp.headers.items()}
            return int(resp.status), headers, resp.read()
    except urllib.error.HTTPError as err:
        headers = {k.lower(): v for k, v in err.headers.items()} if err.headers else {}
        return int(err.code), headers, err.read() or b""


def head(url: str) -> tuple[int, dict[str, str]]:
    req = urllib.request.Request(url, method="HEAD", headers={"User-Agent": "sassy-catalog-arch-probe"})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            headers = {k.lower(): v for k, v in resp.headers.items()}
            return int(resp.status), headers
    except urllib.error.HTTPError as err:
        headers = {k.lower(): v for k, v in err.headers.items()} if err.headers else {}
        return int(err.code), headers


def fail(failures: list[str], message: str) -> None:
    failures.append(message)
    print(f"FAIL  {message}")


def ok(message: str) -> None:
    print(f"ok    {message}")


def main() -> int:
    failures: list[str] = []
    print(f"probe intake={INTAKE}")
    print(f"probe shop={SHOP}")
    print(f"allowlist={' '.join(ALLOWLIST)}")

    if INTAKE == SHOP:
        fail(failures, "intake and shop hosts must stay different")
        return 1

    try:
        intake_status, intake_headers, intake_body = fetch(f"{INTAKE}/api/submissions")
    except OSError as err:
        print(f"network: intake submissions: {err}", file=sys.stderr)
        return 2

    if intake_status != 200:
        fail(failures, f"intake /api/submissions status {intake_status}")
        return 1 if failures else 2

    try:
        payload = json.loads(intake_body.decode("utf-8"))
    except json.JSONDecodeError as err:
        print(f"parse: intake submissions: {err}", file=sys.stderr)
        return 2

    storage = payload.get("storage") or {}
    if storage.get("durable") is not True:
        fail(failures, f"intake storage.durable is {storage!r} (need Blob)")
    else:
        ok("intake storage.durable")

    rows = payload.get("submissions")
    if not isinstance(rows, list):
        fail(failures, "intake submissions is not a list")
        return 1

    intake_mas = [str(row.get("ma", "")) for row in rows if isinstance(row, dict)]
    if INVENTED in intake_mas:
        fail(failures, f"intake invented {INVENTED}")
    else:
        ok(f"intake has no {INVENTED} ({len(intake_mas)} rows)")

    p05 = next((row for row in rows if isinstance(row, dict) and row.get("ma") == "P05"), None)
    if p05 is not None:
        sell = str(p05.get("sell_usd") or p05.get("price") or "").strip()
        ok(f"intake P05 staff sell_usd={sell!r} (must not become catalog.v1 priceUsd)")

    try:
        home_status, home_headers, home_body = fetch(f"{SHOP}/")
    except OSError as err:
        print(f"network: shop /: {err}", file=sys.stderr)
        return 2

    if home_status != 200:
        fail(failures, f"shop / status {home_status}")
    home_html = home_body.decode("utf-8", "replace")
    home_text = visible_text(home_html)
    shop_mas = tuple(sorted(set(re.findall(r"/m/([A-Z]\d{2})", home_html))))
    if shop_mas != tuple(sorted(ALLOWLIST)):
        fail(failures, f"shop tiles {shop_mas} != allowlist")
    else:
        ok("shop home tiles = allowlist of ten")
    if f"/m/{INVENTED}" in home_html:
        fail(failures, f"shop home links /m/{INVENTED}")
    else:
        ok(f"shop home has no /m/{INVENTED}")

    if home_headers.get("x-nextjs-prerender") != "1":
        fail(failures, f"shop / missing x-nextjs-prerender:1 ({home_headers.get('x-nextjs-prerender')})")
    else:
        ok("shop / is prerendered (ISR)")
    if "Hold" not in home_text:
        fail(failures, "shop home visible text missing Hold (P02/P05)")
    else:
        ok(f"shop home shows Hold for {', '.join(HOLD)}")

    for ma, usd in BOSS_USD.items():
        token = f"${usd}"
        if token not in home_text and token not in home_html:
            fail(failures, f"shop home missing {ma} {token}")
    ok("shop home shows Boss available USD")

    try:
        p05_status, p05_headers, p05_body = fetch(f"{SHOP}/m/P05")
    except OSError as err:
        print(f"network: shop /m/P05: {err}", file=sys.stderr)
        return 2

    if p05_status != 200:
        fail(failures, f"shop /m/P05 status {p05_status}")
    p05_text = visible_text(p05_body.decode("utf-8", "replace"))
    if "Hold" not in p05_text:
        fail(failures, "shop /m/P05 visible text missing Hold")
    else:
        ok("shop /m/P05 says Hold")
    if "$23" in p05_text:
        fail(failures, "shop /m/P05 visible text publishes $23")
    else:
        ok("shop /m/P05 does not publish $23")
    if p05_headers.get("x-nextjs-prerender") != "1":
        fail(failures, "shop /m/P05 is not prerendered")

    try:
        a01_status, _, a01_body = fetch(f"{SHOP}/m/A01")
    except OSError as err:
        print(f"network: shop /m/A01: {err}", file=sys.stderr)
        return 2
    if a01_status != 200:
        fail(failures, f"shop /m/A01 status {a01_status}")
    a01_text = visible_text(a01_body.decode("utf-8", "replace"))
    if "$25" not in a01_text:
        fail(failures, "shop /m/A01 missing $25")
    else:
        ok("shop /m/A01 shows $25")

    try:
        a03_status, a03_headers, _ = fetch(f"{SHOP}/m/{INVENTED}")
    except OSError as err:
        print(f"network: shop /m/{INVENTED}: {err}", file=sys.stderr)
        return 2
    if a03_status != 404:
        fail(failures, f"shop /m/{INVENTED} status {a03_status} (need 404)")
    else:
        cache = a03_headers.get("x-vercel-cache", "")
        ok(f"shop /m/{INVENTED} 404 (cache={cache})")

    for path in ("/api/catalog", "/api/admin/catalog"):
        try:
            status, _headers = head(f"{SHOP}{path}")
        except OSError as err:
            print(f"network: shop {path}: {err}", file=sys.stderr)
            return 2
        if status != 404:
            fail(failures, f"shop {path} status {status} (import API not landed; expected 404)")
        else:
            ok(f"shop {path} still 404")

    try:
        admin_status, admin_headers, admin_body = fetch(f"{SHOP}/admin")
    except OSError as err:
        print(f"network: shop /admin: {err}", file=sys.stderr)
        return 2
    if admin_status != 200:
        fail(failures, f"shop /admin status {admin_status}")
    admin_cc = admin_headers.get("cache-control", "")
    if "no-store" not in admin_cc:
        fail(failures, f"shop /admin cache-control={admin_cc!r}")
    else:
        ok("shop /admin is no-store")
    admin_html = admin_body.decode("utf-8", "replace")
    if "Vercel Blob" not in admin_html:
        fail(failures, "shop /admin missing Vercel Blob marker")
    else:
        ok("shop /admin Storage: Vercel Blob")
    if "Next mã" in admin_html and INVENTED in admin_html:
        ok(f"shop /admin still suggests Next mã {INVENTED} — ignore, do not publish")

    try:
        intake_home_status, intake_home_headers = head(f"{INTAKE}/")
    except OSError as err:
        print(f"network: intake /: {err}", file=sys.stderr)
        return 2
    if intake_home_status != 200:
        fail(failures, f"intake / status {intake_home_status}")
    intake_cc = intake_home_headers.get("cache-control", "")
    if "no-store" not in intake_cc:
        fail(failures, f"intake / cache-control={intake_cc!r}")
    else:
        ok("intake / is no-store (force-dynamic)")

    try:
        photo_status, _ = head(f"{INTAKE}/api/photos/A01/001.jpg")
    except OSError as err:
        print(f"network: intake photo: {err}", file=sys.stderr)
        return 2
    if photo_status != 200:
        fail(failures, f"intake /api/photos/A01/001.jpg status {photo_status}")
    else:
        ok("intake photo A01/001.jpg 200")

    if failures:
        print(f"{len(failures)} failure(s)")
        return 1
    print("catalog architecture probe passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
