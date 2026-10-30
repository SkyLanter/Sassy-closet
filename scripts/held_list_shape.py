"""Flag a held-list fixture entry that is not one letter plus two digits.

Reads a held-list fixture and prints a JSON report.
Does not remove the entry. Does not write the fixture, data/held.json, Blob, the hub, or a sell price.
S06 stays off the held list.
Exit 0 when every entry matches, 1 when an entry is flagged, and 2 when a fixture is refused.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path

from held_policy import default_held_path

S06 = "S06"
KIND = "held_shape"
SHAPE_RE = re.compile(r"^[A-Za-z][0-9]{2}$")
SHOP_CATALOG_NAMES = frozenset({"products.json", "catalog.v1.json"})


@dataclass(frozen=True)
class ShapeFlag:
    entry: str
    list_name: str

    def as_json(self) -> dict[str, str]:
        return {"entry": self.entry, "kind": KIND, "list": self.list_name}


@dataclass(frozen=True)
class HeldShapeReport:
    held: tuple[str, ...]
    never: tuple[str, ...]
    flags: tuple[ShapeFlag, ...]

    def as_json(self) -> dict[str, object]:
        return {
            "readOnly": True,
            "heldIncomplete": list(self.held),
            "neverList": list(self.never),
            "flags": [flag.as_json() for flag in self.flags],
            "s06": {"onHeldList": False},
            "writes": [],
        }


def flag_held_entries(held: list[str], never: list[str]) -> HeldShapeReport:
    """Return shape flags. The stored strings stay in both lists."""
    for entry in (*held, *never):
        if entry.strip().upper() == S06:
            raise ValueError("S06 stays off the held list")
    _reject_repeats(held, "heldIncomplete")
    _reject_repeats(never, "neverList")
    _reject_overlap(held, never)
    flags = _shape_flags(held, "heldIncomplete") + _shape_flags(never, "neverList")
    return HeldShapeReport(held=tuple(held), never=tuple(never), flags=tuple(flags))


def flag_file(path: str | Path) -> HeldShapeReport:
    held, never = load_held_fixture(path)
    return flag_held_entries(held, never)


def parse_held(payload: object) -> tuple[list[str], list[str]]:
    if not isinstance(payload, dict):
        raise ValueError("held-list fixture must be a JSON object")
    held = _strings(payload.get("heldIncomplete"), "heldIncomplete")
    never = _strings(payload.get("neverList"), "neverList")
    return held, never


def load_held_fixture(path: str | Path) -> tuple[list[str], list[str]]:
    fixture = _local_fixture(path)
    try:
        payload = json.loads(fixture.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise ValueError(f"{path} is not held-list JSON") from error
    return parse_held(payload)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Flag a held-list fixture entry that is not one letter plus two digits. "
            "Does not remove the entry. Does not write."
        ),
    )
    parser.add_argument("--held", required=True, help="Held-list JSON fixture.")
    args = parser.parse_args(argv)
    try:
        report = flag_file(args.held)
    except (OSError, ValueError) as error:
        print(str(error), file=sys.stderr)
        return 2
    print(json.dumps(report.as_json(), indent=2))
    return 1 if report.flags else 0


def _shape_flags(entries: list[str], list_name: str) -> list[ShapeFlag]:
    flags: list[ShapeFlag] = []
    for entry in entries:
        if _code(entry) is None:
            flags.append(ShapeFlag(entry, list_name))
    return flags


def _code(entry: str) -> str | None:
    stripped = entry.strip()
    if SHAPE_RE.fullmatch(stripped) is None:
        return None
    return stripped.upper()


def _reject_repeats(entries: list[str], label: str) -> None:
    seen: set[str] = set()
    for entry in entries:
        code = _code(entry)
        if code is None:
            continue
        if code in seen:
            raise ValueError(f"{label} repeats {code}")
        seen.add(code)


def _reject_overlap(held: list[str], never: list[str]) -> None:
    held_codes = {code for entry in held if (code := _code(entry)) is not None}
    never_codes = {code for entry in never if (code := _code(entry)) is not None}
    both = sorted(held_codes & never_codes)
    if both:
        raise ValueError(f"lists {both} in both heldIncomplete and neverList")


def _strings(value: object, label: str) -> list[str]:
    if not isinstance(value, list):
        raise ValueError(f"{label} must be a list")
    entries: list[str] = []
    for item in value:
        if not isinstance(item, str):
            raise ValueError(f"{label} contains a non-string entry")
        entries.append(item)
    return entries


def _local_fixture(path: str | Path) -> Path:
    if _is_remote(path):
        raise ValueError("held shape checks read local fixtures only")
    file = Path(path)
    reason = _refuse_path(file)
    if reason:
        raise ValueError(reason)
    if not file.is_file():
        raise ValueError(f"missing held-list fixture {path}")
    resolved = file.resolve()
    reason = _refuse_path(resolved)
    if reason:
        raise ValueError(reason)
    return resolved


def _refuse_path(path: Path) -> str | None:
    if path.name.casefold() in SHOP_CATALOG_NAMES:
        return "held shape checks read a held-list fixture. Shop catalog files are not read."
    if _names_live_held(path):
        return "held shape checks read fixtures only and do not read data/held.json"
    if _under_shop_data(path):
        return "held shape checks read a held-list fixture. Shop files are not read."
    return None


def _names_live_held(path: Path) -> bool:
    if path.name.casefold() != "held.json":
        return False
    if path.parent.name.casefold() == "data":
        return True
    try:
        return path.resolve() == default_held_path().resolve()
    except OSError:
        return False


def _under_shop_data(path: Path) -> bool:
    try:
        resolved = path.expanduser().resolve()
    except OSError:
        return False
    repo = Path(__file__).resolve().parents[1]
    folders = (
        repo / "data",
        repo / "sassy-closet" / "data",
        repo / "sassy-closet-shop" / "data",
    )
    for folder in folders:
        root = folder.resolve()
        if resolved == root or root in resolved.parents:
            return True
    return False


def _is_remote(path: str | Path) -> bool:
    text = str(path).strip()
    return "://" in text or text.startswith("//") or text.startswith("http:") or text.startswith("https:")


if __name__ == "__main__":
    raise SystemExit(main())
