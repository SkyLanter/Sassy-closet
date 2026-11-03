"""Create out/ and refuse to continue when a Python package is missing.

Import this before openpyxl. A missing package exits with a message that
names the bootstrap command, and out/ already exists.
"""

from __future__ import annotations

import importlib
import sys
from pathlib import Path

BOOTSTRAP_COMMAND = "scripts/bootstrap_autolist.sh"


def missing_dependency_message(package: str) -> str:
    return (
        f"Missing Python package {package}. "
        f"Run {BOOTSTRAP_COMMAND} to recreate the auto-list venv."
    )


def ensure_runtime(out_dir: Path, modules: tuple[str, ...] = ("openpyxl",)) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    for name in modules:
        try:
            importlib.import_module(name)
        except ImportError:
            print(missing_dependency_message(name), file=sys.stderr)
            raise SystemExit(2) from None
