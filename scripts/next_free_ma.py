"""Count the next free mã for each letter from a fixture.

The fixture lists taken mãs and a held list. The next code for a letter is
the first number after the highest taken number, walking past held numbers.
Prices are copied through. A fixture that already prices S06 must say $25.

This module only reads the fixture path it is given. It does not write
intake, the on-disk held list, or a sell price.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from pathlib import Path

from held_policy import norm_ma

MAX_NUMBER = 999


@dataclass(frozen=True)
class FreeMaReport:
    next_by_letter: dict[str, str]
    held: tuple[str, ...]
    prices: dict[str, str]

    def as_json(self) -> dict[str, object]:
        return {
            "next": self.next_by_letter,
            "held": list(self.held),
            "prices": self.prices,
        }


def next_code(letter: str, taken: Iterable[str], held: Iterable[str]) -> str:
    """Next free mã for one letter. Held numbers are not chosen."""
    kind = _letter(letter)
    used = _numbers(kind, taken)
    blocked = _numbers(kind, held)
    number = max(used, default=0) + 1
    while number in used or number in blocked:
        number += 1
    if number > MAX_NUMBER:
        raise ValueError(f"no free {kind} mã at or below {MAX_NUMBER}")
    return _format(kind, number)


def count_next_free(
    mas: object,
    held: object,
    prices: object | None = None,
) -> FreeMaReport:
    """Next free mã per letter. Inputs are not mutated."""
    taken = _codes(mas, "mas", allow_duplicates=True)
    blocked = _codes(held, "held", allow_duplicates=False)
    echoed = _prices({} if prices is None else prices)
    letters = sorted({code[0] for code in (*taken, *blocked)})
    nxt = {letter: next_code(letter, taken, blocked) for letter in letters}
    return FreeMaReport(next_by_letter=nxt, held=tuple(blocked), prices=echoed)


def count_fixture(path: Path) -> dict[str, object]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("fixture must be a JSON object")
    if "mas" not in payload or "held" not in payload:
        raise ValueError("fixture needs mas and held")
    report = count_next_free(payload.get("mas"), payload.get("held"), payload.get("prices", {}))
    return report.as_json()


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Print the next free mã per letter from a fixture. Reads only.",
    )
    parser.add_argument("--fixture", required=True, help="JSON with mas, held, and optional prices.")
    args = parser.parse_args(argv)
    try:
        report = count_fixture(Path(args.fixture))
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(error, file=sys.stderr)
        return 2
    print(json.dumps(report, indent=2))
    return 0


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
    raw = norm_ma(item)
    if len(raw) < 3 or not ("A" <= raw[0] <= "Z") or not raw[1:].isdigit():
        raise ValueError(f"{label} has an invalid mã {item!r}")
    number = int(raw[1:])
    if number < 1 or number > MAX_NUMBER or len(raw[1:]) > 3:
        raise ValueError(f"{label} has an invalid mã {item!r}")
    return _format(raw[0], number)


def _numbers(letter: str, codes: Iterable[str]) -> set[int]:
    numbers: set[int] = set()
    for code in codes:
        parsed = _parse_ma(code, "mas")
        if parsed[0] == letter:
            numbers.add(int(parsed[1:]))
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
