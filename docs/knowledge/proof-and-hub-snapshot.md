# Proof folders and the live Excel snapshot

## Status on 2026-11-02

`/cursor/stores/bot/knowledge-snapshot/INDEX.md` is on disk. It was built that day as a read-only, PII-scrubbed export (box `proof-*` folders read only; OneDrive list/download only). This knowledge base copies schemas and the index sentences. It does not copy example rows, proof logs, or the files under `proof-folders/*/files/`.

| What INDEX covers | Where it is written | Still UNKNOWN |
| --- | --- | --- |
| 11 exported workbooks, sheet names, row counts, column headers | [snapshot-excel.md](snapshot-excel.md). Meaning cells are `unknown (header only: …)`. | Order_Log and Wishlist (corrupt, not exported). Which of the two `TAOBAO_PULL_MASTER.xlsx` copies is canonical (Items 35 and Missing 5, versus Items 40 and Missing 0). Whether `sassycloset.xlsx` is the hub. Live `Sassy_Closet_SoT.xlsx`. |
| 1089 proof folders and the truncated sentence for each | [snapshot-proofs.md](snapshot-proofs.md) | 103 folders INDEX lists as having no README or summary. |

INDEX's workbook table uses `Documents/Sassy_Closet/` and `Sassy_Closet/` (underscore). Its Gaps section uses `Documents/Sassy Closet/` and `Sassy Closet/` (space) for the two Taobao copies. `excel-kit/schema.py` `ONEDRIVE_SHOP_DIR` is `Documents/Sassy Closet`. Do not treat the underscore and the space as proven to be one directory.

Do not open OneDrive or a live Excel file to fill a gap. Do not paste supplier costs, customer names, or tokens. The snapshot's own redaction wins.

## What the repo already says about proof folders

- `docs/checkpoints/START-HERE.md` points a dry-run at `out/pending-draft-prs/100-checkpoint-start-here/proof/REVIEW-GUIDE.md`. That path is not in the checkout.
- `docs/overnight-tip-status-lag.md` explains why the tip script names an older piece: the summary file is missing or still being written. The diagnosis is in the doc. The proof trees are not.
- `scripts/archive_daily_inputs.py` says its copies are box-only, under gitignored `out/`.

## What the repo already says about OneDrive

The path Kit is supposed to sync is `Documents/Sassy Closet/Sassy_Closet_SoT.xlsx` (`excel-kit/schema.py` `ONEDRIVE_SOT`). Photos are `Documents/Sassy Closet/Photos/`, links only, never embedded (`PHOTO_RULE`). A committed price comparison lives in `docs/fixtures/onedrive-mirror/mirror-vs-live-2026-10-28.json` and is summarized in `docs/onedrive-mirror-drift.md`. That fixture is not the workbook.
