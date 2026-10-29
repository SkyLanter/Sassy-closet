"""Piece 217 guard: no bare short-digit substring asserts against output text.

`assert "300" not in stdout` false-fails whenever a printed path (pytest's temp
dir, e.g. /tmp/pytest-of-box/pytest-300/...) happens to contain those digits;
`assert "9" in out` can false-pass the same way. That was the piece 215 flake.
Mask the path first (see test_cost_basis_reconcile.stdout_cost_leaks) or compare
parsed values. Known-safe uses are exempted below, each with why.
"""
import ast
import re
from pathlib import Path

TESTS = Path(__file__).resolve().parent
DIGITS = re.compile(r"^\d{1,4}(\.\d+)?$")

# (file, literal) -> why it cannot pick up digits from a path / clock / env.
EXEMPT = {
    ("test_privacy_scan.py", "88"): "checks redact_text() output / redacted file body; no paths in that text",
    ("test_privacy_scan.py", "15.5"): "redact_text() output of an in-memory table; no paths",
    ("test_privacy_scan.py", "0.3"): "redact_text() output of an in-memory table; no paths",
    ("test_privacy_scan.py", "64"): "privacy_scan prints paths relative to the scanned dir (p.json:1:), never the temp dir",
    ("test_cost_basis_reconcile.py", "300.00"): "positive check on the LOCAL ONLY report body, which never contains the out path",
    ("test_summary_new_findings.py", "9.00"): "build() text from in-memory inputs and a fixed date; no paths",
    ("test_size_wiring.py", "38"): "q.reason is a built reason string, not output that includes paths",
}


def hits():
    found = []
    for f in sorted(TESTS.glob("test_*.py")):
        tree = ast.parse(f.read_text(encoding="utf-8"), filename=str(f))
        for node in ast.walk(tree):
            if not isinstance(node, ast.Assert):
                continue
            for cmp in [n for n in ast.walk(node.test) if isinstance(n, ast.Compare)]:
                if not any(isinstance(op, (ast.In, ast.NotIn)) for op in cmp.ops):
                    continue
                left = cmp.left
                if isinstance(left, ast.Constant) and isinstance(left.value, str) and DIGITS.match(left.value):
                    found.append((f.name, left.value, node.lineno))
    return found


def test_no_unmasked_short_digit_substring_asserts():
    bad = [f"{f}:{ln}: assert {lit!r} in/not in <text>" for f, lit, ln in hits() if (f, lit) not in EXEMPT]
    assert bad == [], "bare short-digit substring asserts (mask paths or compare parsed values):\n" + "\n".join(bad)


def test_exemptions_are_still_used():
    used = {(f, lit) for f, lit, _ in hits()}
    stale = sorted(set(EXEMPT) - used)
    assert stale == [], f"remove stale exemptions: {stale}"


def test_guard_catches_the_piece_215_pattern(tmp_path, monkeypatch):
    bad = tmp_path / "test_fake.py"
    bad.write_text('def test_x(capsys):\n    text = "wrote /tmp/x"\n    assert "3" + "00" not in text\n'
                   '    assert "' + "30" + '0" not in text\n')
    monkeypatch.setattr(__import__(__name__), "TESTS", tmp_path)
    assert [(f, lit) for f, lit, _ in hits()] == [("test_fake.py", "300")]
