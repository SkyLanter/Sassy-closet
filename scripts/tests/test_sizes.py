"""Shoe mãs (G, O) keep numeric sizes 33-46; clothing sizes are unchanged."""

from __future__ import annotations

from autolist import ASIA, is_valid_size, norm_sizes


def test_g01_shoe_sizes_kept() -> None:
    assert norm_sizes("35 36 37 38 39 40", "G01") == ["35", "36", "37", "38", "39", "40"]
    assert norm_sizes("35 36 37 38 39 40", "G") == ["35", "36", "37", "38", "39", "40"]


def test_o_kind_and_separators_dedupe() -> None:
    assert norm_sizes("38,36/36;40.0|39", "O") == ["36", "38", "39", "40"]


def test_shoe_range_edges() -> None:
    assert norm_sizes("32 33 46 47", "G") == ["33", "46"]
    assert norm_sizes("12 50 38", "G") == ["38"]


def test_clothing_unchanged() -> None:
    assert norm_sizes("s m xxl", "A") == ["S", "M", "2XL"]
    assert norm_sizes("XL xs 3xl xxs", "A29") == ["2XS", "XS", "XL", "2XL"]
    assert norm_sizes("35 36", "A") == []
    assert norm_sizes("35 36") == []
    assert norm_sizes("38", "S06") == []


def test_empty_and_unknown() -> None:
    assert norm_sizes(None, "G") == []
    assert norm_sizes("", "A") == []
    assert norm_sizes("free 均码", "G") == []


def test_validator() -> None:
    assert is_valid_size("38", "G") and is_valid_size("M", "G")
    assert not is_valid_size("38", "A") and not is_valid_size("38")
    assert all(is_valid_size(s, "A") for s in ASIA)
