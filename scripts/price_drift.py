"""Flag public sell-price drift across in-repo fixtures.

Reads local JSON and the shop README table. Does not fetch, and does not
write Blob, intake, Meta, products.json, or any sell price.
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from pathlib import Path

S06 = "S06"
S06_USD = 25
MA_RE = re.compile(r"^[A-Z][0-9]{2}$")
SOURCE_ORDER = (
    "intake",
    "catalog-seed",
    "readme-hub-ten",
    "preserve-live",
    "boss-price-lock",
)
COST_KEY = re.compile(r"cost|landed|cny|debox|yen", re.IGNORECASE)


@dataclass(frozen=True)
class Drift:
    source: str
    ma: str
    fixture_usd: int
    live_usd: int

    @property
    def gap(self) -> int:
        return abs(self.fixture_usd - self.live_usd)


@dataclass(frozen=True)
class Report:
    observed_at: str
    drifts: tuple[Drift, ...]
    intake_matches: tuple[tuple[str, int], ...]
    s06_live: int | None
    s06_problems: tuple[str, ...]
    problems: tuple[str, ...]
    seed_missing: tuple[str, ...]
    page_checks: tuple[tuple[str, str, int], ...]

    @property
    def exit_code(self) -> int:
        if self.drifts or self.s06_problems or self.problems:
            return 1
        return 0


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def whole_dollars(value: object, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError(f"{label} must be a whole-dollar sell price")
    return value


def _price_map(value: object, label: str) -> dict[str, int]:
    if not isinstance(value, dict):
        raise ValueError(f"{label} must be an object of mã to dollars")
    prices: dict[str, int] = {}
    for key, raw in value.items():
        if not isinstance(key, str) or MA_RE.fullmatch(key) is None:
            raise ValueError(f"{label} has an invalid mã {key!r}")
        prices[key] = whole_dollars(raw, f"{label} {key}")
    return prices


def read_observation(path: Path) -> dict[str, object]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must be a JSON object")
    for key in payload:
        if COST_KEY.search(key):
            raise ValueError(f"{path} contains a cost field {key}")
    if payload.get("readOnly") is not True or payload.get("writesPrices") is not False:
        raise ValueError(f"{path} must be a read-only observation")
    return payload


def read_catalog_seed(path: Path) -> dict[str, int]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict) or not isinstance(payload.get("products"), list):
        raise ValueError(f"{path} must be a catalog with products")
    prices: dict[str, int] = {}
    for row in payload["products"]:
        if not isinstance(row, dict) or not isinstance(row.get("ma"), str):
            raise ValueError(f"{path} has a product without a mã")
        ma = row["ma"]
        if MA_RE.fullmatch(ma) is None:
            raise ValueError(f"{path} has an invalid mã {ma!r}")
        if row.get("priceUsd") is None:
            continue
        prices[ma] = whole_dollars(row.get("priceUsd"), f"{path} {ma}")
    return prices


def read_readme_hub_table(text: str) -> dict[str, int]:
    prices: dict[str, int] = {}
    capturing = False
    for line in text.splitlines():
        if line.startswith("| Mã | USD |"):
            capturing = True
            continue
        if not capturing:
            continue
        if not line.startswith("|"):
            break
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) < 2 or MA_RE.fullmatch(cells[0]) is None:
            continue
        if re.fullmatch(r"\d+", cells[1]) is None:
            raise ValueError(f"README hub table has a non-dollar for {cells[0]}")
        prices[cells[0]] = int(cells[1])
    if not prices:
        raise ValueError("README hub table was not found")
    return prices


def read_preserve_live(path: Path) -> dict[str, int]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must be a JSON object")
    block = payload.get("color_preselect_pass")
    if not isinstance(block, dict):
        raise ValueError(f"{path} has no color_preselect_pass")
    return _price_map(block.get("preserve_live_prices"), f"{path} preserve_live_prices")


def read_catalog_usd_const(text: str) -> dict[str, int]:
    match = re.search(r"const CATALOG_USD = \{(.*?)\} as const;", text, re.S)
    if match is None:
        raise ValueError("CATALOG_USD was not found")
    prices: dict[str, int] = {}
    for ma, usd in re.findall(r"([A-Z][0-9]{2})\s*:\s*(\d+)", match.group(1)):
        prices[ma] = int(usd)
    if not prices:
        raise ValueError("CATALOG_USD has no mãs")
    return prices


def diff_prices(source: str, fixture: dict[str, int], live: dict[str, int]) -> tuple[Drift, ...]:
    rows: list[Drift] = []
    for ma in sorted(fixture):
        if ma not in live or fixture[ma] == live[ma]:
            continue
        rows.append(Drift(source, ma, fixture[ma], live[ma]))
    return tuple(rows)


def _s06_problems(label: str, prices: dict[str, int], *, required: bool) -> list[str]:
    if S06 not in prices:
        if required:
            return [f"{label} is missing S06; the lock is ${S06_USD}"]
        return []
    if prices[S06] != S06_USD:
        return [f"{label} S06 is ${prices[S06]}; the lock is ${S06_USD}"]
    return []


def compare(root: Path | None = None) -> Report:
    base = root or repo_root()
    observation = read_observation(base / "data" / "price-drift" / "observed-public-sell.json")
    observed_at = observation.get("observedAt")
    if not isinstance(observed_at, str) or not observed_at.strip():
        raise ValueError("observedAt must be set")
    live = _price_map(observation.get("liveUsd"), "liveUsd")
    intake = _price_map(observation.get("intakeSellUsd"), "intakeSellUsd")
    page_raw = observation.get("pageChecks")
    if not isinstance(page_raw, dict):
        raise ValueError("pageChecks must be an object")

    seed = read_catalog_seed(base / "sassy-closet-shop" / "data" / "products.json")
    readme = read_readme_hub_table((base / "sassy-closet-shop" / "README.md").read_text(encoding="utf-8"))
    preserve_paths = (
        base / "sassy-closet-shop" / "data" / "taobao_confirm_seed.json",
        base / "sassy-closet-shop" / "public" / "data" / "taobao_confirm_seed.json",
    )
    preserve_maps = [read_preserve_live(path) for path in preserve_paths]
    lock = read_catalog_usd_const(
        (base / "sassy-closet-shop" / "tests" / "boss-price-lock.test.ts").read_text(encoding="utf-8")
    )

    problems: list[str] = []
    if preserve_maps[0] != preserve_maps[1]:
        problems.append("preserve_live_prices copies disagree")
    preserve = preserve_maps[0]

    page_checks: list[tuple[str, str, int]] = []
    for url, raw in page_raw.items():
        if not isinstance(url, str) or "/m/" not in url:
            raise ValueError(f"page check URL is not a product page: {url!r}")
        ma = url.rstrip("/").rsplit("/", 1)[-1]
        if MA_RE.fullmatch(ma) is None:
            raise ValueError(f"page check URL has an invalid mã: {url}")
        usd = whole_dollars(raw, url)
        page_checks.append((url, ma, usd))
        if live.get(ma) != usd:
            problems.append(f"{url} shows ${usd} and the live observation for {ma} is ${live.get(ma)}")

    for source, fixture in (
        ("intake", intake),
        ("catalog-seed", seed),
        ("readme-hub-ten", readme),
        ("preserve-live", preserve),
        ("boss-price-lock", lock),
    ):
        for ma, usd in fixture.items():
            if ma not in live:
                problems.append(f"{source} {ma} is ${usd} and is not on the live observation")

    drifts: list[Drift] = []
    for source, fixture in (
        ("intake", intake),
        ("catalog-seed", seed),
        ("readme-hub-ten", readme),
        ("preserve-live", preserve),
        ("boss-price-lock", lock),
    ):
        drifts.extend(diff_prices(source, fixture, live))
    drifts.sort(key=lambda row: (SOURCE_ORDER.index(row.source), row.ma))

    s06_problems = [
        *_s06_problems("live", live, required=True),
        *_s06_problems("intake", intake, required=False),
        *_s06_problems("catalog-seed", seed, required=False),
        *_s06_problems("readme-hub-ten", readme, required=False),
        *_s06_problems("preserve-live", preserve, required=False),
        *_s06_problems("boss-price-lock", lock, required=False),
    ]
    matches = tuple(sorted((ma, usd) for ma, usd in intake.items() if live.get(ma) == usd))
    missing = tuple(sorted(ma for ma in live if ma not in seed))
    return Report(
        observed_at=observed_at,
        drifts=tuple(drifts),
        intake_matches=matches,
        s06_live=live.get(S06),
        s06_problems=tuple(s06_problems),
        problems=tuple(problems),
        seed_missing=missing,
        page_checks=tuple(page_checks),
    )


def _money(usd: int) -> str:
    return f"${usd}"


def _table(rows: tuple[Drift, ...] | list[Drift]) -> str:
    if not rows:
        return "No dollar differences.\n"
    lines = ["| Mã | Fixture | Live | Gap |", "| --- | ---: | ---: | ---: |"]
    for row in rows:
        lines.append(
            f"| {row.ma} | {_money(row.fixture_usd)} | {_money(row.live_usd)} | {_money(row.gap)} |"
        )
    return "\n".join(lines) + "\n"


def render(report: Report) -> str:
    by_source: dict[str, list[Drift]] = {source: [] for source in SOURCE_ORDER}
    for row in report.drifts:
        by_source[row.source].append(row)
    intake = by_source["intake"]
    biggest = sorted(intake, key=lambda row: row.gap, reverse=True)[:2]
    biggest_text = ", ".join(
        f"{row.ma} live {_money(row.live_usd)} vs intake {_money(row.fixture_usd)}" for row in biggest
    )
    match_text = ", ".join(f"{ma} {_money(usd)}" for ma, usd in report.intake_matches) or "none"
    pages = "\n".join(f"- `{url}` {ma} {_money(usd)}" for url, ma, usd in report.page_checks)
    problems = "\n".join(f"- {item}" for item in (*report.s06_problems, *report.problems))
    if not problems:
        problems = f"- S06 stays ${S06_USD} on the live observation. No checked fixture stores another S06 dollar."
    missing = ", ".join(report.seed_missing) or "none"
    return f"""# Public sell-price drift (draft)

Observed {report.observed_at}. Live dollars are the public catalog. Intake dollars are non-blank public `sell_usd` values. This file records the comparison. It does not change Blob, intake, Meta, or any fixture price.

S06 stays **$25**. The live observation is {_money(report.s06_live) if report.s06_live is not None else "missing"}.

## Boss confirm

Do not copy intake dollars onto the live site, and do not copy live dollars onto intake, until Boss picks a side. Largest intake gaps: {biggest_text or "none"}.

Intake sell already matches live for: {match_text}.

## Intake sell vs live

{_table(intake)}
## Catalog seed (`sassy-closet-shop/data/products.json`) vs live

{_table(by_source["catalog-seed"])}
## README hub-ten table vs live

{_table(by_source["readme-hub-ten"])}
## `preserve_live_prices` vs live

Both Taobao seed copies are read. Only the public dollar map is compared.

{_table(by_source["preserve-live"])}
## `CATALOG_USD` in the boss price lock vs live

{_table(by_source["boss-price-lock"])}
## S06 and other checks

{problems}

Live mãs with no catalog-seed row: {missing}.

Rendered pages checked against the same live dollars:

{pages}
"""


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Print public sell-price drift. Does not write prices.")
    parser.add_argument("--root", default="", help="Repo root. Defaults to this checkout.")
    args = parser.parse_args(argv)
    root = Path(args.root) if args.root else repo_root()
    report = compare(root)
    print(render(report), end="")
    return report.exit_code


if __name__ == "__main__":
    raise SystemExit(main())
