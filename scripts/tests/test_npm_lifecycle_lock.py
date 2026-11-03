"""Neither app runs a script when npm installs it.

npm 10.9.9 runs these when installing the local package: preinstall, install,
postinstall, prepublish, preprepare, prepare, postprepare. prepublishOnly and
prepack are rejected too: publish and pack run them. A script body is rejected
when it would run npm install, curl, wget, or a deploy.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
APPS = ("sassy-closet/package.json", "sassy-closet-shop/package.json")
_LIFECYCLE = frozenset(
    {
        "preinstall",
        "install",
        "postinstall",
        "prepublish",
        "prepublishonly",
        "prepack",
        "preprepare",
        "prepare",
        "postprepare",
    }
)
# npm lib/utils/cmd-list.js names that deref() resolves to install or install-test.
_INSTALL_COMMANDS = frozenset(
    {
        "add",
        "i",
        "in",
        "ins",
        "inst",
        "insta",
        "instal",
        "install",
        "install-t",
        "install-te",
        "install-tes",
        "install-test",
        "isnt",
        "isnta",
        "isntal",
        "isntall",
        "it",
    }
)
_SAFE_COMMANDS = frozenset(
    {
        "ci",
        "cit",
        "clean-install",
        "clean-install-test",
        "config",
        "doctor",
        "get",
        "help",
        "hlep",
        "ic",
        "info",
        "init",
        "install-ci",
        "install-ci-test",
        "install-clean",
        "isntall-clean",
        "la",
        "list",
        "ll",
        "ls",
        "outdated",
        "ping",
        "prefix",
        "show",
        "si",
        "sit",
        "t",
        "test",
        "tst",
        "v",
        "version",
        "view",
        "whoami",
    }
)
_NPM_BOOL = frozenset(
    {
        "-g",
        "-q",
        "-s",
        "-y",
        "--dry-run",
        "--foreground-scripts",
        "--global",
        "--if-present",
        "--ignore-scripts",
        "--json",
        "--no-audit",
        "--no-fund",
        "--package-lock",
        "--package-lock-only",
        "--quiet",
        "--save",
        "--save-dev",
        "--save-exact",
        "--silent",
        "--yes",
    }
)
_RUN_COMMANDS = frozenset({"rum", "run", "run-script", "urn"})
_NPM_LONG_VALUE = frozenset(
    {
        "--cache",
        "--depth",
        "--globalconfig",
        "--include",
        "--loglevel",
        "--omit",
        "--otp",
        "--prefix",
        "--registry",
        "--scope",
        "--script-shell",
        "--tag",
        "--userconfig",
        "--workspace",
    }
)
_FETCH = frozenset({"curl", "wget"})
_DEPLOY = frozenset({"deploy", "vercel", "wrangler"})
_SHELLS = frozenset({"ash", "bash", "busybox", "dash", "ksh", "sh", "zsh"})
_NODE_BINS = frozenset({"bun", "node", "nodejs", "tsx"})
_NODE_EVAL = frozenset({"-e", "--eval", "-p", "--print"})
_PY_BINS = frozenset({"perl", "python", "python3", "ruby"})
_PY_EVAL = frozenset({"-c", "-e", "-m"})
_SPLIT = set(" \t\r\n;|&<>()")


def _no_duplicate(pairs: list[tuple[str, object]]) -> dict[str, object]:
    found: dict[str, object] = {}
    for key, value in pairs:
        if key in found:
            raise ValueError("duplicate key")
        found[key] = value
    return found


def _strings(value: object) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        found: list[str] = []
        for item in value:
            found.extend(_strings(item))
        return found
    if isinstance(value, dict):
        found = []
        for item in value.values():
            found.extend(_strings(item))
        return found
    return []


def _camel(token: str) -> str:
    if not any("A" <= ch <= "Z" for ch in token):
        return token.casefold()
    out: list[str] = []
    for ch in token:
        if "A" <= ch <= "Z":
            out.append("-")
            out.append(ch.lower())
        else:
            out.append(ch)
    return "".join(out).lstrip("-")


def _command_kind(token: str) -> str:
    folded = token.casefold()
    camel = _camel(token)
    for candidate in (folded, camel):
        if candidate in _INSTALL_COMMANDS:
            return "install"
        if candidate in _RUN_COMMANDS:
            return "run"
        if candidate in _SAFE_COMMANDS:
            return "safe"
    return "other"


def _base_name(token: str) -> str:
    return token.casefold().rsplit("/", 1)[-1]


def _is_npm_token(token: str) -> bool:
    base = _base_name(token)
    return base in {"npm", "npm-cli.js"} or base.startswith("npm@")


def _is_npx_token(token: str) -> bool:
    return _base_name(token) == "npx"


def _is_npm_spec(token: str) -> bool:
    base = _base_name(token)
    return base == "npm" or base.startswith("npm@")


def _bad_tool(token: str) -> bool:
    base = _base_name(token).split("@", 1)[0]
    return base in _FETCH or base in _DEPLOY


def _is_lifecycle_word(token: str) -> bool:
    return token.strip().casefold() in _LIFECYCLE


def _npm_flag_takes_value(token: str) -> bool:
    if "=" in token:
        return False
    if token in {"-C", "-w"}:
        return True
    return token.casefold() in _NPM_LONG_VALUE


def _skip_npm_flags(tokens: list[str], index: int) -> tuple[str, int] | None:
    while index < len(tokens):
        token = tokens[index]
        if token == "--":
            if index + 1 < len(tokens):
                return ("word", index + 1)
            return None
        if token.startswith("-"):
            if _npm_flag_takes_value(token):
                if index + 1 < len(tokens) and not tokens[index + 1].startswith("-"):
                    if _is_lifecycle_word(tokens[index + 1]):
                        return ("bad", index)
                    index += 2
                    continue
                index += 1
                continue
            if "=" in token or token.casefold() in _NPM_BOOL:
                index += 1
                continue
            return ("bad", index)
        return ("word", index)
    return None


def _scan_npm(tokens: list[str], start: int) -> bool:
    found = _skip_npm_flags(tokens, start + 1)
    if found is None:
        return False
    kind, index = found
    if kind == "bad":
        return True
    command = _command_kind(tokens[index])
    if command == "install":
        return True
    if command == "run":
        script = _skip_npm_flags(tokens, index + 1)
        if script is None:
            return False
        if script[0] == "bad":
            return True
        return _is_lifecycle_word(tokens[script[1]])
    if command == "safe":
        return False
    return True


def _npx_words(tokens: list[str], start: int) -> list[str]:
    words: list[str] = []
    index = start + 1
    while index < len(tokens):
        token = tokens[index]
        if token == "--":
            words.extend(tokens[index + 1 :])
            break
        if token.startswith("-"):
            if "=" in token:
                words.append(token.split("=", 1)[1])
            index += 1
            continue
        words.append(token)
        index += 1
    return words


def _scan_npx(tokens: list[str], start: int) -> bool:
    words = _npx_words(tokens, start)
    for index, word in enumerate(words):
        if _is_npm_spec(word) and _scan_npm(["npm", *words[index + 1 :]], 0):
            return True
    return False


def _tokenize(plain: str) -> list[str]:
    tokens: list[str] = []
    buf: list[str] = []
    for ch in plain:
        if ch in _SPLIT:
            if buf:
                tokens.append("".join(buf))
                buf = []
            continue
        buf.append(ch)
    if buf:
        tokens.append("".join(buf))
    return tokens


def _short_cluster_has(token: str, letter: str) -> bool:
    flag = token.split("=", 1)[0].casefold()
    return flag.startswith("-") and not flag.startswith("--") and letter in flag[1:]


_VERSIONED = (
    "python3",
    "python",
    "nodejs",
    "node",
    "perl",
    "ruby",
    "php",
    "bash",
    "dash",
    "busybox",
    "zsh",
    "ksh",
    "ash",
    "sh",
    "gawk",
    "nawk",
    "mawk",
    "awk",
    "bun",
    "tsx",
)


def _interpreter_name(token: str) -> str | None:
    base = _base_name(token)
    for name in _VERSIONED:
        if base == name:
            return name
        if base.startswith(name) and base[len(name) :] and all(ch.isdigit() or ch == "." for ch in base[len(name) :]):
            return name
    return None


def _eval_flag(name: str, token: str) -> bool:
    flag = token.split("=", 1)[0].casefold()
    if name in _SHELLS or name in {"ash", "bash", "busybox", "dash", "ksh", "sh", "zsh"}:
        return flag == "--command" or _short_cluster_has(token, "c")
    if name in _NODE_BINS or name in {"bun", "node", "nodejs", "tsx"}:
        return flag in _NODE_EVAL or _short_cluster_has(token, "e") or _short_cluster_has(token, "p")
    if name in _PY_BINS or name in {"perl", "python", "python3", "ruby"}:
        return flag in _PY_EVAL or _short_cluster_has(token, "c") or _short_cluster_has(token, "e")
    if name == "php":
        return flag == "-r" or _short_cluster_has(token, "r")
    return False


def _interpreter_escape(tokens: list[str]) -> bool:
    for index, token in enumerate(tokens):
        name = _interpreter_name(token)
        if name is None:
            continue
        if name in {"awk", "gawk", "mawk", "nawk"}:
            return True
        saw_script = False
        for nxt in tokens[index + 1 :]:
            if nxt.startswith("-"):
                continue
            if nxt in {"-", "/dev/stdin"} or nxt.startswith("/dev/fd/"):
                return True
            saw_script = True
            break
        if name in {"perl", "python", "python3", "ruby", "php"} and not saw_script:
            return True
        for nxt in tokens[index + 1 :]:
            if nxt.startswith("-") and _eval_flag(name, nxt):
                return True
    return False


_SAFE_GLOBS = frozenset({"tests/*.test.js", "tests/*.test.ts"})


def _glob_hides_tool(token: str) -> bool:
    if not any(ch in token for ch in "*?[]"):
        return False
    return token not in _SAFE_GLOBS


_LOAD_FLAGS = frozenset(
    {
        "--experimental-loader",
        "--import",
        "--loader",
        "--require",
        "-r",
    }
)


def _load_value(tokens: list[str], index: int) -> str:
    token = tokens[index]
    if "=" in token:
        return token.split("=", 1)[1]
    if index + 1 < len(tokens) and not tokens[index + 1].startswith("-"):
        return tokens[index + 1]
    return ""


def _load_flag_dangerous(tokens: list[str]) -> bool:
    for index, token in enumerate(tokens):
        flag = token.split("=", 1)[0].casefold()
        if flag not in _LOAD_FLAGS:
            continue
        value = _load_value(tokens, index)
        if not value:
            continue
        lowered = value.casefold()
        if lowered.startswith("data:") or "javascript" in lowered or "%" in value:
            return True
        if any(not (ch.isalnum() or ch in "@/_.+-") for ch in value):
            return True
    return False


def _flag_value_dangerous(token: str) -> bool:
    if "=" not in token:
        return False
    value = token.split("=", 1)[1]
    if not value:
        return False
    if _bad_tool(value):
        return True
    lowered = value.casefold()
    return lowered.startswith("data:") or "javascript" in lowered


def _tokens_dangerous(tokens: list[str]) -> bool:
    if _interpreter_escape(tokens) or _load_flag_dangerous(tokens) or any(
        _glob_hides_tool(token) or _flag_value_dangerous(token) for token in tokens
    ):
        return True
    for index, token in enumerate(tokens):
        if _bad_tool(token):
            return True
        if _is_npm_token(token) and _scan_npm(tokens, index):
            return True
        if _is_npx_token(token) and _scan_npx(tokens, index):
            return True
        if _other_install(tokens, index):
            return True
    return False


_OTHER_PM = frozenset({"bun", "pnpm", "yarn", "yarnpkg"})
_ALLOWED_COMMANDS = frozenset(
    {
        "eslint",
        "next",
        "node",
        "npm",
        "npx",
        "pip",
        "pip3",
        "python3",
        "tsc",
        "tsx",
    }
)


def _other_install(tokens: list[str], index: int) -> bool:
    if _base_name(tokens[index]).split("@", 1)[0] not in _OTHER_PM:
        return False
    index += 1
    command = ""
    while index < len(tokens):
        token = tokens[index]
        if token.startswith("-"):
            index += 1
            continue
        command = token
        index += 1
        break
    if not command:
        return False
    if _command_kind(command) == "install" or _is_lifecycle_word(command):
        return True
    if _command_kind(command) != "run":
        return False
    while index < len(tokens):
        token = tokens[index]
        if token.startswith("-"):
            index += 1
            continue
        return _is_lifecycle_word(token) or _command_kind(token) == "install"
    return False


def _segments(plain: str) -> list[str]:
    text = plain.replace("&&", "\n").replace("||", "\n")
    for ch in ";\n&":
        text = text.replace(ch, "\n")
    return [part for part in text.split("\n") if part.strip()]


def _command_not_allowed(plain: str) -> bool:
    for segment in _segments(plain):
        tokens = _tokenize(segment)
        if not tokens:
            continue
        if _base_name(tokens[0]).split("@", 1)[0] not in _ALLOWED_COMMANDS:
            return True
    return False


def _dangerous(body: str) -> bool:
    if any((ord(ch) < 32 and ch not in "\n\r\t") or ord(ch) >= 127 for ch in body):
        return True
    if any(mark in body for mark in ("\\", "$", "`", "<<", "|", "<", ">")):
        return True
    plain = body.replace("'", "").replace('"', "")
    if "<<" in plain or _command_not_allowed(plain):
        return True
    return _tokens_dangerous(_tokenize(plain))


def _add(problems: list[str], item: str) -> None:
    if item not in problems:
        problems.append(item)


def _walk(node: object, parent_key: str, problems: list[str]) -> None:
    if isinstance(node, dict):
        if parent_key.strip().casefold() == "scripts":
            for key, value in node.items():
                if str(key).strip().casefold() in _LIFECYCLE:
                    _add(problems, "lifecycle script")
                if any(_dangerous(body) for body in _strings(value)):
                    _add(problems, "script runs a fetch or deploy")
        for key, value in node.items():
            _walk(value, str(key), problems)
        return
    if isinstance(node, list):
        for item in node:
            _walk(item, parent_key, problems)


def lifecycle_problems(text: str) -> list[str]:
    try:
        data = json.loads(text, object_pairs_hook=_no_duplicate)
    except json.JSONDecodeError:
        return ["package.json did not parse"]
    except ValueError:
        return ["duplicate key"]
    problems: list[str] = []
    _walk(data, "", problems)
    return problems


def test_apps_do_not_run_install_scripts() -> None:
    for rel in APPS:
        text = (ROOT / rel).read_text(encoding="utf-8")
        assert lifecycle_problems(text) == [], rel
        data = json.loads(text)
        assert "build" in data["scripts"] and "test" in data["scripts"]
        for key in data["scripts"]:
            assert str(key).strip().casefold() not in _LIFECYCLE


def test_rejects_lifecycle_keys_and_fetch_bodies() -> None:
    good = [
        '{"scripts": {"build": "next build", "test": "node --test"}}',
        '{"dependencies": {"preinstall": "1.0.0"}, "scripts": {"build": "next build"}}',
        '{"scripts": {"build": "npx --yes tsx --require ./scripts/alias.cjs scripts/smoke-admin.ts"}}',
        '{"scripts": {"build": "npm ci && npm test"}}',
        '{"scripts": {"build": "npm run build"}}',
        '{"scripts": {"build": "npm --prefix . ci"}}',
        '{"scripts": {"build": "npm ci && pip install -r requirements.txt"}}',
        '{"scripts": {"dev": "node scripts/write-local-product-manifest.mjs && next dev"}}',
        '{"scripts": {"test": "node --import tsx --test --test-concurrency=1 tests/*.test.ts"}}',
        '{"scripts": {"build": "npm ci\\nnpm test"}}',
        '{"scripts": {"build": "npm ping"}}',
        '{"scripts": {"build": "npm whoami"}}',
        '{"scripts": {"build": "npm cit"}}',
        '{"scripts": {"build": "npm config list"}}',
        '{"scripts": {"build": "npm init -y"}}',
        '{"scripts": {"origin": "python3 docs/ai-clothing-shop/qa/qa_selltest_origin_gate.py"}}',
    ]
    for text in good:
        assert lifecycle_problems(text) == [], text

    bad = [
        ('{"scripts": {"preinstall": "echo ok"}}', "lifecycle script"),
        ('{"scripts": {"PrepublishOnly": "echo ok"}}', "lifecycle script"),
        ('{"scripts": {"preprepare": "echo ok"}}', "lifecycle script"),
        ('{"scripts": {"postprepare": "echo ok"}}', "lifecycle script"),
        ('{"scripts": {"prepack": "echo ok"}}', "lifecycle script"),
        (
            '{"scripts": {"build": "next build", "extra": {"scripts": {"prepare": "echo x"}}}}',
            "lifecycle script",
        ),
        ('{"scripts": {"\\u0070reinstall": "echo ok"}}', "lifecycle script"),
        ('{"scripts": {"build": "curl https://example.invalid/x"}}', "script runs a fetch or deploy"),
        ('{"scripts": {"build": "wget https://example.invalid/x"}}', "script runs a fetch or deploy"),
        ('{"scripts": {"build": "c\'url\' https://example.invalid/x"}}', "script runs a fetch or deploy"),
        ('{"scripts": {"build": "w\'get\' https://example.invalid/x"}}', "script runs a fetch or deploy"),
        ('{"scripts": {"build": "ver\'cel\' deploy"}}', "script runs a fetch or deploy"),
        ('{"scripts": {"build": "dep\'loy\'"}}', "script runs a fetch or deploy"),
        ('{"scripts": {"build": "wran\'gler\' deploy"}}', "script runs a fetch or deploy"),
        ('{"scripts": {"build": "cu\\\\rl https://example.invalid/x"}}', "script runs a fetch or deploy"),
        ('{"scripts": {"build": "npm --prefix . install left-pad"}}', "script runs a fetch or deploy"),
        ('{"scripts": {"build": "npm --prefix=. install left-pad"}}', "script runs a fetch or deploy"),
        ('{"scripts": {"build": "npm --ignore-scripts install left-pad"}}', "script runs a fetch or deploy"),
        ('{"scripts": {"build": "npm -C . i left-pad"}}', "script runs a fetch or deploy"),
        ('{"scripts": {"build": "npm ins left-pad"}}', "script runs a fetch or deploy"),
        ('{"scripts": {"build": "npm in left-pad"}}', "script runs a fetch or deploy"),
        ('{"scripts": {"build": "npm insta left-pad"}}', "script runs a fetch or deploy"),
        ('{"scripts": {"build": "npm instal left-pad"}}', "script runs a fetch or deploy"),
        ('{"scripts": {"build": "npm isnt left-pad"}}', "script runs a fetch or deploy"),
        ('{"scripts": {"build": "npm isnta left-pad"}}', "script runs a fetch or deploy"),
        ('{"scripts": {"build": "npm isntal left-pad"}}', "script runs a fetch or deploy"),
        ('{"scripts": {"build": "npm isntall left-pad"}}', "script runs a fetch or deploy"),
        ('{"scripts": {"build": "npm add left-pad"}}', "script runs a fetch or deploy"),
        ('{"scripts": {"build": "npm it"}}', "script runs a fetch or deploy"),
        ('{"scripts": {"build": "npm install-test"}}', "script runs a fetch or deploy"),
        ('{"scripts": {"build": "npm installTest"}}', "script runs a fetch or deploy"),
        ('{"scripts": {"build": "npm ins\'tall\' left-pad"}}', "script runs a fetch or deploy"),
        ('{"scripts": {"build": "npm install&&true"}}', "script runs a fetch or deploy"),
        ('{"scripts": {"build": "npm install;true"}}', "script runs a fetch or deploy"),
        ('{"scripts": {"build": "npm install|cat"}}', "script runs a fetch or deploy"),
        ('{"scripts": {"build": "npm install>/tmp/out"}}', "script runs a fetch or deploy"),
        ('{"scripts": {"build": "npm install&"}}', "script runs a fetch or deploy"),
        ('{"scripts": {"build": "npm $(echo install) left-pad"}}', "script runs a fetch or deploy"),
        ('{"scripts": {"build": "npm `echo install` left-pad"}}', "script runs a fetch or deploy"),
        ('{"scripts": {"build": "npm\\ninstall left-pad"}}', "script runs a fetch or deploy"),
        ('{"scripts": {"build": "npx --yes npm@10.9.2 install left-pad"}}', "script runs a fetch or deploy"),
        ('{"scripts": {"build": "npx -p npm install left-pad"}}', "script runs a fetch or deploy"),
        ('{"scripts": {"build": "npm run install"}}', "script runs a fetch or deploy"),
        ('{"scripts": {"build": "npm run preinstall"}}', "script runs a fetch or deploy"),
        ('{"scripts": {"build": "npm exec curl https://example.invalid/x"}}', "script runs a fetch or deploy"),
        ('{"scripts": {"build": "bash -lc echo ok"}}', "script runs a fetch or deploy"),
        ('{"scripts": {"build": "node -e console.log"}}', "script runs a fetch or deploy"),
        ('{"scripts": {"build": "python3 -c print"}}', "script runs a fetch or deploy"),
        ('{"scripts": {"build": "python3 -m pip install -r requirements.txt"}}', "script runs a fetch or deploy"),
        ('{"scripts": {"build": "npx --yes npm@10.9.2 -- install left-pad"}}', "script runs a fetch or deploy"),
        ('{"scripts": {"build": "npm run --silent preinstall"}}', "script runs a fetch or deploy"),
        ('{"scripts": {"build": "npm run --if-present install"}}', "script runs a fetch or deploy"),
        ('{"scripts": {"build": "npm rum --silent postprepare"}}', "script runs a fetch or deploy"),
        ('{"scripts": {"build": "npm --logl info install --ignore-scripts"}}', "script runs a fetch or deploy"),
        ('{"scripts": {"build": "npm --user-agent test install"}}', "script runs a fetch or deploy"),
        ('{"scripts": {"build": "npm -c ci install"}}', "script runs a fetch or deploy"),
        ('{"scripts": {"build": "npm --prefix . run preinstall"}}', "script runs a fetch or deploy"),
        ('{"scripts": {"build": "npx --yes npm@10.9.2 run preinstall"}}', "script runs a fetch or deploy"),
        ('{"scripts": {"build": "npx --yes vercel@latest --prod"}}', "script runs a fetch or deploy"),
        ('{"scripts": {"build": "npx --yes wrangler@3 publish"}}', "script runs a fetch or deploy"),
        ('{"scripts": {"build": "/usr/bin/cu?l --version"}}', "script runs a fetch or deploy"),
        ('{"scripts": {"build": "/usr/bin/cur[l] --version"}}', "script runs a fetch or deploy"),
        ('{"scripts": {"build": "node /tmp/npm-cli.js install"}}', "script runs a fetch or deploy"),
        ('{"scripts": {"build": "python3.12 -c print"}}', "script runs a fetch or deploy"),
        ('{"scripts": {"build": "perl -we system"}}', "script runs a fetch or deploy"),
        ('{"scripts": {"build": "node -pe process.exit"}}', "script runs a fetch or deploy"),
        ('{"scripts": {"build": "python3 -W ignore -c print"}}', "script runs a fetch or deploy"),
        ('{"scripts": {"build": "dash -o errexit -c echo"}}', "script runs a fetch or deploy"),
        ('{"scripts": {"build": "python3 <<\'END\'\\nprint(1)\\nEND"}}', "script runs a fetch or deploy"),
        ('{"scripts": {"build": "awk BEGIN"}}', "script runs a fetch or deploy"),
        ('{"scripts": {"build": "yarn install"}}', "script runs a fetch or deploy"),
        ('{"scripts": {"build": "pnpm install"}}', "script runs a fetch or deploy"),
        ('{"scripts": {"build": "bun install"}}', "script runs a fetch or deploy"),
        ('{"scripts": {"build": "echo hi | python3"}}', "script runs a fetch or deploy"),
        ('{"scripts": {"build": "mawk BEGIN"}}', "script runs a fetch or deploy"),
        ('{"scripts": {"build": "npx --call=curl https://example.invalid/x"}}', "script runs a fetch or deploy"),
        ('{"scripts": {"build": "yarn run preinstall"}}', "script runs a fetch or deploy"),
        ('{"scripts": {"build": "pnpm -r run preinstall"}}', "script runs a fetch or deploy"),
        ('{"scripts": {"build": "corepack yarn run preinstall"}}', "script runs a fetch or deploy"),
        ('{"scripts": {"build": "node --import=data:text/javascript,process.exit(0)"}}', "script runs a fetch or deploy"),
        (
            '{"scripts": {"build": "node --import data:text/javascript,import%7BexecSync%7D"}}',
            "script runs a fetch or deploy",
        ),
        ('{"scripts": {"build": "/tmp/x.test.ts/* --version"}}', "script runs a fetch or deploy"),
        ('{"scripts": {"build": "python3 -"}}', "script runs a fetch or deploy"),
        ('{"scripts": {"build": "busybox wget https://example.invalid/x"}}', "script runs a fetch or deploy"),
        ('{"scripts": {"build": "deno eval console.log"}}', "script runs a fetch or deploy"),
        ('{"scripts": {"build": "next build", "build": "curl x"}}', "duplicate key"),
        ("{", "package.json did not parse"),
    ]
    for text, needle in bad:
        assert needle in lifecycle_problems(text), text
