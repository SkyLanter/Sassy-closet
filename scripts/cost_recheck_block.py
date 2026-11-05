"""Signed-out Taobao cost recheck is not price evidence and not gone evidence.

Only an explicit taobao_login_needed flag marks a block. A pile of unreachable
rows does not. Callers that print or decide from a summary must use
login_blocked() or evidence() so a world.taobao 404 early-stop is not a
price change, a loss, or a gone listing.
"""


def login_blocked(doc) -> bool:
    """True only for an explicit taobao_login_needed on a cost-recheck summary dict.

    Accept JSON true, int 1, float 1.0, or the strings true/yes/y/1.
    Reject false, 0, 0.0, "false", "no", "1.0", missing, lists, and non-dicts.
    """
    if not isinstance(doc, dict):
        return False
    value = doc.get("taobao_login_needed")
    if value is True:
        return True
    if type(value) is int and value == 1:
        return True
    if type(value) is float and value == 1.0:
        return True
    if isinstance(value, str) and value.strip().lower() in {"true", "yes", "y", "1"}:
        return True
    return False


def evidence(doc):
    """Return doc when it is a usable summary, else {}.

    Callers then see no unreachable or price facts. A blocked dict is not
    copied; the usable path returns the same object.
    """
    if login_blocked(doc) or not isinstance(doc, dict):
        return {}
    return doc
