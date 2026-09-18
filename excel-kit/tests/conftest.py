"""Put excel-kit on sys.path so tests import schema / builder modules."""

from __future__ import annotations

import sys
from pathlib import Path

KIT = Path(__file__).resolve().parents[1]
if str(KIT) not in sys.path:
    sys.path.insert(0, str(KIT))
