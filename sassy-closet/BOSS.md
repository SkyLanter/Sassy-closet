# Boss one-pager

- Tabs: Món mới · Sửa theo mã · Tìm mã · Hỏi Mini Boss. No fifth tab.
- Lưu opens **Saved · Đã lưu**: copy mã / `?ma=` link / caption starter. Done closes. App never Posts.
- Ask relays to Mini Boss when `MINIBOSS_ASK_WEBHOOK_URL` + `MINIBOSS_ASK_WEBHOOK_KEY` are set. Reply via `ASK_REPLY_SECRET`. Offline → local draft banner.
- Dataset sync: paste `INTAKE_DATASET_SYNC_WEBHOOK_URL` + `INTAKE_DATASET_SYNC_WEBHOOK_KEY` (Bearer sender key from Grok Bot routine `intake-dataset-sync-webhook`) into Vercel **intake** env, then Redeploy intake only. Unset → save still works. Never paste the key into chat.
- Tìm mã: code box (sheet with staged + on-hand) **and** existing photo / color detect. Both stay. Card thumbs: ≤3 in one row; tap opens lightbox.
- Missing on-hand = **Staged only — not on Square On_Hand yet**. Never invent qty / $ / storage.
- Square Free = on-hand SoT. Never invent mã. Never Square Save from the site.
- Production persistence: Vercel → Storage → Create **Blob** → **Private** → connect Production. Without this, redeploy wipes mã + photos. Verify: Lưu → Redeploy → mã still in export. See `README.md` Durable store.
