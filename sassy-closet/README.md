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

## Env names (never commit values)

- `MINIBOSS_ASK_WEBHOOK_URL`
- `MINIBOSS_ASK_WEBHOOK_KEY`
- `ASK_REPLY_SECRET`
- optional `GROK_API_KEY` (unused unless you wire LLM later; rules draft is default)
- optional `SASSY_DATA_DIR` (local data root; Vercel uses `/tmp/sassy-closet-data`)

## Run

```bash
cd sassy-closet
npm install
npm test
npm run typecheck
npm run dev
```

## Tìm mã · Find

Two boxes on the same tab (do not drop either):

1. **Code box** — type / paste mã (`Nhập mã · e.g. A01`), Enter or Tìm. Trim + upper. Valid mã opens a sheet with staged fields + on-hand block. Soft **Không tìm thấy mã** if missing. Done / ✕ closes.
2. **Photo / color detect box** — existing drop / choose a saved photo.

`GET /api/ma/{code}` is read-only `{ staged, on_hand, staged_only }`. Empty `on_hand` → **Staged only — not on Square On_Hand yet**. Never invent stock, $, storage, or mã.

Hard stops: no invent mã / qty / $, no Square Save, no Facebook Post/Send.
