"""List catalog mãs that already store more than one color.

Read-only. Pass a catalog.v1 JSON path. Each color id and name is copied
from the stored entry. A blank name stays blank. A comma inside one name
stays one color. Image color ids are not added. Hex is not turned into a
name. Nothing is written: not the catalog, not a price, not data/held.json.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from held_policy import norm_ma

MA_RE = re.compile(r"^[A-Z][0-9]{2}$")


@dataclass(frozen=True)
class StoredColor:
    id: str
    name: str


@dataclass(frozen=True)
class MultiColorMa:
    ma: str
    status: str
    price_usd: object
    colors: tuple[StoredColor, ...]

    def as_json(self) -> dict[str, object]:
        return {
            "ma": self.ma,
            "status": self.status,
            "priceUsd": self.price_usd,
            "count": len(self.colors),
            "colors": [{"id": color.id, "name": color.name} for color in self.colors],
        }


def list_multi_color(document: dict[str, object]) -> list[MultiColorMa]:
    """Return mãs whose stored color list has more than one entry.

    The document is not modified. Colors are not added, renamed, or merged.
    """
    products = document.get("products")
    if not isinstance(products, list):
        return []
    listed: list[MultiColorMa] = []
    for raw in products:
        if not isinstance(raw, dict):
            continue
        code = _ma(raw.get("ma"))
        colors = _stored_colors(raw.get("colors"))
        if code is None or len(colors) < 2:
            continue
        status = raw.get("status")
        listed.append(
            MultiColorMa(
                ma=code,
                status=status if isinstance(status, str) else "",
                price_usd=raw.get("priceUsd", None),
                colors=tuple(colors),
            )
        )
    return listed


def _ma(value: object) -> str | None:
    if not isinstance(value, str):
        return None
    code = norm_ma(value)
    if MA_RE.fullmatch(code) is None:
        return None
    return code


def _stored_colors(value: object) -> list[StoredColor]:
    if not isinstance(value, list):
        return []
    colors: list[StoredColor] = []
    for item in value:
        color = _stored_color(item)
        if color is not None:
            colors.append(color)
    return colors


def _stored_color(item: object) -> StoredColor | None:
    if isinstance(item, str):
        return StoredColor(id="", name=item)
    if not isinstance(item, dict):
        return None
    color_id = item.get("id")
    name = item.get("name")
    return StoredColor(
        id=color_id if isinstance(color_id, str) else "",
        name=name if isinstance(name, str) else "",
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="List catalog mãs with more than one stored color. Read-only."
    )
    parser.add_argument(
        "--catalog",
        required=True,
        help="Path to a catalog.v1 JSON file. The file is only read.",
    )
    args = parser.parse_args(argv)
    path = Path(args.catalog)
    try:
        document = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        print(f"Cannot read catalog: {error}", file=sys.stderr)
        return 2
    if not isinstance(document, dict):
        print("Catalog must be a JSON object.", file=sys.stderr)
        return 2
    rows = list_multi_color(document)
    json.dump([row.as_json() for row in rows], sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
