#!/usr/bin/env python3
"""Piece 103 (+105: highest vs most-recent piece, backup count): READ-ONLY 'Draft work waiting' lines for the daily summary.

Reads the bundle tarball and its unpacked INVENTORY.tsv and reports, in plain
words: piece count, newest piece + commit, short sha256, inventory check
result and tarball age. A missing or unreadable bundle gives one line, never
an exception. No network, no writes.
"""
import datetime as dt
import hashlib
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
DEFAULT_TGZ = Path("/workspace/sassy-closet/out/pending-draft-prs.tgz")
HEAD = "Draft work waiting (local bundle, nothing merged):"


def _num(folder):
    n = ""
    for ch in folder:
        if not ch.isdigit():
            break
        n += ch
    return int(n) if n else -1


def read_rows(inv):
    rows = []
    for ln in Path(inv).read_text(encoding="utf-8").splitlines():
        parts = ln.split("\t")
        if len(parts) >= 2 and parts[0][:1].isdigit():
            rows.append(parts)
    return rows


def short_sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    x = h.hexdigest()
    return f"{x[:8]}…{x[-4:]}"


def age_words(seconds):
    s = max(0, int(seconds))
    if s < 90:
        return "under 2 minutes old"
    if s < 2 * 3600:
        return f"{s // 60} minutes old"
    if s < 2 * 86400:
        return f"{s // 3600} hours old"
    return f"{s // 86400} days old"


def inventory_result(folder):
    try:
        sys.path.insert(0, str(HERE))
        import bundle_inventory_check as bic
        inv = bic.check(str(folder))
    except Exception as e:  # noqa: BLE001
        return f"could not run ({type(e).__name__})"
    bad = len(inv.get("issues", [])) + len(inv.get("unallowed_missing_rows", []))
    allow = len(inv.get("folders_without_row", []))
    if bad:
        return f"PROBLEM, {bad} issue(s) found"
    return (f"OK, {inv.get('folders', '?')} folders and {inv.get('rows', '?')} rows"
            + (f" ({allow} allowlisted folder(s) without a row)" if allow else ""))


def recent_piece(folder, rows):
    """Piece 105: most recently added piece by PROOF.md mtime, else folder mtime."""
    best = None
    for r in rows:
        d = Path(folder) / r[0]
        try:
            pf = d / "proof" / "PROOF.md"
            alt = d / "PROOF.md"
            m = (pf if pf.exists() else alt if alt.exists() else d).stat().st_mtime
        except OSError:
            continue
        if best is None or m > best[0]:
            best = (m, r)
    return best[1] if best else None


def size_words(n):
    for unit, k in (("GB", 1 << 30), ("MB", 1 << 20), ("KB", 1 << 10)):
        if n >= k:
            return f"{n / k:.1f} {unit}"
    return f"{n} bytes"


def _tree_size(p):
    if p.is_symlink() or p.is_file():
        return p.lstat().st_size
    tot = 0
    for root, _dirs, files in os.walk(p):
        for f in files:
            try:
                tot += os.lstat(os.path.join(root, f)).st_size
            except OSError:
                pass
    return tot


def backup_stats(tgz, folder):
    """Piece 105: READ-ONLY count + total size of bundle backups (.bak-*). Deletes nothing."""
    names = {Path(tgz).name + ".bak-", Path(folder).name + ".bak-"}
    count = size = 0
    for parent in {Path(tgz).parent, Path(folder).parent}:
        try:
            entries = list(parent.iterdir())
        except OSError:
            continue
        for e in entries:
            if any(e.name.startswith(n) for n in names):
                count += 1
                try:
                    size += _tree_size(e)
                except OSError:
                    pass
    return count, size


def status_lines(tgz=DEFAULT_TGZ, folder=None, now=None):
    tgz = Path(tgz)
    folder = Path(folder) if folder else Path(str(tgz)[:-4] if str(tgz).endswith(".tgz") else str(tgz) + ".d")
    try:
        st = tgz.stat()
        rows = read_rows(folder / "INVENTORY.tsv")
        sha = short_sha(tgz)
    except Exception as e:  # noqa: BLE001
        return [HEAD, f"- Bundle missing or unreadable ({type(e).__name__}), so draft work can't be listed today."]
    now = now if now is not None else dt.datetime.now().timestamp()
    L = [HEAD, f"- {len(rows)} draft pieces waiting for your review."]
    if rows:
        top = max(rows, key=lambda r: _num(r[0]))
        L.append(f"- Highest-numbered piece: {top[0]} (commit {top[1][:7]}).")
        rec = recent_piece(folder, rows)
        if rec is not None:
            same = " (same piece)" if rec[0] == top[0] else ""
            L.append(f"- Most recently added piece: {rec[0]} (commit {rec[1][:7]}){same}.")
        else:
            L.append("- Most recently added piece: unknown (no piece folders found).")
    else:
        L.append("- Highest-numbered piece: none listed in the inventory.")
    L.append(f"- Bundle fingerprint: {sha}.")
    L.append(f"- Inventory check: {inventory_result(folder)}.")
    L.append(f"- Bundle file is {age_words(now - st.st_mtime)}.")
    n, sz = backup_stats(tgz, folder)
    L.append(f"- Bundle backups (.bak-*): {n}, {size_words(sz)} total (count only, nothing deleted).")
    return L


if __name__ == "__main__":
    print("\n".join(status_lines(sys.argv[1] if len(sys.argv) > 1 else DEFAULT_TGZ)))
