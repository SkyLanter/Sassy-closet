"""Workflows install from the lockfile and do not read secrets or fork-target events."""
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
NODE = ("sassy-closet.yml", "sassy-closet-shop.yml")
_INSTALL_WORDS = frozenset({"install", "isntall", "inst", "add", "it", "i"})
_SAFE_NPM = frozenset({"ci", "test", "run", "run-script", "outdated", "ls", "list", "view", "help"})
_NPM_CI = re.compile(r"(?<![\w-])npm\s+ci(?![\w-])", re.IGNORECASE)
_NPM_WORD = re.compile(r"(?<![\w-])npm\b", re.IGNORECASE)
_SECRETS = re.compile(r"(?<![\w])secrets(?![\w])", re.IGNORECASE)
_BLOCK = re.compile(r":\s*[|>][+-]?\s*$")
_SHELL_END = frozenset({"&&", "||", ";", "|"})


def _yaml_code(line: str) -> str:
    out: list[str] = []
    quote = ""
    for index, ch in enumerate(line):
        if quote:
            out.append(ch)
            if ch == quote:
                quote = ""
            continue
        if ch in "'\"":
            quote = ch
            out.append(ch)
            continue
        if ch == "#" and (index == 0 or line[index - 1].isspace()):
            break
        out.append(ch)
    return "".join(out).rstrip()


def _parts(text: str) -> tuple[str, str]:
    lines = text.splitlines()
    yaml_lines: list[str] = []
    blocks: list[str] = []
    index = 0
    while index < len(lines):
        code = _yaml_code(lines[index])
        yaml_lines.append(code)
        if code.strip() and _BLOCK.search(code):
            indent = len(code) - len(code.lstrip())
            index += 1
            chunk: list[str] = []
            while index < len(lines):
                nxt = lines[index]
                if nxt.strip() and (len(nxt) - len(nxt.lstrip())) <= indent:
                    break
                chunk.append(nxt)
                index += 1
            blocks.append("\n".join(chunk))
            continue
        index += 1
    return "\n".join(yaml_lines), "\n".join(blocks)


def _invokes_install(rest: str) -> bool:
    saw_flag = False
    for token in re.findall(r"\S+", rest):
        if token in _SHELL_END or token.startswith("&&") or token.startswith("||"):
            return False
        word = token.lower().strip("'\"();")
        if word in _INSTALL_WORDS:
            return True
        if word.startswith("-"):
            saw_flag = True
            continue
        if word in _SAFE_NPM:
            return False
        if saw_flag:
            continue
        return False
    return False


def _npm_problem(chunk: str) -> bool:
    if _NPM_WORD.search(chunk) and ("${{" in chunk or re.search(r"npm\s*\$", chunk, re.IGNORECASE)):
        return True
    if "`" in chunk and _NPM_WORD.search(chunk):
        return True
    plain = chunk.replace('"', " ").replace("'", " ")
    return any(_invokes_install(plain[match.end() :]) for match in _NPM_WORD.finditer(plain))


def workflow_install_problems(text: str, *, require_npm_ci: bool = False) -> list[str]:
    problems: list[str] = []
    if "\\" in text:
        problems.append("workflow escape")
    if "pull_request_target" in text.lower():
        problems.append("uses pull_request_target")
    yaml, blocks = _parts(text)
    scanned = yaml + "\n" + blocks
    if _SECRETS.search(scanned):
        problems.append("references secrets")
    if _npm_problem(yaml) or _npm_problem(blocks):
        problems.append("runs npm install")
    if require_npm_ci and not _NPM_CI.search(scanned):
        problems.append("missing npm ci")
    return problems


def test_repo_workflows_install_from_the_lockfile() -> None:
    files = sorted(WF.glob("*.yml")) + sorted(WF.glob("*.yaml"))
    names = {path.name for path in files}
    assert set(REQUIRED) <= names
    for path in files:
        text = path.read_text(encoding="utf-8")
        problems = workflow_install_problems(text, require_npm_ci=path.name in NODE)
        assert problems == [], f"{path.name}: {problems}"


def test_existing_steps_stay() -> None:
    closet = (WF / "sassy-closet.yml").read_text(encoding="utf-8")
    shop = (WF / "sassy-closet-shop.yml").read_text(encoding="utf-8")
    dataset = (WF / "dataset-checks.yml").read_text(encoding="utf-8")
    excel = (WF / "excel-kit.yml").read_text(encoding="utf-8")
    assert "sassy-closet/**" in closet and "npm test" in closet and "npm run build" in closet
    assert "npm run typecheck" in closet and 'node-version: "22"' in closet
    assert "sassy-closet-shop/**" in shop and "until npm run build; do" in shop
    assert 'node-version: "22"' in shop
    assert "python -m pytest scripts/tests -q" in dataset
    assert "pip install -r requirements.txt" in dataset and "pip install -r requirements.txt" in excel
    assert "excel-kit/tests/run_checks.py" in excel
    for text in (closet, shop, dataset, excel):
        assert "pull_request:" in text


def test_rejects_install_secrets_and_target() -> None:
    good = "run: npm ci\nrun: pip install -r requirements.txt\non:\n  pull_request:\n"
    assert workflow_install_problems(good, require_npm_ci=True) == []
    assert "runs npm install" in workflow_install_problems("run: npm install\n")
    assert "runs npm install" in workflow_install_problems("run: npm  install --ignore-scripts\n")
    assert "runs npm install" in workflow_install_problems("run: npm i\n")
    assert "runs npm install" in workflow_install_problems("run: npm ci && npm install left-pad\n")
    assert workflow_install_problems("run: npm ci # npm install\n", require_npm_ci=True) == []
    assert "references secrets" in workflow_install_problems("env:\n  TOKEN: ${{ secrets.NPM_TOKEN }}\n")
    assert "references secrets" in workflow_install_problems("run: echo ${{ secrets['GITHUB_TOKEN'] }}\n")
    assert "references secrets" in workflow_install_problems("run: echo ${{ toJSON(secrets) }}\n")
    assert "uses pull_request_target" in workflow_install_problems("on:\n  Pull_Request_Target:\n")
    assert workflow_install_problems("# secrets.NPM_TOKEN\nrun: npm ci\n", require_npm_ci=True) == []
    assert "uses pull_request_target" in workflow_install_problems("on:\n  pull_request_target:\n")
    assert "workflow escape" in workflow_install_problems("run: npm \\\n  install\n")
    assert "missing npm ci" in workflow_install_problems("run: npm test\n", require_npm_ci=True)
    flagged = "\n".join(
        [
            "run: npm --ignore-scripts install left-pad",
            "run: npm --no-save i left-pad",
            'run: npm "i" left-pad',
            "run: npm add left-pad",
            "run: npm inst left-pad",
            "run: npm isntall",
            "run: npm it",
            "run: npm ${{ 'install' }} left-pad",
            "run: npm${IFS}install",
            "run: echo foo#$(npm install)",
            "TOKEN: x#${{ secrets.GITHUB_TOKEN }}",
        ]
    )
    found = workflow_install_problems(flagged, require_npm_ci=True)
    assert "runs npm install" in found and "references secrets" in found
    folded = 'run: >-\n  npm\n  "install"\n'
    assert "runs npm install" in workflow_install_problems(folded)
    literal = "run: |\n  echo hello # ${{ secrets.GITHUB_TOKEN }}\n  npm ci\n"
    assert "references secrets" in workflow_install_problems(literal, require_npm_ci=True)
    pwsh = "run: |\n  npm `\n  install\n"
    assert "runs npm install" in workflow_install_problems(pwsh)
    prefixed = "run: npm ci && npm --prefix . install left-pad\n"
    assert "runs npm install" in workflow_install_problems(prefixed, require_npm_ci=True)
