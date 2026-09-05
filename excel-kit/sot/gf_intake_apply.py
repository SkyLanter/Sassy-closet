#!/usr/bin/env python3
"""Apply one GF clothes-intake packet to Sassy_Closet_SoT.xlsx.

PRIMARY: GF self-upload in Documents/Sassy Closet/From GF/.
Backups: Slack #shop-intake / Boss paste / email last.
Never Messenger. Never Dial Bot. Never invent mã. Never Square Save.
Never point photo_link at From GF paths. Never embed images.

Usage:
  python3 excel-kit/sot/gf_intake_apply.py --from-gf path/to/packet/ -w ./out/Sassy_Closet_SoT.xlsx
  python3 excel-kit/sot/gf_intake_apply.py --packet path/to/packet/ --dry-run
  python3 excel-kit/sot/gf_intake_apply.py --kind looking --no-source --what-vi "Váy"
"""

from __future__ import annotations

import argparse
import re
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path

_KIT_DIR = Path(__file__).resolve().parent.parent
if str(_KIT_DIR) not in sys.path:
    sys.path.insert(0, str(_KIT_DIR))

from schema import (  # noqa: E402
    ASK_STOCK_MA,
    CANDIDATE_TYPES,
    ONEDRIVE_FROM_GF,
    ONEDRIVE_PHOTOS,
    SOT_WISHLIST_STATUS,
    STAY_OFF_SQUARE,
    MissingMaError,
    is_valid_ma,
    photo_filename_for_ma,
    photo_filename_for_wish,
    require_ma,
    wishlist_status_or_raise,
)

from sot import append_bot_activity  # noqa: E402
from sot import append_official_row  # noqa: E402
from sot import append_wishlist_row  # noqa: E402
from sot.workbook import (  # noqa: E402
    WorkbookError,
    add_dry_run_arg,
    add_workbook_path_arg,
    locate_sot,
)

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".heic"}
NOTE_NAMES = (
    "INTAKE_TEMPLATE.txt",
    "INTAKE_TEMPLATE.md",
    "intake.txt",
    "note.txt",
    "note.md",
)
WISH_PHOTO_STEM = re.compile(r"^#(\d{3})(?:_(\d+))?$", re.IGNORECASE)
MA_INVENT_WORDS = {
    "next",
    "auto",
    "new",
    "invent",
    "mint",
    "generate",
    "tự đặt",
    "tu dat",
    "tự gán",
    "tu gan",
}
INBOX_ROOT_NAMES = {"from gf", "from_gf", "from-gf"}

KIND_ALIASES: dict[str, str] = {}
for _label, _keys in {
    "looking": (
        "looking",
        "look",
        "hunt",
        "hunting",
        "candidate",
        "wishlist",
        "đang xem",
        "dang xem",
        "ứng viên",
        "ung vien",
    ),
    "watching": ("watching", "watch", "theo dõi", "theo doi"),
    "skip": ("skip", "bỏ", "bo", "no"),
    "bought": (
        "bought",
        "buy",
        "purchased",
        "received",
        "owned",
        "arrived",
        "đã mua",
        "da mua",
        "đã nhận",
        "da nhan",
        "nhận rồi",
        "nhan roi",
    ),
}.items():
    for _k in _keys:
        KIND_ALIASES[_k] = _label

KEY_ALIASES: dict[str, str] = {
    "kind": "kind",
    "loại": "kind",
    "loai": "kind",
    "source": "source",
    "link": "source",
    "nguồn": "source",
    "nguon": "source",
    "no_source": "no_source",
    "nosource": "no_source",
    "no-source": "no_source",
    "what_vi": "what_vi",
    "what-vi": "what_vi",
    "what_en": "what_en",
    "what-en": "what_en",
    "name_vi": "name_vi",
    "name-vi": "name_vi",
    "name_en": "name_en",
    "name-en": "name_en",
    "brand": "brand",
    "type": "item_type",
    "item_type": "item_type",
    "size": "size",
    "color": "color",
    "price_original": "price_original",
    "price-original": "price_original",
    "currency": "currency",
    "qty_pieces": "qty_pieces",
    "qty-pieces": "qty_pieces",
    "qty": "qty_pieces",
    "notes": "notes",
    "requested_by": "requested_by",
    "requested-by": "requested_by",
    "prefix": "prefix",
    "ma": "ma",
    "mã": "ma",
    "status": "status",
    "reason": "reason",
    "photo_link": "photo_link",
    "photo-link": "photo_link",
    "list_price": "list_price",
    "list-price": "list_price",
    "condition": "condition",
    "cost": "cost",
    "max_cost": "max_cost",
    "max-cost": "max_cost",
    "target_price": "target_price",
    "target-price": "target_price",
}

TRUTHY = {"yes", "true", "1", "y", "có", "co"}
FALSY = {"no", "false", "0", "n", "không", "khong", ""}


class IntakeError(ValueError):
    """User-facing intake problem — exit 2, never invent a row."""


@dataclass
class IntakeFields:
    kind: str
    source: str | None = None
    no_source: bool = False
    what_vi: str | None = None
    what_en: str | None = None
    name_vi: str | None = None
    name_en: str | None = None
    brand: str | None = None
    item_type: str | None = None
    size: str | None = None
    color: str | None = None
    price_original: str | None = None
    currency: str | None = None
    qty_pieces: str | None = None
    notes: str | None = None
    requested_by: str = "GF"
    prefix: str | None = None
    ma: str | None = None
    status: str | None = None
    reason: str | None = None
    photo_link: str | None = None
    list_price: str | None = None
    condition: str | None = None
    cost: str | None = None
    max_cost: str | None = None
    target_price: str | None = None
    packet_dir: Path | None = None

    def display_what(self) -> str:
        return (
            self.what_vi
            or self.name_vi
            or self.what_en
            or self.name_en
            or self.brand
            or "(unnamed piece)"
        )

    def wishlist_status(self) -> str:
        if self.kind == "bought":
            return "bought"
        if self.status:
            return wishlist_status_or_raise(self.status)
        if self.kind == "looking":
            return "candidate"
        if self.kind in {"watching", "skip"}:
            return self.kind
        return "candidate"

    def route(self) -> str:
        if self.kind == "bought" and self.ma:
            return "official"
        if self.kind == "bought":
            return "wishlist_bought"
        return "wishlist"


def _clean(value: object | None) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text if text else None


def _truthy(value: object | None) -> bool | None:
    if value is None:
        return None
    text = str(value).strip().lower()
    if text in TRUTHY:
        return True
    if text in FALSY:
        return False
    return None


def parse_intake_text(text: str) -> dict[str, str]:
    """Parse INTAKE_TEMPLATE / note.txt key: value lines. Unknown keys ignored."""
    out: dict[str, str] = {}
    unknown: list[str] = []
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if ":" in line:
            key, _, val = line.partition(":")
        elif "=" in line:
            key, _, val = line.partition("=")
        else:
            continue
        key_norm = key.strip().lower().replace(" ", "_")
        logical = KEY_ALIASES.get(key_norm)
        if logical is None:
            unknown.append(key.strip())
            continue
        out[logical] = val.strip().strip('"').strip("'")
    if unknown:
        out["_unknown_keys"] = ", ".join(unknown)
    return out


def normalize_kind(raw: object | None) -> str:
    text = _clean(raw)
    if not text:
        raise IntakeError(
            "kind is required: looking (candidate / hunt) or bought. "
            "Do not invent. See excel-kit/templates/from_gf/INTAKE_TEMPLATE.txt."
        )
    mapped = KIND_ALIASES.get(text.lower())
    if mapped is None:
        raise IntakeError(
            f"kind {text!r} is not looking/candidate/watching/skip/bought. Never invent."
        )
    return mapped


def sanitize_ma_field(raw: object | None) -> str | None:
    text = _clean(raw)
    if text is None:
        return None
    lowered = text.lower()
    if lowered in {"ask", "tbd", "n/a", "na", "none", "-", "ask stock"}:
        return None
    if lowered in MA_INVENT_WORDS or "invent" in lowered or "next mã" in lowered:
        raise IntakeError(
            f"ma {text!r} looks like minting. Never invent a mã. {ASK_STOCK_MA}"
        )
    if is_valid_ma(text):
        try:
            return require_ma(text)
        except MissingMaError as exc:
            raise IntakeError(str(exc)) from exc
    raise IntakeError(
        f"ma {text!r} is not a live mã (AO|QU|VA|AK|GI|PK|SET + 3 digits). "
        f"Do not invent. {ASK_STOCK_MA}"
    )


def validate_photo_link(raw: object | None) -> str | None:
    link = _clean(raw)
    if link is None:
        return None
    lower = link.lower()
    if lower.startswith("file:"):
        raise IntakeError("photo_link must be an OneDrive share URL, not a file: path.")
    if "from gf" in lower or "from_gf" in lower or "from%20gf" in lower:
        raise IntakeError(
            "photo_link must not point at From GF/. "
            f"Use a share URL from {ONEDRIVE_PHOTOS}/ after Kit uploads."
        )
    if not (lower.startswith("https://") or lower.startswith("http://")):
        raise IntakeError(
            "photo_link must be an http(s) OneDrive share URL. "
            "Never store From GF or local paths on SoT. Never embed images."
        )
    return link


def packet_photos(packet_dir: Path) -> list[Path]:
    if not packet_dir.is_dir():
        return []
    found: list[Path] = []
    for path in sorted(packet_dir.iterdir(), key=lambda p: p.name.lower()):
        if path.is_file() and path.suffix.lower() in IMAGE_EXTS:
            found.append(path)
    return found


def load_packet_dir(path: Path) -> tuple[dict[str, str], Path]:
    packet = path.expanduser()
    if not packet.exists():
        raise IntakeError(f"packet not found: {packet}")
    if packet.is_file():
        packet = packet.parent
    packet = packet.resolve()
    if packet.name.lower() in INBOX_ROOT_NAMES and (
        (packet / "HOW_TO_UPLOAD.md").is_file() or (packet / "examples").is_dir()
    ):
        raise IntakeError(
            f"{packet} looks like the From GF inbox root. "
            "Pass one packet folder (photos + INTAKE_TEMPLATE.txt or note.txt). "
            "See excel-kit/sot/FROM_GF_WATCH.md."
        )
    merged: dict[str, str] = {}
    notes_found = 0
    for name in NOTE_NAMES:
        candidate = packet / name
        if candidate.is_file():
            notes_found += 1
            merged.update(parse_intake_text(candidate.read_text(encoding="utf-8-sig")))
    photos = packet_photos(packet)
    if notes_found == 0 and not photos:
        raise IntakeError(
            f"{packet} is not a packet (need INTAKE_TEMPLATE.txt or note.txt, and/or photos)."
        )
    return merged, packet


def next_wish_photo_number(photos_dir: Path) -> int:
    highest = 0
    if photos_dir.is_dir():
        for path in photos_dir.iterdir():
            match = WISH_PHOTO_STEM.match(path.stem)
            if match:
                highest = max(highest, int(match.group(1)))
    nxt = highest + 1
    if nxt > 999:
        raise IntakeError("Photos already has #999.jpg — ask Kit. Do not invent names.")
    return nxt


def _next_ma_extra(photos_dir: Path, ma: str) -> int | None:
    stem = require_ma(ma)
    used = [0]
    if photos_dir.is_dir():
        for path in photos_dir.iterdir():
            name = path.stem.upper()
            if name == stem:
                used.append(1)
            elif name.startswith(stem + "_") and name.split("_")[-1].isdigit():
                used.append(int(name.split("_")[-1]))
    highest = max(used)
    return None if highest == 0 else highest + 1


def plan_photo_copies(
    sources: list[Path],
    photos_dir: Path,
    *,
    ma: str | None,
) -> list[tuple[Path, str]]:
    planned: list[tuple[Path, str]] = []
    if not sources:
        return planned
    if ma:
        start = _next_ma_extra(photos_dir, ma)
        for index, src in enumerate(sources):
            if start is None:
                extra = None if index == 0 else index + 1
            else:
                extra = start + index
            planned.append((src, photo_filename_for_ma(ma, extra)))
        return planned
    number = next_wish_photo_number(photos_dir)
    for index, src in enumerate(sources):
        extra = None if index == 0 else index + 1
        planned.append((src, photo_filename_for_wish(number, extra)))
    return planned


def copy_photos(planned: list[tuple[Path, str]], photos_dir: Path) -> list[Path]:
    photos_dir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    for src, name in planned:
        dest = photos_dir / name
        if dest.exists():
            raise IntakeError(f"photo already exists: {dest} — will not overwrite")
        shutil.copy2(src, dest)
        written.append(dest)
    return written


def default_photos_out(workbook: Path | None) -> Path:
    if workbook is not None:
        parent = Path(workbook).expanduser().resolve().parent
        if parent.name.lower() in {"sassy closet", "sassy-closet"}:
            return parent / "Photos"
    return Path.cwd() / "out" / "Photos"


def _merge_raw(packet: dict[str, str], args: argparse.Namespace) -> dict[str, object]:
    merged: dict[str, object] = dict(packet)
    flag_map = {
        "kind": args.kind,
        "source": args.source,
        "what_vi": args.what_vi,
        "what_en": args.what_en,
        "name_vi": args.name_vi,
        "name_en": args.name_en,
        "brand": args.brand,
        "item_type": args.item_type,
        "size": args.size,
        "color": args.color,
        "price_original": args.price_original,
        "currency": args.currency,
        "qty_pieces": args.qty_pieces,
        "notes": args.notes,
        "requested_by": args.requested_by,
        "prefix": args.prefix,
        "ma": args.ma,
        "status": args.status,
        "reason": args.reason,
        "photo_link": args.photo_link,
        "list_price": args.list_price,
        "condition": args.condition,
        "cost": args.cost,
        "max_cost": args.max_cost,
        "target_price": args.target_price,
    }
    for key, value in flag_map.items():
        if value is not None:
            merged[key] = value
    if args.no_source:
        merged["no_source"] = "yes"
        if args.source is None:
            merged["source"] = ""
    return merged


def build_fields(raw: dict[str, object], packet_dir: Path | None) -> IntakeFields:
    unknown = raw.pop("_unknown_keys", None)
    if unknown:
        print(f"note: ignored unknown template keys: {unknown}")
    kind = normalize_kind(raw.get("kind"))
    ma = sanitize_ma_field(raw.get("ma"))
    no_source = _truthy(raw.get("no_source")) is True
    source = _clean(raw.get("source"))
    if no_source:
        source = None
    photo_link = validate_photo_link(raw.get("photo_link"))
    prefix = _clean(raw.get("prefix"))
    if prefix and is_valid_ma(prefix):
        raise IntakeError(
            f"prefix {prefix!r} looks like a live mã. "
            "prefix is AO/QU/VA/… hint only — never a stock code on intake."
        )
    fields = IntakeFields(
        kind=kind,
        source=source,
        no_source=no_source,
        what_vi=_clean(raw.get("what_vi")),
        what_en=_clean(raw.get("what_en")),
        name_vi=_clean(raw.get("name_vi")),
        name_en=_clean(raw.get("name_en")),
        brand=_clean(raw.get("brand")),
        item_type=_clean(raw.get("item_type")),
        size=_clean(raw.get("size")),
        color=_clean(raw.get("color")),
        price_original=_clean(raw.get("price_original")),
        currency=_clean(raw.get("currency")),
        qty_pieces=_clean(raw.get("qty_pieces")),
        notes=_clean(raw.get("notes")),
        requested_by=_clean(raw.get("requested_by")) or "GF",
        prefix=prefix,
        ma=ma,
        status=_clean(raw.get("status")),
        reason=_clean(raw.get("reason")),
        photo_link=photo_link,
        list_price=_clean(raw.get("list_price")),
        condition=_clean(raw.get("condition")),
        cost=_clean(raw.get("cost")),
        max_cost=_clean(raw.get("max_cost")),
        target_price=_clean(raw.get("target_price")),
        packet_dir=packet_dir,
    )
    if not (fields.what_vi or fields.what_en or fields.name_vi or fields.name_en or fields.brand):
        raise IntakeError("need what_vi / what_en (or name / brand). Never invent a description.")
    if fields.kind != "bought" and fields.ma:
        raise IntakeError(
            "do not put a live mã on Wishlist / looking packets. "
            "Bought finds get a Boss-assigned mã on Official later."
        )
    if fields.status:
        status_lower = fields.status.strip().lower()
        if status_lower == "bought" and fields.kind != "bought":
            raise IntakeError("status=bought requires kind=bought (still off Square; ASK STOCK if no mã).")
    if fields.kind == "bought" and fields.status and fields.status.lower() not in {
        "bought",
        "available",
        "reserved",
        "hold",
    }:
        # Official status is allowed when routing to Official; wishlist bought ignores others.
        try:
            wishlist_status_or_raise(fields.status)
        except ValueError:
            pass
    if not fields.source and not fields.no_source:
        raise IntakeError(
            "Link/source required if available. Set source: URL or no_source: yes "
            "(or pass --source / --no-source)."
        )
    return fields


def compose_notes(fields: IntakeFields, route: str) -> str | None:
    bits: list[str] = []
    if fields.notes:
        bits.append(fields.notes)
    price = fields.price_original or fields.max_cost or fields.cost
    if price or fields.currency:
        bits.append(f"price_original={price or ''} {fields.currency or ''}".strip())
    if fields.qty_pieces and route != "official":
        bits.append(f"qty_pieces={fields.qty_pieces}")
    if route == "official":
        bits.append(f"requested_by={fields.requested_by}")
    bits.append("GF intake — still off Square until Boss Save")
    return "; ".join(bits)


def _wishlist_argv(args: argparse.Namespace, fields: IntakeFields, *, photo_link: str | None) -> list[str]:
    argv: list[str] = []
    if args.workbook:
        argv += ["-w", str(args.workbook)]
    if args.dry_run:
        argv.append("--dry-run")
    if fields.source:
        argv += ["--source", fields.source]
    else:
        argv.append("--no-source")
    argv += ["--status", fields.wishlist_status()]
    what_vi = fields.what_vi or fields.name_vi
    what_en = fields.what_en or fields.name_en
    if what_vi:
        argv += ["--what-vi", what_vi]
    if what_en:
        argv += ["--what-en", what_en]
    if fields.brand:
        argv += ["--brand", fields.brand]
    if fields.item_type:
        argv += ["--type", fields.item_type]
    if fields.size:
        argv += ["--size", fields.size]
    if fields.color:
        argv += ["--color", fields.color]
    cost = fields.max_cost or fields.price_original or fields.cost
    if cost:
        argv += ["--max-cost", cost]
    if fields.target_price or fields.list_price:
        argv += ["--target-price", fields.target_price or fields.list_price or ""]
    if fields.reason:
        argv += ["--reason", fields.reason]
    if fields.requested_by:
        argv += ["--requested-by", fields.requested_by]
    if fields.prefix:
        argv += ["--prefix", fields.prefix]
    if photo_link:
        argv += ["--photo-link", photo_link]
    notes = compose_notes(fields, fields.route())
    if notes:
        argv += ["--notes", notes]
    return argv


def _official_argv(args: argparse.Namespace, fields: IntakeFields, *, photo_link: str | None) -> list[str]:
    if not fields.ma:
        raise IntakeError(f"--ma is required for Official. {ASK_STOCK_MA}")
    argv: list[str] = ["--ma", fields.ma]
    if args.workbook:
        argv += ["-w", str(args.workbook)]
    if args.dry_run:
        argv.append("--dry-run")
    name_vi = fields.name_vi or fields.what_vi
    name_en = fields.name_en or fields.what_en
    if name_vi:
        argv += ["--name-vi", name_vi]
    if name_en:
        argv += ["--name-en", name_en]
    if fields.brand:
        argv += ["--brand", fields.brand]
    if fields.item_type:
        argv += ["--category", fields.item_type]
    if fields.size:
        argv += ["--size", fields.size]
    if fields.color:
        argv += ["--color", fields.color]
    if fields.qty_pieces:
        argv += ["--qty", fields.qty_pieces]
    cost = fields.cost or fields.price_original or fields.max_cost
    if cost:
        argv += ["--cost", cost]
    if fields.list_price or fields.target_price:
        argv += ["--list-price", fields.list_price or fields.target_price or ""]
    if fields.condition:
        argv += ["--condition", fields.condition]
    if fields.source:
        argv += ["--source", fields.source]
    if photo_link:
        argv += ["--photo-link", photo_link]
    if fields.status and fields.status.lower() not in SOT_WISHLIST_STATUS:
        argv += ["--status", fields.status]
    notes = compose_notes(fields, "official")
    if notes:
        argv += ["--notes", notes]
    return argv


def _bot_argv(args: argparse.Namespace, fields: IntakeFields, route: str) -> list[str]:
    bot = "Stock" if fields.kind == "bought" else "Scout"
    summary = f"GF intake {fields.display_what()} → {route} (draft only, off Square)"
    argv = ["--bot", bot, "--action", "intake_draft", "--summary", summary, "--status", "draft"]
    if args.workbook:
        argv += ["-w", str(args.workbook)]
    if args.dry_run:
        argv.append("--dry-run")
    if route == "official" and fields.ma:
        argv += ["--ma", fields.ma]
    return argv


def print_stay_off_square() -> None:
    print(STAY_OFF_SQUARE)
    print("ASK STOCK before any new mã. Slack #shop-decisions before Square Save.")


def print_reply(
    fields: IntakeFields,
    route: str,
    *,
    photo_link: str | None,
    planned: list[tuple[Path, str]],
    copied: bool,
) -> None:
    what = fields.display_what()
    if photo_link:
        photo_vi = f"Ảnh (share): {photo_link}"
        photo_en = f"Photo (share): {photo_link}"
    elif planned:
        names = ", ".join(name for _, name in planned)
        verb = "đã đổi tên" if copied else "sẽ đổi tên"
        photo_vi = (
            f"Ảnh {verb} trong Photos/: {names}. photo_link trống — "
            "Kit dán OneDrive share URL sau. Không trỏ vào folder From GF."
        )
        photo_en = (
            f"Photos {('renamed' if copied else 'would be renamed')} in Photos/: {names}. "
            "photo_link empty until Kit pastes the OneDrive share URL. Never From GF/."
        )
    else:
        photo_vi = "Chưa có ảnh trong packet."
        photo_en = "No photo in this packet."
    source_note = f"Link shop: {fields.source}" if fields.source else "Không có link shop (no_source)."
    if route == "official":
        ma_note = f"mã {fields.ma} (Boss/Stock gán — không phải script bịa)."
        print("--- Boss → GF draft (not sent) ---")
        print("VI:")
        print(
            f"Em ơi, món {what} đã vào Official với {ma_note}\n"
            "Đây là bản làm việc trên Excel — vẫn chưa Save Square.\n"
            f"{photo_vi}\nCảm ơn em đã gửi ảnh 💗"
        )
        print("EN:")
        print(
            f"{what} is on Official with {ma_note}\n"
            "Excel working copy only — still not a Square Save.\n"
            f"{photo_en}\nThank you for the photos 💗"
        )
        return
    if route == "wishlist_bought":
        ma_note = f"ASK STOCK: {ASK_STOCK_MA}"
        print("--- Boss → GF draft (not sent) ---")
        print("VI:")
        print(
            f"Em ơi, Boss biết em đã mua / đã nhận {what} rồi 💕\n"
            "Kit ghi Wishlist status = bought. Vẫn chưa lên Square.\n"
            f"Chưa có mã — Boss hỏi Stock. Không ai tự bịa mã.\n"
            f"{photo_vi}\n{source_note}\n{ma_note}"
        )
        print("EN:")
        print(
            f"Love, Boss has {what} as bought / received 💕\n"
            "Kit wrote Wishlist status = bought. Still off Square.\n"
            f"No mã yet — ASK STOCK. Nobody invents a code.\n"
            f"{photo_en}\n{source_note}\n{ma_note}"
        )
        return
    print("--- Boss → GF draft (not sent) ---")
    print("VI:")
    print(
        f"Em ơi, nhận đồ rồi 💕\n"
        f"Kit đã ghi Wishlist cho: {what}\n"
        "Đây là đang xem / ứng viên — chưa lên Square, chưa phải hàng shop đang bán.\n"
        f"{photo_vi}\n{source_note}\n"
        "Boss xác nhận với em: đúng món này không?"
    )
    print("EN:")
    print(
        f"Got your upload, love 💕\n"
        f"Kit staged a Wishlist row for: {what}\n"
        "Hunt / candidate — not on Square, not on-hand stock.\n"
        f"{photo_en}\n{source_note}\n"
        "Boss confirm: is this the right piece?"
    )


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "GF clothes intake: parse From GF packet (or flags), rename photos, "
            "append Wishlist/Official via existing append_* . Never invent mã. Never Square Save."
        ),
        epilog=(
            f"PRIMARY inbox: OneDrive {ONEDRIVE_FROM_GF}/ (GF self-upload). "
            "Kit watcher: excel-kit/sot/FROM_GF_WATCH.md. "
            "Contract: excel-kit/prompts/GF_CLOTHES_INTAKE.md. "
            "Dial Bot / Messenger are not intake. "
            + STAY_OFF_SQUARE
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    add_workbook_path_arg(parser)
    add_dry_run_arg(parser)
    parser.add_argument(
        "--from-gf",
        dest="from_gf",
        type=Path,
        default=None,
        help=f"packet folder from {ONEDRIVE_FROM_GF}/ (photos + INTAKE_TEMPLATE or note.txt)",
    )
    parser.add_argument(
        "--packet",
        dest="packet",
        type=Path,
        default=None,
        help="same schema as --from-gf (optional copy / backup packet)",
    )
    parser.add_argument(
        "--photos-out",
        "--photos-dir",
        dest="photos_out",
        type=Path,
        default=None,
        help=f"destination Photos/ (default: sibling of SoT or ./out/Photos). Never From GF.",
    )
    parser.add_argument("--photo-link", dest="photo_link", default=None, help="OneDrive Photos share URL")
    parser.add_argument("--kind", default=None, help="looking / candidate / watching / skip / bought")
    parser.add_argument("--status", default=None)
    parser.add_argument("--source", "--link", dest="source", default=None)
    parser.add_argument("--no-source", action="store_true")
    parser.add_argument("--what-vi", dest="what_vi", default=None)
    parser.add_argument("--what-en", dest="what_en", default=None)
    parser.add_argument("--name-vi", dest="name_vi", default=None)
    parser.add_argument("--name-en", dest="name_en", default=None)
    parser.add_argument("--brand", default=None)
    parser.add_argument("--type", dest="item_type", default=None, help=f"{list(CANDIDATE_TYPES)}")
    parser.add_argument("--size", default=None, help="Asia size + cm")
    parser.add_argument("--color", default=None)
    parser.add_argument("--price-original", dest="price_original", default=None)
    parser.add_argument("--currency", default=None)
    parser.add_argument("--qty", "--qty-pieces", dest="qty_pieces", default=None)
    parser.add_argument("--notes", default=None)
    parser.add_argument("--requested-by", dest="requested_by", default=None)
    parser.add_argument("--prefix", default=None, help="AO/QU/VA/AK/GI/PK/SET hint — not a mã")
    parser.add_argument("--ma", default=None, help="Boss/Stock-assigned mã only; forbidden on looking")
    parser.add_argument("--reason", default=None)
    parser.add_argument("--list-price", dest="list_price", default=None)
    parser.add_argument("--condition", default=None)
    parser.add_argument("--cost", default=None)
    parser.add_argument("--max-cost", dest="max_cost", default=None)
    parser.add_argument("--target-price", dest="target_price", default=None)
    parser.add_argument("--no-bot-activity", action="store_true", help="skip Bot_Activity draft")
    parser.add_argument("--no-reply", action="store_true", help="do not print Boss→GF draft")
    return parser


def resolve_packet_arg(args: argparse.Namespace) -> Path | None:
    from_gf = args.from_gf
    packet = args.packet
    if from_gf and packet:
        if Path(from_gf).expanduser().resolve() != Path(packet).expanduser().resolve():
            raise IntakeError("--from-gf and --packet point at different folders")
    path = from_gf or packet
    return Path(path) if path is not None else None


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        packet_dir: Path | None = None
        raw: dict[str, object] = {}
        packet_path = resolve_packet_arg(args)
        if packet_path is not None:
            loaded, packet_dir = load_packet_dir(packet_path)
            raw.update(loaded)
        elif args.kind is None and args.what_vi is None and args.what_en is None:
            raise IntakeError(
                "pass --from-gf / --packet and/or flags (--kind, --what-vi, --source or --no-source). "
                f"PRIMARY folder is OneDrive {ONEDRIVE_FROM_GF}/."
            )
        raw = _merge_raw({k: str(v) for k, v in raw.items()}, args)
        fields = build_fields(raw, packet_dir)
        route = fields.route()
        workbook = locate_sot(args.workbook)
        photos_dir = Path(args.photos_out) if args.photos_out else default_photos_out(workbook)
        if "from gf" in str(photos_dir).lower() or "from_gf" in str(photos_dir).lower():
            raise IntakeError(
                f"photos destination must be Photos/, not From GF: {photos_dir}"
            )
        sources = packet_photos(packet_dir) if packet_dir else []
        planned = plan_photo_copies(sources, photos_dir, ma=fields.ma if route == "official" else None)
        print(f"GF intake route: {route}  kind={fields.kind}  what={fields.display_what()}")
        print(f"  requested_by: {fields.requested_by}")
        if fields.source:
            print(f"  source: {fields.source}")
        else:
            print("  source: none (no_source)")
        if fields.ma:
            print(f"  mã: {fields.ma} (Boss/Stock assigned — not minted)")
        elif route == "wishlist_bought":
            print(f"  mã: none — {ASK_STOCK_MA}")
        else:
            print("  mã: none (correct for Wishlist)")
        if planned:
            print("  photos plan:")
            for src, name in planned:
                print(f"    {src.name} → {photos_dir / name}")
                if src.suffix.lower() not in {".jpg", ".jpeg"}:
                    print(
                        f"    note: {src.name} will be named {name} "
                        "(Photos/ uses .jpg names; Kit may convert later)"
                    )
        else:
            print("  photos: none in packet")
        photo_link = fields.photo_link
        if photo_link:
            print(f"  photo_link: {photo_link}")
        elif planned:
            print(
                "  photo_link: empty — Kit upload note: paste the OneDrive "
                f"{ONEDRIVE_PHOTOS}/ share URL after upload. Do not point SoT at From GF/."
            )
        else:
            print("  photo_link: omitted (optional)")

        copied = False
        if planned and not args.dry_run:
            copy_photos(planned, photos_dir)
            copied = True
            print(f"  copied {len(planned)} photo(s) → {photos_dir}")
        elif planned and args.dry_run:
            print("  dry-run: photos not copied")

        if route == "official":
            rc = append_official_row.main(_official_argv(args, fields, photo_link=photo_link))
        else:
            rc = append_wishlist_row.main(_wishlist_argv(args, fields, photo_link=photo_link))
        if rc != 0:
            return rc

        if not args.no_bot_activity:
            bot_rc = append_bot_activity.main(_bot_argv(args, fields, route))
            if bot_rc != 0:
                return bot_rc

        if not args.no_reply:
            print_reply(
                fields,
                route,
                photo_link=photo_link,
                planned=planned,
                copied=copied,
            )
        print_stay_off_square()
        if args.dry_run:
            print("dry-run: xlsx not saved, photos not copied")
        return 0
    except (IntakeError, WorkbookError, ValueError, MissingMaError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
