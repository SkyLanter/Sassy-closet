#!/usr/bin/env python3
"""Sell-test a11y + reduced-motion gate for watery/frosted galleries (LEARN 17).

LOOK must stay green on every run (Kelly Ying chrome, allowlist, Hold, no cart).
GATE is expected red until Origin lands
docs/ai-clothing-shop/17-a11y-watery-motion.md §11 / §18.

Never POST. Never mint mã. Never invent prices or color names.

Usage:
  python3 docs/ai-clothing-shop/qa/qa_a11y_watery_motion.py
  python3 docs/ai-clothing-shop/qa/qa_a11y_watery_motion.py --look
  python3 docs/ai-clothing-shop/qa/qa_a11y_watery_motion.py --gate
  SHOP=https://… python3 docs/ai-clothing-shop/qa/qa_a11y_watery_motion.py

Exit:
  0  LOOK + GATE green (Origin landed)
  1  GATE red (a11y APPLY not landed; look still locked)
  2  LOOK red (Kelly Ying look / commerce honesty drifted — stop)
  3  transport / unexpected error
"""
from __future__ import annotations

import argparse
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
INVENTED = ("A03", "Q01", "V984", "V826", "AO001", "AO003")
FB_PAGE = "https://www.facebook.com/profile.php?id=61594312648057"
UA = "SassyCloset-Learn17-A11yQA/1.0"
HEX_COLOR_LABEL = re.compile(r'aria-label="Color\s*#[0-9A-Fa-f]{3,8}"')
CSS_HREF = re.compile(r'href="(/_next/static/immutable/chunks/[^"]+\.css)"')


def get(url: str) -> tuple[int, bytes, dict[str, str]]:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=25) as res:
            headers = {k.lower(): v for k, v in res.headers.items()}
            return res.status, res.read(), headers
    except urllib.error.HTTPError as err:
        headers = {k.lower(): v for k, v in err.headers.items()}
        return err.code, err.read(), headers


def decode(body: bytes) -> str:
    return body.decode("utf-8", "replace")


def visible(html: str) -> str:
    html = re.sub(r"<script[\s\S]*?</script>", " ", html, flags=re.I)
    html = re.sub(r"<style[\s\S]*?</style>", " ", html, flags=re.I)
    html = re.sub(r"<[^>]+>", " ", html)
    return re.sub(r"\s+", " ", html)


def record(bucket: list[str], ok: bool, msg: str) -> None:
    mark = "PASS" if ok else "FAIL"
    print(f"  {mark} {msg}")
    if not ok:
        bucket.append(msg)


def look_home(failed: list[str], html: str, text: str) -> None:
    for ma in ALLOW:
        record(failed, ma in text, f"home lists {ma}")
    for code in INVENTED:
        record(failed, code not in html, f"home has no invented {code}")
    for usd in PRICE.values():
        record(failed, f"${usd}" in text, f"home shows ${usd}")
    record(failed, "Inbox for price" in text and "Hold" in text, "home Hold / Inbox copy")
    record(failed, "P02" in text and "$23" not in text, "home has no $23")
    record(failed, FB_PAGE in html, "home Facebook Page id")
    record(failed, "Message to buy" in text, "home Message to buy")
    record(failed, "Zelle" in text, "home Zelle word")
    record(failed, "Facebook livestream" in text, "home livestream rail")
    record(failed, "bg-paper" in html and "text-ink" in html, "home paper/ink")
    record(
        failed,
        "ma-mark" in html and ("border-gold" in html or "bg-gold" in html),
        "home gold / ma-mark",
    )
    record(failed, "be_vietnam_pro" in html and "cormorant_garamond" in html, "home Be Vietnam + Cormorant")
    record(failed, "Shopify" not in html and "Horizon" not in html, "home is not Horizon")
    record(failed, "role=\"tablist\"" in html, "home Featured tablist")
    record(
        failed,
        'aria-roledescription="carousel"' not in html.lower(),
        "home does not mark Featured as a carousel",
    )
    record(failed, "Checkout" not in text, "home has no Checkout")
    record(failed, "Shop now" not in text, "home has no Shop now")


def look_pdp(failed: list[str], ma: str, html: str, text: str) -> None:
    record(failed, ma in text, f"/{ma} prints {ma}")
    record(failed, FB_PAGE in html, f"/{ma} Messenger Page")
    record(failed, "be_vietnam_pro" in html and "cormorant_garamond" in html, f"/{ma} fonts")
    if ma in HOLD:
        record(failed, "Hold" in text, f"/{ma} Hold word")
        record(failed, "Inbox for price" in text, f"/{ma} Inbox for price")
        own_paid = bool(
            re.search(
                rf'\\"ma\\":\\"{ma}\\"[^\\]*\\"priceUsd\\":(?!null)\d',
                html,
            )
        ) or bool(
            re.search(rf'"ma":"{ma}"[^]]{{0,200}}"priceUsd":(?!null)\d', html)
        )
        record(failed, not own_paid, f"/{ma} payload priceUsd is null")
    else:
        usd = PRICE[ma]
        record(failed, f"${usd}" in text, f"/{ma} shows ${usd}")
        record(failed, "Available" in text, f"/{ma} Available word")
    for code in INVENTED:
        record(failed, code not in html, f"/{ma} has no invented {code}")
    record(
        failed,
        "bg-rose-950" not in html and "Allura" not in html,
        f"/{ma} is not intake rose/Allura",
    )


def look_dock_frost(failed: list[str], html: str) -> None:
    # Chrome frost is allowed. Fail only if the hero img carries backdrop-blur.
    img_blur = bool(
        re.search(r"<img[^>]+(backdrop-blur|filter:\s*url\(#)", html, re.I)
    )
    record(failed, not img_blur, "hero img is not frosted / goo-filtered")
    dock = "backdrop-blur-md" in html and "bg-paper/95" in html
    record(failed, True, f"phone dock frost present={dock} (allowed chrome)")


def fetch_css(home_html: str) -> str:
    hrefs = CSS_HREF.findall(home_html)
    if not hrefs:
        return ""
    status, body, _ = get(SHOP + hrefs[0])
    if status != 200:
        return ""
    return decode(body)


def gate_a11y(failed: list[str], home: str, a01: str, p05: str, css: str) -> None:
    # Hue-only customer chips (LEARN 17 FIX A)
    a01_hex = HEX_COLOR_LABEL.findall(a01)
    p05_hex = HEX_COLOR_LABEL.findall(p05)
    home_hex = HEX_COLOR_LABEL.findall(home)
    record(
        failed,
        len(a01_hex) == 0,
        f"/m/A01 has no hue-only Color # labels (found {len(a01_hex)})",
    )
    record(
        failed,
        len(p05_hex) == 0,
        f"/m/P05 has no hue-only Color # labels (found {len(p05_hex)})",
    )
    record(
        failed,
        len(home_hex) == 0,
        f"home has no hue-only Color # labels (found {len(home_hex)})",
    )

    # Featured is tabs, not a carousel
    record(
        failed,
        "tabpanel" in home or "aria-controls" in home,
        "Featured tablist has tabpanel or aria-controls",
    )
    record(
        failed,
        'aria-roledescription="carousel"' not in home.lower(),
        "home still must not be a carousel landmark",
    )

    # Reduced-motion CSS coverage (LEARN 10 FIX 1 + 17 FIX D)
    record(failed, "prefers-reduced-motion" in css, "CSS declares prefers-reduced-motion")
    record(
        failed,
        bool(re.search(r"announce-fade[^{,\n]*animation:\s*none", css))
        or "announce-fade,.shimmer" in css.replace(" ", ""),
        "reduce query still kills announce/shimmer/cta",
    )
    motion_safe = "motion-safe:" in home or "motion-safe:" in a01 or "motion-safe:" in css
    no_pref_shimmer = "prefers-reduced-motion:no-preference" in css.replace(" ", "")
    hover_gated = motion_safe or "group-hover:scale-[1.08]" not in home
    record(
        failed,
        hover_gated,
        "card 1.08 zoom is motion-safe or removed from ungated hover",
    )
    record(
        failed,
        no_pref_shimmer or motion_safe,
        "infinite shimmer wrapped in no-preference (or motion-safe path landed)",
    )

    # Single-file PDP must not claim carousel
    record(
        failed,
        'aria-roledescription="carousel"' not in a01.lower(),
        "/m/A01 is not a one-slide carousel landmark (cover-only)",
    )

    # Keyboard: img onclick cycle is a gate until lightbox/button
    record(
        failed,
        "cursor-pointer" not in a01 or "Xem ảnh lớn" in a01 or "View larger" in a01,
        "/m/A01 hero is enlarge-or-static, not a pointer-cycle affordance without a name",
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--look", action="store_true", help="LOOK checks only")
    parser.add_argument("--gate", action="store_true", help="GATE checks only")
    args = parser.parse_args()
    run_look = args.look or not args.gate
    run_gate = args.gate or not args.look
    if args.look and args.gate:
        run_look = run_gate = True

    look_failed: list[str] = []
    gate_failed: list[str] = []

    try:
        print("LOOK GET /", SHOP)
        st, body, hdr = get(SHOP + "/")
        home = decode(body)
        print(f"  HTTP {st} cache={hdr.get('x-vercel-cache', '?')}")
        if st != 200:
            look_failed.append(f"home HTTP {st}")
            print("  FAIL home HTTP")
        else:
            if run_look:
                look_home(look_failed, home, visible(home))

        pages = {
            "A01": "/m/A01",
            "P02": "/m/P02",
            "P05": "/m/P05",
        }
        htmls: dict[str, str] = {}
        for ma, path in pages.items():
            print(f"LOOK GET {path}")
            st, body, hdr = get(SHOP + path)
            html = decode(body)
            htmls[ma] = html
            print(f"  HTTP {st} cache={hdr.get('x-vercel-cache', '?')}")
            if st != 200:
                look_failed.append(f"{path} HTTP {st}")
                continue
            if run_look:
                look_pdp(look_failed, ma, html, visible(html))
                if ma == "A01":
                    look_dock_frost(look_failed, html)

        css = ""
        if run_gate:
            css = fetch_css(home)
            print("GATE CSS", "ok" if css else "MISSING")
            record(gate_failed, bool(css), "downloaded shop CSS chunk")
            if css:
                gate_a11y(
                    gate_failed,
                    home,
                    htmls.get("A01", ""),
                    htmls.get("P05", ""),
                    css,
                )

    except Exception as exc:  # noqa: BLE001 — transport bucket
        print("ERROR", type(exc).__name__, exc)
        return 3

    print()
    print(f"LOOK {'RED' if look_failed else 'GREEN'} ({len(look_failed)} fail)")
    print(f"GATE {'RED' if gate_failed else 'GREEN'} ({len(gate_failed)} fail)")
    if look_failed:
        print("LOOK fails:")
        for row in look_failed:
            print(" -", row)
    if gate_failed:
        print("GATE fails (expected until Origin APPLY):")
        for row in gate_failed:
            print(" -", row)

    if look_failed:
        return 2
    if gate_failed:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
