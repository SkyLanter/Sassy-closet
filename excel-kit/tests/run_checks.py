#!/usr/bin/env python3
"""Kit checks: py_compile, CLI --help, no fake inventory in git.

Run from repo root:
  python3 excel-kit/tests/run_checks.py
"""

from __future__ import annotations

import csv
import py_compile
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
KIT = REPO / "excel-kit"
if str(KIT) not in sys.path:
    sys.path.insert(0, str(KIT))

from schema import (  # noqa: E402
    ASK_STOCK_MA,
    CANDIDATES,
    MA_LIST,
    ORDER_STATUS,
    SOT_DASHBOARD_BRIEF_CELL,
    SOT_WISHLIST,
    SQUARE_IMPORT_HEADERS,
    MissingMaError,
    looks_like_demo_row,
    require_ma,
)

SCRIPTS = [
    KIT / "schema.py",
    KIT / "clean_sot_demo.py",
    KIT / "build_boutique_desktop.py",
    KIT / "sot" / "workbook.py",
    KIT / "sot" / "append_official_row.py",
    KIT / "sot" / "append_wishlist_row.py",
    KIT / "sot" / "append_order_row.py",
    KIT / "sot" / "append_bot_activity.py",
    KIT / "sot" / "dashboard_brief.py",
    KIT / "sot" / "build_sot_desktop.py",
    KIT / "square" / "validate_import.py",
    KIT / "tests" / "run_checks.py",
]

CLIS = [
    KIT / "clean_sot_demo.py",
    KIT / "build_boutique_desktop.py",
    KIT / "sot" / "append_official_row.py",
    KIT / "sot" / "append_wishlist_row.py",
    KIT / "sot" / "append_order_row.py",
    KIT / "sot" / "append_bot_activity.py",
    KIT / "sot" / "dashboard_brief.py",
    KIT / "sot" / "build_sot_desktop.py",
    KIT / "square" / "validate_import.py",
]

FAKE_TOKENS = (
    "fake stock",
    "demo buyer",
    "test buyer",
    "ao999",
    "qu999",
    "va999",
    "~25 sample",
)


def _run(args: list[str], *, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        args,
        cwd=cwd or REPO,
        text=True,
        capture_output=True,
        check=False,
    )


def check_py_compile() -> None:
    for path in SCRIPTS:
        py_compile.compile(str(path), doraise=True)
    print(f"py_compile ok ({len(SCRIPTS)} files)")


def check_help() -> None:
    for path in CLIS:
        proc = _run([sys.executable, str(path), "--help"])
        if proc.returncode != 0:
            raise AssertionError(f"{path.name} --help failed:\n{proc.stderr}")
        if "usage:" not in proc.stdout.lower() and "usage:" not in proc.stderr.lower():
            raise AssertionError(f"{path.name} --help produced no usage")
    print(f"--help ok ({len(CLIS)} CLIs)")


def check_schema_contract() -> None:
    assert MA_LIST[-1] == "photo_link"
    assert CANDIDATES[-1] == "photo_link"
    assert SOT_WISHLIST[-1] == "photo_link"
    assert "source" in SOT_WISHLIST
    assert ORDER_STATUS == (
        "Inquiry",
        "Reserved",
        "Paid",
        "Shipped",
        "Picked up",
        "Cancelled",
    )
    assert SOT_DASHBOARD_BRIEF_CELL == "B43"
    try:
        require_ma(None)
        raise AssertionError("require_ma(None) must fail")
    except MissingMaError as exc:
        assert "Ask Stock" in str(exc) or "ask Stock" in str(exc) or "ASK" in ASK_STOCK_MA
    assert require_ma("ao015") == "AO015"
    assert looks_like_demo_row(["AO999", "demo buyer"]) is True
    assert looks_like_demo_row(["", None, ""]) is False
    print("schema contract ok")


def check_no_fake_inventory_in_git() -> None:
    skip_suffix = {".md", ".py"}
    # Markdown/prompts may mention AO999 as a forbidden example — that is not a data row.
    # Scan committed non-doc payloads (csv / json / xlsx would be the leak).
    leaked: list[str] = []
    for path in REPO.rglob("*"):
        if not path.is_file():
            continue
        if ".git" in path.parts or "out" in path.parts or "__pycache__" in path.parts:
            continue
        if path.suffix.lower() == ".xlsx":
            leaked.append(f"committed xlsx (forbidden): {path.relative_to(REPO)}")
            continue
        if path.suffix.lower() not in {".csv", ".tsv", ".json"}:
            continue
        text = path.read_text(encoding="utf-8", errors="replace").lower()
        for token in FAKE_TOKENS:
            if token in text:
                leaked.append(f"{path.relative_to(REPO)} contains {token!r}")
    if leaked:
        raise AssertionError("fake inventory in git:\n  " + "\n  ".join(leaked))
    print("no fake inventory rows committed")


def check_square_template() -> None:
    path = KIT / "square" / "square_import_template.csv"
    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.reader(handle)
        rows = [r for r in reader if any(c.strip() for c in r)]
    if len(rows) != 1:
        raise AssertionError(f"square template must be headers-only, got {len(rows)} rows")
    headers = rows[0]
    for required in ("Token", "Item Name", "Variation Name", "SKU", "Stockable"):
        if required not in headers:
            raise AssertionError(f"square template missing {required}")
    proc = _run([sys.executable, str(KIT / "square" / "validate_import.py"), str(path)])
    if proc.returncode != 0:
        raise AssertionError(proc.stdout + proc.stderr)
    if "headers-only" not in proc.stdout:
        raise AssertionError("validate_import should report headers-only")
    print("square template headers-only ok")


def check_builders_and_append() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp)
        sot = _run([sys.executable, str(KIT / "sot" / "build_sot_desktop.py"), "--out-dir", str(out)])
        if sot.returncode != 0:
            raise AssertionError(sot.stdout + sot.stderr)
        book = out / "Sassy_Closet_SoT.xlsx"
        if not book.is_file():
            raise AssertionError("SoT builder did not write Sassy_Closet_SoT.xlsx")

        desk = _run([sys.executable, str(KIT / "build_boutique_desktop.py"), "--out-dir", str(out)])
        if desk.returncode != 0:
            raise AssertionError(desk.stdout + desk.stderr)

        missing = _run(
            [
                sys.executable,
                str(KIT / "sot" / "append_official_row.py"),
                "-w",
                str(book),
                "--name-vi",
                "should fail",
            ]
        )
        if missing.returncode == 0:
            raise AssertionError("Official append without --ma must fail")
        err = missing.stderr + missing.stdout
        if "ma" not in err.lower() and "mã" not in err.lower():
            raise AssertionError(f"missing-mã error unclear:\n{err}")

        bad_ma = _run(
            [
                sys.executable,
                str(KIT / "sot" / "append_official_row.py"),
                "-w",
                str(book),
                "--ma",
                "SHIRT1",
            ]
        )
        if bad_ma.returncode == 0:
            raise AssertionError("invented / invalid mã must fail")

        ok = _run(
            [
                sys.executable,
                str(KIT / "sot" / "append_official_row.py"),
                "-w",
                str(book),
                "--ma",
                "AO001",
                "--name-vi",
                "Áo test-harness",
                "--size",
                "M",
                "--color",
                "đen",
                "--qty",
                "1",
                "--status",
                "Available",
            ]
        )
        if ok.returncode != 0:
            raise AssertionError(ok.stdout + ok.stderr)

        dup = _run(
            [
                sys.executable,
                str(KIT / "sot" / "append_official_row.py"),
                "-w",
                str(book),
                "--ma",
                "AO001",
                "--name-vi",
                "dup",
            ]
        )
        if dup.returncode == 0:
            raise AssertionError("duplicate mã must fail")

        wish_fail = _run(
            [
                sys.executable,
                str(KIT / "sot" / "append_wishlist_row.py"),
                "-w",
                str(book),
                "--what-vi",
                "no link",
            ]
        )
        if wish_fail.returncode == 0:
            raise AssertionError("wishlist without source/--no-source must fail")

        wish_ok = _run(
            [
                sys.executable,
                str(KIT / "sot" / "append_wishlist_row.py"),
                "-w",
                str(book),
                "--source",
                "https://item.taobao.com/item.htm?id=1",
                "--what-vi",
                "Váy harness",
                "--status",
                "candidate",
            ]
        )
        if wish_ok.returncode != 0:
            raise AssertionError(wish_ok.stdout + wish_ok.stderr)

        order_bad = _run(
            [
                sys.executable,
                str(KIT / "sot" / "append_order_row.py"),
                "-w",
                str(book),
                "--status",
                "Maybe",
            ]
        )
        if order_bad.returncode == 0:
            raise AssertionError("invalid order status must fail")

        order_ok = _run(
            [
                sys.executable,
                str(KIT / "sot" / "append_order_row.py"),
                "-w",
                str(book),
                "--status",
                "Inquiry",
                "--ma",
                "AO001",
                "--channel",
                "Facebook",
            ]
        )
        if order_ok.returncode != 0:
            raise AssertionError(order_ok.stdout + order_ok.stderr)

        bot_ok = _run(
            [
                sys.executable,
                str(KIT / "sot" / "append_bot_activity.py"),
                "-w",
                str(book),
                "--bot",
                "Stock",
                "--action",
                "draft",
                "--summary",
                "harness log",
                "--ma",
                "AO001",
            ]
        )
        if bot_ok.returncode != 0:
            raise AssertionError(bot_ok.stdout + bot_ok.stderr)

        # Lean Official desktop always has Bot_Activity; strip it to prove skip-note.
        from openpyxl import load_workbook

        skip_book = out / "no_bot.xlsx"
        wb = load_workbook(book)
        if "Bot_Activity" in wb.sheetnames:
            del wb["Bot_Activity"]
        wb.save(skip_book)
        wb.close()
        skip = _run(
            [
                sys.executable,
                str(KIT / "sot" / "append_bot_activity.py"),
                "-w",
                str(skip_book),
                "--bot",
                "Stock",
                "--action",
                "draft",
                "--summary",
                "should skip",
            ]
        )
        if skip.returncode != 0:
            raise AssertionError(skip.stdout + skip.stderr)
        if "skipped" not in (skip.stdout + skip.stderr).lower():
            raise AssertionError(f"expected skip note, got:\n{skip.stdout}\n{skip.stderr}")

        brief = _run([sys.executable, str(KIT / "sot" / "dashboard_brief.py"), "-w", str(book)])
        if brief.returncode != 0:
            raise AssertionError(brief.stdout + brief.stderr)
        blob = brief.stdout + brief.stderr
        if "B43" not in blob:
            raise AssertionError("dashboard_brief must mention B43")

        clean = _run(
            [sys.executable, str(KIT / "clean_sot_demo.py"), str(book), "--check"]
        )
        if clean.returncode != 0:
            raise AssertionError(clean.stdout + clean.stderr)

    print("builders + append CLIs ok")


def main() -> int:
    try:
        check_py_compile()
        check_help()
        check_schema_contract()
        check_no_fake_inventory_in_git()
        check_square_template()
        check_builders_and_append()
    except Exception as exc:  # noqa: BLE001 — kit runner prints and exits
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    print("all excel-kit checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
