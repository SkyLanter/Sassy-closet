"""Dry-run pickup decisions. Nothing here publishes or writes held.json."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation

from autolist import listing_quote
from held_policy import HeldPolicy

S06_LOCK = 25


@dataclass(frozen=True)
class PickupEvent:
    ma: str
    via: str
    action: str
    cost_cny: str
    landed_usd: str | None
    sell_usd: str | None
    sizes: tuple[str, ...]
    photo_count: int | None
    public_cny: Decimal | None
    taobao_state: str
    boss_approved: bool
    already_listed: bool
    listed_sell_usd: str | None
    reused: bool


@dataclass(frozen=True)
class PickupDecision:
    ma: str
    via: str
    action: str
    held: bool
    live: bool
    publish: bool
    reprice: bool
    quoted_usd: int | None
    flags: tuple[str, ...]
    stored_cny: str
    detail: str

    @property
    def blocks_live(self) -> bool:
        if self.held:
            return True
        return any(
            flag in {"never_list", "duplicate", "reused", "s06_lock", "no_reprice"}
            for flag in self.flags
        )

    def as_json(self) -> dict[str, object]:
        return {
            "ma": self.ma,
            "via": self.via,
            "action": self.action,
            "held": self.held,
            "live": self.live,
            "publish": self.publish,
            "reprice": self.reprice,
            "quotedUsd": self.quoted_usd,
            "flags": list(self.flags),
            "storedCny": self.stored_cny,
            "detail": self.detail,
        }


def plan_pickups(events: list[PickupEvent], policy: HeldPolicy) -> list[PickupDecision]:
    """Quote, hold, or block. live and publish stay false. Stored ¥ is copied."""
    counts: dict[str, int] = {}
    codes = [event.ma.strip().upper() for event in events]
    for code in codes:
        counts[code] = counts.get(code, 0) + 1
    decisions: list[PickupDecision] = []
    for event, code in zip(events, codes, strict=True):
        if event.reused or counts[code] > 1:
            flag = "reused" if event.reused else "duplicate"
            decisions.append(_blocked(event, code, (flag,), "not published"))
            continue
        reason = policy.skip_reason(code)
        if reason == "never-list":
            decisions.append(_blocked(event, code, ("never_list",), "Q02 stays unlisted"))
            continue
        if reason == "held":
            decisions.append(
                _blocked(event, code, ("held",), "held mã stays off live", held=True)
            )
            continue
        if code == "S06":
            decisions.append(_s06(event, code))
            continue
        if event.already_listed:
            decisions.append(_listed_edit(event, code))
            continue
        missing = _missing_taobao(event)
        if missing:
            decisions.append(
                _decision(
                    event,
                    code,
                    held=True,
                    quoted=None,
                    flags=tuple(missing),
                    reprice=False,
                    detail="incomplete Taobao; not quoted live",
                )
            )
            continue
        quote = listing_quote(code, event.landed_usd, policy)
        if not event.boss_approved:
            decisions.append(
                _decision(
                    event,
                    code,
                    held=True,
                    quoted=quote.sell_usd,
                    flags=("boss_approval",),
                    reprice=False,
                    detail="no Boss yes; quoted and held; not live",
                )
            )
            continue
        decisions.append(
            _decision(
                event,
                code,
                held=False,
                quoted=quote.sell_usd,
                flags=(),
                reprice=False,
                detail="Boss approved; dry-run does not publish",
            )
        )
    return decisions


def events_from_json(value: object) -> list[PickupEvent]:
    if value is None:
        return []
    if not isinstance(value, list):
        raise ValueError("fixture pickup must be a list")
    events: list[PickupEvent] = []
    for item in value:
        if not isinstance(item, dict) or not isinstance(item.get("ma"), str):
            raise ValueError("fixture pickup row needs a mã")
        sizes_raw = item.get("sizes", [])
        if not isinstance(sizes_raw, list) or not all(isinstance(part, str) for part in sizes_raw):
            raise ValueError("fixture pickup sizes must be a list of strings")
        photos = item.get("photo_count")
        photo_count = None if photos is None else int(photos)
        events.append(
            PickupEvent(
                ma=item["ma"],
                via=str(item.get("via", "webhook")),
                action=str(item.get("action", "create")),
                cost_cny="" if item.get("cost_cny") is None else str(item.get("cost_cny")),
                landed_usd=None if item.get("landed_usd") is None else str(item.get("landed_usd")),
                sell_usd=None if item.get("sell_usd") is None else str(item.get("sell_usd")),
                sizes=tuple(sizes_raw),
                photo_count=photo_count,
                public_cny=_decimal_or_none(item.get("public_cny")),
                taobao_state=str(item.get("taobao_state", "ok")),
                boss_approved=bool(item.get("boss_approved", False)),
                already_listed=bool(item.get("already_listed", False)),
                listed_sell_usd=(
                    None if item.get("listed_sell_usd") is None else str(item.get("listed_sell_usd"))
                ),
                reused=bool(item.get("reused", False)),
            )
        )
    return events


def _missing_taobao(event: PickupEvent) -> list[str]:
    missing: list[str] = []
    if not event.sizes:
        missing.append("missing_size")
    if event.photo_count is None or event.photo_count < 1:
        missing.append("missing_photos")
    if event.taobao_state != "skip" and event.public_cny is None:
        missing.append("missing_yen")
    return missing


def _s06(event: PickupEvent, code: str) -> PickupDecision:
    raw = "" if event.sell_usd is None else event.sell_usd.strip()
    if raw and _whole_dollars(event.sell_usd) != S06_LOCK:
        return _blocked(event, code, ("s06_lock",), "S06 stays $25")
    return _decision(
        event,
        code,
        held=False,
        quoted=S06_LOCK,
        flags=(),
        reprice=False,
        detail="S06 stays $25",
    )


def _listed_edit(event: PickupEvent, code: str) -> PickupDecision:
    raw = "" if event.sell_usd is None else event.sell_usd.strip()
    if raw:
        new_sell = _whole_dollars(event.sell_usd)
        listed = _whole_dollars(event.listed_sell_usd)
        if new_sell is None or new_sell != listed:
            return _blocked(event, code, ("no_reprice",), "listed sell is not replaced")
    return _decision(
        event,
        code,
        held=False,
        quoted=None,
        flags=(),
        reprice=False,
        detail="edit after listing does not publish a new dollar",
    )


def _blocked(
    event: PickupEvent,
    code: str,
    flags: tuple[str, ...],
    detail: str,
    held: bool = False,
) -> PickupDecision:
    return _decision(event, code, held=held, quoted=None, flags=flags, reprice=False, detail=detail)


def _decision(
    event: PickupEvent,
    code: str,
    *,
    held: bool,
    quoted: int | None,
    flags: tuple[str, ...],
    reprice: bool,
    detail: str,
) -> PickupDecision:
    return PickupDecision(
        ma=code,
        via=event.via,
        action=event.action,
        held=held,
        live=False,
        publish=False,
        reprice=reprice,
        quoted_usd=quoted,
        flags=flags,
        stored_cny=event.cost_cny,
        detail=detail,
    )


def _whole_dollars(value: str | None) -> int | None:
    if value is None:
        return None
    text = value.strip().replace("$", "").replace(",", "")
    if text == "":
        return None
    try:
        number = Decimal(text)
    except (InvalidOperation, ValueError):
        return None
    integral = number.to_integral_value()
    if number != integral:
        return None
    return int(integral)


def _decimal_or_none(value: object) -> Decimal | None:
    if value is None or value == "":
        return None
    return Decimal(str(value))
