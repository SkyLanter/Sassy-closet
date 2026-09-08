# Sassy Closet intake (Next.js)

GF intake at https://sassy-closet.vercel.app. Existing tabs only: **Món mới**, **Sửa theo mã**, **Tìm mã**, **Hỏi Mini Boss · Ask**.

This folder is the site source. The Excel kit stays at repo-root `excel-kit/`. Vercel Root Directory should be `sassy-closet`.

## Saved card

After Lưu (create / edit / rename) a **Saved · Đã lưu** sheet opens: big mã, kind + colors, **Copy mã**, **Copy link** (`/?ma=…` → Sửa), **Copy caption starter** (mã line 1), toast **Đã copy**, **Done** closes. No Post / Send / Square Save. No extra tab.

## Ask relay

| Method | Path | Notes |
| --- | --- | --- |
| POST | `/api/ask` | Stores `{id, question}` as `waiting` |
| POST | webhook | `MINIBOSS_ASK_WEBHOOK_URL` + `MINIBOSS_ASK_WEBHOOK_KEY` |
| POST | `/api/ask/reply` | `{id, answer}` gated by `ASK_REPLY_SECRET` |
| GET | `/api/ask/{id}` | UI poll until `ready` (~45s then local draft) |

If webhook envs are missing, the current rules fallback answers and the UI shows **Mini Boss offline — local draft**.

## Durable store (Production)

Vercel serverless disk (`/tmp`) is wiped on every Production redeploy. That is why export went to 0 rows and `/api/photos/…` 404’d.

**One Vercel Blob store holds both mã metadata and photo bytes** (Hobby-friendly: one click, no Redis/Postgres). UI URLs stay `/api/photos/{ma}/{file}`.

### Boss clicks (Vercel dashboard)

1. Open the **sassy-closet** project (Root Directory already `sassy-closet`).
2. **Storage** → **Create Database** → **Blob**.
3. Access: **Private** (must match the app default). Do not pick Public unless you also set `BLOB_ACCESS=public`.
4. Name: `sassy-closet` (any name is fine).
5. Environments: tick **Production**, **Preview**, and **Development**.
6. Create. On the store **Projects** tab, **Connect to Project** if it is not already connected.
7. Vercel injects env vars and usually redeploys. If not: **Deployments → Production → Redeploy**.

Hobby Blob (free): 1 GB storage, 10k simple reads / 2k writes per month. Boutique volume fits. If Blob suspends after the cap, wait for the monthly reset or move the project to Pro.

### Env names (never commit values)

Durable (auto after Blob connect; do not paste values into git):

- `BLOB_READ_WRITE_TOKEN` — long-lived token (also used off-Vercel / `vercel env pull`)
- `BLOB_STORE_ID` — set when the store is connected; used with Vercel OIDC on Production
- optional `BLOB_ACCESS` — `private` (default) or `public`; must match the store you created

Ask relay:

- `MINIBOSS_ASK_WEBHOOK_URL`
- `MINIBOSS_ASK_WEBHOOK_KEY`
- `ASK_REPLY_SECRET`
- optional `GROK_API_KEY` (unused unless you wire LLM later; rules draft is default)

Local only:

- optional `SASSY_DATA_DIR` — data root. Default local: `sassy-closet/data/` (gitignored). On Vercel *without* Blob: `/tmp/sassy-closet-data` (ephemeral).

Code treats the store as **durable** when `BLOB_READ_WRITE_TOKEN` or `BLOB_STORE_ID` is set. Check `GET /api/submissions` → `storage.durable` or `/admin` “Kho”.

### Verify after Blob is connected

1. Món mới → real photos + fields → **Lưu & lấy mã**. Note the mã.
2. `/admin` → Tải CSV should list that mã. Photo URL `/api/photos/{ma}/001.jpg` should 200.
3. Vercel → Deployments → Production → **Redeploy**.
4. Same mã still in export / Tìm mã / Sửa mã; photo still 200. If this fails, Blob is not connected to Production.

### Local / dev

```bash
cd sassy-closet
npm install
npm test
npm run typecheck
npm run dev
```

Without Blob envs, mãs live in `sassy-closet/data/` and survive local restarts. They are **not** Production.

To talk to the same Blob store from a laptop: `npx vercel env pull` in this folder (after Development is ticked on the store), then `npm run dev`.

### Restore if Production already wiped

Blob + this code cannot recover mãs that `/tmp` already deleted.

1. **Laptop `data/` leftover** — if `submissions.json` + `photos/` still exist, put them at `sassy-closet/data/` or `SASSY_DATA_DIR`, set Blob envs, hit any API once. If the Blob store is empty, a one-time migrate copies existing rows and photo bytes up. Never invent missing photos.
2. **Export CSV + re-upload** — CSV has fields only (`photo_link` is a folder path, not bytes). For each real row: Món mới (or `POST /api/submissions` multipart) with the same fields GF already had + the real photo files. Same APIs as normal Lưu. Do not invent $, qty, or photos.
3. `/admin` export going forward is the backup. Download after important saves.

Lightbox / 3-up photo row (PR #14) should land **after or with** this store change so Production merges do not keep writing into an empty ephemeral disk.

## Tìm mã · Find

Two boxes on the same tab (do not drop either):

1. **Code box** — type / paste mã (`Nhập mã · e.g. A01`), Enter or Tìm. Trim + upper. Valid mã opens a sheet with staged fields + on-hand block. Soft **Không tìm thấy mã** if missing. Done / ✕ closes.
2. **Photo / color detect box** — existing drop / choose a saved photo.

`GET /api/ma/{code}` is read-only `{ staged, on_hand, staged_only }`. Empty `on_hand` → **Staged only — not on Square On_Hand yet**. Never invent stock, $, storage, or mã.

Hard stops: no invent mã / qty / $, no Square Save, no Facebook Post/Send.
