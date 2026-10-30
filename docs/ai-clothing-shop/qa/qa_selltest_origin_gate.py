#!/usr/bin/env python3
"""Sell-test Origin gate + Kelly Ying look lock.

LOOK must stay green on every run. GATE is expected red until Origin
lands the admin/Blob APPLY list in docs/ai-clothing-shop/11-vercel-blob-admin-qa.md §18.

Never POST. Never mint mã. Never invent prices.

Usage:
  python3 docs/ai-clothing-shop/qa/qa_selltest_origin_gate.py
  python3 docs/ai-clothing-shop/qa/qa_selltest_origin_gate.py --look
  python3 docs/ai-clothing-shop/qa/qa_selltest_origin_gate.py --gate
  SHOP=https://… python3 docs/ai-clothing-shop/qa/qa_selltest_origin_gate.py

Exit:
  0  LOOK + GATE green (Origin landed)
  1  GATE red (silent Save / cache-drift contract missing)
  2  LOOK red (Kelly Ying look drifted — stop and restore chrome)
  3  transport / unexpected error
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import urllib.error
import urllib.request

SHOP = os.environ.get("SHOP", "https://sassy-closet-shop.vercel.app").rstrip("/")
ALLOW = ["A01", "S01", "P01", "P02", "P03", "P04", "P05", "K01", "H01", "A02"]
PRICE = {
    "A01": "25",
    "S01": "28",
    "P01": "5",
    "P03": "18",
    "P04": "13",
    "K01": "37",
    "H01": "8",
    "A02": "22",
}
HOLD = frozenset({"P02", "P05"})
INVENTED_NEXT = ("A03", "Q01", "V01", "K02", "G01", "B01", "P06", "H02", "J01", "S02", "O01", "D01")
FB_PAGE = "https://www.facebook.com/profile.php?id=61594312648057"
UA = "SassyCloset-LearnQA/1.0"
CATALOG_CANDIDATES = (
    "/api/admin/catalog",
    "/api/catalog",
    "/api/admin/catalog.json",
)


def get(url: str) -> tuple[int, bytes, dict[str, str]]:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=25) as res:
            headers = {k.lower(): v for k, v in res.headers.items()}
            return res.status, res.read(), headers
    except urllib.error.HTTPError as err:
        headers = {k.lower(): v for k, v in err.headers.items()}
        return err.code, err.read(), headers


def visible(html: str) -> str:
    html = re.sub(r"<script[\s\S]*?</script>", " ", html, flags=re.I)
    html = re.sub(r"<style[\s\S]*?</style>", " ", html, flags=re.I)
    html = re.sub(r"<[^>]+>", " ", html)
    return re.sub(r"\s+", " ", html)


def decode(body: bytes) -> str:
    return body.decode("utf-8", "replace")


def cache_line(hdr: dict[str, str]) -> str:
    return (
        f"cache={hdr.get('x-vercel-cache', '?')} "
        f"age={hdr.get('age', '?')} "
        f"cc={hdr.get('cache-control', '?')}"
    )


def no_store(hdr: dict[str, str]) -> bool:
    cc = hdr.get("cache-control", "").lower()
    return "no-store" in cc or "private" in cc


def record(bucket: list[str], ok: bool, msg: str) -> None:
    mark = "PASS" if ok else "FAIL"
    print(f"  {mark} {msg}")
    if not ok:
        bucket.append(msg)


def look_home(failed: list[str]) -> None:
    status, body, hdr = get(f"{SHOP}/")
    html = decode(body)
    text = visible(html)
    print("LOOK GET /", status, cache_line(hdr))
    record(failed, status == 200, f"home HTTP {status}")
    for ma in ALLOW:
        record(failed, ma in text, f"home lists {ma}")
    record(failed, "A03" not in text, "home has no invented A03")
    record(failed, "$23" not in text and not re.search(r"\$\s*23\b", text), "home has no $23")
    for usd in PRICE.values():
        record(failed, f"${usd}" in text, f"home shows ${usd}")
    record(failed, "Inbox for price" in text and "Hold" in text, "home Hold / Inbox copy")
    record(failed, "Messenger" in text, "home Messenger CTA")
    record(failed, "Zelle" in text, "home Zelle word")
    record(failed, "Facebook livestream" in text, "home Facebook livestream")
    record(failed, FB_PAGE in html, "home Facebook Page id 61594312648057")
    record(failed, "Message to buy" in text, "home Message to buy")
    record(failed, "bg-paper" in html and "text-ink" in html, "home paper/ink chrome")
    record(failed, "border-gold" in html and "ma-mark" in html, "home gold / ma-mark chrome")
    record(failed, "rounded-full" in html, "home rounded-full pills")
    record(failed, "Shopify" not in html and "Horizon" not in html, "home is not Shopify Horizon")
    record(failed, not re.search(r"\bInter\b", html), "home is not Inter luxury")


def look_hold_pdps(failed: list[str]) -> None:
    for ma in sorted(HOLD):
        status, body, hdr = get(f"{SHOP}/m/{ma}")
        text = visible(decode(body))
        print(f"LOOK GET /m/{ma}", status, cache_line(hdr))
        record(failed, status == 200, f"/m/{ma} HTTP {status}")
        record(failed, "Hold" in text and "Inbox for price" in text, f"/m/{ma} Hold / Inbox")
        record(failed, "no USD" in text, f"/m/{ma} no-USD line")
        record(failed, "$23" not in text, f"/m/{ma} no $23")
        record(failed, "Messenger" in text and "Zelle" in text, f"/m/{ma} Messenger + Zelle")
        record(failed, "Facebook livestream" in text, f"/m/{ma} livestream chrome")


def look_admin(failed: list[str]) -> None:
    status, body, hdr = get(f"{SHOP}/admin")
    html = decode(body)
    text = visible(html)
    print("LOOK GET /admin", status, cache_line(hdr))
    record(failed, status == 200, f"admin HTTP {status}")
    record(failed, no_store(hdr), "admin Cache-Control private/no-store")
    record(
        failed,
        hdr.get("x-vercel-cache", "").upper() in {"MISS", "BYPASS"},
        f"admin x-vercel-cache is MISS/BYPASS (got {hdr.get('x-vercel-cache')})",
    )
    record(failed, "Vercel Blob" in text, "admin Storage: Vercel Blob")
    record(failed, "Catalog" in text and "10" in text, "admin Catalog (10)")
    record(failed, "Test only" in text, "admin Test only")
    record(failed, "bg-paper" in html and "bg-blush" in html, "admin paper/blush chrome")
    record(failed, "border-gold" in html and "text-ink" in html, "admin gold/ink chrome")
    record(failed, "Boxes only" in text, "admin hex boxes unnamed (customer text stays)")
    record(failed, "Shopify" not in html and "Horizon" not in html, "admin is not Horizon")


def look_no_invented_pdps(failed: list[str]) -> None:
    for ma in ("A03", "Q01", "V01"):
        status, _, hdr = get(f"{SHOP}/m/{ma}")
        print(f"LOOK GET /m/{ma}", status, cache_line(hdr))
        record(failed, status == 404, f"/m/{ma} stays 404")


def run_look() -> list[str]:
    print("== LOOK (Kelly Ying chrome must stay) ==")
    failed: list[str] = []
    look_home(failed)
    look_hold_pdps(failed)
    look_admin(failed)
    look_no_invented_pdps(failed)
    print(f"LOOK failed={len(failed)}")
    return failed


def gate_next_grid(failed: list[str]) -> None:
    _, body, _ = get(f"{SHOP}/admin")
    html = decode(body)
    text = visible(html)
    publishable = 'data-publishable="false"' in html or "data-publishable='false'" in html
    extra_add = [ma for ma in INVENTED_NEXT if f"Add {ma}" in text]
    print(
        "GATE admin next-grid Add=",
        extra_add,
        "Next A03=",
        "Next mã A03" in text,
        "publishable=false=",
        publishable,
    )
    record(
        failed,
        publishable or not extra_add,
        "admin must not offer Add A03 / next unused mã unless data-publishable=false",
    )


def gate_catalog_api(failed: list[str]) -> tuple[dict[str, object] | None, str | None]:
    found: dict[str, object] | None = None
    found_path: str | None = None
    holes: list[str] = []
    for path in CATALOG_CANDIDATES:
        status, body, hdr = get(f"{SHOP}{path}")
        print(f"GATE GET {path}", status, cache_line(hdr), hdr.get("content-type", ""))
        if status == 404:
            holes.append(f"{path} 404 {cache_line(hdr)}")
            continue
        if status != 200:
            holes.append(f"{path} HTTP {status}")
            continue
        if not no_store(hdr):
            record(failed, False, f"{path} must be private/no-store (got {hdr.get('cache-control')})")
        ctype = hdr.get("content-type", "")
        if "json" not in ctype:
            holes.append(f"{path} content-type {ctype} (need JSON)")
            continue
        try:
            payload = json.loads(decode(body))
        except json.JSONDecodeError:
            holes.append(f"{path} is not JSON")
            continue
        record(failed, True, f"{path} 200 JSON {cache_line(hdr)}")
        found = payload if isinstance(payload, dict) else {"products": payload}
        found_path = path
        break
    if found is None:
        record(
            failed,
            False,
            "no no-store catalog JSON at "
            + " | ".join(CATALOG_CANDIDATES)
            + " — last holes: "
            + "; ".join(holes),
        )
        return None, None
    products = found.get("products")
    if not isinstance(products, list):
        record(failed, False, "catalog JSON missing products[]")
        return found, found_path
    mas = [p.get("ma") if isinstance(p, dict) else None for p in products]
    record(failed, mas == ALLOW, f"catalog products ma order {mas}")
    sha = found.get("catalogSha") or found.get("sha256")
    updated = found.get("updatedAt") or found.get("exportedAt")
    record(failed, isinstance(sha, str) and len(sha) >= 8, "catalog JSON has catalogSha")
    record(failed, isinstance(updated, str) and len(updated) >= 8, "catalog JSON has updatedAt")
    for row in products:
        if not isinstance(row, dict):
            continue
        ma = row.get("ma")
        status = row.get("status")
        price = row.get("priceUsd")
        if ma in HOLD:
            record(failed, status == "hold" and price is None, f"catalog {ma} hold ⇔ priceUsd null")
        elif ma in PRICE:
            record(failed, status == "available" and price == int(PRICE[ma]), f"catalog {ma} ${PRICE[ma]}")
    return found, found_path


def gate_save_receipt(failed: list[str]) -> None:
    _, body, _ = get(f"{SHOP}/admin")
    html = decode(body)
    has_contract = (
        'data-save-contract="blob+revalidate"' in html
        or "data-save-receipt" in html
        or "blobWritten" in html
    )
    print("GATE admin save-contract marker=", has_contract)
    record(
        failed,
        has_contract,
        'admin must expose data-save-contract="blob+revalidate" (Save receipt after Blob write + revalidatePath)',
    )
    path = "/api/admin/revalidate"
    status, _, hdr = get(f"{SHOP}{path}")
    print(f"GATE GET {path}", status, cache_line(hdr))
    record(
        failed,
        status in {200, 401, 403, 405},
        f"{path} must exist (200/401/403/405); 404 HIT is a cached hole ({status} {cache_line(hdr)})",
    )


def gate_cover_bust(failed: list[str]) -> None:
    status, body, hdr = get(f"{SHOP}/")
    html = decode(body)
    print("GATE GET / cover tags", status, cache_line(hdr))
    srcs = re.findall(r'<img[^>]+src="([^"]+)"', html)
    covers = [s for s in srcs if "/products/" in s and "cover" in s]
    if not covers:
        record(failed, False, "home has no /products/{MA}/cover images")
        return
    stale_covers = [
        src
        for src in covers
        if "?" not in src and not re.search(r"cover-[a-f0-9]{8,}\.", src, re.I)
    ]
    record(
        failed,
        not stale_covers,
        "cover src must be hashed or ?v= "
        f"({len(stale_covers)} bare paths, e.g. {stale_covers[0] if stale_covers else '—'})",
    )
    _, cover_body, cover_hdr = get(f"{SHOP}/products/A01/cover.jpg")
    print("GATE GET /products/A01/cover.jpg", cache_line(cover_hdr), "sha", hashlib.sha256(cover_body).hexdigest()[:12])
    age_raw = cover_hdr.get("age", "0")
    try:
        age = int(age_raw)
    except ValueError:
        age = 0
    if cover_hdr.get("x-vercel-cache", "").upper() == "HIT" and age > 60:
        record(
            failed,
            False,
            f"A01 cover is CDN HIT age={age} etag={cover_hdr.get('etag')} — overwrite will look like silent Save",
        )


def run_gate() -> list[str]:
    print("== GATE (silent Save + cache drift — red until §18) ==")
    failed: list[str] = []
    gate_next_grid(failed)
    gate_catalog_api(failed)
    gate_save_receipt(failed)
    gate_cover_bust(failed)
    print(f"GATE failed={len(failed)}")
    return failed


def main() -> int:
    parser = argparse.ArgumentParser(description="Sell-test look lock + Origin admin/Blob gate")
    parser.add_argument("--look", action="store_true", help="Kelly Ying look lock only")
    parser.add_argument("--gate", action="store_true", help="Origin silent-Save / cache-drift gate only")
    args = parser.parse_args()
    run_look_flag = args.look or not args.gate
    run_gate_flag = args.gate or not args.look
    if args.look and args.gate:
        run_look_flag = True
        run_gate_flag = True

    print(f"SHOP={SHOP}")
    look_failed: list[str] = []
    gate_failed: list[str] = []
    try:
        if run_look_flag:
            look_failed = run_look()
        if run_gate_flag:
            gate_failed = run_gate()
    except Exception as exc:  # noqa: BLE001 — transport / unexpected
        print("ERROR", type(exc).__name__, exc)
        return 3

    print("== SUMMARY ==")
    print(f"look_failed={len(look_failed)}")
    print(f"gate_failed={len(gate_failed)}")
    if look_failed:
        print("LOOK is red — restore Kelly Ying chrome before any Origin Save work.")
        for row in look_failed:
            print("  -", row)
        return 2
    if gate_failed:
        print("GATE is red — Origin must land §18 (admin/Blob) so Save cannot stay silent and HTML cannot drift.")
        for row in gate_failed:
            print("  -", row)
        return 1
    print("LOOK + GATE green.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
