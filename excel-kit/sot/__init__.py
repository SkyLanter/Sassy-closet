"""SoT automation for the ONE desktop workbook: Sassy_Closet_SoT.xlsx.

Square Free = on-hand inventory source of truth.
Official Excel = working copy / mã index / captions — not a second stock.
Scripts never invent mã. Photos are photo_link only (no embeds).
"""

from __future__ import annotations

from .workbook import (
    WorkbookError,
    append_mapped_row,
    locate_sot,
    open_sot,
    require_sheet,
)

__all__ = [
    "WorkbookError",
    "append_mapped_row",
    "locate_sot",
    "open_sot",
    "require_sheet",
]
