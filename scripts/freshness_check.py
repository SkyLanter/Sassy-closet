"""Compare intake, Blob, hub Official, live PDPs, and public Taobao ¥.

Read-only. The only files this writes are out/dataset-freshness-YYYY-MM-DD.md
and the JSON sibling. Guard failures exit 1. A Taobao login wall is SKIP,
not FAIL. Intake ¥ flags are reported and do not change the exit code.

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
from pathlib import Path

_KIT_ROOT = Path(__file__).resolve().parents[1] / "excel-kit"
if str(_KIT_ROOT) not in sys.path:
    sys.path.insert(0, str(_KIT_ROOT))

from openpyxl import load_workbook
from schema import header_row_for_sheet, read_headers, resolve_header_key

from held_policy import HeldPolicy, load_held_policy
from intake_flags import IntakeFlag, IntakeRow, PublicCny, flag_intake

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


_ITEM_URL_PRICE_RE = re.compile(
    r"""https?://(?:item\.taobao\.com|detail\.tmall\.com)/item\.htm\?"""
    r"""(?:[^'"\s<>]|&amp;)*?(?:\?|&|&amp;)price=(\d+(?:\.\d{1,2})?)""",
    flags=re.IGNORECASE,
)


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
    embedded = _ITEM_URL_PRICE_RE.search(html)
    if embedded:
        return Decimal(embedded.group(1))
    return None


def classify_taobao(status: int, html: str) -> TaobaoView:
    if status != 200 or taobao_blocked(html):
        return TaobaoView("", "skip", None, "login-walled or unreachable")
    price = parse_taobao_cny(html)
    if price is None:
        return TaobaoView("", "skip", None, "no public ¥ on the page")
    return TaobaoView("", "ok", price, "")


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
    public = {
        item.ma: PublicCny(item.state, item.public_cny, item.detail) for item in snapshot.taobao
    }
    flags = flag_intake(snapshot.intake, public)
    return Report(
        day=snapshot.day,
        guards=guards,
        flags=flags,
        rows=_comparison_rows(snapshot, public),
        sources={
            "intake": snapshot.intake_state,
            "blob": snapshot.blob_state,
            "hub": snapshot.hub_state,
        },
    )


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
        rows.append(
            TaobaoView(
                item["ma"].strip().upper(),
                state,
                None if raw is None else Decimal(str(raw)),
                "" if item.get("detail") is None else str(item.get("detail")),
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
    return TaobaoView(code, classified.state, classified.public_cny, classified.detail)


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
