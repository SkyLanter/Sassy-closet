# UNKNOWN / not in repo

Do not guess these. If a later commit or the knowledge snapshot adds the fact, replace the row and cite the new file.

| Topic | Why it is unknown |
| --- | --- |
| `Sassy_Closet_Order_Log.xlsx` and `Sassy_Closet_Wishlist.xlsx` (OneDrive drive root) | INDEX Gaps: zip CRC/inflate fails, a re-download was byte-identical, files not exported. Columns UNKNOWN. |
| Which `TAOBAO_PULL_MASTER.xlsx` is canonical | Two exports: Items 35 and Missing 5, versus Items 40 and Missing 0. INDEX says the choice is unknown. |
| Whether `sassycloset.xlsx` is the hub | INDEX assumes `Documents/Sassy Closet/sassycloset.xlsx` (Official, 62 rows) and says no note confirms it. |
| Column meanings in the exported workbooks | Snapshot meaning cells are `unknown (header only: …)`. Headers are in [snapshot-excel.md](snapshot-excel.md). |
| 103 proof folders with no README or summary | Named in [snapshot-proofs.md](snapshot-proofs.md). INDEX says what they prove is UNKNOWN. |
| Live OneDrive `Sassy_Closet_SoT.xlsx` rows, and columns that are not in `excel-kit/schema.py` | That workbook is not in the snapshot export and not in git. |
| Floor tracker (`Sassy_Closet_Data.xlsx` in open PR #7's title) | No export file uses that name. PR #7 is not merged. |
| `Sassy_Closet_Official_desktop.xlsx` and `Sassy_Closet_Wishlist_desktop.xlsx` | Named in `excel-kit/schema.py`. Not in the export. The corrupt drive-root Wishlist file is a different name. |
| Cell values inside the exported workbooks | Example rows were not copied. |
| Who runs daily shop check, midnight QC, or the Muse pack, and on what clock | No `schedule` in `.github/workflows`. |
| Grok Bot poll backup timing | `sassy-closet/README.md` says the poll exists. The bot config is not in the repo. |
| Who saves the Facebook/Instagram caption export the linters read | `scripts/meta_inventory.py` takes a file. It does not download one. |
| Whether Luxubu is the person who publishes or edits the Facebook/Instagram posts | Dual-confirm and a local status file are in repo. The README says the owner posts. It does not identify the owner as Luxubu. |
| Slack `#shop-decisions` message text | Named as the yes/no channel. The messages are not in git. |
| Routine prompts that live only on a box | `excel-kit/PROMPTS.md` and `excel-kit/prompts/` are in git. Any prompt file that is not under those paths is unknown. |
| Customer names, live cost cells, Square tokens | Forbidden in git (`README.md`). Absence is intentional. |
| A password on intake | Main has no login gate. Drafts #188 and #189 are not merged. |

`excel-kit/prompts/` is in the repo. Those files are sources. A prompt that only exists in a chat or on OneDrive is not.
