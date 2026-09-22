# Sassy Closet — sell-only shop

Category-first boutique catalog. Live: [https://sassy-closet-shop.vercel.app](https://sassy-closet-shop.vercel.app)

This is **not** the GF intake tool. Do not deploy over [https://sassy-closet.vercel.app](https://sassy-closet.vercel.app).

## Source of truth (GitHub)

Boss (2026-09-21): this folder in [SkyLanter/Sassy-closet](https://github.com/SkyLanter/Sassy-closet) is the only main for the sell shop. Origin temp `tiensidequests/tmp-87ea3acf7683fefe` is **deprecated for new commits**. Do not delete that Origin project from this repo.

**Mini Boss / Boss must reconnect Vercel before Origin is deleted:**

1. Point the existing Vercel project at this GitHub repo.
2. Set **Root Directory** to `sassy-closet-shop`.
3. Leave the live URL at [https://sassy-closet-shop.vercel.app](https://sassy-closet-shop.vercel.app).

Product photos stay on Vercel Blob / CDN. Git keeps the existing `/products/...` path references and does not store those image binaries. This pull request does not deploy production.

Customer chrome is English. Product titles and metadata stay English. Product descriptions may include a short Vietnamese flavor line. This shop sells **mainly Taobao dropship**: customer messages → Boss sources/orders. Messenger first — Zelle as a method word only. No cart, no Square pretends, no invented ship $. Customers never see **Available / Hold / on hand / Status:** — those words stay in admin. Desktop Message stays on `https://m.me/61594312648057` in the **same tab**. iPhone/Android Message is a native `<a href="fb-messenger://user-thread/61594312648057">` so the Messenger **app** opens the Page thread — no `onClick`, no delayed fallback to `m.me` / messenger.com / Facebook profile (that timer is what forced Safari before). A separate **Open on web** text link still points at `https://m.me/61594312648057` for shoppers without the app. Do not `dns-prefetch` or `preconnect` `https://m.me`. Do not send the primary tap to facebook.com/messages, facebook.com/profile, or messenger.com web.

The home hero is the **full D02 front+back diptych** (`/editorial/hero.jpg`, 3890×3890) shown as **two equal columns** (`hero-front.jpg` | `hero-back.jpg`) with a paper gap between them. Each panel is `object-contain` on warm paper `#faf7f4` so the full dress (head to shoes) stays in frame — editorial only, not a D02 product. Do not ship a front-only hero. Do not invent a D02 SKU. The homepage does not render the under-hero collection tile rail; categories stay in the header, Looks filters, `/c/{slug}`, and admin. Nav lists every letter (Tops, Bottoms, Skirts, Dresses, Jackets, Shoes/High heels 35–41, Bags, Accessories, Hair accessories, Jewelry, Sets, Other). Empty category pages are allowed. Looks with no own photos stay in admin, not the shop.

## Local run

The top-right header keeps a compact **search** on every shop page (`/`, `/m/{ma}`, `/c/{slug}`, how-to-buy, meetup-ship) next to Messenger. Type a mã or look name. An exact catalog mã (H01, A01, …) opens `/m/{ma}`. Anything else filters home Looks (`/?q=`). Search does not live only on the home Looks section, and tapping a mã does not remove it. Category pages (`/c/{slug}`) do **not** get a second search box.

Looks page-open (and color-chip / Looks-tab change) plays a **one-shot soft gold sheen** — A06-like, left→right, then still. No heart curtain. No watery ribbon. Reduce Motion skips it.

```bash
npm install
npm run dev
```

```bash
npm run build
npm start
```

Never commit secrets. Copy `.env.example` to `.env.local` for Blob/KV, or set the same names on Vercel.

## Catalog

Default shop order (home Looks and `/c/{slug}`) is **Popular**: Facebook views high → low, engagement as the tie-break. That ranking is the first paint / hard refresh / new session default — shoppers do not have to pick it. A small **Popular** chip (with **Mã** as the other option) sits on Looks; Popular stays selected until someone taps Mã, and a reload returns to Popular.

Source: Facebook Professional Dashboard → Content Library for Page `61594312648057` (90-day). Authoritative table: `data/ma-default-sort.csv` (aggregated views DESC, engagement DESC). `data/fb-ma-rank.json` is that table stamped onto catalog mãs as `fbRank` / `fbViews` / `fbEngagement` / `fbPosts`. `data/ma-engagement-rank.csv` is the raw per-post export for reference only.

Mãs in the CSV keep those fields on parse (CSV wins over any stale stored values). Mãs not in the CSV (no FB post yet, e.g. P05 / A09 / A12) have no rank and sort **after** every ranked look, then by **mã** (letter order A→O, then number: A09 before A12 before P05). Do not invent a missing mã to fill a hole. Admin `/admin` stays hub-ten-first, then extras.

`npm run catalog:fb-rank` rebuilds `data/fb-ma-rank.json` from the CSV. `npm run smoke:fb-rank` checks CSV ↔ JSON, hub Looks order, and that Popular is the default state.

`npm run smoke:search` checks header search on every shop page: exact catalog mã → `/m/{ma}`, name queries filter Looks, unknown mãs are not invented.

`data/products.json` is the **seed document** (`catalog.v1`). Shape is stable:

- `schema` — always `catalog.v1`
- `siteId` — which store this file belongs to (`SITE_ID`)

- `products[]` — each item has `ma`, bilingual titles/descriptions, `qty: 1`, `status` (`available` | `hold` | `sold`)
- `colors[]` — `{ id, hex, name, note }` (empty if the piece is one look). Admin hex; shop is **text-only** names
- `images[]` — `{ src, colorId, order }` where `colorId` is `null` or a color `id` already on **this** mã (hub slugs `kem` / `xanh` / `cham-bi` on the ten). Shop gallery = tagged ∪ untagged for this mã. PDP gallery is one native snap reel: color chips **scroll** to tagged (or shared) slides instead of remounting the same JPEG. The center frame is full-bleed (no neighbor peek gutters on the product). Frosted **liquid glass** is boutique chrome (header, chips, captions, sticky Message bar, gallery arrows/dots, lightbox sheet) sitting over photos: thin glass edge + backdrop blur, not a milky paper wash and not an iOS lock-screen keypad. Regular bars use 48% frost + ink halo; Clear captions stay a darker 32% frost. `backdrop-filter` never sits on the garment JPEG. Never borrow another mã’s `/products/{MA}/` files (A02 never shows A01 Kem/Xanh).
- `sizes[]` — Asia letters only (`2XS XS S M L XL 2XL`). Empty if unknown — never invent, never US. The PDP paints **Cỡ / Size** chips from this array only (hide the row when empty; H01 hair stays empty). JSON-LD still does not list sizes.
- `fitCm` — stored `{ bustChestCm, waistCm, lengthCm }` or nulls. Never guessed from a letter
- `fulfillment` — `dropship` (default) or `on_hand` (only after Boss received the piece)
- `sourceLink` — Taobao URL (`e.tb.cn`) if Boss pasted one; otherwise `null`. Never invented
- `fbRank` / `fbViews` / `fbEngagement` / `fbPosts` — optional. Present only when the mã is in `data/ma-default-sort.csv`. Overlay on parse; not shown on customer tiles.
- `settings` — announcement lines + Messenger / Facebook Page URL

Writes always emit that document. A legacy array (string `images`, missing `colors`) still parses.

The shop reads a **live** catalog from Vercel Blob (preferred), KV, or — on a local machine only — `data/live-catalog.json`. Seed is the fallback when nothing live exists. Every write is read back before the save is treated as success. Blob key is `{SITE_ID}/catalog.v1.json` — no shop hostname in the data layer.

`npm run catalog:hub` **copies the hub ten** from `data/products.json` into that sell catalog (Blob on Vercel, local file here) and stamps the recorded staff `source_link`s. It keeps live extras (A03+). It never writes Excel, OneDrive, or intake. Customer tiles strip `sourceLink`. Hub All sheet has **no size column** — sizes stay empty (Message for Asia size). P05 Excel $23 is ignored; P02/P05 stay Hold / Inbox. Square / on-hand may be 0.

Official clone (new Vercel + Blob, same code): [docs/OFFICIAL_CLONE.md](./docs/OFFICIAL_CLONE.md). Catalog handoff: [OFFICIAL_HANDOFF.md](./OFFICIAL_HANDOFF.md).

`npm run catalog:backup` dumps live catalog.v1 JSON to `data/backups/` (gitignored). The file is validated as catalog.v1 before write. Admin **Export catalog.v1** refuses HTML or kit-xlsx payloads.

`npm run smoke:persist` proves: canonical seed JSON, in-memory Blob put/list/fetch round-trip, and local file write→read (this environment has no Blob token). On Vercel, set `BLOB_READ_WRITE_TOKEN` so Add/Save use Blob.

| Mã | USD | Category |
| --- | --- | --- |
| A01 | 25 | Tops |
| S01 | 28 | Sets |
| P01 | 5 | Accessories |
| P02 | — (Hold · Inbox for price) | Accessories |
| P03 | 18 | Accessories |
| P04 | 13 | Accessories |
| P05 | — (Hold · Inbox for price) | Accessories |
| K01 | 37 | Jackets |
| H01 | 8 | Hair accessories |
| A02 | 22 | Tops |

The hub ten stay on the catalog. **Add next mãs (A03+)** Saves to the live catalog (Blob on Vercel, `data/live-catalog.json` locally) and the piece appears on the shop. Official alphabet (`AO001`) is still rejected. Qty is always 1. Hold ⇔ `priceUsd` null (P02/P05 never $23). Excel / OneDrive / intake are read-only — copy colors, empty sizes, staff `source_link`, and Message-first dropship copy into this sell catalog only.

## Test admin (`/admin`)

Open sell-ops console. No password, no login. Not linked in the main nav. On the shop: long-press the logo, or tap the tiny gold dot (bottom-right) → **Open admin**.

- **Catalog** (`/admin`) — thumb, mã, title, status, price, colors, image count, search, type/status filters, bulk Hold, Edit + Preview PDP. Marker `data-save-contract="blob+revalidate"`
- **Add** (`/admin/new`) — pick a letter (`A · Tops`, not `→ Q01` tiles). Save assigns the next unused mã via `POST /api/admin/add` (JSON receipt). That path does **not** use a Server Action, so the page does not die behind React #441 after Blob write. Success toast + footer receipt, then soft-navigate to Edit. Visible error if write fails — never the minified React overlay.
- **Edit item** (`/admin/edit/A01`) — identity, status/price, colors+photos, copy, change mã. Preview PDP. Sticky Save writes on click (the bar is the confirm — no native dialog). Success is a receipt (`ok`, `blobWritten`, `catalogSha`, `revalidated`) or a visible error. Never silent.
- **Change mã** — JSON `POST /api/admin/rename`. Hub ten stay. Taken / Official codes refused. Photos keep their URLs so thumbs do not 404
- **Colors** — Boxes only — no names on the swatches (admin hex). Shop shows **text-only** color names. Link / unlink / reorder gallery slides per color (`image.colorId`); Save still Blob + revalidate
- **Images** — hashed Blob path (never in-place `cover.jpg`). Shop `<img>` uses `/products/{MA}/cover.jpg?v=`
- **Sold / Gone** — hides the piece from the shop without a checkout flow
- **Site settings** (`/admin/settings`) — announcement lines, Messenger / Facebook Page URL (no personal name), **Export / Import catalog.v1** (import keeps extras; hub ten must stay)

`GET /api/admin/catalog` — private no-store JSON (`products` hub-first then extras, `catalogSha`, `updatedAt`).  
`POST /api/admin/save` — `{ ma, titleEn }` receipt after write + revalidate + two warms.  
`POST /api/admin/add` — `{ letter: "A" }` assigns the next unused mã (A03+), writes Blob/local, returns the same receipt. GET is 405.  
`POST /api/admin/rename` · `POST /api/admin/remove` · `POST /api/admin/settings` · `POST /api/admin/hold` — same JSON receipt pattern (no Server Action / RSC #441).  
`POST /api/admin/revalidate` — marks `/`, `/c/[slug]` `page`, `/m/[ma]` `page`. GET is 405, never 404.

P02 and P05 stay Hold / Inbox for price (no invented $). All ten are **Message to buy** (dropship OK; Square on-hand may be 0). Available hub rows keep Boss USD.

### Env vars for Mini Boss (Vercel project `sassy-closet-shop`)

Set on **Production** (and Preview). Do not put values in git. There is **no** `ADMIN_PASSWORD`.

| Name | Required | What it does |
| --- | --- | --- |
| `SITE_ID` / `NEXT_PUBLIC_SITE_ID` | Store name | Blob/KV prefix. Default `sassy-closet-shop` |
| `NEXT_PUBLIC_SITE_MODE` | `test` or `official` | Labels admin; official uses a different default id |
| `NEXT_PUBLIC_SHOP_URL` | Official public origin | Canonical shop URL. Empty locally — not hardcoded |
| `NEXT_PUBLIC_MESSENGER_URL` | Messenger Page URL | Overrides the default Page link |
| `BLOB_READ_WRITE_TOKEN` | Preferred store | Live catalog JSON + image uploads (Vercel Blob) |
| `KV_REST_API_URL` | Alternative store | Catalog JSON only, if Blob is unset |
| `KV_REST_API_TOKEN` | With the URL | Catalog JSON only, if Blob is unset |

On Vercel without Blob/KV, `/admin` still opens; Add/Save show an error toast until a store is attached. Blob wins when both are set.

Locally (not on Vercel), Add/Save persist to `data/live-catalog.json` and uploads go to `public/uploads/` so you can sell-test without tokens. That file is gitignored. Do not write the catalog to the serverless filesystem on Vercel.

## Buy path

- Desktop Message opens a **plain** `m.me/{Page id}` chat. iPhone/Android Message is `fb-messenger://user-thread/{Page id}` (no timer fallback). No `?text=` prefill. Copy mã on the PDP if you want it in chat. **Open on web** is a separate m.me link for shoppers without the app.
- Buy path: **Message → Zelle → Taobao order**. No cart
- Looks without a printed USD: **Inbox for price** — admin still stores these as Hold internally (P02 / P05)
Customer tiles show **name, price, description, color, photos** and **Message**. The shopper payload is a `ShopLook` (no `status` / Hold / Available / sourceLink in HTML). Inbox-price looks print **Inbox for price** (no USD). Admin still stores Hold internally (P02 / P05).
- Hub covers are **real intake photos** under `public/products/{MA}/` (`cover.jpg` plus `photo-N.jpg`). Color chips roll to tagged slides (A01 Kem = lavender cardigan, Xanh = yellow). A cleaned studio hero of A01 is review-only until Boss says yes — it is not the live cover
- Gallery is a native CSS snap roll in the named 3/4 frame: **full-bleed** when a neighbor JPEG exists (no 78% side peeks eating the product on phone), full-bleed when n=1. Paper-edge mask stays off the current photo so cups/garments are not faded. Controls sit **on** the photo as boutique liquid glass: rounded-2xl arrows at the edges and a capsule of dots that scrolls when a look has many shots — see-through frost, not a keypad and not a dock below the hero. Regular chrome (header, sticky Message) is 48% white frost with an ink halo so type reads over photos; Clear captions over media stay a 32% dark frost. Reduced motion keeps UA snap, kills card springs, and scrolls instantly. Color chips sit **just below the pictures** (under thumbs): text names (Kem / Xanh) in a gold outlined glass chip, selected vs unselected obvious. Color tap rolls this mã’s tagged slides. A color with **no shots on this mã** frosts over the other finish — it does not steal that JPEG. Thumbs list every shot; center tap opens the ink/gold lightbox.
- Featured **Looks** heading, then tabs that **crossfade** the grid (~280ms opacity + a small ease slide). No watery ribbon, goo, heart curtain, or clip-path pour. Page-open and color-chip play a one-shot soft gold sheen, then still. Gold hairline still stretches with a restrained spring. Message CTAs keep a 1–1.5px gold/ink metal rim (still, no hover spin). Header border is a static gold `color-mix` film, not glass. Counts say **looks**, not pieces
- Ship bar: mã + CTA + optional **address + mã** draft. After Zelle we order Taobao; meetup or US ship quoted in chat — no flat rate
- Copy: **Message on Messenger**. Dest and pay method stay in chat — never invented on the lookbook
- How to buy / Meetup & ship routes redirect home. Announcement is the shop name only
- Share cards: unique title/description/OG per mã (`A01 · Puppy cardigan`). Canonical `/m/A01` (lowercase 308s)
- Test site stays **noindex**. `robots.txt` + `sitemap.xml` exist; do not flip index until Boss says
- No card checkout. No Square inventory. Never invent a ship $ or a Taobao link

## How to test admin

1. Open `/admin` (or gold-dot → Open admin). Test only · not in the main nav.
2. **Add mã** → letter A → title → Save. Receipt toast shows `Saved A04 · sha …`. Footer is not stuck on unsaved. No React #441. Edit opens with the new mã. **A03+** appears on `/` and `/m/{ma}`.
3. Edit **A01** → title nudge → Save. Confirm `/m/A01` (refresh twice if needed) and `GET /api/admin/catalog` `catalogSha` changed. Restore the title.
4. `POST /api/admin/save` with `{ "ma": "A03" }` works after Add (400 only if A03 is not in the catalog yet). P05 never $23. `AO001` stays rejected.

`npm run smoke:admin` checks Add A03 / Hold pairing / leftover Remove / missing-hub import / Official `AO001` refuse without the browser.

`npm run smoke:persist` checks catalog JSON shape and Blob/local read-write round-trips.

`npm run smoke:contract` checks catalog.v1, SITE_ID Blob prefix, Boss prices, and that the data layer has no shop hostname.

`GET /api/health` reports Blob/schema/`SITE_ID` and whether the 10 known mãs are present. `npm run smoke:health` hits that route.

`npm run smoke:unit` checks rename uniqueness, color merge (retag photos), catalog.v1 overlay merge, image reorder, and Hold JSON-LD (no invented USD).

`npm run smoke:dropship` checks Taobao `sourceLink` keep/reject, Official Message-first seed copy (no “on hand” / “đang có” / Hold / Available), ship-draft (mã, no $), and Nhắn tin hỏi giá copy.

`npm run smoke:pdp` checks text-only color law (tagged ∪ untagged, empty —), Asia sizes + stored cm, and Message-first copy with no Hold / Available.

`npm run smoke:media` checks hub slugs on the ten (`kem` / `cham-bi`), `colorId` null-or-on-this-mã, image `order`, K01/H01 unbound, and P02/P05 Hold.

`npm run smoke:handoff` checks kit catalog.v1 import (word types, empty titles, OneDrive paths dropped, live A03 kept) and handoff export `allowlist`.

`npm run smoke:excel-ro` fails if the shop writes Official Excel, OneDrive, or intake (`store.json`). Copy into this sell catalog only.

`npm run smoke:safety` fails if shop/public components mention Square, Facebook Send, `ADMIN_PASSWORD`, the locked personal name, or customer-facing Hold / Available / on hand / Status.

`npm run smoke:seo` checks unique per-mã OG copy, test `noindex`, `/m/a01` → `/m/A01`, short announce (`Facebook livestream` / `Inbox · Zelle · US`), Message→Zelle→Taobao how-to-buy, dest-after-confirm, and no invented ship $.

`npm run smoke:bugcheck` ticks Official #27 blockers: Change mã uniqueness, Save→refresh paths, text-only colors, P02/P05 never `$23`.

`npm run smoke:kit-apply` ticks Official #29 + #21: no Add A03 / Add Q01 tiles, Save confirm (mã + status + $ or Hold), Blob + revalidate receipt, plain `m.me` Message CTA (no `?text=`), 4.5 MB upload cap, hub-ten seed.

`npm run smoke:motion` ticks Official #31 plus LEARN 13 + 20/37 Featured springs (quiet ~280ms opacity/slide, `replay={false}`) + LEARN 16 gallery snap + 18/34 liquid chrome: gold hairline layoutId (no goo/overshoot), APG Featured tabs, peek roll, Message CTA `.ky-chrome-rim` (no spin), header `.ky-header-film`, zero displacement on covers. Watery ribbon / heart curtain / gallery-water sheen / clip-path pour must stay gone. The A06-like content-wave sheen (page-open + chip) must stay.

`npm run smoke:matrix` ticks Official #32 §17 **with Boss override**: Blob receipt + `revalidatePath`, hashed covers, text `colorId`s, import/export, settings, `GET /api/admin/catalog`, edit merge, per-color photos. Add A03+ Saves and shows. Rename extras OK. Kit O1/O15 (`/m/A03` 404 · rename closed) are **not** applied. See [32-admin-matrix-apply.md](./docs/ai-clothing-shop/32-admin-matrix-apply.md).

`npm run prove:add-a03` writes A03 to the live catalog (local file here, Blob on Vercel). `npm run prove:add-a03-blob` proves the same Add on an in-memory `{SITE_ID}/catalog.v1.json` port: hub ten stay Message to buy, A03 is shop-visible, no invented Q01 / staff link.

`npm run prove:enrich` checks the hub ten (recorded colors, empty sizes, staff links, P02/P05 Hold) and that A03 is shop-visible.

Craft notes (learn → apply): [docs/ai-clothing-shop/](./docs/ai-clothing-shop/).

`npm run smoke:link` POSTs `/api/admin/save` on A01 (title nudge + restore), checks the receipt, two PDP warms, catalog sha, and revalidate. `/m/A03` is 200 after Add, 404 until then.

Origin gate (look + silent-Save): `python3 docs/ai-clothing-shop/qa/qa_selltest_origin_gate.py` — [§18 apply note](./docs/ai-clothing-shop/11-origin-f18-apply.md).

## Vercel

The live host stays [https://sassy-closet-shop.vercel.app](https://sassy-closet-shop.vercel.app) (project `sassy-closet-shop`). Do not attach or deploy over intake [https://sassy-closet.vercel.app](https://sassy-closet.vercel.app). Official is a **second** project — [CLONE_TO_OFFICIAL.md](./CLONE_TO_OFFICIAL.md).

GitHub `SkyLanter/Sassy-closet` is the source of truth. When reconnecting, set Vercel **Root Directory** to `sassy-closet-shop`. Origin temp `tiensidequests/tmp-87ea3acf7683fefe` is deprecated for new commits; leave it in place until Mini Boss / Boss finishes that reconnect. Do not production-deploy from this migration. Never link this app to the intake project.
