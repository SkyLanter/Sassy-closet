# Kit — site env names

Intake app lives in repo `sassy-closet/` (Vercel Root Directory). Excel kit stays here.

Document **names only**. Never paste secret values into git, PRs, or chat logs.

| Env | Used by |
| --- | --- |
| `MINIBOSS_ASK_WEBHOOK_URL` | `POST /api/ask` relays `{id, question}` |
| `MINIBOSS_ASK_WEBHOOK_KEY` | Bearer / `x-miniboss-ask-key` on that webhook POST |
| `ASK_REPLY_SECRET` | Gates `POST /api/ask/reply` |
| `INTAKE_DATASET_SYNC_WEBHOOK_URL` | Grok Bot routine `intake-dataset-sync-webhook` POST URL. Empty → no-op |
| `INTAKE_DATASET_SYNC_WEBHOOK_KEY` | Sender key as `Authorization: Bearer <key>` (optional `X-Automation-Key`). Both vars required or no-op |
| `SASSY_DATA_DIR` | Optional local data root |
| `BLOB_READ_WRITE_TOKEN` | Vercel Blob (auto). Durable mã JSON + photo bytes |
| `BLOB_STORE_ID` | Vercel Blob store id (auto when connected; OIDC on Vercel) |
| `BLOB_ACCESS` | Optional `private` (default) or `public`; must match the Blob store |

If `MINIBOSS_ASK_WEBHOOK_URL` or `MINIBOSS_ASK_WEBHOOK_KEY` is missing, Ask uses the on-site rules draft and shows **Mini Boss offline — local draft**.

Full contracts:

- `prompts/SAVED_CARD_AND_REAL_MINIBOSS_ASK_2026-09-07.md`
- `prompts/FIND_MA_CARD_2026-09-08.md` — Tìm mã code box + full info card. Keep find-by-photo / color detect. `GET /api/ma/{code}` is read-only staged + `on_hand` (empty = staged-only, never fake Square Free).
