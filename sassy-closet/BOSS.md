# Boss one-pager

- Tabs: Món mới · Sửa theo mã · Tìm mã · Hỏi Mini Boss. No fifth tab.
- Lưu opens **Saved · Đã lưu**: copy mã / `?ma=` link / caption starter. Done closes. App never Posts.
- Ask relays to Mini Boss when `MINIBOSS_ASK_WEBHOOK_URL` + `MINIBOSS_ASK_WEBHOOK_KEY` are set. Reply via `ASK_REPLY_SECRET`. Offline → local draft banner.
- Dataset sync (immediate path): after merge, Boss pastes URL + sender key into **Vercel intake only**, then Redeploy intake. Poll backup already exists on Grok Bot — Mini Boss does not need to be online. Unset env → save still works. Never paste the key into chat.
  1. Grok Bot desktop → routine `intake-dataset-sync-webhook` → copy **Webhook URL** + **sender key** (often `crsr_…`).
  2. Vercel → project for https://sassy-closet.vercel.app (Root Directory `sassy-closet`) → Settings → Environment Variables.
  3. Add `INTAKE_DATASET_SYNC_WEBHOOK_URL` and `INTAKE_DATASET_SYNC_WEBHOOK_KEY` (Production + Preview as needed). Header the app sends: `Authorization: Bearer <key>`.
  4. **Redeploy intake only.** Do not touch sell-test (`sassy-closet-shop`).
  5. Smoke: one Món mới Lưu + one Sửa theo mã Lưu → routine run history shows create + update. Poll backup stays ON if a webhook is missed.
- Tìm mã: code box (sheet with staged + on-hand) **and** existing photo / color detect. Both stay. Card thumbs: ≤3 in one row; tap opens lightbox.
- Missing on-hand = **Staged only — not on Square On_Hand yet**. Never invent qty / $ / storage.
- Square Free = on-hand SoT. Never invent mã. Never Square Save from the site.
- Production persistence: Vercel → Storage → Create **Blob** → **Private** → connect Production. Without this, redeploy wipes mã + photos. Verify: Lưu → Redeploy → mã still in export. See `README.md` Durable store.
