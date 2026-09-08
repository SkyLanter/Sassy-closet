#!/usr/bin/env python3
"""Compatibility wrapper. Floor tracker lives in build_floor_track.py.

Boss 2026-09-07 ~10:24 PT: land Sassy_Closet_Track.xlsx, not the 20-column dump.
"""

from __future__ import annotations

import sys
from pathlib import Path

_KIT_DIR = Path(__file__).resolve().parent
if str(_KIT_DIR) not in sys.path:
    sys.path.insert(0, str(_KIT_DIR))

from build_floor_track import main

if __name__ == "__main__":
    raise SystemExit(main())
