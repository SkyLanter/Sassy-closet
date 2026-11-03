"""cursor/* does not deploy. main and other branches still do.

Polarity from Vercel Git configuration (checked 2026-10-15):
https://vercel.com/docs/project-configuration/git-configuration

- Patterns are minimatch. `*` does not cross `/`, so `cursor/*` matches
  `cursor/example` and does not match `main` or `feature/example`.
- A matching rule of false does not deploy that branch.
- Any branch with no matching rule stays enabled (default true).
- If several rules match and at least one is true, the branch deploys.

ignoreCommand is a different switch and is not used. Its exit codes are the
opposite of a normal shell test: 0 ignores the build, 1 continues it
(https://vercel.com/docs/project-configuration/vercel-json#ignorecommand).
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
PROJECTS = ("sassy-closet/vercel.json", "sassy-closet-shop/vercel.json")
BRANCHES = (
    ("cursor/example", False),
    ("main", True),
    ("feature/example", True),
)


def minimatch(name: str, pattern: str) -> bool:
    """Default minimatch for `*`, `**`, `?`, and literals. `*` stays in one segment."""
    i = 0
    parts = ["^"]
    while i < len(pattern):
        if pattern.startswith("**/", i):
            parts.append("(?:.*/)?")
            i += 3
            continue
        if pattern.startswith("**", i):
            parts.append(".*")
            i += 2
            continue
        char = pattern[i]
        if char == "*":
            parts.append("[^/]*")
        elif char == "?":
            parts.append("[^/]")
        else:
            parts.append(re.escape(char))
        i += 1
    parts.append("$")
    return re.match("".join(parts), name) is not None


def deployment_enabled(config: dict, branch: str) -> bool:
    rules = config.get("git", {}).get("deploymentEnabled", True)
    if isinstance(rules, bool):
        return rules
    matched = [enabled for pattern, enabled in rules.items() if minimatch(branch, pattern)]
    if not matched:
        return True
    return any(matched)


def _load(rel: str) -> dict:
    return json.loads((ROOT / rel).read_text())


@pytest.mark.parametrize("rel", PROJECTS)
@pytest.mark.parametrize(("branch", "builds"), BRANCHES)
def test_branch_deploy_decision(rel: str, branch: str, builds: bool) -> None:
    assert deployment_enabled(_load(rel), branch) is builds


@pytest.mark.parametrize("rel", PROJECTS)
def test_only_cursor_branches_are_disabled(rel: str) -> None:
    config = _load(rel)
    assert "ignoreCommand" not in config
    assert config["git"]["deploymentEnabled"] == {"cursor/*": False}


def test_intake_keeps_existing_vercel_keys() -> None:
    config = _load("sassy-closet/vercel.json")
    assert config["framework"] == "nextjs"


def test_unspecified_branch_stays_enabled_and_any_true_rule_wins() -> None:
    disabled = {"git": {"deploymentEnabled": False}}
    assert deployment_enabled(disabled, "main") is False
    assert deployment_enabled(disabled, "cursor/example") is False

    mixed = {"git": {"deploymentEnabled": {"experiment-*": False, "*-dev": True}}}
    assert deployment_enabled(mixed, "experiment-my-branch-dev") is True
    assert deployment_enabled(mixed, "experiment-only") is False
    assert deployment_enabled(mixed, "main") is True


@pytest.mark.parametrize(
    ("name", "pattern", "matches"),
    [
        ("cursor/example", "cursor/*", True),
        ("main", "cursor/*", False),
        ("feature/example", "cursor/*", False),
        ("cursor/foo/bar", "cursor/*", False),
        ("internal-foo", "internal-*", True),
        ("experiment-my-branch-dev", "experiment-*", True),
        ("experiment-my-branch-dev", "*-dev", True),
    ],
)
def test_minimatch_matches_vercel_docs(name: str, pattern: str, matches: bool) -> None:
    assert minimatch(name, pattern) is matches
