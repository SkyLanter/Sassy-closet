"""Machine bearer for intake GETs. The secret stays in the environment."""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

from intake_pipeline_auth import (
    MAX_LENGTH,
    MIN_LENGTH,
    authorization_headers,
    secret_usable,
)

ROOT = Path(__file__).resolve().parents[2]
SECRET = "-".join(["pipeline", "test", "secret", "abcd"])


def test_lengths_match_the_server_constants():
    source = (ROOT / "sassy-closet" / "lib" / "pipeline-auth.ts").read_text(encoding="utf-8")
    assert f"INTAKE_PIPELINE_SECRET_MIN_LENGTH = {MIN_LENGTH}" in source
    assert f"INTAKE_PIPELINE_SECRET_MAX_LENGTH = {MAX_LENGTH}" in source


def test_unset_or_blank_sends_nothing(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.delenv("INTAKE_PIPELINE_SECRET", raising=False)
    assert authorization_headers() == {}
    monkeypatch.setenv("INTAKE_PIPELINE_SECRET", "   ")
    assert authorization_headers() == {}


def test_short_or_spaced_secret_is_not_sent(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("INTAKE_PIPELINE_SECRET", "a" * (MIN_LENGTH - 1))
    assert authorization_headers() == {}
    monkeypatch.setenv("INTAKE_PIPELINE_SECRET", SECRET + " tail")
    assert authorization_headers() == {}
    assert secret_usable(SECRET) is True


def test_bearer_is_the_trimmed_env_value(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("INTAKE_PIPELINE_SECRET", f"  {SECRET}  ")
    headers = authorization_headers()
    assert list(headers) == ["Authorization"]
    assert headers["Authorization"] == f"Bearer {SECRET}"


def test_header_is_attached_only_to_the_intake_fetch():
    tree = ast.parse((ROOT / "scripts" / "freshness_check.py").read_text(encoding="utf-8"))
    calls = [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "authorization_headers"
    ]
    assert len(calls) == 1
    fetch_intake = next(
        node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == "_fetch_intake"
    )
    attached = [
        node
        for node in ast.walk(fetch_intake)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "_http_get"
        and any(keyword.arg == "headers" for keyword in node.keywords)
    ]
    assert len(attached) == 1
    for name in ("_fetch_blob", "_fetch_hub", "_fetch_pdp", "_fetch_taobao"):
        fn = next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == name)
        leaked = [
            node
            for node in ast.walk(fn)
            if isinstance(node, ast.Call) and any(keyword.arg == "headers" for keyword in node.keywords)
        ]
        assert leaked == []
