# 02 — Fashion PDP + color / size variant UX

**Learn track:** Ultra burn (research + as-built map + apply notes).  
**Shop:** Sassy Closet — small clothing boutique, Facebook inbox as the store, Square Free as on-hand truth.  
**Audience:** Mini Boss / Stock / a later sell-test implementer.  
**Date researched:** 2026-09-09.  
**This file does not assign stock, mint a mã, or redesign the boutique.**

---

## 0. How to read this document

This is a **learn-track** note, not a rebuild brief.

- **Cite, don’t invent.** Every shop-law claim points at a file, Slack permalink, or public standard. Industry claims point at Baymard, Nielsen Norman Group, W3C WCAG, ISO, China’s GB/T, Square’s catalog docs, or peer-reviewed color-vision literature. If a fact is missing from those sources, the gap is named. The gap is not filled with a made-up mã, qty, price, or “typical boutique” anecdote.
- **Never invent a mã.** Format strings (`AO` + three digits; hub letter + two-or-more digits) are **patterns**. Slack’s `AO001` / `AO003` lines are **decision-template examples** from `#shop-decisions` (2026-09-04), not proof those pieces exist in Square. Do not copy them into Official, Square, or a sell-test catalog.
- **No redesign mandate.** Improve **inside** the existing boutique look: rose / blush, Allura script + Nunito, rounded-full pills, bottom sheets, rose-950 overlays, existing lightbox. Do not replace that language with a generic Shopify / Horizon PDP.
- **Facebook is still the store** until Boss changes that in `#shop-decisions`. A sell-test PDP is a **look + choose + inbox mã** surface, not a silent checkout.

### 0.1 Research method (and what this pass could not see)

| Source | Result |
| --- | --- |
| Repo `excel-kit/`, `sassy-closet/`, `README.md` | Read. Primary shop law. |
| Slack `#shop-decisions` | Five standing messages (2026-09-04). Cited below. |
| Linear | Only `TIE-1` (“Get familiar with Linear”). No PDP issue. |
| Granola meetings | MCP unauthorized — no meeting notes available this pass. |
| Notion AI search | Requires Business plan. Keyword search returned no Sassy Closet PDP pages. |
| Public UX / standards / Square docs | Fetched 2026-09-09. URLs in §17. |

If later agents find a Granola call or a Notion page that contradicts a shop-law cite here, **shop law wins**. Industry research never overrides Square-as-SoT, “never invent mã,” or Asia-size + cm.

### 0.2 Sister docs

This file is numbered `02` so a later catalog / intake / photography note can sit beside it as `01` / `03`. It is readable alone.

---

## 1. Executive summary

A fashion product-detail page (PDP) for a **small clothing shop** has one job: help a buyer see the exact piece, pick a **color name** and an **Asian size + cm**, know whether that combination is **Available / Reserved-Hold / Sold / staged-only**, and leave with a **copyable mã** they can paste into Facebook inbox.

Sassy Closet already has most of the **data nouns** (mã, color list, Asian size chips, Official measurements, Hold / Reserved, Square variation name = size + color). It does **not** yet have a customer PDP. The intake site is labeled `INTAKE • NHẬN ĐỒ` — staff, not shoppers (`sassy-closet/components/BrandHeader.tsx`).

Industry research (Baymard, NN/G) pushes **exposed size buttons**, **swatches on list pages**, and **galleries that change with the selected color**. This shop should take the **buttons** and the **gallery sync**, and **decline hue-only customer swatches** for the sell-test:

1. The locked color vocabulary includes **patterns and non-hues** (Caro, Hoa, Ánh kim, Pastel, Khác) that a hex circle **cannot** tell the truth about (`sassy-closet/lib/kinds.ts`).
2. WCAG 2.2 SC **1.4.1 Use of Color** forbids using hue as the *only* way to tell options apart.
3. Red–green color vision deficiency is common enough (on the order of **8% of men of Northern European ancestry**; lower but non-zero in East Asian men) that a boutique selling “Hồng đậm” vs “Đỏ đô” as two dots will mis-sell.
4. The **APPLY** rule for sell-test is explicit: **admin swatches + per-color photos**; **customer TEXT-ONLY colors → gallery**; **keep fancy motion**.

Hold is **not** one bit. Official `Hold`, Official `Reserved`, Ma_List `held`, Orders `Reserved`, fulfill `Hold`, site `reserved`, and Slack “Hold {ma} past 24h?” are different machines. A PDP that prints a single “Held” badge will lie.

Two mã **alphabets** already exist in this repo (Official/Square `AO001`-style vs hub `A01`-style). A sell-test page must **display the assigned code for that row**, never translate one alphabet into the other, and never mint the next Dashboard code.

---

## 2. Hard constraints (print these on the implementer’s wall)

1. **Never invent a mã.** Stock reads Dashboard `B21:B27`. Scripts require `--ma` or print ASK STOCK (`excel-kit/schema.py` `ASK_STOCK_MA`; `excel-kit/sot/append_official_row.py`). Sold mã stays retired. Unique piece = unique mã (`excel-kit/DESIGN_NOTES.md`; `excel-kit/square/README.md`).
2. **Never invent qty, $, storage, or photos.** Empty = `—` or **Staged only — not on Square On_Hand yet** (`excel-kit/prompts/FIND_MA_CARD_2026-09-08.md`; `sassy-closet/lib/on-hand.ts`).
3. **Square Free = on-hand source of truth.** Official Excel is a working copy / mã index / captions — not a second warehouse (`README.md`; `excel-kit/DESIGN_NOTES.md`).
4. **Bots draft only.** No Square Save, no Facebook Post/Send, no Zelle from the app (`README.md`; Slack `#shop-decisions` 2026-09-04).
5. **Customer-facing fit = Asia size + cm. Never quote US sizes to buyers** (`excel-kit/DESIGN_NOTES.md` “What we refuse to ship”; `excel-kit/prompts/BOUTIQUE_PHONE_SAFE.md`; `excel-kit/square/README.md`).
6. **Track stock ON** for every item **and** every variation. Boss **yes** 2026-09-04 (`excel-kit/square/README.md`; Slack permalink in §17).
7. **No redesign mandate.** Keep the boutique look and the existing motion language (sheets, rose overlays, rounded-3xl lightbox). NN/G calls some extras “fancy features” and warns they harm if they are not flawless — keep *this shop’s* motion, do not add AR try-on or a new design system ([NN/G, *UX Guidelines for Ecommerce Product Pages*](https://www.nngroup.com/articles/ecommerce-product-pages/)).
8. **Do not treat Wishlist / staged as for-sale stock.** Wishlist mã is forbidden. Bought-without-mã stays on Wishlist + ASK STOCK (`excel-kit/prompts/GF_CLOTHES_INTAKE.md`).

---

## 3. What a PDP is here (and what it is not)

Nielsen Norman Group: the product-detail page is where people decide **whether and what** to buy, because they cannot touch the cloth. Weak PDPs cause abandon **or** the wrong order / return ([NN/G](https://www.nngroup.com/articles/ecommerce-product-pages/)). Their **must-haves**: name, recognizable images, enlarge, price (plus extra charges), **clear options (color / size)**, **availability**, a clear next action, a concise description.

Map that onto Sassy Closet **without** pretending the shop is Shopify-checkout:

| NN/G must-have | Sassy Closet sell-test meaning |
| --- | --- |
| Descriptive name | Official `name_vi` / hub kind label — not a made-up English SEO title |
| Images + enlarge | Per-color photos + existing `PhotoLightbox` (PR #14 language) |
| Price | Sell $ only if already stored; never invent |
| Color / size options | **Text** color names + **exposed** Asian size buttons + cm |
| Availability | Square / Official status, per size×color, honest empty |
| Add to cart | **Inbox mã** (caption already says `Inbox mã để lấy nha`) until Boss changes the store |
| Description | Caption / blurb / notes already on the card — copy, don’t rewrite as ads |

NN/G **nice-to-haves** (reviews, video, zoom, related items) are optional. Do not block sell-test on them. NN/G **fancy features** (AR try-on, 360, subscription) stay off unless Boss asks and the motion is already boutique-quality.

**This is not:** a second inventory, a Square Online replacement, a US-size converter, a swatch-only fashion theme, or a license to mint parent “style SKUs” that group mãs the shop did not assign.

---

## 4. As-built map (cite the code, don’t redesign it)

### 4.1 Surfaces today

| Surface | Job | Customer PDP? |
| --- | --- | --- |
| Facebook inbox | Store (`README.md`; Slack `#shop-decisions`) | Yes — chat, not a page |
| Square Free item library | On-hand, Track ON, SKU = mã | POS / import, not this repo’s UI |
| `Sassy_Closet_SoT.xlsx` Official | Working copy, measurements, status | No |
| Intake site `sassy-closet/` | Món mới / Sửa / Tìm mã / Ask | **No** — `INTAKE • NHẬN ĐỒ` |
| Tìm mã card | Big mã + colors + sizes + thumbs + on-hand | Staff card, closest ancestor of a PDP |
| Saved · Đã lưu | Big mã + Copy mã / link / caption | Staff confirmation |

The Tìm mã card is the **pattern library** a sell-test PDP should steal from, not replace: huge rose mã, kind · colors line, size field, 3-up thumbs, lightbox, staged-only amber, Copy mã (`sassy-closet/components/FindMaCard.tsx`; `excel-kit/prompts/FIND_MA_CARD_2026-09-08.md`).

### 4.2 Color and size as they are stored

**Intake form (staff):**

- Colors are **text chips** of Vietnamese names (`COLORS[].vi`), multi-select, joined with `", "` (`IntakeApp.tsx` `colorLine`). They already look like **pills**, not hue circles — even on admin.
- `color_note` is a free string for shade / fabric / “hơi lệch ảnh.”
- Sizes are `2XS XS S M L XL 2XL` (`SIZES` in `kinds.ts`), multi-select, joined with spaces.
- Mini Boss fallback: “Size trên form: 2XS XS S M L XL 2XL (Asian). Không đổi sang US.” (`ask-fallback.ts`).

**Hub persistence:**

- `Submission.color` / `Submission.size` are **flat strings**, not a matrix (`types.ts`).
- `Piece[]` already has `{ photos, suggested, color, note }` — a per-color photo hook — but **Món mới saves `pieces` as `[]`** (`IntakeApp.tsx` `form.set("pieces", JSON.stringify([]))`). Export CSV has a `color_pieces` column that will stay empty until admin per-color photos are wired (`store.ts` `exportCsv`).
- Photos are stored as `{ma}/001.jpg`, `{ma}/002.jpg` … sequential, **not** `{ma}/{color}/…` (`store.ts` `saveSubmission`).

**Official Excel:**

- Columns include `size`, `color`, `bust_chest`, `waist`, `length` (`schema.py` `SOT_OFFICIAL`).
- Candidates header is literally `Size Asia + cm`.
- Photo files on disk: owned `{MA}.jpg` / `{MA}_2.jpg`; wishlist `#001.jpg` (`DESIGN_NOTES.md`; `GF_CLOTHES_INTAKE.md`). Excel stores `photo_link` only.

**Square:**

- Item Name = `{mã} + short name`.
- Variation Name = **Asia size + color** (`M / đen`).
- SKU = mã.
- One variation row per size/color.
- Unique piece = unique mã (`excel-kit/square/README.md`; `SQUARE_SKU_IS_MA` in `schema.py`).

That last pair is the **boutique constraint** mass-fashion PDPs ignore: you do not invent a parent style code and 12 child SKUs. If two physical pieces exist, Stock assigns **two** mãs. A PDP “color option” on one mã is **the colors recorded on that mã**, not a new catalog.

### 4.3 Two mã alphabets (display clarity starts here)

| Alphabet | Pattern (not stock) | Who mints? | Where |
| --- | --- | --- | --- |
| Official / Square / Photos-on-OneDrive | `AO\|QU\|VA\|AK\|GI\|PK\|SET` + **3 digits**. Regex `MA_RE` | **Nobody in git.** Stock reads Dashboard `MAXIFS` `B21:B27`. Boss assigns. | `excel-kit/schema.py`, `append_official_row.py`, Square import |
| Hub intake | Kind letter `A Q V D K G B P H J S O` + **2+ digits** (UI placeholder “A01”) | **The site `nextMa()` on Lưu & lấy mã** (`store.ts` `resolveSaveMa`) | `sassy-closet/lib/mint.ts` |

These are **not** mechanically equivalent. `A` ≠ `AO`. `D` (Đầm) exists on the hub (`kinds.ts`; PR #17) and does **not** appear in Official `MA_PREFIXES`. A sell-test that “helpfully” reprints a hub `A01` as `AO001` **invented a mã**. Forbidden.

**Display rule:** one alphabet per row, the one already stored on that row. Show it huge. Copy it verbatim. Never convert.

### 4.4 Boutique look (the thing you must not replace)

Cited tokens, not a moodboard:

- Page wash: `#fff1f5` + pink radial (`globals.css`).
- Primary: `#D82B60` / `#fff7fa` (`tailwind.config.ts`).
- Type: Nunito (Latin + Vietnamese) + Allura script title (`layout.tsx`, `BrandHeader.tsx`).
- Controls: `rounded-full` pills, `min-h-10` / `min-h-11`, `ring-1 ring-rose-100`.
- Overlays: `bg-rose-950/30` sheets, `bg-rose-950/70` lightbox, `rounded-3xl` image (`PhotoLightbox.tsx`).
- Motion language already shipped: **bottom sheet on phone / centered sheet on `sm`**, Done / ✕ / Esc, focus restore, body scroll lock. That *is* the “fancy motion” to keep — soft, rose, the same as Saved / Tìm mã — not a new spring-physics design system.

Excel boutique books: deep rose / blush headers, yellow = type, no lock, freeze header only (`DESIGN_NOTES.md`; `BOUTIQUE_PHONE_SAFE.md`). Same personality, different surface.

---

## 5. Industry research (what the literature actually says)

### 5.1 Exposed options beat dropdowns

Baymard’s product-page and size-selector work is consistent across 2017–2026 public write-ups:

- Size (and color) **hidden in a `<select>`** makes people open the menu to learn their size is gone — disappointment after effort ([*Always Use “Buttons” for Size Selection*](https://baymard.com/blog/use-buttons-for-size-selection); [*Product Page UX Best Practices 2026*](https://baymard.com/blog/current-state-ecommerce-product-page-ux)).
- Exposed **button-like** selectors let people see the set and the gaps at a glance. Baymard’s 2026 product-page article still lists “always use buttons for size” as a top miss (they report **57%** of benchmarked sites still don’t).
- The shop **already** uses exposed size pills on intake. Sell-test should **keep buttons**, not “upgrade” to a dropdown to look more like a theme.

Craftshift / MECLABS (vendor-cited, treat as weaker than Baymard): visible options beat hidden menus; they quote a **14.6%** order-rate lift for visible vs dropdown in a MECLABS test ([Craftshift variant-image article](https://craftshift.com/shopify-variant-image-swatches-conversion-rates/)). Use as supporting color, not shop law.

### 5.2 Swatches: Baymard likes them on **lists**; this shop still says text on the **PDP**

Baymard’s list-item research: for visually driven types, **color swatches on the product card** help people compare without opening every PDP. They recommend showing **all** colors (horizontal scroll + a truncated last chip or arrows). They report **57%** of sites fail to expose the full set on mobile lists ([*Make All Color Swatches Available in Mobile List Items*](https://baymard.com/blog/mobile-interactive-color-swatches); [*Mobile UX Trends 2026*](https://baymard.com/blog/mobile-ux-ecommerce)). Combining colors into **one** list item (not one card per color) also tested better than exploding the grid ([*Combine Variations of Products into One List Item*](https://baymard.com/blog/combine-variations-one-list-item)).

**That is list UX.** It does not override:

- WCAG 1.4.1 (hue cannot be the only cue).
- This shop’s color words that are **not hues**.
- The sell-test APPLY: customer **text-only** → gallery.

A later PLP (lookbook grid) may add **admin-generated** mini photos as “swatches” (a photo of the cloth, not a CSS circle). That is still not a hex dot. Out of scope for this file except as a pointer.

### 5.3 WCAG: text (or another non-color cue) is required

[W3C WCAG 2.2 Understanding SC 1.4.1](https://www.w3.org/WAI/WCAG22/Understanding/use-of-color.html) (Level **A**):

> Color is not used as the *only* visual means of conveying information, indicating an action, prompting a response, or distinguishing a visual element.

Sufficient technique **G14**: information conveyed by color differences is also available in **text**. Contrast between two hues does **not** excuse a “this ring is the selected color” control if the user must recognize *which named color* it is.

Also in play for a PDP picker (not all Level A):

- **1.1.1** Non-text content — a circle needs an accessible name (“Đen”, not “button”).
- **1.3.1** Info and relationships — group label “Màu” / “Size”.
- **2.4.7** Focus visible.
- **2.5.5** Target size (AAA, 44×44 CSS px) — intake already uses `min-h-10` / `min-h-11`; keep that.
- **4.1.2** Name, Role, Value — selected / unavailable announced.

Fashion-theme writeups that only add `aria-label` on a dot still fail **1.4.1 for sighted** users who cannot tell Hồng đậm from Đỏ đô. Visible **words** are the Level A fix. That is exactly the customer text-only APPLY.

### 5.4 Color vision deficiency (why “just make nicer dots” fails)

- Birch (2012), widely cited: inherited red–green deficiency about **8% of European-Caucasian men** and **0.4% of women**; **about 4–6.5% of Chinese and Japanese men** (J. Birch, “Worldwide prevalence of red-green color deficiency,” *J. Opt. Soc. Am. A* 29(3), 2012 — [ResearchGate record](https://www.researchgate.net/publication/223985289_Worldwide_prevalence_of_red-green_color_deficiency)).
- Narrative review (2025): up to **8% / 0.5%** Northern-European men/women; lower in many Asian and African samples ([Hasrod, *Healthcare* 13(16):2031](https://www.mdpi.com/2227-9032/13/16/2031)).
- A 2024–2025 meta-analysis summarized in *Review of Optometry* estimated **global** CVD ≈ **2.59%**, males **4.38%**, females **0.64%**, deutan > protan ([summary](https://www.reviewofoptometry.com/article/study-describes-epidemiology-of-congenital-color-vision-deficiency)).

Sassy Closet’s US Facebook buyers + Asian-sourced clothes sit across those populations. A PDP that distinguishes **Đỏ / Hồng đậm / Đỏ đô / Nude** by hue alone will fail a non-trivial slice of buyers **and** fail WCAG. **Photos of the actual cloth** plus **the Vietnamese name** are the boutique-honest pair.

### 5.5 Gallery must follow the selected color

NN/G: one view is rarely enough; people use extra angles (inside of a bag, fabric, on-body) and often decide from images before they finish the text ([NN/G product pages](https://www.nngroup.com/articles/ecommerce-product-pages/); [NN/G listing photos](https://www.nngroup.com/articles/product-photos-listing-pages/)).

Shopify’s **native** model (relevant as the industry default, **not** as something this shop should install): one featured image per variant; the theme **scrolls** to it; the rest of the gallery **stays mixed**. Merchants and theme authors treat that as the main apparel-PDP failure mode ([Craftshift, *Shopify variant images*](https://craftshift.com/shopify-variant-images-complete-guide/); [Craftshift, *Group gallery by variant*](https://craftshift.com/shopify-image-gallery-grouping-by-variant/); [Shopify Community, Horizon thread](https://community.shopify.com/t/horizon/659928)). Square Catalog is closer to “images on the variation” (`image_ids` on [`CatalogItemVariation`](https://developer.squareup.com/reference/square/objects/CatalogItemVariation)) — still not a filtered boutique gallery unless the **storefront** filters.

**Sell-test rule (ours, derived from the above + shop photo law):** selecting a color **replaces** the visible gallery with photos tagged to that color. If none are tagged, show only **unassigned** photos for that mã. If those are empty, show the existing empty state (`—`), **never** a placeholder stock photo, never another mã’s photos.

### 5.6 Sizing: letters are a nickname; cm is the fact

**Shop law (already locked):** Asia size + cm to customers; refuse US quotes (`DESIGN_NOTES.md`; GF HOW_TO; Square variation name; `append_official_row.py --size` help: “Asia size + cm (never US)”).

**Why that law is scientifically ordinary, not a quirk:**

- [ISO 8559-1:2017](https://www.iso.org/standard/61686.html) (*Size designation of clothes — Part 1: Anthropometric definitions*) defines **how to measure bodies**, confirmed current in ISO’s 2026 review. It is meant to sit **beside** national systems, not replace them. ISO 8559-2 (primary/secondary dimension indicators) was updated **2025**; ISO 8559-3:2018 covers how to build measurement tables ([ISO/TC 133 catalogue](https://www.iso.org/committee/52374/x/catalogue/)).
- China’s **GB/T 1335.1-2008** *服装号型 男子* (Standard sizing systems for garments — Men), implemented 2009-08-01, reviewed **continue effective** 2025-05-30 ([SAMR national standards platform](https://std.samr.gov.cn/gb/search/gbDetailed?id=bJm52CpSOZ0%3D&mode=p); [openstd.samr.gov.cn record](https://openstd.samr.gov.cn/bzgk/std/newGbInfo?hcno=EC87D6B2262ABDCFD055989D2C9DCC9F)). The series is the familiar **height / bust-or-chest + body-type letter** (e.g. the textbook form `165/88A` — **example of the national notation, not a Sassy Closet mã or a live size we assigned**). GB/T 1335.2 is the women’s counterpart in the same series.
- Japan’s apparel numbers (commonly discussed as a **9** ≈ bust near 83 cm) and Korea’s older **55 / 66** scale are **different national encodings of centimetres**, not US 0–16 ([ConvertSizes explainer](https://convertsizes.com/guides/asian-clothing-sizes/) — secondary; prefer measuring the **garment**).
- Trade blogs that publish “Asian M = US 8” tables ([HiSourcing](https://www.hisourcing.com/asian-size-to-us-size/), [Eprolo](https://eprolo.com/asian-size-to-us-size), [HiredChina](https://www.hiredchina.com/articles/asian-sizing-to-american-sizing-guide/)) **disagree with each other** and with shop law. They are useful only as evidence that **letter conversion is unstable**. HiredChina’s usable sentence: skip S/M/L, compare **your cm** to the **garment chart**. AllChinaBuying’s usable caution: some charts list **garment** circumference, not body circumference — ease of a few cm matters ([AllChinaBuying](https://allchinabuying.com/blog/chinese-clothing-sizing-guide)).

Baymard’s apparel sizing list (10 parts) asks for conventional **and** numeric sizes, **inches and cm**, international conversions, how-to-measure, type-specific charts, a **Size guide link next to the selector**, Back-button-safe overlay, CS link, model measures ([*Apparel: 10 Best Practices on Sizing*](https://baymard.com/blog/apparel-size-information); [*5 Apparel UX Best Practices*](https://baymard.com/blog/apparel-5-best-practices)).  

**Boutique cut of that list (improve within look, do not ship a US converter):**

| Baymard item | Sell-test |
| --- | --- |
| Conventional size | `2XS`…`2XL` pills (already) |
| Numeric / measurements | Official `bust_chest`, `waist`, `length` **in cm**, shown when present |
| Inches + cm | **cm primary.** Inches only if Boss later asks; never instead of cm |
| International conversions | **Do not** add a US column. That is the refused feature |
| How to measure | Short VI + pictogram, in a sheet (same sheet chrome as Tìm mã) |
| Type-specific | Áo vs Quần vs Váy vs Giày use different cm rows (ISO 8559 primary dimensions differ by garment) |
| Link next to selector | `Size Á châu + cm` text button beside the pills |
| Back closes overlay | Same as lightbox / find card |
| CS | “Inbox mã” — Facebook is the store |
| Model measures | Only if a real model measure was recorded. Never invent |

Baymard also notes a Pangaia chart that was **cm-only** frustrated inch-native testers. This shop **accepts that tension on purpose**: the clothes and the GF intake are cm-native; US buyers are told Asia + cm, not a fake US equivalent.

### 5.7 Availability, Hold, and “out of stock”

Baymard on temporary OOS: telling people “out of stock” with no path makes ~**30%** leave the site; **68%** of their benchmark (that article’s figure) did not let people order a temporarily missing item ([*Let Users Purchase Temporarily Out of Stock Products*](https://baymard.com/blog/handling-out-of-stock-products)). For a **unique-piece** boutique, “backorder the same mã” is often **false** — the piece is gone. Do **not** apply mass-replenish UX to a sold unique mã.

Baymard on reservation sites: if the **viewer** is the one holding the piece, do not show them “Sold out” — show **in your hold / in your cart** ([*Highlight Items Already in the User's Cart*](https://baymard.com/blog/highlight-products-if-in-users-cart)). Slack’s hold-extend example is a **Boss yes/no**, not a public countdown widget.

Square: inventory and sold-out live on the **variation**, with `track_inventory` and location `sold_out` ([Catalog design](https://developer.squareup.com/docs/catalog-api/design-a-catalog); [Monitor sold-out](https://developer.squareup.com/docs/inventory-api/monitor-sold-out-status-on-item-variation); [`CatalogItemVariation`](https://developer.squareup.com/reference/square/objects/CatalogItemVariation)). A parent item has **no** SKU. This matches “SKU = mã on the variation row” in `square/README.md`.

---

## 6. Per-color photos

### 6.1 Why they exist

NN/G: images set the contract; wrong or missing views cause the wrong order or no order. Apparel color is a **visual** decision. A mixed gallery (đen + hồng + hoa in one strip) is the Shopify-default failure: the buyer is never sure which photos are the piece they will receive (Craftshift / Horizon thread, §5.5).

Shop photo law:

- Bytes live in `Documents/Sassy Closet/Photos/` or hub Blob ` /api/photos/{ma}/{file} `.
- Excel never embeds images (`DESIGN_NOTES.md`).
- Never invent missing photos (`sassy-closet/README.md` restore notes; FIND_MA_CARD hard stops).
- Tìm mã shows up to **3** thumbs in one row, `+N` overflow, tap → lightbox; zero photos stays text-only (PR #14 / `photos.ts` `FIND_CARD_THUMB_LIMIT`).

### 6.2 What “per-color” means in *this* data model

Content-modeling rule: store **meaning**, not “pinkSwatchHero” ([separation of concerns](https://www.sanity.io/docs) as taught in the content-modeling skill: fields named for *what the content is*).

Recommended **semantic** shape (do not implement in this PR; this is the learn note):

```text
ma            → already assigned. Never minted here.
colors[]      → list of { key, label_vi, note }   // label is the customer text
photos[]      → list of { path, color_key | null, role }
role          → hero | flat | on_body | detail | flaw | other
size_cm       → { letter, bust_chest?, waist?, length?, extra? }  // Official already has three cm columns
availability  → from Square / Official, per size×color, never invented
```

`color_key` is a **stable slug** (`den`, `dodo`, `hoa`, `khac`, or a note-hash for a one-off). The **customer string** is `label_vi` (“Đỏ đô”), never the slug.

The unused `Piece` type is the closest existing hook: `{ photos, suggested, color, note }`. Admin per-color photos should **fill `pieces`**, not invent a second photo table that the CSV cannot see.

### 6.3 Admin (staff) — swatches + attach photos

APPLY: **admin swatches + per-color photos.**

Admin may use:

- The existing **named pills** (already not hex dots).
- Optional **hue hint** *next to* the name for the simple chips (Đen, Trắng, Hồng) — a 16–20px disc **plus** the word, never the disc alone.
- **No disc** for Caro, Hoa, Ánh kim, Pastel, Khác — those get a tiny **photo thumb** or a pattern mark, plus the word.
- `color_note` stays the override (“hồng baby, không phải hồng đậm”).
- For each selected color: drop zone “Ảnh cho màu {label}”. Reuse dashed rose drop + ♡ from Món mới.
- Untagged uploads remain **shared** (flat / label / flaw that apply to every color). Shared photos stay visible for every color.

Do **not** require a photo for every color before Lưu. Empty is honest.

Do **not** auto-generate a color from a photo (the find-by-photo path is **retrieval**, not minting a color name). Suggested colors on `Piece.suggested` may pre-tick a chip; a human still confirms.

### 6.4 Customer — photos are the swatch

Customer does not get a disc. They get:

1. The **word**.
2. The **gallery of that word**.
3. Lightbox / 3-up / `+N` already shipped.

If a color has no photos, do not grey-lie with a CSS circle of “approximate hồng.” Keep the text option; gallery falls back to shared photos or `—`.

### 6.5 File names (do not invent mã in the path)

Keep `{assigned_ma}/001.jpg` on Blob. Color is **metadata**, not a second folder that implies a second mã.

OneDrive Official photos stay `{MA}.jpg` / `{MA}_2.jpg` as in GF intake. If a later Kit sync wants color in the filename, use `{MA}_{color_key}_2.jpg` **only** when `{MA}` is already assigned. Never `AO002` because `AO001` existed.

---

## 7. Text-only vs swatch — customer UI

### 7.1 Decision (sell-test)

| Role | Color UI | Why |
| --- | --- | --- |
| **Admin / Stock / GF intake** | Named pills + optional hue hint + per-color photo attach | Fast tagging; matches `COLORS` + `color_note` |
| **Customer PDP** | **Text only** (same pill chrome: rose ring, rounded-full, `aria-pressed`) | WCAG 1.4.1; non-hue names; APPLY; gallery is the proof |
| **Customer PLP (later)** | Prefer **photo** chips over hex; text of selected color on the card | Baymard list-swatch research, without lying discs |

### 7.2 Why this is not “ignoring Baymard”

Baymard’s swatch guideline is about **seeing that other colors exist** and **not hiding them in a menu**. Text pills that are **all visible** satisfy the “exposed options” finding. They fail only the “chromatic preview on a *list card*” finding — which this shop should meet later with **photos**, not hex.

Baymard also says: show **unavailable** sizes/colors as visible-but-disabled, not missing (size-button articles). Same for text pills: **Hồng** with a thin strike / 50% opacity + `aria-disabled` if Square says 0, still **readable**.

### 7.3 Copy and grouping

- Group label: `Màu` / `Color` (fieldset + legend, like intake).
- Selected echo: `Đang xem: Đỏ đô` so the gallery change is verbal, not only visual (WCAG + NN/G “explain each variation”).
- `color_note` when present: one line under the pills (`Ghi chú: …`), not a tooltip-only (tooltips fail touch and 1.4.1).
- Multi-color **on one mã**: these are **names recorded on that piece**, not a promise of N sellable SKUs. If Official/Square has one variation `M / đen`, do not show Trắng as buyable.

### 7.4 Interaction

Treat the set as a **single-select** for gallery (radio semantics) even if Official stored several names:

- Staff multi-select on intake = “these names apply.”
- Customer single-select = “show me this name.”
- `role="radiogroup"` + `aria-checked` **or** native radios styled as pills (prefer native). Intake today uses `aria-pressed` toggle (multi). Customer PDP should not copy multi-toggle — that is how people add two colors to one inbox ask by accident.

Size stays **single-select** on the PDP (one body). Intake multi-size means “this mã was tagged with several letters” — customer still picks one letter to ask about.

---

## 8. Gallery sync

### 8.1 Desired behavior

```text
load PDP for assigned {ma}
  → photos = all photos for that mã only
  → selectedColor = first color that has photos, else first color, else null
  → view = filter(photos, color == selectedColor) ∪ filter(photos, untagged)
  → if view empty → text-only empty (—)

on customer color text activate
  → selectedColor = that label
  → rebuild view (same filter)
  → move hero to view[0]
  → keep fancy motion (see 8.3)
  → do not change mã
  → do not fetch another mã’s folder

on customer size activate
  → selectedSize = that letter
  → availability block updates (Square / Official / staged-only)
  → gallery does **not** change unless a photo is tagged to that size
      (default: photos are color-keyed, not size-keyed)

on lightbox open
  → same PhotoLightbox (Esc, ✕, backdrop, focus)
  → stay on this mã’s current view (do not leak other colors into the lightbox)
```

### 8.2 Sync bugs to refuse

| Bug | Why it’s wrong |
| --- | --- |
| Scroll-to-image but leave 40 mixed thumbs | Shopify-default; Craftshift / Horizon |
| Swap hero, thumbs still mixed | Same bug, prettier |
| Missing color → show a CSS circle | Invents a hue |
| Missing photos → show another mã | Invents stock appearance |
| Color change remints or “related mã” | Invents mã |
| Size change silently switches mã | Unique-piece law |
| Animation so long it feels like navigation | NN/G: extra chrome must not obscure info |

### 8.3 Keep fancy motion (boutique, not a new brand)

Reuse, don’t replace:

- **Sheet / overlay** timing already implied by Saved + Find + Lightbox (instant open, Esc / Done / backdrop).
- **Hero change:** short opacity crossfade (150–250ms) on the **image only**, rose-tinted if you must tint — not a page wipe, not a Shopify theme section reload.
- **Thumb selected:** thicker ring + `aria-current`, same as active kind pill (`bg-primary`), not a bouncing dot.
- **Lightbox** stays `rounded-3xl` + `ring-4 ring-white/80` + rose-950 veil.
- Prefer `prefers-reduced-motion: reduce` → instant swap (WCAG 2.3.3 / 2.2.2 spirit).

Do **not** add: full-page parallax, auto-playing lookbook video, cursor-follow zoom, or a canvas WebGL cloth. NN/G files those under fancy features that fail when imperfect.

### 8.4 Performance (so the motion stays pretty)

Hero: `fetchpriority="high"`, not lazy. Secondary thumbs lazy. That is ordinary LCP hygiene; no source required beyond common practice, but it protects the boutique feel on a phone — the same phone GF and buyers use (`BOUTIQUE_PHONE_SAFE.md` is the shop’s phone ethic).

---

## 9. Asian sizing (cm) on the PDP

### 9.1 Selector

Match intake chrome:

```text
Size (Á châu)
[2XS] [XS] [S] [M] [L] [XL] [2XL]
Size Á châu + cm    ← opens sheet
```

- Only **letters that exist on this mã** are enabled. Others: visible disabled **or** omitted? Baymard prefers **visible disabled** so people see the shop’s scale. For a unique piece with one letter, showing seven dead pills is honest (“we use this scale; this piece is M”) **if** it does not look like six hidden SKUs. Prefer: **all letters in the shop scale**, unavailable ones disabled, selected one filled primary. Caption line already prints `Size {letters}` (`captions.ts`).
- **Never** print `US 8` / `US M` next to them. Not in the sheet, not in alt text, not in schema.org `size`.

### 9.2 The cm sheet (boutique sheet, not a new modal kit)

Title: `Size Á châu + cm`  
Body, **only fields that exist** on Official / the staged row:

| Field | Source |
| --- | --- |
| Letter | `size` / `sizes_in_stock` |
| Ngực / ngực-ngang / chest | `bust_chest` |
| Eo / waist | `waist` |
| Dài / length | `length` |
| Extra | `notes` / `flaws` if they are fit-related |

Units: **cm**. Label the unit on every number (`88 cm`, not `88`).

How-to (short, VI first — GF contract is VI first):

1. Thước dây, không thước sắt.  
2. Ngực: vòng đầy nhất, thước song song sàn.  
3. Eo: chỗ nhỏ nhất.  
4. So **số trên áo / quần** (nếu Staff đo garment) với số trên người + chút rộng.

ISO 8559-1 is the measurement vocabulary; do not paste ISO’s copyrighted table. A **pictogram** in the sheet is allowed if it is ours (Allura/Nunito/rose), not a ripped Uniqlo chart.

If **no cm** is stored: sheet says so. Do not fill “typical Asian M = 88.” That invents measurements the same way inventing a mã invents stock.

### 9.3 Shoes, sets, accessories

`SIZES` is a **body-letter** list. Giày / túi / tóc / trang sức may not use 2XS–2XL. Official `category` / hub kind must drive the selector:

- Giày: show the **stored** size string (cm / EU-from-source) as **text**, still no US conversion.
- PK / túi: hide the letter row if `size` is empty; don’t force M.
- SET: letters + cm for the piece that was measured; don’t invent a second mã for the skirt.

`assertNever` on kind when adding a new kind’s fit UI (`kinds.ts` already exports `assertNever`).

### 9.4 Square variation name

Keep `Variation Name = {Asia letter} / {color word}` (`M / đen`). The PDP should **read** that pair, not invent a third encoding (`Medium / Black` US).

---

## 10. Hold states (do not collapse)

### 10.1 The machines (cited)

| Machine | Values | Meaning | Customer PDP? |
| --- | --- | --- | --- |
| Official `status` | Available, **Reserved**, Sold, **Hold**, Damaged, Donated | Working-copy life of the **piece** (`schema.py` `SOT_OFFICIAL_STATUS`) | See 10.2 |
| Ma_List `status` | in_stock, **held**, sold, archived | Lean desktop map. `Reserved`→`held`, `Hold`→`held` (`OFFICIAL_TO_MA_LIST_STATUS`) | Do not show Ma_List words; they merge two Official states |
| Orders `order_status` | Inquiry, **Reserved**, Paid, Shipped, Picked up, Cancelled | **Buyer thread**, not the piece shelf | Not a PDP badge |
| Orders `fulfill` | Ship, Local pickup, **Hold**, TBD | How they will get it | Not “this piece is Official Hold” |
| Hub `on_hand[].status` | on_hand, **reserved**, sold, dead | Site overlay; empty ⇒ staged-only | Yes, per size×color, if rows exist |
| Square | Track ON; variation `sold_out` / qty | **SoT** | Yes, if wired; never fake |
| Slack `#shop-decisions` | “Hold {ma} past 24h?” yes/no | **Extend** a hold; bots stay read-only until Boss answers ([permalink](https://tien-ota6716.slack.com/archives/C0BV3GYC602/p1788541753903809)) | Do not start a public 24h timer unless Boss said that hold exists |

Dashboard already **separates** Official Reserved (row 7) from Other Official Hold/Damaged/Donated (row 9) and Orders Reserved (row 14) (`SOT_DASHBOARD_ROWS`). The PDP must stay as careful as the Dashboard.

### 10.2 Customer-facing status (honest, small vocabulary)

Use **one** customer word per **selected size×color**. Prefer Square when present; else Official; else staged-only. Never average them.

| Internal | Customer line (VI / EN) | CTA |
| --- | --- | --- |
| Square qty > 0 and Official Available (or no Official) | `Còn · Available` | Copy mã → inbox |
| Official **Reserved** or hub `reserved` or Orders Reserved **for this piece** | `Đang giữ · Reserved` | Copy mã; “Inbox hỏi còn giữ không” — do **not** claim it is free |
| Official **Hold** | `Tạm giữ · Hold` (not “sold”, not “available”) | No “buy” language. Staff/Boss only unless Boss says the hold is a customer hold |
| Official Sold / Square 0 / hub sold | `Đã bán · Sold` | Do not mint a replacement mã |
| Official Damaged / Donated / hub dead / Ma_List archived | `Không bán · Unavailable` | No qty theatre |
| No Square on-hand rows | **Staged only — not on Square On_Hand yet** (exact string) | Not for sale as stock |

**Do not** map Official Hold and Official Reserved to the same customer badge just because Ma_List maps both to `held`.

### 10.3 24 hours

The only **time** in shop law this pass found is the Slack **example question** “Hold AO003 past 24h?” — a **template**, and the mã in it is **not live stock**. It tells us:

- Holds can **expire** in the team’s head.
- **Extending** is a Boss yes/no in `#shop-decisions`.
- Bots do not silently keep a piece reserved.

Sell-test must **not** invent a countdown (`23:59:12`) unless a real `hold_until` field is added later and filled by Stock. A fake timer is fake scarcity (Baymard’s reservation article is about **accurate** “you reserved this,” not a ticking marketing badge).

### 10.4 Unique piece vs Baymard backorder

Baymard’s “let them buy OOS” assumes **replenish**. Shop law: unique piece = unique mã; sold stays retired. Customer CTA on Sold is **not** “preorder this mã.” Optional later: inbox “xin mã khác cùng kiểu” — still **no** invented sibling mã.

---

## 11. Mã display clarity

### 11.1 Why mã is the product

Captions put **mã on line 1** (`captionStarter` / `buildCaptionVi`). Footer: `Inbox mã để lấy nha`. Saved card and Find card use **text-5xl / text-6xl**, `tracking-wide`, rose-700. Soft-launch Slack examples ask Save as `{mã} / {size} / {color}`. The mã is how Facebook, Square, Photos, and Excel meet.

If the PDP hides the mã under a pretty English title, inbox matching breaks.

### 11.2 Visual rules (steal, don’t restyle)

From Saved / Find (cite components):

- One line: the **assigned** mã, centered, extra-bold, wide tracking, primary rose.
- Second line: `kind · colors · color_note` (`kindColorsLine`) — **text**, not discs.
- Third: size letters + cm if present.
- Actions: **Copy mã**, Copy caption starter (mã line 1), then the inbox instruction.
- Toast: `Đã copy` (already).

Minimum contrast: rose-700 on blush already used; do not drop to light pink on pink (WCAG 1.4.3 for the mã itself).

### 11.3 What never appears

- Dashboard “next AO” strings (`B21:B27`) — those are Stock tools, not product codes.
- A second “SKU” field that differs from mã.
- Hub-to-Official “translation.”
- Wishlist `wish_id` / `#001` dressed up as a mã (`GF_CLOTHES_INTAKE.md`: mã forbidden on Wishlist).
- Example codes from this doc or Slack, unless that exact code is **on the row you loaded**.

### 11.4 Deep links

Hub already uses `/?ma={code}` for **Sửa** (staff). A public sell-test URL should still be the **assigned** mã (query or path). Unknown code → the same soft `Không tìm thấy mã`, not a generated suggestion.

### 11.5 Square item vs variation

Square: the **item** has no SKU; the **variation** has SKU + name ([Design a Catalog](https://developer.squareup.com/docs/catalog-api/design-a-catalog)). Shop import: SKU = mã, variation name = size + color. On a one-variation item, Square POS **hides** the variation name. The **PDP should still show size + color + mã**, because Facebook buyers never see POS.

If one day one Square item has two variations, shop law still says unique piece = unique mã — treat a second variation with a **second assigned mã**, or stop and ASK STOCK. Do not reuse a sold or live mã on a new variation.

---

## 12. Information architecture (content, not a new theme)

Structured content: **color label**, **size letter**, **cm measures**, **photo role**, **availability** are nouns. `heroPinkCircle` is not. The content-modeling rule is the same one in Sanity’s “content is data, not pages” guidance: name fields for meaning so a later pixel pass does not require a data migration (see the content-modeling skill’s *separation of concerns* note in this workspace).

Channel reuse (same nouns):

| Noun | Facebook caption | PDP | Square | Official |
| --- | --- | --- | --- | --- |
| mã | Line 1 | Hero | SKU | `ma` |
| color words | `Màu …` | Text pills | Variation name tail | `color` |
| size letter + cm | `Size …` | Pills + sheet | Variation name head | `size`, `bust_chest`, `waist`, `length` |
| photos | Owner posts | Gallery filter | (out of git) | `photo_link` |
| status | — | 10.2 words | Track / sold_out | `status` |

A redesign of **pixels** should not require renaming these. That is the test.

---

## 13. APPLY notes — sell-test

These are the implementation notes the title asked for. Still **no mã minting**, still **no redesign**.

### 13.1 Scope

A **read-only** PDP (or PDP-ish block) for **rows that already have a mã**. CTA = Copy mã + inbox line. No Square Save. No Post. No cart that decrements stock.

### 13.2 Admin (behind intake / Tìm mã / a slim staff flag)

1. Keep **Màu có sẵn** pills (`COLORS` + Khác + `color_note`).
2. Optional hue disc **only** on hue-like chips, always **with** the word.
3. Enable `pieces`: each selected color can own a photo list. Shared photos stay on `photo_paths` with `color_key = null`.
4. Do not block Lưu on missing photos.
5. Do not mint mã to “create a colorway.”
6. Swatches are a **staff acceleration**, not a customer preview.

### 13.3 Customer

1. **TEXT-ONLY** color controls (boutique pills, not circles).
2. Activating a color **filters** the gallery (hero + thumbs + lightbox set).
3. Size = exposed Asian letters + **Size Á châu + cm** sheet; no US.
4. Status from §10.2. Staged-only uses the **exact** amber sentence.
5. Mã display from §11. Copy mã is first-class.
6. **Keep fancy motion:** existing sheets, rose overlays, image crossfade, lightbox. `prefers-reduced-motion` instant.
7. Vietnamese first on fit copy (GF / intake ethic).

### 13.4 Within boutique look (checklist)

- Nunito + Allura, `#D82B60`, blush wash.
- `rounded-full` pills, `rounded-3xl` cards / lightbox.
- Bottom sheet on small screens.
- No new color system, no Inter/system-ui takeover, no dark luxury theme, no Shopify Horizon clone.
- No fifth intake tab (`BOSS.md`). A public PDP is a **different route**, not a fifth tab on intake.

### 13.5 Data you may read

Staged `GET /api/ma/{code}` (already). Official cm if a later read-only export exists — **do not** write Official from the PDP. Square qty only if a read path exists; otherwise staged-only. Never display Dashboard next-mã.

### 13.6 Explicit non-goals for sell-test

Shopify, Square Online theme, US size widget, hex-only customer swatches, fake model measurements, fake reviews, AR try-on, auto-playing video, inventing sibling mãs for each color, collapsing Hold into Reserved, countdown timers without `hold_until`, embedding photos in Excel.

---

## 14. Suggested PDP skeleton (chrome reuse, not a mock redesign)

```text
[ Allura: Sassy Closet ]          ← mark; kicker not “INTAKE” on public
[  {ASSIGNED MÃ}  ]               ← 5xl, copy on tap
[ Áo · Đỏ đô · ghi chú ]          ← text
[ gallery hero — current color ]
[ 3 thumbs +N → existing lightbox ]
[ Màu ]
[ Đen ] [ Đỏ đô ] [ Hoa ]         ← text pills, one selected
Đang xem: Đỏ đô
[ Size Á châu ]
[2XS][XS][S][M][L][XL][2XL]      ← disabled where not on this mã
Size Á châu + cm
[ Còn · Available  |  or staged-only / Reserved / Hold / Sold ]
[ Copy mã ] [ Copy caption ]
Inbox mã để lấy nha 💕            ← existing footer idea
```

Motion: color pill → hero crossfade → thumbs replace. Size pill → status line updates. No route change.

---

## 15. Anti-patterns (quick refuse list)

1. Minting `AO00x` “for the red one.”  
2. Showing US 4 / 6 / 8.  
3. Hex circles as the only color UI.  
4. Mixed-color gallery after a color tap.  
5. Stock photos / other-mã photos / generated models.  
6. `held` as one badge for Reserved + Hold + fulfill Hold.  
7. Fake 24h countdown.  
8. Wishlist `#` as a product code.  
9. Translating hub `A12` → `AO012`.  
10. Dropdowns for 7 sizes.  
11. New visual language “to look more premium.”  
12. Checkout that Saves Square.  
13. Inventing cm from a letter.  
14. Treating staged as on-hand.

---

## 16. Acceptance (sell-test)

A reviewer can fail the page against this list without a redesign argument:

- [ ] Every mã on the page was **already assigned**. None match “next Dashboard” math performed in the client.  
- [ ] Customer colors are **words**. No customer-only hue disc.  
- [ ] Changing color changes **this mã’s** gallery; no other folder.  
- [ ] Empty photos = `—` / existing empty, not a placeholder jpeg.  
- [ ] Sizes are exposed letters; cm sheet shows **stored** cm only; no US.  
- [ ] Official Hold ≠ Official Reserved in the copy.  
- [ ] Staged-only sentence is the exact FIND_MA_CARD string when on-hand is empty.  
- [ ] Copy mã copies the displayed code. Caption starter still starts with mã.  
- [ ] Motion is the existing sheet / overlay / short fade; reduced-motion respected.  
- [ ] Fonts, rose, pills, lightbox match intake.  
- [ ] No Square Save, no FB Post.  
- [ ] Sources in §17 still explain every shop-law sentence.

---

## 17. Sources

### 17.1 Shop law and as-built (this repo + Slack)

- `README.md` — Square SoT; Official working copy; mã prefixes; bots draft; Facebook inbox; Cloud Agent rules.  
- `excel-kit/DESIGN_NOTES.md` — layers; `MA_RE`; photo file names; status sets; refuse US sizes; no fake Official rows.  
- `excel-kit/schema.py` — `MA_PREFIXES`, `SOT_OFFICIAL`, measurements, Hold/Reserved, Dashboard `B21:B27`, `OFFICIAL_TO_MA_LIST_STATUS`, `SQUARE_SKU_IS_MA`, `ASK_STOCK_MA`.  
- `excel-kit/square/README.md` — Track ON (Boss yes 2026-09-04); SKU = mã; variation = Asia size + color; unique piece = unique mã.  
- `excel-kit/sot/append_official_row.py` — `--ma` required; size help “Asia size + cm (never US).”  
- `excel-kit/prompts/GF_CLOTHES_INTAKE.md` + `templates/from_gf/HOW_TO_UPLOAD.md` + `INTAKE_TEMPLATE.txt` — no invent mã; Asia + cm; Wishlist mã forbidden.  
- `excel-kit/prompts/BOUTIQUE_PHONE_SAFE.md` — customer-facing fit Asia + cm.  
- `excel-kit/prompts/FIND_MA_CARD_2026-09-08.md` — big mã; staged vs on-hand; never invent qty/$.  
- `sassy-closet/BOSS.md`, `sassy-closet/README.md` — tabs; Blob; lightbox; staged-only.  
- `sassy-closet/lib/kinds.ts` — `SIZES`, `COLORS` (incl. Caro, Hoa, Ánh kim, Khác).  
- `sassy-closet/lib/mint.ts`, `lib/store.ts` — hub alphabet + `nextMa` on create (contrast with Excel).  
- `sassy-closet/lib/types.ts` — `Piece`, `OnHandRow` statuses.  
- `sassy-closet/lib/captions.ts` — mã line 1; inbox footer.  
- `sassy-closet/lib/ask-fallback.ts` — Asian sizes; no US.  
- `sassy-closet/components/{BrandHeader,IntakeApp,FindMaCard,SavedCard,PhotoThumbs,PhotoLightbox}.tsx`, `app/globals.css`, `tailwind.config.ts`, `app/layout.tsx`.  
- Slack `#shop-decisions` (2026-09-04):  
  - [Channel law + Hold-past-24h **example**](https://tien-ota6716.slack.com/archives/C0BV3GYC602/p1788541753903809) — Facebook stays the store; bots read-only until yes/no. The `AO001` / `AO003` strings are **examples in that message**, not a stock dump.  
  - [Track stock ON proposal](https://tien-ota6716.slack.com/archives/C0BV3GYC602/p1788553328521899)  
  - [Boss yes](https://tien-ota6716.slack.com/archives/C0BV3GYC602/p1788553474026779)  
  - [Square LIVE](https://tien-ota6716.slack.com/archives/C0BV3GYC602/p1788556083454949)  
  - [Soft-launch prep, draft only](https://tien-ota6716.slack.com/archives/C0BV3GYC602/p1788557030839509)

### 17.2 UX research

- Nielsen Norman Group, *UX Guidelines for Ecommerce Product Pages* — <https://www.nngroup.com/articles/ecommerce-product-pages/>  
- Nielsen Norman Group, *Product Photos on Listing Pages: 6 Tips* — <https://www.nngroup.com/articles/product-photos-listing-pages/>  
- Baymard, *Always Use “Buttons” for Size Selection* — <https://baymard.com/blog/use-buttons-for-size-selection>  
- Baymard, *Product Page UX Best Practices 2026* — <https://baymard.com/blog/current-state-ecommerce-product-page-ux>  
- Baymard, *Make All Color Swatches Available in Mobile List Items* — <https://baymard.com/blog/mobile-interactive-color-swatches>  
- Baymard, *Mobile UX Trends 2026* — <https://baymard.com/blog/mobile-ux-ecommerce>  
- Baymard, *Combine Variations of Products into One List Item* — <https://baymard.com/blog/combine-variations-one-list-item>  
- Baymard, *Apparel: 10 Best Practices on Sizing* — <https://baymard.com/blog/apparel-size-information>  
- Baymard, *5 Apparel UX Best Practices* — <https://baymard.com/blog/apparel-5-best-practices>  
- Baymard, *Let Users Purchase Temporarily Out of Stock Products* — <https://baymard.com/blog/handling-out-of-stock-products>  
- Baymard, *Highlight Items Already in the User's Cart* (reservation confusion) — <https://baymard.com/blog/highlight-products-if-in-users-cart>

### 17.3 Accessibility

- W3C, WCAG 2.2 Understanding SC 1.4.1 Use of Color — <https://www.w3.org/WAI/WCAG22/Understanding/use-of-color.html>  
- W3C technique G14 (in the same Understanding document).  
- MDN, `radiogroup` — <https://developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA/Reference/Roles/radiogroup_role>

### 17.4 Color vision

- J. Birch, “Worldwide prevalence of red-green color deficiency,” *JOSA A* (2012) — record: <https://www.researchgate.net/publication/223985289_Worldwide_prevalence_of_red-green_color_deficiency>  
- Hasrod et al., *Healthcare* 13(16):2031 (2025) — <https://www.mdpi.com/2227-9032/13/16/2031>  
- *Review of Optometry* summary of a global CVD meta-analysis — <https://www.reviewofoptometry.com/article/study-describes-epidemiology-of-congenital-color-vision-deficiency>

### 17.5 Sizing standards

- ISO 8559-1:2017 — <https://www.iso.org/standard/61686.html>  
- ISO/TC 133 catalogue (8559-2:2025, 8559-3:2018, …) — <https://www.iso.org/committee/52374/x/catalogue/>  
- GB/T 1335.1-2008 (SAMR) — <https://std.samr.gov.cn/gb/search/gbDetailed?id=bJm52CpSOZ0%3D&mode=p>  
- GB/T 1335.1-2008 (openstd) — <https://openstd.samr.gov.cn/bzgk/std/newGbInfo?hcno=EC87D6B2262ABDCFD055989D2C9DCC9F>  
- Secondary explainers (do **not** copy their US columns into the PDP): <https://convertsizes.com/guides/asian-clothing-sizes/>, <https://www.hiredchina.com/articles/asian-sizing-to-american-sizing-guide/>, <https://allchinabuying.com/blog/chinese-clothing-sizing-guide>

### 17.6 Catalog / gallery platforms (defaults to learn from, not to install)

- Square, *Design a Catalog* — <https://developer.squareup.com/docs/catalog-api/design-a-catalog>  
- Square, `CatalogItemVariation` — <https://developer.squareup.com/reference/square/objects/CatalogItemVariation>  
- Square, *Monitor Sold-out Item Variations* — <https://developer.squareup.com/docs/inventory-api/monitor-sold-out-status-on-item-variation>  
- Craftshift, Shopify variant images / gallery grouping / conversion claims — <https://craftshift.com/shopify-variant-images-complete-guide/>, <https://craftshift.com/shopify-image-gallery-grouping-by-variant/>, <https://craftshift.com/shopify-variant-image-swatches-conversion-rates/>  
- Shopify Community, Horizon “hide unselected variant media” limits — <https://community.shopify.com/t/horizon/659928>

### 17.7 Weaker / vendor sources (do not treat as shop law)

Theme-app posts that claim “+65% conversion from more views” or MECLABS 14.6% without a public method note are **directional**. Prefer Baymard / NN/G / WCAG / ISO / GB/T / this repo.

---

## 18. Open questions (do not answer by inventing)

These are **Boss / Stock** questions. A later agent must not fill them with sample mãs or fake cm.

1. Is the public sell-test allowed to show **price**, or caption-only until `#shop-decisions`? (No price in git as live stock.)  
2. Will sell-test rows use the **Official** alphabet, the **hub** alphabet, or only rows that exist in **both** without translation?  
3. Is Official **Hold** ever a **customer** hold (inbox, 24h) or only a back-room park? Slack example is an **ask**, not a standing public policy.  
4. Per unique-piece law, will one Square **item** ever have two variations with **two** mãs, or always one variation per mã?  
5. Who measures `bust_chest` / `waist` / `length` — garment flat or on body — and will that label appear in the cm sheet?  
6. After Granola/Notion access exists: did a meeting already pick text-only for customers? This file treats the user prompt’s APPLY line as the standing sell-test instruction.

---

## 19. One-page APPLY card (tear-off)

```text
SELL-TEST PDP — Sassy Closet
Admin:  named pills + optional hue hint + photos per color (pieces[])
Customer: TEXT color pills → filter gallery (this mã only)
Size: 2XS–2XL buttons + cm sheet (stored cm only). NO US.
Hold: Reserved ≠ Hold ≠ Orders Reserved ≠ fulfill Hold
Mã: assigned only, huge, copyable, never translated, never minted
Look: rose / Allura / Nunito / sheets / lightbox. Keep that motion.
Truth: Square on-hand or “Staged only — not on Square On_Hand yet”
Store: Facebook inbox. Bots draft. No Save. No Post.
```

End of 02.
