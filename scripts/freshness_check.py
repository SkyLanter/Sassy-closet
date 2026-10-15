"""Compare intake, Blob, hub Official, live PDPs, and public Taobao ¥.

Read-only. The only files this writes are out/dataset-freshness-YYYY-MM-DD.md
and the JSON sibling. Guard failures exit 1. A Taobao login wall is SKIP,
not FAIL. A public list ¥ on an e.tb.cn bridge page is the price= value on
the item URL. Promo and final ¥ are login-mode flags and do not replace
intake ¥. A SKU size table is parsed when the page has one. No Taobao
sign-in. Intake ¥ flags are reported and do not change the exit code.
Meta is fixture-only: logged out is NOTE, and login reads captions. No
Meta sign-in, create, delete, or edit. Pickup decisions do not publish.

PDP hosts are the primary sell host and the alias the shop already checks:
https://sassycloset.vercel.app and https://sassy-closet-shop.vercel.app.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import Decimal
from html import unescape
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
_KIT_ROOT = _ROOT / "excel-kit"
_SCRIPTS = Path(__file__).resolve().parent
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))
if str(_KIT_ROOT) not in sys.path:
    sys.path.insert(0, str(_KIT_ROOT))

from runtime_check import ensure_runtime

ensure_runtime(_ROOT / "out")

from openpyxl import load_workbook
from schema import header_row_for_sheet, read_headers, resolve_header_key

from held_policy import HeldPolicy, load_held_policy
from intake_flags import IntakeFlag, IntakeRow, PublicCny, flag_intake
from pickup import PickupDecision, PickupEvent, events_from_json, plan_pickups

PRIMARY_ORIGIN = "https://sassycloset.vercel.app"
ALIAS_ORIGIN = "https://sassy-closet-shop.vercel.app"
SELL_ORIGINS = (PRIMARY_ORIGIN, ALIAS_ORIGIN)
INTAKE_URL = "https://sassy-closet.vercel.app/api/submissions"
DEFAULT_BLOB_URL = (
    "https://efsi0jejsfy7j058.public.blob.vercel-storage.com/sassy-closet-shop/catalog.v1.json"
)
S06 = "S06"
S06_USD = Decimal("25")
USER_AGENT = "SassyClosetFreshness/1.0"


@dataclass(frozen=True)
class SourceState:
    state: str
    detail: str = ""

    def as_json(self) -> dict[str, str]:
        return {"state": self.state, "detail": self.detail}


@dataclass(frozen=True)
class MoneyRow:
    ma: str
    price_usd: Decimal | None


@dataclass(frozen=True)
class PdpView:
    status: int | None
    price_usd: Decimal | None = None
    error: str | None = None


@dataclass(frozen=True)
class TaobaoView:
    ma: str
    state: str
    public_cny: Decimal | None = None
    detail: str = ""
    promo_cny: Decimal | None = None
    final_cny: Decimal | None = None
    sizes: tuple[str, ...] | None = None
    photo_count: int | None = None


@dataclass(frozen=True)
class MetaPost:
    caption: str
    gia: str | None
    priced: bool
    held: bool

    def as_json(self) -> dict[str, object]:
        return {
            "caption": self.caption,
            "gia": self.gia,
            "priced": self.priced,
            "held": self.held,
        }


@dataclass
class Snapshot:
    day: str
    origins: tuple[str, ...]
    intake: list[IntakeRow]
    intake_state: SourceState
    blob_rows: list[MoneyRow] | None
    blob_state: SourceState
    hub_rows: list[MoneyRow] | None
    hub_state: SourceState
    pdp: dict[str, dict[str, PdpView]]
    taobao: list[TaobaoView] = field(default_factory=list)
    taobao_mode: str = "logged-out"
    meta_mode: str = "logged-out"
    meta_posts: tuple[MetaPost, ...] = ()
    pickup_events: list[PickupEvent] = field(default_factory=list)


@dataclass(frozen=True)
class Guard:
    name: str
    ok: bool
    detail: str

    def as_json(self) -> dict[str, str | bool]:
        return {"name": self.name, "ok": self.ok, "detail": self.detail}


@dataclass
class Report:
    day: str
    guards: list[Guard]
    flags: list[IntakeFlag]
    rows: list[dict[str, object]]
    sources: dict[str, SourceState]
    pickup: list[PickupDecision] = field(default_factory=list)
    meta_reads: list[MetaPost] = field(default_factory=list)

    @property
    def guards_pass(self) -> bool:
        return all(guard.ok for guard in self.guards)


def money_text(value: Decimal | None) -> str | None:
    if value is None:
        return None
    text = format(value, "f")
    if "." in text:
        text = text.rstrip("0").rstrip(".")
    return text


def parse_usd(value: object) -> Decimal | None:
    if value is None:
        return None
    if isinstance(value, bool):
        return None
    if isinstance(value, Decimal):
        return value
    if isinstance(value, (int, float)):
        if isinstance(value, float) and value != value:
            return None
        return Decimal(str(value))
    text = str(value).strip().replace("$", "").replace(",", "")
    if text == "" or re.fullmatch(r"\d+(?:\.\d+)?", text) is None:
        return None
    return Decimal(text)


def parse_blob_catalog(payload: object) -> list[MoneyRow]:
    if not isinstance(payload, dict) or not isinstance(payload.get("products"), list):
        raise ValueError("blob catalog has no products")
    rows: list[MoneyRow] = []
    for item in payload["products"]:
        if not isinstance(item, dict):
            continue
        raw_ma = item.get("ma")
        if not isinstance(raw_ma, str) or not raw_ma.strip():
            continue
        rows.append(MoneyRow(raw_ma.strip().upper(), parse_usd(item.get("priceUsd"))))
    return rows


def read_hub_official(path: Path) -> list[MoneyRow]:
    workbook = load_workbook(path, data_only=True)
    try:
        if "Official" not in workbook.sheetnames:
            raise ValueError("hub workbook has no Official sheet")
        sheet = workbook["Official"]
        header_row = header_row_for_sheet("Official")
        headers = read_headers(sheet, header_row)
        ma_idx = resolve_header_key(headers, "ma")
        price_idx = resolve_header_key(headers, "list_price")
        if ma_idx is None or price_idx is None:
            raise ValueError("Official sheet is missing ma or list_price")
        rows: list[MoneyRow] = []
        for cells in sheet.iter_rows(min_row=header_row + 1, values_only=True):
            if ma_idx >= len(cells) or cells[ma_idx] is None:
                continue
            ma = str(cells[ma_idx]).strip().upper()
            if ma == "":
                continue
            raw_price = cells[price_idx] if price_idx < len(cells) else None
            rows.append(MoneyRow(ma, parse_usd(raw_price)))
        return rows
    finally:
        workbook.close()


def parse_pdp_price(html: str) -> Decimal | None:
    for block in re.findall(
        r'<script[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
        html,
        flags=re.IGNORECASE | re.DOTALL,
    ):
        try:
            payload = json.loads(block)
        except json.JSONDecodeError:
            continue
        found = _find_offer_price(payload)
        if found is not None:
            return found
    return None


def _find_offer_price(payload: object) -> Decimal | None:
    if isinstance(payload, list):
        for item in payload:
            found = _find_offer_price(item)
            if found is not None:
                return found
        return None
    if not isinstance(payload, dict):
        return None
    offers = payload.get("offers")
    if isinstance(offers, dict) and "price" in offers:
        return parse_usd(offers.get("price"))
    if isinstance(offers, list):
        for offer in offers:
            if isinstance(offer, dict) and "price" in offer:
                return parse_usd(offer.get("price"))
    for value in payload.values():
        if isinstance(value, (dict, list)):
            found = _find_offer_price(value)
            if found is not None:
                return found
    return None


def taobao_blocked(html: str) -> bool:
    if not html or len(html) < 2000:
        return True
    if "访问受限" in html or "访问被拒绝" in html or "安全验证" in html:
        return True
    if "S11" in html and "tfs" in html:
        return True
    if re.search(
        r"""window\.location\.href\s*=\s*["']https?://(login|passport)\.taobao\.com""",
        html,
        flags=re.IGNORECASE,
    ):
        return True
    return False


_ITEM_URL_RE = re.compile(
    r"""https?://(?:"""
    r"""(?:item\.taobao\.com|detail\.tmall\.com)/item\.htm"""
    r"""|h5\.m\.taobao\.com/awp/core/detail\.htm"""
    r""")\?([^'"\s<>]+)""",
    flags=re.IGNORECASE,
)
_QUERY_PRICE_RE = re.compile(r"(?:^|&)price=(\d+(?:\.\d{1,2})?)(?!\d)")


def _price_from_item_url(html: str) -> Decimal | None:
    """List ¥ from price= on an item URL embedded in an e.tb.cn bridge page."""
    for match in _ITEM_URL_RE.finditer(html):
        query = match.group(1).replace("\\u0026", "&").replace("&amp;", "&")
        found = _QUERY_PRICE_RE.search(query)
        if found:
            return Decimal(found.group(1))
    return None


def parse_taobao_cny(html: str) -> Decimal | None:
    for pattern in (
        r'"defaultItemPrice"\s*:\s*"(\d+(?:\.\d{1,2})?)"',
        r'"priceText"\s*:\s*"(\d+(?:\.\d{1,2})?)"',
        r'"reservePrice"\s*:\s*"(\d+(?:\.\d{1,2})?)"',
        r'"price"\s*:\s*"(\d+(?:\.\d{1,2})?)"',
    ):
        match = re.search(pattern, html)
        if match:
            return Decimal(match.group(1))
    return _price_from_item_url(html)


def parse_taobao_promo(html: str) -> Decimal | None:
    return _first_decimal(
        html,
        (
            r'"promoPrice"\s*:\s*"(\d+(?:\.\d{1,2})?)"',
            r'"promotionPrice"\s*:\s*"(\d+(?:\.\d{1,2})?)"',
            r'"salePrice"\s*:\s*"(\d+(?:\.\d{1,2})?)"',
        ),
    )


def parse_taobao_final(html: str) -> Decimal | None:
    return _first_decimal(html, (r'"finalPrice"\s*:\s*"(\d+(?:\.\d{1,2})?)"',))


_SIZE_AXIS_RE = re.compile(r"尺码|尺寸|sizes?", re.IGNORECASE)
_SKU_PROP_RE = re.compile(
    r'\{[^{}]*"pid"\s*:\s*"\d+"[^{}]*"name"\s*:\s*"((?:[^"\\]|\\.)*)"[^{}]*"values"\s*:\s*\[([^\]]*)\]'
)
_SKU_VALUE_RE = re.compile(r'"name"\s*:\s*"((?:[^"\\]|\\.)*)"')
_SCRIPT_RE = re.compile(r"<script\b[^>]*>.*?</script>", re.IGNORECASE | re.DOTALL)
_TABLE_RE = re.compile(r"<table\b[^>]*>(.*?)</table>", re.IGNORECASE | re.DOTALL)
_ROW_RE = re.compile(r"<tr\b[^>]*>(.*?)</tr>", re.IGNORECASE | re.DOTALL)
_CELL_RE = re.compile(r"<t[hd]\b[^>]*>(.*?)</t[hd]>", re.IGNORECASE | re.DOTALL)
_TAG_RE = re.compile(r"<[^>]+>")
_CM_RE = re.compile(r"^\d+(?:\.\d+)?$")
_MEASUREMENT_LABELS = frozenset({"胸围", "衣长", "腰围", "肩宽", "臀围", "袖长", "裤长", "身高", "体重", "裙长"})


def parse_taobao_sizes(html: str) -> tuple[str, ...] | None:
    """Seller size labels from a SKU prop or a size table. None when absent."""
    sku_sizes = _sizes_from_sku_props(html)
    if sku_sizes:
        return sku_sizes
    return _sizes_from_tables(html)


def _unescape_sku(value: str) -> str:
    return unescape(value.replace("\\/", "/").replace('\\"', '"')).strip()


def _sizes_from_sku_props(html: str) -> tuple[str, ...] | None:
    labels: list[str] = []
    for match in _SKU_PROP_RE.finditer(html):
        name = _unescape_sku(match.group(1))
        if _SIZE_AXIS_RE.fullmatch(name) is None:
            continue
        for value_match in _SKU_VALUE_RE.finditer(match.group(2)):
            label = _unescape_sku(value_match.group(1))
            if label and label not in labels:
                labels.append(label)
    if not labels:
        return None
    return tuple(labels)


def _sizes_from_tables(html: str) -> tuple[str, ...] | None:
    body = _SCRIPT_RE.sub(" ", html)
    for table_match in _TABLE_RE.finditer(body):
        found = _sizes_from_rows(_table_rows(table_match.group(1)))
        if found:
            return found
    return None


def _table_rows(table_html: str) -> list[list[str]]:
    rows: list[list[str]] = []
    for row_match in _ROW_RE.finditer(table_html):
        cells = [_cell_plain(cell) for cell in _CELL_RE.findall(row_match.group(1))]
        if any(cell != "" for cell in cells):
            rows.append(cells)
    return rows


def _cell_plain(raw: str) -> str:
    return re.sub(r"\s+", " ", unescape(_TAG_RE.sub(" ", raw))).strip()


def _is_size_label(text: str) -> bool:
    if text == "" or len(text) > 16:
        return False
    if _CM_RE.fullmatch(text) or _SIZE_AXIS_RE.fullmatch(text):
        return False
    if text in _MEASUREMENT_LABELS:
        return False
    return True


def _unique_labels(labels: list[str]) -> tuple[str, ...]:
    seen: list[str] = []
    for label in labels:
        if label not in seen:
            seen.append(label)
    return tuple(seen)


def _sizes_from_rows(rows: list[list[str]]) -> tuple[str, ...] | None:
    for row in rows:
        if not row or _SIZE_AXIS_RE.fullmatch(row[0]) is None:
            continue
        rest = [cell for cell in row[1:] if cell != ""]
        if rest and all(_is_size_label(cell) for cell in rest):
            return _unique_labels(rest)
    if not rows:
        return None
    header = rows[0]
    for index, cell in enumerate(header):
        if _SIZE_AXIS_RE.fullmatch(cell) is None:
            continue
        labels: list[str] = []
        aligned = True
        for row in rows[1:]:
            if index >= len(row) or not _is_size_label(row[index]):
                aligned = False
                break
            labels.append(row[index])
        if aligned and labels:
            return _unique_labels(labels)
    return None


def _first_decimal(html: str, patterns: tuple[str, ...]) -> Decimal | None:
    for pattern in patterns:
        match = re.search(pattern, html)
        if match:
            return Decimal(match.group(1))
    return None


_GIA_RE = re.compile(r"Giá\s*:?\s*([^\n]+)", re.IGNORECASE)
_GIA_PRICE_RE = re.compile(r"^\$?\s*\d+(?:\.\d+)?$")
TAOBAO_MODES = ("logged-out", "login")
META_MODES = ("logged-out", "login")


def read_meta_caption(caption: str, held: bool) -> MetaPost:
    match = _GIA_RE.search(caption)
    gia = match.group(1).strip() if match else None
    priced = bool(gia and _GIA_PRICE_RE.match(gia.replace(" ", "")))
    return MetaPost(caption=caption, gia=gia, priced=priced, held=held)


def meta_source(mode: str, posts: tuple[MetaPost, ...]) -> tuple[SourceState, tuple[MetaPost, ...]]:
    if mode == "logged-out":
        return SourceState("note", "NOTE logged out; captions not read"), ()
    if mode == "login":
        if not posts:
            return SourceState("note", "NOTE login mode is fixture-only; not signing in"), ()
        return SourceState("ok", f"NOTE {len(posts)} fixture posts; no sign-in"), posts
    raise ValueError("meta mode must be logged-out or login")


def _mode_value(value: object, fallback: str, allowed: tuple[str, ...]) -> str:
    if value is None:
        return fallback
    chosen = str(value).strip() or fallback
    if chosen not in allowed:
        raise ValueError(f"mode must be {' or '.join(allowed)}")
    return chosen


def _meta_posts_from_json(value: object) -> tuple[MetaPost, ...]:
    if value is None:
        return ()
    if not isinstance(value, list):
        raise ValueError("fixture metaPosts must be a list")
    posts: list[MetaPost] = []
    for item in value:
        if not isinstance(item, dict) or not isinstance(item.get("caption"), str):
            raise ValueError("fixture meta post needs a caption")
        posts.append(read_meta_caption(item["caption"], bool(item.get("held", False))))
    return tuple(posts)


def resolve_mode(cli: str | None, env_name: str, fallback: str, allowed: tuple[str, ...]) -> str:
    chosen = cli if cli else os.environ.get(env_name, "").strip() or fallback
    if chosen not in allowed:
        raise ValueError(f"{env_name} must be {' or '.join(allowed)}")
    return chosen


def classify_taobao(status: int, html: str) -> TaobaoView:
    if status != 200 or taobao_blocked(html):
        return TaobaoView("", "skip", None, "login-walled or unreachable")
    price = parse_taobao_cny(html)
    promo = parse_taobao_promo(html)
    final = parse_taobao_final(html)
    sizes = parse_taobao_sizes(html)
    if price is None:
        return TaobaoView("", "skip", None, "no public ¥ on the page", promo, final, sizes)
    return TaobaoView("", "ok", price, "", promo, final, sizes)


def _index(rows: list[MoneyRow] | None) -> dict[str, Decimal | None]:
    if rows is None:
        return {}
    return {row.ma: row.price_usd for row in rows}


def _guard_codes(policy: HeldPolicy) -> list[str]:
    return list(policy.held) + [code for code in policy.never_list if code not in policy.held]


def evaluate(snapshot: Snapshot, policy: HeldPolicy | None = None) -> Report:
    rules = policy or load_held_policy()
    guards: list[Guard] = []
    if not snapshot.origins:
        guards.append(Guard("pdp-hosts", False, "no PDP hosts configured"))
    blob = _index(snapshot.blob_rows)
    hub = _index(snapshot.hub_rows)
    for code in _guard_codes(rules):
        for origin in snapshot.origins:
            view = snapshot.pdp.get(code, {}).get(origin)
            if view is None or view.status is None:
                detail = "PDP was not checked" if view is None else (view.error or "PDP unreachable")
                guards.append(Guard(f"pdp-404:{code}:{origin}", False, detail))
            elif view.status != 404:
                guards.append(Guard(f"pdp-404:{code}:{origin}", False, f"HTTP {view.status}"))
            else:
                guards.append(Guard(f"pdp-404:{code}:{origin}", True, "404"))
        if snapshot.blob_rows is not None:
            present = code in blob
            guards.append(
                Guard(
                    f"off-catalog:{code}:blob",
                    not present,
                    "present on Blob" if present else "absent",
                )
            )
        if snapshot.hub_rows is not None:
            present = code in hub
            guards.append(
                Guard(
                    f"off-catalog:{code}:hub",
                    not present,
                    "present on hub Official" if present else "absent",
                )
            )
    _guard_s06(snapshot, guards)
    _guard_duplicate_rows(snapshot.blob_rows, "blob", guards)
    _guard_duplicate_rows(snapshot.hub_rows, "hub", guards)
    public = {
        item.ma: PublicCny(item.state, item.public_cny, item.detail) for item in snapshot.taobao
    }
    flags = flag_intake(snapshot.intake, public)
    decisions = plan_pickups(
        [*snapshot.pickup_events, *intake_pickup_events(snapshot)],
        rules,
    )
    flags.extend(_pickup_flags(decisions))
    flags.extend(_login_price_flags(snapshot))
    _guard_pickup(decisions, snapshot, guards)
    meta_state, meta_reads = meta_source(snapshot.meta_mode, snapshot.meta_posts)
    return Report(
        day=snapshot.day,
        guards=guards,
        flags=flags,
        rows=_comparison_rows(snapshot, public),
        sources={
            "intake": snapshot.intake_state,
            "blob": snapshot.blob_state,
            "hub": snapshot.hub_state,
            "meta": meta_state,
        },
        pickup=decisions,
        meta_reads=list(meta_reads),
    )


def _guard_duplicate_rows(rows: list[MoneyRow] | None, source: str, guards: list[Guard]) -> None:
    if rows is None:
        return
    counts: dict[str, int] = {}
    s06_prices: list[Decimal | None] = []
    for row in rows:
        counts[row.ma] = counts.get(row.ma, 0) + 1
        if row.ma == S06:
            s06_prices.append(row.price_usd)
    for ma, count in counts.items():
        if count > 1:
            guards.append(Guard(f"duplicate:{source}:{ma}", False, f"{count} rows"))
    other = [price for price in s06_prices if price != S06_USD]
    if len(s06_prices) > 1 and other:
        guards.append(Guard(f"s06-second-dollar:{source}", False, "second S06 row at another dollar"))


def intake_pickup_events(snapshot: Snapshot) -> list[PickupEvent]:
    """New intake rows the fixture did not already put in pickup. No writes."""
    explicit = {event.ma.strip().upper() for event in snapshot.pickup_events}
    taobao = {item.ma: item for item in snapshot.taobao}
    events: list[PickupEvent] = []
    for row in snapshot.intake:
        code = row.ma.strip().upper()
        if code in explicit:
            continue
        sell = "" if row.sell_usd is None else row.sell_usd.strip()
        if sell:
            continue
        view = taobao.get(code)
        if not _candidate_shape(row, view):
            continue
        sizes = _joined_sizes(row, view)
        events.append(
            PickupEvent(
                ma=code,
                via="intake",
                action="create",
                cost_cny="" if row.cost_cny is None else row.cost_cny,
                landed_usd=None,
                sell_usd=row.sell_usd,
                sizes=sizes,
                photo_count=_joined_photos(row, view),
                public_cny=None if view is None else view.public_cny,
                taobao_state="ok" if view is None else view.state,
                boss_approved=False,
                already_listed=False,
                listed_sell_usd=None,
                reused=False,
                taobao_detail="" if view is None else view.detail,
            )
        )
    return events


def _candidate_shape(row: IntakeRow, view: TaobaoView | None) -> bool:
    if row.sizes is not None or row.photo_count is not None:
        return True
    if view is None:
        return False
    return view.sizes is not None or view.photo_count is not None


def _joined_sizes(row: IntakeRow, view: TaobaoView | None) -> tuple[str, ...]:
    if view is not None and view.sizes is not None:
        return view.sizes
    if row.sizes is not None:
        return row.sizes
    return ()


def _joined_photos(row: IntakeRow, view: TaobaoView | None) -> int | None:
    if view is not None and view.photo_count is not None:
        return view.photo_count
    return row.photo_count


def _guard_pickup(decisions: list[PickupDecision], snapshot: Snapshot, guards: list[Guard]) -> None:
    present = {row.ma for row in snapshot.blob_rows} if snapshot.blob_rows is not None else set()
    hub = {row.ma for row in snapshot.hub_rows} if snapshot.hub_rows is not None else set()
    for decision in decisions:
        if decision.blocks_live and decision.ma in present:
            guards.append(Guard(f"off-live:{decision.ma}", False, "on Blob without a Boss yes"))
        if decision.blocks_live and decision.ma in hub:
            guards.append(Guard(f"off-live:{decision.ma}:hub", False, "on hub without a Boss yes"))
        if decision.blocks_live:
            for origin, view in snapshot.pdp.get(decision.ma, {}).items():
                if view.status is not None and view.status != 404:
                    guards.append(
                        Guard(f"off-live:{decision.ma}:{origin}", False, f"HTTP {view.status}")
                    )
        if any(
            flag in {"duplicate", "reused", "never_list", "s06_lock", "no_reprice", "held"}
            for flag in decision.flags
        ):
            guards.append(Guard(f"publish-block:{decision.ma}:{decision.flags[0]}", False, decision.detail))


def _pickup_flags(decisions: list[PickupDecision]) -> list[IntakeFlag]:
    flags: list[IntakeFlag] = []
    for decision in decisions:
        for flag in decision.flags:
            flags.append(IntakeFlag(decision.ma, flag, decision.stored_cny))
    return flags


def _login_price_flags(snapshot: Snapshot) -> list[IntakeFlag]:
    if snapshot.taobao_mode != "login":
        return []
    intake = {row.ma.strip().upper(): row for row in snapshot.intake}
    flags: list[IntakeFlag] = []
    for item in snapshot.taobao:
        row = intake.get(item.ma)
        stored = "" if row is None or row.cost_cny is None else row.cost_cny
        if item.promo_cny is not None:
            flags.append(IntakeFlag(item.ma, "promo_cny", stored, money_text(item.promo_cny)))
        if item.final_cny is not None:
            flags.append(IntakeFlag(item.ma, "final_cny", stored, money_text(item.final_cny)))
    return flags


def _guard_s06(snapshot: Snapshot, guards: list[Guard]) -> None:
    if snapshot.blob_rows is not None:
        price = _index(snapshot.blob_rows).get(S06)
        guards.append(_s06_guard("blob", price))
    if snapshot.hub_rows is not None:
        price = _index(snapshot.hub_rows).get(S06)
        guards.append(_s06_guard("hub", price))
    for origin in snapshot.origins:
        view = snapshot.pdp.get(S06, {}).get(origin)
        if view is None or view.status is None:
            detail = "PDP was not checked" if view is None else (view.error or "PDP unreachable")
            guards.append(Guard(f"s06-price:{origin}", False, detail))
        elif view.status != 200:
            guards.append(Guard(f"s06-price:{origin}", False, f"HTTP {view.status}"))
        else:
            guards.append(_s06_guard(origin, view.price_usd))


def _s06_guard(source: str, price: Decimal | None) -> Guard:
    if price is None:
        return Guard(f"s06-price:{source}", False, "no USD price")
    if price != S06_USD:
        return Guard(f"s06-price:{source}", False, f"USD {money_text(price)}")
    return Guard(f"s06-price:{source}", True, "25")


def _comparison_rows(snapshot: Snapshot, public: dict[str, PublicCny]) -> list[dict[str, object]]:
    blob = _index(snapshot.blob_rows) if snapshot.blob_rows is not None else None
    hub = _index(snapshot.hub_rows) if snapshot.hub_rows is not None else None
    intake = {row.ma.strip().upper(): row for row in snapshot.intake}
    taobao = {item.ma: item for item in snapshot.taobao}
    codes = sorted(set(intake) | set(blob or {}) | set(hub or {}) | set(snapshot.pdp) | set(taobao))
    rows: list[dict[str, object]] = []
    for code in codes:
        form = intake.get(code)
        pdp_prices = {
            origin: _pdp_cell(snapshot.pdp.get(code, {}).get(origin)) for origin in snapshot.origins
        }
        listed = taobao.get(code)
        note = _price_note(blob.get(code) if blob else None, hub.get(code) if hub else None, blob, hub)
        rows.append(
            {
                "ma": code,
                "intakeCny": None if form is None else form.cost_cny,
                "intakeSellUsd": None if form is None else form.sell_usd,
                "blobUsd": None if blob is None or code not in blob else money_text(blob[code]),
                "hubUsd": None if hub is None or code not in hub else money_text(hub[code]),
                "pdp": pdp_prices,
                "publicCny": None
                if listed is None or listed.public_cny is None
                else money_text(listed.public_cny),
                "publicState": None if listed is None else listed.state,
                "publicDetail": "" if listed is None else listed.detail,
                "note": note,
            }
        )
    return rows


def _pdp_cell(view: PdpView | None) -> dict[str, object]:
    if view is None:
        return {"status": None, "priceUsd": None, "error": "not checked"}
    return {
        "status": view.status,
        "priceUsd": money_text(view.price_usd),
        "error": view.error,
    }


def _price_note(
    blob_price: Decimal | None,
    hub_price: Decimal | None,
    blob: dict[str, Decimal | None] | None,
    hub: dict[str, Decimal | None] | None,
) -> str:
    if blob is None or hub is None:
        return ""
    if blob_price is None or hub_price is None:
        return ""
    if blob_price != hub_price:
        return "blob and hub USD differ"
    return ""


def render_markdown(report: Report) -> str:
    lines = [
        f"# Dataset freshness {report.day}",
        "",
        "Read-only comparison. Stored intake ¥ is copied here and is not corrected.",
        "",
        f"Guards: {'PASS' if report.guards_pass else 'FAIL'}",
        "",
    ]
    for guard in report.guards:
        mark = "PASS" if guard.ok else "FAIL"
        lines.append(f"- {mark} `{guard.name}` — {guard.detail}")
    lines.extend(["", "## Sources", ""])
    for name, source in report.sources.items():
        detail = f" — {source.detail}" if source.detail else ""
        lines.append(f"- {name}: {source.state}{detail}")
    lines.extend(["", "## Pickup", ""])
    if not report.pickup:
        lines.append("None.")
    else:
        for decision in report.pickup:
            quoted = "—" if decision.quoted_usd is None else str(decision.quoted_usd)
            lines.append(
                f"- {decision.ma} held={decision.held} live={decision.live} "
                f"publish={decision.publish} quote={quoted} flags={','.join(decision.flags) or '—'}"
            )
    lines.extend(["", "## Meta", ""])
    meta = report.sources.get("meta")
    if meta is None:
        lines.append("None.")
    else:
        lines.append(f"- {meta.state} — {meta.detail}")
    for post in report.meta_reads:
        lines.append(f"- held={post.held} priced={post.priced} Giá {post.gia}")
    lines.extend(["", "## Intake ¥ flags", ""])
    if not report.flags:
        lines.append("None.")
    else:
        for flag in report.flags:
            public = f" public ¥ {flag.public_cny}" if flag.public_cny else ""
            lines.append(f"- {flag.ma} {flag.kind}: stored `{flag.stored}`{public}")
    lines.extend(
        [
            "",
            "## Comparison",
            "",
            "mã | intake ¥ | blob | hub | public ¥ | note",
            "--- | --- | --- | --- | --- | ---",
        ]
    )
    for row in report.rows:
        lines.append(
            " | ".join(
                [
                    str(row["ma"]),
                    _cell(row["intakeCny"]),
                    _cell(row["blobUsd"]),
                    _cell(row["hubUsd"]),
                    _public_cell(row),
                    _cell(row["note"]),
                ]
            )
        )
    lines.extend(["", "## PDP", ""])
    for row in report.rows:
        pdp = row["pdp"]
        if not isinstance(pdp, dict):
            continue
        bits = []
        for origin, cell in pdp.items():
            if isinstance(cell, dict):
                bits.append(f"{origin} HTTP {cell.get('status')} price {cell.get('priceUsd')}")
        if bits:
            lines.append(f"- {row['ma']}: " + "; ".join(bits))
    lines.append("")
    return "\n".join(lines)


def _cell(value: object) -> str:
    if value is None or value == "":
        return "—"
    return str(value).replace("|", "/")


def _public_cell(row: dict[str, object]) -> str:
    state = row.get("publicState")
    if state == "skip":
        detail = row.get("publicDetail") or "skip"
        return f"SKIP ({detail})"
    if state == "ok":
        return _cell(row.get("publicCny"))
    return "—"


def report_json(report: Report) -> dict[str, object]:
    return {
        "day": report.day,
        "guardsPass": report.guards_pass,
        "guards": [guard.as_json() for guard in report.guards],
        "flags": [flag.as_json() for flag in report.flags],
        "sources": {name: source.as_json() for name, source in report.sources.items()},
        "rows": report.rows,
        "pickup": [decision.as_json() for decision in report.pickup],
        "meta": [post.as_json() for post in report.meta_reads],
    }


def write_report(report: Report, out_dir: Path) -> tuple[Path, Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    markdown_path = out_dir / f"dataset-freshness-{report.day}.md"
    json_path = out_dir / f"dataset-freshness-{report.day}.json"
    markdown_path.write_text(render_markdown(report), encoding="utf-8")
    json_path.write_text(json.dumps(report_json(report), indent=2) + "\n", encoding="utf-8")
    return markdown_path, json_path


def snapshot_from_json(payload: object) -> Snapshot:
    if not isinstance(payload, dict):
        raise ValueError("fixture must be a JSON object")
    day = payload.get("day")
    if not isinstance(day, str) or re.fullmatch(r"\d{4}-\d{2}-\d{2}", day) is None:
        raise ValueError("fixture day must be YYYY-MM-DD")
    origins_raw = payload.get("origins", list(SELL_ORIGINS))
    if not isinstance(origins_raw, list) or not all(isinstance(item, str) for item in origins_raw):
        raise ValueError("fixture origins must be a list of hosts")
    return Snapshot(
        day=day,
        origins=tuple(origins_raw),
        intake=_intake_from_json(payload.get("intake", [])),
        intake_state=_state_from_json(payload.get("intakeState"), "ok"),
        blob_rows=_money_from_json(payload.get("blob")),
        blob_state=_source_block_state(payload.get("blob"), "blob"),
        hub_rows=_money_from_json(payload.get("hub")),
        hub_state=_source_block_state(payload.get("hub"), "hub"),
        pdp=_pdp_from_json(payload.get("pdp", {})),
        taobao=_taobao_from_json(payload.get("taobao", [])),
        taobao_mode=_mode_value(payload.get("taobaoMode"), "logged-out", TAOBAO_MODES),
        meta_mode=_mode_value(payload.get("metaMode"), "logged-out", META_MODES),
        meta_posts=_meta_posts_from_json(payload.get("metaPosts", [])),
        pickup_events=events_from_json(payload.get("pickup", [])),
    )


def _state_from_json(value: object, default: str) -> SourceState:
    if not isinstance(value, dict):
        return SourceState(default)
    state = value.get("state", default)
    detail = value.get("detail", "")
    return SourceState(str(state), "" if detail is None else str(detail))


def _source_block_state(value: object, label: str) -> SourceState:
    if not isinstance(value, dict):
        raise ValueError(f"fixture {label} must be an object")
    state = value.get("state", "ok")
    detail = value.get("detail", "")
    return SourceState(str(state), "" if detail is None else str(detail))


def _sizes_field(item: dict[str, object]) -> tuple[str, ...] | None:
    if "sizes" in item:
        raw = item.get("sizes")
        if raw is None:
            return ()
        if isinstance(raw, str):
            return tuple(part for part in re.split(r"[\s,]+", raw) if part.strip())
        if isinstance(raw, list):
            parts: list[str] = []
            for part in raw:
                if not isinstance(part, str):
                    raise ValueError("fixture sizes must be a list of strings")
                text = part.strip()
                if text:
                    parts.append(text)
            return tuple(parts)
        raise ValueError("fixture sizes must be a list of strings")
    if "size" in item and isinstance(item.get("size"), str):
        return tuple(part for part in re.split(r"[\s,]+", str(item.get("size"))) if part.strip())
    return None


def _photo_field(item: dict[str, object]) -> int | None:
    if "photo_count" in item and item.get("photo_count") is not None:
        return int(str(item.get("photo_count")))
    for key in ("gallery", "photos", "images", "gallery_urls"):
        raw = item.get(key)
        if isinstance(raw, list):
            return sum(1 for part in raw if str(part).strip())
    return None


def _intake_from_json(value: object) -> list[IntakeRow]:
    if not isinstance(value, list):
        raise ValueError("fixture intake must be a list")
    rows: list[IntakeRow] = []
    for item in value:
        if not isinstance(item, dict) or not isinstance(item.get("ma"), str):
            raise ValueError("fixture intake row needs a mã")
        cost = item.get("cost_cny")
        sell = item.get("sell_usd")
        link = item.get("link")
        rows.append(
            IntakeRow(
                item["ma"],
                None if cost is None else str(cost),
                None if sell is None else str(sell),
                None if link is None else str(link),
                _sizes_field(item),
                _photo_field(item),
            )
        )
    return rows


def _money_from_json(value: object) -> list[MoneyRow] | None:
    if not isinstance(value, dict):
        raise ValueError("fixture catalog block must be an object")
    if value.get("state") == "skip":
        return None
    raw_rows = value.get("rows", [])
    if not isinstance(raw_rows, list):
        raise ValueError("fixture catalog rows must be a list")
    rows: list[MoneyRow] = []
    for item in raw_rows:
        if not isinstance(item, dict) or not isinstance(item.get("ma"), str):
            raise ValueError("fixture catalog row needs a mã")
        rows.append(MoneyRow(item["ma"].strip().upper(), parse_usd(item.get("price_usd"))))
    return rows


def _pdp_from_json(value: object) -> dict[str, dict[str, PdpView]]:
    if not isinstance(value, dict):
        raise ValueError("fixture pdp must be an object")
    parsed: dict[str, dict[str, PdpView]] = {}
    for ma, hosts in value.items():
        if not isinstance(ma, str) or not isinstance(hosts, dict):
            raise ValueError("fixture pdp entries must be mã -> host")
        parsed[ma.strip().upper()] = {}
        for origin, cell in hosts.items():
            if not isinstance(origin, str) or not isinstance(cell, dict):
                raise ValueError("fixture pdp host cell is invalid")
            status = cell.get("status")
            parsed[ma.strip().upper()][origin] = PdpView(
                None if status is None else int(status),
                parse_usd(cell.get("price_usd")),
                None if cell.get("error") is None else str(cell.get("error")),
            )
    return parsed


def _taobao_from_json(value: object) -> list[TaobaoView]:
    if not isinstance(value, list):
        raise ValueError("fixture taobao must be a list")
    rows: list[TaobaoView] = []
    for item in value:
        if not isinstance(item, dict) or not isinstance(item.get("ma"), str):
            raise ValueError("fixture taobao row needs a mã")
        state = str(item.get("state", "skip"))
        raw = item.get("public_cny")
        promo = item.get("promo_cny")
        final = item.get("final_cny")
        rows.append(
            TaobaoView(
                item["ma"].strip().upper(),
                state,
                None if raw is None else Decimal(str(raw)),
                "" if item.get("detail") is None else str(item.get("detail")),
                None if promo is None else Decimal(str(promo)),
                None if final is None else Decimal(str(final)),
                _sizes_field(item),
                _photo_field(item),
            )
        )
    return rows


def fetch_live(day: str) -> Snapshot:
    """GET intake, Blob, hub (when configured), PDPs, and public Taobao pages."""
    intake_rows, intake_state = _fetch_intake()
    blob_rows, blob_state = _fetch_blob()
    hub_rows, hub_state = _fetch_hub()
    codes = _live_codes(intake_rows, blob_rows, hub_rows)
    pdp = {code: {} for code in codes}
    for origin in SELL_ORIGINS:
        for code in codes:
            pdp[code][origin] = _fetch_pdp(origin, code)
    taobao = [_fetch_taobao(row) for row in intake_rows]
    return Snapshot(
        day=day,
        origins=SELL_ORIGINS,
        intake=intake_rows,
        intake_state=intake_state,
        blob_rows=blob_rows,
        blob_state=blob_state,
        hub_rows=hub_rows,
        hub_state=hub_state,
        pdp=pdp,
        taobao=taobao,
        taobao_mode="logged-out",
        meta_mode="logged-out",
    )


def _live_codes(
    intake_rows: list[IntakeRow],
    blob_rows: list[MoneyRow] | None,
    hub_rows: list[MoneyRow] | None,
) -> list[str]:
    policy = load_held_policy()
    codes = {row.ma.strip().upper() for row in intake_rows}
    codes.update(row.ma for row in blob_rows or [])
    codes.update(row.ma for row in hub_rows or [])
    codes.update(policy.held)
    codes.update(policy.never_list)
    codes.add(S06)
    return sorted(codes)


def _fetch_intake() -> tuple[list[IntakeRow], SourceState]:
    status, body, error = _http_get(INTAKE_URL)
    if error or status != 200:
        return [], SourceState("skip", error or f"HTTP {status}")
    try:
        payload = json.loads(body)
    except json.JSONDecodeError:
        return [], SourceState("skip", "intake JSON did not parse")
    submissions = payload.get("submissions") if isinstance(payload, dict) else None
    if not isinstance(submissions, list):
        return [], SourceState("skip", "intake response has no submissions")
    rows: list[IntakeRow] = []
    for item in submissions:
        if not isinstance(item, dict) or not isinstance(item.get("ma"), str):
            continue
        rows.append(
            IntakeRow(
                item["ma"],
                None if item.get("cost_cny") is None else str(item.get("cost_cny")),
                None if item.get("sell_usd") is None else str(item.get("sell_usd")),
                None if item.get("link") is None else str(item.get("link")),
            )
        )
    return rows, SourceState("ok", f"{len(rows)} forms")


def _fetch_blob() -> tuple[list[MoneyRow] | None, SourceState]:
    url = os.environ.get("SASSY_BLOB_CATALOG_URL", DEFAULT_BLOB_URL).strip()
    status, body, error = _http_get(url)
    if error or status != 200:
        return None, SourceState("skip", error or f"HTTP {status}")
    try:
        rows = parse_blob_catalog(json.loads(body))
    except (json.JSONDecodeError, ValueError) as exc:
        return None, SourceState("skip", str(exc))
    return rows, SourceState("ok", f"{len(rows)} products")


def _fetch_hub() -> tuple[list[MoneyRow] | None, SourceState]:
    raw_path = os.environ.get("SASSY_HUB_XLSX", "").strip()
    raw_url = os.environ.get("SASSY_HUB_URL", "").strip()
    if raw_path:
        return _hub_from_path(Path(raw_path))
    if not raw_url:
        return None, SourceState("skip", "no SASSY_HUB_XLSX or SASSY_HUB_URL")
    status, raw, error = _http_get_bytes(raw_url)
    if error or status != 200 or raw is None:
        return None, SourceState("skip", error or f"HTTP {status}")
    tmp = Path(os.environ.get("TMPDIR", "/tmp")) / "sassy-hub-official.xlsx"
    tmp.write_bytes(raw)
    return _hub_from_path(tmp)


def _hub_from_path(path: Path) -> tuple[list[MoneyRow] | None, SourceState]:
    try:
        rows = read_hub_official(path)
    except (OSError, ValueError) as exc:
        return None, SourceState("skip", str(exc))
    return rows, SourceState("ok", f"{len(rows)} Official rows")


def _fetch_pdp(origin: str, ma: str) -> PdpView:
    status, body, error = _http_get(f"{origin}/m/{ma}")
    if error:
        return PdpView(None, None, error)
    price = parse_pdp_price(body) if status == 200 else None
    return PdpView(status, price, None)


def _fetch_taobao(row: IntakeRow) -> TaobaoView:
    code = row.ma.strip().upper()
    link = (row.link or "").strip()
    if link == "":
        return TaobaoView(code, "skip", None, "no source link")
    status, body, error = _http_get(link)
    if error:
        return TaobaoView(code, "skip", None, "login-walled or unreachable")
    classified = classify_taobao(status, body)
    return TaobaoView(
        code,
        classified.state,
        classified.public_cny,
        classified.detail,
        classified.promo_cny,
        classified.final_cny,
        classified.sizes,
    )


def _http_get(url: str, timeout: float = 20) -> tuple[int, str, str | None]:
    status, raw, error = _http_get_bytes(url, timeout)
    if error or raw is None:
        return status, "", error
    return status, raw.decode("utf-8", errors="replace"), None


def _http_get_bytes(url: str, timeout: float = 20) -> tuple[int, bytes | None, str | None]:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "*/*"})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return getattr(response, "status", 200), response.read(), None
    except urllib.error.HTTPError as error:
        raw = error.read() if error.fp else b""
        return error.code, raw, None
    except Exception as error:  # noqa: BLE001 — a down host is a source result, not a crash
        return 0, None, str(error)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Write a read-only dataset freshness report.")
    parser.add_argument("--date", default=datetime.now(timezone.utc).date().isoformat())
    parser.add_argument("--out", default="out")
    parser.add_argument("--fixture", help="Snapshot JSON. Skips the network.")
    parser.add_argument("--mode", help="Taobao mode: logged-out or login. Env SASSY_TAOBAO_MODE.")
    parser.add_argument("--meta", help="Meta mode: logged-out or login. Fixtures only. Env SASSY_META_MODE.")
    args = parser.parse_args(argv)
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", args.date) is None:
        print("date must be YYYY-MM-DD", file=sys.stderr)
        return 2
    try:
        if args.fixture:
            snapshot = snapshot_from_json(json.loads(Path(args.fixture).read_text(encoding="utf-8")))
            snapshot.day = args.date
        else:
            snapshot = fetch_live(args.date)
            snapshot.meta_posts = ()
        snapshot.taobao_mode = resolve_mode(args.mode, "SASSY_TAOBAO_MODE", snapshot.taobao_mode, TAOBAO_MODES)
        snapshot.meta_mode = resolve_mode(args.meta, "SASSY_META_MODE", snapshot.meta_mode, META_MODES)
        if not args.fixture:
            snapshot.meta_mode = "logged-out"
            snapshot.meta_posts = ()
        report = evaluate(snapshot)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(str(error), file=sys.stderr)
        return 2
    markdown_path, json_path = write_report(report, Path(args.out))
    print(f"{markdown_path}")
    print(f"{json_path}")
    return 0 if report.guards_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
