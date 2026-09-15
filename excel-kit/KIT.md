# Kit — site env names

Intake app lives in repo `sassy-closet/` (Vercel Root Directory). Excel kit stays here.

Document **names only**. Never paste secret values into git, PRs, or chat logs.

| Env | Used by |
| --- | --- |
| `MINIBOSS_ASK_WEBHOOK_URL` | `POST /api/ask` relays `{id, question}` |
| `MINIBOSS_ASK_WEBHOOK_KEY` | Bearer / `x-miniboss-ask-key` on that webhook POST |
| `ASK_REPLY_SECRET` | Gates `POST /api/ask/reply` |
| `SASSY_DATA_DIR` | Optional local data root |
| `BLOB_READ_WRITE_TOKEN` | Vercel Blob (auto). Durable mã JSON + photo bytes |
| `BLOB_STORE_ID` | Vercel Blob store id (auto when connected; OIDC on Vercel) |
| `BLOB_ACCESS` | Optional `private` (default) or `public`; must match the Blob store |

If `MINIBOSS_ASK_WEBHOOK_URL` or `MINIBOSS_ASK_WEBHOOK_KEY` is missing, Ask uses the on-site rules draft and shows **Mini Boss offline — local draft**.

## Square.xlsx + Finance.xlsx

Bought / on-hand + tax books (Boss 2026-09-07 / 2026-09-15). Land on OneDrive `Documents/Sassy Closet/`.

- **Square.xlsx** = bought / on-hand team tracker. **Not** the website staged list. Staged site mãs are NOT bought. On_Hand starts empty.
- **Finance.xlsx** = tax-ready Sales / Fees / Payouts_Transfers / Expenses / Tax_Summary. Empty templates — no invented sales.
- **sassycloset.xlsx** = website staged hub. Do not overwrite.
- Square Free Dashboard remains inventory SoT. Excel is the team tracker.
- Sold item → Square `qty_on_hand` 0 + one Finance Sales row (`square_xlsx_ma`).
- Zelle display customers see: Thang Tien Huynh (note only — never store bank passwords).
- Cute Excel is retired.

```bash
python3 excel-kit/build_square_finance.py --out-dir ./out
unzip -t out/Square.xlsx
unzip -t out/Finance.xlsx
```

Contract: `prompts/SQUARE_AND_FINANCE_EXCEL_2026-09-07.md`.

Full contracts:

- `prompts/SAVED_CARD_AND_REAL_MINIBOSS_ASK_2026-09-07.md`
- `prompts/FIND_MA_CARD_2026-09-08.md` — Tìm mã code box + full info card. Keep find-by-photo / color detect. `GET /api/ma/{code}` is read-only staged + `on_hand` (empty = staged-only, never fake Square Free).
