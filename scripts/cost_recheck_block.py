"""Signed-out Taobao cost recheck is not price evidence and not gone evidence.

Only an explicit taobao_login_needed flag marks a block. A pile of unreachable
rows does not. Every reader of these JSON files uses ENCODING so a UTF-8 BOM
is not part of the first token.
"""
import json
from pathlib import Path

ENCODING = "utf-8-sig"


def login_blocked(doc) -> bool:
    """True only for an explicit taobao_login_needed on a cost-recheck summary dict.

    Accept JSON true, int 1, float 1.0 (JSON numbers 1.0 and 1e0), or the strings
    true/yes/y/1 after strip and lower. Float 1.0 is the same flag as int 1.
    Reject false, 0, 0.0, strings false/no in any case or surrounding whitespace,
    the string "1.0", missing, and non-dicts.
    """
    if not isinstance(doc, dict):
        return False
    value = doc.get("taobao_login_needed")
    if value is True or (type(value) is int and value == 1):
        return True
    # JSON 1.0 and 1e0 are floats. Only exact 1.0 matches int 1. The text "1.0" does not.
    if type(value) is float and value == 1.0:
        return True
    if isinstance(value, str) and value.strip().lower() in {"true", "yes", "y", "1"}:
        return True
    return False


def evidence(doc):
    """Return doc when it is a usable summary, else {}. Callers then see no unreachable or price facts."""
    if login_blocked(doc) or not isinstance(doc, dict):
        return {}
    return doc


def read_json(path):
    """Load JSON text. A leading UTF-8 BOM is stripped. Missing path raises."""
    return json.loads(Path(path).read_text(encoding=ENCODING))
