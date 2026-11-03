"""Intake ¥ flags from fixtures. Stored strings stay as they were."""

from __future__ import annotations

from decimal import Decimal

from intake_flags import IntakeRow, PublicCny, flag_intake


def test_known_bad_yen_are_flagged_and_not_rewritten() -> None:
    rows = [
        IntakeRow("K01", ""),
        IntakeRow("H01", "  "),
        IntakeRow("O04", None),
        IntakeRow("S07", "127;145"),
        IntakeRow("S09", "134"),
        IntakeRow("S11", "221.43"),
        IntakeRow("A01", "80"),
        IntakeRow("A07", "87.23"),
    ]
    public = {
        "S09": PublicCny("ok", Decimal("100")),
        "S11": PublicCny("ok", Decimal("200")),
        "A01": PublicCny("ok", Decimal("80")),
        "A07": PublicCny("skip", None, "login-walled"),
    }
    flags = flag_intake(rows, public)
    found = {(flag.ma, flag.kind, flag.stored) for flag in flags}
    assert ("K01", "blank_cny", "") in found
    assert ("H01", "blank_cny", "  ") in found
    assert ("O04", "blank_cny", "") in found
    assert ("S07", "garbled_cny", "127;145") in found
    assert ("S09", "above_public", "134") in found
    assert ("S11", "above_public", "221.43") in found
    assert not any(flag.ma == "A01" for flag in flags)
    assert not any(flag.ma == "A07" for flag in flags)
    assert rows[3].cost_cny == "127;145"
    assert rows[4].cost_cny == "134"
    assert rows[5].cost_cny == "221.43"
    s07 = next(flag for flag in flags if flag.ma == "S07")
    assert s07.stored == "127;145"
    assert "corrected" not in s07.as_json()
