#!/usr/bin/env python3
"""Print the held mãs the read-only shop gates must see as 404, space separated.

The one source is data/held.json (heldIncomplete + neverList, plus Q02, which
stays off sell). HELD_MAS overrides it for a test or a one-off check; entries
are canonicalised with held_policy.norm_ma, the same key every other reader
uses, and de-duplicated in the order given.

Read-only: this prints a list and never writes a file, a price or a held row.
Exit 0 with the list, 1 when the list cannot be built.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from held_policy import default_held_path, norm_ma  # noqa: E402

OFF_SELL_ALWAYS = ("Q02",)


def held_mas(override: str | None = None, path: Path | None = None) -> list[str]:
    """Canonical held mãs: the gate override, else the shared held list plus Q02."""
    raw = (override or "").split()
    if not raw:
        data = json.loads((path or default_held_path()).read_text(encoding="utf-8"))
        raw = list(data.get("heldIncomplete", [])) + list(data.get("neverList", []))
        raw += list(OFF_SELL_ALWAYS)
    codes: list[str] = []
    for item in raw:
        code = norm_ma(item)
        if code and code not in codes:
            codes.append(code)
    return codes


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    path = Path(args[0]) if args else None
    try:
        codes = held_mas(os.environ.get("HELD_MAS"), path)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"held_mas: {error}", file=sys.stderr)
        return 1
    print(" ".join(codes))
    return 0


if __name__ == "__main__":
    sys.exit(main())
