"""Flag catalog and intake size text that has no number.

A blank size and any size text with no digit are flags. The word free
with no measurement is one of those. A measurement such as 80cm or a
shoe number keeps the row quiet. The stored text is copied into the
flag and is not replaced with a guessed size.

This module only reads a fixture passed on the command line. It does
not write catalog rows.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

Source = Literal["catalog", "intake"]
SOURCES: tuple[Source, ...] = ("catalog", "intake")


@dataclass(frozen=True)
class SizeText:
    ma: str
    source: Source
    size_text: str | None


@dataclass(frozen=True)
class SizeFlag:
    ma: str
    source: Source
    kind: str
    stored: str

    def as_json(self) -> dict[str, str]:
        return {
            "ma": self.ma,
            "source": self.source,
            "kind": self.kind,
            "stored": self.stored,
        }


def flag_sizes(rows: list[SizeText]) -> list[SizeFlag]:
    """Return flags. Leave every SizeText.size_text as it was passed in."""
    flags: list[SizeFlag] = []
    for row in rows:
        _check_source(row.source)
        stored = "" if row.size_text is None else row.size_text
        code = row.ma.strip().upper()
        if stored.strip() == "":
            flags.append(SizeFlag(code, row.source, "blank_size", stored))
            continue
        if not _has_digit(stored):
            flags.append(SizeFlag(code, row.source, "no_number", stored))
    return flags


def rows_from_fixture(payload: object) -> list[SizeText]:
    if not isinstance(payload, dict):
        raise ValueError("fixture must be an object with catalog and intake lists")
    extra = sorted(set(payload) - set(SOURCES))
    if extra:
        raise ValueError(f"fixture may only contain catalog and intake, found {extra}")
    missing = [source for source in SOURCES if source not in payload]
    if missing:
        raise ValueError(f"fixture needs catalog and intake lists, missing {missing}")
    rows: list[SizeText] = []
    for source in SOURCES:
        rows.extend(_rows(payload[source], source))
    return rows


def load_fixture(path: Path) -> list[SizeText]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return rows_from_fixture(payload)


def report_json(flags: list[SizeFlag]) -> str:
    body = {"flags": [flag.as_json() for flag in flags]}
    return json.dumps(body, ensure_ascii=False, indent=2) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Report catalog and intake size text that has no number. Reads a fixture only."
    )
    parser.add_argument("--fixture", help="Fixture JSON with catalog and intake size text.")
    args = parser.parse_args(argv)
    if not args.fixture:
        print(
            "Pass --fixture. This check reads a fixture only and does not open the live catalog.",
            file=sys.stderr,
        )
        return 2
    path = Path(args.fixture)
    try:
        flags = flag_sizes(load_fixture(path))
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


def _has_digit(text: str) -> bool:
    return any(char.isdecimal() for char in text)


def _rows(value: object, source: Source) -> list[SizeText]:
    if not isinstance(value, list):
        raise ValueError(f"{source} must be a list")
    rows: list[SizeText] = []
    for item in value:
        ma = item.get("ma") if isinstance(item, dict) else None
        if not isinstance(ma, str) or ma.strip() == "":
            raise ValueError(f"{source} row needs a mã")
        if "size" in item and "sizes" in item:
            raise ValueError(f"{source} row {ma} has both size and sizes")
        if "size" in item:
            rows.append(SizeText(ma, source, _size_text(item.get("size"), source)))
            continue
        if "sizes" in item:
            rows.extend(_size_list(item.get("sizes"), ma, source))
            continue
        rows.append(SizeText(ma, source, None))
    return rows


def _size_text(raw: object, source: Source) -> str | None:
    if raw is None:
        return None
    if isinstance(raw, str):
        return raw
    raise ValueError(f"{source} size text must be a string or null")


def _size_list(raw: object, ma: str, source: Source) -> list[SizeText]:
    if not isinstance(raw, list) or not all(isinstance(part, str) for part in raw):
        raise ValueError(f"{source} sizes for {ma} must be a list of strings")
    if len(raw) == 0:
        return [SizeText(ma, source, "")]
    return [SizeText(ma, source, part) for part in raw]


if __name__ == "__main__":
    raise SystemExit(main())
