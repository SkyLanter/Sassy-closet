import json, subprocess, sys
from pathlib import Path
import caption_lint as cl

HERE = Path(__file__).parent
FX = HERE / "fixtures" / "captions"
PRICES = json.loads((FX / "prices.json").read_text())


def codes(name):
    return {c for c, _ in cl.lint_text((FX / name).read_text(encoding="utf-8"), PRICES)}


def test_prices_fixture_keeps_s06_25():
    assert PRICES["S06"] == 25


def test_a09_flags():
    c = codes("a09.txt")
    assert {"MA_MISSING_ACCENT", "MISSING_ACCENT"} <= c
    assert "NO_GIA" not in c and "GIA_MISMATCH" not in c and "NO_SIZE" not in c
    msgs = " ".join(m for _, m in cl.lint_text((FX / "a09.txt").read_text(encoding="utf-8"), PRICES))
    for w in ('"mc"', '"mu"'):
        assert w in msgs


def test_s06_clean():
    assert codes("s06_clean.txt") == set()


def test_no_gia():
    assert codes("a08_no_gia.txt") == {"NO_GIA"}


def test_ma_no_accent_and_malformed_gia():
    c = codes("d06_ma_noaccent_gia_malformed.txt")
    assert "MA_MISSING_ACCENT" in c and "GIA_MALFORMED" in c
    assert "PRICE_UNKNOWN" in c  # D06 not in price list


def test_price_mismatch():
    assert codes("s06_wrong_price.txt") == {"GIA_MISMATCH"}


def test_no_size():
    assert codes("s06_no_size.txt") == {"NO_SIZE"}


def test_no_ma_line():
    c = codes("no_ma_line.txt")
    assert "NO_MA_LINE" in c and "PRICE_UNCHECKED" in c


def test_cli_exit_codes():
    script = str(HERE / "caption_lint.py")
    ok = subprocess.run([sys.executable, script, "--prices", str(FX / "prices.json"), str(FX / "s06_clean.txt")],
                        capture_output=True, text=True)
    assert ok.returncode == 0 and "OK" in ok.stdout
    bad = subprocess.run([sys.executable, script, "--prices", str(FX / "prices.json"),
                          str(FX / "s06_clean.txt"), str(FX / "a09.txt")], capture_output=True, text=True)
    assert bad.returncode == 1
    assert "a09.txt: FLAG" in bad.stdout and "s06_clean.txt: OK" in bad.stdout
