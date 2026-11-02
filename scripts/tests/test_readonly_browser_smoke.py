"""Read-only Playwright smoke: checks, dry-run, and the on-demand workflow."""
from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CHECKS = ROOT / "scripts" / "browser_smoke_checks.test.mjs"
RUNNER = ROOT / "scripts" / "readonly_browser_smoke.sh"
SMOKE = ROOT / "scripts" / "browser-smoke" / "smoke.mjs"
WORKFLOW = ROOT / ".github" / "workflows" / "readonly-browser-smoke.yml"


def _held():
    path = ROOT / "scripts" / "browser_smoke_held.py"
    spec = importlib.util.spec_from_file_location("browser_smoke_held", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_held_list_matches_curl_smoke_and_rejects_a_null_list() -> None:
    module = _held()
    doc = json.loads((ROOT / "data" / "held.json").read_text(encoding="utf-8"))
    codes = module.codes_from_doc(doc)
    assert codes[-1] == "Q02"
    assert "K03" in codes and len(codes) == len(set(codes))
    assert module.codes_from_doc({"heldIncomplete": ["k3"], "neverList": []}) == ["K03", "Q02"]
    try:
        module.codes_from_doc({"heldIncomplete": None, "neverList": []})
    except ValueError as err:
        assert "heldIncomplete" in str(err)
    else:
        raise AssertionError("null heldIncomplete should fail")


def test_check_module() -> None:
    got = subprocess.run(
        ["node", "--test", str(CHECKS)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert got.returncode == 0, got.stdout + got.stderr


def test_dry_run_lists_checks_without_playwright(tmp_path: Path) -> None:
    env = {
        **os.environ,
        "SHOP_HOSTS": "https://shop.example",
        "INTAKE_BASE": "https://intake.example",
        "HELD_MAS": "k3",
        "NODE_PATH": str(tmp_path),
    }
    got = subprocess.run(
        ["bash", str(RUNNER), "--dry-run"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
        env=env,
    )
    assert got.returncode == 0, got.stdout + got.stderr
    assert "DRY RUN" in got.stdout
    assert "https://shop.example/m/K03 -> 404" in got.stdout
    assert "https://shop.example/m/S06 -> 200" in got.stdout
    assert "https://intake.example/ -> noindex" in got.stdout
    assert "playwright" not in got.stdout.lower()


def test_unknown_arg_and_two_modes() -> None:
    bad = subprocess.run(["bash", str(RUNNER), "--live"], capture_output=True, text=True, check=False)
    assert bad.returncode == 2
    both = subprocess.run(
        ["bash", str(RUNNER), "--dry-run", "--self-test"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert both.returncode == 2


def test_smoke_script_is_get_only() -> None:
    text = SMOKE.read_text(encoding="utf-8")
    assert "chromium.launch" in text
    assert "page.goto" in text
    assert "javaScriptEnabled: false" in text
    assert "route.abort" in text
    assert "await import(\"playwright\")" in text
    for bad in ("request.post", ".post(", ".fill(", ".click(", "storageState", "setExtraHTTPHeaders", "httpCredentials"):
        assert bad not in text, bad


def test_workflow_is_manual_and_read_only() -> None:
    text = WORKFLOW.read_text(encoding="utf-8")
    assert "workflow_dispatch:" in text
    assert "pull_request" not in text
    assert "schedule:" not in text
    assert "permissions:\n  contents: read\n" in text
    assert "persist-credentials: false" in text
    assert "bash scripts/readonly_browser_smoke.sh --self-test" in text
    assert "bash scripts/readonly_browser_smoke.sh\n" in text
    assert "secrets." not in text
    for bad in ("git push", "gh pr", "vercel", "BLOB_", "META_", "SQUARE", "held.json", ": write"):
        assert bad not in text, bad
