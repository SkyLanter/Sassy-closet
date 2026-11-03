"""Load the single held-mã source at data/held.json.

Callers must not keep a second list. This module does not write intake,
Blob, the hub, or a sell price.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path

MA_RE = re.compile(r"^[A-Z][0-9]{2}$")


_SPELLING = re.compile(r"^([A-Z])(\d+)$")


def norm_ma(value: object) -> str:
    """Canonical mã key, same as ma.ts canonicalMaSpelling.

    Trimmed, upper-cased, zero padding collapsed: ' k03 ', 'K003', 'k3' -> 'K03';
    'A100' stays. Non-mã text is returned trimmed + upper-cased; None -> ''.
    """
    code = "" if value is None else str(value).strip().upper()
    m = _SPELLING.match(code)
    return f"{m.group(1)}{int(m.group(2)):02d}" if m else code


@dataclass(frozen=True)
class HeldPolicy:
    held: tuple[str, ...]
    never_list: tuple[str, ...]

    def skip_reason(self, ma: str) -> str | None:
        code = norm_ma(ma)
        if code in self._held:
            return "held"
        if code in self._never:
            return "never-list"
        return None

    @property
    def _held(self) -> frozenset[str]:
        return frozenset(self.held)

    @property
    def _never(self) -> frozenset[str]:
        return frozenset(self.never_list)


def default_held_path() -> Path:
    return Path(__file__).resolve().parents[1] / "data" / "held.json"


def load_held_policy(path: Path | None = None) -> HeldPolicy:
    file = path or default_held_path()
    return policy_from_mapping(json.loads(file.read_text(encoding="utf-8")), source=str(file))


def policy_from_mapping(payload: object, *, source: str = "held policy") -> HeldPolicy:
    """Read a held policy object already in memory. Does not write a file."""
    if not isinstance(payload, dict):
        raise ValueError(f"{source} must be a JSON object")
    held = _codes(payload.get("heldIncomplete"), "heldIncomplete")
    never = _codes(payload.get("neverList"), "neverList", allow_empty=True)
    overlap = sorted(set(held) & set(never))
    if overlap:
        raise ValueError(f"{source} lists {overlap} in both heldIncomplete and neverList")
    return HeldPolicy(held=tuple(held), never_list=tuple(never))


def _codes(value: object, label: str, *, allow_empty: bool = False) -> list[str]:
    if not isinstance(value, list):
        raise ValueError(f"{label} must be a list of mãs")
    if not value and not allow_empty:
        raise ValueError(f"{label} must be a non-empty list of mãs")
    codes: list[str] = []
    seen: set[str] = set()
    for item in value:
        if not isinstance(item, str):
            raise ValueError(f"{label} contains a non-string mã")
        code = norm_ma(item)
        if not MA_RE.fullmatch(code):
            raise ValueError(f"{label} has an invalid mã {item!r}")
        if code in seen:
            raise ValueError(f"{label} repeats {code}")
        seen.add(code)
        codes.append(code)
    return codes
