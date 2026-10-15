"""Add a new intake mã to a held file.

A mã is added when it is absent from the held file, absent from the never-list,
not S06, and absent from the fixture Blob and hub rows, and either its Taobao
data has no size, no photo, or no public ¥, or the intake ¥ differs from that
public ¥. A login wall is not a missing ¥.

The fixture and the held path are local files. This module writes that held
path only when a mã is added, and it refuses data/held.json. It does not fetch
intake, Blob, Meta, or Square, and it does not invent a sell price.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path

from held_policy import MA_RE, HeldPolicy, default_held_path, load_held_policy
from intake_flags import CNY_RE, IntakeRow

S06 = "S06"
_LOGIN_TOKENS = ("login-walled", "unreachable", "访问受限", "passport", "安全验证")


@dataclass(frozen=True)
class TaobaoSlice:
    ma: str
    state: str
    public_cny: Decimal | None
    detail: str
    sizes: tuple[str, ...] | None
    photo_count: int | None


@dataclass(frozen=True)
class HeldAdd:
    ma: str
    reasons: tuple[str, ...]
    intake_cny: str
    public_cny: str | None

    def as_json(self) -> dict[str, object]:
        return {
            "ma": self.ma,
            "reasons": list(self.reasons),
            "intakeCny": self.intake_cny,
            "publicCny": self.public_cny,
        }


@dataclass(frozen=True)
class IntakeFixture:
    intake: tuple[IntakeRow, ...]
    taobao: dict[str, TaobaoSlice]
    live: frozenset[str]


def plan_additions(fixture: IntakeFixture, policy: HeldPolicy) -> list[HeldAdd]:
    """Return mãs to append. Existing held mãs and the never-list stay put."""
    added: list[HeldAdd] = []
    seen: set[str] = set()
    held = set(policy.held)
    never = set(policy.never_list)
    for row in fixture.intake:
        code = row.ma.strip().upper()
        if code in seen:
            continue
        seen.add(code)
        if code == S06 or code in held or code in never or code in fixture.live:
            continue
        view = fixture.taobao.get(code)
        reasons = _reasons(row, view)
        if not reasons:
            continue
        added.append(
            HeldAdd(
                ma=code,
                reasons=tuple(reasons),
                intake_cny="" if row.cost_cny is None else row.cost_cny,
                public_cny=None if view is None else _cny_text(view.public_cny),
            )
        )
    return added


def sync_held_file(fixture_path: Path, held_path: Path) -> dict[str, object]:
    """Append planned mãs to held_path. Refuse the repo held file."""
    destination = _writable_held(held_path)
    fixture = load_fixture(fixture_path)
    policy = load_held_policy(destination)
    added = plan_additions(fixture, policy)
    resulting = list(policy.held) + [item.ma for item in added]
    wrote = False
    if added:
        _write_held(destination, resulting, list(policy.never_list))
        written = load_held_policy(destination)
        if written.held != tuple(resulting) or written.never_list != policy.never_list:
            raise ValueError("held file did not keep the existing mãs")
        wrote = True
    return {
        "added": [item.as_json() for item in added],
        "heldIncomplete": resulting,
        "neverList": list(policy.never_list),
        "wrote": wrote,
    }


def load_fixture(path: Path) -> IntakeFixture:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("fixture must be a JSON object")
    intake_raw = payload.get("intake")
    if not isinstance(intake_raw, list):
        raise ValueError("fixture intake must be a list")
    taobao_raw = payload.get("taobao", [])
    if not isinstance(taobao_raw, list):
        raise ValueError("fixture taobao must be a list")
    if "blob" not in payload:
        raise ValueError("fixture blob catalog is required so a live mã is not held")
    live = _catalog_codes(payload.get("blob"), "blob")
    if "hub" in payload:
        live |= _catalog_codes(payload.get("hub"), "hub")
    intake = tuple(_intake_row(item) for item in intake_raw)
    taobao = {item.ma: item for item in (_taobao_row(item) for item in taobao_raw)}
    return IntakeFixture(intake=intake, taobao=taobao, live=frozenset(live))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Append a new intake mã to a held file. Fixture only. Does not write data/held.json.",
    )
    parser.add_argument("--fixture", required=True, help="Local intake fixture JSON.")
    parser.add_argument("--held", required=True, help="Held file to update. Refuses data/held.json.")
    args = parser.parse_args(argv)
    try:
        summary = sync_held_file(Path(args.fixture), Path(args.held))
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(str(error), file=sys.stderr)
        return 2
    print(json.dumps(summary, indent=2))
    return 0


def _reasons(row: IntakeRow, view: TaobaoSlice | None) -> list[str]:
    reasons: list[str] = []
    sizes = _sizes(row, view)
    photos = _photos(row, view)
    if not any(part.strip() for part in sizes):
        reasons.append("missing_size")
    if photos is None or photos < 1:
        reasons.append("missing_photos")
    public = None if view is None else view.public_cny
    if public is None and not _login_wall(view):
        reasons.append("missing_yen")
    stored = "" if row.cost_cny is None else row.cost_cny.strip()
    if public is not None and CNY_RE.fullmatch(stored) is not None and Decimal(stored) != public:
        reasons.append("cost_drift")
    return reasons


def _sizes(row: IntakeRow, view: TaobaoSlice | None) -> tuple[str, ...]:
    if view is not None and view.sizes is not None:
        return view.sizes
    if row.sizes is not None:
        return row.sizes
    return ()


def _photos(row: IntakeRow, view: TaobaoSlice | None) -> int | None:
    if view is not None and view.photo_count is not None:
        return view.photo_count
    return row.photo_count


def _login_wall(view: TaobaoSlice | None) -> bool:
    if view is None or view.state != "skip":
        return False
    detail = view.detail.casefold()
    if detail == "":
        return False
    return any(token in detail for token in _LOGIN_TOKENS)


def _intake_row(item: object) -> IntakeRow:
    if not isinstance(item, dict) or not isinstance(item.get("ma"), str):
        raise ValueError("fixture intake row needs a mã")
    code = item["ma"].strip().upper()
    if MA_RE.fullmatch(code) is None:
        raise ValueError(f"fixture intake mã {item['ma']!r} is invalid")
    cost = item.get("cost_cny")
    return IntakeRow(
        code,
        None if cost is None else str(cost),
        None,
        None,
        _sizes_field(item),
        _photo_field(item),
    )


def _taobao_row(item: object) -> TaobaoSlice:
    if not isinstance(item, dict) or not isinstance(item.get("ma"), str):
        raise ValueError("fixture taobao row needs a mã")
    code = item["ma"].strip().upper()
    if MA_RE.fullmatch(code) is None:
        raise ValueError(f"fixture taobao mã {item['ma']!r} is invalid")
    public = _decimal(item.get("public_cny"))
    state = item.get("state")
    if state is None:
        state = "ok" if public is not None else "skip"
    detail = item.get("detail", "")
    return TaobaoSlice(
        code,
        str(state),
        public,
        "" if detail is None else str(detail),
        _sizes_field(item),
        _photo_field(item),
    )


def _sizes_field(item: dict[str, object]) -> tuple[str, ...] | None:
    if "sizes" not in item and "size" not in item:
        return None
    raw = item.get("sizes", item.get("size"))
    if raw is None:
        return ()
    if isinstance(raw, str):
        return tuple(part for part in raw.replace(",", " ").split() if part)
    if isinstance(raw, list):
        parts: list[str] = []
        for part in raw:
            if not isinstance(part, str):
                raise ValueError("fixture sizes must be a list of strings")
            text = part.strip()
            if text:
                parts.append(text)
        return tuple(parts)
    raise ValueError("fixture sizes must be a list of strings")


def _photo_field(item: dict[str, object]) -> int | None:
    if "photo_count" in item and item.get("photo_count") is not None:
        raw = item.get("photo_count")
        if isinstance(raw, bool) or not isinstance(raw, (int, str)):
            raise ValueError("photo_count must be an integer")
        text = str(raw).strip()
        if not text.isdigit():
            raise ValueError("photo_count must be an integer")
        return int(text)
    for key in ("gallery", "photos", "images"):
        raw = item.get(key)
        if isinstance(raw, list):
            return sum(1 for part in raw if str(part).strip())
    return None


def _catalog_codes(value: object, label: str) -> set[str]:
    if isinstance(value, dict):
        if str(value.get("state", "ok")) == "skip":
            if label == "blob":
                raise ValueError("fixture blob catalog is required so a live mã is not held")
            return set()
        raw_rows = value.get("rows", [])
    elif isinstance(value, list):
        raw_rows = value
    else:
        raise ValueError(f"fixture {label} must be a list of mãs or a catalog object")
    if not isinstance(raw_rows, list):
        raise ValueError(f"fixture {label} rows must be a list")
    codes: set[str] = set()
    for item in raw_rows:
        if isinstance(item, str):
            code = item.strip().upper()
        elif isinstance(item, dict) and isinstance(item.get("ma"), str):
            code = item["ma"].strip().upper()
        else:
            raise ValueError(f"fixture {label} row needs a mã")
        if MA_RE.fullmatch(code) is None:
            raise ValueError(f"fixture {label} mã {code!r} is invalid")
        codes.add(code)
    return codes


def _writable_held(path: Path) -> Path:
    resolved = path.resolve()
    if resolved == default_held_path().resolve():
        raise ValueError("refusing to write data/held.json")
    if not resolved.is_file():
        raise ValueError("held file must already exist")
    return resolved


def _write_held(path: Path, held: list[str], never: list[str]) -> None:
    payload = {"heldIncomplete": held, "neverList": never}
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def _decimal(value: object) -> Decimal | None:
    if value is None or value == "":
        return None
    return Decimal(str(value))


def _cny_text(value: Decimal | None) -> str | None:
    if value is None:
        return None
    text = format(value, "f")
    if "." in text:
        text = text.rstrip("0").rstrip(".")
    return text


if __name__ == "__main__":
    raise SystemExit(main())
