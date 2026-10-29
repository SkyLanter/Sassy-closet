"""Report-only intake ¥ checks.

Blank ¥, a garbled ¥ string, and an intake ¥ above a known public ¥ are
flags. The stored text is copied into the flag and is not rewritten.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from decimal import Decimal
from held_policy import norm_ma

from held_policy import norm_ma

CNY_RE = re.compile(r"^\d+(?:\.\d+)?$")


@dataclass(frozen=True)
class IntakeRow:
    ma: str
    cost_cny: str | None
    sell_usd: str | None = None
    link: str | None = None
    sizes: tuple[str, ...] | None = None
    photo_count: int | None = None


@dataclass(frozen=True)
class PublicCny:
    state: str
    value: Decimal | None = None
    detail: str = ""


@dataclass(frozen=True)
class IntakeFlag:
    ma: str
    kind: str
    stored: str
    public_cny: str | None = None

    def as_json(self) -> dict[str, str | None]:
        return {
            "ma": self.ma,
            "kind": self.kind,
            "stored": self.stored,
            "publicCny": self.public_cny,
        }


def flag_intake(rows: list[IntakeRow], public: dict[str, PublicCny] | None = None) -> list[IntakeFlag]:
    """Return flags. Leave every IntakeRow.cost_cny as it was passed in."""
    known = public or {}
    flags: list[IntakeFlag] = []
    for row in rows:
        stored = "" if row.cost_cny is None else str(row.cost_cny)
        stripped = stored.strip()
        code = norm_ma(row.ma)
        if stripped == "":
            flags.append(IntakeFlag(code, "blank_cny", stored))
            continue
        if CNY_RE.fullmatch(stripped) is None:
            flags.append(IntakeFlag(code, "garbled_cny", stored))
            continue
        listed = known.get(code)
        if listed is None or listed.state != "ok" or listed.value is None or not listed.value.is_finite():
            continue
        if Decimal(stripped) > listed.value:
            flags.append(
                IntakeFlag(
                    code,
                    "above_public",
                    stored,
                    _decimal_text(listed.value),
                )
            )
    return flags


def _decimal_text(value: Decimal) -> str:
    text = format(value, "f")
    if "." in text:
        text = text.rstrip("0").rstrip(".")
    return text
