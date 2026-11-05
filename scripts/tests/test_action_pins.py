"""Third-party actions are pinned to the commit the major tag resolved to."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WF = ROOT / ".github" / "workflows"
REQUIRED = (
    "dataset-checks.yml",
    "excel-kit.yml",
    "sassy-closet.yml",
    "sassy-closet-shop.yml",
)
CHECKOUT = "actions/checkout@11d5960a326750d5838078e36cf38b85af677262 # v4.4.0"
SETUP_NODE = "actions/setup-node@49933ea5288caeca8642d1e84afbd3f7d6820020 # v4.4.0"
SETUP_PYTHON = "actions/setup-python@a26af69be951a213d495a4c3e4e4022e16d87065 # v5.6.0"
_PINNED = re.compile(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_./-]+@[0-9a-f]{40}\Z")
_ACTION_AT = re.compile(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_./-]+@")


def _code(line: str) -> str:
    out: list[str] = []
    quote = ""
    for ch in line:
        if quote:
            out.append(ch)
            if ch == quote:
                quote = ""
            continue
        if ch in "'\"":
            quote = ch
            out.append(ch)
            continue
        if ch == "#":
            break
        out.append(ch)
    return "".join(out).rstrip()


def _uses_value(line: str) -> str | None:
    stripped = line.strip()
    if stripped.startswith("- "):
        stripped = stripped[2:].strip()
    match = re.match(r"""^(['"]?)uses\1\s*:\s*(.*)$""", stripped)
    if not match:
        return None
    value = match.group(2).strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "'\"":
        value = value[1:-1].strip()
    return value


def action_pin_problems(text: str) -> list[str]:
    problems: list[str] = []
    for raw in text.splitlines():
        code = _code(raw)
        if not code.strip():
            continue
        value = _uses_value(code)
        if value is None:
            if _ACTION_AT.search(code):
                problems.append("action reference is not a plain uses pin")
            continue
        if value.startswith("./"):
            continue
        if value.startswith("docker://") or not _PINNED.fullmatch(value):
            problems.append("uses is not pinned to a commit")
    return problems


def test_repo_actions_are_pinned() -> None:
    files = sorted(WF.glob("*.yml")) + sorted(WF.glob("*.yaml"))
    assert {path.name for path in files} >= set(REQUIRED)
    for path in files:
        text = path.read_text(encoding="utf-8")
        assert action_pin_problems(text) == [], path.name


def test_resolved_tags_and_existing_steps() -> None:
    closet = (WF / "sassy-closet.yml").read_text(encoding="utf-8")
    shop = (WF / "sassy-closet-shop.yml").read_text(encoding="utf-8")
    dataset = (WF / "dataset-checks.yml").read_text(encoding="utf-8")
    excel = (WF / "excel-kit.yml").read_text(encoding="utf-8")
    for text in (closet, shop, dataset, excel):
        assert CHECKOUT in text
        assert "@v4" not in text and "@v5" not in text
    assert SETUP_NODE in closet and SETUP_NODE in shop
    assert SETUP_PYTHON in dataset and SETUP_PYTHON in excel
    assert 'sassy-closet/**' in closet and "npm test" in closet and "npm run build" in closet
    assert "npm run typecheck" in closet
    assert 'sassy-closet-shop/**' in shop and "until npm run build; do" in shop
    assert "python -m pytest scripts/tests -q" in dataset
    assert "excel-kit/tests/run_checks.py" in excel
    for text in (closet, shop):
        assert "node-version: \"22\"" in text
    for text in (dataset, excel):
        assert 'python-version: "3.11"' in text


def test_tag_comment_sha_and_local_action() -> None:
    pinned = f"jobs:\n  check:\n    steps:\n      - uses: {CHECKOUT}\n"
    assert action_pin_problems(pinned) == []
    tagged = pinned.replace(CHECKOUT.split()[0], "actions/checkout@v4")
    assert action_pin_problems(tagged)
    commented = "      - uses: actions/checkout@v4 # " + CHECKOUT.split("@", 1)[1].split()[0] + "\n"
    assert action_pin_problems(commented)
    folded = "      - uses: >-\n          actions/checkout@v4\n"
    assert action_pin_problems(folded)
    quoted = '      - uses: "actions/checkout@v4.4.0"\n'
    assert action_pin_problems(quoted)
    local = "      - uses: ./.github/actions/build\n"
    assert action_pin_problems(local) == []
    short = pinned.replace(CHECKOUT.split("@", 1)[1][:40], "11d5960a")
    assert "uses is not pinned to a commit" in "".join(action_pin_problems(short))
