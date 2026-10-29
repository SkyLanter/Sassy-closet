"""Piece 94: Inputs header is worktree-neutral (placeholder data only)."""
import subprocess, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import boss_decisions as bd  # noqa: E402

ORDER = '{"order": ["Z01", "Z02"]}\n'
HELD = '{"held": ["Z02"]}\n'


def wt(tmp, name, order=ORDER):
    d = tmp / name
    (d / "sassy-closet-shop/data").mkdir(parents=True)
    (d / "data").mkdir()
    (d / ".git").write_text("gitdir: placeholder\n")
    (d / "sassy-closet-shop/data/popular-order.json").write_text(order)
    (d / "data/held.json").write_text(HELD)
    return d


def run(root, w, *extra):
    return bd.main(["--date", "2026-01-01", "--root", str(root), "--digest", str(root / "dig.txt"),
                    "--order", str(w / "sassy-closet-shop/data/popular-order.json"),
                    "--held", str(w / "data/held.json"), *extra])


def setup(tmp):
    root = tmp / "root"
    root.mkdir()
    (root / "dig.txt").write_text("placeholder digest\n")
    return root


def test_identical_worktrees_pass(tmp_path):
    root = setup(tmp_path)
    a, b = wt(tmp_path, "work-a"), wt(tmp_path, "work-b")
    assert run(root, a) == 0
    assert run(root, b) == 0
    text = (root / "out/reports/2026-01-01/BOSS-DECISIONS.md").read_text()
    assert str(tmp_path) not in text
    assert "order=sassy-closet-shop/data/popular-order.json@" in text
    assert "digest=dig.txt " in text


def test_changed_file_refused(tmp_path):
    root = setup(tmp_path)
    a, b = wt(tmp_path, "work-a"), wt(tmp_path, "work-b", order='{"order": ["Z03"]}\n')
    assert run(root, a) == 0
    assert run(root, b) == 2
    assert run(root, b, "--force") == 0


def test_old_absolute_header_is_unrecorded(tmp_path):
    out = tmp_path / "BOSS-DECISIONS.md"
    out.write_text("# x\n\nInputs: date=2026-01-01 root=/r order=/w/o.json held=- digest=- | total=1\n")
    assert bd.existing_inputs(out) == ""


def test_neutral_path_forms(tmp_path):
    root = setup(tmp_path)
    a = wt(tmp_path, "work-a")
    assert bd.neutral_path(root, root / "out/x.md") == "out/x.md"
    assert bd.neutral_path(root, a / "data/held.json") == "data/held.json"
    assert bd.neutral_path(root, None) == "-"
