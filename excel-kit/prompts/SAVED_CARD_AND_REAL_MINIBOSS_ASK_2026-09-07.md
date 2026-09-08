# Saved card + real Mini Boss Ask — Boss 2026-09-07 ~10:53 PM PT

Site job for https://sassy-closet.vercel.app. **Existing tabs only.** Do not add another top-level tab.

Shop law (unchanged): no Post / Send / Square Save. Never invent mã. Bots draft only. Facebook inbox is the store. Square Free = on-hand SoT.

## A) Saved card popup — NO new tab

After successful **Lưu** on **Món mới** / **Sửa theo mã** (including rename):

Modal / bottom sheet titled **Saved · Đã lưu**:

- Big mã
- kind + colors one-liner
- Buttons:
  - **Copy mã**
  - **Copy link** — deep link to Sửa with `?ma=…` (add that smallest query if missing)
  - **Copy caption starter** — mã on line 1
- Toast **Đã copy**
- **Done** closes the sheet

Do **not** add a Post / Send / Square Save control. Do not invent mã. App never posts.

## B) Real Mini Boss Ask relay

Upgrade **Hỏi Mini Boss · Ask** (same tab):

1. `POST /api/ask` → store pending `{id, question}` with status `waiting`
2. `POST` to env `MINIBOSS_ASK_WEBHOOK_URL` with key `MINIBOSS_ASK_WEBHOOK_KEY` (never commit secret values)
3. `POST /api/ask/reply` `{id, answer}` gated by `ASK_REPLY_SECRET`
4. `GET /api/ask/{id}` for UI poll until ready (~45s timeout)
5. If webhook envs are missing → current rules / LLM fallback + banner **Mini Boss offline — local draft**

Hard stops unchanged for answers: copy-only drafts. No Post, no Send, no Square Save, no invented mã.

## Env names (document only — never paste secret values)

| Name | Role |
| --- | --- |
| `MINIBOSS_ASK_WEBHOOK_URL` | Mini Boss inbound webhook |
| `MINIBOSS_ASK_WEBHOOK_KEY` | Shared key sent with the webhook POST |
| `ASK_REPLY_SECRET` | Gates `POST /api/ask/reply` |

Optional LLM for local draft when webhook envs are missing: `GROK_API_KEY` (rules fallback if unset).

## Success

- Deploy proof on the intake site
- Saved popup works after Lưu (create / edit / rename)
- Ask API paths exist
- Fallback + offline banner work without webhook envs
