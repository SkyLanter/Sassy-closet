# Kit

Bought / on-hand + tax books (Boss 2026-09-07 ~11:30 PM PT; San Jose tax 2026-09-18).

```bash
python3 excel-kit/build_square_finance.py --out-dir ./out
./excel-kit/kit.sh square    # same as: kit.sh finance | kit.sh books
python3 -m pytest excel-kit/tests/test_finance_schema_exports.py \
  excel-kit/tests/test_square_finance_builder.py \
  excel-kit/tests/test_finance_formulas.py -q
```

`kit.sh square` rebuilds `out/Square.xlsx` + `out/Finance.xlsx` and copies them into the shop folder only if it already exists. It does not delete other OneDrive files.

OneDrive land path:

```
Documents/Sassy Closet/Square.xlsx
Documents/Sassy Closet/Finance.xlsx
```

On_Hand starts empty. Staged site mãs are not bought. Finance starts empty — no invented sales. Square Free = SoT. No Square Save.

Shop jurisdiction: **San Jose, California**. Combined sales tax **10.000%** (CDTFA, effective Apr 1, 2026). Encoded as `SAN_JOSE_SALES_TAX_RATE` — do not treat 9.375% as current. Customer flat ship $ is TBD.

Contract: `prompts/SQUARE_AND_FINANCE_EXCEL_2026-09-07.md`.

## Site env names

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

Full contracts:

- `prompts/SAVED_CARD_AND_REAL_MINIBOSS_ASK_2026-09-07.md`
- `prompts/FIND_MA_CARD_2026-09-08.md` — Tìm mã code box + full info card. Keep find-by-photo / color detect. `GET /api/ma/{code}` is read-only staged + `on_hand` (empty = staged-only, never fake Square Free).
