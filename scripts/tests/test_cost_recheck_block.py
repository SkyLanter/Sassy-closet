"""Explicit taobao_login_needed is the only signed-out cost-recheck block."""
import json

import cost_recheck_block as block


def test_login_blocked_accepts_only_the_explicit_flag():
    accepted = [
        {"taobao_login_needed": True},
        {"taobao_login_needed": 1},
        {"taobao_login_needed": 1.0},
        {"taobao_login_needed": 1e0},
        {"taobao_login_needed": "true"},
        {"taobao_login_needed": " TRUE "},
        {"taobao_login_needed": "yes"},
        {"taobao_login_needed": "Y"},
        {"taobao_login_needed": "1"},
        {"taobao_login_needed": " 1 "},
        json.loads('{"taobao_login_needed": true}'),
        json.loads('{"taobao_login_needed": 1}'),
        json.loads('{"taobao_login_needed": 1.0}'),
        json.loads('{"taobao_login_needed": 1e0}'),
    ]
    for doc in accepted:
        assert block.login_blocked(doc) is True

    rejected = [
        {"taobao_login_needed": False},
        {"taobao_login_needed": 0},
        {"taobao_login_needed": 0.0},
        {"taobao_login_needed": None},
        {},
        {"taobao_login_needed": "false"},
        {"taobao_login_needed": "False"},
        {"taobao_login_needed": "no"},
        {"taobao_login_needed": ""},
        {"taobao_login_needed": " "},
        {"taobao_login_needed": "1.0"},
        {"taobao_login_needed": "1.00"},
        {"taobao_login_needed": []},
        {"taobao_login_needed": [True]},
        {"taobao_login_needed": 2},
        {"taobao_login_needed": 1.5},
        {"unreachable_mas": ["A01", "A02", "A03"]},
        json.loads('{"taobao_login_needed": false}'),
        json.loads('{"taobao_login_needed": 0}'),
        json.loads('{"taobao_login_needed": 0.0}'),
    ]
    for doc in rejected:
        assert block.login_blocked(doc) is False
    for doc in (None, [], "true", True, 1, 1.0, 0):
        assert block.login_blocked(doc) is False


def test_evidence_returns_the_same_dict_or_empty():
    usable = {"unreachable_mas": ["A01"], "taobao_login_needed": "false"}
    assert block.evidence(usable) is usable
    blocked = {"taobao_login_needed": True, "unreachable_mas": ["A01"], "live_price_changed": ["A02"]}
    assert block.evidence(blocked) == {}
    assert block.evidence(blocked) is not blocked
    for doc in (None, [], "false", 1, True):
        assert block.evidence(doc) == {}
