# Official #32 APPLY — admin feature matrix (Boss override)

Quiet apply of [SkyLanter/Sassy-closet#32](https://github.com/SkyLanter/Sassy-closet/pull/32) `14-complete-admin-feature-matrix.md` **§17**. Kelly Ying paper / ink / gold / blush + Cormorant + Be Vietnam Pro stay. Excel / OneDrive / intake stay **read-only**.

Source matrix: [14-complete-admin-feature-matrix.md](./14-complete-admin-feature-matrix.md).

## Boss override (do not collapse)

Kit §17 Wave 0 **O1** and Wave 3 **O15** / §15.1 (`/m/A03` 404 · rename closed · refuse 11th mã) are **not** the law on this shop.

| Kit matrix | This shop |
| --- | --- |
| O1 kill Add A03 + Next-grid; Save ∉ allowlist → 400; `/m/A03` 404 | **Add A03+ MUST Save** and appear on the shop **Message to buy**. Next-grid **trap tiles** stay off (`Add mã` / letter picker / Assigned on Save). Official `AO001` still 400 |
| O15 rename closed; 400 unless already allowlisted | **Rename extras OK** with uniqueness. Hub ten cannot leave the allowlist. Photos keep URLs |
| O17 import hard-fail extras | Import **keeps** live extras (A03+). Missing hub ten / P05 `$23` / Official alphabet still fail |
| §15.1 Catalog (10) only | Hub ten stay Message-ready. After Add, counts include extras |

Keep: P02 / P05 Hold · Inbox for price (never `$23`). Qty 1. No cart. No Square Save. No FB Send. No passwords. No invented hex / mã / `source_link`.

## Used from the matrix (landed)

| §17 | Landed |
| --- | --- |
| O0 look lock | `--paper` / `--ink` / `--gold` `#b08968` / `--blush`; Cormorant + Be Vietnam; Page `61594312648057` |
| O2–O3 Blob get/put | Live catalog Blob / KV / local `data/live-catalog.json`. `allowOverwrite`, no random suffix on catalog JSON |
| O4 Save receipt | `{ ok, blobWritten, catalogSha, updatedAt, revalidated[] }` — toast only after a complete receipt |
| O5–O7 cache | `revalidatePath` `/` + `/c/[slug]` `"page"` + `/m/[ma]` `"page"`; two public warms; validate before put |
| O8 Hold ⇔ null $ | Server pairing. P02 / P05 never `$23` |
| O9–O10 markers | `data-save-contract="blob+revalidate"`; `/admin` force-dynamic no-store |
| O11 edit merge | Empty kit titles / photos do not wipe shop copy (`overlayProduct`) |
| O12 text colorIds | Shop text names. Admin hex boxes. `colorId` ∈ this mã or `null` |
| O13 hashed covers | Upload path is hashed; refuse in-place `cover.jpg`. Shop `<img>` uses `?v=` |
| O14 Hold copy | Inbox for price · Nhắn tin hỏi giá |
| O16 settings | Announcement + Page URL + Import / Export. No secrets |
| O17–O18 import/export | `catalog.v1` HTTP + settings buttons. Extras kept. No cost/source on customer export |
| O19 `GET /api/admin/catalog` | no-store JSON, hub-first then extras, `catalogSha` |
| O20 `POST /api/admin/revalidate` | GET is 405, never 404 |
| O21 Blob isolation | `{SITE_ID}/catalog.v1.json` — not intake |

## Enrich (hub ten)

`npm run catalog:hub` copies the seed ten into the live catalog and stamps recorded staff `source_link`s. Excel is never opened. Hub All has **no size column** — `sizes[]` stay empty. Customer tiles strip `sourceLink` (`shopSafeProduct`). K01 / H01 stay color-empty (do not invent `den`).

## Gate

`npm run smoke:matrix` plus `npm run prove:add-a03` and `npm run prove:enrich`. Existing admin / handoff / kit-apply / persist smokes stay.

Granola was unauthorized this run. Slack `#shop-decisions` is not an `/admin` field spec.
