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

Full contracts:

- `prompts/SAVED_CARD_AND_REAL_MINIBOSS_ASK_2026-09-07.md`
- `prompts/FIND_MA_CARD_2026-09-08.md` — Tìm mã code box + full info card. Keep find-by-photo / color detect. `GET /api/ma/{code}` is read-only staged + `on_hand` (empty = staged-only, never fake Square Free).
- `prompts/CATALOG_EXPORT_CLONE_OFFICIAL_2026-09-09.md` — OD `sassycloset.xlsx` → sell-site `catalog.v1` (allowlist A01 S01 P01 P02 P03 P04 P05 K01 H01 A02; P02/P05 Hold). Docs: `docs/SELL_CATALOG_CONTRACT.md`, `docs/CLONE_TO_OFFICIAL.md`. Scripts: `scripts/export_sell_catalog.py`, `scripts/validate_sell_catalog.py`. Sample: `samples/sell-catalog.v1.json`. Never invent mã. Intake untouched. Origin owns the live shop.
