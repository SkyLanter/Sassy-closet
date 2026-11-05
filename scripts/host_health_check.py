#!/usr/bin/env python3
"""Read-only sell-host health check: DNS, TLS, HTTP status, held PDP 404, S06 $25.

For each of the two vercel.app sell hosts it reports:
  dns      resolves (getaddrinfo) -> ok / error text
  tls      TLS handshake on :443 with cert verification -> ok / error text
  status   HTTP status of GET /
  held     every heldIncomplete mã returns 404 (not live), and so does its
           held_alias spelling (/m/s019 for S19: lowercase + zero-padded).
           held_pdp / held_alias_pdp stay the --held-ma probe (default S19).
           The shop redirects aliases to the canonical mã; urllib follows that
           redirect, so this catches a redirect/normalisation regression that
           would serve a held piece under another spelling.
  s06      the S06 PDP (/m/S06) returns 200 and the offer is read with
           s06_offer_price.s06_offer_dollars ($25). A spliced price such as
           2$5 is rejected, and neighbour cards are ignored.

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

from held_policy import load_held_policy, norm_ma
from s06_offer_price import s06_offer_dollars

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


def s06_offer_usd(body: str) -> str | None:
    """Agreed S06 Product JSON-LD offer, as a whole-dollar string like 25.00."""
    dollars = s06_offer_dollars(body)
    if type(dollars) is int:
        return f"{dollars:.2f}"
    return None


def s06_shows_25(body: str) -> bool:
    """True when S06's own Product JSON-LD offer is exactly the $25 lock."""
    return s06_offer_dollars(body) == S06_LOCK


def held_alias(ma: str) -> str:
    """S19 -> s019: lowercase letters, digits zero-padded to 3. Same mã after norm_ma."""
    m = re.fullmatch(r"([A-Za-z]+)0*([0-9]+)", ma.strip())
    if not m:
        return ma.strip().lower()
    return m.group(1).lower() + m.group(2).zfill(3)


def held_codes(held_ma: str = HELD_MA, codes: tuple[str, ...] | None = None) -> tuple[str, ...]:
    """Every data/held.json heldIncomplete mã, plus held_ma when it is not already listed."""
    listed = load_held_policy().held if codes is None else tuple(norm_ma(code) for code in codes)
    probe = norm_ma(held_ma) if held_ma else ""
    if probe and probe not in listed:
        return (probe, *listed)
    return tuple(listed)


def check_host(host: str, held_ma: str = HELD_MA, codes: tuple[str, ...] | None = None) -> dict:
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
    rows: list[dict] = []
    for ma in held_codes(held_ma, codes):
        st, _, err = fetch(base + PDP.format(ma=ma))
        status = st if st is not None else err
        if st != 404:
            r["problems"].append(f"held {ma} PDP -> {status} (want 404)")
        alias = held_alias(ma)
        st, _, err = fetch(base + PDP.format(ma=alias))
        alias_status = st if st is not None else err
        if st != 404:
            r["problems"].append(f"held {ma} alias /m/{alias} -> {alias_status} (want 404)")
        rows.append({"ma": ma, "status": status, "alias": alias, "alias_status": alias_status})
    r["held_pdps"] = rows
    probe = norm_ma(held_ma) if held_ma else ""
    row = next((item for item in rows if item["ma"] == probe), None)
    if row is None and rows:
        row = rows[0]
    if row is not None:
        r["held_pdp"] = {"ma": row["ma"], "status": row["status"]}
        r["held_alias_pdp"] = {"ma": row["alias"], "status": row["alias_status"]}
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


def run(hosts_vercel=VERCEL_HOSTS, held_ma: str = HELD_MA, codes: tuple[str, ...] | None = None) -> dict:
    listed = held_codes(held_ma, codes)
    results = [check_host(h, held_ma, listed) for h in hosts_vercel]
    fail = [f"{r['host']}: {p}" for r in results for p in r["problems"]]
    warn: list[str] = []
    overall = "FAIL" if fail else "WARN" if warn else "PASS"
    return {"overall": overall, "fail": fail, "warn": warn, "hosts": results,
            "writes": "none", "network": "read-only GET"}


def markdown(s: dict) -> str:
    out = [f"# Host health: {s['overall']}", "",
           "| host | DNS | TLS | GET / | held PDP 404 | held alias 404 | S06 $25 |",
           "|---|---|---|---|---|---|---|"]
    for r in s["hosts"]:
        alias = r.get("held_alias_pdp") or {}
        alias_cell = alias.get("status", "-")
        if alias.get("ma"):
            alias_cell = f"{alias['ma']} {alias_cell}"
        out.append(f"| {r['host']} | {r['dns']} | {r['tls']} | {r.get('status', '-')} | "
                   f"{r.get('held_pdp', {}).get('status', '-')} | {alias_cell} | "
                   f"{r.get('s06_pdp', {}).get('shows_25', '-')} |")
    checked = [r for r in s["hosts"] if "held_pdps" in r]
    if checked:
        n = len(checked[0]["held_pdps"])
        bad = 0
        for host in checked:
            for row in host["held_pdps"]:
                if row["status"] != 404 or row["alias_status"] != 404:
                    bad += 1
        if bad:
            out.append(f"Held mãs checked: {n} on each host. {bad} not 404.")
        else:
            out.append(f"Held mãs checked: {n} on each host, all 404.")
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
