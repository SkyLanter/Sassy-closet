"""Read-only desk status.

Prints intake count, catalog count, held count, open pull-request numbers,
freshness, and what is waiting on Boss. Sources are fixture files or
data/held.json. This module does not write Blob, intake, Meta, or
data/held.json, and it does not invent a sell price.

A local HTML page is written only from the snapshot already loaded.
`--read-prs` may ask `gh` for open pull-request numbers. That path does
not write the page.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from collections.abc import Callable, Sequence
from dataclasses import dataclass, replace
from pathlib import Path
from typing import NoReturn

from held_policy import default_held_path, norm_ma, policy_from_mapping

_FORBIDDEN_PAGE_NAMES = frozenset({"held.json", "submissions.json", "catalog.v1.json"})


@dataclass(frozen=True)
class Count:
    value: int | None
    state: str
    detail: str = ""


@dataclass(frozen=True)
class FreshnessView:
    state: str
    day: str | None = None
    guards_pass: bool | None = None


@dataclass(frozen=True)
class BossWait:
    kind: str
    ref: str
    detail: str


@dataclass(frozen=True)
class DeskStatus:
    intake: Count
    catalog: Count
    held: Count
    open_prs: tuple[int, ...] | None
    open_prs_state: str
    open_prs_detail: str
    freshness: FreshnessView
    waiting: tuple[BossWait, ...] | None
    waiting_state: str
    s06_usd: str | None
    local: bool


def status_from_json(payload: object) -> DeskStatus:
    if not isinstance(payload, dict):
        raise ValueError("fixture must be a JSON object")
    catalog_rows: list[object] | None = None
    if "catalog" in payload:
        catalog_rows = _catalog_rows(payload.get("catalog"))
    waiting, waiting_state, open_prs, open_state = _waiting_and_prs(payload)
    return DeskStatus(
        intake=_count_field(payload, "intake", _intake_rows),
        catalog=_count_field(payload, "catalog", _catalog_rows),
        held=_held_count(payload),
        open_prs=open_prs,
        open_prs_state=open_state,
        open_prs_detail="",
        freshness=_freshness(payload),
        waiting=waiting,
        waiting_state=waiting_state,
        s06_usd=None if catalog_rows is None else _s06_price(catalog_rows),
        local=True,
    )


def render_text(status: DeskStatus) -> str:
    lines = [
        f"intake: {_count_text(status.intake)}",
        f"catalog: {_count_text(status.catalog)}",
        f"held: {_count_text(status.held)}",
        f"open PRs: {_prs_text(status)}",
        f"freshness: {_fresh_text(status.freshness)}",
        f"waiting on Boss: {_wait_text(status)}",
    ]
    if status.s06_usd is not None:
        lines.append(f"S06: ${status.s06_usd}")
    return "\n".join(lines) + "\n"


def render_json(status: DeskStatus) -> dict[str, object]:
    waiting: list[dict[str, str]] | None
    if status.waiting is None:
        waiting = None
    else:
        waiting = [
            {"kind": item.kind, "ref": item.ref, "detail": item.detail} for item in status.waiting
        ]
    return {
        "intakeCount": status.intake.value,
        "intakeState": status.intake.state,
        "catalogCount": status.catalog.value,
        "catalogState": status.catalog.state,
        "heldCount": status.held.value,
        "heldState": status.held.state,
        "openPullRequests": None if status.open_prs is None else list(status.open_prs),
        "openPullRequestsState": status.open_prs_state,
        "freshness": {
            "day": status.freshness.day,
            "guardsPass": status.freshness.guards_pass,
            "state": status.freshness.state,
        },
        "waitingOnBoss": waiting,
        "waitingOnBossState": status.waiting_state,
        "s06Usd": status.s06_usd,
        "local": status.local,
    }


def render_page(status: DeskStatus) -> str:
    if not status.local:
        raise ValueError("local page needs local data")
    rows = [
        ("Intake", _count_text(status.intake)),
        ("Catalog", _count_text(status.catalog)),
        ("Held", _count_text(status.held)),
        ("Open PRs", _prs_text(status)),
        ("Freshness", _fresh_text(status.freshness)),
        ("Waiting on Boss", _wait_text(status)),
    ]
    if status.s06_usd is not None:
        rows.append(("S06", f"${status.s06_usd}"))
    items = "\n".join(
        f"<dt>{_escape(label)}</dt><dd>{_escape(value)}</dd>" for label, value in rows
    )
    return (
        "<!DOCTYPE html>\n"
        '<html lang="en">\n'
        "<head>\n"
        '<meta charset="utf-8">\n'
        "<title>Sassy Closet desk</title>\n"
        "</head>\n"
        "<body>\n"
        "<h1>Sassy Closet desk</h1>\n"
        "<p>Local snapshot. No live fetch.</p>\n"
        f"<dl>\n{items}\n</dl>\n"
        "</body>\n"
        "</html>\n"
    )


def write_page(status: DeskStatus, path: Path) -> None:
    if not status.local:
        raise ValueError("local page needs local data")
    _refuse_page_target(path)
    body = render_page(status)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")


def read_open_pr_numbers(
    repo: str,
    runner: Callable[..., subprocess.CompletedProcess[str]] | None = None,
) -> tuple[tuple[int, ...] | None, str, str]:
    """Read open pull-request numbers. Does not merge, comment, or push."""
    run = runner or subprocess.run
    command = [
        "gh",
        "pr",
        "list",
        "--repo",
        repo,
        "--state",
        "open",
        "--json",
        "number",
        "--limit",
        "200",
    ]
    try:
        completed = run(command, text=True, capture_output=True, check=False)
    except OSError as error:
        return None, "unread", str(error)
    if completed.returncode != 0:
        detail = (completed.stderr or completed.stdout or "gh failed").strip().splitlines()
        return None, "unread", detail[0] if detail else "gh failed"
    try:
        payload = json.loads(completed.stdout)
    except json.JSONDecodeError:
        return None, "unread", "gh JSON did not parse"
    if not isinstance(payload, list):
        return None, "unread", "gh JSON must be a list"
    numbers: list[int] = []
    for item in payload:
        if not isinstance(item, dict):
            return None, "unread", "gh row needs an integer number"
        try:
            number = _positive_int(item.get("number"), "gh pull request")
        except ValueError as error:
            return None, "unread", str(error)
        numbers.append(number)
    unique = tuple(sorted(set(numbers)))
    return unique, "ok", f"{len(unique)} open"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Print a read-only desk status. Does not write Blob, intake, Meta, or data/held.json."
        )
    )
    parser.add_argument("--fixture", help="Desk JSON. Skips every other source.")
    parser.add_argument("--intake", help="Local intake JSON.")
    parser.add_argument("--catalog", help="Local catalog JSON.")
    parser.add_argument("--held", help="Held policy JSON. Defaults to data/held.json.")
    parser.add_argument("--prs", help="Local open pull-request JSON.")
    parser.add_argument("--freshness", help="Local freshness report JSON.")
    parser.add_argument(
        "--read-prs",
        action="store_true",
        help="Read open pull-request numbers with gh. Disables the local page.",
    )
    parser.add_argument("--repo", default="SkyLanter/Sassy-closet")
    parser.add_argument("--page", help="Write a local HTML page from data already loaded.")
    parser.add_argument("--json", action="store_true", help="Print JSON instead of text.")
    args = parser.parse_args(argv)
    try:
        status = _status_from_args(args)
        if args.page:
            write_page(status, Path(args.page))
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(str(error), file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps(render_json(status), indent=2))
    else:
        print(render_text(status), end="")
        if args.page:
            print(f"page: {args.page}")
    return 0


def _status_from_args(args: argparse.Namespace) -> DeskStatus:
    if args.read_prs and args.prs:
        raise ValueError("pass either --prs or --read-prs")
    if args.fixture:
        if any([args.intake, args.catalog, args.held, args.prs, args.freshness, args.read_prs]):
            raise ValueError("fixture mode does not take other sources")
        payload = json.loads(Path(args.fixture).read_text(encoding="utf-8"))
        return status_from_json(payload)
    held_path = Path(args.held) if args.held else default_held_path()
    payload: dict[str, object] = {"held": json.loads(held_path.read_text(encoding="utf-8"))}
    if args.intake:
        payload["intake"] = json.loads(Path(args.intake).read_text(encoding="utf-8"))
    if args.catalog:
        payload["catalog"] = json.loads(Path(args.catalog).read_text(encoding="utf-8"))
    if args.prs:
        payload["pullRequests"] = json.loads(Path(args.prs).read_text(encoding="utf-8"))
    if args.freshness:
        payload["freshness"] = json.loads(Path(args.freshness).read_text(encoding="utf-8"))
    status = status_from_json(payload)
    if not args.read_prs:
        return status
    numbers, state, detail = read_open_pr_numbers(args.repo)
    return replace(
        status,
        open_prs=numbers,
        open_prs_state=state,
        open_prs_detail=detail,
        local=False,
    )


def _count_field(
    payload: dict[str, object],
    key: str,
    rows_of: Callable[[object], list[object]],
) -> Count:
    if key not in payload:
        return Count(None, "unread")
    rows = rows_of(payload[key])
    return Count(_ma_count(rows, key), "ok")


def _held_count(payload: dict[str, object]) -> Count:
    if "held" not in payload:
        return Count(None, "unread")
    policy = policy_from_mapping(payload.get("held"), source="held")
    return Count(len(policy.held), "ok")


def _waiting_and_prs(
    payload: dict[str, object],
) -> tuple[tuple[BossWait, ...] | None, str, tuple[int, ...] | None, str]:
    groups: list[list[BossWait]] = []
    open_prs: tuple[int, ...] | None = None
    open_state = "unread"
    if "pullRequests" in payload:
        numbers, waits = _pull_requests(payload.get("pullRequests"))
        open_prs = tuple(numbers)
        open_state = "ok"
        groups.append(waits)
    if "waitingOnBoss" in payload:
        groups.append(_explicit_waits(payload.get("waitingOnBoss")))
    freshness = payload.get("freshness")
    if isinstance(freshness, dict) and "pickup" in freshness:
        groups.append(_pickup_waits(freshness.get("pickup")))
    if not groups:
        return None, "unread", open_prs, open_state
    return tuple(_merge_waits(groups)), "ok", open_prs, open_state


def _freshness(payload: dict[str, object]) -> FreshnessView:
    if "freshness" not in payload:
        return FreshnessView("unread")
    value = payload.get("freshness")
    if not isinstance(value, dict):
        raise ValueError("freshness must be an object")
    day = value.get("day")
    if day is not None and not isinstance(day, str):
        raise ValueError("freshness day must be a string")
    if isinstance(day, str) and day.strip() == "":
        day = None
    guards = value.get("guardsPass")
    if not isinstance(guards, bool):
        raise ValueError("freshness guardsPass must be true or false")
    return FreshnessView("pass" if guards else "fail", day, guards)


def _intake_rows(value: object) -> list[object]:
    return _rows(value, "intake", ("submissions", "intake", "rows"))


def _catalog_rows(value: object) -> list[object]:
    return _rows(value, "catalog", ("products", "rows"))


def _rows(value: object, label: str, keys: Sequence[str]) -> list[object]:
    if isinstance(value, list):
        return list(value)
    if isinstance(value, dict):
        for key in keys:
            found = value.get(key)
            if isinstance(found, list):
                return list(found)
    raise ValueError(f"{label} must be a list of mãs")


def _ma_count(rows: Sequence[object], label: str) -> int:
    count = 0
    for item in rows:
        if not isinstance(item, dict) or not isinstance(item.get("ma"), str) or not item["ma"].strip():
            raise ValueError(f"{label} row needs a mã")
        count += 1
    return count


def _s06_price(rows: Sequence[object]) -> str | None:
    for item in rows:
        if not isinstance(item, dict):
            continue
        ma = item.get("ma")
        if not isinstance(ma, str) or norm_ma(ma) != "S06":
            continue
        for key in ("priceUsd", "price_usd"):
            if key not in item:
                continue
            parsed = _plain_number(item.get(key))
            if parsed is None:
                raise ValueError("S06 price is not a number")
            return parsed
        return None
    return None


def _plain_number(value: object) -> str | None:
    if value is None or isinstance(value, bool):
        return None
    if isinstance(value, int):
        return str(value)
    if isinstance(value, float):
        if value != value:
            return None
        text = format(value, "f").rstrip("0").rstrip(".")
        return text or "0"
    if isinstance(value, str):
        text = value.strip().replace("$", "").replace(",", "")
        if text == "":
            return None
        parts = text.split(".")
        if len(parts) > 2 or not all(part.isdigit() for part in parts) or parts[0] == "":
            return None
        return text
    return None


def _pull_requests(value: object) -> tuple[list[int], list[BossWait]]:
    if not isinstance(value, list):
        raise ValueError("pullRequests must be a list")
    numbers: list[int] = []
    waits: list[BossWait] = []
    for item in value:
        if isinstance(item, bool):
            raise ValueError("pull request needs an integer number")
        if isinstance(item, int):
            numbers.append(_positive_int(item, "pull request"))
            continue
        if isinstance(item, dict):
            number = _positive_int(item.get("number"), "pull request")
            numbers.append(number)
            if item.get("waitingOnBoss") is True:
                title = item.get("title")
                detail = "" if title is None else str(title)
                waits.append(BossWait("pull_request", str(number), detail))
            continue
        raise ValueError("pull request must be a number or an object")
    return sorted(set(numbers)), waits


def _explicit_waits(value: object) -> list[BossWait]:
    if not isinstance(value, list):
        raise ValueError("waitingOnBoss must be a list")
    waits: list[BossWait] = []
    for item in value:
        if not isinstance(item, dict):
            raise ValueError("waitingOnBoss row must be an object")
        kind = item.get("kind")
        detail = "" if item.get("detail") is None else str(item.get("detail"))
        if kind == "pull_request":
            raw = item.get("number", item.get("ref"))
            number = _positive_int(raw, "waiting pull request")
            waits.append(BossWait("pull_request", str(number), detail))
        elif kind == "ma":
            ma = item.get("ma", item.get("ref"))
            if not isinstance(ma, str) or not ma.strip():
                raise ValueError("waiting mã needs a mã")
            waits.append(BossWait("ma", norm_ma(ma), detail))
        else:
            _unexpected_kind(kind)
    return waits


def _pickup_waits(value: object) -> list[BossWait]:
    if not isinstance(value, list):
        raise ValueError("freshness pickup must be a list")
    waits: list[BossWait] = []
    for item in value:
        if not isinstance(item, dict):
            raise ValueError("pickup row must be an object")
        flags = item.get("flags", [])
        if not isinstance(flags, list):
            raise ValueError("pickup flags must be a list")
        if "boss_approval" not in flags:
            continue
        ma = item.get("ma")
        if not isinstance(ma, str) or not ma.strip():
            raise ValueError("pickup row needs a mã")
        detail = "" if item.get("detail") is None else str(item.get("detail"))
        waits.append(BossWait("ma", norm_ma(ma), detail))
    return waits


def _merge_waits(groups: Sequence[Sequence[BossWait]]) -> list[BossWait]:
    merged: list[BossWait] = []
    seen: set[tuple[str, str]] = set()
    for group in groups:
        for item in group:
            key = (item.kind, item.ref)
            if key in seen:
                continue
            seen.add(key)
            merged.append(item)
    return merged


def _positive_int(value: object, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        raise ValueError(f"{label} needs an integer number")
    return value


def _unexpected_kind(kind: object) -> None:
    raise ValueError(f"waitingOnBoss kind must be pull_request or ma, not {kind!r}")


def _count_text(count: Count) -> str:
    if count.state != "ok" or count.value is None:
        return "unread"
    return str(count.value)


def _prs_text(status: DeskStatus) -> str:
    if status.open_prs_state != "ok" or status.open_prs is None:
        if status.open_prs_detail:
            return f"unread ({status.open_prs_detail})"
        return "unread"
    if not status.open_prs:
        return "none"
    return ", ".join(str(number) for number in status.open_prs)


def _fresh_text(fresh: FreshnessView) -> str:
    if fresh.state == "unread":
        return "unread"
    label = _fresh_label(fresh.state)
    if fresh.day:
        return f"{fresh.day} {label}"
    return label


def _fresh_label(state: str) -> str:
    if state == "pass":
        return "PASS"
    if state == "fail":
        return "FAIL"
    _never(state)


def _wait_text(status: DeskStatus) -> str:
    if status.waiting_state != "ok" or status.waiting is None:
        return "unread"
    if not status.waiting:
        return "none"
    return "; ".join(_wait_label(item) for item in status.waiting)


def _wait_label(item: BossWait) -> str:
    if item.kind == "pull_request":
        label = f"PR {item.ref}"
    elif item.kind == "ma":
        label = item.ref
    else:
        _never(item.kind)
    if item.detail:
        return f"{label} ({item.detail})"
    return label


def _never(value: object) -> NoReturn:
    raise AssertionError(f"unexpected {value!r}")


def _escape(value: str) -> str:
    return (
        value.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def _refuse_page_target(path: Path) -> None:
    resolved = path if path.is_absolute() else Path.cwd() / path
    resolved = resolved.resolve()
    if resolved == default_held_path().resolve() or resolved.name in _FORBIDDEN_PAGE_NAMES:
        raise ValueError(f"refusing to write {resolved.name}")
    repo = Path(__file__).resolve().parents[1]
    try:
        relative = resolved.relative_to(repo)
    except ValueError:
        relative = None
    if relative is not None and relative.parts and relative.parts[0] in {
        "data",
        "sassy-closet",
        "sassy-closet-shop",
    }:
        raise ValueError("refusing to write inside the shop app or data/")
    if resolved.suffix.lower() not in {".html", ".htm"}:
        raise ValueError("local page must be an html file")


if __name__ == "__main__":
    raise SystemExit(main())
