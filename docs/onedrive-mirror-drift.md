# OneDrive mirror drift (sell USD) — Boss decision

Read-only report. Nothing was written to OneDrive, Blob, intake, Meta, or `products.json`.

Source: committed fixture `docs/fixtures/onedrive-mirror/mirror-vs-live-2026-10-28.json`
(from the piece-259 snapshot, proof-241, 2026-10-28 ~11:18 PM PT). The OneDrive mirror was not re-read live for this piece. Only rows proven in committed fixtures are listed.

| mã | OneDrive mirror | live (Blob) | status |
|---|---|---|---|
| D05 | 28 | 26 | DRIFT (+2 on mirror) |
| V03 | 24 | 21 | DRIFT (+3 on mirror) |

S06: no OneDrive mirror row. Live is $25; the lock is untouched.

Regenerate: `python3 scripts/onedrive_mirror_drift_report.py` (`--strict` exits 1 on drift). The script writes nothing.

## Boss decision needed
Live Blob is what the shop reads. The mirror is stale. Pick one:
1. Refresh the mirror D05→26 and V03→21 to match live. **This needs Boss's OK before any OneDrive write.**
2. Leave the mirror as is and treat it as stale.

Mã compares use `held_policy.norm_ma`.
