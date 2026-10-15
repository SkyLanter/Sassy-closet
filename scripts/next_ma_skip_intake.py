"""Next free mã per letter from a fixture.

Three lists are skipped: catalog mãs, a held list, and intake mãs that are
not in the catalog yet. The walk starts one past the highest catalog number
for that letter, then steps over held numbers and those intake numbers.

Prices are copied through. A fixture that prices S06 must say $25.

This module only reads the fixture path it is given. A live intake URL is
refused and is not read. It does not write intake, the on-disk held list,
or a sell price.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from pathlib import Path

MAX_NUMBER = 999
ROOT = Path(__file__).resolve().parents[1]
_HELD_FILE = (ROOT / "data" / "held.json").resolve()
_SHOP_DATA = (ROOT / "sassy-closet-shop" / "data").resolve()
_INTAKE_DATA = (ROOT / "sassy-closet" / "data").resolve()
_LIVE_INTAKE = "Live intake is not read. Pass a fixture file."
_REMOTE_KEYS = ("url", "intakeUrl", "intake_url", "catalogUrl", "catalog_url")


@dataclass(frozen=True)
class FreeMaReport:
    next_by_letter: dict[str, str]
    catalog: tuple[str, ...]
    held: tuple[str, ...]
    intake: tuple[str, ...]
    intake_not_in_catalog: tuple[str, ...]
    prices: dict[str, str]

    def as_json(self) -> dict[str, object]:
        return {
            "next": self.next_by_letter,
            "catalog": list(self.catalog),
            "held": list(self.held),
            "intake": list(self.intake),
            "intakeNotInCatalog": list(self.intake_not_in_catalog),
            "prices": dict(self.prices),
        }


def next_code(
    letter: str,
    catalog: Iterable[str],
    held: Iterable[str],
    intake: Iterable[str],
) -> str:
    """Next free mã for one letter. Held and unpublished intake numbers are not chosen."""
    kind = _letter(letter)
    catalog_codes = {_parse_ma(code, "catalog") for code in catalog}
    held_codes = {_parse_ma(code, "held") for code in held}
    intake_codes = {_parse_ma(code, "intake") for code in intake}
    unpublished = {code for code in intake_codes if code not in catalog_codes}
    used = _numbers(kind, catalog_codes)
    blocked = _numbers(kind, held_codes | unpublished)
    number = max(used, default=0) + 1
    while number in used or number in blocked:
        number += 1
    if number > MAX_NUMBER:
        raise ValueError(f"no free {kind} mã at or below {MAX_NUMBER}")
    return _format(kind, number)


def count_next_free(
    catalog: object,
    held: object,
    intake: object,
    prices: object | None = None,
) -> FreeMaReport:
    """Next free mã per letter. Inputs are not mutated."""
    catalog_codes = _codes(catalog, "catalog", allow_duplicates=True)
    held_codes = _codes(held, "held", allow_duplicates=False)
    intake_codes = _codes(intake, "intake", allow_duplicates=False)
    catalog_set = set(catalog_codes)
    unpublished = tuple(code for code in intake_codes if code not in catalog_set)
    echoed = _prices({} if prices is None else prices)
    letters = sorted({code[0] for code in (*catalog_codes, *held_codes, *intake_codes)})
    nxt = {
        letter: next_code(letter, catalog_codes, held_codes, intake_codes) for letter in letters
    }
    return FreeMaReport(
        next_by_letter=nxt,
        catalog=tuple(catalog_codes),
        held=tuple(held_codes),
        intake=tuple(intake_codes),
        intake_not_in_catalog=unpublished,
        prices=echoed,
    )


def count_fixture(path: Path) -> dict[str, object]:
    _refuse_live(path)
    payload = json.loads(path.read_text(encoding="utf-8"))
    if _remote_pointer(payload):
        raise ValueError(_LIVE_INTAKE)
    if not isinstance(payload, dict):
        raise ValueError("fixture must be a JSON object")
    for key in ("catalog", "held", "intake"):
        if key not in payload:
            raise ValueError("fixture needs catalog, held, and intake")
    report = count_next_free(
        payload.get("catalog"),
        payload.get("held"),
        payload.get("intake"),
        payload.get("prices", {}),
    )
    return report.as_json()


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Print the next free mã per letter from a fixture. Reads only.",
    )
    parser.add_argument(
        "--fixture",
        required=True,
        help="JSON with catalog, held, intake, and optional prices.",
    )
    args = parser.parse_args(argv)
    if _is_live_target(args.fixture):
        print(_LIVE_INTAKE, file=sys.stderr)
        return 2
    try:
        report = count_fixture(Path(args.fixture))
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(error, file=sys.stderr)
        return 2
    print(json.dumps(report, indent=2))
    return 0


def _refuse_live(path: Path) -> None:
    if _is_live_target(str(path)):
        raise ValueError(_LIVE_INTAKE)
    resolved = path.resolve(strict=False)
    refused = (
        resolved == _HELD_FILE
        or _is_inside(resolved, _SHOP_DATA)
        or _is_inside(resolved, _INTAKE_DATA)
    )
    if refused:
        raise ValueError("live reads are refused")


def _is_live_target(value: str) -> bool:
    text = value.strip().casefold()
    return "://" in text or text.startswith("//") or text.startswith("blob:") or text.startswith("http")


def _remote_pointer(payload: object) -> bool:
    if isinstance(payload, str):
        return _is_live_target(payload)
    if not isinstance(payload, dict):
        return False
    for key in ("intake", "catalog", "held", *_REMOTE_KEYS):
        value = payload.get(key)
        if isinstance(value, str) and _is_live_target(value):
            return True
    return False


def _is_inside(child: Path, parent: Path) -> bool:
    try:
        child.relative_to(parent)
    except ValueError:
        return False
    return True


def _letter(letter: str) -> str:
    if not isinstance(letter, str):
        raise ValueError(f"letter must be A-Z, got {letter!r}")
    kind = letter.strip().upper()
    if len(kind) != 1 or not ("A" <= kind <= "Z"):
        raise ValueError(f"letter must be A-Z, got {letter!r}")
    return kind


def _codes(value: object, label: str, *, allow_duplicates: bool) -> list[str]:
    if not isinstance(value, list):
        raise ValueError(f"{label} must be a list of mãs")
    codes: list[str] = []
    seen: set[str] = set()
    for item in value:
        code = _parse_ma(item, label)
        if code in seen:
            if not allow_duplicates:
                raise ValueError(f"{label} repeats {code}")
            continue
        seen.add(code)
        codes.append(code)
    return codes


def _parse_ma(item: object, label: str) -> str:
    if not isinstance(item, str):
        raise ValueError(f"{label} contains a non-string mã")
    raw = item.strip().upper()
    if len(raw) < 2 or not ("A" <= raw[0] <= "Z") or not raw[1:].isdigit():
        raise ValueError(f"{label} has an invalid mã {item!r}")
    number = int(raw[1:])
    if number < 1 or number > MAX_NUMBER or len(raw[1:]) > 3:
        raise ValueError(f"{label} has an invalid mã {item!r}")
    return _format(raw[0], number)


def _numbers(letter: str, codes: Iterable[str]) -> set[int]:
    numbers: set[int] = set()
    for code in codes:
        if code[0] == letter:
            numbers.add(int(code[1:]))
    return numbers


def _format(letter: str, number: int) -> str:
    if number < 100:
        return f"{letter}{number:02d}"
    return f"{letter}{number}"


def _prices(value: object) -> dict[str, str]:
    if not isinstance(value, dict):
        raise ValueError("prices must be an object of mã to dollar")
    echoed: dict[str, str] = {}
    for key, raw in value.items():
        code = _parse_ma(key, "prices")
        if code in echoed:
            raise ValueError(f"prices repeats {code}")
        if not isinstance(raw, str):
            raise ValueError(f"prices {code} must be a dollar string")
        text = raw.strip()
        if code == "S06" and not _is_twenty_five(text):
            raise ValueError("S06 stays $25")
        echoed[code] = text
    return echoed


def _is_twenty_five(text: str) -> bool:
    try:
        return Decimal(text) == Decimal("25")
    except InvalidOperation:
        return False


if __name__ == "__main__":
    raise SystemExit(main())
