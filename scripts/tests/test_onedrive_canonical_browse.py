"""The From GF link helper must not call its own canonical output broken.

A canonical owner-browse URL is already in the fixed shape: a slash after
``.com`` and ``!`` encoded as ``%21``. ``looks_like_broken_live_browse``
decoded the query first, so the ``%21`` turned back into a bare ``!`` and
every canonical URL was reported as the failed Graph webUrl shape.

URLs with no ``id``/``resid`` must behave as they do on ``main``: the
``?cid=`` browse falls back to the path-style From GF URL, and the bare
host is a ``LinkError``. The raw-query reader must never hand ``None`` to
a substring test (that raised ``TypeError``).
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SOT = ROOT / "excel-kit" / "sot"
if str(SOT) not in sys.path:
    sys.path.insert(0, str(SOT))

from onedrive_from_gf_link import (  # noqa: E402
    LinkError,
    build_plan,
    looks_like_broken_live_browse,
)

CLI = SOT / "onedrive_from_gf_link.py"
CID = "7a74d53e91d4f05f"

CANONICAL = (
    "https://onedrive.live.com/?cid=7a74d53e91d4f05f"
    "&id=7A74D53E91D4F05F%21sae89effd79104c01a63f092754d1c9f9"
)
GUID_BROWSE = "https://onedrive.live.com/?id=ae89effd-7910-4c01-a63f-092754d1c9f9&cid=7a74d53e91d4f05f"
GRAPH_BROKEN = (
    "https://onedrive.live.com?cid=7a74d53e91d4f05f"
    "&id=7A74D53E91D4F05F!sae89effd79104c01a63f092754d1c9f9"
)

CID_ONLY = "https://onedrive.live.com/?cid=7a74d53e91d4f05f"
HOMEPAGE = "https://onedrive.live.com/"
EMPTY_ID = "https://onedrive.live.com/?id=&cid=7a74d53e91d4f05f"

PATH_BROWSE = (
    "https://d.docs.live.net/7a74d53e91d4f05f/Documents/Sassy%20Closet/From%20GF"
)
NO_ITEM_NOTE = "No item id — printed the path-style From GF URL only."
BROKEN_NOTE = "Input matches the failed Graph webUrl shape"
LINK_ERROR = "Need --cid and --item-id"


def run_cli(url: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(CLI), "--web-url", url],
        capture_output=True,
        text=True,
        timeout=60,
    )


def test_encoded_bang_is_not_the_broken_shape() -> None:
    assert looks_like_broken_live_browse(CANONICAL) is False


def test_canonical_url_gives_no_broken_warning() -> None:
    plan = build_plan(web_url=CANONICAL)
    assert plan.canonical_browse == CANONICAL
    assert plan.input_was_broken_browse is False
    assert plan.warnings == []


def test_guid_browse_stays_quiet() -> None:
    assert looks_like_broken_live_browse(GUID_BROWSE) is False
    assert build_plan(web_url=GUID_BROWSE).warnings == []


def test_graph_weburl_is_still_broken() -> None:
    assert looks_like_broken_live_browse(GRAPH_BROKEN) is True
    plan = build_plan(web_url=GRAPH_BROKEN)
    assert plan.input_was_broken_browse is True
    assert plan.canonical_browse == CANONICAL
    assert plan.warnings


def test_cid_only_prints_path_browse_without_crashing() -> None:
    """No `id`/`resid` at all: main prints the path-style URL and exits 0."""
    assert looks_like_broken_live_browse(CID_ONLY) is False
    plan = build_plan(web_url=CID_ONLY)
    assert plan.input_was_broken_browse is False
    assert plan.canonical_browse == PATH_BROWSE
    assert plan.path_browse == PATH_BROWSE
    assert len(plan.warnings) == 1
    assert NO_ITEM_NOTE in plan.warnings[0]
    assert not any(BROKEN_NOTE in note for note in plan.warnings)

    cli = run_cli(CID_ONLY)
    assert cli.returncode == 0, cli.stderr
    assert PATH_BROWSE in cli.stdout
    assert BROKEN_NOTE not in cli.stdout


def test_homepage_is_a_link_error_not_a_crash() -> None:
    """The bare host has nothing to resolve: main raises LinkError, exit 2."""
    assert looks_like_broken_live_browse(HOMEPAGE) is False
    with pytest.raises(LinkError, match=LINK_ERROR):
        build_plan(web_url=HOMEPAGE)

    cli = run_cli(HOMEPAGE)
    assert cli.returncode == 2, cli.stderr
    assert LINK_ERROR in cli.stderr
    assert "Traceback" not in cli.stderr
    assert "TypeError" not in cli.stderr


def test_empty_id_falls_back_to_path_browse() -> None:
    """An empty `id=` is falsy, so it must not shadow the no-item-id branch."""
    assert looks_like_broken_live_browse(EMPTY_ID) is False
    plan = build_plan(web_url=EMPTY_ID)
    assert plan.input_was_broken_browse is False
    assert plan.canonical_browse == PATH_BROWSE
    assert len(plan.warnings) == 1
    assert NO_ITEM_NOTE in plan.warnings[0]

    cli = run_cli(EMPTY_ID)
    assert cli.returncode == 0, cli.stderr
    assert PATH_BROWSE in cli.stdout
    assert "Traceback" not in cli.stderr
