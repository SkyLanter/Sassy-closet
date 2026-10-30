# 09 — Bugcheck sell-site checklist

**Learn track:** Ultra burn (QA, not a rebuild).  
**Shop under test:** [https://sassy-closet-shop.vercel.app](https://sassy-closet-shop.vercel.app) — sell-test lookbook, Origin-owned.  
**Audience:** Mini Boss / Stock / whoever bugs the sell-site before Boss flips soft-launch.  
**Date crawled:** 2026-09-09 (headers + HTML of `/`, `/c/*`, `/m/{MA}`, `/admin`).  
**This file does not assign stock, mint a mã, Save in Square, post to Facebook, or redesign the boutique.**

---

## 0. How to read this document

This is a **print-and-tick QA book** for an AI-built Taobao-dropship clothing boutique **sell-site**. Sister notes (`01`–`07`) explain *why*. This note says *what to click* and *what “pass” means* on the live chrome.

- **Cite, don’t invent.** Every shop-law claim points at a file, Slack channel, or public standard. Every “live pattern” claim was observed on the sell-test host on 2026-09-09 or is labeled **as-built gap**. Industry claims point at NN/G, W3C WCAG 2.2, Google Search Central, Meta Messenger docs, Open Graph, or Vercel ISR/Blob docs. If a fact is missing, the gap is named.
- **Never invent a mã.** The only customer-facing codes this pass may use are the **first-ten allowlist**. Admin “Next mã” tiles are **predictions**, not products. Slack’s `AO001` / `AO003` lines are **decision-template examples** from `#shop-decisions` (2026-09-04), not proof those pieces exist on the shop or in Square.
- **Two alphabets.** Sell-site / hub display = letter + 2–3 digits (`A01`). Official / Square / SoT = `AO` / `QU` / `VA` / `AK` / `GI` / `PK` / `SET` + three digits (`AO001`). Do not translate one into the other on a tile, caption, or test account. See `excel-kit/schema.py` `MA_RE`; `sassy-closet/lib/mint.ts`; `excel-kit/docs/SELL_CATALOG_CONTRACT.md` (PR #18).
- **Facebook inbox is still the store** until Boss changes that in `#shop-decisions`. A “buy” on this site is **Message {code}**. There is no cart. NN/G’s “add to cart” maps to inbox, not Shopify checkout ([NN/G, *UX Guidelines for Ecommerce Product Pages*](https://www.nngroup.com/articles/ecommerce-product-pages/)).
- **No redesign mandate.** Motion language to keep: paper / ink / gold / blush, Be Vietnam Pro + Cormorant Garamond, `ma-mark`, `shimmer`, `announce-fade`, `cta-shine`, `view-transition-name: site-header` / `product-{MA}`, hover lift + 1.08 scale, gold underline. Improve *inside* that look. Do not replace it with Horizon / Shopify / a new design system (`01` §11; `07` §11.0).

### 0.1 Research method (and what this pass could not see)

| Source | Result |
| --- | --- |
| Live sell-test HTML + `curl -I` of `/`, `/c/ao`, `/c/set`, `/c/phu-kien`, `/c/ao-khoac`, `/c/toc`, `/c/quan`, `/c/giay`, `/c/tui`, `/c/vay`, `/c/dam`, `/c/trang-suc`, `/c/khac`, `/m/A01`, `/m/A02`, `/m/S01`, `/m/P01`–`/m/P05`, `/m/K01`, `/m/H01`, `/m/a01`, `/m/MISSING`, `/admin`, `/robots.txt`, `/sitemap.xml`, `/products/{MA}/cover.jpg`, `/editorial/*` | Read 2026-09-09. Primary **as-built** map. |
| Repo `excel-kit/`, `sassy-closet/`, `README.md` | Read. Primary shop law. Sell-site **app source is Origin-owned** — not in this repo. |
| Slack `#shop-decisions` (`C0BV3GYC602`) | Five standing messages (2026-09-04). Cited below. |
| Sister LEARN TRACK PRs #19–#25 | Headings + APPLY excerpts. This file is `09`. |
| Linear | No sell-site QA issue found this pass. |
| Granola meetings | MCP unauthorized — no meeting notes. |
| Notion | No Sassy Closet QA page. |
| Public a11y / SEO / Messenger / ISR docs | URLs in §19. |

If a later crawl disagrees with a **live** cell in this book, **the new crawl wins** — update the date line. Shop law still wins over industry taste.

### 0.2 Sister docs

| # | File | Job vs this checklist |
| --- | --- | --- |
| 01 | `01-messenger-social-commerce.md` | Why Message-first; Hold vs Reserved; `m.me` prefill APPLY |
| 02 | `02-pdp-color-size-ux.md` | Customer **text** colors; gallery sync; Asia size + cm |
| 03 | `03-tiny-boutique-admin.md` | Add / Edit / rename / status / Blob brains |
| 04 | `04-next-blob-catalog-arch.md` | ISR, three Blobs, `catalog.v1`, `/m/A03` must 404 |
| 05 | `05-ai-product-media.md` | Per-color attach; HQ folder law; no invented binds |
| 06 | `06-seo-trust-diaspora-boutique.md` | `noindex` / OG / bilingual SEO (go-live vs soft-launch) |
| 07 | `07-taobao-dropship-boutique.md` | 现货 vs 预售; `source_link` stays staff-only |
| 08 | *(ops runbook — land when that PR exists)* | Staff clock; do not wait on it to run §5–§14 |
| **09** | **This file** | **Tick-box QA mapped to live chrome** |
| Kit | `excel-kit/docs/SELL_CATALOG_CONTRACT.md` (PR #18) | Allowlist + prices + Hold null `$` |

Readable alone. When APPLY docs disagree with live HTML, **record both** (law vs as-built). Do not “fix” the shop from this repo (`SELL_CATALOG_CONTRACT.md`: *Do not modify Origin shop app code from this repo*).

### 0.3 Severity (how to fail a row)

| Sev | Meaning | Example |
| --- | --- | --- |
| **Blocker** | Ships a lie or a law break | Invented mã; P05 shows `$23`; Available tile with no `$` *or* Hold tile with a `$`; Blob wipe after redeploy; cart / Square Save / FB Send from the site |
| **Major** | Buyer or admin cannot finish the intended job | Save does not persist; Message CTA 404s the Page; gallery ignores selected text color; keyboard trap; contrast fail on price |
| **Minor** | Polish / empty-collection / motion / SEO-when-still-private | `/c/quan` empty copy; hover scale with `prefers-reduced-motion`; missing `og:image` **while** Boss still wants `noindex` |
| **Note** | As-built observation. Not a fail until Boss APPLY says so | Soft-launch `noindex, nofollow` is **correct today** (`01` §11.6; `04` §11). It becomes a fail only after Boss says *index*. |

Mark each row `P` / `F` / `N/A` / `BLOCKED` (need Boss yes). `N/A` is allowed when the feature is **absent and the absence is the law** (no cart, no US size, no 11th mã).

### 0.4 Fixtures — the only mãs you may type

**Customer / public surfaces** — first ten only (`SELL_CATALOG_CONTRACT.md`; live Featured Board payload 2026-09-09):

| Mã | Type (live EN) | USD | Status (live) | Cover | PDP |
| --- | --- | --- | --- | --- | --- |
| `A01` | Top | $25 | Available | `/products/A01/cover.jpg` | `/m/A01` |
| `S01` | Set | $28 | Available | `/products/S01/cover.jpg` | `/m/S01` |
| `P01` | Accessory | $5 | Available | `/products/P01/cover.jpg` | `/m/P01` |
| `P02` | Thermos | — | **Hold** · Inbox for price | `/products/P02/cover.jpg` | `/m/P02` |
| `P03` | Accessory | $18 | Available | `/products/P03/cover.jpg` | `/m/P03` |
| `P04` | Accessory | $13 | Available | `/products/P04/cover.jpg` | `/m/P04` |
| `P05` | Thermos | — | **Hold** · Inbox for price | `/products/P05/cover.jpg` | `/m/P05` |
| `K01` | Jacket | $37 | Available | `/products/K01/cover.jpg` | `/m/K01` |
| `H01` | Hair | $8 | Available | `/products/H01/cover.jpg` | `/m/H01` |
| `A02` | Top | $22 | Available | `/products/A02/cover.jpg` | `/m/A02` |

`P02` / `P05` stay Hold even if an xlsx cell shows a number (contract: P05 `23` on All — **do not publish it**). Empty `sell_usd` → Hold. `qty` is always `1` on `catalog.v1`.

**Admin Next-mã tiles (2026-09-09, not products):** `A03` Tops · `Q01` Pants · `V01` Skirts · `K02` Jackets · `G01` Shoes · `B01` Bags · `P06` Accessories · `H02` Hair · `J01` Jewelry · `S02` Sets · `O01` Other · `D01` Dresses. These codes **must 404** on `/m/{tile}` until Boss + Stock assign them (`04` §11: `/m/A03` is 404). **Do not Add them in a QA pass** unless Boss typed **yes** in `#shop-decisions` for a throwaway sell-test row — and then leave the new row on Hold and revert.

**Refuse these in any test account, caption, or URL:** `AO001`, `AO015`, `AO999`, `A99`, `A04`, `P07`, `SET001`, `#001`, or any code not in the two tables above. Demo tokens are stripped by `excel-kit/clean_sot_demo.py`; do not reintroduce them.

**Throwaway edit rule.** Prefer **read-only** checks on the ten. If you must Save, edit a **description space** or a Hold note on sell-test only, then put the original copy back. Never upload a photo you do not have. Never invent hex, `$`, or a second mã.

---

## 1. Executive summary

The sell-test is a **Next.js lookbook** (ISR, `x-nextjs-prerender: 1`, `x-nextjs-stale-time: 300`) with a hidden `/admin` that claims **Storage: Vercel Blob**. Buyers see ten unique pieces, **Available** or **Hold**, and a Messenger CTA to Facebook Page `id=61594312648057`. There is **no cart**, **no Stripe**, **no Square Online**. Footer: `Zelle · Message on Messenger`. Announcement bar: `Facebook livestream`.

A boutique QA pass is not “does Add to cart work.” It is:

1. **Identity** — the code on the tile is the code in the inbox and the code in Blob. Never a translated Official `AO…`. Never a minted 11th SKU.
2. **Persist** — Save on `/admin` survives refresh **and** Production redeploy (Blob, not `/tmp`). ISR must not serve yesterday’s Hold/`$` (`04` §7).
3. **Color honesty** — admin may tag photos with a hue box; **customers read color as text** and the gallery follows that text (`02` §7; WCAG 2.2 SC [1.4.1](https://www.w3.org/WAI/WCAG22/Understanding/use-of-color)). Live 2026-09-09: all ten `colors: []` — empty is honest; a fake swatch is not.
4. **Hold / Message-first** — Hold tiles say **Inbox for price** and carry **no USD**. Available tiles carry the Boss `$` and `Message {MA}`. CTA starts a message, not a checkout (`01` §7).
5. **Phone + a11y + SEO** — two-column grid, sticky header, `viewport-fit=cover`, `prefers-reduced-motion` already kills shimmer / announce / view-transitions. Soft-launch stays `noindex, nofollow` until Boss says index (`06` vs `01`).

If you only have twenty minutes, run **§20 tear-off**. If you are signing a soft-launch, run **§5–§14** in order and file the log in §17.

---

## 2. Hard constraints (print these on the tester’s wall)

1. **Never invent a mã.** Stock reads Dashboard `B21:B27`. Scripts require `--ma` or print ASK STOCK (`excel-kit/schema.py`; `excel-kit/DESIGN_NOTES.md`). Sold mã stays retired. Unique piece = unique mã.
2. **Never invent qty, `$`, storage, photos, or hex.** Empty = `—` / Hold / Inbox for price / **Staged only — not on Square On_Hand yet** (`excel-kit/prompts/FIND_MA_CARD_2026-09-08.md`; `sassy-closet/lib/on-hand.ts`).
3. **Square Free = on-hand SoT.** Official Excel is a working copy. Sell JSON is a **lookbook**, `qty=1` = “this unique piece,” not a cycle count (`README.md`; `07` §5.2).
4. **Bots / agents / this site draft only.** No Square Save, no Facebook Post/Send, no Zelle from the app (`README.md`; Slack `#shop-decisions` 2026-09-04).
5. **Customer-facing fit = Asia size + cm. Never quote US sizes** (`excel-kit/DESIGN_NOTES.md` “What we refuse to ship”).
6. **Track stock ON** for every item **and** variation — Boss **yes** 2026-09-04. That is Square later, not a site toggle.
7. **Do not treat Wishlist / staged as for-sale stock.** Wishlist mã is forbidden (`excel-kit/prompts/GF_CLOTHES_INTAKE.md`).
8. **Do not publish `cost`, Taobao `source_link`, customer names, or a personal Zelle name** (`SELL_CATALOG_CONTRACT.md`; `06` §8).
9. **Do not share Blobs** across intake (`sassy-closet.vercel.app`), sell-test, and official (`04` §8).
10. **Admin is test-only and off the main nav.** A gold-dot “Shop tools” control is the staff door. Do not advertise `/admin` on the lookbook.

---

## 3. As-built map (cite the live host, don’t redesign it)

Crawled 2026-09-09. Origin app — this repo does not contain these files.

### 3.1 Routes

| Pattern | Live job | 2026-09-09 |
| --- | --- | --- |
| `/` | Home: announce + hero `/editorial/hero.jpg` + 5 collection tiles + Featured Board | 200, ISR, `x-matched-path: /` |
| `/c/ao` `/c/set` `/c/phu-kien` `/c/ao-khoac` `/c/toc` | Category grids for types that have tiles | 200; titles `Tops · Sassy Closet` etc. |
| `/c/quan` `/c/giay` `/c/tui` `/c/vay` `/c/dam` `/c/trang-suc` `/c/khac` | Empty letter collections | 200, `Nothing in this collection yet.` `x-matched-path: /c/[slug]` |
| `/c/a` `/c/tops` | English / short junk | **404** |
| `/m/{MA}` | PDP | 200 for the ten; `x-matched-path: /m/A01` (prerender) |
| `/m/a01` | Case fold | **200** same title as `A01` (not a 308) — SEO gap in `06` P0.7 |
| `/m/A01/` | Trailing slash | **308** → `/m/A01` |
| `/m/MISSING` | Unknown code | **404**, `x-matched-path: /m/[ma]`, “Not found” + Back to shop |
| `/admin` | Staff editor | 200, `cache-control: private, no-cache, no-store`, **not** in header nav |
| `/robots.txt` `/sitemap.xml` `/opengraph-image` `/twitter-image` | SEO files | **404** (HTML not-found chrome) |
| `/products/{MA}/cover.jpg` | Public cover | **200** `image/jpeg` for the ten |
| `/products/A01/001.jpg` | HQ filename on the CDN | **404** — OD `001.jpg` is **not** this URL (`05` §6) |
| `/api/*` (guessed catalog/admin paths) | Public JSON | **404** — do not assume a public catalog API |

### 3.2 Chrome (keep)

- `html lang="en"` · fonts: `--font-be-vietnam` + `--font-cormorant` · tokens `--paper #fff --ink #111 --muted #6b6b6b --gold #b08968 --blush #f3eee8`.
- Sticky header: wordmark → `/` · **Messenger** → `https://www.facebook.com/profile.php?id=61594312648057` (`target=_blank` `rel=noopener noreferrer` `aria-label="Message on Messenger"`).
- Category nav `aria-label="Categories"`: Tops `/c/ao` · Sets `/c/set` · Accessories `/c/phu-kien` · Jackets `/c/ao-khoac` · Hair `/c/toc`. Letters present on home payload: `types: ["A","S","P","K","H"]` — empty kinds stay **off** the header.
- Featured filters: `role="tablist"` `aria-label="Filter featured collection"` · All **10** · Tops **2** · Sets **1** · Accessories **5** · Jackets **1** · Hair **1**.
- Card: `view-transition-name: product-{MA}` · `shimmer` overlay · hover `-translate-y-1.5` + `scale-[1.08]` + gold underline · badge `sr-only` “Status: ” + Available (ink) or Hold (gold) · `ma-mark` + kind · `$` or **Inbox for price** · `Message to buy`.
- Footer: `Sassy Closet · Zelle · Message on Messenger` + ghost CTA.
- Fixed `aria-label="Shop tools"` gold dot (bottom-right) — staff door, not a cart.
- 404: `h1` “Not found” · `Back to shop` → `/`.

### 3.3 PDP skeleton (`/m/A01`, `/m/P02`)

Available (`A01`): breadcrumb `Tops / A01` · `h1` **A01** + **TOP** · `Status: Available` · `$25` · `1 piece · Message to buy. No cart.` · EN *“One unique top on hand. Message A01 for real photos and size.”* · VN *“Áo độc bản — một chiếc đang có.”* · CTA **Message A01 →** · related `A02` · second CTA.

Hold (`P02`): breadcrumb `Accessories / P02` · **P02 THERMOS** · `Status: Hold` · **Inbox for price** · *“Hold · Inbox for price. Message to buy — photo-check, no USD yet.”* · EN *“Thermos on Hold (photo-check). No USD sell price yet — inbox for price.”* · VN *“Bình giữ nhiệt đang Hold — kiểm tra ảnh.”* · CTA **Message to buy →** (code not always in the Hold verb — check `01` APPLY) · related `P01` `P03` `P04` `P05`.

No Open Graph. No JSON-LD. No `m.me` / `text=` prefill (bare profile). No customer color row when `colors: []`. No lightbox string in A01 HTML this crawl (single `cover.jpg`).

### 3.4 Admin skeleton (`/admin`)

Visible copy: **Admin · Sassy Closet** · **Test only · not in the main nav** · **Open sell-test editor. Edit English titles and bilingual descriptions, prices, Hold / Inbox for price, and images. New items get the next unused mã for the letter you pick.** · **Storage: Vercel Blob**.

**Add item:** *New items start on Hold. Type comes from the letter. Qty is always 1. Each tile shows the next unused mã.* Letter tiles (see §0.4). Fields: Status (Hold · Inbox for price / Available) · Price USD · Title EN / VN · Description EN / VN flavor · Colors (*Boxes only — no names on the swatches. Optional note is admin-only.* · **Add hex**) · Images (tag color · Remove · Add URL · Upload image) · **Add {next}**.

**Catalog (10):** one editor per allowlist mã · **Save {MA}**.

**Rename control:** **not present** in the 2026-09-09 visible tree. Intake rename lives on `sassy-closet` Sửa (`03` §6.2), not here.

**Image alts on admin thumbs:** empty `alt=""` this crawl.

### 3.5 Three hosts (do not cross-wire)

| Host | Job | Blob |
| --- | --- | --- |
| `https://sassy-closet.vercel.app` | Intake: Món mới / Sửa / Tìm mã / Ask | Intake Blob (`sassy-closet/store.json`) |
| `https://sassy-closet-shop.vercel.app` | Sell-test lookbook + `/admin` | Sell-test Blob (admin label) |
| Official shop (not this crawl) | Future public | **Third** Blob (`04` §8) |

QA on the wrong host is a failed pass.

---

## 4. How to run a pass

### 4.1 Environments

| Surface | URL | Notes |
| --- | --- | --- |
| Customer desktop | 1280×800 and 1440×900 | Hover motion exists (`@media (hover:hover)`) |
| Customer phone | 390×844 and 360×740 | `grid-cols-2`, `overflow-x-auto` nav, `viewport-fit=cover` |
| Prefers-reduced-motion | OS setting on | CSS already zeros `announce-fade`, `shimmer`, `cta-shine`, view-transition animations |
| Staff | `/admin` via Shop tools | Confirm you are on **sell-test**, not intake |
| Headers | `curl -sI` | Record `x-vercel-cache` (`HIT`/`STALE`/`MISS`), `x-nextjs-prerender`, `cache-control` |

### 4.2 Tools (enough)

Browser + phone. `curl -sI` / View Source for meta. Contrast: browser DevTools or [WebAIM Contrast Checker](https://webaim.org/resources/contrastchecker/). Keyboard only. Screen reader **one** PDP (VoiceOver / TalkBack) if you have it — otherwise keyboard + zoom 200%. Facebook Sharing Debugger **only after** Boss wants OG (`06` P0.10).

Do **not** need Square login, OneDrive write, or a new mã to finish a read-only pass.

### 4.3 Order

1. §5 identity (10 minutes, read-only).  
2. §10 Hold + Message (15 minutes).  
3. §7 Blob / ISR **if** Boss allows one Save + revert (20 minutes).  
4. §6 admin Add/Edit/rename (Add only with Boss yes).  
5. §8–§9 color + gallery (skip invented binds; use empty + one tagged photo if already on a row).  
6. §11–§13 mobile / a11y / SEO.  
7. §14 IA + 404s.  
8. File §17.

---

## 5. QC-LAW — identity / never invent mã

| ID | Check | Live map | Pass | Fail | Sev | Cite |
| --- | --- | --- | --- | --- | --- | --- |
| LAW-01 | Featured All count is **10** | `/` tab All `10` · `10 pieces` | Count = 10 and the ten codes in §0.4 | 11th tile, duplicate, or missing allowlist mã | Blocker | PR #18 allowlist; home payload |
| LAW-02 | Every public tile code ∈ allowlist | Cards `/m/A01`…`/m/A02` | Exact set | Any `A03`, `Q01`, `AO001`, demo `AO999` | Blocker | Contract; `clean_sot_demo.py` |
| LAW-03 | Display alphabet is A01-style, not Official | `ma-mark` on cards + PDP `h1` | `A01` not `AO001` | Auto-translated Official code on a tile | Blocker | `02` §4.3; `03` §3.1 |
| LAW-04 | Kind letter matches type chrome | `A`→Top/`/c/ao`; `S`→Set; `P`→Accessory or Thermos; `K`→Jacket; `H`→Hair | Letter, nav, badge, title agree | `A01` under Jackets; `P02` typed as Top | Blocker | Contract type map; `07` §5 |
| LAW-05 | Unknown `/m/{junk}` is 404 | `/m/MISSING` | 404 + Not found + Back to shop | 200 empty PDP or a guessed product | Blocker | Live 404; `04` §7.7 |
| LAW-06 | Admin next tiles are **not** public | `/m/A03` `/m/Q01` `/m/P06` `/m/D01` | 404 | Public PDP for an unused tile | Blocker | Admin “Next mã”; `04` §11 |
| LAW-07 | No `$` invented on Hold | `/` + `/m/P02` + `/m/P05` | “Inbox for price”, no number | `$23` or any USD on Hold | Blocker | Contract P05 note; `01` §3.6 |
| LAW-08 | Available `$` match Boss table | A01 25 · S01 28 · P01 5 · P03 18 · P04 13 · K01 37 · H01 8 · A02 22 | Exact | Off-by-one, ¥, or blank Available | Blocker | Contract table; home payload `priceUsd` |
| LAW-09 | `qty` story is “1 piece” not warehouse | PDP `1 piece · Message to buy. No cart.` | That sentence (or equivalent) | “In stock 12”, backorder, US warehouse | Major | `07` §5.2; live A01 |
| LAW-10 | Cost / Taobao / names absent | View Source + admin fields customer-side | No `e.tb.cn`, no vốn, no personal name | Source link or cost on `/m/*` | Blocker | Contract omit list; `07` §6 |
| LAW-11 | Intake host is a different site | Open `sassy-closet.vercel.app` | Four staff tabs, `INTAKE` chrome | Sell-test nav on intake or vice versa | Blocker | `sassy-closet/BOSS.md`; `04` §3 |
| LAW-12 | Test never types a new code | Tester notes | Only §0.4 codes in URLs / forms | Tester-created `A99` | Blocker | This file §0.4 |

---

## 6. QC-ADM — admin Add / Edit / rename

Run on [https://sassy-closet-shop.vercel.app/admin](https://sassy-closet-shop.vercel.app/admin). Confirm the gold-dot **Shop tools** reaches the same page. Do not bookmark-share admin in a customer caption.

### 6.1 Door and chrome

| ID | Check | Live map | Pass | Fail | Sev | Cite |
| --- | --- | --- | --- | --- | --- | --- |
| ADM-01 | `/admin` is **not** in category nav | Header links | Only `/`, Messenger, `/c/*` | “Admin” in customer nav | Major | Copy: *Test only · not in the main nav* |
| ADM-02 | Shop tools is findable by staff, not a cart | `aria-label="Shop tools"` gold dot | Opens admin or a staff sheet | Opens checkout / Messenger | Major | Home HTML |
| ADM-03 | Admin `cache-control` is private | `curl -sI /admin` | `private, no-cache, no-store` | Public CDN cache of the editor | Major | Live headers; `04` §7 |
| ADM-04 | Storage line reads Blob when durable | Admin “Storage: Vercel Blob” | Exact durable label | “local” / `/tmp` / empty on Production | Blocker | Admin copy; `sassy-closet/README.md` Durable store (same *idea*) |
| ADM-05 | Catalog count = 10 | `Catalog (10)` | 10 editors, allowlist order | Extra / missing card | Blocker | Live admin |

### 6.2 Add (create)

Live copy: *New items start on Hold. Type comes from the letter. Qty is always 1. Each tile shows the next unused mã.*

| ID | Check | Live map | Pass | Fail | Sev | Cite |
| --- | --- | --- | --- | --- | --- | --- |
| ADM-06 | Next-mã tiles match unused letters | Tiles A03…D01 | Prediction = max(existing)+1 per letter; **no public PDP** | Tile shows `A01` or a used code | Blocker | Admin; `mint.nextMa` *pattern* on intake |
| ADM-07 | Type is letter-locked | Pick `K` tile | Kind = Jacket; cannot type “Top” onto `K02` | Free-typed type that disagrees with letter | Major | Admin: *Type comes from the letter* |
| ADM-08 | New row starts Hold | Add form default | Status = Hold · Inbox for price; Price empty/disabled-until-Available | New row publishes `$` immediately | Blocker | Admin: *New items start on Hold* |
| ADM-09 | Qty cannot become 2 | Add form | Always 1; no stepper to 12 | Multi-qty warehouse field | Major | Contract `qty` always 1 |
| ADM-10 | Add without Boss yes is **out of scope** | This checklist | Row marked N/A | Tester minted `A03` “to see” | Blocker | `#shop-decisions`; `03` §4.4 |
| ADM-11 | If Boss **yes** on a throwaway Add | Use **only** the printed tile (e.g. `A03`) | Code = tile; starts Hold; `/m/{that}` after Save + revalidate; then revert / keep Hold | Tester typed a different code; Available `$` invented | Blocker | `03` §4; `04` §7.6 |
| ADM-12 | Duplicate Add refused | Try Add when tile still shows the same next code after a create | 409 / “đã có rồi” / tile advanced | Two rows same mã | Blocker | Intake `maExists` / `03` §11.3 |
| ADM-13 | Empty titles do not invent SEO copy | Add with blank Title EN/VN | Blanks stay blank or kind label only | Autofilled “Sexy Summer Top 2026” | Major | Contract: do not invent shop copy |
| ADM-14 | Add does not write Official / Square | After Add | SoT / Square unchanged | Silent Square Save | Blocker | `README.md`; Slack 2026-09-04 |

### 6.3 Edit (same identity)

Use **Save A01** (or another allowlist **Save {MA}**). Prefer a reversible description tweak on sell-test.

| ID | Check | Live map | Pass | Fail | Sev | Cite |
| --- | --- | --- | --- | --- | --- | --- |
| ADM-15 | Save keeps the same mã | Catalog card `A01 · Top · $25` + **Save A01** | URL / identity unchanged | Save minting `A03` or renaming silently | Blocker | `03` §5 |
| ADM-16 | Bilingual fields persist independently | Title EN/VN, Desc EN / VN flavor | Each string returns after reload | VN overwritten by EN or vice versa | Major | Admin labels; `06` §4 |
| ADM-17 | Available requires a Boss `$` | Toggle Available on a row that has `$` | `$` shows on `/` and `/m/{MA}` | Available + blank price | Blocker | Contract; `01` §3 |
| ADM-18 | Hold clears public `$` | Toggle P02 / P05 Hold | Inbox for price everywhere | Hold + `$18` | Blocker | Live P02; contract |
| ADM-19 | Cannot type a new `$` on Hold “to test” | P05 | Still no USD | Publishing xlsx `23` | Blocker | Contract P05 |
| ADM-20 | Description edits do not invent size/US | EN/VN boxes | No “US 4 / S” | US size in customer copy | Major | `DESIGN_NOTES.md` refuse |
| ADM-21 | Save is **visible** (no silent success) | Save A01 | Toast / disabled / error | Spinner then old text | Major | `03` §11.1; `07` §10.3 |
| ADM-22 | Failed Save does not half-write | Pull network, Save | Error; old values remain | Title saved, photos gone | Major | `03` §11.1 |
| ADM-23 | Customer surfaces refresh after Save | `/`, `/c/ao`, `/m/A01` hard refresh | New copy/status | ISR stale > 5–10 min with no path to bust | Major | `04` §7.4–7.5; `x-nextjs-stale-time: 300` |
| ADM-24 | Edit cannot attach another mã’s folder | Images on A01 | Only A01 bytes / URLs | Thumb from `/products/S01/cover.jpg` labeled A01 | Blocker | `02` §6; `05` §5 |

### 6.4 Rename (identity change)

Intake has **Đổi mã · Change code** (`03` §6.2). Sell-test admin **did not show a rename control** on 2026-09-09.

| ID | Check | Live map | Pass | Fail | Sev | Cite |
| --- | --- | --- | --- | --- | --- | --- |
| ADM-25 | Document presence | `/admin` visible tree | Either: no rename (report **Note**) **or** an explicit “Change code” | Hidden rename that mints | Major | This crawl; `03` §6 |
| ADM-26 | If rename exists: new code is Boss-assigned + free | — | New code ∈ Stock assignment; 409 if taken | Accepts `A99` / `AO001` / in-use `S01` | Blocker | `03` §6.1 |
| ADM-27 | If rename exists: metadata **and** bytes move | Photos under old/new | New `/m/{new}` 200; old 404 or honest redirect; no 404 thumbs | New mã, old photos 404, tester uploads invented jpg | Blocker | `03` §6.2 photo caveat |
| ADM-28 | If rename exists: do not leave two live SKUs | Allowlist | One public tile | `A01` and `A03` both selling the same top | Blocker | `03` §6.1 |
| ADM-29 | Testers do **not** invent a rename API | — | N/A if no UI | POST guessed `/api/rename` | Blocker | Live `/api/*` 404 |

---

## 7. QC-BLOB — persist, ISR, isolation

Intake lesson (PR #15): Vercel `/tmp` dies on Production redeploy; **one Blob holds JSON + bytes**; verify Lưu → Redeploy → mã still there (`sassy-closet/README.md`). Sell-test admin already prints **Vercel Blob**. Same drill, **different store**.

| ID | Check | Live map | Pass | Fail | Sev | Cite |
| --- | --- | --- | --- | --- | --- | --- |
| BLOB-01 | Production is durable | Admin Storage line + env **names** only (`BLOB_READ_WRITE_TOKEN` / `BLOB_STORE_ID`) | Durable | Ephemeral `/tmp` | Blocker | `KIT.md`; intake README |
| BLOB-02 | Save → hard refresh `/admin` | Edit A01 desc, Save, reload | Text still there | Reverts to seed | Blocker | `03` §8 |
| BLOB-03 | Save → customer hard refresh | `/m/A01` | Same text/status | Admin new, PDP old with no bust | Major | `04` §7 |
| BLOB-04 | Redeploy drill (Boss window) | Vercel → Production → Redeploy | Same 10 mãs; covers 200 | Export 0 / cover 404 | Blocker | Intake verify steps; `04` §11 |
| BLOB-05 | Preview ≠ Production leak | A Preview deploy | Preview Blob or read-only; not wiping Production | Preview write empties prod | Blocker | `04` §8 |
| BLOB-06 | Intake Blob ≠ shop Blob | Intake `/admin` “Kho” vs shop Storage | Different stores | Shared token / copied `store.json` | Blocker | `04` §8.4 |
| BLOB-07 | Photo URLs stay shop-shaped | Covers `/products/{MA}/cover.jpg` | 200 jpeg | Raw `blob:` or signed URL in customer HTML | Major | Contract: do not invent Blob URLs in JSON |
| BLOB-08 | ISR understood, not feared | `curl -I /` `/m/A01` | Record HIT/STALE/MISS + stale-time 300 | Assuming “Save = instant global HTML” with no revalidate | Note | `x-nextjs-stale-time: 300`; `04` §7.1 |
| BLOB-09 | Cached 404 does not trap a later real mã | `/m/MISSING` 404 now | A future Boss-assigned code is not stuck 404 | `generateStaticParams` invented codes **or** cached 404 forever | Major | `04` §7.6–7.7 |
| BLOB-10 | Failed regenerate keeps last **good** page | Kill Blob mid-revalidate (only if safe) | Old good PDP | Blank shop | Major | `04` §7.5 |
| BLOB-11 | No public dump of the catalog | Guessed `/api/catalog` etc. | 404 / auth | World-readable JSON with cost | Major | This crawl 404; contract omit |
| BLOB-12 | Restore does not invent photos | Intake restore story | Re-upload **real** files or migrate leftover `data/` | “placeholder.jpg” invented | Blocker | Intake README restore; `05` |

---

## 8. QC-COL — color photos (admin)

Live 2026-09-09: every product `colors: []`, each `images: [{ src: "/products/{MA}/cover.jpg", colorId: null }]`. OD HQ files exist (`001.jpg` / `001.jpeg` …) but **`/products/A01/001.jpg` 404s**. Admin: *Boxes only — no names on the swatches. Optional note is admin-only. Add hex.* Image: *Add a color above to tag this image.*

Do **not** invent a color name or hex to “complete” the catalog. If a row is still empty, empty is the pass.

| ID | Check | Live map | Pass | Fail | Sev | Cite |
| --- | --- | --- | --- | --- | --- | --- |
| COL-01 | Empty colors are honest | Home payload `colors: []` | No fake “Black / White” chips on the PDP | Invented Kem/Đen on A01 | Blocker | Payload; `05` §3.2 |
| COL-02 | Cover ≠ HQ filename | `/products/A01/cover.jpg` 200; `/products/A01/001.jpg` 404 | Testers don’t report 001 as a shop bug *unless* admin claimed that URL | Linking customer to OD paths | Note | `05` §6.1; contract photo table |
| COL-03 | Admin hex is staff-only | Color help text | Customer PDP does not show unnamed circles as the *only* cue | Customer hue-only dots | Major | Admin copy; `02` §7; WCAG 1.4.1 |
| COL-04 | Admin note stays admin | “Optional note is admin-only” | Note not in `/m/A01` HTML | Staff shade note published | Major | Admin copy; contract `flag` omit |
| COL-05 | Tag image requires a color that exists on **this** mã | “Add a color above to tag this image” | Cannot tag S01’s cover onto A01 | Cross-mã tag | Blocker | `02` §6.2; `05` §5 |
| COL-06 | Add URL / Upload write this mã only | Images on P03 | Bytes land under P03 | Upload silently on P04 | Blocker | Admin per-card Save |
| COL-07 | Remove does not delete another mã | Remove on P01 | P02 cover still 200 | Cascade delete | Blocker | `05` §5.2 |
| COL-08 | Do not invent hex | Add hex | Only if the garment’s recorded color exists in hub/xlsx | `#ff69b4` “for pretty” | Blocker | Contract: no invented hex; `kinds.ts` names |
| COL-09 | Pattern colors cannot be a circle | Caro / Hoa / Ánh kim / Khác (`kinds.ts`) | Text name on customer; admin may keep a box **plus** name | Circle-only “Caro” | Major | `02` §5.3; `kinds.ts` COLORS |
| COL-10 | AI / Higgsfield derivatives tagged | If used | Not presented as the real garment | Fake try-on as cover | Blocker | `05` §4 |
| COL-11 | One color ≠ new mã | — | Extra photo, same `A01` | New `A03` “for the other color” | Blocker | `05` §3.1 |
| COL-12 | Admin thumbs have usable alt **or** are decorative | Admin `alt=""` today | Decorative `alt=""` OK **if** mã is in the heading; else `alt="A01 cover"` | Empty alt + no nearby text | Minor | WCAG [1.1.1](https://www.w3.org/WAI/WCAG22/Understanding/non-text-content.html); live empty alts |

---

## 9. QC-PDP — customer text colors + gallery motion

APPLY (`02` §13; `07` §7): **admin swatches + per-color photos; customer TEXT-ONLY colors drive the gallery; keep boutique motion.**

Live: no customer color row (empty arrays). Motion **is** present (shimmer, hover scale, view-transition, announce-fade). Reduced-motion CSS **is** present.

### 9.1 When `colors` is empty (today)

| ID | Check | Live map | Pass | Fail | Sev | Cite |
| --- | --- | --- | --- | --- | --- | --- |
| PDP-01 | No hue-only chooser | `/m/A01` | No swatch row pretending options exist | Empty product + 4 mystery dots | Major | Payload `colors: []`; WCAG 1.4.1 |
| PDP-02 | Gallery is this mã’s cover | `img alt="A01. TOP"` `/products/A01/cover.jpg` | 200, recognizable garment | Broken image / other mã | Blocker | Live A01 |
| PDP-03 | Related tiles stay same kind | A01 → A02; P02 → other P | Same letter family | A01 related = K01 only because “pretty” | Minor | Live related; NN/G related-items caution |
| PDP-04 | Enlarge path | Single cover | Either lightbox **or** a honest “Message A01 for real photos” (already in EN) | Dead zoom control | Major | NN/G must-have “enlarged view”; live copy |

### 9.2 When a row later has recorded colors (do not invent the list)

Use **only** colors already stored on that mã in admin / `catalog.v1`. Sister `05` §3.2 lists recorded first-ten colors — copy from the live admin row, not from memory.

| ID | Check | Live map | Pass | Fail | Sev | Cite |
| --- | --- | --- | --- | --- | --- | --- |
| PDP-05 | Customer control is **text** (named pill / radio) | Future `/m/{MA}` | Visible Vietnamese/EN **name**; selected state ≠ hue-only | Circles with no name | Major | `02` §7; WCAG 1.4.1 G14 |
| PDP-06 | Selected name filters **this** gallery | Hero + thumbs | Photos with that `colorId` (or untagged + that color) | Shows the other color’s photos | Blocker | `02` §8; `05` §7.2 |
| PDP-07 | Color change does not change mã | URL stays `/m/A01` | Same identity | Navigates to a minted sibling | Blocker | `05` §3.1 |
| PDP-08 | Size (if exposed) does not swap photos by default | Asia chips `2XS`–`2XL` | Photos stay on color; size changes availability | Size S loads a different garment folder | Major | `02` §8.1; `kinds.ts` SIZES |
| PDP-09 | No US conversion | Any size UI | No “US 4” | Converter | Blocker | `DESIGN_NOTES.md`; `ask-fallback.ts` |
| PDP-10 | Missing color photos → honest empty, not borrow | A color with `colorId` and no images | Placeholder / “Message {MA} for photos” | Borrow `/products/A02/cover.jpg` | Blocker | `02` §8.2 |
| PDP-11 | Keyboard selects color | Tab + arrows / Enter | Name announced; gallery updates | Mouse-only | Major | WCAG 2.1.1 |
| PDP-12 | Selected color in accessible name | `aria-pressed` / `aria-checked` + visible text | SR hears “Kem, selected” | “button, button” | Major | WCAG 4.1.2; admin already has `aria-pressed` on boxes |

### 9.3 Motion (keep fancy, don’t fight reduced-motion)

Live CSS: `.announce-fade` 4.2s · `.shimmer` 1.3s infinite · `.cta-shine` · card `duration-500` lift · image `duration-[800ms] scale-[1.08]` · `::view-transition-group(site-header)` · `@media (prefers-reduced-motion: reduce)` zeros those **animations** (not necessarily hover `scale`).

| ID | Check | Live map | Pass | Fail | Sev | Cite |
| --- | --- | --- | --- | --- | --- | --- |
| MOT-01 | Boutique motion still there (default) | Home hover / hero | Shimmer, lift, gold underline, announce | Motion stripped “for performance” into a flat Shopify theme | Major | `02` §8.3; `07` §11.0 |
| MOT-02 | Reduced motion kills looping animation | OS reduce on | No shimmer slide, no announce fade, no view-transition anim | Infinite shimmer remains | Major | Live CSS; WCAG 2.3.3 / 2.2.2 |
| MOT-03 | Hover scale is not a new brand | `@media (hover:hover)` | Same gold/ink language | Springy material redesign | Minor | Live utilities |
| MOT-04 | View transition is the **same mã** | `view-transition-name: product-A01` | A01 card → A01 PDP | Cross-fade into S01 | Major | Home HTML |
| MOT-05 | Header transition does not trap clicks | `::view-transition { pointer-events: none }` | Can tap Messenger during nav | Frozen header | Minor | Live CSS |
| MOT-06 | No AR / 360 / try-on required | — | N/A pass | Blocked sell-test on AR | Note | NN/G “fancy features” |
| MOT-07 | Lightbox (when present) matches intake law | Intake `PhotoLightbox` Esc / backdrop / ✕ | Same close rules if shop adds one | Esc does nothing; focus lost | Major | PR #14; `PhotoLightbox.tsx` |
| MOT-08 | Motion never hides status | Hold gold badge vs Available ink | Badge readable mid-shimmer | Hold only visible after hover | Major | Live badges; `01` §3 |

---

## 10. QC-HOLD — Hold / Message-first

Three vocabularies (`01` §3; `02` §10; Slack 2026-09-04 `Hold AO003 past 24h?` **template**):

| Layer | Words | Not the same as |
| --- | --- | --- |
| Public lookbook | **Available** + `$` · **Hold** + Inbox for price | Official `Reserved`, Ma_List `held`, Orders `Reserved` |
| Official / Slack | Hold extend 24h, Reserved, Sold | A gold badge |
| Square later | Track ON, qty | Lookbook `qty=1` |

### 10.1 Hold vs Available

| ID | Check | Live map | Pass | Fail | Sev | Cite |
| --- | --- | --- | --- | --- | --- | --- |
| HOLD-01 | Available badge + `$` + Message {MA} | `/` A01 · `/m/A01` | Ink badge Available; `$25`; `Message A01` | Hold chrome on A01 | Blocker | Live A01 |
| HOLD-02 | Hold badge + Inbox for price + no `$` | `/` P02/P05 · `/m/P02` | Gold Hold; Inbox for price; photo-check sentence | `$` on P02/P05 | Blocker | Live P02 |
| HOLD-03 | Hold still Message-able | P02 CTA | Opens Page; buyer can ask | Disabled CTA / “sold out” lie | Major | Live “Message to buy”; `01` §3.6 |
| HOLD-04 | Hold ≠ Reserved | Copy | No “Reserved for Jenny” on the tile | Collapsed status | Major | `02` §10; Slack examples |
| HOLD-05 | Hold ≠ Sold | — | Sold mã **gone** from allowlist, not gold-Hold | Reused sold code | Blocker | `DESIGN_NOTES.md`; `03` §7 |
| HOLD-06 | Filter tabs keep Hold visible | Featured Accessories (5) | P02 + P05 still listed | Hold hidden so “Available looks fuller” | Major | Tab count 5 includes holds |
| HOLD-07 | Category `/c/phu-kien` matches | Five P tiles | Same five + statuses | Missing Holds | Major | Live category |
| HOLD-08 | PDP related Hold stays honest | `/m/P01` related P02/P05 | Hold + Inbox for price | Related P02 shows `$` | Blocker | Live P01 links |

### 10.2 Message-first (no cart)

| ID | Check | Live map | Pass | Fail | Sev | Cite |
| --- | --- | --- | --- | --- | --- | --- |
| MSG-01 | No cart / checkout / Shop Pay | Whole site | None | Cart icon, Stripe, Square Online | Blocker | Live; `01` §11.3; `DESIGN_NOTES.md` refuse Shopify |
| MSG-02 | Header Messenger hits the real Page | `profile.php?id=61594312648057` | 200 Page, `noopener` | Dead link / personal profile / `m.me` to a person | Blocker | Live header |
| MSG-03 | Card “Message to buy” is the PDP, then inbox | `/m/A01` then CTA | Two steps OK | Card CTA that POSTs an order | Major | Live `<a href="/m/A01">` |
| MSG-04 | PDP CTA names the code on Available | `Message A01 →` | Code in the verb | Generic “Buy now” | Major | Live A01; `01` §7 |
| MSG-05 | Hold CTA still honest | P02 `Message to buy →` | Does not say “Buy $23” | Prefills a fake price | Blocker | Live P02; `01` APPLY |
| MSG-06 | Prefill gap recorded | All CTAs = bare profile | **Note** until APPLY `m.me?text=` | Testers invent a `text=` that mints a code | Note | `01` §11.1; [m.me links](https://developers.facebook.com/docs/messenger-platform/discovery/m-me-links/) |
| MSG-07 | New tab does not lose the lookbook | `target=_blank` `rel=noopener noreferrer` | Both present | `target=_blank` without rel | Minor | Live anchors |
| MSG-08 | Footer repeats Message + Zelle **word only** | Footer | `Zelle · Message on Messenger`; no personal name | Phone / @handle / legal name | Blocker | Live footer; `06` §8 |
| MSG-09 | No ship `$` | Announce + PDP + footer | No `$8 ship` | Invented flat ship | Blocker | Slack still needs Boss ship $; `01` §6 |
| MSG-10 | Livestream bar is a channel, not a fake clock | `Facebook livestream` + `announce-fade` | Either a real day (`01` APPLY) or this honest channel label | “Live now” when offline | Major | Live bar; `01` §11.5 |
| MSG-11 | Site never Sends | — | No FB graph send | Auto-DM | Blocker | `README.md` |
| MSG-12 | Icebreaker is Owner-side | Meta Inbox greeting | N/A on the website | Agent posts as the Page | Note | `01` §11.7 |

---

## 11. QC-MOB — mobile

Live: `viewport width=device-width, initial-scale=1, viewport-fit=cover` · header `h-14` / `sm:h-16` · nav `overflow-x-auto` · featured `tab-scroll` · cards `grid-cols-2` · `sm:grid-cols-3` `lg:grid-cols-4` `xl:grid-cols-5` · hero `h-[58vh] min-h-[320px]` / `sm:h-[72vh]` · collection tiles `grid-cols-2 md:grid-cols-3 lg:grid-cols-5` · PDP `pb-32` (room for sticky CTA) · Shop tools `bottom-3 right-3`.

| ID | Check | Live map | Pass | Fail | Sev | Cite |
| --- | --- | --- | --- | --- | --- | --- |
| MOB-01 | 390px: 2-up cards, no horizontal page bleed | `/` | Grid fits; nav scrolls **inside** | Body scroll sideways | Major | `grid-cols-2`; `overflow-x-auto` |
| MOB-02 | Category nav reachable with thumb | `aria-label="Categories"` | All five labels readable | Hair clipped forever | Major | Live nav |
| MOB-03 | Featured tabs scroll, counts visible | All 10 … Hair 1 | Can reach Hair | Tabs clipped, All looks like the only filter | Major | `tab-scroll` |
| MOB-04 | Sticky header does not eat the hero CTA | `sticky top-0 z-50` | Wordmark + Messenger still tappable | Overlay blocking tiles | Major | Live header |
| MOB-05 | PDP primary CTA above the fold **or** sticky | `Message A01` + `pb-32` | Can Message without hunting | CTA under Safari chrome | Major | Live PDP; NN/G “clear next action” |
| MOB-06 | Shop tools does not cover Message | `z-50` gold dot | Can tap footer CTA | Dot sits on the CTA | Major | Live layout |
| MOB-07 | Safe area | `viewport-fit=cover` | Notched phones: bar not under Dynamic Island | Cropped announce | Minor | Viewport meta |
| MOB-08 | Covers are portrait 3/4 | `aspect-[3/4]` `object-cover` | Face/garment not cropped to nonsense | Cover letterboxed into a square theme | Minor | Live cards; `06` 864×1152 note |
| MOB-09 | Hover motion not required | Hover MQ | Phone tap still opens `/m/A01` | Affordances only on hover | Major | `@media (hover:hover)` |
| MOB-10 | 200% zoom | iOS accessibility zoom | Price + mã + CTA still readable | Tiny `$` only | Major | WCAG 1.4.4 (reflow/zoom) |
| MOB-11 | Empty collection on phone | `/c/quan` | “Nothing in this collection yet.” | Infinite spinner | Minor | Live empty |
| MOB-12 | Messenger opens a usable Facebook surface | Phone | App or m-web Page | `about:blank` | Major | Page id |

---

## 12. QC-A11Y — accessibility

Map to WCAG 2.2. This shop is small; **Level A + AA** on the lookbook is the bar. Do not wait for a VPAT.

### 12.1 Name, role, status

| ID | Check | Live map | Pass | Fail | Sev | Cite |
| --- | --- | --- | --- | --- | --- | --- |
| A11Y-01 | Page titles unique | `Sassy Closet` / `A01 · Top · Sassy Closet` / `P02 · Thermos · Sassy Closet` / `Tops · Sassy Closet` / `Admin · Sassy Closet` | Each URL a distinct `<title>` | All “Sassy Closet” | Major | [WCAG 2.4.2](https://www.w3.org/WAI/WCAG22/Understanding/page-titled.html); `06` §6.1 |
| A11Y-02 | Status not color-only | Badge text Available/Hold + `sr-only` “Status: ” + ink vs gold | Text present | Gold circle only | Blocker | Live badges; [1.4.1](https://www.w3.org/WAI/WCAG22/Understanding/use-of-color) |
| A11Y-03 | Messenger name | `aria-label="Message on Messenger"` | Present | Icon-only unlabeled | Major | Live header; [2.4.4](https://www.w3.org/WAI/WCAG22/Understanding/link-purpose-in-context.html) |
| A11Y-04 | Shop tools name | `aria-label="Shop tools"` | Present | Unlabeled gold pixel | Major | Live button |
| A11Y-05 | Featured tabs are tabs | `role="tab"` `aria-selected` `role="tablist"` | State updates | Clickable `<div>`s | Major | Home HTML; [4.1.2](https://www.w3.org/WAI/WCAG22/Understanding/name-role-value.html) |
| A11Y-06 | Card link purpose | `alt="A01. TOP"` + visible `A01 TOP` + `$25` | Context in the `<a>` | “image, image, image” | Major | Live cards; 2.4.4 |
| A11Y-07 | Decorative gradients `aria-hidden` | Header/hero overlays | Hidden | SR reads empty images | Minor | Live `aria-hidden="true"` |
| A11Y-08 | 404 has an `h1` | “Not found” | Yes + link home | Empty main | Major | Live 404 |

### 12.2 Contrast, target, keyboard, motion

Tokens: ink `#111` on paper `#fff` (fine). muted `#6b6b6b` on `#fff` ≈ 5.7:1 (AA for normal text — **measure**, don’t assume). gold `#b08968` on ink for Hold badge — **measure**. 9px uppercase badges are small.

| ID | Check | Live map | Pass | Fail | Sev | Cite |
| --- | --- | --- | --- | --- | --- | --- |
| A11Y-09 | Body text ≥ 4.5:1 | `.text-ink` / `.text-muted` | AA | Muted fails on blush | Major | [1.4.3](https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html) |
| A11Y-10 | Hold badge gold-on-ink / paper-on-ink | `.bg-gold` + `.text-ink`; Available `.bg-ink` + `.text-paper` | AA (large or small as used) | Gold on blush 2:1 | Major | 1.4.3 |
| A11Y-11 | Focus visible | Tab through header → tiles → CTA | Outline / gold focus (`focus:border-gold` on admin) | `outline-none` with no replacement on customer links | Major | [2.4.7](https://www.w3.org/WAI/WCAG22/Understanding/focus-visible.html) |
| A11Y-12 | Target ≥ 24×24 (or spacing exception) | Messenger text link; tabs; Shop tools `h-8 w-8` but inner dot `h-2.5 w-2.5` | Hit area ≥ 24px or spaced | Adjacent 10px chips | Major | [2.5.8](https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum) |
| A11Y-13 | Admin letter tiles are large enough | Next-mã tiles | Thumb-friendly | 16px tiles flush | Major | 2.5.8; admin Add |
| A11Y-14 | Keyboard can Message | Tab to CTA, Enter | Opens Page | Click-only | Blocker | 2.1.1 |
| A11Y-15 | Keyboard can filter Featured | Tabs | Arrow/Tab changes All→Tops and grid | Mouse-only | Major | tablist |
| A11Y-16 | No keyboard trap on admin sheets | `/admin` | Esc / Tab cycles | Focus stuck in hex popover | Major | 2.1.2 |
| A11Y-17 | `lang` honest enough | `lang="en"` + VN lines | VN phrases still readable; don’t mark whole page `vi` unless flipped | `lang=en` on a VN-only string that a SR mispronounces **and** no VN `lang` span | Minor | `06` §4; [3.1.1](https://www.w3.org/WAI/WCAG22/Understanding/language-of-page.html) / 3.1.2 |
| A11Y-18 | Reduced motion | §9.3 | MOT-02 pass | — | Major | Live CSS |
| A11Y-19 | Admin hex boxes are not the customer UI | Admin `aria-pressed` | Staff-only | Same boxes on `/m/A01` | Major | Admin vs `02` §7 |
| A11Y-20 | Zoom 400% / reflow | PDP | Mã + price + CTA stack | Horizontal-only PDP | Major | [1.4.10](https://www.w3.org/WAI/WCAG22/Understanding/reflow.html) |

---

## 13. QC-SEO — index, OG, trust (two clocks)

**Clock A — sell-test now (law):** `noindex, nofollow` on every HTML page is **intentional soft-launch** (`01` §11.6; `04` §11). `/robots.txt` and `/sitemap.xml` 404. No `og:*`. **Do not flip index from this repo.**

**Clock B — Boss said public (`06` P0):** then the same facts are **fails**.

Record **which clock** at the top of the log.

### 13.1 Clock A (soft-launch) — pass when private

| ID | Check | Live map | Pass | Fail | Sev | Cite |
| --- | --- | --- | --- | --- | --- | --- |
| SEO-A1 | Public lookbook is noindex | `<meta name="robots" content="noindex, nofollow"/>` on `/`, `/c/*`, `/m/*` | Present | Accidentally `index` before Boss yes | Blocker | [Google noindex](https://developers.google.com/search/docs/crawling-indexing/block-indexing); live meta |
| SEO-A2 | Admin also noindex | `/admin` same meta | Present | Admin indexed | Major | Live admin; `06` P0.2 idea |
| SEO-A3 | Intake stays off this host | — | Different project | Sell-test DNS on intake | Blocker | `04` §3 |
| SEO-A4 | Titles still unique (for Messenger unfurl later) | PDP titles | A01 ≠ P02 | Duplicate titles | Minor | `06` §6.1 |
| SEO-A5 | Descriptions mention the **real** mã / Hold | A01 / P02 metas | A01 asks to message A01; P02 says no USD | Generic spam + invented code | Major | Live metas |

### 13.2 Clock B (go-live) — fail until APPLY

Copy the P0/P1 list from `06` §14. Do not invent extra landing pages.

| ID | Check | Live 2026-09-09 | Go-live pass | Sev | Cite |
| --- | --- | --- | --- | --- | --- |
| SEO-B1 | `index,follow` (or omit) on `/`, `/c/*`, `/m/{ALLOW}` | **FAIL** noindex | Flip on **shop** host only | Blocker | `06` P0.1 |
| SEO-B2 | `/robots.txt` 200 + sitemap line | **404** | 200 | Major | [robots intro](https://developers.google.com/search/docs/crawling-indexing/robots/intro) |
| SEO-B3 | `/sitemap.xml` absolute URLs, uppercase `/m/A01` only | **404** | 200; no `/m/a01`, no `/admin` | Major | [Sitemaps](https://developers.google.com/search/docs/crawling-indexing/sitemaps/overview) |
| SEO-B4 | Self-canonical | **absent** | Present | Major | `06` P0.6 |
| SEO-B5 | `/m/a01` → 308 `/m/A01` | **both 200** | Redirect | Major | This crawl; `06` P0.7 |
| SEO-B6 | `og:title` `og:description` `og:image` `og:url` `og:type` | **absent**; `/opengraph-image` 404 | Present; image ~1200×630 not raw 3/4 cover | Major | [ogp.me](https://ogp.me/); `06` §6.3 |
| SEO-B7 | No JSON-LD Product with fake `offers.price` on Hold | **no JSON-LD** (honest absence) | Still no `$` on P02/P05 if you add schema | Blocker | `06` §10; `07` §4.2 |
| SEO-B8 | How-to / meetup pages | `/how-to-buy` `/meetup-ship` **404** | Only after Boss copy; **no ship $** | Note | `06` §9 |
| SEO-B9 | Announcement may name a day | “Facebook livestream” only | Day **or** stay channel-honest | Minor | `01` §11.5 |

---

## 14. QC-NAV — IA, empty collections, 404s, photos

| ID | Check | Live map | Pass | Fail | Sev | Cite |
| --- | --- | --- | --- | --- | --- | --- |
| NAV-01 | Header kinds = kinds with stock | A S P K H | Matches Featured counts 2/1/5/1/1 | Header “Pants” with 0 and a fake SKU | Major | Home `types` |
| NAV-02 | Slug language | `/c/ao` not `/c/tops` | VN slug + EN label | `/c/tops` 200 duplicate | Minor | Live 404 `/c/tops`; `06` §3.1 |
| NAV-03 | Empty collection copy | `/c/quan` | Honest empty; **no invented Q01 product** | Placeholder garments | Blocker | Live sentence |
| NAV-04 | English junk slugs 404 | `/c/a` `/c/tops` | 404 | Thin duplicate index | Minor | This crawl |
| NAV-05 | Trailing slash PDP | `/m/A01/` → 308 | Canonical | Soft 200 duplicate | Minor | This crawl |
| NAV-06 | Cover 200 for all ten | `/products/{MA}/cover.jpg` | All 200 jpeg | Any 404 | Blocker | This crawl sample A01/P02/P03/K01 |
| NAV-07 | Editorial 200 | `/editorial/hero.jpg` `ao.jpg` `set.jpg` `phu-kien.jpg` `ao-khoac.jpg` `toc.jpg` | 200 | Broken hero | Major | Home preloads |
| NAV-08 | Favicon 200 | `/favicon.ico` `/icon.svg` | 200 | Browser tab broken | Minor | Live |
| NAV-09 | Cross-surface price/status | Home card = category card = PDP = admin header | A01 $25 Available everywhere | Home $25, PDP $22 | Blocker | §0.4 table |
| NAV-10 | Related does not mint | PDP related | Only allowlist mãs | “You may also like A03” | Blocker | Live related |

---

## 15. Cross-surface consistency matrix

Tick each cell against §0.4. One mismatch = **NAV-09** fail.

| Mã | `/` card | Featured tab | `/c/…` | `/m/{MA}` title | `/m/{MA}` `$`/Hold | `/admin` card | cover.jpg |
| --- | --- | --- | --- | --- | --- | --- | --- |
| A01 | Available $25 | Tops | `/c/ao` | `A01 · Top · Sassy Closet` | $25 | A01 · Top · $25 | 200 |
| S01 | Available $28 | Sets | `/c/set` | `S01 · Set · …` | $28 | S01 · Set · $28 | 200 |
| P01 | Available $5 | Accessories | `/c/phu-kien` | `P01 · Accessory · …` | $5 | P01 · Accessory · $5 | 200 |
| P02 | Hold Inbox | Accessories | `/c/phu-kien` | `P02 · Thermos · …` | Inbox | P02 · Thermos · Hold | 200 |
| P03 | Available $18 | Accessories | `/c/phu-kien` | `P03 · Accessory · …` | $18 | P03 · $18 | 200 |
| P04 | Available $13 | Accessories | `/c/phu-kien` | `P04 · Accessory · …` | $13 | P04 · $13 | 200 |
| P05 | Hold Inbox | Accessories | `/c/phu-kien` | `P05 · Thermos · …` | Inbox | P05 · Hold | 200 |
| K01 | Available $37 | Jackets | `/c/ao-khoac` | `K01 · Jacket · …` | $37 | K01 · $37 | 200 |
| H01 | Available $8 | Hair | `/c/toc` | `H01 · Hair · …` | $8 | H01 · $8 | 200 |
| A02 | Available $22 | Tops | `/c/ao` | `A02 · Top · …` | $22 | A02 · $22 | 200 |

---

## 16. Anti-patterns (instant fail)

Refuse these even if a generator “helps”:

1. Minting `A03` (or any next-tile) to make the grid look fuller.  
2. Showing P05 at `$23`.  
3. Translating `A01` → `AO001` on the lookbook “for Square consistency.”  
4. Hue-only customer swatches for Caro / Hoa / Ánh kim.  
5. Borrowing another mã’s photo.  
6. Adding a cart “just for QA.”  
7. Inventing ship `$`, US size, or a livestream “Live now.”  
8. Putting `e.tb.cn` or cost on `/m/*`.  
9. Sharing intake Blob with the shop.  
10. Running Add/rename on Production official without `#shop-decisions` yes.  
11. Treating this repo as the Origin shop (it is not).  
12. Filing a pass from a single screenshot (`user_rule` / `04` cache smoke).

---

## 17. Pass log template (copy per run)

```text
Sell-site bugcheck
Host: https://sassy-closet-shop.vercel.app
Clock: A soft-launch / B go-live
Date (PT):
Tester:
Viewport: desktop __  phone __  reduced-motion __
Boss yes for write tests?: no / yes (paste Slack)

Allowlist seen (10): A01 S01 P01 P02 P03 P04 P05 K01 H01 A02
Hold pair still Inbox: P02 __  P05 __
P05 is NOT $23: __

LAW  Blocker fails:
ADM  (Add N/A unless Boss yes):
BLOB Redeploy done?: no / yes
COL  colors still [] ?: yes / named list (copy admin, don’t invent)
PDP/MOT
HOLD/MSG  Page id 61594312648057 opens: __
MOB
A11Y  contrast notes:
SEO   clock A noindex present: __
NAV   /m/A03 404: __   /c/quan empty honest: __

Screens/video: (paths)
Ship decision: PASS / FAIL
```

Never paste secrets, customer names, or Square tokens into the log (`README.md`).

---

## 18. As-built gaps (observed 2026-09-09 — not inventions)

These are **notes** for Origin / APPLY, not licenses to mint data.

| Gap | Live fact | Sister APPLY | QA handling |
| --- | --- | --- | --- |
| No `m.me?text=` | All CTAs = profile `61594312648057` | `01` §11.1 | MSG-06 Note |
| Hold CTA omits code | P02 “Message to buy →” vs A01 “Message A01 →” | `01` §7 | MSG-05 watch |
| Customer colors empty | `colors: []` | `02` / `05` bind later | COL-01 pass if empty |
| Admin hex-only boxes | “Boxes only — no names” | Customer must stay text | A11Y-19 |
| No rename UI | Not in admin tree | `03` §6 | ADM-25 Note |
| `/m/a01` 200 duplicate | Same title as A01 | `06` P0.7 | SEO-B5 Clock B |
| No OG / sitemap / robots.txt | 404 / no tags | `06` P0 | Clock A pass / B fail |
| HQ `001.jpg` not on CDN | cover.jpg only | `05` §6 | COL-02 Note |
| Livestream bar has no day | “Facebook livestream” | `01` §11.5 | MSG-10 |
| No how-to / meetup routes | 404 | `06` §9 | SEO-B8 |
| Shop-tools hit area | 8×8 wrapper, 2.5×2.5 visible | WCAG 2.5.8 | A11Y-12 |
| Hover scale not in reduced-motion query | Only *animations* killed | MOT-02 / MOT-03 | Measure |

---

## 19. Sources

### 19.1 Shop law and as-built

- This crawl: [https://sassy-closet-shop.vercel.app](https://sassy-closet-shop.vercel.app) (2026-09-09).  
- [SkyLanter/Sassy-closet](https://github.com/SkyLanter/Sassy-closet) `README.md`, `excel-kit/DESIGN_NOTES.md`, `excel-kit/schema.py`, `excel-kit/KIT.md`, `excel-kit/prompts/FIND_MA_CARD_2026-09-08.md`, `excel-kit/prompts/GF_CLOTHES_INTAKE.md`, `sassy-closet/README.md`, `sassy-closet/BOSS.md`, `sassy-closet/lib/mint.ts`, `sassy-closet/lib/kinds.ts`, `sassy-closet/lib/store-backend.ts`, `sassy-closet/lib/captions.ts`, `sassy-closet/components/PhotoLightbox.tsx`.  
- PR #15 Durable Blob; PR #14 lightbox; PR #18 `excel-kit/docs/SELL_CATALOG_CONTRACT.md`.  
- Slack `#shop-decisions` (`C0BV3GYC602`), 2026-09-04: Facebook is the store; bots draft only; Track stock ON **yes**; example *templates* `AO001` / `Hold AO003 past 24h?` — **not live shop stock**.  
- Sister docs `01`–`07` (PRs #19–#25).

### 19.2 UX

- Nielsen Norman Group, [*UX Guidelines for Ecommerce Product Pages*](https://www.nngroup.com/articles/ecommerce-product-pages/) (must-have / nice / fancy; retrieved 2026-09-09).  
- Baymard Institute product-page / variant research as cited in `02` (do not copy unsourced %).

### 19.3 Accessibility (WCAG 2.2)

- [WCAG 2.2](https://www.w3.org/TR/WCAG22/).  
- [1.4.1 Use of Color](https://www.w3.org/WAI/WCAG22/Understanding/use-of-color).  
- [1.4.3 Contrast (Minimum)](https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html).  
- [1.1.1 Non-text Content](https://www.w3.org/WAI/WCAG22/Understanding/non-text-content.html).  
- [1.4.10 Reflow](https://www.w3.org/WAI/WCAG22/Understanding/reflow.html).  
- [2.1.1 Keyboard](https://www.w3.org/WAI/WCAG22/Understanding/keyboard.html).  
- [2.4.2 Page Titled](https://www.w3.org/WAI/WCAG22/Understanding/page-titled.html).  
- [2.4.4 Link Purpose](https://www.w3.org/WAI/WCAG22/Understanding/link-purpose-in-context.html).  
- [2.4.7 Focus Visible](https://www.w3.org/WAI/WCAG22/Understanding/focus-visible.html).  
- [2.5.8 Target Size (Minimum)](https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum).  
- [4.1.2 Name, Role, Value](https://www.w3.org/WAI/WCAG22/Understanding/name-role-value.html).  
- [WebAIM Contrast Checker](https://webaim.org/resources/contrastchecker/).

### 19.4 SEO / social

- [Google: Block indexing (`noindex`)](https://developers.google.com/search/docs/crawling-indexing/block-indexing).  
- [Google: Robots meta tags](https://developers.google.com/search/docs/crawling-indexing/robots-meta-tag).  
- [Google: robots.txt](https://developers.google.com/search/docs/crawling-indexing/robots/intro).  
- [Google: Sitemaps](https://developers.google.com/search/docs/crawling-indexing/sitemaps/overview).  
- [Google: Title links](https://developers.google.com/search/docs/appearance/title-link).  
- [Open Graph protocol](https://ogp.me/).

### 19.5 Messenger / infra

- [Meta: m.me links](https://developers.facebook.com/docs/messenger-platform/discovery/m-me-links/).  
- Facebook Page used by the site: [profile `61594312648057`](https://www.facebook.com/profile.php?id=61594312648057).  
- [Vercel ISR](https://vercel.com/docs/incremental-static-regeneration).  
- [Vercel Blob](https://vercel.com/docs/storage/vercel-blob).  
- Next.js `revalidatePath` (see `04` §7.4).

---

## 20. One-page tear-off (twenty minutes)

Print. Soft-launch. **No new mã.**

1. `/` All = **10**. Codes = A01 S01 P01 P02 P03 P04 P05 K01 H01 A02 only.  
2. A01 `$25` Available · P02 / P05 **Inbox for price** · **P05 is not $23**.  
3. `/m/A03` 404. `/m/MISSING` 404. `/c/quan` empty, no fake pants.  
4. Covers `/products/A01/cover.jpg` … `/products/A02/cover.jpg` all 200.  
5. Message CTA opens Page `61594312648057`. No cart. Footer Zelle **word**, no personal name.  
6. `/admin` off nav · Storage **Vercel Blob** · Catalog (10) · Save does not change the mã.  
7. Next tiles (A03…D01) are **not** public. Do not Add.  
8. Customer PDP: no hue-only swatches; empty colors stay empty.  
9. Phone 390px: 2-up, Message reachable, Shop tools not on the CTA.  
10. Keyboard: Tab to Message A01. Status is text, not color-only. Reduce-motion: shimmer/announce off.  
11. Clock A: `noindex, nofollow` still on. Clock B: run `06` P0 instead.  
12. If you Saved anything, revert copy. Redeploy only with Boss. **Never invent mã.**

---

## 21. Open questions (do not answer by inventing)

1. When does Boss flip Clock A → Clock B (`noindex` off)? Not a tester decision.  
2. Will sell-test grow a rename control, or is identity change Official-only (`03` §6.3)?  
3. When do first-ten `colors[]` get **recorded** names (not guessed hex)?  
4. Official custom domain — not this host; do not steal DNS (`04` §3).  
5. Flat ship `$` — still missing in `#shop-decisions`. Do not put a number on the bar.

If a question needs a code that is not in §0.4, the answer is **ASK STOCK**, not a new tile.
