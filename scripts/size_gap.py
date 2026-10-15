"""Flag a size list that skips a clothing step.

S and L with no M is a skip. The steps are the existing intake letters
2XS, XS, S, M, L, XL, 2XL. A single size, a shoe number, and free with
a measurement stay quiet. The stored list is copied into the flag. The
missing step is named and is not written back into the list.

This module only reads a fixture passed on the command line. It does
not write catalog rows.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

Source = Literal["catalog", "intake"]
SOURCES: tuple[Source, ...] = ("catalog", "intake")

# Same letters as excel-kit INTAKE_CLOTHING_SIZES. No extra step is added.
CLOTHING_STEPS: tuple[str, ...] = ("2XS", "XS", "S", "M", "L", "XL", "2XL")
# Spellings the shop already reads as those steps. Not new steps.
_STEP_ALIAS = {"XXS": "2XS", "XXL": "2XL", "3XL": "2XL"}
_STEP_INDEX = {step: index for index, step in enumerate(CLOTHING_STEPS)}
_LETTER = re.compile(r"(?<![A-Z0-9])(2XS|XXS|3XL|XXL|2XL|XS|XL|S|M|L)(?![A-Z0-9])")


@dataclass(frozen=True)
class SizeList:
    ma: str
    source: Source
    stored: str
    parts: tuple[str, ...]


@dataclass(frozen=True)
class SizeGapFlag:
    ma: str
    source: Source
    kind: str
    stored: str
    skipped: str

    def as_json(self) -> dict[str, str]:
        return {
            "ma": self.ma,
            "source": self.source,
            "kind": self.kind,
            "stored": self.stored,
            "skipped": self.skipped,
        }


def flag_size_lists(rows: list[SizeList]) -> list[SizeGapFlag]:
    """Return flags. Leave every SizeList.parts and stored text as passed in."""
    flags: list[SizeGapFlag] = []
    for row in rows:
        _check_source(row.source)
        missing = skipped_steps(row.parts)
        if not missing:
            continue
        flags.append(
            SizeGapFlag(
                row.ma.strip().upper(),
                row.source,
                "skipped_step",
                row.stored,
                ", ".join(missing),
            )
        )
    return flags


def skipped_steps(parts: tuple[str, ...]) -> list[str]:
    """Letters on the existing ladder that sit between the sizes in parts."""
    present: set[int] = set()
    for part in parts:
        for step in _letters(part):
            present.add(_STEP_INDEX[step])
    if len(present) < 2:
        return []
    ordered = sorted(present)
    missing: list[str] = []
    for left, right in zip(ordered, ordered[1:]):
        if right - left > 1:
            missing.extend(CLOTHING_STEPS[left + 1 : right])
    return missing


def rows_from_fixture(payload: object) -> list[SizeList]:
    if not isinstance(payload, dict):
        raise ValueError("fixture must be an object with catalog and intake lists")
    extra = sorted(set(payload) - set(SOURCES))
    if extra:
        raise ValueError(f"fixture may only contain catalog and intake, found {extra}")
    missing = [source for source in SOURCES if source not in payload]
    if missing:
        raise ValueError(f"fixture needs catalog and intake lists, missing {missing}")
    rows: list[SizeList] = []
    for source in SOURCES:
        rows.extend(_rows(payload[source], source))
    return rows


def load_fixture(path: Path) -> list[SizeList]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return rows_from_fixture(payload)


def report_json(flags: list[SizeGapFlag]) -> str:
    body = {"flags": [flag.as_json() for flag in flags]}
    return json.dumps(body, ensure_ascii=False, indent=2) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Report a size list that skips a clothing step. Reads a fixture only."
    )
    parser.add_argument("--fixture", help="Fixture JSON with catalog and intake size lists.")
    args = parser.parse_args(argv)
    if not args.fixture:
        print(
            "Pass --fixture. This check reads a fixture only and does not open the live catalog.",
            file=sys.stderr,
        )
        return 2
    path = Path(args.fixture)
    try:
        flags = flag_size_lists(load_fixture(path))
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(str(error), file=sys.stderr)
        return 2
    sys.stdout.write(report_json(flags))
    return 0


def _check_source(source: str) -> Source:
    if source == "catalog":
        return "catalog"
    if source == "intake":
        return "intake"
    raise ValueError(f"size source must be catalog or intake, found {source!r}")


def _letters(text: str) -> list[str]:
    found: list[str] = []
    for match in _LETTER.finditer(text.upper()):
        raw = match.group(1)
        found.append(_STEP_ALIAS.get(raw, raw))
    return found


def _rows(value: object, source: Source) -> list[SizeList]:
    if not isinstance(value, list):
        raise ValueError(f"{source} must be a list")
    rows: list[SizeList] = []
    for item in value:
        ma = item.get("ma") if isinstance(item, dict) else None
        if not isinstance(ma, str) or ma.strip() == "":
            raise ValueError(f"{source} row needs a mã")
        if isinstance(item, dict) and "size" in item and "sizes" in item:
            raise ValueError(f"{source} row {ma} has both size and sizes")
        if isinstance(item, dict) and "size" in item:
            stored, parts = _size_text(item.get("size"), source)
            rows.append(SizeList(ma, source, stored, parts))
            continue
        if isinstance(item, dict) and "sizes" in item:
            stored, parts = _size_list(item.get("sizes"), ma, source)
            rows.append(SizeList(ma, source, stored, parts))
            continue
        rows.append(SizeList(ma, source, "", ()))
    return rows


def _size_text(raw: object, source: Source) -> tuple[str, tuple[str, ...]]:
    if raw is None:
        return "", ()
    if isinstance(raw, str):
        return raw, (raw,)
    raise ValueError(f"{source} size text must be a string or null")


def _size_list(raw: object, ma: str, source: Source) -> tuple[str, tuple[str, ...]]:
    if not isinstance(raw, list) or not all(isinstance(part, str) for part in raw):
        raise ValueError(f"{source} sizes for {ma} must be a list of strings")
    parts = tuple(raw)
    return ", ".join(parts), parts


if __name__ == "__main__":
    raise SystemExit(main())
