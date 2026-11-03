"""Compare two held-list JSON fixtures.

Reports mãs added to heldIncomplete and mãs removed from it.
Reads the two fixture files only.
Does not write data/held.json, either fixture, Blob, the hub, or a sell price.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path

from held_policy import HeldPolicy, default_held_path, load_held_policy

S06 = "S06"


@dataclass(frozen=True)
class HeldDiff:
    added: tuple[str, ...]
    removed: tuple[str, ...]
    held: tuple[str, ...]
    never_added: tuple[str, ...]
    never_removed: tuple[str, ...]
    s06_on_held_before: bool
    s06_on_held_after: bool


def diff_held_lists(before: HeldPolicy, after: HeldPolicy) -> HeldDiff:
    """Describe held-list differences. Does not mutate either list."""
    before_held = set(before.held)
    after_held = set(after.held)
    before_never = set(before.never_list)
    after_never = set(after.never_list)
    return HeldDiff(
        added=tuple(sorted(after_held - before_held)),
        removed=tuple(sorted(before_held - after_held)),
        held=tuple(sorted(before_held & after_held)),
        never_added=tuple(sorted(after_never - before_never)),
        never_removed=tuple(sorted(before_never - after_never)),
        s06_on_held_before=S06 in before_held,
        s06_on_held_after=S06 in after_held,
    )


def diff_held_files(before: str | Path, after: str | Path) -> HeldDiff:
    return diff_held_lists(load_held_list(before), load_held_list(after))


def load_held_list(path: str | Path) -> HeldPolicy:
    fixture = _local_fixture(path)
    try:
        return load_held_policy(fixture)
    except json.JSONDecodeError as error:
        raise ValueError(f"{path} is not held-list JSON") from error


def report_json(report: HeldDiff) -> dict[str, object]:
    return {
        "added": list(report.added),
        "removed": list(report.removed),
        "held": list(report.held),
        "neverAdded": list(report.never_added),
        "neverRemoved": list(report.never_removed),
        "s06": {
            "onHeldBefore": report.s06_on_held_before,
            "onHeldAfter": report.s06_on_held_after,
        },
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Compare two held-list JSON fixtures and print added and removed mãs. "
            "Does not write."
        ),
    )
    parser.add_argument("--before", required=True, help="Earlier held-list fixture.")
    parser.add_argument("--after", required=True, help="Later held-list fixture.")
    args = parser.parse_args(argv)
    try:
        report = diff_held_files(args.before, args.after)
    except (OSError, ValueError) as error:
        print(error, file=sys.stderr)
        return 2
    print(json.dumps(report_json(report), indent=2))
    return 0


def _is_remote(path: str) -> bool:
    return "://" in path or path.startswith("http:") or path.startswith("https:")


def _local_fixture(path: str | Path) -> Path:
    if isinstance(path, str) and _is_remote(path):
        raise ValueError("held diff reads local held-list fixtures only")
    file = Path(path)
    if not file.is_file():
        raise ValueError(f"missing held-list fixture {path}")
    resolved = file.resolve()
    if resolved == default_held_path().resolve():
        raise ValueError("held diff reads fixtures only and does not read data/held.json")
    return resolved


if __name__ == "__main__":
    raise SystemExit(main())
