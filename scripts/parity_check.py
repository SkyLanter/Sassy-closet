#!/usr/bin/env python3
"""Read-only parity across pricing, mã spelling, size rules, and committed catalogs.

Compares Python with the intake and shop TypeScript helpers, then compares
products.json, intake extras, the live price snapshot, the drift file, and
the held list. Prints disagreements. Does not write a price, a catalog, Blob,
or data/held.json.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import subprocess
import sys
from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from typing import Mapping, Sequence

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from autolist import ASIA, S06_LOCK_USD, SHOE_EU, is_valid_size, margin_for_sell, norm_sizes, price
from held_policy import load_held_policy, norm_ma
from size_gap import CLOTHING_STEPS

PRODUCTS = ROOT / "sassy-closet-shop" / "data" / "products.json"
EXTRAS = ROOT / "sassy-closet-shop" / "data" / "intake-extras.json"
SNAPSHOT = ROOT / "shared" / "live-price-snapshot.json"
DRIFT = ROOT / "data" / "price-drift" / "observed-public-sell.json"
LIVE_FIXTURE = ROOT / "data" / "fixtures" / "seed-vs-live" / "live-sell-2026-10-22.json"
GIA = ROOT / "data" / "approved-held-gia.json"
TAOBAO = ROOT / "sassy-closet-shop" / "data" / "taobao_confirm_seed.json"
TAOBAO_PUBLIC = ROOT / "sassy-closet-shop" / "public" / "data" / "taobao_confirm_seed.json"
VECTOR = ROOT / "scripts" / "testdata" / "ma-normalization-vectors.json"
INTAKE_APP = ROOT / "sassy-closet"
SHOP_APP = ROOT / "sassy-closet-shop"
INTAKE_PROBE = SCRIPTS / "parity_probe_intake.ts"
SHOP_PROBE = SCRIPTS / "parity_probe_shop.ts"

# Official Excel prefixes that already correspond to an intake letter.
EXCEL_PREFIX_FOR_LETTER = {
    "A": "AO",
    "Q": "QU",
    "V": "VA",
    "K": "AK",
    "G": "GI",
    "P": "PK",
    "S": "SET",
}
S06 = "S06"
LOCK_USD = "25"
MAX_EXAMPLES = 12
# Shop EU is 34–42. These trailing-.0 forms sit inside that window.
IN_WINDOW_DECIMAL = ("34.0", "35.0", "40.0", "42.0")
# Both parsers drop these. ".00" and ".5" are not the autolist ".0" suffix.
DROPPED_DECIMAL = ("32.0", "34.00", "34.5", "40.00", "47.0")
# Autolist keeps 33–46. Shop still drops these. The window itself is unchanged.
WINDOW_DECIMAL = ("33.0", "46.0")
DECIMAL_SHOE_TOKENS = IN_WINDOW_DECIMAL + DROPPED_DECIMAL + WINDOW_DECIMAL


@dataclass(frozen=True)
class Example:
    key: str
    left: str
    right: str


@dataclass(frozen=True)
class Finding:
    severity: str
    code: str
    detail: str
    examples: tuple[Example, ...] = ()


@dataclass(frozen=True)
class Report:
    findings: tuple[Finding, ...]

    def code_fails(self) -> tuple[Finding, ...]:
        return tuple(item for item in self.findings if item.severity == "fail")

    def boss_notes(self) -> tuple[Finding, ...]:
        return tuple(item for item in self.findings if item.severity == "boss")

    def to_json(self) -> dict[str, object]:
        return {
            "codeFails": len(self.code_fails()),
            "boss": len(self.boss_notes()),
            "findings": [
                {
                    "severity": item.severity,
                    "code": item.code,
                    "detail": item.detail,
                    "examples": [
                        {"key": example.key, "left": example.left, "right": example.right}
                        for example in item.examples
                    ],
                }
                for item in self.findings
            ],
        }


class ProbeError(RuntimeError):
    pass


def _rank(severity: str) -> int:
    if severity == "fail":
        return 0
    if severity == "boss":
        return 1
    raise ValueError(f"unknown severity {severity}")


def _sorted(findings: list[Finding]) -> tuple[Finding, ...]:
    return tuple(sorted(findings, key=lambda item: (_rank(item.severity), item.code)))


def _note(
    severity: str,
    code: str,
    detail: str,
    examples: Sequence[Example] = (),
    keep: Sequence[str] = (),
) -> Finding:
    pinned = [example for example in examples if example.key in keep]
    rest = [example for example in examples if example.key not in keep]
    shown = tuple((pinned + rest)[:MAX_EXAMPLES])
    if len(examples) > len(shown):
        detail = f"{detail} ({len(examples)} rows, first {len(shown)} shown)"
    return Finding(severity, code, detail, shown)


def _decimal(raw: object) -> Decimal | None:
    try:
        return Decimal(str(raw))
    except (ArithmeticError, ValueError, TypeError):
        return None


def _money_text(value: Decimal) -> str:
    return format(value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP), "f")


def dual_cost_findings(intake: Mapping[str, object], shop: Mapping[str, object]) -> list[Finding]:
    """Shop calcPricing ignores a named USD cost when a yen cost is also set.

    The shop formula stays as it is. A match with the named USD landed means
    the split is gone. A match with neither landed is a broken probe.
    """
    usd = _decimal(intake.get("dualUsdLanded"))
    cny = _decimal(intake.get("dualCnyLanded"))
    shop_landed = _decimal(shop.get("dualShopLanded"))
    if usd is None or cny is None or shop_landed is None:
        return [_note(
            "fail",
            "dual-cost-landed",
            "dual-cost landed probe did not return numbers",
            [Example("Q", str(intake.get("dualUsdLanded")), str(shop.get("dualShopLanded")))],
        )]
    tolerance = Decimal("0.01")
    if abs(shop_landed - usd) <= tolerance:
        return []
    if abs(shop_landed - cny) <= tolerance:
        return [_note(
            "boss",
            "shop-prefers-yen",
            "shop calcPricing prefers the yen figure when both cost fields are set. "
            "Intake named USD uses the dollar cost. The shop formula was not changed.",
            [Example("Q", _money_text(usd), _money_text(shop_landed))],
        )]
    return [_note(
        "fail",
        "dual-cost-landed",
        "shop calcPricing matches neither the named USD landed nor the named CNY landed",
        [Example("Q", _money_text(usd), f"shop {_money_text(shop_landed)}; cny {_money_text(cny)}")],
    )]


def _same_decimal(raw: object, expected: Decimal, tolerance: Decimal) -> bool:
    got = _decimal(raw)
    if got is None:
        return False
    return abs(got - expected) <= tolerance


def dollar_text(raw: object) -> tuple[str, bool]:
    """Return a dollar string and whether it is a non-negative whole dollar."""
    if isinstance(raw, bool) or raw is None:
        return ("", False)
    if isinstance(raw, int):
        return (str(raw), raw >= 0)
    if isinstance(raw, float):
        if raw.is_integer() and raw >= 0:
            return (str(int(raw)), True)
        return (str(raw), False)
    if isinstance(raw, str):
        text = raw.strip()
        if text.isdigit():
            return (str(int(text)), True)
        return (text, False)
    return (str(raw), False)


def price_disagreements(left: Mapping[str, str], right: Mapping[str, str]) -> tuple[Example, ...]:
    """Whole-dollar keys present on both sides whose amounts differ. Inputs stay as passed."""
    rows: list[Example] = []
    for key in sorted(set(left) & set(right)):
        if left[key] != right[key]:
            rows.append(Example(key, left[key], right[key]))
    return tuple(rows)


def quote_examples(
    python_quotes: Mapping[str, int],
    shared_quotes: Mapping[str, object],
    intake_quotes: Mapping[str, object],
) -> tuple[Example, ...]:
    rows: list[Example] = []
    for key in sorted(set(python_quotes) | set(shared_quotes) | set(intake_quotes)):
        py = python_quotes.get(key)
        shared = shared_quotes.get(key)
        intake = intake_quotes.get(key)
        if shared != py or intake != py:
            rows.append(Example(str(key), str(py), f"shared {shared}; intake {intake}"))
    return tuple(rows)


def _load(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def _excel():
    file = ROOT / "excel-kit" / "schema.py"
    spec = importlib.util.spec_from_file_location("sassy_excel_schema", file)
    if spec is None or spec.loader is None:
        raise ProbeError(f"cannot load {file}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _rows(payload: object, field: str) -> list[dict[str, object]]:
    if not isinstance(payload, dict):
        raise ValueError(f"{field} file must be an object")
    rows = payload.get(field)
    if not isinstance(rows, list):
        raise ValueError(f"{field} must be a list")
    return [row for row in rows if isinstance(row, dict)]


def _index_prices(rows: Sequence[Mapping[str, object]], field: str) -> tuple[dict[str, str], list[str], list[str]]:
    prices: dict[str, str] = {}
    duplicates: list[str] = []
    odd: list[str] = []
    for row in rows:
        code = norm_ma(row.get("ma"))
        if code in prices:
            duplicates.append(code)
        text, whole = dollar_text(row.get(field))
        if text and not whole:
            odd.append(code or str(row.get("ma")))
        prices[code] = text
    return prices, duplicates, odd


def _statuses(rows: Sequence[Mapping[str, object]]) -> dict[str, str]:
    out: dict[str, str] = {}
    for row in rows:
        status = row.get("status")
        out[norm_ma(row.get("ma"))] = status.strip().lower() if isinstance(status, str) else ""
    return out


def landed_grid() -> list[str]:
    values: list[str] = []
    cents = 5
    while cents <= 4000:
        values.append(f"{cents // 100}.{cents % 100:02d}")
        cents += 5
    for extra in ("3.90", "16.26", "19.50", "19.51", "19.58", "33.75"):
        if extra not in values:
            values.append(extra)
    return values


def _vector_inputs() -> list[object]:
    payload = _load(VECTOR)
    if not isinstance(payload, dict) or not isinstance(payload.get("rows"), list):
        raise ProbeError("mã vector is missing rows")
    return [row.get("input") if isinstance(row, dict) else None for row in payload["rows"]]


def _probe_request() -> dict[str, object]:
    shoe = [str(number) for number in range(32, 48)]
    letters = list(EXCEL_PREFIX_FOR_LETTER)
    letters.extend(["D", "B", "H", "J", "O"])
    stale_yen = "100"
    named_usd = "10"
    one_usd = "1"
    return {
        "mas": _vector_inputs(),
        "landed": landed_grid(),
        "sells": list(range(1, 81)),
        "letters": letters,
        "aliasTokens": ["XXS", "3XL", "XXL"],
        "shoeTokens": [*shoe, *DECIMAL_SHOE_TOKENS],
        "currencyCase": {
            "ma": "A04",
            "kind": "A",
            "liveUsd": 27,
            "costCny": stale_yen,
            "costUsd": named_usd,
            "fx": "6.723",
        },
        "captionCase": {
            "ma": "A04",
            "kind": "A",
            "sellUsd": "3",
            "costCny": stale_yen,
            "costUsd": one_usd,
            "fx": "6.723",
        },
        "deboxCase": {
            "ma": "Q01",
            "kind": "Q",
            "liveUsd": 40,
            "costCny": "",
            "costUsd": named_usd,
        },
        "dualCost": {
            "kind": "Q",
            "costCny": stale_yen,
            "costUsd": named_usd,
            "fx": "6.723",
        },
    }


def _parse_probe(stdout: str) -> dict[str, object]:
    text = stdout.strip()
    if not text:
        raise ProbeError("probe printed nothing")
    try:
        payload = json.loads(text)
    except json.JSONDecodeError:
        payload = json.loads(text.splitlines()[-1])
    if not isinstance(payload, dict):
        raise ProbeError("probe did not print an object")
    return payload


def _run_probe(app: Path, args: list[str], request: dict[str, object]) -> dict[str, object]:
    if not (app / "node_modules" / "tsx").exists():
        raise ProbeError(f"tsx is not installed in {app.name}; run npm ci there before the parity check")
    try:
        proc = subprocess.run(
            args,
            cwd=app,
            input=json.dumps(request),
            capture_output=True,
            text=True,
            timeout=120,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as error:
        raise ProbeError(f"{app.name} probe failed: {error}") from error
    if proc.returncode != 0:
        tail = (proc.stderr or proc.stdout or "").strip().splitlines()
        detail = tail[-1] if tail else f"exit {proc.returncode}"
        raise ProbeError(f"{app.name} probe exit {proc.returncode}: {detail[:400]}")
    return _parse_probe(proc.stdout)


def run_probes() -> tuple[dict[str, object], dict[str, object]]:
    request = _probe_request()
    intake = _run_probe(
        INTAKE_APP,
        ["node", "--import", "tsx", str(INTAKE_PROBE)],
        request,
    )
    shop = _run_probe(
        SHOP_APP,
        ["node", "--require", "./scripts/alias.cjs", "--import", "tsx", str(SHOP_PROBE)],
        request,
    )
    return intake, shop


def _strings(value: object) -> tuple[str, ...]:
    if not isinstance(value, list):
        return ()
    return tuple(str(item) for item in value)


def _joined(sizes: tuple[str, ...]) -> str:
    return " ".join(sizes) if sizes else "dropped"


def decimal_shoe_misses(shop_parsed: Mapping[str, object]) -> tuple[Example, ...]:
    """In-window trailing .0 must become the same EU size. Other suffixes must drop."""
    misses: list[Example] = []
    for token in IN_WINDOW_DECIMAL:
        expected = token.split(".", 1)[0]
        py = tuple(norm_sizes(token, "G"))
        shop_got = _strings(shop_parsed.get(token))
        if py != (expected,) or shop_got != (expected,):
            misses.append(Example(token, expected, f"autolist {_joined(py)}; shop {_joined(shop_got)}"))
    for token in DROPPED_DECIMAL:
        py = tuple(norm_sizes(token, "G"))
        shop_got = _strings(shop_parsed.get(token))
        if py or shop_got:
            misses.append(Example(token, "dropped", f"autolist {_joined(py)}; shop {_joined(shop_got)}"))
    return tuple(misses)


def decimal_shoe_window(shop_parsed: Mapping[str, object]) -> tuple[Example, ...]:
    """33.0 and 46.0 stay a window split. Shop does not grow to 33–46."""
    rows: list[Example] = []
    for token in WINDOW_DECIMAL:
        py = tuple(norm_sizes(token, "G"))
        shop_got = _strings(shop_parsed.get(token))
        if py != shop_got:
            rows.append(Example(token, _joined(py), _joined(shop_got)))
    return tuple(rows)


def _mapping(value: object) -> dict[str, object]:
    if not isinstance(value, dict):
        return {}
    return value


def data_findings() -> list[Finding]:
    findings: list[Finding] = []
    required = (PRODUCTS, EXTRAS, SNAPSHOT, DRIFT, LIVE_FIXTURE, GIA, TAOBAO, TAOBAO_PUBLIC, VECTOR)
    missing = [str(path.relative_to(ROOT)) for path in required if not path.is_file()]
    if missing:
        findings.append(_note("fail", "missing-file", "a catalog file used for parity is missing", [
            Example(path, "missing", "") for path in missing
        ]))
        return findings
    if TAOBAO.read_bytes() != TAOBAO_PUBLIC.read_bytes():
        findings.append(_note("fail", "taobao-seed-copy", "shop data and public taobao seed files differ"))

    products = _rows(_load(PRODUCTS), "products")
    extras = _rows(_load(EXTRAS), "products")
    snapshot_rows = _rows(_load(SNAPSHOT), "rows")
    fixture_rows = _rows(_load(LIVE_FIXTURE), "products")
    product_prices, product_dups, product_odd = _index_prices(products, "priceUsd")
    extra_prices, extra_dups, extra_odd = _index_prices(extras, "priceUsd")
    live_prices, live_dups, live_odd = _index_prices(snapshot_rows, "liveUsd")
    fixture_prices, fixture_dups, fixture_odd = _index_prices(fixture_rows, "priceUsd")
    for code, dups in (
        ("duplicate-ma", product_dups + extra_dups + live_dups + fixture_dups),
    ):
        if dups:
            findings.append(_note("fail", code, "a committed catalog repeats a mã", [
                Example(item, "duplicate", "") for item in sorted(set(dups))
            ]))
    odd = sorted(set(product_odd + extra_odd + live_odd + fixture_odd))
    if odd:
        findings.append(_note("boss", "non-whole-price", "a committed price is not a non-negative whole dollar", [
            Example(item, "non-whole", "") for item in odd
        ]))

    drift_payload = _load(DRIFT)
    drift_raw = drift_payload.get("liveUsd") if isinstance(drift_payload, dict) else None
    drift_prices: dict[str, str] = {}
    if isinstance(drift_raw, dict):
        for key, value in drift_raw.items():
            text, whole = dollar_text(value)
            if whole:
                drift_prices[norm_ma(key)] = text
    for code, left, right, detail in (
        ("snapshot-vs-drift", live_prices, drift_prices, "live snapshot liveUsd and price-drift liveUsd differ"),
        ("snapshot-vs-fixture", live_prices, fixture_prices, "live snapshot and the 2026-10-22 live fixture differ"),
    ):
        rows = price_disagreements(left, right)
        if rows:
            findings.append(_note("fail", code, detail, rows))

    seed_rows = price_disagreements(product_prices, live_prices)
    if seed_rows:
        findings.append(_note(
            "boss",
            "seed-vs-live-price",
            "products.json priceUsd disagrees with the live snapshot; prices were not changed",
            seed_rows,
        ))
    missing_live = sorted(set(live_prices) - set(product_prices))
    if missing_live:
        findings.append(_note(
            "boss",
            "seed-missing-live",
            "live snapshot mãs are absent from products.json",
            [Example(item, "live", "not in seed") for item in missing_live],
            keep=(S06,),
        ))
    extra_rows = price_disagreements(extra_prices, live_prices)
    if extra_rows:
        findings.append(_note(
            "boss",
            "extras-vs-live-price",
            "intake-extras.json priceUsd disagrees with the live snapshot; prices were not changed",
            extra_rows,
        ))
    if extra_prices.get(S06) not in (None, "", LOCK_USD):
        findings.append(_note(
            "boss",
            "extras-s06-lock",
            "intake-extras.json has S06 off $25; the file was not changed",
            [Example(S06, extra_prices.get(S06, ""), LOCK_USD)],
        ))
    if live_prices.get(S06) not in (None, LOCK_USD):
        findings.append(_note(
            "boss",
            "live-s06-lock",
            "the live snapshot has S06 off $25; the file was not changed",
            [Example(S06, live_prices.get(S06, ""), LOCK_USD)],
        ))

    policy = load_held_policy()
    held = set(policy.held)
    available = [
        code
        for code, status in _statuses(products).items()
        if code in held and status == "available"
    ]
    if available:
        findings.append(_note(
            "boss",
            "held-available-in-seed",
            "a held mã is available in products.json; held.json was not changed",
            [Example(code, "held", "available") for code in sorted(available)],
        ))
    gia_payload = _load(GIA)
    approved = gia_payload.get("approvedGia") if isinstance(gia_payload, dict) else None
    if isinstance(approved, dict):
        off = sorted(norm_ma(key) for key in approved if norm_ma(key) not in held)
        if off:
            findings.append(_note(
                "boss",
                "gia-off-held",
                "approved held Giá names a mã that is not on the held list",
                [Example(code, "approved Giá", "not held") for code in off],
            ))
    allow = _load(PRODUCTS)
    if isinstance(allow, dict) and isinstance(allow.get("allowlist"), list):
        missing_allow = sorted(
            norm_ma(item)
            for item in allow["allowlist"]
            if isinstance(item, str) and norm_ma(item) not in product_prices
        )
        if missing_allow:
            findings.append(_note("fail", "allowlist-missing", "an allowlist mã is not in products.json", [
                Example(code, "allowlist", "missing") for code in missing_allow
            ]))
    return findings


def _excel_findings(excel) -> list[Finding]:
    findings: list[Finding] = []
    letters = tuple(excel.INTAKE_KIND_CODES)
    missing_prefix = [letter for letter in letters if letter not in EXCEL_PREFIX_FOR_LETTER]
    unknown_prefix = [
        letter
        for letter, prefix in EXCEL_PREFIX_FOR_LETTER.items()
        if prefix not in excel.MA_PREFIXES
    ]
    if unknown_prefix:
        findings.append(_note("fail", "excel-prefix", "an Excel prefix mapped here is not in MA_PREFIXES", [
            Example(letter, EXCEL_PREFIX_FOR_LETTER[letter], "missing") for letter in unknown_prefix
        ]))
    if missing_prefix:
        findings.append(_note(
            "boss",
            "excel-letter-gap",
            "intake letters have no Official Excel prefix (AO/QU/VA/AK/GI/PK/SET); schema was not changed",
            [Example(letter, "intake letter", "no Official prefix") for letter in missing_prefix],
        ))
    return findings


def _rule_findings(excel, intake: Mapping[str, object], shop: Mapping[str, object]) -> list[Finding]:
    findings: list[Finding] = []
    ladders = {
        "autolist": tuple(ASIA),
        "size_gap": tuple(CLOTHING_STEPS),
        "excel": tuple(excel.INTAKE_CLOTHING_SIZES),
        "intake": _strings(intake.get("clothing")),
        "shop": _strings(shop.get("clothing")),
    }
    drift = [name for name, ladder in ladders.items() if ladder != tuple(ASIA)]
    if drift:
        findings.append(_note("fail", "clothing-ladder", "clothing size ladders disagree", [
            Example(name, " ".join(ladders[name]), " ".join(ASIA)) for name in drift
        ]))
    if _strings(intake.get("shoe")) != tuple(excel.INTAKE_SHOE_SIZES):
        findings.append(_note(
            "fail",
            "intake-excel-shoe",
            "intake shoe sizes and excel-kit INTAKE_SHOE_SIZES disagree",
            [Example("shoe", " ".join(_strings(intake.get("shoe"))), " ".join(excel.INTAKE_SHOE_SIZES))],
        ))
    kind_sets = {
        "excel": tuple(excel.INTAKE_KIND_CODES),
        "intake": _strings(intake.get("kindLetters")),
        "shop": _strings(shop.get("kindLetters")),
    }
    kind_drift = [name for name, letters in kind_sets.items() if letters != tuple(excel.INTAKE_KIND_CODES)]
    if kind_drift:
        findings.append(_note("fail", "kind-letters", "kind letter lists disagree", [
            Example(name, "".join(kind_sets[name]), "".join(excel.INTAKE_KIND_CODES)) for name in kind_drift
        ]))

    tokens = [str(number) for number in range(32, 48)]
    derived_py = tuple(norm_sizes(" ".join(tokens), "G"))
    if derived_py != tuple(SHOE_EU):
        findings.append(_note("fail", "shoe-behavior", "autolist.norm_sizes does not match SHOE_EU"))
    if _strings(intake.get("keepG")) != _strings(intake.get("shoe")):
        findings.append(_note("fail", "shoe-behavior", "intake keepSizesForKind does not match its shoe list"))
    shop_parsed = _mapping(shop.get("shoeParsed"))
    derived_shop = tuple(token for token in tokens if _strings(shop_parsed.get(token)))
    if derived_shop != _strings(shop.get("shoe")):
        findings.append(_note("fail", "shoe-behavior", "shop parseAsiaSizes does not match EU_SHOE_SIZES"))

    windows = {
        "autolist": derived_py,
        "intake": _strings(intake.get("shoe")),
        "shop": _strings(shop.get("shoe")),
    }
    if len(set(windows.values())) > 1:
        findings.append(_note(
            "boss",
            "shoe-window",
            "shoe EU windows disagree; no size list was rewritten",
            [Example(name, " ".join(window), " ".join(windows["intake"])) for name, window in windows.items()],
        ))
    if norm_sizes("36", "O") and "36" not in _strings(intake.get("keepO")):
        findings.append(_note(
            "boss",
            "kind-o-scale",
            "autolist treats O as a shoe kind; intake keeps clothing sizes for O",
            [Example("O", "autolist keeps 36", "intake drops 36")],
        ))
    if _strings(shop_parsed.get("36")) and "36" not in _strings(_mapping(intake.get("scales")).get("A")):
        ignored = [Example("36", "shop keeps 36", "intake clothing drops 36")]
        if _strings(shop_parsed.get("40.0")) == ("40",) and not norm_sizes("40.0", "A"):
            ignored.append(Example("40.0", "shop keeps 40", "autolist clothing drops 40.0"))
        findings.append(_note(
            "boss",
            "shop-parse-ignores-kind",
            "shop parseAsiaSizes keeps an EU shoe token on any row; intake clothing kinds drop it",
            ignored,
        ))
    decimal_misses = decimal_shoe_misses(shop_parsed)
    if decimal_misses:
        findings.append(_note(
            "fail",
            "shoe-decimal",
            "a trailing .0 shoe token does not collapse to the same EU size",
            decimal_misses,
        ))
    decimal_window = decimal_shoe_window(shop_parsed)
    if decimal_window:
        findings.append(_note(
            "boss",
            "shoe-decimal-window",
            "trailing .0 outside the shop EU window stays dropped there; autolist keeps 33-46. No size list was rewritten.",
            decimal_window,
        ))
    if is_valid_size("M", "G") and not _strings(intake.get("keepGLetters")):
        findings.append(_note(
            "boss",
            "shoe-letter-size",
            "autolist accepts clothing letter M on a G mã; intake shoe sizes drop M",
        ))

    alias_py = tuple(norm_sizes("XXS 3XL XXL", "A"))
    alias_shop = tuple(sorted(_strings(shop.get("aliasParsed")), key=lambda item: ASIA.index(item) if item in ASIA else 99))
    if alias_py != alias_shop:
        findings.append(_note(
            "fail",
            "size-alias",
            "XXS / 3XL / XXL do not collapse to the same clothing sizes",
            [Example("alias", " ".join(alias_py), " ".join(alias_shop))],
        ))
    return findings


def _ma_findings(intake: Mapping[str, object], shop: Mapping[str, object]) -> list[Finding]:
    inputs = _vector_inputs()
    helpers = {
        "mint": _mapping(intake.get("normalizeMa")),
        "held": _mapping(intake.get("canonicalHeldKey")),
        "quote": _mapping(intake.get("canonicalQuoteMa")),
        "shop": _mapping(shop.get("canonicalMaSpelling")),
    }
    misses: list[Example] = []
    pad_misses: list[Example] = []
    shop_plain = _mapping(shop.get("normalizeMa"))
    for index, raw in enumerate(inputs):
        expected = norm_ma(raw)
        for name, table in helpers.items():
            got = table.get(str(index))
            if got != expected:
                misses.append(Example(str(raw), expected, f"{name} {got}"))
        plain = shop_plain.get(str(index))
        if plain != expected:
            pad_misses.append(Example(str(raw), expected, str(plain)))
    findings: list[Finding] = []
    if misses:
        findings.append(_note("fail", "ma-vector", "a canonical mã helper disagrees with norm_ma", misses))
    if pad_misses:
        findings.append(_note(
            "boss",
            "shop-normalize-no-pad",
            "shop normalizeMa trims and upper-cases only; canonicalMaSpelling collapses padding",
            pad_misses,
            keep=("K003",),
        ))
    short = _mapping(intake.get("shortA1"))
    if short.get("ok") is False and norm_ma("A1") == "A01":
        findings.append(_note(
            "boss",
            "short-ma-quote",
            "wouldBeLiveUsd rejects A1; norm_ma maps A1 to A01. The shop test locks the rejection. No quote was stored.",
            [Example("A1", "A01", str(short.get("error")))],
        ))
    elif short.get("ma") != "A01":
        findings.append(_note("fail", "short-ma-quote", "wouldBeLiveUsd accepted A1 as a different mã", [
            Example("A1", "A01", str(short.get("ma")))
        ]))
    s6 = _mapping(intake.get("shortS6"))
    if s6.get("ok") is not True or s6.get("ma") != S06 or s6.get("wouldBeUsd") != S06_LOCK_USD:
        findings.append(_note("fail", "s06-short-spelling", "s6 is not locked at $25", [
            Example("s6", str(S06_LOCK_USD), str(s6))
        ]))
    return findings


def _price_findings(intake: Mapping[str, object], shop: Mapping[str, object]) -> list[Finding]:
    findings: list[Finding] = []
    grid = landed_grid()
    py_quotes = {text: price(Decimal(text)) for text in grid}
    shared = _mapping(intake.get("sharedTier"))
    intake_tier = _mapping(intake.get("intakeTier"))
    tier_rows = quote_examples(py_quotes, shared, intake_tier)
    if tier_rows:
        findings.append(_note("fail", "tier-quote", "tiered sell quotes disagree", tier_rows))

    flat_rows: list[Example] = []
    intake_flat = _mapping(intake.get("flat"))
    shop_flat = _mapping(shop.get("flat"))
    for text in grid:
        if intake_flat.get(text) != shop_flat.get(text):
            flat_rows.append(Example(text, str(intake_flat.get(text)), str(shop_flat.get(text))))
    if flat_rows:
        findings.append(_note("fail", "flat-quote", "flat 25% sell quotes disagree", flat_rows))

    margin_rows: list[Example] = []
    shared_margin = _mapping(intake.get("sharedMargin"))
    intake_margin = _mapping(intake.get("intakeMargin"))
    for sell in range(1, 81):
        py = margin_for_sell(sell)
        shared_value = shared_margin.get(str(sell))
        intake_value = intake_margin.get(str(sell))
        shared_ok = _same_decimal(shared_value, py, Decimal(0))
        # Intake's copy is binary float. A tiny remainder is not a different margin.
        intake_ok = _same_decimal(intake_value, py, Decimal("0.000000001"))
        if not shared_ok or not intake_ok:
            margin_rows.append(Example(str(sell), str(py), f"shared {shared_value}; intake {intake_value}"))
    if margin_rows:
        findings.append(_note("fail", "tier-margin", "tier margins disagree", margin_rows))

    if intake.get("blankUsd") != intake.get("wouldBeUsd") or intake.get("blankCny") != intake.get("wouldBeCny"):
        findings.append(_note(
            "fail",
            "named-currency-tier",
            "a named cost currency does not produce the same tier quote in intake and wouldBeLiveUsd",
            [Example("USD", str(intake.get("blankUsd")), str(intake.get("wouldBeUsd"))),
             Example("CNY", str(intake.get("blankCny")), str(intake.get("wouldBeCny")))],
        ))
    if intake.get("blankEmpty") != intake.get("wouldBeEmpty"):
        findings.append(_note(
            "fail",
            "empty-currency-tier",
            "an empty cost currency does not match between intake and wouldBeLiveUsd",
        ))
    if intake.get("wouldBeOmitted") != intake.get("blankEmpty"):
        findings.append(_note(
            "boss",
            "cost-currency-default",
            "omitting costCurrency still prefers yen when both costs are set; intake's blank currency prefers USD. No price was stored.",
            [Example("A04", f"omitted {intake.get('wouldBeOmitted')}", f"intake blank currency {intake.get('blankEmpty')}")],
        ))
    if intake.get("viewFlag") != intake.get("sellFlag"):
        findings.append(_note(
            "boss",
            "caption-vs-intake-tier",
            "intakePriceView flags a sell under the tier quote; sellPriceFlag still uses the 35% floor, so the caption can show the dollar. Caption copy was not changed.",
            [Example("A04", str(intake.get("viewFlag")), f"sellFlag {intake.get('sellFlag')}; caption {intake.get('caption')}")],
        ))
    expected_debox = price(Decimal("17.50"))
    if intake.get("deboxWouldBe") != expected_debox or intake.get("deboxBlank") != expected_debox:
        findings.append(_note(
            "fail",
            "debox-tier",
            "Q debox $7.50 is not included in the named-USD tier quote",
            [Example("Q01", str(expected_debox), f"wouldBe {intake.get('deboxWouldBe')}; intake {intake.get('deboxBlank')}")],
        ))

    locked = _mapping(intake.get("lockedDebox"))
    intake_debox = _mapping(intake.get("intakeDebox"))
    shop_debox = _mapping(shop.get("debox"))
    debox_fail: list[Example] = []
    shop_unknown = False
    for letter, raw in intake_debox.items():
        amount = _decimal(raw)
        locked_amount = _decimal(locked.get(letter))
        if amount is None or locked_amount is None or locked_amount != amount:
            debox_fail.append(Example(letter, str(raw), str(locked.get(letter))))
            continue
        shop_value = shop_debox.get(letter)
        if letter in {"V", "Q", "D"}:
            if not _same_decimal(shop_value, Decimal("7.5"), Decimal(0)):
                debox_fail.append(Example(letter, "7.5", str(shop_value)))
        elif shop_value is None and amount == 0:
            shop_unknown = True
        elif not _same_decimal(shop_value, amount, Decimal(0)):
            debox_fail.append(Example(letter, str(amount), str(shop_value)))
    if debox_fail:
        findings.append(_note("fail", "debox-table", "debox tables disagree", debox_fail))
    if shop_unknown:
        findings.append(_note(
            "boss",
            "shop-debox-unknown",
            "shop deboxForLetter is null off V/Q/D (it will not invent $0); intake and the shared quote use $0. No debox was written.",
        ))
    findings.extend(dual_cost_findings(intake, shop))
    return findings


def build_report() -> Report:
    findings = data_findings()
    excel = _excel()
    findings.extend(_excel_findings(excel))
    try:
        intake, shop = run_probes()
    except ProbeError as error:
        findings.append(_note("fail", "ts-probe", str(error)))
        return Report(_sorted(findings))
    findings.extend(_rule_findings(excel, intake, shop))
    findings.extend(_ma_findings(intake, shop))
    findings.extend(_price_findings(intake, shop))
    return Report(_sorted(findings))


def render_text(report: Report) -> str:
    lines = [
        f"code fails: {len(report.code_fails())}",
        f"boss notes: {len(report.boss_notes())}",
    ]
    for item in report.findings:
        sample = ", ".join(f"{example.key} {example.left} vs {example.right}" for example in item.examples)
        suffix = f" {sample}" if sample else ""
        lines.append(f"{item.severity} {item.code}: {item.detail}{suffix}")
    lines.append("read-only: no price writes, held.json not changed")
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Read-only pricing, mã, size, and catalog parity check.")
    parser.add_argument("--json", action="store_true", help="print the report as JSON")
    parser.add_argument("--strict", action="store_true", help="exit 1 when a Boss note is present")
    args = parser.parse_args(argv)
    report = build_report()
    if args.json:
        sys.stdout.write(json.dumps(report.to_json(), indent=2) + "\n")
    else:
        sys.stdout.write(render_text(report))
    blocked = report.findings if args.strict else report.code_fails()
    return 1 if blocked else 0


if __name__ == "__main__":
    sys.exit(main())
