#!/usr/bin/env python3
"""Print held mãs for the read-only browser smoke. Does not write held.json."""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parent
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from held_policy import norm_ma

ROOT = Path(__file__).resolve().parents[1]
HELD_PATH = ROOT / "data" / "held.json"


def codes_from_doc(doc: object, override: str = "") -> list[str]:
    if override.strip():
        raw = override.split()
    else:
        if not isinstance(doc, dict):
            raise ValueError("held file is not an object")
        raw = []
        for key in ("heldIncomplete", "neverList"):
            if key not in doc:
                continue
            value = doc[key]
            if not isinstance(value, list):
                raise ValueError(f"{key} is not a list")
            raw.extend(value)
        raw.append("Q02")
    out: list[str] = []
    for item in raw:
        code = norm_ma(item)
        if code and code not in out:
            out.append(code)
    return out


def main() -> int:
    override = os.environ.get("HELD_MAS", "")
    try:
        doc = None
        if not override.strip():
            doc = json.loads(HELD_PATH.read_text(encoding="utf-8"))
        print(" ".join(codes_from_doc(doc, override)))
    except (OSError, json.JSONDecodeError, ValueError) as err:
        print(f"held list: {err}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
