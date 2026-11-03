"""piece-295: hard_recheck.sh step timeouts never hang on prompts or TERM-ignoring children."""
import pathlib, re, subprocess

SCRIPT = pathlib.Path(__file__).resolve().parents[1] / "hard_recheck.sh"


def _timed_fn():
    src = SCRIPT.read_text()
    return re.search(r"^timed\(\) \{.*?^\}", src, re.S | re.M).group(0)


def _run(cmd, tmo="1", kill="1"):
    script = f'TMO={tmo}; KILL_AFTER={kill}\n{_timed_fn()}\ntimed "$1" bash -c "$2"; echo "RC=$RC"'
    return subprocess.run(["bash", "-c", script, "x", "/dev/null", cmd],
                          capture_output=True, text=True, timeout=20)


def test_syntax_and_kill_after():
    assert subprocess.run(["bash", "-n", str(SCRIPT)]).returncode == 0
    src = SCRIPT.read_text()
    assert 'timeout -k "$KILL_AFTER"' in src and "< /dev/null" in src


def test_stdin_prompt_does_not_hang():
    r = _run("read x; exit 0", tmo="5")
    assert "RC=0" in r.stdout


def test_term_ignoring_child_is_killed_and_reported_as_timeout():
    r = _run("trap '' TERM; sleep 30", tmo="1", kill="1")
    assert "RC=124" in r.stdout
