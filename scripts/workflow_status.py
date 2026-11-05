#!/usr/bin/env python3
"""Read-only status report for every Sassy Closet workflow.

HTTP is GET only: no POST, PATCH, PUT, or DELETE, and no file, Blob, price,
or Meta writes. The report covers intake reachability and noindex headers,
sell-host blob health, the S06 $25 page, held-mã 404s, and local midnight-qc,
Muse, digest, and cost-recheck verdicts, plus optional draft pull requests.
Response bodies stay in memory for checks and are never printed.
--offline does not call the shop, intake, or gh.
"""

from __future__ import annotations

import argparse
import html
import http.client
import json
import re
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Literal, Never, NoReturn

_SCRIPTS = Path(__file__).resolve().parent
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

import cost_recheck_block  # noqa: E402
from daily_summary_draft import read_meta_status  # noqa: E402
from held_policy import MA_RE, load_held_policy, norm_ma  # noqa: E402

DEFAULT_ROOT = _SCRIPTS.parent
DEFAULT_INTAKE = "https://sassy-closet.vercel.app"
DEFAULT_SHOPS = (
    "https://sassycloset.vercel.app",
    "https://sassy-closet-shop.vercel.app",
)
DEFAULT_REPO = "SkyLanter/Sassy-closet"
DEFAULT_TIMEOUT = 20.0
USER_AGENT = "sassy-workflow-status/1 (read-only)"
MAX_BYTES = 2_000_000
_S06 = "S06"
_STORE_DOWN = '"storeUnavailable":true'
_FALLBACK = "kho đang không đọc được"
_NOINDEX = re.compile(r"(?i)^noindex,\s*nofollow,\s*nosnippet\b")
_LOCK_USD = Decimal("25")
_PRICE_TOKEN = re.compile(r"^\$?(?P<amount>\d+(?:\.\d+)?)$")
_DESC_PRICE = re.compile(r"(?P<price>\$\d+(?:\.\d+)?)\s*·\s*S06\b")
_JSONLD = re.compile(
    r"<script\b[^>]*\btype\s*=\s*(?P<q>[\"'])application/ld\+json(?P=q)[^>]*>(?P<body>.*?)</script>",
    re.I | re.S,
)
_META_TAG = re.compile(r"<meta\b(?P<attrs>[^>]*)/?>", re.I)
_PDP_SPAN = re.compile(
    r"<(?P<tag>[a-zA-Z0-9]+)\b(?P<attrs>[^>]*\bclass\s*=\s*(?P<q>[\"'])(?P<class>[^\"']*)(?P=q)[^>]*)>(?P<text>.*?)</(?P=tag)>",
    re.I | re.S,
)
_ATTR = re.compile(r"([:\w-]+)\s*=\s*(?P<q>[\"'])(?P<value>.*?)(?P=q)", re.I | re.S)
_PDP_CLASS = re.compile(r"(?:^|\s)ky-pdp-price(?:\s|$)")
_DATE = re.compile(r"^(\d{4}-\d{2}-\d{2})$")
_META_NAME = re.compile(r"^meta-qc-(\d{4}-\d{2}-\d{2})\.json$")
_PACK_NAME = re.compile(r"^pack-(\d{4}-\d{2}-\d{2})\.md$")
_EXTRAS_NAME = re.compile(r"^extras-(\d{4}-\d{2}-\d{2})\.md$")
_LUXUBU_NAME = re.compile(r"^luxubu-status-(\d{4}-\d{2}-\d{2})\.json$")
_SUMMARY_NAME = re.compile(r"^summary\.(\d{4}-\d{2}-\d{2})\.json$")
_COST_CSV = re.compile(r"^cost-recheck-(\d{4}-\d{2}-\d{2})\.csv$")
_COST_MD = re.compile(r"^REPORT-(\d{4}-\d{2}-\d{2})\.md$")
_TOTAL_LINE = re.compile(r"^TOTAL\s+(\d+)\b")
_OVERALL_LINE = re.compile(r"^Overall:\s*(OK|GAPS|FAILED)\b")
_READING_TOKEN = re.compile(r"^[A-Za-z0-9_-]{1,32}$")
_VERDICT_WORDS = frozenset({"PASS", "WARN", "FAIL"})
_INDEX_WORDS = frozenset({"OK", "GAPS", "FAILED"})
_META_WORDS = frozenset({"PASS", "FAIL", "UNCHECKED", "DISAGREE"})
_BASE_REJECTED = "base must be http or https with no userinfo"

Overall = Literal["PASS", "WARN", "FAIL"]
LiveState = Literal["PASS", "FAIL", "SKIP"]
DraftState = Literal["skipped", "ok", "unread"]
NetworkMode = Literal["read-only GET", "offline"]

__all__ = [
    "GetResult",
    "WorkflowReport",
    "build_report",
    "http_get",
    "main",
    "render_json",
    "render_text",
]


class ConfigError(ValueError):
    """CLI or URL configuration that must exit 2."""


@dataclass(frozen=True)
class GetResult:
    """One GET. The body is for in-memory checks and is omitted from repr."""

    status: int | None
    headers: dict[str, str]
    body: str = field(repr=False)
    error: str = ""


@dataclass(frozen=True)
class Check:
    name: str
    path: str
    status: int | None
    noindex: bool
    ok: bool
    note: str = ""


@dataclass(frozen=True)
class IntakeReport:
    state: LiveState
    checks: tuple[Check, ...]


@dataclass(frozen=True)
class Miss:
    ma: str
    status: int | None


@dataclass(frozen=True)
class HeldView:
    count: int
    misses: tuple[Miss, ...]


@dataclass(frozen=True)
class HostReport:
    host: str
    health: LiveState
    reading: str | None
    blob_readable: bool | None
    product_count: int | None
    s06: LiveState
    held: HeldView
    health_status: int | None = None
    health_why: str = ""
    s06_status: int | None = None
    s06_price: bool | None = None


@dataclass(frozen=True)
class ReportLine:
    kind: str
    date: str | None
    verdict: str
    path: str | None
    warn: bool = False
    data_ok: str | None = None
    sell_site: str | None = None
    ig: str | None = None
    fb: str | None = None
    total: int | None = None
    index_overall: str | None = None
    unreachable: int | None = None
    unreachable_mas: int | None = None
    persistent_new_unreachable: int | None = None
    live_price_changed: int | None = None
    new_under_or_loss: int | None = None
    taobao_login_needed: bool | None = None


@dataclass(frozen=True)
class Pull:
    number: int
    url: str
    title: str


@dataclass(frozen=True)
class DraftPrs:
    state: DraftState
    detail: str
    pulls: tuple[Pull, ...]


@dataclass(frozen=True)
class WorkflowReport:
    """Status shared by the text and JSON renderers. No response bodies."""

    overall: Overall
    writes: Literal["none"]
    network: NetworkMode
    intake: IntakeReport
    hosts: tuple[HostReport, ...]
    reports: tuple[ReportLine, ...]
    draft_prs: DraftPrs
    config_notes: tuple[str, ...] = ()
    s06_held: bool = False


@dataclass(frozen=True)
class _IntakeProbe:
    name: str
    path: str
    allowed: frozenset[int]
    require_noindex: bool
    api: bool
    needles: tuple[str, ...] = ()


@dataclass(frozen=True)
class _HealthJudge:
    state: Literal["PASS", "FAIL"]
    reading: str | None
    blob_readable: bool | None
    product_count: int | None
    why: str


_INTAKE_PROBES: tuple[_IntakeProbe, ...] = (
    _IntakeProbe("home", "/", frozenset({200}), False, False),
    _IntakeProbe("export", "/api/export", frozenset({200}), True, True),
    _IntakeProbe("submissions", "/api/submissions", frozenset({200}), True, True),
    _IntakeProbe("ma", "/api/ma/S06", frozenset({200}), True, True),
    _IntakeProbe("admin", "/admin/shop", frozenset({200}), True, False),
    _IntakeProbe("csv", "/admin", frozenset({200}), True, True),
    _IntakeProbe("fx", "/api/fx", frozenset({200}), True, True, ("usd_cny",)),
    _IntakeProbe("submission", "/api/submissions/S06", frozenset({200, 404}), True, True),
)
_BLOB_KEYS = frozenset({"configured", "readable"})
_SECRET_KEYS = frozenset({
    "path",
    "prefix",
    "listed",
    "token",
    "sourcelink",
    "sourcelinks",
    "catalogsiteid",
})


class _GetOnlyRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):  # type: ignore[no-untyped-def]
        parts = urllib.parse.urlsplit(newurl)
        current = urllib.parse.urlsplit(req.full_url)
        if parts.scheme not in {"http", "https"} or parts.username or parts.password:
            return None
        if parts.netloc != current.netloc:
            return None
        redirected = super().redirect_request(req, fp, code, msg, headers, newurl)
        if redirected is None:
            return None
        redirected.method = "GET"
        return redirected


def http_get(url: str, timeout: float) -> GetResult:
    """GET url and keep the body in memory. Never prints the response."""

    rejected = _rejected_get(url, timeout)
    if rejected is not None:
        return rejected
    request = urllib.request.Request(
        url,
        headers={"User-Agent": USER_AGENT},
        method="GET",
    )
    opener = urllib.request.build_opener(_GetOnlyRedirect)
    try:
        with opener.open(request, timeout=timeout) as response:
            status = response.status if isinstance(response.status, int) else None
            headers = _header_map(response.headers)
            body = _read_body(response)
            return GetResult(status, headers, body, "")
    except urllib.error.HTTPError as error:
        try:
            headers = _header_map(error.headers)
            body = _read_body(error)
            code = error.code if isinstance(error.code, int) else None
        finally:
            error.close()
        return GetResult(code, headers, body, "")
    except (urllib.error.URLError, TimeoutError, OSError, ValueError) as error:
        return GetResult(None, {}, "", error.__class__.__name__)


def build_report(
    root: Path | str | None = None,
    *,
    intake: str = DEFAULT_INTAKE,
    shops: Sequence[str] | None = None,
    timeout: float = DEFAULT_TIMEOUT,
    offline: bool = False,
    held: Path | str | None = None,
    read_draft_prs: bool = False,
    repo: str = DEFAULT_REPO,
    getter: Callable[[str, float], GetResult] | None = None,
    runner: Callable[..., object] | None = None,
) -> WorkflowReport:
    """Build a status report. Pass getter so tests never touch the network."""

    root_path = DEFAULT_ROOT if root is None else Path(root)
    shop_list = list(DEFAULT_SHOPS) if shops is None else list(shops)
    notes: list[str] = []
    origins: list[str] = []
    if not _timeout_ok(timeout):
        notes.append("timeout must be a positive number")
    try:
        origins.append(_origin(intake))
    except ConfigError:
        notes.append("intake base rejected")
        origins.clear()
    shop_origins: list[str] = []
    if not shop_list:
        notes.append("shop base missing")
    else:
        for shop in shop_list:
            try:
                shop_origins.append(_origin(shop))
            except ConfigError:
                notes.append("shop base rejected")
    if "intake base rejected" in notes:
        intake_origin = ""
    else:
        intake_origin = origins[0] if origins else ""
    policy_codes: tuple[str, ...] = ()
    policy_ok = False
    try:
        policy_codes = _held_codes(Path(held) if held is not None else None)
        policy_ok = True
    except ConfigError as error:
        notes.append(str(error))
    s06_held = _S06 in policy_codes
    checked_codes = tuple(code for code in policy_codes if code != _S06)
    config_bad = bool(notes)
    run_live = not offline and not config_bad
    fetch = http_get if getter is None else getter
    if run_live:
        intake_report = _intake_report(intake_origin, float(timeout), fetch)
        host_reports = tuple(
            _host_report(origin, checked_codes, float(timeout), fetch) for origin in shop_origins
        )
    else:
        intake_report = IntakeReport("SKIP", ())
        if offline and not config_bad and policy_ok:
            host_reports = tuple(
                _skipped_host(origin, len(checked_codes)) for origin in shop_origins
            )
        else:
            host_reports = ()
    report_lines = _local_reports(root_path)
    if read_draft_prs and not offline:
        draft = _read_drafts(repo, runner if runner is not None else subprocess.run)
    elif read_draft_prs:
        draft = DraftPrs("skipped", "offline", ())
    else:
        draft = DraftPrs("skipped", "not requested", ())
    overall = _overall(
        config_bad=config_bad,
        offline=offline,
        intake_report=intake_report,
        hosts=host_reports,
        reports=report_lines,
        draft=draft,
        s06_held=s06_held and policy_ok,
        ran_live=run_live,
    )
    network: NetworkMode = "offline" if offline else "read-only GET"
    return WorkflowReport(
        overall=overall,
        writes="none",
        network=network,
        intake=intake_report,
        hosts=host_reports,
        reports=tuple(report_lines),
        draft_prs=draft,
        config_notes=tuple(notes),
        s06_held=s06_held and policy_ok,
    )


def render_text(report: WorkflowReport) -> str:
    """Plain text report ending with a newline. Omits response bodies."""

    lines = [
        f"Sassy Closet workflow status: {report.overall}",
        f"Network: {report.network}",
        "",
    ]
    for note in report.config_notes:
        lines.append(f"Config: {note}")
    if report.config_notes:
        lines.append("")
    lines.append(f"Intake: {report.intake.state}")
    for check in report.intake.checks:
        lines.append(f"  {_check_text(check)}")
    lines.append("")
    skipped = report.network == "offline" or report.intake.state == "SKIP"
    lines.append("Sell hosts: SKIP" if skipped else "Sell hosts:")
    for host in report.hosts:
        lines.append(f"  {_health_text(host)}")
    lines.append("")
    lines.append("Held mãs: SKIP" if skipped else "Held mãs:")
    if report.s06_held:
        lines.append(f"  WARN {_S06} is on the held list")
    for host in report.hosts:
        lines.append(f"  {_held_text(host, skipped)}")
    lines.append("")
    lines.append("S06: SKIP" if skipped else "S06:")
    for host in report.hosts:
        lines.append(f"  {_s06_text(host, skipped)}")
    lines.append("")
    lines.append("Reports:")
    for item in report.reports:
        lines.append(f"  {_report_text(item)}")
    lines.append("")
    lines.append(f"Draft PRs: {_draft_label(report.draft_prs.state)}")
    if report.draft_prs.detail and report.draft_prs.state != "skipped":
        lines.append(f"  {report.draft_prs.detail}")
    for pull in report.draft_prs.pulls:
        title = _one_line(pull.title, 200)
        url = _one_line(pull.url, 300)
        if title:
            lines.append(f"  #{pull.number} {url} {title}")
        else:
            lines.append(f"  #{pull.number} {url}")
    lines.append("")
    lines.append("Read-only GETs. No writes.")
    return "\n".join(lines) + "\n"


def render_json(report: WorkflowReport) -> dict[str, object]:
    """JSON-ready report with no response bodies or header dumps."""

    return {
        "overall": report.overall,
        "writes": report.writes,
        "network": report.network,
        "intake": {
            "state": report.intake.state,
            "checks": [
                {
                    "name": check.name,
                    "path": check.path,
                    "status": check.status,
                    "noindex": check.noindex,
                    "ok": check.ok,
                }
                for check in report.intake.checks
            ],
        },
        "hosts": [
            {
                "host": host.host,
                "health": host.health,
                "reading": host.reading,
                "blobReadable": host.blob_readable,
                "productCount": host.product_count,
                "s06": host.s06,
                "held": {
                    "count": host.held.count,
                    "misses": [
                        {"ma": miss.ma, "status": miss.status} for miss in host.held.misses
                    ],
                },
            }
            for host in report.hosts
        ],
        "reports": [
            {
                "kind": item.kind,
                "date": item.date,
                "verdict": item.verdict,
                "path": item.path,
            }
            for item in report.reports
        ],
        "draftPrs": {
            "state": report.draft_prs.state,
            "detail": report.draft_prs.detail,
            "pulls": [
                {"number": pull.number, "url": pull.url, "title": pull.title}
                for pull in report.draft_prs.pulls
            ],
        },
    }


def main(argv: list[str] | None = None) -> int:
    """Run the CLI. 0 PASS, 1 WARN, 2 FAIL or usage/config error."""

    parser = _parser()
    try:
        args = parser.parse_args(argv)
    except ConfigError as error:
        print(f"workflow_status: error: {error}", file=sys.stderr)
        return 2
    report = build_report(
        args.root,
        intake=args.intake,
        shops=args.shops,
        timeout=args.timeout,
        offline=args.offline,
        held=args.held,
        read_draft_prs=args.read_draft_prs,
        repo=args.repo,
        getter=http_get,
        runner=subprocess.run,
    )
    if args.json:
        print(json.dumps(render_json(report), indent=2, ensure_ascii=False))
    else:
        sys.stdout.write(render_text(report))
    return _exit_code(report.overall)


def _parser() -> argparse.ArgumentParser:
    parser = _ArgumentParser(
        prog="workflow_status",
        description="Read-only Sassy Closet workflow status. GET only. No writes.",
    )
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--held", type=Path)
    parser.add_argument("--intake", default=DEFAULT_INTAKE)
    parser.add_argument("--shop", action="append", dest="shops")
    parser.add_argument("--timeout", type=float, default=DEFAULT_TIMEOUT)
    parser.add_argument("--offline", action="store_true")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--read-draft-prs", action="store_true")
    parser.add_argument("--repo", default=DEFAULT_REPO)
    return parser


class _ArgumentParser(argparse.ArgumentParser):
    def error(self, message: str) -> NoReturn:
        raise ConfigError(message)


def _exit_code(overall: Overall) -> int:
    if overall == "PASS":
        return 0
    if overall == "WARN":
        return 1
    if overall == "FAIL":
        return 2
    never: Never = overall
    raise AssertionError(never)


def _draft_label(state: DraftState) -> str:
    if state == "skipped":
        return "skipped"
    if state == "ok":
        return "ok"
    if state == "unread":
        return "unread"
    never: Never = state
    raise AssertionError(never)


def _timeout_ok(timeout: object) -> bool:
    if isinstance(timeout, bool) or not isinstance(timeout, (int, float)):
        return False
    number = float(timeout)
    if number != number or number in {float("inf"), float("-inf")}:
        return False
    return number > 0


def _origin(base: str) -> str:
    if not isinstance(base, str):
        raise ConfigError(_BASE_REJECTED)
    raw = base.strip()
    if raw == "" or any(char.isspace() for char in raw) or "\\" in raw:
        raise ConfigError(_BASE_REJECTED)
    parts = urllib.parse.urlsplit(raw)
    if parts.scheme not in {"http", "https"}:
        raise ConfigError(_BASE_REJECTED)
    if parts.username is not None or parts.password is not None or "@" in parts.netloc:
        raise ConfigError(_BASE_REJECTED)
    if parts.hostname is None or parts.hostname == "":
        raise ConfigError(_BASE_REJECTED)
    return urllib.parse.urlunsplit((parts.scheme, parts.netloc, "", "", ""))


def _join(origin: str, path: str) -> str:
    if not path.startswith("/") or path.startswith("//") or "\\" in path or "://" in path:
        raise ConfigError("path escaped the base host")
    base = origin if origin.endswith("/") else origin + "/"
    joined = urllib.parse.urljoin(base, path)
    out = urllib.parse.urlsplit(joined)
    base_parts = urllib.parse.urlsplit(origin)
    if out.scheme != base_parts.scheme or out.netloc != base_parts.netloc:
        raise ConfigError("path escaped the base host")
    if out.username is not None or out.password is not None or "@" in out.netloc:
        raise ConfigError("path escaped the base host")
    safe_path = out.path or "/"
    return urllib.parse.urlunsplit((out.scheme, out.netloc, safe_path, "", ""))


def _rejected_get(url: str, timeout: float) -> GetResult | None:
    if not _timeout_ok(timeout):
        return GetResult(None, {}, "", "bad-timeout")
    try:
        origin = _origin(url)
    except ConfigError:
        return GetResult(None, {}, "", "rejected-url")
    parts = urllib.parse.urlsplit(url)
    origin_parts = urllib.parse.urlsplit(origin)
    if parts.scheme != origin_parts.scheme or parts.netloc != origin_parts.netloc:
        return GetResult(None, {}, "", "rejected-url")
    return None


def _header_map(message: http.client.HTTPMessage | None) -> dict[str, str]:
    if message is None:
        return {}
    grouped: dict[str, list[str]] = {}
    order: list[str] = []
    for key, value in message.items():
        if key not in grouped:
            order.append(key)
            grouped[key] = []
        grouped[key].append(value)
    mapped: dict[str, str] = {}
    for key in order:
        values = grouped[key]
        if key.lower() == "x-robots-tag":
            match = next((item for item in values if _NOINDEX.match(item.strip())), None)
            mapped[key] = match if match is not None else values[0]
        else:
            mapped[key] = values[-1]
    return mapped


def _read_body(response: object) -> str:
    read = getattr(response, "read", None)
    if not callable(read):
        return ""
    try:
        raw = read(MAX_BYTES)
    except (OSError, http.client.HTTPException):
        return ""
    if isinstance(raw, str):
        return raw
    if isinstance(raw, bytes):
        return raw.decode("utf-8", "replace")
    return ""


def _has_noindex(headers: Mapping[str, str]) -> bool:
    for key, value in headers.items():
        if key.lower() == "x-robots-tag" and _NOINDEX.match(value.strip()):
            return True
    return False


def _held_codes(path: Path | None) -> tuple[str, ...]:
    try:
        policy = load_held_policy(path)
    except json.JSONDecodeError:
        raise ConfigError("held policy unreadable") from None
    except UnicodeError:
        raise ConfigError("held policy unreadable") from None
    except OSError:
        raise ConfigError("held policy unreadable") from None
    except ValueError as error:
        raise ConfigError(_safe_held_message(error, path)) from None
    codes = {norm_ma(code) for code in (*policy.held, *policy.never_list)}
    safe = [code for code in codes if MA_RE.fullmatch(code)]
    return tuple(sorted(safe))


def _safe_held_message(error: ValueError, path: Path | None) -> str:
    text = str(error).splitlines()[0] if str(error) else "held policy rejected"
    if path is not None:
        text = text.replace(str(path), "held policy")
        try:
            text = text.replace(str(path.resolve()), "held policy")
        except OSError:
            pass
    text = _one_line(text, 200)
    return text or "held policy rejected"


def _intake_report(
    origin: str,
    timeout: float,
    fetch: Callable[[str, float], GetResult],
) -> IntakeReport:
    checks: list[Check] = []
    for probe in _INTAKE_PROBES:
        result = fetch(_join(origin, probe.path), timeout)
        checks.append(_judge_intake(probe, result))
    state: LiveState = "PASS" if all(check.ok for check in checks) else "FAIL"
    return IntakeReport(state, tuple(checks))


def _judge_intake(probe: _IntakeProbe, result: GetResult) -> Check:
    noindex = _has_noindex(result.headers)
    down = probe.api and _STORE_DOWN in result.body
    missing = _missing_needle(probe, result.body)
    if probe.name == "home":
        fallback = _FALLBACK in result.body
        ok = result.status == 200 and not fallback
        note = _home_note(result.status, fallback)
    else:
        ok = (
            result.status in probe.allowed
            and (noindex or not probe.require_noindex)
            and not down
            and not missing
        )
        note = _api_note(result.status, probe, noindex, down, missing)
    return Check(probe.name, probe.path, result.status, noindex, ok, note)


def _home_note(status: int | None, fallback: bool) -> str:
    if status is None:
        return "network"
    if status != 200:
        return "status"
    if fallback:
        return "fallback"
    return ""


def _api_note(
    status: int | None,
    probe: _IntakeProbe,
    noindex: bool,
    down: bool,
    missing: str,
) -> str:
    if down:
        return "store-unavailable"
    if status is None:
        return "network"
    if status not in probe.allowed:
        return "status"
    if probe.require_noindex and not noindex:
        return "noindex"
    if missing:
        return "rate"
    return ""


def _missing_needle(probe: _IntakeProbe, body: str) -> str:
    for needle in probe.needles:
        if needle not in body:
            return needle
    return ""


def _host_report(
    origin: str,
    codes: Sequence[str],
    timeout: float,
    fetch: Callable[[str, float], GetResult],
) -> HostReport:
    health_result = fetch(_join(origin, "/api/health"), timeout)
    judged = _judge_health(health_result)
    s06_result = fetch(_join(origin, f"/m/{_S06}"), timeout)
    price = _s06_shows_lock(s06_result.body)
    s06_state: Literal["PASS", "FAIL"] = "PASS" if s06_result.status == 200 and price else "FAIL"
    misses: list[Miss] = []
    for code in codes:
        result = fetch(_join(origin, f"/m/{code}"), timeout)
        if result.status != 404:
            misses.append(Miss(code, result.status))
        alias = _held_alias(code)
        if alias == code:
            continue
        alias_result = fetch(_join(origin, f"/m/{alias}"), timeout)
        if alias_result.status != 404:
            misses.append(Miss(alias, alias_result.status))
    return HostReport(
        host=origin,
        health=judged.state,
        reading=judged.reading,
        blob_readable=judged.blob_readable,
        product_count=judged.product_count,
        s06=s06_state,
        held=HeldView(len(codes), tuple(misses)),
        health_status=health_result.status,
        health_why=judged.why,
        s06_status=s06_result.status,
        s06_price=price,
    )


def _judge_health(result: GetResult) -> _HealthJudge:
    if result.status != 200:
        why = "network" if result.status is None else "status"
        return _HealthJudge("FAIL", None, None, None, why)
    try:
        payload = json.loads(result.body)
    except (json.JSONDecodeError, ValueError, RecursionError):
        return _HealthJudge("FAIL", None, None, None, "json")
    if not isinstance(payload, dict):
        return _HealthJudge("FAIL", None, None, None, "json")
    reading = _reading_token(payload.get("reading"))
    blob = payload.get("blob")
    readable: bool | None = None
    if isinstance(blob, dict) and isinstance(blob.get("readable"), bool):
        readable = blob.get("readable")
    count, count_ok = _product_count(payload)
    ok_field = "ok" not in payload or payload.get("ok") is True
    if reading != "blob":
        return _HealthJudge("FAIL", reading, readable, count, "reading")
    if readable is not True:
        return _HealthJudge("FAIL", reading, readable, count, "blob")
    if not count_ok:
        return _HealthJudge("FAIL", reading, readable, count, "productCount")
    if not ok_field:
        return _HealthJudge("FAIL", reading, readable, count, "ok")
    if not _health_is_public(result.body):
        return _HealthJudge("FAIL", reading, readable, count, "leak")
    if not _has_noindex(result.headers):
        return _HealthJudge("FAIL", reading, readable, count, "noindex")
    return _HealthJudge("PASS", reading, readable, count, "")


def _held_alias(ma: str) -> str:
    """S19 -> s019. Same spelling host_health_check uses for the held PDP alias."""

    match = re.fullmatch(r"([A-Za-z]+)0*([0-9]+)", ma.strip())
    if not match:
        return ma.strip().lower()
    return match.group(1).lower() + match.group(2).zfill(3)


def _secret_key(value: object) -> bool:
    if isinstance(value, dict):
        return any(
            str(key).lower() in _SECRET_KEYS or _secret_key(child)
            for key, child in value.items()
        )
    if isinstance(value, list):
        return any(_secret_key(item) for item in value)
    return False


def _health_is_public(raw: str) -> bool:
    """True for the public shop health shape: blob keys configured and readable only."""

    try:
        data = json.loads(raw)
    except (json.JSONDecodeError, ValueError, RecursionError):
        return False
    if not isinstance(data, dict):
        return False
    blob = data.get("blob") if isinstance(data.get("blob"), dict) else {}
    if data.get("reading") != "blob" or blob.get("readable") is not True:
        return False
    if blob.get("configured") is not True or set(blob) != _BLOB_KEYS:
        return False
    low = raw.lower()
    if "token" in low or "vercel_blob" in low or _secret_key(data):
        return False
    return True


def _reading_token(value: object) -> str | None:
    if isinstance(value, str) and _READING_TOKEN.fullmatch(value):
        return value
    return None


def _product_count(payload: Mapping[str, object]) -> tuple[int | None, bool]:
    if "productCount" not in payload:
        return None, False
    value = payload["productCount"]
    if isinstance(value, bool) or not isinstance(value, int):
        return None, False
    if value < 1:
        return value, False
    return value, True


def _s06_shows_lock(body: str) -> bool:
    """True only when S06's own price signals all say $25.

    Related cards on /m/S06 also print prices. A bare $25 anywhere on the
    page is not this product's price. Own signals are the Product JSON-LD
    offer, the share description (`$25 · S06`), and the ky-pdp-price element.
    """

    signals = _jsonld_locks(body) + _meta_locks(body) + _pdp_locks(body)
    return bool(signals) and all(signals)


def _jsonld_locks(body: str) -> list[bool]:
    found: list[bool] = []
    for match in _JSONLD.finditer(body):
        try:
            payload = json.loads(match.group("body").strip())
        except (json.JSONDecodeError, ValueError, RecursionError):
            continue
        _collect_s06_product(payload, found)
    return found


def _collect_s06_product(node: object, found: list[bool]) -> None:
    if isinstance(node, list):
        for item in node:
            _collect_s06_product(item, found)
        return
    if not isinstance(node, dict):
        return
    graph = node.get("@graph")
    if graph is not None:
        _collect_s06_product(graph, found)
    if not _is_s06_product(node):
        return
    offer = _offer_lock(node.get("offers"))
    if offer is not None:
        found.append(offer)
    description = node.get("description")
    if isinstance(description, str):
        described = _description_lock(description)
        if described is not None:
            found.append(described)


def _is_s06_product(node: Mapping[str, object]) -> bool:
    kind = node.get("@type")
    names = kind if isinstance(kind, list) else [kind]
    if not any(name == "Product" for name in names):
        return False
    return norm_ma(node.get("sku")) == _S06


def _offer_lock(offers: object) -> bool | None:
    if isinstance(offers, list):
        known = [flag for item in offers if (flag := _offer_lock(item)) is not None]
        if not known:
            return None
        return all(known)
    if not isinstance(offers, dict) or "price" not in offers:
        return None
    price = offers.get("price")
    if isinstance(price, bool) or price is None:
        return False
    if isinstance(price, (int, float, Decimal)):
        try:
            return Decimal(str(price)) == _LOCK_USD
        except InvalidOperation:
            return False
    if isinstance(price, str):
        return _amount_is_lock(price)
    return False


def _meta_locks(body: str) -> list[bool]:
    found: list[bool] = []
    for match in _META_TAG.finditer(body):
        attrs = _attr_map(match.group("attrs"))
        name = attrs.get("name", "").lower()
        prop = attrs.get("property", "").lower()
        if name != "description" and prop != "og:description":
            continue
        content = attrs.get("content")
        if content is None:
            continue
        flag = _description_lock(html.unescape(content))
        if flag is not None:
            found.append(flag)
    return found


def _pdp_locks(body: str) -> list[bool]:
    found: list[bool] = []
    for match in _PDP_SPAN.finditer(body):
        if _PDP_CLASS.search(match.group("class")) is None:
            continue
        text = re.sub(r"<[^>]+>", "", match.group("text"))
        text = " ".join(html.unescape(text).split())
        found.append(_amount_is_lock(text))
    return found


def _description_lock(text: str) -> bool | None:
    match = _DESC_PRICE.search(text)
    if match is None:
        return None
    return _amount_is_lock(match.group("price"))


def _amount_is_lock(text: str) -> bool:
    match = _PRICE_TOKEN.fullmatch(text.strip())
    if match is None:
        return False
    try:
        return Decimal(match.group("amount")) == _LOCK_USD
    except InvalidOperation:
        return False


def _attr_map(text: str) -> dict[str, str]:
    return {match.group(1).lower(): match.group("value") for match in _ATTR.finditer(text)}


def _skipped_host(origin: str, count: int) -> HostReport:
    return HostReport(
        host=origin,
        health="SKIP",
        reading=None,
        blob_readable=None,
        product_count=None,
        s06="SKIP",
        held=HeldView(count, ()),
    )


def _local_reports(root: Path) -> list[ReportLine]:
    return [
        _midnight(root),
        _meta(root),
        _dated_present(root, "muse-pack", _PACK_NAME),
        _dated_present(root, "muse-extras", _EXTRAS_NAME),
        _luxubu(root),
        _today(root),
        _digest(root),
        _cost(root),
    ]


def _midnight(root: Path) -> ReportLine:
    base = root / "out" / "midnight-qc"
    entries, unreadable = _list_dir(base)
    if unreadable:
        return _bad("midnight-qc")
    found: list[tuple[str, Path]] = []
    for entry in entries:
        if not entry.is_dir() or not _date_ok(entry.name):
            continue
        summary = entry / "summary.json"
        try:
            exists = summary.is_file()
        except OSError:
            continue
        if exists:
            found.append((entry.name, summary))
    picked = _newest(found)
    if picked is None:
        return _missing("midnight-qc")
    stamp, path = picked
    payload = _load_object(path)
    rel = _rel(root, path)
    if payload is None:
        return _bad("midnight-qc", stamp, rel)
    overall = payload.get("overall")
    verdict = overall if isinstance(overall, str) and overall in _VERDICT_WORDS else "UNKNOWN"
    return ReportLine(
        "midnight-qc",
        stamp,
        verdict,
        rel,
        warn=verdict != "PASS",
        data_ok=_verdict_word(payload.get("dataOk")),
        sell_site=_verdict_word(payload.get("sellSite")),
    )


def _meta(root: Path) -> ReportLine:
    picked = _newest_named(root / "out" / "muse", _META_NAME)
    if picked is False:
        return _bad("meta-qc")
    if picked is None:
        return _missing("meta-qc")
    stamp, path = picked
    rel = _rel(root, path)
    try:
        status, _source = read_meta_status(root, stamp)
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError, RecursionError):
        return _bad("meta-qc", stamp, rel)
    ig = _meta_word(status.get("ig") if isinstance(status, dict) else None)
    fb = _meta_word(status.get("fb") if isinstance(status, dict) else None)
    verdict = "CLEAR" if ig == "PASS" and fb == "PASS" else "NOT CLEAR"
    return ReportLine("meta-qc", stamp, verdict, rel, warn=False, ig=ig, fb=fb)


def _dated_present(root: Path, kind: str, pattern: re.Pattern[str]) -> ReportLine:
    picked = _newest_named(root / "out" / "muse", pattern)
    if picked is None:
        return _missing(kind)
    if picked is False:
        return _bad(kind)
    stamp, path = picked
    return ReportLine(kind, stamp, "PRESENT", _rel(root, path), warn=False)


def _luxubu(root: Path) -> ReportLine:
    picked = _newest_named(root / "out" / "muse", _LUXUBU_NAME)
    if picked is None:
        return _missing("luxubu-status")
    if picked is False:
        return _bad("luxubu-status")
    stamp, path = picked
    rel = _rel(root, path)
    if _load_object(path) is None:
        return _bad("luxubu-status", stamp, rel)
    return ReportLine("luxubu-status", stamp, "PRESENT", rel, warn=False)


def _today(root: Path) -> ReportLine:
    path = root / "out" / "muse" / "TODAY.md"
    try:
        exists = path.is_file()
    except OSError:
        return _bad("muse-today")
    if not exists:
        return _missing("muse-today")
    try:
        mtime = path.stat().st_mtime
    except OSError:
        return _bad("muse-today", path=_rel(root, path))
    stamp = datetime.fromtimestamp(mtime, timezone.utc).date().isoformat()
    return ReportLine("muse-today", stamp, "PRESENT", _rel(root, path), warn=False)


def _digest(root: Path) -> ReportLine:
    base = root / "out" / "reports"
    entries, unreadable = _list_dir(base)
    if unreadable:
        return _bad("digest")
    days = [entry for entry in entries if entry.is_dir() and _date_ok(entry.name)]
    if not days:
        return _missing("digest")
    best: tuple[str, Path, str] | None = None
    for day in sorted(days, key=lambda item: item.name, reverse=True):
        try:
            files = [path for path in day.rglob("*") if path.is_file()]
        except OSError:
            return _bad("digest", day.name)
        chosen, mode = _pick_digest(day, files)
        if chosen is None:
            continue
        best = (day.name, chosen, mode)
        break
    if best is None:
        return _missing("digest")
    stamp, chosen, mode = best
    rel = _rel(root, chosen)
    if mode == "index":
        row, overall = _index_signals(chosen)
        if row is None and overall is None and _file_unreadable(chosen):
            return _bad("digest", stamp, rel)
        verdict = row or overall or "PRESENT"
        return ReportLine(
            "digest",
            stamp,
            verdict,
            rel,
            warn=False,
            index_overall=overall,
        )
    total = _total_signal(chosen)
    if total is False:
        return _bad("digest", stamp, rel)
    if total is None:
        verdict = "PRESENT"
        counted: int | None = None
    elif total > 0:
        verdict = "OPEN"
        counted = total
    else:
        verdict = "NONE"
        counted = total
    return ReportLine("digest", stamp, verdict, rel, warn=False, total=counted)


def _pick_digest(day: Path, files: Sequence[Path]) -> tuple[Path | None, str]:
    digest_files = [path for path in files if "digest" in path.name.lower()]
    if digest_files:
        boss = [path for path in digest_files if "boss_decisions_digest" in path.name.lower()]
        pool = boss or digest_files
        return _shallowest(day, pool), "text"
    boss_decisions = [path for path in files if path.name == "BOSS-DECISIONS.md"]
    if boss_decisions:
        return _shallowest(day, boss_decisions), "text"
    indexes = [path for path in files if path.name == "INDEX.md"]
    if indexes:
        return _shallowest(day, indexes), "index"
    return None, "text"


def _cost(root: Path) -> ReportLine:
    base = root / "verify" / "cost-recheck"
    entries, unreadable = _list_dir(base)
    if unreadable:
        return _bad("cost-recheck")
    files = [entry for entry in entries if entry.is_file()]
    ranked: list[tuple[str, int, Path, str]] = []
    for stamp, path in _named(files, _SUMMARY_NAME):
        ranked.append((stamp, 2, path, "summary"))
    for stamp, path in _named(files, _COST_CSV):
        ranked.append((stamp, 1, path, "csv"))
    for stamp, path in _named(files, _COST_MD):
        ranked.append((stamp, 0, path, "md"))
    if not ranked:
        return _missing("cost-recheck")
    stamp, _rank, path, kind = max(ranked, key=lambda item: (item[0], item[1], item[2].name))
    rel = _rel(root, path)
    if kind != "summary":
        return ReportLine("cost-recheck", stamp, "FILE-ONLY", rel, warn=False)
    payload = _load_object(path)
    if payload is None:
        return _bad("cost-recheck", stamp, rel)
    return _cost_parsed(stamp, rel, payload)


def _cost_parsed(stamp: str, rel: str, payload: Mapping[str, object]) -> ReportLine:
    unreachable = None
    counts = payload.get("counts")
    if isinstance(counts, dict) and "unreachable" in counts:
        unreachable = _plain_int(counts.get("unreachable"))
    login = cost_recheck_block.login_blocked(payload)
    verdict = "LOGIN" if login else "PARSED"
    return ReportLine(
        "cost-recheck",
        stamp,
        verdict,
        rel,
        warn=False,
        unreachable=unreachable,
        unreachable_mas=_list_len(payload, "unreachable_mas"),
        persistent_new_unreachable=_list_len(payload, "persistent_new_unreachable"),
        live_price_changed=_list_len(payload, "live_price_changed"),
        new_under_or_loss=_list_len(payload, "new_under_or_loss"),
        taobao_login_needed=login,
    )


def _read_drafts(repo: str, runner: Callable[..., object]) -> DraftPrs:
    command = [
        "gh",
        "pr",
        "list",
        "--repo",
        repo,
        "--state",
        "open",
        "--draft",
        "--json",
        "number,title,url,isDraft",
        "--limit",
        "50",
    ]
    try:
        completed = runner(command, capture_output=True, text=True, check=False)
    except OSError as error:
        detail = "gh not found" if isinstance(error, FileNotFoundError) else error.__class__.__name__
        return DraftPrs("unread", detail, ())
    code = getattr(completed, "returncode", 1)
    if code != 0:
        detail = _one_line(
            _text_attr(completed, "stderr") or _text_attr(completed, "stdout") or "gh failed",
            160,
        )
        return DraftPrs("unread", detail or "gh failed", ())
    try:
        payload = json.loads(_text_attr(completed, "stdout"))
    except (json.JSONDecodeError, ValueError, TypeError):
        return DraftPrs("unread", "gh JSON did not parse", ())
    pulls = _pulls(payload)
    if pulls is None:
        return DraftPrs("unread", "gh JSON did not parse", ())
    count = len(pulls)
    noun = "draft" if count == 1 else "drafts"
    return DraftPrs("ok", f"{count} {noun}", pulls)


def _pulls(payload: object) -> tuple[Pull, ...] | None:
    if not isinstance(payload, list):
        return None
    pulls: list[Pull] = []
    seen: set[int] = set()
    for item in payload:
        if not isinstance(item, dict):
            return None
        if item.get("isDraft") is not True:
            continue
        number = item.get("number")
        if isinstance(number, bool) or not isinstance(number, int):
            return None
        url = item.get("url", "")
        title = item.get("title", "")
        if not isinstance(url, str) or not isinstance(title, str):
            return None
        if number in seen:
            continue
        seen.add(number)
        pulls.append(Pull(number, url, title))
    pulls.sort(key=lambda pull: pull.number)
    return tuple(pulls)


def _overall(
    *,
    config_bad: bool,
    offline: bool,
    intake_report: IntakeReport,
    hosts: Sequence[HostReport],
    reports: Sequence[ReportLine],
    draft: DraftPrs,
    s06_held: bool,
    ran_live: bool,
) -> Overall:
    live_failed = False
    if ran_live:
        if intake_report.state != "PASS":
            live_failed = True
        for host in hosts:
            if host.health != "PASS" or host.s06 != "PASS" or host.held.misses:
                live_failed = True
    warned = offline or s06_held or draft.state == "unread" or any(item.warn for item in reports)
    if config_bad or live_failed:
        return "FAIL"
    if warned:
        return "WARN"
    return "PASS"


def _check_text(check: Check) -> str:
    bits = [
        check.name,
        check.path,
        f"http={_status_text(check.status)}",
        f"noindex={'true' if check.noindex else 'false'}",
        "ok" if check.ok else "FAIL",
    ]
    if check.note:
        bits.append(check.note)
    return " ".join(bits)


def _health_text(host: HostReport) -> str:
    bits = [
        host.host,
        f"health={host.health}",
        f"http={_status_text(host.health_status)}",
        f"reading={host.reading if host.reading is not None else 'null'}",
        f"blobReadable={_json_bool(host.blob_readable)}",
    ]
    if host.product_count is not None:
        bits.append(f"productCount={host.product_count}")
    if host.health_why:
        bits.append(f"why={host.health_why}")
    return " ".join(bits)


def _held_text(host: HostReport, skipped: bool) -> str:
    if skipped:
        return f"{host.host} count={host.held.count}"
    if not host.held.misses:
        return f"{host.host} all 404 ({host.held.count})"
    misses = " ".join(
        f"miss {miss.ma} {_status_text(miss.status)}" for miss in host.held.misses
    )
    return f"{host.host} count={host.held.count} {misses}"


def _s06_text(host: HostReport, skipped: bool) -> str:
    if skipped:
        return host.host
    price = ""
    if host.s06_price is True:
        price = " price=yes"
    elif host.s06_price is False:
        price = " price=no"
    return f"{host.host} {host.s06} http={_status_text(host.s06_status)}{price}"


def _report_text(item: ReportLine) -> str:
    bits = [item.kind, item.date if item.date else "null", item.verdict]
    if item.ig is not None:
        bits.append(f"ig={item.ig}")
    if item.fb is not None:
        bits.append(f"fb={item.fb}")
    if item.data_ok is not None:
        bits.append(f"dataOk={item.data_ok}")
    if item.sell_site is not None:
        bits.append(f"sellSite={item.sell_site}")
    if item.total is not None:
        bits.append(f"total={item.total}")
    if item.index_overall is not None:
        bits.append(f"overall={item.index_overall}")
    if item.unreachable is not None:
        bits.append(f"unreachable={item.unreachable}")
    for label, value in (
        ("unreachable_mas", item.unreachable_mas),
        ("persistent_new_unreachable", item.persistent_new_unreachable),
        ("live_price_changed", item.live_price_changed),
        ("new_under_or_loss", item.new_under_or_loss),
    ):
        if value is not None:
            bits.append(f"{label}={value}")
    if item.taobao_login_needed is not None:
        bits.append(f"taobao_login_needed={_json_bool(item.taobao_login_needed)}")
    bits.append(item.path if item.path else "null")
    return " ".join(bits)


def _json_bool(value: bool | None) -> str:
    if value is True:
        return "true"
    if value is False:
        return "false"
    return "null"


def _status_text(status: int | None) -> str:
    if status is None:
        return "none"
    return str(status)


def _missing(kind: str) -> ReportLine:
    return ReportLine(kind, None, "MISSING", None, warn=True)


def _bad(kind: str, stamp: str | None = None, path: str | None = None) -> ReportLine:
    return ReportLine(kind, stamp, "UNREADABLE", path, warn=True)


def _list_dir(path: Path) -> tuple[list[Path], bool]:
    try:
        exists = path.exists()
    except OSError:
        return [], True
    if not exists:
        return [], False
    try:
        if not path.is_dir():
            return [], True
        return list(path.iterdir()), False
    except OSError:
        return [], True


def _date_ok(value: str) -> bool:
    if _DATE.fullmatch(value) is None:
        return False
    try:
        date.fromisoformat(value)
    except ValueError:
        return False
    return True


def _newest(items: Sequence[tuple[str, Path]]) -> tuple[str, Path] | None:
    if not items:
        return None
    return max(items, key=lambda item: (item[0], item[1].name))


def _newest_named(directory: Path, pattern: re.Pattern[str]) -> tuple[str, Path] | None | bool:
    entries, unreadable = _list_dir(directory)
    if unreadable:
        return False
    found: list[tuple[str, Path]] = []
    for entry in entries:
        try:
            file_ok = entry.is_file()
        except OSError:
            continue
        if not file_ok:
            continue
        match = pattern.fullmatch(entry.name)
        if match is None or not _date_ok(match.group(1)):
            continue
        found.append((match.group(1), entry))
    return _newest(found)


def _named(files: Sequence[Path], pattern: re.Pattern[str]) -> list[tuple[str, Path]]:
    found: list[tuple[str, Path]] = []
    for path in files:
        match = pattern.fullmatch(path.name)
        if match is None or not _date_ok(match.group(1)):
            continue
        found.append((match.group(1), path))
    return found


def _shallowest(day: Path, paths: Sequence[Path]) -> Path:
    def rank(path: Path) -> tuple[int, str]:
        try:
            depth = len(path.relative_to(day).parts)
        except ValueError:
            depth = 99
        return (depth, path.name.lower())

    return min(paths, key=rank)


def _rel(root: Path, path: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except (OSError, ValueError):
        return path.name


def _load_object(path: Path) -> dict[str, object] | None:
    try:
        raw = path.read_bytes()
    except OSError:
        return None
    if len(raw) > MAX_BYTES:
        return None
    try:
        payload = json.loads(raw.decode("utf-8-sig"))
    except (UnicodeError, json.JSONDecodeError, ValueError, RecursionError):
        return None
    if not isinstance(payload, dict):
        return None
    return payload


def _verdict_word(value: object) -> str | None:
    if isinstance(value, str) and value in _VERDICT_WORDS:
        return value
    return None


def _meta_word(pair: object) -> str:
    if isinstance(pair, tuple) and pair and isinstance(pair[0], str):
        word = pair[0].upper()
        if word in _META_WORDS:
            return word
    return "UNCHECKED"


def _plain_int(value: object) -> int | None:
    if isinstance(value, bool) or not isinstance(value, int):
        return None
    return value


def _list_len(payload: Mapping[str, object], key: str) -> int | None:
    if key not in payload:
        return None
    value = payload[key]
    if isinstance(value, list):
        return len(value)
    return None


def _file_unreadable(path: Path) -> bool:
    try:
        with path.open("r", encoding="utf-8", errors="replace"):
            return False
    except OSError:
        return True


def _total_signal(path: Path) -> int | None | bool:
    total: int | None = None
    try:
        with path.open("r", encoding="utf-8", errors="replace") as handle:
            for line in handle:
                match = _TOTAL_LINE.match(line[:4000])
                if match:
                    total = int(match.group(1))
                    break
    except OSError:
        return False
    return total


def _index_signals(path: Path) -> tuple[str | None, str | None]:
    row: str | None = None
    overall: str | None = None
    try:
        with path.open("r", encoding="utf-8", errors="replace") as handle:
            for raw in handle:
                line = raw[:4000]
                if row is None and "boss_decisions_digest" in line:
                    cells = [cell.strip() for cell in line.split("|")]
                    for cell in cells:
                        if cell in _INDEX_WORDS:
                            row = cell
                            break
                if overall is None:
                    match = _OVERALL_LINE.match(line)
                    if match:
                        overall = match.group(1)
    except OSError:
        return None, None
    return row, overall


def _text_attr(completed: object, name: str) -> str:
    value = getattr(completed, name, "")
    if isinstance(value, bytes):
        return value.decode("utf-8", "replace")
    if isinstance(value, str):
        return value
    return ""


def _one_line(value: str, limit: int) -> str:
    text = re.sub(r"\s+", " ", value).strip()
    if len(text) > limit:
        return text[:limit]
    return text


if __name__ == "__main__":
    sys.exit(main())
