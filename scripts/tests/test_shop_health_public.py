"""Shop /api/health public-shape classifier. No network and no echoed secrets."""
import json

import shop_health_public as health


def _line(body: dict) -> str:
    return health.shop_health_verdict(json.dumps(body))


def test_public_blob_shape_is_clean():
    body = {
        "ok": True,
        "schema": "catalog.v1",
        "reading": "blob",
        "blob": {"configured": True, "readable": True},
        "productCount": 62,
        "shopVisible": 62,
        "knownMas": ["A01", "S06"],
    }
    assert _line(body) == "blob True no"


def test_seed_short_shape_and_secret_keys_leak_without_echoing_values():
    secret = "SECRET-BLOB-PATH"
    assert _line({"reading": "seed", "blob": {"readable": False}}) == "seed False yes"
    assert _line({"reading": "blob", "blob": {"readable": True}}) == "blob True yes"
    leaked = _line({
        "reading": "blob",
        "blob": {"configured": True, "readable": True, "path": secret, "listed": ["a"]},
    })
    assert leaked == "blob True yes"
    assert secret not in leaked
    token = "vercel_blob_rw_SECRET"
    hidden = _line({
        "reading": "blob",
        "blob": {"configured": True, "readable": True},
        "note": token,
    })
    assert hidden == "blob True yes"
    assert token not in hidden
    assert _line({"reading": "blob", "listed": ["sassy/catalog.v1.json"], "blob": {"configured": True, "readable": True}}) == "blob True yes"
    assert health.shop_health_verdict("not-json") == "? False yes"
    hidden_reading = health.shop_health_verdict(
        '{"reading":"SECRET-BLOB-PATH","blob":{"configured":true,"readable":true}}'
    )
    assert hidden_reading == "? True no"
    assert "SECRET-BLOB-PATH" not in hidden_reading
