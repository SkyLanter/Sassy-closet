"""Flag intake rows whose photo fields are blank or unusable.

Read a JSON fixture and write a report. Photo bytes stay untouched.
S06 stays $25. Held mãs stay held. This module does not upload, delete,
or rewrite photos, and it does not write intake, Blob, Meta, Square,
data/held.json, prices, or catalog rows.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parent
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from held_policy import HeldPolicy, load_held_policy

_IMAGE_RE = re.compile(
    r"^[A-Za-z0-9][A-Za-z0-9_-]*(?:/[A-Za-z0-9][A-Za-z0-9_-]*)*\.(?:jpe?g|png|webp)$",
    re.IGNORECASE,
)
_HASH_RE = re.compile(r"^[0-9a-fA-F]{64}$")
_BLANK = frozenset(
    {
        "",
        "none",
        "n/a",
        "na",
        "null",
        "undefined",
        "blank",
        "missing",
        "todo",
        "tbd",
        "-",
        "—",
        "nil",
    }
)
_EMPTY_SHA = hashlib.sha256(b"").hexdigest()
_MISSING = object()


@dataclass(frozen=True)
class PhotoFlag:
    ma: str
    kind: str
    field: str
    stored: str
    reason: str
    held: bool

    def as_json(self) -> dict[str, object]:
        return {
            "ma": self.ma,
            "kind": self.kind,
            "field": self.field,
            "stored": self.stored,
            "reason": self.reason,
            "held": self.held,
        }


@dataclass(frozen=True)
class PhotoRow:
    ma: str
    held: bool
    sell_usd: str | None
    usable_photos: int
    flags: tuple[PhotoFlag, ...]

    def as_json(self) -> dict[str, object]:
        return {
            "ma": self.ma,
            "held": self.held,
            "sellUsd": self.sell_usd,
            "usablePhotos": self.usable_photos,
            "flags": [flag.as_json() for flag in self.flags],
        }


@dataclass(frozen=True)
class PhotoReport:
    rows: tuple[PhotoRow, ...]

    @property
    def flags(self) -> tuple[PhotoFlag, ...]:
        return tuple(flag for row in self.rows for flag in row.flags)

    @property
    def flag_count(self) -> int:
        return len(self.flags)


def flag_intake_photos(rows: list[dict[str, object]], policy: HeldPolicy) -> PhotoReport:
    """Return flags. Leave every input row as it was passed in."""
    checked: list[PhotoRow] = []
    for row in rows:
        if not isinstance(row, dict) or not isinstance(row.get("ma"), str) or row.get("ma", "").strip() == "":
            raise ValueError("fixture intake row needs a mã")
        checked.append(_flag_row(row, policy))
    return PhotoReport(tuple(checked))


def load_rows(payload: object) -> list[dict[str, object]]:
    if isinstance(payload, list):
        rows = payload
    elif isinstance(payload, dict) and isinstance(payload.get("submissions"), list):
        rows = payload["submissions"]
    elif isinstance(payload, dict) and isinstance(payload.get("intake"), list):
        rows = payload["intake"]
    else:
        raise ValueError("fixture must be a list or an object with submissions")
    if not all(isinstance(row, dict) for row in rows):
        raise ValueError("fixture intake row needs a mã")
    return rows


def render_markdown(report: PhotoReport) -> str:
    lines = [
        "# Intake photo flags",
        "",
        "Read-only copy of fixture photo fields. Photo bytes stay untouched.",
        "S06 stays $25. Held mãs stay held.",
        "",
        f"Rows: {len(report.rows)}",
        f"Flags: {report.flag_count}",
        "",
        "## Flags",
        "",
    ]
    if not report.flags:
        lines.append("None.")
    else:
        for flag in report.flags:
            hold = " stays held" if flag.held else ""
            lines.append(
                f"- {flag.ma} {flag.kind} `{flag.field}` {flag.reason}: "
                f"stored `{_md(flag.stored)}`{hold}"
            )
    lines.extend(
        [
            "",
            "## Rows",
            "",
            "mã | held | usable photos | sell | flags",
            "--- | --- | --- | --- | ---",
        ]
    )
    for row in report.rows:
        kinds = ", ".join(flag.kind for flag in row.flags) or "—"
        sell = "—" if row.sell_usd is None else _md(row.sell_usd)
        lines.append(
            f"{row.ma} | {str(row.held).lower()} | {row.usable_photos} | {sell} | {kinds}"
        )
    lines.append("")
    return "\n".join(lines)


def report_json(report: PhotoReport) -> dict[str, object]:
    return {
        "readOnly": True,
        "photoBytes": "untouched",
        "s06": "stays $25",
        "heldMas": "stay held",
        "flagCount": report.flag_count,
        "flags": [flag.as_json() for flag in report.flags],
        "rows": [row.as_json() for row in report.rows],
    }


def write_report(report: PhotoReport, out_dir: Path) -> tuple[Path, Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    markdown_path = out_dir / "intake-photo-flags.md"
    json_path = out_dir / "intake-photo-flags.json"
    markdown_path.write_text(render_markdown(report), encoding="utf-8")
    json_path.write_text(json.dumps(report_json(report), indent=2) + "\n", encoding="utf-8")
    return markdown_path, json_path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Flag blank or unusable intake photo fields in a fixture. Writes a report only.",
    )
    parser.add_argument("--fixture", required=True, help="Path to a JSON fixture. Live intake is not read.")
    parser.add_argument("--out", required=True, help="Directory for the markdown report and JSON sibling.")
    parser.add_argument("--held", default="", help="Held-list JSON to read. Defaults to data/held.json.")
    args = parser.parse_args(argv)
    if _is_live_target(args.fixture) or _is_live_target(args.held):
        print("Live intake is not read. Pass a fixture file.", file=sys.stderr)
        return 2
    fixture = Path(args.fixture)
    if not fixture.is_file():
        print(f"Fixture not found: {fixture}", file=sys.stderr)
        return 2
    try:
        payload = json.loads(fixture.read_text(encoding="utf-8"))
        rows = load_rows(payload)
        policy = load_held_policy(Path(args.held) if args.held else None)
        report = flag_intake_photos(rows, policy)
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as error:
        print(str(error), file=sys.stderr)
        return 2
    markdown_path, _json_path = write_report(report, Path(args.out))
    print(f"Intake photo flags: {report.flag_count}")
    print(f"report: {markdown_path}")
    return 1 if report.flag_count else 0


def _flag_row(row: dict[str, object], policy: HeldPolicy) -> PhotoRow:
    ma = str(row["ma"]).strip().upper()
    held = policy.skip_reason(ma) == "held"
    sell = row.get("sell_usd")
    sell_usd = None if sell is None else sell if isinstance(sell, str) else str(sell)
    field_name, raw = _path_source(row)
    flags, reasons = _path_flags(ma, held, field_name, raw)
    flags.extend(_hash_flags(ma, held, row, reasons))
    flags.extend(_piece_flags(ma, held, row.get("pieces", _MISSING), reasons))
    return PhotoRow(ma, held, sell_usd, _usable_count(row, reasons), tuple(flags))


def _path_source(row: dict[str, object]) -> tuple[str, object]:
    if "photo_paths" in row:
        return "photo_paths", row["photo_paths"]
    if "photos" in row:
        return "photos", row["photos"]
    return "photo_paths", _MISSING


def _path_flags(
    ma: str,
    held: bool,
    field_name: str,
    raw: object,
) -> tuple[list[PhotoFlag], list[str | None] | None]:
    if raw is _MISSING:
        return [_blank(ma, held, field_name, "", "missing")], None
    if raw is None:
        return [_blank(ma, held, field_name, "null", "null")], None
    if isinstance(raw, str) and raw.strip().casefold() in _BLANK:
        return [_blank(ma, held, field_name, raw, "blank")], None
    if not isinstance(raw, list):
        return [PhotoFlag(ma, "unusable_photo", field_name, _stored(raw), "not_a_list", held)], None
    if raw == [] or all(_is_blank_item(item) for item in raw):
        reason = "empty" if raw == [] else "blank"
        return [_blank(ma, held, field_name, _stored(raw), reason)], None
    reasons = [_classify_path(ma, item) for item in raw]
    flags = [
        PhotoFlag(ma, "unusable_photo", f"{field_name}[{index}]", _stored(raw[index]), reason, held)
        for index, reason in enumerate(reasons)
        if reason is not None
    ]
    return flags, reasons


def _usable_count(row: dict[str, object], reasons: list[str | None] | None) -> int:
    if reasons is None:
        return 0
    raw = row.get("photo_hashes", _MISSING)
    if not isinstance(raw, list) or len(raw) != len(reasons):
        return 0
    return sum(
        1
        for index, reason in enumerate(reasons)
        if reason is None and _classify_hash(raw[index]) is None
    )


def _hash_flags(
    ma: str,
    held: bool,
    row: dict[str, object],
    reasons: list[str | None] | None,
) -> list[PhotoFlag]:
    present = "photo_hashes" in row
    raw = row.get("photo_hashes", _MISSING)
    if reasons is None:
        if not present or _hash_field_blank(raw):
            return []
        if not isinstance(raw, list):
            return [PhotoFlag(ma, "unusable_hash", "photo_hashes", _stored(raw), "not_a_list", held)]
        return _hash_items(ma, held, raw)
    if not present or _hash_field_blank(raw):
        stored, reason = _blank_hash_detail(present, raw)
        return [_blank_hash(ma, held, stored, reason)]
    if not isinstance(raw, list):
        return [PhotoFlag(ma, "unusable_hash", "photo_hashes", _stored(raw), "not_a_list", held)]
    flags: list[PhotoFlag] = []
    if len(raw) != len(reasons):
        flags.append(
            PhotoFlag(
                ma,
                "unusable_hash",
                "photo_hashes",
                f"{len(reasons)} paths, {len(raw)} hashes",
                "length",
                held,
            )
        )
    flags.extend(_hash_items(ma, held, raw))
    return flags


def _hash_items(ma: str, held: bool, raw: list[object]) -> list[PhotoFlag]:
    flags: list[PhotoFlag] = []
    for index, item in enumerate(raw):
        reason = _classify_hash(item)
        if reason is not None:
            flags.append(PhotoFlag(ma, "unusable_hash", f"photo_hashes[{index}]", _stored(item), reason, held))
    return flags


def _piece_flags(
    ma: str,
    held: bool,
    raw: object,
    reasons: list[str | None] | None,
) -> list[PhotoFlag]:
    if raw is _MISSING:
        return []
    if not isinstance(raw, list):
        return [PhotoFlag(ma, "unusable_piece_photo", "pieces", _stored(raw), "not_a_list", held)]
    flags: list[PhotoFlag] = []
    for piece_index, piece in enumerate(raw):
        if not isinstance(piece, dict) or "photos" not in piece:
            continue
        photos = piece.get("photos")
        field = f"pieces[{piece_index}].photos"
        if not isinstance(photos, list):
            flags.append(PhotoFlag(ma, "unusable_piece_photo", field, _stored(photos), "not_a_list", held))
            continue
        for photo_index, item in enumerate(photos):
            reason = _classify_index(item, reasons)
            if reason is None:
                continue
            flags.append(
                PhotoFlag(
                    ma,
                    "unusable_piece_photo",
                    f"{field}[{photo_index}]",
                    _stored(item),
                    reason,
                    held,
                )
            )
    return flags


def _classify_index(item: object, reasons: list[str | None] | None) -> str | None:
    if isinstance(item, bool) or not isinstance(item, int):
        return "not_an_index"
    if reasons is None or item < 0 or item >= len(reasons):
        return "out_of_range"
    if reasons[item] is not None:
        return "points_at_unusable"
    return None


def _classify_path(ma: str, value: object) -> str | None:
    if _is_blank_item(value):
        return "blank_entry"
    if not isinstance(value, str):
        return "not_a_string"
    if value != value.strip():
        return "spaced"
    if "\x00" in value or ".." in value or "\\" in value:
        return "traversal"
    if ":" in value:
        return "remote"
    if value.startswith("/"):
        return "absolute"
    if _IMAGE_RE.fullmatch(value) is None or "/" not in value:
        return "not_image"
    folder = value.split("/", 1)[0]
    if folder.upper() != ma:
        return "wrong_ma"
    return None


def _classify_hash(value: object) -> str | None:
    if _is_blank_item(value):
        return "blank_entry"
    if not isinstance(value, str):
        return "not_a_string"
    if value != value.strip():
        return "spaced"
    if _HASH_RE.fullmatch(value) is None:
        return "not_sha256"
    if value.lower() == _EMPTY_SHA:
        return "empty_file"
    return None


def _is_blank_item(value: object) -> bool:
    if value is None:
        return True
    return isinstance(value, str) and value.strip().casefold() in _BLANK


def _blank(ma: str, held: bool, field_name: str, stored: str, reason: str) -> PhotoFlag:
    return PhotoFlag(ma, "blank_photos", field_name, stored, reason, held)


def _blank_hash(ma: str, held: bool, stored: str, reason: str) -> PhotoFlag:
    return PhotoFlag(ma, "blank_hashes", "photo_hashes", stored, reason, held)


def _hash_field_blank(raw: object) -> bool:
    if raw is None or raw == []:
        return True
    return isinstance(raw, str) and raw.strip().casefold() in _BLANK


def _blank_hash_detail(present: bool, raw: object) -> tuple[str, str]:
    if not present:
        return "", "missing"
    if raw is None:
        return "null", "null"
    if raw == []:
        return "[]", "empty"
    return _stored(raw), "blank"


def _stored(value: object) -> str:
    if isinstance(value, str):
        return value
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"))


def _md(value: str) -> str:
    return value.replace("`", "'")


def _is_live_target(value: str) -> bool:
    text = value.strip().casefold()
    return "://" in text or text.startswith("blob:") or text.startswith("http")


if __name__ == "__main__":
    raise SystemExit(main())
