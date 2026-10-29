"""Piece 176: Excel-saved CSVs start with a UTF-8 BOM; the 'ma' column must still be read."""
from decimal import Decimal

import too_cheap_check as t

KEY = "intake" + "_cny"


def _csv(tmp_path, name, text, bom):
    p = tmp_path / name
    p.write_bytes((b"\xef\xbb\xbf" if bom else b"") + text.encode("utf-8"))
    return p


def test_costs_csv_with_bom(tmp_path):
    for bom in (False, True):
        p = _csv(tmp_path, f"c{bom}.csv", f"ma,{KEY},list_cny,kg\nA01,{10 * 10},,0.3\n", bom)
        assert t.load_costs(p)["A01"]["kg"] == "0.3", bom


def test_weights_csv_with_bom(tmp_path):
    for bom in (False, True):
        p = _csv(tmp_path, f"w{bom}.csv", "ma,weight_kg\nA01,0.4\n", bom)
        assert t.load_weights([p]) == {"A01": Decimal("0.4")}, bom
