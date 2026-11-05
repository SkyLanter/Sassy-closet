#!/usr/bin/env python3
"""Plain-English list of what is waiting on Boss. Read-only.

One list for the 2-day digest. It names four sources and nothing else:

- Intake submissions with no stored sell price, or a stored price that is
  under the intake floor or hand-edited. A blank sell stays blank. This
  does not invent a dollar. The floor is the intake rule: tiered quote, and
  the 35% caption floor. V/Q/D debox is the locked $7.50. Other letters use
  $0, the same as the intake calculator. A typed price with no saved
  calculator snapshot is hand-edited even when it matches the quote.
- Held mãs in data/held.json (heldIncomplete).
- Open draft pull requests in this repo whose latest independent recheck
  comment is PASS. `gh pr list` is used when it runs. `--prs-json` is the
  offline fixture. A comment counts only when its first line is
  "INDEPENDENT RECHECK PASS" or "INDEPENDENT RECHECK FAIL" and the author
  is not the pull request author. The latest of those verdicts must be PASS.
- Whether the latest Taobao cost recheck summary is signed-out blocked.
  scripts/cost_recheck_block.py is used when this checkout has it (draft
  #294). Otherwise taobao_login_needed is read with that same truth table.

Pass --intake, --held, --prs-json, and --cost-summary to stay offline.
A failed read prints a "could not read" line and does not raise. Nothing
is written. No message is sent. S06 stays $25, and a different stored sell
for S06 is not repeated.
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import urllib.request
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from pathlib import Path

from autolist import price
from held_policy import MA_RE, default_held_path, norm_ma

try:
    import cost_recheck_block
except ImportError:
    cost_recheck_block = None

ROOT = Path(__file__).resolve().parents[1]
INTAKE_URL = "https://sassy-closet.vercel.app/api/submissions"
USER_AGENT = "sassy-boss-approval-queue/1 (read-only)"
DEFAULT_FX = Decimal("6.723")
MARGIN_FLOOR = Decimal("0.35")
S06 = "S06"
S06_LOCK = Decimal("25")
DEBOX = {"V": Decimal("7.5"), "Q": Decimal("7.5"), "D": Decimal("7.5")}
_AMOUNT = re.compile(r"^\d+(?:\.\d+)?$")
_URL = re.compile(r"https?://\S+", re.I)
_PHONE = re.compile(r"(?:\+\d{1,3}[ .-]?)?\d{3}[ .-]\d{3}[ .-]\d{4}")
_VERDICT = re.compile(r"^INDEPENDENT RECHECK (PASS|FAIL)\b", re.I)
_YEN = "\u00a5\uffe5"
_HOSTS = ("taobao", "tmall", "tb.cn", "1688")
_SUMMARY_NAME = re.compile(r"^summary\.(\d{4}-\d{2}-\d{2})\.json$")
_BLOCK_STRINGS = {"true", "yes", "y", "1"}
GH_ARGS = [
    "gh", "pr", "list", "--state", "open", "--draft", "--limit", "1000",
    "--json", "number,title,isDraft,state,author,comments,reviews",
]

BLOCKED = "The latest Taobao cost recheck is signed out, so it is blocked."
NOT_BLOCKED = "The latest Taobao cost recheck is not signed-out blocked."
NO_SUMMARY = "No Taobao cost recheck summary was found."
TAOBAO_UNREAD = "Taobao cost recheck: could not read."
INTAKE_UNREAD = "Intake prices: could not read."
HELD_UNREAD = "Held list: could not read."
DRAFTS_UNREAD = "Draft PRs: could not read."


def _amount(value: object) -> Decimal | None:
    """A positive plain dollar or JSON number. Junk text is not a price."""
    if isinstance(value, bool) or value is None:
        return None
    if isinstance(value, int):
        number = Decimal(value)
    elif isinstance(value, float):
        try:
            number = Decimal(str(value))
        except InvalidOperation:
            return None
    elif isinstance(value, str):
        text = value.strip()
        if text.startswith("$"):
            text = text[1:].strip()
        if not _AMOUNT.fullmatch(text):
            return None
        try:
            number = Decimal(text)
        except InvalidOperation:
            return None
    else:
        return None
    if not number.is_finite() or number <= 0:
        return None
    return number


def _token(value: object) -> str:
    return "" if value is None else str(value).strip().casefold()


def _letter(row: dict, code: str) -> str:
    raw = row.get("kind")
    text = "" if raw is None else str(raw).strip()
    if text:
        return text[:1].upper()
    return code[:1]


def _fx(value: str) -> Decimal | None:
    try:
        number = Decimal(str(value).strip())
    except InvalidOperation:
        return None
    if not number.is_finite() or number <= 0:
        return None
    return number


def _is_lock(number: Decimal) -> bool:
    return number == S06_LOCK


def _dollars(number: Decimal) -> str:
    cents = number.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    if cents == cents.to_integral_value():
        return f"${int(cents)}"
    return f"${cents}"


def stored_sell(row: dict, fx: Decimal) -> tuple[Decimal | None, str]:
    """Stored sell as USD, plus 'usd' or 'cny' for how it may be printed."""
    if _token(row.get("sell_currency")) == "cny":
        cny = _amount(row.get("sell_cny"))
        if cny is None or fx <= 0:
            return None, "cny"
        return cny / fx, "cny"
    return _amount(row.get("sell_usd")), "usd"


def _goods(row: dict, fx: Decimal) -> Decimal | None:
    currency = _token(row.get("cost_currency"))
    cny = _amount(row.get("cost_cny"))
    usd = _amount(row.get("cost_usd"))
    if currency == "cny" and cny is not None:
        return cny / fx
    if usd is not None:
        return usd
    if cny is not None:
        return cny / fx
    return None


def landed_usd(row: dict, fx: Decimal, code: str) -> Decimal | None:
    goods = _goods(row, fx)
    if goods is None:
        return None
    return goods + DEBOX.get(_letter(row, code), Decimal(0))


def auto_sell(row: dict) -> Decimal | None:
    snapshot = row.get("auto_price")
    if not isinstance(snapshot, dict):
        return None
    return _amount(snapshot.get("sellUsd"))


def _under(sell: Decimal, landed: Decimal, quote: int) -> bool:
    if sell + Decimal("0.000001") < Decimal(quote):
        return True
    if sell <= 0:
        return False
    return (sell - landed) / sell < MARGIN_FLOOR


def classify(row: dict, fx: Decimal) -> str | None:
    """blank, under, hand, under-hand, lock, or None when the row is not waiting."""
    code = norm_ma(row.get("ma"))
    if not MA_RE.fullmatch(code):
        return None
    stored, _mode = stored_sell(row, fx)
    if code == S06:
        if stored is None or _is_lock(stored):
            return None
        return "lock"
    if stored is None:
        return "blank"
    snapshot = auto_sell(row)
    hand = snapshot is None or abs(stored - snapshot) > Decimal("0.005")
    landed = landed_usd(row, fx, code)
    under = False
    if landed is not None and landed > 0:
        try:
            quote = price(landed)
        except (ArithmeticError, ValueError, RuntimeError):
            quote = None
        if quote is not None and _under(stored, landed, quote):
            under = True
    if under and hand:
        return "under-hand"
    if under:
        return "under"
    if hand:
        return "hand"
    return None


def _priced_line(code: str, row: dict, fx: Decimal, kind: str) -> str:
    stored, mode = stored_sell(row, fx)
    if mode == "cny":
        lines = {
            "under": f"{code} has a CNY sell price under the price floor.",
            "hand": f"{code} has a hand-edited CNY sell price.",
            "under-hand": f"{code} has a CNY sell price under the price floor and it is hand-edited.",
        }
        return lines[kind]
    label = _dollars(stored if stored is not None else Decimal(0))
    lines = {
        "under": f"{code} is {label} on intake, under the price floor.",
        "hand": f"{code} is {label} on intake, hand-edited.",
        "under-hand": f"{code} is {label} on intake, under the price floor and hand-edited.",
    }
    return lines[kind]


def price_lines(rows: list, fx: Decimal) -> list[str]:
    chosen: dict[str, dict] = {}
    for row in rows:
        if not isinstance(row, dict):
            continue
        code = norm_ma(row.get("ma"))
        if MA_RE.fullmatch(code):
            chosen[code] = row
    blanks: list[str] = []
    priced: list[str] = []
    locks: list[str] = []
    for code in sorted(chosen):
        kind = classify(chosen[code], fx)
        if kind == "blank":
            blanks.append(code)
        elif kind == "lock":
            locks.append("S06 stays $25.")
        elif kind in {"under", "hand", "under-hand"}:
            priced.append(_priced_line(code, chosen[code], fx, kind))
    lines: list[str] = []
    if blanks:
        lines.append("No sell price on intake: " + ", ".join(blanks) + ".")
    lines.extend(priced)
    lines.extend(locks)
    return lines


def rows_from_payload(payload: object) -> list | None:
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict):
        for key in ("submissions", "rows"):
            value = payload.get(key)
            if isinstance(value, list):
                return value
    return None


def held_codes(payload: object) -> list[str] | None:
    """heldIncomplete order, with invalid entries skipped. None if the shape is wrong."""
    if isinstance(payload, list):
        raw = payload
    elif isinstance(payload, dict) and isinstance(payload.get("heldIncomplete"), list):
        raw = payload["heldIncomplete"]
    else:
        return None
    codes: list[str] = []
    seen: set[str] = set()
    for item in raw:
        if not isinstance(item, str):
            continue
        code = norm_ma(item)
        if not MA_RE.fullmatch(code) or code in seen:
            continue
        seen.add(code)
        codes.append(code)
    return codes


def held_line(codes: list[str]) -> str | None:
    if not codes:
        return None
    return "Held mãs still waiting: " + ", ".join(codes) + "."


def _login(value: object) -> str:
    if isinstance(value, str):
        return value.strip().casefold()
    if isinstance(value, dict):
        for key in ("login", "name"):
            raw = value.get(key)
            if isinstance(raw, str) and raw.strip():
                return raw.strip().casefold()
    return ""


def _open_draft(pr: dict) -> bool:
    if pr.get("merged") is True:
        return False
    state = pr.get("state")
    if isinstance(state, str) and state.strip() and state.strip().casefold() != "open":
        return False
    draft = pr.get("isDraft", pr.get("draft"))
    if isinstance(draft, str):
        return draft.strip().casefold() in {"true", "yes", "1"}
    return draft is True


def _pr_number(pr: dict) -> int | None:
    raw = pr.get("number")
    if isinstance(raw, str) and raw.isdigit():
        raw = int(raw)
    if isinstance(raw, bool) or not isinstance(raw, int) or raw < 1:
        return None
    return raw


def _verdict(body: object) -> str | None:
    if not isinstance(body, str):
        return None
    for line in body.splitlines():
        text = line.strip()
        if not text:
            continue
        match = _VERDICT.match(text)
        return match.group(1).upper() if match else None
    return None


def _skip_token(token: str) -> bool:
    if "@" in token or any(mark in token for mark in _YEN):
        return True
    folded = token.casefold()
    if any(host in folded for host in _HOSTS) or _PHONE.search(token):
        return True
    return False


def _clean_title(title: object) -> str:
    text = title if isinstance(title, str) else ""
    text = _URL.sub("", text)
    parts = [token for token in text.split() if not _skip_token(token)]
    text = " ".join(parts).strip(" -")
    if len(text) > 120:
        text = text[:117].rstrip() + "..."
    return text


def _notes(pr: dict) -> list[tuple[str, int, str, str]]:
    """Independent-recheck notes in list order. A missing time inherits the previous one.

    A later FAIL that arrived without a timestamp then sorts after the PASS it follows.
    """
    pending: list[tuple[int, str, str, str]] = []
    index = 0
    sources = (
        ("comments", ("createdAt", "submittedAt")),
        ("reviews", ("submittedAt", "createdAt")),
    )
    for key, time_keys in sources:
        raw = pr.get(key)
        if not isinstance(raw, list):
            continue
        for note in raw:
            index += 1
            if not isinstance(note, dict):
                continue
            verdict = _verdict(note.get("body"))
            if verdict is None:
                continue
            when = ""
            for time_key in time_keys:
                stamp = note.get(time_key)
                if isinstance(stamp, str) and stamp.strip():
                    when = stamp.strip()
                    break
            pending.append((index, _login(note.get("author")), verdict, when))
    carried = ""
    notes: list[tuple[str, int, str, str]] = []
    for index, author, verdict, when in pending:
        if when:
            carried = when
        notes.append((when or carried, index, author, verdict))
    return notes


def draft_lines(prs: list) -> list[str]:
    chosen: dict[int, str] = {}
    for pr in prs:
        if not isinstance(pr, dict) or not _open_draft(pr):
            continue
        number = _pr_number(pr)
        if number is None:
            continue
        author = _login(pr.get("author"))
        verdicts = [
            (when, index, verdict)
            for when, index, note_author, verdict in _notes(pr)
            if author and note_author and note_author != author
        ]
        verdicts.sort()
        if not verdicts or verdicts[-1][2] != "PASS":
            continue
        title = _clean_title(pr.get("title"))
        if title:
            line = f"Draft PR #{number}, {title}, has an independent PASS and is still open."
        else:
            line = f"Draft PR #{number} has an independent PASS and is still open."
        chosen[number] = line
    return [chosen[number] for number in sorted(chosen)]


def defensive_login_blocked(doc: object) -> bool:
    """Same taobao_login_needed table as cost_recheck_block.login_blocked.

    JSON true, int 1, and float 1.0 count. The strings true, yes, y, and 1
    count after strip and case fold. False, 0, 0.0, false, no, the string
    1.0, a missing field, and a non-dict do not.
    """
    if not isinstance(doc, dict):
        return False
    value = doc.get("taobao_login_needed")
    if isinstance(value, bool):
        return value is True
    if type(value) is int and value == 1:
        return True
    if type(value) is float and value == 1.0:
        return True
    if isinstance(value, str) and value.strip().casefold() in _BLOCK_STRINGS:
        return True
    return False


def login_blocked(doc: object) -> bool:
    module = cost_recheck_block
    if module is not None and hasattr(module, "login_blocked"):
        try:
            return bool(module.login_blocked(doc))
        except Exception:
            return defensive_login_blocked(doc)
    return defensive_login_blocked(doc)


def read_json(path: Path) -> tuple[str, object]:
    try:
        text = path.read_text(encoding="utf-8-sig")
    except FileNotFoundError:
        return "missing", None
    except (OSError, UnicodeError):
        return "bad", None
    try:
        return "ok", json.loads(text)
    except json.JSONDecodeError:
        return "bad", None


def summary_state(path: Path) -> str:
    """missing, bad, blocked, or ok. Never raises."""
    module = cost_recheck_block
    if module is not None and hasattr(module, "load_summary"):
        try:
            state, _doc = module.load_summary(path)
        except Exception:
            state = None
        if state in {"missing", "bad", "blocked", "ok"}:
            return state
    status, doc = read_json(path)
    if status == "missing":
        return "missing"
    if status != "ok" or not isinstance(doc, dict):
        return "bad"
    if login_blocked(doc):
        return "blocked"
    return "ok"


def latest_summary(directory: Path) -> tuple[str, Path | None]:
    """(ok|missing|bad, path). bad is a read failure. missing means no dated file."""
    try:
        if not directory.is_dir():
            return "missing", None
        found: list[tuple[str, Path]] = []
        for path in directory.glob("summary.????-??-??.json"):
            match = _SUMMARY_NAME.match(path.name)
            if match:
                found.append((match.group(1), path))
    except OSError:
        return "bad", None
    if not found:
        return "missing", None
    found.sort()
    return "ok", found[-1][1]


def taobao_line(summary: Path | None, directory: Path) -> str:
    if summary is not None:
        state = summary_state(summary)
        if state == "missing" or state == "bad":
            return TAOBAO_UNREAD
    else:
        found, path = latest_summary(directory)
        if found == "bad":
            return TAOBAO_UNREAD
        if found == "missing" or path is None:
            return NO_SUMMARY
        state = summary_state(path)
        if state == "bad":
            return TAOBAO_UNREAD
        if state == "missing":
            return NO_SUMMARY
    if state == "blocked":
        return BLOCKED
    if state == "ok":
        return NOT_BLOCKED
    return TAOBAO_UNREAD


def _http_url(url: str) -> bool:
    return url.startswith("https://") or url.startswith("http://")


def fetch_json(url: str, timeout: float) -> object | None:
    if timeout <= 0 or not _http_url(url):
        return None
    request = urllib.request.Request(
        url,
        headers={"Accept": "application/json", "User-Agent": USER_AGENT},
        method="GET",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            raw = response.read()
        return json.loads(raw.decode("utf-8-sig"))
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError):
        return None


def _run_gh(args: list[str], cwd: str, timeout: float) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        args,
        cwd=cwd,
        timeout=timeout,
        check=False,
        capture_output=True,
        text=True,
    )


def load_prs(path: Path | None) -> tuple[str, list | None]:
    if path is not None:
        status, data = read_json(path)
        if status != "ok" or not isinstance(data, list):
            return "bad", None
        return "ok", data
    if shutil.which("gh") is None:
        return "bad", None
    try:
        completed = _run_gh(GH_ARGS, str(ROOT), 20)
    except (OSError, subprocess.TimeoutExpired):
        return "bad", None
    if completed.returncode != 0 or not isinstance(completed.stdout, str):
        return "bad", None
    try:
        data = json.loads(completed.stdout)
    except json.JSONDecodeError:
        return "bad", None
    if not isinstance(data, list):
        return "bad", None
    return "ok", data


def intake_section(path: Path | None, url: str, timeout: float, fx_text: str) -> list[str]:
    fx = _fx(fx_text)
    if fx is None:
        return [INTAKE_UNREAD]
    if path is not None:
        status, payload = read_json(path)
        if status != "ok":
            return [INTAKE_UNREAD]
    else:
        payload = fetch_json(url, timeout)
        if payload is None:
            return [INTAKE_UNREAD]
    rows = rows_from_payload(payload)
    if rows is None:
        return [INTAKE_UNREAD]
    return price_lines(rows, fx)


def held_section(path: Path) -> list[str]:
    status, payload = read_json(path)
    if status != "ok":
        return [HELD_UNREAD]
    codes = held_codes(payload)
    if codes is None:
        return [HELD_UNREAD]
    line = held_line(codes)
    return [line] if line else []


def draft_section(path: Path | None) -> list[str]:
    status, prs = load_prs(path)
    if status != "ok" or prs is None:
        return [DRAFTS_UNREAD]
    return draft_lines(prs)


def render(parts: list[str], taobao: str) -> str:
    body = list(parts)
    blocked = taobao == BLOCKED
    unread = any("could not read" in line for line in body) or "could not read" in taobao
    if not body and not blocked and not unread:
        body.append("Nothing is waiting.")
    lines = ["Waiting on Boss", *[f"- {line}" for line in body], f"- {taobao}"]
    return "\n".join(lines) + "\n"


def report(args: argparse.Namespace) -> str:
    prices = intake_section(args.intake, args.intake_url, args.timeout, args.fx)
    held = held_section(args.held or default_held_path())
    drafts = draft_section(args.prs_json)
    taobao = taobao_line(args.cost_summary, args.cost_dir)
    return render([*prices, *held, *drafts], taobao)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Read-only list of what is waiting on Boss.")
    parser.add_argument("--intake", type=Path, help="Submissions JSON fixture. Skips the network.")
    parser.add_argument("--intake-url", default=INTAKE_URL, help="Used only when --intake is omitted.")
    parser.add_argument("--timeout", type=float, default=15, help="Intake GET timeout in seconds.")
    parser.add_argument("--fx", default=str(DEFAULT_FX), help="CNY per USD. Default matches intake.")
    parser.add_argument("--held", type=Path, help="Held JSON. Default is data/held.json.")
    parser.add_argument("--prs-json", type=Path, help="Draft PR fixture. Skips gh.")
    parser.add_argument("--cost-summary", type=Path, help="One cost-recheck summary JSON file.")
    parser.add_argument(
        "--cost-dir",
        type=Path,
        default=ROOT / "verify" / "cost-recheck",
        help="Directory of summary.YYYY-MM-DD.json files, used when --cost-summary is omitted.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    try:
        args = build_parser().parse_args(argv)
    except SystemExit as exc:
        code = exc.code
        return 0 if code is None else int(code)
    sys.stdout.write(report(args))
    return 0


if __name__ == "__main__":
    sys.exit(main())
