"""Report-only intake ¥ checks.

Blank ¥, a garbled ¥ string, and an intake ¥ above a known public ¥ are
flags. flag_cost_drift flags a gap over 8% versus that public ¥.
The stored text is copied into the flag and is not rewritten.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal

CNY_RE = re.compile(r"^\d+(?:\.\d+)?$")
DRIFT_LIMIT = Decimal("0.08")


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
    drift: str | None = None

    def as_json(self) -> dict[str, str | None]:
        payload: dict[str, str | None] = {
            "ma": self.ma,
            "kind": self.kind,
            "stored": self.stored,
            "publicCny": self.public_cny,
        }
        if self.drift is not None:
            payload["drift"] = self.drift
        return payload


def format_cny(value: Decimal) -> str:
    text = format(value, "f")
    if "." in text:
        text = text.rstrip("0").rstrip(".")
    return text


def format_drift(ratio: Decimal) -> str:
    percent = (ratio * Decimal(100)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return f"{format_cny(percent)}%"


def flag_intake(rows: list[IntakeRow], public: dict[str, PublicCny] | None = None) -> list[IntakeFlag]:
    """Return flags. Leave every IntakeRow.cost_cny as it was passed in."""
    known = public or {}
    flags: list[IntakeFlag] = []
    for row in rows:
        code, stored, stripped = _cost_parts(row)
        problem = _cost_problem(code, stored, stripped)
        if problem is not None:
            flags.append(problem)
            continue
        listed = known.get(code)
        if listed is None or listed.state != "ok" or listed.value is None:
            continue
        if Decimal(stripped) > listed.value:
            flags.append(
                IntakeFlag(
                    code,
                    "above_public",
                    stored,
                    format_cny(listed.value),
                )
            )
    return flags


def flag_cost_drift(rows: list[IntakeRow], public: dict[str, PublicCny] | None = None) -> list[IntakeFlag]:
    """Flag blank ¥, garbled ¥, and a gap over 8%. Do not rewrite cost_cny."""
    known = public or {}
    flags: list[IntakeFlag] = []
    for row in rows:
        code, stored, stripped = _cost_parts(row)
        problem = _cost_problem(code, stored, stripped)
        if problem is not None:
            flags.append(problem)
            continue
        listed = known.get(code)
        if listed is None or listed.state != "ok" or listed.value is None:
            continue
        intake = Decimal(stripped)
        if listed.value == 0:
            if intake != 0:
                flags.append(IntakeFlag(code, "drift", stored, format_cny(listed.value), "over 8%"))
            continue
        ratio = abs(intake - listed.value) / listed.value
        if ratio > DRIFT_LIMIT:
            flags.append(
                IntakeFlag(
                    code,
                    "drift",
                    stored,
                    format_cny(listed.value),
                    format_drift(ratio),
                )
            )
    return flags


def _cost_parts(row: IntakeRow) -> tuple[str, str, str]:
    stored = "" if row.cost_cny is None else str(row.cost_cny)
    return row.ma.strip().upper(), stored, stored.strip()


def _cost_problem(code: str, stored: str, stripped: str) -> IntakeFlag | None:
    if stripped == "":
        return IntakeFlag(code, "blank_cny", stored)
    if CNY_RE.fullmatch(stripped) is None:
        return IntakeFlag(code, "garbled_cny", stored)
    return None
