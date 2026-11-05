"""Signed-out Taobao cost recheck is not price evidence and not gone evidence.

Only an explicit taobao_login_needed flag marks a block. A pile of unreachable
rows does not.
"""


def login_blocked(doc) -> bool:
    """True only for an explicit taobao_login_needed on a cost-recheck summary dict.

    Accept JSON true, 1, or the strings true/yes/y/1. Reject false, 0, "false", "no", missing, and non-dicts.
    """
    if not isinstance(doc, dict):
        return False
    value = doc.get("taobao_login_needed")
    if value is True or (type(value) is int and value == 1):
        return True
    if isinstance(value, str) and value.strip().lower() in {"true", "yes", "y", "1"}:
        return True
    return False


def evidence(doc):
    """Return doc when it is a usable summary, else {}. Callers then see no unreachable or price facts."""
    if login_blocked(doc) or not isinstance(doc, dict):
        return {}
    return doc
