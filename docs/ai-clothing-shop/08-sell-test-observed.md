# Sell-test observed (2026-09-09)

First-party notes from [sassy-closet-shop.vercel.app](https://sassy-closet-shop.vercel.app). This is the shop the apply list targets. Do not treat intake (`sassy-closet.vercel.app`) as the same UI.

## Stack (from response headers + HTML)

- **Next.js on Vercel** (`x-powered-by: Next.js`, Turbopack chunks).
- Home: `x-nextjs-prerender: 1`, `x-vercel-cache: HIT` — **static/prerendered catalog**.
- `/admin`: `cache-control: private, no-cache, no-store` — **dynamic editor**.
- Fonts: **Be Vietnam Pro** + **Cormorant Garamond**.
- `robots: noindex, nofollow` — test shop, not a public SEO launch.
- Meta: “unique pieces. Facebook livestream. Zelle · Message on Messenger.”

## Routes that exist

| Path | Role |
| --- | --- |
| `/` | Featured collection + editorial tiles |
| `/c/ao` | Tops |
| `/c/set` | Sets |
| `/c/phu-kien` | Accessories |
| `/c/ao-khoac` | Jackets |
| `/c/toc` | Hair |
| `/m/{MA}` | Piece page (`A01` … `A02`) |
| `/admin` | Tiny merchandiser (not in main nav) |

`/m/A03` is **not** a product — Next error page. `/api/catalog`, `/api/export`, `/api/products` **404**. Catalog is rendered into HTML, not a public JSON API (yet). That is why kit needs an **export** — see [06-clone-to-official.md](06-clone-to-official.md).

## Allowlist (10). Never add to this list from an agent.

| mã | Kind (shop) | Status | Price | Cover |
| --- | --- | --- | --- | --- |
| A01 | TOP | Available | $25 | `/products/A01/cover.jpg` |
| S01 | SET | Available | $28 | `/products/S01/cover.jpg` |
| P01 | ACCESSORY | Available | $5 | `/products/P01/cover.jpg` |
| P02 | THERMOS | **Hold** | Inbox for price | `/products/P02/cover.jpg` |
| P03 | ACCESSORY | Available | $18 | `/products/P03/cover.jpg` |
| P04 | ACCESSORY | Available | $13 | `/products/P04/cover.jpg` |
| P05 | THERMOS | **Hold** | Inbox for price | `/products/P05/cover.jpg` |
| K01 | JACKET | Available | $37 | `/products/K01/cover.jpg` |
| H01 | HAIR | Available | $8 | `/products/H01/cover.jpg` |
| A02 | TOP | Available | $22 | `/products/A02/cover.jpg` |

Filter chips on `/`: All **10** · Tops **2** · Sets **1** · Accessories **5** · Jackets **1** · Hair **1**.

Editorial stills: `/editorial/hero.jpg`, `ao.jpg`, `set.jpg`, `phu-kien.jpg`, `ao-khoac.jpg`, `toc.jpg`.

## PDP copy (A01 / P02)

**A01** ([/m/A01](https://sassy-closet-shop.vercel.app/m/A01)):

- Breadcrumb `Tops / A01`
- `1 piece · Message to buy. No cart.`
- EN: “One unique top on hand. Message A01 for real photos and size.”
- VN: “Áo độc bản — một chiếc đang có.”
- CTA: **Message A01 →**
- Related: A02 on the same category rail

**P02** ([/m/P02](https://sassy-closet-shop.vercel.app/m/P02)):

- `Hold · Inbox for price. Message to buy — photo-check, no USD yet.`
- No dollar on the card.
- Related: P01, P03, P04, P05

## Message-first, today

Every “Message to buy” / footer “Message on Messenger →” currently points at the **Facebook Page profile**, not an `m.me/{page}?ref=A01` deep link:

`https://www.facebook.com/profile.php?id=61594312648057`

The *pattern* is message-first. The *implementation* is not yet mã-aware. Apply list item: keep human inbox, add `ref=<mã>` (site still must not Send).

## Admin (tiny ops)

[/admin](https://sassy-closet-shop.vercel.app/admin) text, 2026-09-09:

- “Test only · not in the main nav”
- “Open sell-test editor. Edit English titles and bilingual descriptions, prices, Hold / Inbox for price, and images.”
- “New items get the next unused mã for the letter you pick.”
- **Storage: Vercel Blob**
- Add item: “New items start on Hold. Type comes from the letter. Qty is always 1.”
- **Next mã tiles (DO NOT USE):** A03, Q01, V01, K02, G01, B01, P06, H02, J01, S02, O01, D01
- Colors: “Boxes only — no names on the swatches. Optional note is admin-only.”
- Images: URL or upload; “Add a color above to tag this image.”
- Per-row **Save {mã}** (explicit, not autosave — keep it that way and make failures loud)

The next-mã tiles are the live **mã-collision / invent-mã** trap. Kit law: those codes are not real until Stock/Boss assign them. Sell-test must not mint them.

## Motion (preserve)

From `/_next/static/immutable/chunks/34vl_zddoo4ws.css`:

- `@keyframes announce-fade` · class `.announce-fade` (4.2s)
- `@keyframes shimmer-slide` · class `.shimmer` (1.3s infinite)
- `@keyframes cta-flash` · `.cta-shine:hover:after` (0.7s)
- View transitions on `site-header`
- Reduced-motion: those animations set to `none !important`

## What is *not* here

- No cart, no checkout, no Stripe, no Square widget
- No password on `/admin`
- No public catalog JSON
- No intake tabs (Món mới / Tìm mã / Ask)
- No Kelly Ying *string* in HTML — the name is Boss’s for this paper/ink/gold + Cormorant system
