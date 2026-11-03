"""Piece 97: --guide / stale-guide gate (placeholder data only)."""
import pytest

import stack_apply_dryrun as sad
from test_stack_apply_dryrun import _repo, _patch


def _write_guide(bundle, folder, order, included=()):
    pd = bundle / folder / "proof"
    pd.mkdir(parents=True, exist_ok=True)
    lines = ["# Draft review guide", "", "## Suggested merge order", ""]
    lines += ["%d. %s (base main)" % (i + 1, p) for i, p in enumerate(order)]
    if included:
        lines += ["", "Not listed (already included in the main chain, no separate merge): "
                  + ", ".join(included) + "."]
    (pd / "REVIEW-GUIDE.md").write_text("\n".join(lines) + "\n")
    return pd / "REVIEW-GUIDE.md"


def _inv(bundle, pieces):
    (bundle / "INVENTORY.tsv").write_text(
        "".join("%s\tabc1234\tdraft/%s\tmain\t1\n" % (p, p) for p in pieces))


def _setup(tmp_path):
    r = _repo(tmp_path)
    b = tmp_path / "bundle"
    _patch(r, b, "01-new", "b.txt", "new\n", "Piece 01: add b")
    _patch(r, b, "02-edit", "a.txt", "two\n", "Piece 02: edit a")
    return r, b


def test_guide_range_and_inventory_max(tmp_path):
    assert sad.guide_range(["17-a", "95-b"], ["18-c"]) == (17, 95)
    assert sad.guide_range([], []) == (None, None)
    _inv(tmp_path, ["01-new", "12-x", "03-y"])
    assert sad.inventory_max(str(tmp_path)) == 12


def test_stale_newest_guide_exits_3(tmp_path, capsys):
    r, b = _setup(tmp_path)
    _write_guide(b, "01-new", ["01-new"])
    _inv(b, ["01-new", "02-edit"])
    rc = sad.main(["--repo", str(r), "--bundle", str(b), "--main", "main", "--no-tests",
                   "--out", str(tmp_path / "o.md")])
    assert rc == 3
    assert "WARNING: guide covers up to 01 but bundle has 02" in capsys.readouterr().err
    assert not (tmp_path / "o.md").exists()


def test_allow_stale_runs_and_records(tmp_path):
    r, b = _setup(tmp_path)
    _write_guide(b, "01-new", ["01-new"])
    _inv(b, ["01-new", "02-edit"])
    res = sad.dryrun(str(r), str(b), "main", tests=False, allow_stale=True)
    md = sad.render(res)
    assert "Guide range: 01-01; newest INVENTORY piece: 02" in md
    assert "WARNING: guide covers up to 01 but bundle has 02" in md


def test_explicit_guide_used_over_newest(tmp_path):
    r, b = _setup(tmp_path)
    old = _write_guide(b, "01-new", ["01-new", "02-edit"])
    _write_guide(b, "02-edit", ["01-new"])  # newest, but narrower
    _inv(b, ["01-new", "02-edit"])
    res = sad.dryrun(str(r), str(b), "main", tests=False, guide_path=str(old))
    assert [p for p, _, _ in res["rows"]] == ["01-new", "02-edit"]
    md = sad.render(res)
    assert "(--guide)" in md and "Guide range: 01-02" in md
    assert "WARNING" not in md


def test_current_guide_no_warning(tmp_path):
    r, b = _setup(tmp_path)
    _write_guide(b, "02-edit", ["01-new", "02-edit"])
    _inv(b, ["01-new", "02-edit"])
    res = sad.dryrun(str(r), str(b), "main", tests=False)
    assert res["stale"] is None and res["guide_source"] == "newest in bundle"


def test_missing_explicit_guide(tmp_path):
    r, b = _setup(tmp_path)
    _inv(b, ["01-new"])
    with pytest.raises(SystemExit):
        sad.dryrun(str(r), str(b), "main", tests=False, guide_path=str(tmp_path / "nope.md"))
