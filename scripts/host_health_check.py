#!/usr/bin/env python3
"""Read-only sell-host health check: DNS, TLS, HTTP status, held PDP 404, S06 $25.

For each of the two vercel.app sell hosts it reports:
  dns      resolves (getaddrinfo) -> ok / error text
  tls      TLS handshake on :443 with cert verification -> ok / error text
  status   HTTP status of GET /
  held     a held mã PDP (default /m/S19) returns 404 (not live)
  s06      the S06 PDP (/m/S06) returns 200 and shows $25

Severity: any host problem is FAIL. (There is no custom domain: sassycloset.shop
was never registered, NXDOMAIN.) GET/HEAD-free of side effects:
plain GET requests only. No Blob, Vercel, Meta, Square or price writes.

Exit codes: 0 PASS, 1 WARN, 2 FAIL.
"""
from __future__ import annotations

import argparse
import json
import re
import socket
import ssl
import sys
import urllib.error
import urllib.request

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


def shows_price(body: str, usd: int) -> bool:
    return re.search(rf"\$\s?{usd}(?:\.00)?(?![0-9])", body) is not None


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
    ok = st == 200 and shows_price(body, S06_LOCK)
    r["s06_pdp"] = {"status": st if st is not None else err, "shows_25": ok}
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
