"""Bootstrap command and the pre-import dependency check. No live calls."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from runtime_check import BOOTSTRAP_COMMAND, ensure_runtime, missing_dependency_message

ROOT = Path(__file__).resolve().parents[2]


def test_missing_package_creates_out_and_names_bootstrap(tmp_path: Path) -> None:
    out = tmp_path / "out"
    try:
        ensure_runtime(out, ("no_such_package_zz",))
    except SystemExit as error:
        assert error.code == 2
    else:
        raise AssertionError("missing package did not exit")
    assert out.is_dir()
    assert BOOTSTRAP_COMMAND in missing_dependency_message("openpyxl")


def test_freshness_import_checks_before_openpyxl() -> None:
    text = (ROOT / "scripts" / "freshness_check.py").read_text(encoding="utf-8")
    assert text.index("ensure_runtime") < text.index("from openpyxl import")


def test_missing_openpyxl_on_import_has_no_traceback(tmp_path: Path) -> None:
    script = tmp_path / "block_openpyxl.py"
    script.write_text(
        "\n".join(
            [
                "import importlib.machinery",
                "import sys",
                "class Loader:",
                "    def create_module(self, spec):",
                "        return None",
                "    def exec_module(self, module):",
                "        raise ModuleNotFoundError('no openpyxl')",
                "class Finder:",
                "    def find_spec(self, fullname, path, target=None):",
                "        if fullname == 'openpyxl' or fullname.startswith('openpyxl.'):",
                "            return importlib.machinery.ModuleSpec(fullname, Loader())",
                "        return None",
                "sys.meta_path.insert(0, Finder())",
                "sys.path.insert(0, 'scripts')",
                "import freshness_check",
                "",
            ]
        ),
        encoding="utf-8",
    )
    ran = subprocess.run(
        [sys.executable, str(script)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert ran.returncode == 2, ran.stderr
    assert BOOTSTRAP_COMMAND in ran.stderr
    assert "Traceback" not in ran.stderr
    assert (ROOT / "out").is_dir()


def test_bootstrap_recreates_venv_and_installs_pytest() -> None:
    script = ROOT / "scripts" / "bootstrap_autolist.sh"
    text = script.read_text(encoding="utf-8")
    requirements = (ROOT / "requirements.txt").read_text(encoding="utf-8")
    assert "pytest" in requirements
    assert "rm -rf .venv" in text
    assert "python3 -m venv .venv" in text
    assert "pip install -r requirements.txt" in text
    assert "mkdir -p out" in text
    checked = subprocess.run(["sh", "-n", str(script)], check=False, capture_output=True, text=True)
    assert checked.returncode == 0, checked.stderr
    assert os.access(script, os.X_OK)
