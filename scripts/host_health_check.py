#!/usr/bin/env python3
"""Read-only sell-host health check: DNS, TLS, HTTP status, held PDP 404, S06 $25.

For each of the two vercel.app sell hosts it reports:
  dns      resolves (getaddrinfo) -> ok / error text
  tls      TLS handshake on :443 with cert verification -> ok / error text
  status   HTTP status of GET /
  held     a held mã PDP (default /m/S19) returns 404 (not live)
  s06      the S06 PDP (/m/S06) returns 200 and the check reads S06's own Product JSON-LD offer ($25)

Severity: any host problem is FAIL. (There is no custom domain: sassycloset.shop
was never registered, NXDOMAIN.) GET/HEAD-free of side effects:
plain GET requests only. No Blob, Vercel, Meta, Square or price writes.

Exit codes: 0 PASS, 1 WARN, 2 FAIL.
"""
from __future__ import annotations

import argparse
import html
import json
import math
import re
import socket
import ssl
import sys
import urllib.error
import urllib.request

from held_policy import norm_ma

VERCEL_HOSTS = ("sassycloset.vercel.app", "sassy-closet-shop.vercel.app")
HELD_MA = "S19"
S06_LOCK = 25
PDP = "/m/{ma}"
TIMEOUT = 15
EXIT = {"PASS": 0, "WARN": 1, "FAIL": 2}


def check_dns(host: str) -> tuple[bool, str]:
    try:
        socket.getaddrinfo(host, 443, proto=socket.IPPROTO_TCP)
        return True, "ok"
    except OSError as e:
        return False, f"{type(e).__name__}: {e}"


def check_tls(host: str, timeout: float = TIMEOUT) -> tuple[bool, str]:
    ctx = ssl.create_default_context()
    try:
        with socket.create_connection((host, 443), timeout=timeout) as sock:
            with ctx.wrap_socket(sock, server_hostname=host) as tls:
                return True, f"ok ({tls.version()})"
    except (OSError, ssl.SSLError) as e:
        return False, f"{type(e).__name__}: {e}"


def fetch(url: str, timeout: float = TIMEOUT) -> tuple[int | None, str, str]:
    """GET url -> (status, body, error). Status None on network/TLS error."""
    req = urllib.request.Request(url, headers={"User-Agent": "sassy-host-health/1 (read-only)"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.read(2_000_000).decode("utf-8", "replace"), ""
    except urllib.error.HTTPError as e:
        return e.code, "", ""
    except (OSError, ssl.SSLError) as e:
        return None, "", f"{type(e).__name__}: {getattr(e, 'reason', e)}"


_SCRIPT_OPEN_RE = re.compile(r"<script\b([^>]*)>", re.IGNORECASE)
_SCRIPT_CLOSE_RE = re.compile(r"</script\s*>", re.IGNORECASE)
_LD_TYPE_RE = re.compile(
    r"(?:^|\s)type\s*=\s*(['\"])application/ld\+json\1",
    re.IGNORECASE,
)
_PLAIN_WHOLE_RE = re.compile(r"(?:0|[1-9]\d*)(?:\.0+)?")
_S06 = "S06"


def whole_dollar_usd(value: object) -> int | None:
    """Plain whole-dollar amount, or None when the price cannot be read.

    Accepts an int 25 and the strings 25, 25.0, and 25.00. Rejects booleans,
    blanks, scientific notation, hex, commas, currency signs, fractions, and
    non-finite numbers. True is not 1.
    """
    # bool is a subclass of int; True must not become 1.
    if isinstance(value, bool) or value is None:
        return None
    if isinstance(value, int):
        return value if value >= 0 else None
    if isinstance(value, float):
        if not math.isfinite(value) or value < 0 or not value.is_integer():
            return None
        return int(value)
    if isinstance(value, str):
        text = value.strip()
        if _PLAIN_WHOLE_RE.fullmatch(text) is None:
            return None
        return int(text.split(".", 1)[0])
    return None


def _ld_json_payloads(body: str) -> list[object]:
    payloads: list[object] = []
    for match in _SCRIPT_OPEN_RE.finditer(body):
        if _LD_TYPE_RE.search(match.group(1)) is None:
            continue
        close = _SCRIPT_CLOSE_RE.search(body, match.end())
        if close is None:
            continue
        raw = html.unescape(body[match.end():close.start()])
        try:
            payloads.append(json.loads(raw))
        except json.JSONDecodeError:
            continue
    return payloads


def _jsonld_nodes(payload: object):
    if isinstance(payload, list):
        for item in payload:
            yield from _jsonld_nodes(item)
        return
    if not isinstance(payload, dict):
        return
    yield payload
    graph = payload.get("@graph")
    if isinstance(graph, (dict, list)):
        yield from _jsonld_nodes(graph)


def _is_s06_product(node: dict) -> bool:
    kind = node.get("@type")
    if isinstance(kind, str):
        is_product = kind == "Product"
    elif isinstance(kind, list):
        is_product = any(item == "Product" for item in kind)
    else:
        is_product = False
    return is_product and norm_ma(node.get("sku")) == _S06


def _offer_amounts(offers: object) -> list[int | None]:
    if isinstance(offers, dict):
        nodes = [offers]
    elif isinstance(offers, list):
        nodes = list(offers)
    else:
        nodes = []
    if not nodes:
        return [None]
    amounts: list[int | None] = []
    for offer in nodes:
        if not isinstance(offer, dict) or "price" not in offer:
            amounts.append(None)
            continue
        amounts.append(whole_dollar_usd(offer.get("price")))
    return amounts


def _s06_offer_prices(body: str) -> list[int | None]:
    prices: list[int | None] = []
    for payload in _ld_json_payloads(body):
        for node in _jsonld_nodes(payload):
            if _is_s06_product(node):
                prices.extend(_offer_amounts(node.get("offers")))
    return prices


def s06_offer_usd(body: str) -> str | None:
    """Agreed S06 Product JSON-LD offer, as a whole-dollar string like 25.00."""
    prices = _s06_offer_prices(body)
    if not prices or any(price is None for price in prices):
        return None
    unique = set(prices)
    if len(unique) != 1:
        return None
    return f"{unique.pop():.2f}"


def s06_shows_25(body: str) -> bool:
    """True when S06's own Product JSON-LD offer is exactly the $25 lock."""
    return s06_offer_usd(body) == f"{S06_LOCK:.2f}"


def check_host(host: str, held_ma: str = HELD_MA) -> dict:
    r = {"host": host, "kind": "vercel", "problems": []}
    r["dns_ok"], r["dns"] = check_dns(host)
    if not r["dns_ok"]:
        r["problems"].append(f"DNS: {r['dns']}")
        r["tls_ok"], r["tls"] = False, "skipped (no DNS)"
        return r
    r["tls_ok"], r["tls"] = check_tls(host)
    if not r["tls_ok"]:
        r["problems"].append(f"TLS: {r['tls']}")
        return r
    base = f"https://{host}"
    st, _, err = fetch(base + "/")
    r["status"] = st if st is not None else err
    if st != 200:
        r["problems"].append(f"GET / -> {r['status']}")
    st, _, err = fetch(base + PDP.format(ma=held_ma))
    r["held_pdp"] = {"ma": held_ma, "status": st if st is not None else err}
    if st != 404:
        r["problems"].append(f"held {held_ma} PDP -> {r['held_pdp']['status']} (want 404)")
    st, body, err = fetch(base + PDP.format(ma="S06"))
    offer_usd = s06_offer_usd(body) if st == 200 else None
    ok = st == 200 and offer_usd == f"{S06_LOCK:.2f}"
    r["s06_pdp"] = {
        "status": st if st is not None else err,
        "shows_25": ok,
        "offer_usd": offer_usd,
    }
    if not ok:
        r["problems"].append(f"S06 PDP -> {r['s06_pdp']['status']}, ${S06_LOCK} shown={ok}")
    return r


def run(hosts_vercel=VERCEL_HOSTS, held_ma: str = HELD_MA) -> dict:
    results = [check_host(h, held_ma) for h in hosts_vercel]
    fail = [f"{r['host']}: {p}" for r in results for p in r["problems"]]
    warn: list[str] = []
    overall = "FAIL" if fail else "WARN" if warn else "PASS"
    return {"overall": overall, "fail": fail, "warn": warn, "hosts": results,
            "writes": "none", "network": "read-only GET"}


def markdown(s: dict) -> str:
    out = [f"# Host health: {s['overall']}", "",
           "| host | DNS | TLS | GET / | held PDP 404 | S06 $25 |", "|---|---|---|---|---|---|"]
    for r in s["hosts"]:
        out.append(f"| {r['host']} | {r['dns']} | {r['tls']} | {r.get('status', '-')} | "
                   f"{r.get('held_pdp', {}).get('status', '-')} | {r.get('s06_pdp', {}).get('shows_25', '-')} |")
    out += [""] + [f"- FAIL: {x}" for x in s["fail"]] + [f"- WARN: {x}" for x in s["warn"]]
    out += ["", "Read-only GETs. No Blob, Vercel, Meta, Square or price writes."]
    return "\n".join(out) + "\n"


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--held-ma", default=HELD_MA)
    p.add_argument("--out-json")
    p.add_argument("--out-md")
    a = p.parse_args(argv)
    s = run(held_ma=a.held_ma)
    md = markdown(s)
    if a.out_json:
        open(a.out_json, "w", encoding="utf-8").write(json.dumps(s, indent=2) + "\n")
    if a.out_md:
        open(a.out_md, "w", encoding="utf-8").write(md)
    print(md, end="")
    return EXIT[s["overall"]]


if __name__ == "__main__":
    sys.exit(main())
