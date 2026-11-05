"""Pull-request workflows stay read-only: contents read, no stored checkout token."""
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

_CHECKOUT = re.compile(r"uses:\s*['\"]?actions/checkout@")
_PLAIN_ACTION = re.compile(r"actions/checkout@[A-Za-z0-9._/-]+")


def _plain_checkout(line: str) -> bool:
    stripped = line.strip()
    if stripped.startswith("- "):
        stripped = stripped[2:].strip()
    match = re.match(r"^uses:\s*(.+)$", stripped)
    if not match:
        return False
    value = match.group(1).strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "'\"":
        value = value[1:-1].strip()
    return _PLAIN_ACTION.fullmatch(value) is not None
_PERM_HEADER = re.compile(r"""^(['"]?)permissions\1\s*:\s*(.*)$""")
_WRITE_VALUE = re.compile(r":\s*['\"]?write['\"]?(?=\s*(?:[,}#]|$))", re.IGNORECASE | re.MULTILINE)
_CONTENTS_READ = re.compile(
    r"(?:^|[{,])\s*contents:\s*['\"]?read['\"]?(?=\s*(?:[,}#]|$))",
    re.MULTILINE,
)
_PERSIST_KEY = re.compile(
    r"""(?:^|[{,])\s*(['"]?)persist-credentials\1\s*:\s*([^\n#,}]+)"""
)


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


def _permission_blobs(text: str) -> list[tuple[int, str]]:
    lines = text.splitlines()
    found: list[tuple[int, str]] = []
    index = 0
    while index < len(lines):
        code = _code(lines[index])
        if not code.strip():
            index += 1
            continue
        indent = len(code) - len(code.lstrip())
        stripped = code.strip()
        header = _PERM_HEADER.match(stripped)
        if header:
            inline = header.group(2).strip()
            block: list[str] = []
            if inline:
                block.append(inline)
            else:
                nxt = index + 1
                while nxt < len(lines):
                    piece = _code(lines[nxt])
                    if not piece.strip():
                        nxt += 1
                        continue
                    piece_indent = len(piece) - len(piece.lstrip())
                    if piece_indent <= indent:
                        break
                    block.append(piece.strip())
                    nxt += 1
            found.append((indent, "\n".join(block)))
        index += 1
    return found


def _checkout_bodies(text: str) -> list[list[tuple[int, str]]]:
    lines = text.splitlines()
    bodies: list[list[tuple[int, str]]] = []
    for idx, raw in enumerate(lines):
        code = _code(raw)
        if not code.strip() or not _CHECKOUT.search(code):
            continue
        uses_indent = len(code) - len(code.lstrip())
        start = idx
        for back in range(idx, -1, -1):
            piece = _code(lines[back])
            if not piece.strip():
                continue
            piece_indent = len(piece) - len(piece.lstrip())
            if piece.lstrip().startswith("- ") and piece_indent <= uses_indent:
                start = back
                break
            if piece_indent < uses_indent:
                break
        start_piece = _code(lines[start])
        start_indent = len(start_piece) - len(start_piece.lstrip())
        body = [(start_indent, start_piece.strip())]
        for nxt in lines[start + 1 :]:
            piece = _code(nxt)
            if not piece.strip():
                continue
            piece_indent = len(piece) - len(piece.lstrip())
            if piece_indent <= start_indent:
                break
            body.append((piece_indent, piece.strip()))
        bodies.append(body)
    return bodies


def _persist_on_line(line: str) -> list[str]:
    return [match.group(2).strip() for match in _PERSIST_KEY.finditer(line)]


def _with_persist(body: list[tuple[int, str]]) -> list[str]:
    values: list[str] = []
    with_indent: int | None = None
    for indent, text in body:
        stripped = text[2:].strip() if text.startswith("- ") else text
        if with_indent is not None and indent <= with_indent:
            with_indent = None
        header = re.match(r"^with\s*:\s*(.*)$", stripped)
        if header:
            with_indent = indent
            inline = header.group(1).strip()
            if inline:
                values.extend(_persist_on_line(inline))
            continue
        if with_indent is not None and indent > with_indent:
            values.extend(_persist_on_line(stripped))
    return values


def workflow_problems(text: str) -> list[str]:
    problems: list[str] = []
    if "pull_request_target" in text:
        problems.append("uses pull_request_target")
    if "\\" in text:
        problems.append("workflow escape")
    blobs = _permission_blobs(text)
    roots = [blob for indent, blob in blobs if indent == 0]
    if not roots or any(_CONTENTS_READ.search(blob) is None for blob in roots):
        problems.append("workflow permissions do not set contents: read")
    for _indent, blob in blobs:
        if "write-all" in blob.lower() or _WRITE_VALUE.search(blob):
            problems.append("write permission")
        if blob.startswith("{") and not blob.endswith("}"):
            problems.append("permissions value is not plain")
        if re.match(r"^[|>]", blob) or re.search(r":\s*[|>]", blob):
            problems.append("permissions value is not plain")
        if re.search(r"[&*]|<<", blob):
            problems.append("permissions alias")
    for raw in text.splitlines():
        code = _code(raw).strip()
        if "actions/checkout@" in code and not _plain_checkout(code):
            problems.append("checkout reference is not a plain uses line")
    for body in _checkout_bodies(text):
        blob = "\n".join(line for _, line in body)
        if "<<" in blob or re.search(r"[&*]", blob):
            problems.append("checkout credentials are not explicit")
            continue
        if _with_persist(body) != ["false"]:
            problems.append("checkout keeps credentials")
    return problems


_GOOD = """\
name: sample

permissions:
  contents: read

on:
  pull_request:

jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          persist-credentials: false
"""


def test_repo_workflows_are_read_only() -> None:
    files = sorted(WF.glob("*.yml")) + sorted(WF.glob("*.yaml"))
    assert {path.name for path in files} >= set(REQUIRED)
    for path in files:
        problems = workflow_problems(path.read_text(encoding="utf-8"))
        assert problems == [], f"{path.name}: {problems}"


def test_existing_steps_and_filters_stay() -> None:
    closet = (WF / "sassy-closet.yml").read_text(encoding="utf-8")
    shop = (WF / "sassy-closet-shop.yml").read_text(encoding="utf-8")
    dataset = (WF / "dataset-checks.yml").read_text(encoding="utf-8")
    excel = (WF / "excel-kit.yml").read_text(encoding="utf-8")
    assert 'sassy-closet/**' in closet and "npm test" in closet and "npm run build" in closet
    assert "npm run typecheck" in closet
    assert 'sassy-closet-shop/**' in shop and "until npm run build; do" in shop
    assert "python -m pytest scripts/tests -q" in dataset
    assert "excel-kit/tests/run_checks.py" in excel
    for text in (closet, shop, dataset, excel):
        assert "pull_request:" in text
        assert "permissions:\n  contents: read\n" in text


def test_good_workflow_is_clean() -> None:
    assert workflow_problems(_GOOD) == []


def test_rejects_target_write_and_stored_credentials() -> None:
    assert "uses pull_request_target" in workflow_problems(_GOOD.replace("pull_request:", "pull_request_target:"))
    assert workflow_problems(_GOOD.replace("contents: read", "contents: write"))
    assert workflow_problems(_GOOD.replace("contents: read", "contents: 'write'"))
    assert workflow_problems("permissions: write-all\n" + _GOOD)
    job_write = _GOOD + "\n    permissions:\n      contents: write\n"
    assert "write permission" in workflow_problems(job_write)
    bare = _GOOD.replace("        with:\n          persist-credentials: false\n", "")
    assert "checkout keeps credentials" in workflow_problems(bare)
    flipped = _GOOD.replace("persist-credentials: false", "persist-credentials: true")
    assert "checkout keeps credentials" in workflow_problems(flipped)
    commented = _GOOD.replace(
        "          persist-credentials: false",
        "          # persist-credentials: false",
    )
    assert "checkout keeps credentials" in workflow_problems(commented)
    scalar = _GOOD.replace("contents: read", "contents: |\n    read")
    assert workflow_problems(scalar)
    merged = _GOOD.replace(
        "        with:\n          persist-credentials: false",
        "        with:\n          <<: *cred",
    )
    assert "checkout credentials are not explicit" in workflow_problems(merged)
    alias = _GOOD.replace("contents: read", "contents: *can_write")
    assert "permissions alias" in workflow_problems(alias)
    inline = _GOOD.replace("permissions:\n  contents: read", "permissions: {contents: read}")
    assert workflow_problems(inline) == []
    inline_write = _GOOD.replace("permissions:\n  contents: read", "permissions: {contents: write}")
    assert "write permission" in workflow_problems(inline_write)
    named = _GOOD.replace(
        "      - uses: actions/checkout@v4\n        with:\n          persist-credentials: false",
        "      - name: Checkout\n        uses: actions/checkout@v4\n        with: {persist-credentials: false}",
    )
    assert workflow_problems(named) == []
    hidden_write = _GOOD.replace(
        "    runs-on: ubuntu-latest\n",
        "    permissions:\n      contents: 'write'\n      packages: read\n    runs-on: ubuntu-latest\n",
    )
    assert "write permission" in workflow_problems(hidden_write)
    split_flow = _GOOD.replace(
        "permissions:\n  contents: read",
        "permissions: {contents: read,\n  actions: write}",
    )
    assert workflow_problems(split_flow)
    folded = _GOOD.replace(
        "    runs-on: ubuntu-latest\n",
        "    permissions: >-\n      write-all\n    runs-on: ubuntu-latest\n",
    )
    assert workflow_problems(folded)
    spaced = _GOOD.replace(
        "    runs-on: ubuntu-latest\n",
        "    permissions : write-all\n    runs-on: ubuntu-latest\n",
    )
    assert "write permission" in workflow_problems(spaced)
    quoted_key = _GOOD.replace(
        "    runs-on: ubuntu-latest\n",
        '    "permissions": write-all\n    runs-on: ubuntu-latest\n',
    )
    assert "write permission" in workflow_problems(quoted_key)
    folded_uses = _GOOD.replace(
        "      - uses: actions/checkout@v4\n        with:\n          persist-credentials: false",
        "      - uses: >-\n          actions/checkout@v4",
    )
    assert "checkout reference is not a plain uses line" in workflow_problems(folded_uses)
    quoted_persist = _GOOD.replace(
        "        with:\n          persist-credentials: false",
        '        with:\n          "persist-credentials": true\n        env:\n          X: "persist-credentials: false"',
    )
    assert "checkout keeps credentials" in workflow_problems(quoted_persist)
    env_only = _GOOD.replace(
        "        with:\n          persist-credentials: false",
        '        env:\n          persist-credentials: "false"',
    )
    assert "checkout keeps credentials" in workflow_problems(env_only)
    escaped = _GOOD.replace(
        "    runs-on: ubuntu-latest\n",
        '    permissions: "\\u0077rite-all"\n    runs-on: ubuntu-latest\n',
    )
    assert "workflow escape" in workflow_problems(escaped)
