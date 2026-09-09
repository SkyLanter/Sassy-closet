# Clone sell-test → official sell site

Boss runbook. **Kit / this repo does not own the live shop.** Mini Boss’s Origin agent owns [sassy-closet-shop](https://sassy-closet-shop.vercel.app) (Blob SoT, `/admin`). Do not push to Origin `main`. Do not fight that app. Do not point this clone at the **intake** project.

| Surface | URL | Role | Touch? |
| --- | --- | --- | --- |
| Intake | https://sassy-closet.vercel.app | GF upload · Tìm mã · Ask | **Never** (leave Production as-is) |
| Sell-test | https://sassy-closet-shop.vercel.app | Public tiles · Messenger CTA · `/admin` | Read / export only |
| Official | *new Vercel project* | Customer shop | **New project only** |

Shop law still applies after clone: no Square Save from agents, no Facebook Post/Send, no invented mã, Messenger-first, **Zelle** as a method word, **no personal name** on the site.

## 1. New Vercel project (never intake)

1. In Vercel, **Add New… → Project**.
2. Import the **sell-site** git remote (Origin / `sassy-closet-shop`), **not** `SkyLanter/Sassy-closet` and **not** Root Directory `sassy-closet`.
3. Name it something like `sassy-closet` **shop** / official — **do not reuse** the intake project (`sassy-closet` that already serves `sassy-closet.vercel.app`).
4. Framework: Next.js. Leave intake env vars (`MINIBOSS_ASK_WEBHOOK_*`, `ASK_REPLY_SECRET`, `GROK_API_KEY`) **off** this project unless Mini Boss explicitly wires Ask on the shop later.
5. Production hostname: pick a **new** `*.vercel.app` (or attach the real shop domain later). Do not overwrite intake DNS.

If someone “clones” by adding a domain to the intake app, stop. That is the wrong surface.

## 2. Blob store (SoT for the shop)

Sell-test already uses **Vercel Blob** as source of truth (see `/admin` → Storage). Official needs its **own** Blob (Hobby: one store per project is fine).

1. Official project → **Storage → Create Database → Blob**.
2. Access: **Private** unless Mini Boss set `BLOB_ACCESS=public` on the shop and you match it.
3. Connect **Production** (and Preview if you want).
4. Vercel injects names only — never paste token values into git, PRs, or Slack:

| Env name | Used by |
| --- | --- |
| `BLOB_READ_WRITE_TOKEN` | Read/write catalog + photo bytes |
| `BLOB_STORE_ID` | Store id (OIDC on Vercel) |
| `BLOB_ACCESS` | Optional `private` (default) or `public` — must match the store |

Do **not** point official at the intake Blob. Do **not** point official at sell-test Blob unless you are doing a one-time migrate (next section) and then disconnect.

Redeploy Production after the store is connected. Serverless `/tmp` is not durable.

## 3. Migrate / import catalog

### A. JSON import (kit → shop)

This repo exports **catalog.v1**:

```bash
python3 excel-kit/scripts/export_sell_catalog.py \
  -w "$HOME/OneDrive/Documents/Sassy Closet/sassycloset.xlsx" \
  --photos-dir "$HOME/OneDrive/Documents/Sassy Closet/Photos" \
  -o ./out/sell-catalog.v1.json
python3 excel-kit/scripts/validate_sell_catalog.py ./out/sell-catalog.v1.json
```

Contract: `SELL_CATALOG_CONTRACT.md`. Committed catalog (allowlist only): `out/sell-catalog.v1.json`.

On official `/admin`, use the shop’s **import catalog.v1** control when Origin lands it. Until that button exists, Mini Boss imports on Origin — **do not** fork shop code in this kit repo.

Allowlist only: `A01 S01 P01 P02 P03 P04 P05 K01 H01 A02`. Hold = `P02`, `P05` (`priceUsd` null). Everyone else uses the Boss USD table. `qty` is always 1.

Image `src` values in the JSON are OneDrive paths (`Documents/Sassy Closet/Photos/A01/001.jpg`), **not** public URLs. After import, upload those files (next step) or the tiles stay letter-placeholders.

### B. Blob-to-Blob copy (test → official)

If sell-test already has the 10 pieces + uploaded photos you want:

1. On sell-test `/admin`, confirm Storage: Vercel Blob and Catalog (10).
2. Ask Mini Boss (Origin) for the shop’s documented **export / migrate** path (Blob prefix copy or admin export). Kit does not have Blob credentials and must not ask for passwords.
3. Copy **only** allowlisted mãs. Do not copy intake submissions (`sassy-closet` Blob).
4. On official `/admin`, confirm the same 10 mãs, Hold on P02/P05, prices match the table, no extra codes.

Never invent missing photos. If a Photo folder has only `_placeholder.jpg`, skip it.

## 4. Photos

```
Documents/Sassy Closet/Photos/{MA}/001.jpg
```

Upload real `001` / `002` / `003` (`.jpg` / `.jpeg`) per mã. Skip `_placeholder.jpg`, `_probe.jpg`, `.keep`, `README.txt`.

Customer site: Messenger CTA, no cart. Admin may keep hex swatches; **customer-facing colors stay text** (`Kem`, `Xanh`). Do not invent hex just to fill boxes.

## 5. Messenger + copy

Sell-test already uses:

- Facebook Page: `https://www.facebook.com/profile.php?id=61594312648057`
- CTA: **Message on Messenger** / **Message {mã}**
- Announcement: **Facebook livestream · Zelle · Message on Messenger**

On official:

1. Confirm the Page URL with Boss (same Page is fine).
2. Keep Messenger-first. No cart. No “Buy now” checkout.
3. Keep the word **Zelle**. **Do not** put a personal name, handle, or phone on the site.
4. Do not connect a bot that Posts or Sends. Owner messages from the inbox.

Env names the shop may already document (values never in git): whatever Origin uses for the Page URL if it is not hardcoded. If it is hardcoded on sell-test, Mini Boss copies that constant onto official — still no secrets.

## 6. What not to copy from intake

| Intake | Official |
| --- | --- |
| Tabs Món mới / Sửa / Tìm mã / Ask | Customer catalog + `/admin` |
| `MINIBOSS_ASK_WEBHOOK_*` / `ASK_REPLY_SECRET` | Omit unless Boss wants Ask on the shop |
| `SASSY_DATA_DIR` / GF packets | Omit |
| Square language / Save | Still **no Save** from the site |
| AO001 SoT append scripts | Shop is A01-style allowlist |

## 7. Domain + go-live checklist

Print and tick. Soft-launch stays sell-test until this list is green.

- [ ] New Vercel project created (not intake, not a domain steal)
- [ ] Official Blob connected on Production; `/admin` says Vercel Blob
- [ ] catalog.v1 imported or Blob-migrated — **exactly** the 10 allowlist mãs
- [ ] `validate_sell_catalog.py` PASS on the JSON you imported
- [ ] Prices: A01 $25 · S01 $28 · P01 $5 · P03 $18 · P04 $13 · K01 $37 · H01 $8 · A02 $22
- [ ] Hold · Inbox for price: **P02**, **P05** (no $23 on P05)
- [ ] Photos uploaded for mãs that have real OD files; no placeholders
- [ ] Messenger CTA opens the real Page; Zelle word present; **no personal name**
- [ ] Customer colors read as text (not fake named swatches)
- [ ] Custom domain (optional) pointed at **official**, not intake
- [ ] Intake `sassy-closet.vercel.app` still the GF site
- [ ] Sell-test left up until Boss says sunset
- [ ] No Square Save, no FB Post/Send, no passwords in chat or git
- [ ] `#shop-decisions` yes before calling it official

## 8. After go-live

- Hub of record for rows remains `Documents/Sassy Closet/sassycloset.xlsx` + `Photos/{MA}/`.
- Re-export JSON when Boss adds a **new assigned** mã — do not mint `A03` here just because admin shows Next mã A03.
- Square Free remains on-hand SoT. Official Excel / this JSON are not a second warehouse.
- Bots draft only.

## Related

- `excel-kit/docs/SELL_CATALOG_CONTRACT.md`
- `excel-kit/prompts/CATALOG_EXPORT_CLONE_OFFICIAL_2026-09-09.md`
- `excel-kit/KIT.md` (env **names** only)
- Sell-test admin: https://sassy-closet-shop.vercel.app/admin
