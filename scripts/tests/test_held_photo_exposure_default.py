"""Piece 209: held_photo_exposure default held source is data/held.json (fake mãs only)."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import held_photo_exposure as hpe  # noqa: E402


def _root(tmp_path, data_held, state_held=None):
    (tmp_path / "data").mkdir()
    (tmp_path / "data/held.json").write_text(json.dumps({"heldIncomplete": data_held, "neverList": []}))
    if state_held is not None:
        st = tmp_path / "auto-list/state"; st.mkdir(parents=True)
        (st / "held.json").write_text(json.dumps({m: {} for m in state_held}))
    return tmp_path


def test_default_reads_data_held_json(tmp_path):
    r = _root(tmp_path, ["X01", "X02"], state_held=["Y09"])
    assert hpe.load_held(r) == ["X01", "X02"]


def test_default_without_state_file(tmp_path):
    r = _root(tmp_path, ["X05"])
    assert hpe.load_held(r) == ["X05"]


def test_variant_spellings_match(tmp_path):
    r = _root(tmp_path, [" a24 ", "K003", "x7"])
    assert hpe.load_held(r) == ["A24", "K03", "X07"]


def test_override_still_works(tmp_path):
    r = _root(tmp_path, ["X01"])
    alt = tmp_path / "alt.json"; alt.write_text(json.dumps({"Z003": {}}))
    assert hpe.load_held(r, alt) == ["Z03"]


def test_default_path_helper_is_repo_relative(tmp_path):
    assert hpe.default_held_path(tmp_path) == tmp_path / "data" / "held.json"
