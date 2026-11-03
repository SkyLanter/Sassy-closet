"""Read-only midnight QC for Blob, hub Official, and both sell hosts.

Writes summary.json and data-ok.md. Held PDP 404s, the S06 $25 lock, and
the Blob/hub/PDP guards come from scripts/freshness_check.py. This file
does not fetch Taobao, does not write data/held.json, and does not replace
the hub sheet parser.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parent
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

import freshness_check
from freshness_check import (
    ALIAS_ORIGIN,
    PRIMARY_ORIGIN,
    S06,
    SELL_ORIGINS,
    USER_AGENT,
    MoneyRow,
    PdpView,
    SourceState,
    evaluate,
    money_text,
    parse_blob_catalog,
    parse_pdp_price,
    parse_usd,
    read_hub_official,
    snapshot_from_json,
)
from held_policy import HeldPolicy, load_held_policy, norm_ma

ROOT = Path(__file__).resolve().parents[1]
Q02 = "Q02"
TIMEZONE = "America/Los_Angeles"
PR105_URL = "https://github.com/SkyLanter/Sassy-closet/pull/105"
NEW_INTAKE_CUTOFFS = (
    ("newIntakeSince20261007", "2026-10-07T00:00:00Z"),
    ("newIntakeSince20261009", "2026-10-09T00:00:00Z"),
    ("newIntakeSince20261011", "2026-10-11T00:00:00Z"),
)
SUMMARY_KEYS = (
    "date",
    "checkedAt",
    "timezone",
    "overall",
    "dataOk",
    "sellSite",
    "metaLight",
    "blobCount",
    "sellCount",
    "hubCount",
    "intakeCount",
    "heldCount",
    "s06Usd",
    "a02TitleEn",
    "k06OnBlob",
    "k06Pdp",
    "v05OnBlob",
    "v05Pdp",
    "v05IntakeCostCny",
    "v05CreatedAt",
    "v05SellUsd",
    "blobUpdatedAt",
    "blobSha256",
    "blobEtag",
    "blobLastModifiedHeader",
    "blobAgeSecondsAtCheckedAt",
    "hubSha256",
    "hubLastModified",
    "homeSha256",
    "aliasFirstFetchSha256",
    "homeRefetchSha256",
    "mainSha",
    "mainHeldList",
    "mainIncludesK06",
    "mainIncludesV05",
    "mainNeverList",
    "saveRouteCallsHeldCheck",
    "shopMintRefusesHeld",
    "shopSaveRefusesOffLockS06",
    "blobHubUsdMismatches",
    "intakeVsBlobMismatches",
    "heldAbsent",
    "q02Absent",
    "b01Referenced",
    "imagesChecked",
    "imagesOk",
    "newIntakeSince20261007",
    "newIntakeSince20261009",
    "newIntakeSince20261011",
    "pr105Url",
    "pr105Draft",
    "pr105Head",
    "pr105AddsV05",
    "pr101Head",
    "pr101Draft",
    "pr101State",
    "newDraftPr",
    "newDraftPrHead",
    "bossPing",
    "changedSince20261007",
    "changedSince20261009",
    "changedSince20261010",
    "changedSince20261011",
    "unchangedOpenPrs",
    "notes",
    "freshnessGuards",
    "freshnessHub",
)
_HOME_PRICE_RE = re.compile(
    r'"ma"\s*:\s*"(?P<ma>[A-Za-z][0-9]{2})"(?P<body>.{0,2000}?)'
    r'"priceUsd"\s*:\s*(?P<price>null|\d+(?:\.\d+)?)',
    flags=re.DOTALL,
)
_SHA_RE = re.compile(r"[0-9a-f]{40}")


@dataclass(frozen=True)
class HttpResult:
    status: int
    body: bytes
    headers: dict[str, str]
    error: str | None


@dataclass(frozen=True)
class CatalogProduct:
    ma: str
    price_usd: Decimal | None
    title_en: str | None
    status: str | None
    raw_text: str


@dataclass(frozen=True)
class IntakeForm:
    ma: str
    cost_cny: str | None
    sell_usd: str | None
    created_at: str | None
    link: str | None


@dataclass(frozen=True)
class HomeView:
    sha256: str | None
    refetch_sha256: str | None
    prices: dict[str, Decimal | None] | None


@dataclass(frozen=True)
class ImageCheck:
    ok: bool
    status: int | None


@dataclass
class Night:
    day: str
    checked_at: str
    timezone: str
    origins: tuple[str, ...]
    products: list[CatalogProduct]
    blob_state: SourceState
    blob_updated_at: str | None
    blob_sha256: str | None
    blob_etag: str | None
    blob_last_modified: str | None
    blob_age_seconds: int | None
    hub_rows: list[MoneyRow] | None
    hub_state: SourceState
    hub_sha256: str | None
    hub_last_modified: str | None
    intake: list[IntakeForm]
    intake_state: SourceState
    pdp: dict[str, dict[str, PdpView]]
    homes: dict[str, HomeView]
    images: list[ImageCheck]
    main_sha: str | None
    context: dict[str, object] = field(default_factory=dict)


@dataclass(frozen=True)
class Finding:
    kind: str
    name: str
    detail: str


def http_get(url: str, timeout: float = 20) -> HttpResult:
    """GET only. Midnight QC never posts a price, a catalog, or a form."""
    request = urllib.request.Request(
        url,
        headers={"User-Agent": USER_AGENT, "Accept": "*/*"},
        method="GET",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            raw_headers = getattr(response, "headers", {})
            return HttpResult(
                getattr(response, "status", 200),
                response.read(),
                _header_map(raw_headers),
                None,
            )
    except urllib.error.HTTPError as error:
        raw = error.read() if error.fp else b""
        return HttpResult(error.code, raw, _header_map(error.headers), None)
    except Exception as error:  # noqa: BLE001 — a down host is a source result
        return HttpResult(0, b"", {}, str(error))


def _header_map(headers: object) -> dict[str, str]:
    if headers is None:
        return {}
    items = headers.items() if hasattr(headers, "items") else ()
    return {str(key).lower(): str(value) for key, value in items}


def parse_home_prices(html: str) -> dict[str, Decimal | None]:
    found: dict[str, Decimal | None] = {}
    for match in _HOME_PRICE_RE.finditer(html):
        ma = match.group("ma").upper()
        raw = match.group("price")
        price = None if raw == "null" else parse_usd(raw)
        previous = found.get(ma)
        if ma in found and previous != price:
            found[ma] = None
            continue
        found[ma] = price
    return found


def catalog_products(payload: object) -> list[CatalogProduct]:
    """Titles stay here. USD comes from freshness_check.parse_blob_catalog."""
    parsed = parse_blob_catalog(payload)
    if not isinstance(payload, dict) or not isinstance(payload.get("products"), list):
        raise ValueError("blob catalog has no products")
    products: list[CatalogProduct] = []
    for item in payload["products"]:
        if not isinstance(item, dict):
            continue
        raw_ma = item.get("ma")
        if not isinstance(raw_ma, str) or not raw_ma.strip():
            continue
        title = item.get("titleEn")
        status = item.get("status")
        products.append(
            CatalogProduct(
                norm_ma(raw_ma),
                parse_usd(item.get("priceUsd")),
                title.strip() if isinstance(title, str) and title.strip() else None,
                status.strip().lower() if isinstance(status, str) and status.strip() else None,
                json.dumps(item, ensure_ascii=False).lower(),
            )
        )
    if [item.ma for item in products] != [row.ma for row in parsed]:
        raise ValueError("blob parse mismatch")
    if [item.price_usd for item in products] != [row.price_usd for row in parsed]:
        raise ValueError("blob price mismatch")
    return products


def summary_from_payload(payload: object, *, root: Path | None = None) -> tuple[dict[str, object], str]:
    night = night_from_payload(payload, root=root or ROOT)
    return render_night(night, root=root or ROOT)


def night_from_payload(payload: object, *, root: Path | None = None) -> Night:
    if not isinstance(payload, dict):
        raise ValueError("fixture must be a JSON object")
    day = payload.get("day", payload.get("date"))
    if not isinstance(day, str) or re.fullmatch(r"\d{4}-\d{2}-\d{2}", day) is None:
        raise ValueError("fixture day must be YYYY-MM-DD")
    origins_raw = payload.get("origins", list(SELL_ORIGINS))
    if not isinstance(origins_raw, list) or not all(isinstance(item, str) for item in origins_raw):
        raise ValueError("fixture origins must be a list of hosts")
    checked = payload.get("checkedAt")
    if checked is None:
        checked_at = _utc_now()
    elif isinstance(checked, str) and checked.strip():
        checked_at = checked.strip()
    else:
        raise ValueError("fixture checkedAt must be a string")
    zone = payload.get("timezone", TIMEZONE)
    if not isinstance(zone, str) or not zone.strip():
        raise ValueError("fixture timezone must be a string")
    products, blob_state, blob_meta = _blob_from_payload(payload.get("blob"))
    hub_rows, hub_state, hub_sha, hub_modified = _hub_from_payload(payload)
    intake, intake_state = _intake_from_payload(payload.get("intake"))
    context = payload.get("context", {})
    if not isinstance(context, dict):
        raise ValueError("fixture context must be an object")
    main = payload.get("main", {})
    if not isinstance(main, dict):
        raise ValueError("fixture main must be an object")
    main_sha = main.get("sha")
    if main_sha is not None and not isinstance(main_sha, str):
        raise ValueError("fixture main.sha must be a string")
    return Night(
        day=day,
        checked_at=checked_at,
        timezone=zone.strip(),
        origins=tuple(origins_raw),
        products=products,
        blob_state=blob_state,
        blob_updated_at=_optional_str(blob_meta.get("updatedAt")),
        blob_sha256=_optional_str(blob_meta.get("sha256")),
        blob_etag=_optional_str(blob_meta.get("etag")),
        blob_last_modified=_optional_str(blob_meta.get("lastModified")),
        blob_age_seconds=_optional_int(blob_meta.get("ageSeconds")),
        hub_rows=hub_rows,
        hub_state=hub_state,
        hub_sha256=hub_sha,
        hub_last_modified=hub_modified,
        intake=intake,
        intake_state=intake_state,
        pdp=_pdp_block(payload.get("pdp", {})),
        homes=_homes_from_payload(payload.get("homes", {})),
        images=_images_from_payload(payload.get("images")),
        main_sha=main_sha.strip() if isinstance(main_sha, str) and main_sha.strip() else _origin_main_sha(root or ROOT),
        context=context,
    )


def render_night(night: Night, *, root: Path | None = None) -> tuple[dict[str, object], str]:
    policy = load_held_policy()
    report = evaluate(_freshness_snapshot(night), policy)
    flags = _shop_flags(root or ROOT)
    findings, warnings = _findings(night, policy)
    for guard in report.guards:
        if guard.ok or any(item.name == guard.name for item in findings):
            continue
        kind = "sell" if _guard_is_sell(guard.name) else "data"
        findings.append(Finding(kind, guard.name, guard.detail))
    data_fail = (not report.guards_pass) or any(item.kind == "data" for item in findings)
    sell_fail = any(item.kind == "sell" for item in findings)
    data_ok = "FAIL" if data_fail else "PASS"
    sell_site = "FAIL" if sell_fail else "PASS"
    overall = "FAIL" if data_ok == "FAIL" or sell_site == "FAIL" else "PASS"
    blob_prices = _price_index(night.products)
    live_prices = _live_price_index(night.products)
    hub_prices = None if night.hub_rows is None else {row.ma: row.price_usd for row in night.hub_rows}
    intake_index = {row.ma: row for row in night.intake}
    blob_hub = [] if hub_prices is None else _usd_mismatches(blob_prices, hub_prices)
    intake_lags = _intake_lags(live_prices, intake_index)
    ops_held = _ops_held(night.intake, blob_prices)
    summary = _summary_dict(
        night,
        policy,
        flags,
        overall=overall,
        data_ok=data_ok,
        sell_site=sell_site,
        guards_pass=report.guards_pass,
        blob_prices=blob_prices,
        live_prices=live_prices,
        hub_prices=hub_prices,
        intake_index=intake_index,
        blob_hub=blob_hub,
        intake_lags=intake_lags,
        ops_held=ops_held,
        warnings=warnings,
        findings=findings,
    )
    markdown = _render_markdown(
        summary,
        night,
        live_prices,
        hub_prices,
        intake_index,
        ops_held,
        warnings,
        findings,
        policy,
    )
    return summary, markdown


def fetch_night(day: str, *, check_images: bool = False) -> dict[str, object]:
    """Read Blob, intake, hub (via freshness_check), and both sell hosts.

    No Taobao request. No Meta request. No catalog write.
    """
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", day) is None:
        raise ValueError("date must be YYYY-MM-DD")
    blob_url = os.environ.get("SASSY_BLOB_CATALOG_URL", freshness_check.DEFAULT_BLOB_URL).strip()
    blob_response = http_get(blob_url)
    blob_block = _blob_block_from_http(blob_response)
    intake_response = http_get(freshness_check.INTAKE_URL)
    intake_block = _intake_block_from_http(intake_response)
    hub_rows, hub_state, hub_sha = _hub_live()
    products = blob_block.get("products") if isinstance(blob_block.get("products"), list) else []
    forms = intake_block.get("submissions") if isinstance(intake_block.get("submissions"), list) else []
    codes = _live_codes(products, forms)
    pdp: dict[str, dict[str, dict[str, object]]] = {}
    for code in codes:
        pdp[code] = {}
        for origin in SELL_ORIGINS:
            pdp[code][origin] = _pdp_cell_from_http(http_get(f"{origin}/m/{code}"))
    homes: dict[str, dict[str, object]] = {}
    for origin in SELL_ORIGINS:
        first = http_get(origin)
        second = http_get(origin) if origin == PRIMARY_ORIGIN else None
        homes[origin] = _home_block(first, second)
    images: list[dict[str, object]] | None = None
    if check_images and blob_block.get("state") == "ok":
        images = _image_checks(products, PRIMARY_ORIGIN)
    hub_block: dict[str, object]
    if hub_rows is None:
        hub_block = {"state": "skip", "detail": hub_state.detail}
    else:
        hub_block = {
            "state": "ok",
            "detail": hub_state.detail,
            "sha256": hub_sha,
            "rows": [{"ma": row.ma, "price_usd": money_text(row.price_usd)} for row in hub_rows],
        }
    payload: dict[str, object] = {
        "day": day,
        "checkedAt": _utc_now(),
        "timezone": TIMEZONE,
        "origins": list(SELL_ORIGINS),
        "blob": blob_block,
        "hub": hub_block,
        "intake": intake_block,
        "pdp": pdp,
        "homes": homes,
    }
    if images is not None:
        payload["images"] = images
    return payload


def write_night(summary: dict[str, object], markdown: str, out_dir: Path) -> tuple[Path, Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    summary_path = out_dir / "summary.json"
    data_path = out_dir / "data-ok.md"
    summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    data_path.write_text(markdown, encoding="utf-8")
    return summary_path, data_path


def _freshness_snapshot(night: Night):
    blob_block: dict[str, object]
    if night.blob_state.state == "skip":
        blob_block = {"state": "skip", "detail": night.blob_state.detail}
    else:
        blob_block = {
            "state": "ok",
            "detail": night.blob_state.detail,
            "rows": [{"ma": item.ma, "price_usd": money_text(item.price_usd)} for item in night.products],
        }
    hub_block: dict[str, object]
    if night.hub_rows is None:
        hub_block = {"state": "skip", "detail": night.hub_state.detail}
    else:
        hub_block = {
            "state": "ok",
            "detail": night.hub_state.detail,
            "rows": [{"ma": row.ma, "price_usd": money_text(row.price_usd)} for row in night.hub_rows],
        }
    pdp: dict[str, dict[str, dict[str, object]]] = {}
    for ma, hosts in night.pdp.items():
        pdp[ma] = {}
        for origin, view in hosts.items():
            pdp[ma][origin] = {
                "status": view.status,
                "price_usd": money_text(view.price_usd),
                "error": view.error,
            }
    return snapshot_from_json(
        {
            "day": night.day,
            "origins": list(night.origins),
            "intakeState": {"state": night.intake_state.state, "detail": night.intake_state.detail},
            "intake": [
                {
                    "ma": row.ma,
                    "cost_cny": row.cost_cny,
                    "sell_usd": row.sell_usd,
                    "link": row.link,
                }
                for row in night.intake
            ],
            "blob": blob_block,
            "hub": hub_block,
            "pdp": pdp,
            "taobao": [],
            "taobaoMode": "logged-out",
            "metaMode": "logged-out",
        }
    )


def _findings(night: Night, policy: HeldPolicy) -> tuple[list[Finding], list[Finding]]:
    findings: list[Finding] = []
    warnings: list[Finding] = []
    if set(night.origins) != set(SELL_ORIGINS):
        findings.append(Finding("sell", "sell-hosts", "both sell hosts are required"))
    if night.blob_state.state != "ok":
        findings.append(Finding("data", "blob-source", night.blob_state.detail or "blob source skipped"))
    if night.intake_state.state != "ok":
        findings.append(Finding("data", "intake-source", night.intake_state.detail or "intake source skipped"))
    blob_prices = _price_index(night.products)
    live_prices = _live_price_index(night.products)
    hub_prices = None if night.hub_rows is None else {row.ma: row.price_usd for row in night.hub_rows}
    if hub_prices is None:
        detail = night.hub_state.detail or "hub source skipped"
        warnings.append(Finding("warn", "W-hub", f"{detail} The hub parser was not rewritten."))
    else:
        for item in _usd_mismatches(blob_prices, hub_prices):
            findings.append(Finding("data", "blob-hub-usd", item))
    for item in _host_price_problems(live_prices, night):
        findings.append(Finding("sell", "sell-price", item))
    for item in _home_problems(live_prices, night):
        findings.append(Finding("sell", "home-price", item))
    ops = _ops_held(night.intake, blob_prices)
    omitted = [ma for ma in ops if ma not in policy.held and ma != Q02]
    if omitted:
        warnings.append(
            Finding(
                "warn",
                "W-held-gap",
                "data/held.json omits "
                + ", ".join(omitted)
                + ". They stay off sell. This file was not rewritten.",
            )
        )
    for ma in ops:
        if ma in policy.held:
            continue
        _ops_held_findings(ma, night, blob_prices, hub_prices, findings)
    if _q02_live(night, blob_prices, hub_prices):
        findings.append(Finding("data", "q02-live", "Q02 is on Blob, hub, or a sell PDP"))
    elif Q02 in {row.ma for row in night.intake}:
        warnings.append(
            Finding(
                "warn",
                "W-q02",
                "Q02 is in intake and is not on sell. It stays held until Boss approves.",
            )
        )
    if _intake_lags(live_prices, {row.ma: row for row in night.intake}):
        warnings.append(
            Finding(
                "warn",
                "W-intake",
                "Stored intake sell_usd lags live Blob. No price was written.",
            )
        )
    if not night.images:
        warnings.append(Finding("note", "N-images", "Catalog images were not checked on this run."))
    warnings.append(Finding("note", "N-meta", "No Meta read. Meta is not CLEAR and is not a sell FAIL."))
    return findings, warnings


def _ops_held_findings(
    ma: str,
    night: Night,
    blob_prices: dict[str, Decimal | None],
    hub_prices: dict[str, Decimal | None] | None,
    findings: list[Finding],
) -> None:
    if ma in blob_prices:
        findings.append(Finding("data", f"ops-held:{ma}", f"{ma} is on Blob and is not in data/held.json"))
    if hub_prices is not None and ma in hub_prices:
        findings.append(Finding("data", f"ops-held-hub:{ma}", f"{ma} is on hub Official"))
    for origin in night.origins:
        view = night.pdp.get(ma, {}).get(origin)
        if view is None or view.status != 404:
            status = "not checked" if view is None or view.status is None else f"HTTP {view.status}"
            findings.append(Finding("sell", f"ops-held-pdp:{ma}:{origin}", f"{ma} PDP {status}"))


def _summary_dict(
    night: Night,
    policy: HeldPolicy,
    flags: dict[str, bool],
    *,
    overall: str,
    data_ok: str,
    sell_site: str,
    guards_pass: bool,
    blob_prices: dict[str, Decimal | None],
    live_prices: dict[str, Decimal | None],
    hub_prices: dict[str, Decimal | None] | None,
    intake_index: dict[str, IntakeForm],
    blob_hub: list[str],
    intake_lags: list[str],
    ops_held: list[str],
    warnings: list[Finding],
    findings: list[Finding],
) -> dict[str, object]:
    del warnings
    v05 = intake_index.get("V05")
    primary_home = night.homes.get(PRIMARY_ORIGIN)
    alias_home = night.homes.get(ALIAS_ORIGIN)
    fields: dict[str, object] = {
        "date": night.day,
        "checkedAt": night.checked_at,
        "timezone": night.timezone,
        "overall": overall,
        "dataOk": data_ok,
        "sellSite": sell_site,
        "metaLight": "NOTE",
        "blobCount": None if night.blob_state.state != "ok" else len(live_prices),
        "sellCount": _sell_count(night, live_prices),
        "hubCount": None if hub_prices is None else len(hub_prices),
        "intakeCount": None if night.intake_state.state != "ok" else len(night.intake),
        "heldCount": len(ops_held) if night.blob_state.state == "ok" and night.intake_state.state == "ok" else len(policy.held),
        "s06Usd": _json_number(blob_prices.get(S06)) if S06 in blob_prices else None,
        "a02TitleEn": next((item.title_en for item in night.products if item.ma == "A02"), None),
        "k06OnBlob": "K06" in blob_prices,
        "k06Pdp": _primary_status(night, "K06"),
        "v05OnBlob": "V05" in blob_prices,
        "v05Pdp": _primary_status(night, "V05"),
        "v05IntakeCostCny": None if v05 is None else v05.cost_cny,
        "v05CreatedAt": None if v05 is None else v05.created_at,
        "v05SellUsd": None if v05 is None else _json_number(parse_usd(v05.sell_usd)),
        "blobUpdatedAt": night.blob_updated_at,
        "blobSha256": night.blob_sha256,
        "blobEtag": night.blob_etag,
        "blobLastModifiedHeader": night.blob_last_modified,
        "blobAgeSecondsAtCheckedAt": night.blob_age_seconds,
        "hubSha256": night.hub_sha256,
        "hubLastModified": night.hub_last_modified,
        "homeSha256": None if primary_home is None else primary_home.sha256,
        "aliasFirstFetchSha256": None if alias_home is None else alias_home.sha256,
        "homeRefetchSha256": _refetch_sha(primary_home),
        "mainSha": night.main_sha,
        "mainHeldList": list(policy.held),
        "mainIncludesK06": "K06" in policy.held,
        "mainIncludesV05": "V05" in policy.held,
        "mainNeverList": list(policy.never_list),
        "saveRouteCallsHeldCheck": flags["saveRouteCallsHeldCheck"],
        "shopMintRefusesHeld": flags["shopMintRefusesHeld"],
        "shopSaveRefusesOffLockS06": flags["shopSaveRefusesOffLockS06"],
        "blobHubUsdMismatches": blob_hub,
        "intakeVsBlobMismatches": intake_lags,
        "heldAbsent": _held_absent(night, policy, ops_held, blob_prices, hub_prices),
        "q02Absent": _q02_absent(night, blob_prices, hub_prices),
        "b01Referenced": any("gail" in item.raw_text for item in night.products),
        "imagesChecked": len(night.images),
        "imagesOk": sum(1 for item in night.images if item.ok),
        "pr105Url": _context(night, "pr105Url", PR105_URL),
        "pr105Draft": _context(night, "pr105Draft", None),
        "pr105Head": _context(night, "pr105Head", None),
        "pr105AddsV05": _context(night, "pr105AddsV05", None),
        "pr101Head": _context(night, "pr101Head", None),
        "pr101Draft": _context(night, "pr101Draft", None),
        "pr101State": _context(night, "pr101State", None),
        "newDraftPr": _context(night, "newDraftPr", None),
        "newDraftPrHead": _context(night, "newDraftPrHead", None),
        "bossPing": False,
        "unchangedOpenPrs": _open_prs(night),
        "freshnessGuards": "PASS" if guards_pass else "FAIL",
        "freshnessHub": "skip" if night.hub_rows is None else "ok",
    }
    for key, cutoff in NEW_INTAKE_CUTOFFS:
        fields[key] = _new_intake(night.intake, cutoff)
    fields.update(_changed_since(night, fields, findings))
    fields["notes"] = _notes(fields, findings)
    return _ordered(fields)


def _render_markdown(
    summary: dict[str, object],
    night: Night,
    live_prices: dict[str, Decimal | None],
    hub_prices: dict[str, Decimal | None] | None,
    intake_index: dict[str, IntakeForm],
    ops_held: list[str],
    warnings: list[Finding],
    findings: list[Finding],
    policy: HeldPolicy,
) -> str:
    lines = [
        f"# DATA OK — Midnight QC {summary['date']}",
        "",
        (
            f"Live data result: **{summary['dataOk']}**. "
            f"Sell site: **{summary['sellSite']}**. Overall: **{summary['overall']}**."
        ),
        "",
        "Read only. No live catalog write. No reprice. No Blob write. No intake write. No merge. No Meta write.",
        "",
        (
            f"Checked {summary['checkedAt']} ({summary['timezone']}). "
            f"S06 is {_dollar(summary['s06Usd'])}. "
            f"freshness guards {summary['freshnessGuards']}. "
            f"freshness hub {summary['freshnessHub']}."
        ),
        "",
        "## Counts",
        "",
        "| set | count |",
        "|---|---|",
        f"| Blob live | {_count_cell(summary['blobCount'])} |",
        f"| Hub Official live | {_count_cell(summary['hubCount'])} |",
        f"| Sell | {_count_cell(summary['sellCount'])} |",
        f"| Intake forms | {_count_cell(summary['intakeCount'])} |",
        f"| Intake held staged, off Blob | {_count_cell(summary['heldCount'])} |",
        f"| Blob↔hub USD mismatches | {len(summary['blobHubUsdMismatches']) if isinstance(summary['blobHubUsdMismatches'], list) else '—'} |",
        "",
        "## Blob↔hub mismatch table",
        "",
        "mã | field | blob | hub | intake | result",
        "--- | --- | --- | --- | --- | ---",
    ]
    mismatches = summary["blobHubUsdMismatches"]
    if isinstance(mismatches, list) and mismatches:
        for item in mismatches:
            lines.append(_mismatch_row(str(item), "sell_usd", intake_index, intake_lag=False))
    else:
        lines.append("")
        if summary["freshnessHub"] == "skip":
            lines.append("Empty. Hub source skipped, so USD was not compared here.")
        else:
            lines.append("Empty. Every live mã has the same USD on Blob and hub Official.")
    lines.extend(
        [
            "",
            "## Intake mismatch table",
            "",
            "mã | field | blob | hub | intake | result",
            "--- | --- | --- | --- | --- | ---",
        ]
    )
    lags = summary["intakeVsBlobMismatches"]
    if isinstance(lags, list) and lags:
        for item in lags:
            lines.append(_mismatch_row(str(item), "sell_usd", intake_index, intake_lag=True))
    else:
        lines.append("")
        lines.append("Empty. No stored numeric sell_usd differs from Blob.")
    lines.extend(["", "## WARN / NOTE", "", "| id | kind | what | proof |", "|---|---|---|---|"])
    if warnings:
        for item in warnings:
            lines.append(f"| {item.name} | {item.kind.upper()} | {_cell(item.detail)} | freshness + this read |")
    else:
        lines.append("| — | — | none | — |")
    lines.extend(["", "## FAIL", ""])
    if findings:
        for item in findings:
            lines.append(f"- {item.kind} `{item.name}` — {item.detail}")
    else:
        lines.append("None.")
    lines.extend(
        [
            "",
            "## Every live mã",
            "",
            "mã | blob | hub | intake sell_usd | result",
            "--- | --- | --- | --- | ---",
        ]
    )
    for ma in sorted(live_prices):
        lines.append(_live_row(ma, live_prices, hub_prices, intake_index))
    lines.extend(
        [
            "",
            "## Held, and Q02",
            "",
            "mã | blob | hub | sell PDP | intake | result",
            "--- | --- | --- | --- | ---",
        ]
    )
    held_rows = list(dict.fromkeys([*policy.held, *ops_held, Q02]))
    for ma in held_rows:
        lines.append(_held_row(ma, night, hub_prices, intake_index))
    lines.extend(
        [
            "",
            "## Sources",
            "",
            f"- Blob: {night.blob_state.state} — {night.blob_state.detail or '—'}",
            f"- Hub: {night.hub_state.state} — {night.hub_state.detail or '—'}",
            f"- Intake: {night.intake_state.state} — {night.intake_state.detail or '—'}",
            f"- Sell hosts: {PRIMARY_ORIGIN} and {ALIAS_ORIGIN}",
            f"- origin/main: {summary['mainSha'] or '—'}",
            f"- data/held.json heldIncomplete: {', '.join(policy.held) or '—'}",
            f"- neverList: {', '.join(policy.never_list) or 'empty'}",
            "- Meta: NOTE. No Meta read and no Meta write.",
            "",
        ]
    )
    return "\n".join(lines)


def _blob_from_payload(value: object) -> tuple[list[CatalogProduct], SourceState, dict[str, object]]:
    if not isinstance(value, dict):
        raise ValueError("fixture blob must be an object")
    state = str(value.get("state", "ok"))
    detail = "" if value.get("detail") is None else str(value.get("detail"))
    meta = {
        "updatedAt": value.get("updatedAt"),
        "sha256": value.get("sha256"),
        "etag": value.get("etag"),
        "lastModified": value.get("lastModified"),
        "ageSeconds": value.get("ageSeconds"),
    }
    if state == "skip":
        return [], SourceState("skip", detail), meta
    products = value.get("products", [])
    if not isinstance(products, list):
        raise ValueError("fixture blob products must be a list")
    return catalog_products({"products": products}), SourceState(state, detail or f"{len(products)} products"), meta


def _hub_from_payload(payload: dict[str, object]) -> tuple[list[MoneyRow] | None, SourceState, str | None, str | None]:
    hub_file = payload.get("hubFile")
    hub = payload.get("hub")
    if hub_file is not None and hub is not None:
        raise ValueError("fixture hubFile and hub are mutually exclusive")
    if isinstance(hub_file, str) and hub_file.strip():
        path = Path(hub_file)
        sha = hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None
        try:
            rows = read_hub_official(path)
        except (OSError, ValueError) as exc:
            return None, SourceState("skip", str(exc)), sha, None
        return rows, SourceState("ok", f"{len(rows)} Official rows"), sha, None
    if hub is None:
        return None, SourceState("skip", "no hub rows"), None, None
    if not isinstance(hub, dict):
        raise ValueError("fixture hub must be an object")
    state = str(hub.get("state", "ok"))
    detail = "" if hub.get("detail") is None else str(hub.get("detail"))
    sha = _optional_str(hub.get("sha256"))
    modified = _optional_str(hub.get("lastModified"))
    if state == "skip":
        return None, SourceState("skip", detail), sha, modified
    raw_rows = hub.get("rows", [])
    if not isinstance(raw_rows, list):
        raise ValueError("fixture hub rows must be a list")
    rows: list[MoneyRow] = []
    for item in raw_rows:
        if not isinstance(item, dict) or not isinstance(item.get("ma"), str):
            raise ValueError("fixture hub row needs a mã")
        rows.append(MoneyRow(norm_ma(item["ma"]), parse_usd(item.get("price_usd", item.get("priceUsd")))))
    return rows, SourceState(state, detail or f"{len(rows)} Official rows"), sha, modified


def _intake_from_payload(value: object) -> tuple[list[IntakeForm], SourceState]:
    if value is None:
        return [], SourceState("skip", "no intake")
    if isinstance(value, list):
        block: dict[str, object] = {"state": "ok", "submissions": value}
    elif isinstance(value, dict):
        block = value
    else:
        raise ValueError("fixture intake must be an object")
    state = str(block.get("state", "ok"))
    detail = "" if block.get("detail") is None else str(block.get("detail"))
    if state == "skip":
        return [], SourceState("skip", detail)
    raw_rows = block.get("submissions", [])
    if not isinstance(raw_rows, list):
        raise ValueError("fixture intake submissions must be a list")
    rows: list[IntakeForm] = []
    for item in raw_rows:
        if not isinstance(item, dict) or not isinstance(item.get("ma"), str):
            raise ValueError("fixture intake row needs a mã")
        created = item.get("created_at", item.get("createdAt"))
        rows.append(
            IntakeForm(
                norm_ma(item["ma"]),
                None if item.get("cost_cny") is None else str(item.get("cost_cny")),
                None if item.get("sell_usd") is None else str(item.get("sell_usd")),
                None if created is None else str(created),
                None if item.get("link") is None else str(item.get("link")),
            )
        )
    return rows, SourceState(state, detail or f"{len(rows)} forms")


def _homes_from_payload(value: object) -> dict[str, HomeView]:
    if value is None:
        return {}
    if not isinstance(value, dict):
        raise ValueError("fixture homes must be an object")
    homes: dict[str, HomeView] = {}
    for origin, cell in value.items():
        if not isinstance(origin, str) or not isinstance(cell, dict):
            raise ValueError("fixture home cell is invalid")
        prices = cell.get("prices")
        parsed: dict[str, Decimal | None] | None
        if prices is None:
            parsed = None
        elif isinstance(prices, dict):
            parsed = {}
            for ma, price in prices.items():
                if not isinstance(ma, str):
                    raise ValueError("fixture home price mã must be a string")
                parsed[norm_ma(ma)] = parse_usd(price)
        else:
            raise ValueError("fixture home prices must be an object")
        homes[origin] = HomeView(
            _optional_str(cell.get("sha256")),
            _optional_str(cell.get("refetchSha256")),
            parsed,
        )
    return homes


def _images_from_payload(value: object) -> list[ImageCheck]:
    if value is None:
        return []
    if not isinstance(value, list):
        raise ValueError("fixture images must be a list")
    images: list[ImageCheck] = []
    for item in value:
        if not isinstance(item, dict):
            raise ValueError("fixture image must be an object")
        status = item.get("status")
        if "ok" in item:
            ok = bool(item.get("ok"))
        else:
            ok = status in (200, 206)
        images.append(ImageCheck(ok, None if status is None else int(status)))
    return images


def _pdp_block(value: object) -> dict[str, dict[str, PdpView]]:
    snapshot = snapshot_from_json(
        {
            "day": "2026-10-14",
            "origins": list(SELL_ORIGINS),
            "intake": [],
            "blob": {"state": "skip"},
            "hub": {"state": "skip"},
            "pdp": value,
        }
    )
    return snapshot.pdp


def _price_index(products: list[CatalogProduct]) -> dict[str, Decimal | None]:
    return {item.ma: item.price_usd for item in products}


def _live_price_index(products: list[CatalogProduct]) -> dict[str, Decimal | None]:
    return {
        item.ma: item.price_usd
        for item in products
        if item.status in (None, "available", "live")
    }


def _ops_held(intake: list[IntakeForm], blob_prices: dict[str, Decimal | None]) -> list[str]:
    return [row.ma for row in intake if row.ma not in blob_prices]


def _usd_mismatches(
    blob_prices: dict[str, Decimal | None],
    hub_prices: dict[str, Decimal | None],
) -> list[str]:
    rows: list[str] = []
    for ma in sorted(set(blob_prices) | set(hub_prices)):
        on_blob = ma in blob_prices
        on_hub = ma in hub_prices
        blob = blob_prices.get(ma)
        hub = hub_prices.get(ma)
        if on_blob and on_hub and blob == hub:
            continue
        rows.append(f"{ma} {_side(blob if on_blob else None)}→{_side(hub if on_hub else None)}")
    return rows


def _intake_lags(
    live_prices: dict[str, Decimal | None],
    intake_index: dict[str, IntakeForm],
) -> list[str]:
    rows: list[str] = []
    for ma in sorted(live_prices):
        form = intake_index.get(ma)
        if form is None:
            continue
        stored = parse_usd(form.sell_usd)
        live = live_prices[ma]
        if stored is None or live is None or stored == live:
            continue
        rows.append(f"{ma} {money_text(stored)}→{money_text(live)}")
    return rows


def _host_price_problems(live_prices: dict[str, Decimal | None], night: Night) -> list[str]:
    problems: list[str] = []
    for ma, price in sorted(live_prices.items()):
        for origin in (PRIMARY_ORIGIN, ALIAS_ORIGIN):
            if origin not in night.origins:
                continue
            view = night.pdp.get(ma, {}).get(origin)
            if view is None or view.status != 200:
                status = "not checked" if view is None or view.status is None else f"HTTP {view.status}"
                problems.append(f"{ma} {origin} {status}")
            elif view.price_usd != price:
                problems.append(f"{ma} {origin} USD {money_text(view.price_usd)} blob {money_text(price)}")
    return problems


def _home_problems(live_prices: dict[str, Decimal | None], night: Night) -> list[str]:
    if not night.homes:
        return []
    problems: list[str] = []
    for origin in (PRIMARY_ORIGIN, ALIAS_ORIGIN):
        home = night.homes.get(origin)
        if home is None or home.prices is None:
            problems.append(f"home prices missing for {origin}")
            continue
        if set(home.prices) != set(live_prices):
            problems.append(f"home mã set on {origin} does not match Blob")
        for ma, price in live_prices.items():
            if ma in home.prices and home.prices[ma] != price:
                problems.append(f"{ma} home {origin} USD {money_text(home.prices[ma])} blob {money_text(price)}")
    return problems


def _held_absent(
    night: Night,
    policy: HeldPolicy,
    ops_held: list[str],
    blob_prices: dict[str, Decimal | None],
    hub_prices: dict[str, Decimal | None] | None,
) -> bool:
    codes = list(dict.fromkeys([*policy.held, *ops_held]))
    return all(_code_absent(ma, night, blob_prices, hub_prices) for ma in codes)


def _code_absent(
    ma: str,
    night: Night,
    blob_prices: dict[str, Decimal | None],
    hub_prices: dict[str, Decimal | None] | None,
) -> bool:
    if ma in blob_prices:
        return False
    if hub_prices is not None and ma in hub_prices:
        return False
    for origin in night.origins:
        view = night.pdp.get(ma, {}).get(origin)
        if view is None or view.status != 404:
            return False
    return True


def _q02_live(
    night: Night,
    blob_prices: dict[str, Decimal | None],
    hub_prices: dict[str, Decimal | None] | None,
) -> bool:
    if Q02 in blob_prices:
        return True
    if hub_prices is not None and Q02 in hub_prices:
        return True
    for origin in night.origins:
        view = night.pdp.get(Q02, {}).get(origin)
        if view is not None and view.status is not None and view.status != 404:
            return True
    return False


def _q02_absent(
    night: Night,
    blob_prices: dict[str, Decimal | None],
    hub_prices: dict[str, Decimal | None] | None,
) -> bool:
    in_intake = any(row.ma == Q02 for row in night.intake)
    on_hub = hub_prices is not None and Q02 in hub_prices
    return Q02 not in blob_prices and not in_intake and not on_hub and not _q02_live(night, blob_prices, hub_prices)


def _sell_count(night: Night, live_prices: dict[str, Decimal | None]) -> int | None:
    if night.blob_state.state != "ok":
        return None
    home = night.homes.get(PRIMARY_ORIGIN)
    if home is not None and home.prices is not None:
        return len(home.prices)
    count = 0
    for ma in live_prices:
        view = night.pdp.get(ma, {}).get(PRIMARY_ORIGIN)
        if view is not None and view.status == 200:
            count += 1
    return count


def _primary_status(night: Night, ma: str) -> int | None:
    view = night.pdp.get(ma, {}).get(PRIMARY_ORIGIN)
    if view is None:
        return None
    return view.status


def _new_intake(intake: list[IntakeForm], cutoff: str) -> list[str]:
    rows = [row for row in intake if row.created_at is not None and row.created_at[:10] >= cutoff[:10]]
    rows.sort(key=lambda row: (row.created_at or "", row.ma))
    return [row.ma for row in rows]


def _changed_since(
    night: Night,
    fields: dict[str, object],
    findings: list[Finding],
) -> dict[str, object]:
    latest = (
        f"Read-only midnight QC. Blob {fields['blobCount']}, hub {fields['hubCount']}, "
        f"sell {fields['sellCount']}, intake {fields['intakeCount']}, held {fields['heldCount']}. "
        f"S06 is {_dollar(fields['s06Usd'])}. freshness guards {fields['freshnessGuards']}. "
        f"freshness hub {fields['freshnessHub']}. Findings {len(findings)}. "
        "No live price was changed."
    )
    generated = {
        "changedSince20261007": ["See changedSince20261011."],
        "changedSince20261009": ["See changedSince20261011."],
        "changedSince20261010": ["See changedSince20261011."],
        "changedSince20261011": [latest],
    }
    for key in generated:
        override = night.context.get(key)
        if isinstance(override, list) and all(isinstance(item, str) for item in override):
            generated[key] = override
    return generated


def _notes(fields: dict[str, object], findings: list[Finding]) -> str:
    finding_text = " No FAIL." if not findings else " FAIL: " + "; ".join(item.detail for item in findings) + "."
    return (
        f"Data {fields['dataOk']}. Sell {fields['sellSite']}. "
        f"Blob {fields['blobCount']}, hub {fields['hubCount']}, sell {fields['sellCount']}, "
        f"intake {fields['intakeCount']}, held {fields['heldCount']}. "
        f"S06 is {_dollar(fields['s06Usd'])}. "
        f"freshness guards {fields['freshnessGuards']}. freshness hub {fields['freshnessHub']}. "
        "Meta is not CLEAR and is not a sell FAIL. No Boss ping. No live price was changed."
        + finding_text
    )


def _ordered(fields: dict[str, object]) -> dict[str, object]:
    missing = [key for key in SUMMARY_KEYS if key not in fields]
    extra = [key for key in fields if key not in SUMMARY_KEYS]
    if missing or extra:
        raise RuntimeError(f"summary shape missing {missing} extra {extra}")
    return {key: fields[key] for key in SUMMARY_KEYS}


def _context(night: Night, key: str, default: object) -> object:
    if key not in night.context:
        return default
    return night.context[key]


def _open_prs(night: Night) -> dict[str, str]:
    raw = night.context.get("unchangedOpenPrs", {})
    if raw is None:
        return {}
    if not isinstance(raw, dict):
        raise ValueError("fixture unchangedOpenPrs must be an object")
    cleaned: dict[str, str] = {}
    for key, value in raw.items():
        if not isinstance(key, str) or not isinstance(value, str):
            raise ValueError("fixture unchangedOpenPrs entries must be strings")
        cleaned[key] = value
    return cleaned


def _shop_flags(root: Path) -> dict[str, bool]:
    route = _read_text(root / "sassy-closet-shop/app/api/admin/save/route.ts")
    ops = _read_text(root / "sassy-closet-shop/lib/admin-ops.ts")
    return {
        "saveRouteCallsHeldCheck": "isHeldIncompleteMa" in route,
        "shopMintRefusesHeld": "isOffLiveSell" in _function_body(ops, "addProductToCatalog"),
        "shopSaveRefusesOffLockS06": "S06 stays $25" in _function_body(ops, "saveProductInCatalog"),
    }


def _function_body(source: str, name: str) -> str:
    marker = f"function {name}"
    start = source.find(marker)
    if start < 0:
        return ""
    nxt = source.find("\nexport function ", start + len(marker))
    if nxt < 0:
        nxt = source.find("\nfunction ", start + len(marker))
    if nxt < 0:
        return source[start:]
    return source[start:nxt]


def _guard_is_sell(name: str) -> bool:
    return name.startswith("pdp-404:") or name.startswith("s06-price:http") or ":https://" in name


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return ""


def _origin_main_sha(root: Path) -> str | None:
    try:
        completed = subprocess.run(
            ["git", "rev-parse", "origin/main"],
            cwd=root,
            check=False,
            capture_output=True,
            text=True,
        )
    except OSError:
        return None
    if completed.returncode != 0:
        return None
    sha = completed.stdout.strip()
    if _SHA_RE.fullmatch(sha) is None:
        return None
    return sha


def _live_codes(products: object, forms: object) -> list[str]:
    policy = load_held_policy()
    codes = set(policy.held)
    codes.update(policy.never_list)
    codes.add(S06)
    codes.add(Q02)
    if isinstance(products, list):
        for item in products:
            if isinstance(item, dict) and isinstance(item.get("ma"), str):
                codes.add(norm_ma(item["ma"]))
    if isinstance(forms, list):
        for item in forms:
            if isinstance(item, dict) and isinstance(item.get("ma"), str):
                codes.add(norm_ma(item["ma"]))
    return sorted(codes)


def _hub_live() -> tuple[list[MoneyRow] | None, SourceState, str | None]:
    rows, state = freshness_check._fetch_hub()
    raw_path = os.environ.get("SASSY_HUB_XLSX", "").strip()
    sha = _sha_file(Path(raw_path)) if raw_path else None
    if sha is None and state.state == "ok":
        tmp = Path(os.environ.get("TMPDIR", "/tmp")) / "sassy-hub-official.xlsx"
        sha = _sha_file(tmp)
    return rows, state, sha


def _sha_file(path: Path) -> str | None:
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError:
        return None


def _blob_block_from_http(result: HttpResult) -> dict[str, object]:
    if result.error or result.status != 200:
        return {"state": "skip", "detail": result.error or f"HTTP {result.status}", "products": []}
    try:
        payload = json.loads(result.body)
        catalog_products(payload)
    except (json.JSONDecodeError, ValueError) as exc:
        return {"state": "skip", "detail": str(exc), "products": []}
    products = payload.get("products") if isinstance(payload, dict) else []
    return {
        "state": "ok",
        "detail": f"{len(products) if isinstance(products, list) else 0} products",
        "updatedAt": payload.get("updatedAt") if isinstance(payload, dict) else None,
        "sha256": hashlib.sha256(result.body).hexdigest(),
        "etag": _strip_etag(result.headers.get("etag")),
        "lastModified": result.headers.get("last-modified"),
        "ageSeconds": _optional_int(result.headers.get("age")),
        "products": products if isinstance(products, list) else [],
    }


def _intake_block_from_http(result: HttpResult) -> dict[str, object]:
    if result.error or result.status != 200:
        return {"state": "skip", "detail": result.error or f"HTTP {result.status}", "submissions": []}
    try:
        payload = json.loads(result.body)
    except json.JSONDecodeError:
        return {"state": "skip", "detail": "intake JSON did not parse", "submissions": []}
    submissions = payload.get("submissions") if isinstance(payload, dict) else None
    if not isinstance(submissions, list):
        return {"state": "skip", "detail": "intake response has no submissions", "submissions": []}
    return {"state": "ok", "detail": f"{len(submissions)} forms", "submissions": submissions}


def _pdp_cell_from_http(result: HttpResult) -> dict[str, object]:
    if result.error:
        return {"status": None, "error": result.error}
    html = result.body.decode("utf-8", errors="replace")
    price = parse_pdp_price(html) if result.status == 200 else None
    return {"status": result.status, "price_usd": money_text(price)}


def _home_block(first: HttpResult, second: HttpResult | None) -> dict[str, object]:
    if first.error or first.status != 200:
        return {"sha256": None, "prices": None}
    html = first.body.decode("utf-8", errors="replace")
    block: dict[str, object] = {
        "sha256": hashlib.sha256(first.body).hexdigest(),
        "prices": {ma: money_text(price) for ma, price in parse_home_prices(html).items()},
    }
    if second is not None and not second.error and second.status == 200:
        block["refetchSha256"] = hashlib.sha256(second.body).hexdigest()
    return block


def _image_checks(products: list[object], origin: str) -> list[dict[str, object]]:
    checks: list[dict[str, object]] = []
    for item in products:
        if not isinstance(item, dict) or not isinstance(item.get("images"), list):
            continue
        for image in item["images"]:
            src = image.get("src") if isinstance(image, dict) else None
            if not isinstance(src, str) or not src.strip():
                continue
            url = src if src.startswith("http://") or src.startswith("https://") else origin.rstrip("/") + "/" + src.lstrip("/")
            result = http_get(url)
            ok = result.error is None and result.status in (200, 206)
            checks.append({"ok": ok, "status": result.status})
    return checks


def _refetch_sha(home: HomeView | None) -> str | None:
    if home is None:
        return None
    return home.refetch_sha256 or home.sha256


def _side(value: Decimal | None) -> str:
    text = money_text(value)
    return "missing" if text is None else text


def _json_number(value: Decimal | None) -> int | float | None:
    if value is None:
        return None
    if value == value.to_integral():
        return int(value)
    return float(value)


def _dollar(value: object) -> str:
    if value is None:
        return "missing"
    return f"${value}"


def _count_cell(value: object) -> str:
    if value is None:
        return "—"
    return str(value)


def _cell(value: str) -> str:
    return value.replace("|", "/")


def _mismatch_row(item: str, field_name: str, intake_index: dict[str, IntakeForm], *, intake_lag: bool) -> str:
    ma, left, right = _split_pair(item)
    form = intake_index.get(ma)
    stored = "—" if form is None or form.sell_usd in (None, "") else str(form.sell_usd)
    if intake_lag:
        blob, hub, intake, result = right, "—", left, f"LAG {left}→{right}"
    else:
        blob, hub, intake, result = left, right, stored, "MISMATCH"
    return " | ".join([_cell(ma), field_name, _cell(blob), _cell(hub), _cell(intake), result])


def _split_pair(item: str) -> tuple[str, str, str]:
    ma, rest = item.split(" ", 1)
    left, right = rest.split("→", 1)
    return ma, left, right


def _live_row(
    ma: str,
    live_prices: dict[str, Decimal | None],
    hub_prices: dict[str, Decimal | None] | None,
    intake_index: dict[str, IntakeForm],
) -> str:
    blob = money_text(live_prices.get(ma)) or "—"
    if hub_prices is None:
        hub = "—"
        hub_result = "HUB SKIP"
    elif ma not in hub_prices:
        hub = "missing"
        hub_result = "MISMATCH"
    else:
        hub = money_text(hub_prices[ma]) or "—"
        hub_result = "ALIGN" if hub_prices[ma] == live_prices.get(ma) else "MISMATCH"
    form = intake_index.get(ma)
    stored = None if form is None else parse_usd(form.sell_usd)
    if form is None or form.sell_usd in (None, ""):
        intake = "blank" if form is not None else "—"
        result = "BLANK stored; live agrees" if hub_result == "ALIGN" else hub_result
    elif stored == live_prices.get(ma):
        intake = money_text(stored) or "—"
        result = "ALIGN" if hub_result == "ALIGN" else hub_result
    else:
        intake = money_text(stored) or "—"
        result = f"LAG {money_text(stored)}→{money_text(live_prices.get(ma))}"
    return " | ".join([ma, blob, hub, intake, result])


def _held_row(
    ma: str,
    night: Night,
    hub_prices: dict[str, Decimal | None] | None,
    intake_index: dict[str, IntakeForm],
) -> str:
    on_blob = "present" if any(item.ma == ma for item in night.products) else "absent"
    if hub_prices is None:
        on_hub = "skip"
    else:
        on_hub = "present" if ma in hub_prices else "absent"
    bits = []
    for origin in (PRIMARY_ORIGIN, ALIAS_ORIGIN):
        view = night.pdp.get(ma, {}).get(origin)
        status = "not checked" if view is None or view.status is None else str(view.status)
        bits.append(status)
    pdp = bits[0] if len(set(bits)) == 1 else " / ".join(bits)
    form = intake_index.get(ma)
    intake = "no form" if form is None else "staged"
    if on_blob == "absent" and on_hub in {"absent", "skip"} and pdp == "404":
        result = "PASS unpublished" if ma != Q02 else "Observed 404. Not a never-list requirement."
    elif ma == Q02 and on_blob == "absent" and pdp == "404":
        result = "Observed 404. Not a never-list requirement."
    else:
        result = "CHECK"
    return " | ".join([ma, on_blob, on_hub, pdp, intake, result])


def _optional_str(value: object) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _optional_int(value: object) -> int | None:
    if value is None or isinstance(value, bool):
        return None
    try:
        return int(str(value).strip())
    except (TypeError, ValueError):
        return None


def _strip_etag(value: str | None) -> str | None:
    if value is None:
        return None
    text = value.strip()
    if len(text) >= 2 and text.startswith('"') and text.endswith('"'):
        return text[1:-1]
    return text or None


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Write a read-only midnight QC summary and data-ok report.")
    parser.add_argument("--date", default=datetime.now(timezone.utc).date().isoformat())
    parser.add_argument("--out", help="Directory for summary.json and data-ok.md.")
    parser.add_argument("--fixture", help="Night JSON. Skips the network.")
    parser.add_argument(
        "--check-images",
        action="store_true",
        help="On a live read, GET catalog image URLs. Fixture images are used as given.",
    )
    args = parser.parse_args(argv)
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", args.date) is None:
        print("date must be YYYY-MM-DD", file=sys.stderr)
        return 2
    out_dir = Path(args.out) if args.out else Path("out") / "midnight-qc" / args.date
    try:
        if args.fixture:
            payload = json.loads(Path(args.fixture).read_text(encoding="utf-8"))
            if isinstance(payload, dict):
                payload["day"] = args.date
            summary, markdown = summary_from_payload(payload)
        else:
            summary, markdown = summary_from_payload(fetch_night(args.date, check_images=args.check_images))
    except (OSError, ValueError, json.JSONDecodeError, RuntimeError) as error:
        print(str(error), file=sys.stderr)
        return 2
    summary_path, data_path = write_night(summary, markdown, out_dir)
    print(summary_path)
    print(data_path)
    return 0 if summary.get("overall") == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
