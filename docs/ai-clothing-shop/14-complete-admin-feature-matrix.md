# 14 — Complete admin feature matrix (ready-to-sell test boutique)

**LEARN TRACK (Ultra burn)** · LEARN → **APPLY sell-test only** · never mutate Excel / intake.

This chapter is the **full merchandiser matrix** for a 10-piece lookbook that can take a real inbox sale: **Add / Edit / rename / colors / photos / Hold / settings / import**. It is the spine that [03](./03-tiny-boutique-admin.md) (ops), [04](./04-next-blob-catalog-arch.md) (Blob + `catalog.v1`), [05](./05-ai-product-media.md) (per-color bind), [11](./11-vercel-blob-admin-qa.md) (Save/cache QA), and playbook [03-tiny-admin-ops.md](./03-tiny-admin-ops.md) already slice. This file does **not** replace those clocks — it says **what the admin must do, what live `/admin` already does, and the Origin APPLY order**.

**This kit PR writes docs only.** Do not edit `excel-kit/**`, `sassy-closet/**`, Official Excel, Square, or Origin shop `main`. APPLY lands on Origin `sassy-closet-shop` (sell-test / a shop feature branch). [[S1]](#s1-sell-catalog-contract) [[S2]](#s2-clone-to-official)

**Kelly Ying look stays.** Paper / ink / gold / blush, Be Vietnam Pro + Cormorant Garamond, Messenger / Zelle / Facebook livestream. Do not restyle. [[S3]](#s3-look-lock)

**Never invent mã.** The only sell-site codes this lane may name are the Boss allowlist of ten. Live **Add A03** / Next-grid `Q01 V01 K02…` is a publish invitation — Origin must refuse it. [[S1]](#s1-sell-catalog-contract) [[S4]](#s4-live-2026-09-09)

Written 2026-09-09 against kit `main` @ `ba33024` plus the open handoff on [PR #18](https://github.com/SkyLanter/Sassy-closet/pull/18). Live sell-test `/` and `/admin` were fetched the same day. Granola MCP was unauthorized. Slack `#shop-decisions` (2026-09-04) is Square Track ON + bots draft only — not an admin-screen spec. Shop law is repo contracts + live HTML.

---

## 0. How to use this matrix

| If you need… | Jump to |
| --- | --- |
| What “ready-to-sell test” means | [§2](#2-ready-to-sell-test-boutique--definition) |
| One table for every admin verb | [§4 Master matrix](#4-master-matrix) |
| Add / mint refuse | [§5](#5-add) |
| Edit (same mã) | [§6](#6-edit) |
| Rename (identity change) | [§7](#7-rename) |
| Colors (text vs hex) | [§8](#8-colors) |
| Photos + `colorId` | [§9](#9-photos) |
| Hold / Available | [§10](#10-hold) |
| Settings (shop chrome, not a PIM) | [§11](#11-settings) |
| Import / export `catalog.v1` | [§12](#12-import--export) |
| **Origin APPLY order** | [§14](#14-origin-apply-order) |
| Paste-ready Origin brief | [§17](#17-paste-into-origin-agent) |

**Default stance:** live sell-test and intake Production are **read-only** from this kit. Mutation of shop code is Origin’s job. Mutation of Excel / intake from this LEARN is **forbidden**.

A screenshot of `/admin` is **not** a complete merchandiser. Completeness is: the ten allowlist rows, honest Hold, real photos, Save receipt + cache bust, no invented 11th mã, and an import path that cannot lie.

---

## 1. Standing law (print first)

| Law | Meaning on sell-test admin | Cited |
| --- | --- | --- |
| **SKU = mã** | One unique piece → one unique code. Sold stays retired. | [`README.md`](../../README.md); [`schema.py`](../../excel-kit/schema.py) `ASK_STOCK_MA` |
| **Never invent mã** | Admin “Next mã A03” is **not** an assignment. Stock/Boss assign; kit allowlist publishes. | [PR #18](https://github.com/SkyLanter/Sassy-closet/pull/18); [03](./03-tiny-boutique-admin.md) §3 |
| **Sell catalog ≠ warehouse** | `qty=1` is “this unique piece,” not a cycle count. Square Free is on-hand SoT **later**. | [`DESIGN_NOTES.md`](../../excel-kit/DESIGN_NOTES.md); Slack `#shop-decisions` 2026-09-04 |
| **Hold ⇔ no public $** | `status=hold` **and** `priceUsd=null`. P02 / P05 today. Hub `23` on P05 must not publish. | [PR #18](https://github.com/SkyLanter/Sassy-closet/pull/18) `SELL_ALLOWLIST_PRICE_USD` |
| **Customer colors are text** | `Kem` / `Xanh` / `Chấm bi`. Admin may keep hex **boxes**. Do not invent hex to fill them. | [PR #18](https://github.com/SkyLanter/Sassy-closet/pull/18) contract; [05](./05-ai-product-media.md) |
| **Bots draft only** | Owner posts, messages, takes Zelle, taps Square Save. Site never Posts / Saves. | [`PROMPTS.md`](../../excel-kit/PROMPTS.md); `#shop-decisions` |
| **Three Blobs** | Intake ≠ sell-test ≠ official. A Save that writes the wrong store is silent on the host you are staring at. | [04](./04-next-blob-catalog-arch.md) §8; [PR #18](https://github.com/SkyLanter/Sassy-closet/pull/18) `CLONE_TO_OFFICIAL.md` |
| **No password wall** | `/admin` stays public + `noindex` + “Test only.” Do not add Basic Auth from this LEARN. | Playbook [README](./README.md); [03-tiny-admin-ops](./03-tiny-admin-ops.md) |
| **Do not fight Origin `main`** | APPLY on sell-test / shop feature branch. Kit does not fork shop code. | Playbook [README](./README.md); [S1](#s1-sell-catalog-contract) |

**One sentence for Origin:** edit the ten; refuse the eleventh; Save must write Blob **and** bust public HTML; Hold must drop the dollar.

---

## 2. Ready-to-sell test boutique — definition

“Ready-to-sell **test**” is **not** official go-live and **not** Square Save. It is: a buyer can open [sassy-closet-shop.vercel.app](https://sassy-closet-shop.vercel.app), see the ten pieces honestly, tap **Message to buy**, and Boss can merchandize those ten on `/admin` without the site lying after Save.

| Must be true | Must stay false |
| --- | --- |
| Exactly ten allowlist mãs on `/` and `/admin` | Cart, checkout, Stripe, Square widget |
| Available tiles show Boss USD | `$23` anywhere (P05 leak) |
| Hold tiles show **Inbox for price**, no `$` | Available tile with blank price |
| `/m/A03` **404** | Public A03 / Q01 / P06 tile |
| Photos are real JPEG/s, not letter placeholders after upload | Invented HQ bytes / AI as original |
| Storage: **Vercel Blob** (not `/tmp`) | Shared intake Blob |
| Save {MA} persists + public HTML matches after two warms | Silent Saved toast |
| Messenger + Zelle + livestream chrome | Password wall; personal name; Zelle handle |
| `robots: noindex, nofollow` until Boss says index | SEO launch from this LEARN |
| Import `catalog.v1` rejects extras | Kind-tab merge / invented hex |

Official clone is a **later** project ([04](./04-next-blob-catalog-arch.md) §8, [PR #18](https://github.com/SkyLanter/Sassy-closet/pull/18) `CLONE_TO_OFFICIAL.md`). Soft-launch stays sell-test until `#shop-decisions` yes.

---

## 3. Surfaces this matrix may name

```
 Square Free          on-hand SoT later. Boss Save only.     THIS LEARN: never Save.
 Official Excel       AO001 working copy / captions.         THIS LEARN: never write xlsx.
 OD hub + Photos/     sassycloset.xlsx All + Photos/{MA}/    THIS LEARN: read contract only.
 Intake Next+Blob     sassy-closet.vercel.app                THIS LEARN: read-only. Do not mutate.
 Sell-test Next+Blob  sassy-closet-shop.vercel.app /admin    APPLY TARGET (Origin).
 catalog.v1 JSON      PR #18 export / validate               Kit writes JSON. Origin imports.
```

| Surface | URL / path | Admin today | This LEARN |
| --- | --- | --- | --- |
| **Intake** | https://sassy-closet.vercel.app · repo `sassy-closet/` | `/admin` = **Tải CSV** + Kho. Tabs: Món mới / Sửa / Tìm mã / Ask | **Do not mutate.** Cite only. |
| **Sell-test** | https://sassy-closet-shop.vercel.app · `/admin` | Per-mã merchandiser. Storage: Vercel Blob. Catalog (10) | **APPLY.** Origin shop code. |
| **Official** | *new* Vercel project (never intake DNS) | Same family as sell-test | Same matrix after clone |
| **Kit JSON** | `out/sell-catalog.v1.json` on [PR #18](https://github.com/SkyLanter/Sassy-closet/pull/18) | n/a | Validate only. Do not hand-mint products |

Two alphabets (do not coerce):

| Alphabet | Shape | Where |
| --- | --- | --- |
| Hub / sell | `A01` (letter + 2–3 digits) | Intake `parseHubMa`, sell `SELL_MA_RE`, this matrix |
| SoT / Square | `AO001` | Official Excel, Square SKU until the A01 handoff |

`A01` ≠ `A001` ≠ `AO001`. A rename that “translates” across alphabets is a **duplicate-code** incident. [[S5]](#s5-schema-py) [[S6]](#s6-intake-mint)

---

## 4. Master matrix

Legend: **HAVE** = live sell-test 2026-09-09 · **GAP** = Origin must land · **REFUSE** = must never ship · **INTAKE** = exists on GF hub only (do not copy onto the shop).

| ID | Verb | Ready-to-sell need | Live sell-test `/admin` | Intake (this repo) | Kit `catalog.v1` | Status | Origin APPLY |
| --- | --- | --- | --- | --- | --- | --- | --- |
| **A1** | Add (allowlisted row) | Not needed — ten already on Blob | Catalog (10) tiles | Món mới mints **draft** `nextMa` | Allowlist closed at ten | **HAVE** the ten | Do not add an 11th |
| **A2** | Add (next unused) | **Refuse.** Stock/Boss only | **Add A03** + letter tiles Q01 V01 K02 G01 B01 P06 H02 J01 S02 O01 D01 | `nextMa()` intake-local | Extra mã **hard-fail** export | **GAP / REFUSE** | [O1](#o1--kill-next-grid-publish) |
| **E1** | Edit copy | EN/VN title + description | Fields exist; A01 EN/VN already filled | Sửa theo mã (staff fields, cost, Taobao) | Titles often `""` (hub has no title cols) | **HAVE** | [O11](#o11--edit-contract) — merge: empty JSON must not wipe shop copy |
| **E2** | Edit price / status | Hold ↔ Available inside Boss table | Dropdown + Price USD; placeholder `Inbox for price` | `sell_usd` on hub; always `status=staged` | Hold ⇔ `priceUsd` null | **HAVE UI / GAP server** | [O8](#o8--hold--price-server-side) |
| **E3** | Edit qty | Locked **1** | Copy: “Qty is always 1.” No qty field | No qty on CSV (test-locked) | `qty` must be `1` | **HAVE** | Keep lock. No stock counter |
| **R1** | Rename mã | Allowlist closed → **refuse** on sell-test | **No rename field** | **Đổi mã** (`data-testid="rename-ma"`) | mã is product id | **HAVE refuse-by-absence** | [O15](#o15--rename-policy) — keep closed; 400 if typed |
| **C1** | Colors (customer) | Text names from hub: `kem` `xanh`… | **Boxes only — no names on the swatches** | Color chips + `color` / `color_note` | `{id,name}` text; **no invented hex** | **GAP** (hex-first UI) | [O12](#o12--colors-text-first) |
| **C2** | Colors (admin hex) | Optional staff boxes; gold `#B08968` is **theme**, not a garment | Palette + custom hex; default `#B08968`; notes admin-only | Intake chips are VN words, not gold token | `hex?` optional; do not invent | **HAVE boxes** | Keep boxes; do not publish names of hex on PDP |
| **P1** | Photos attach | URL or upload on **existing** mã | Add URL / Upload image; cover `/products/{MA}/cover.jpg` | `{ma}/001.jpg` on Blob; keep_photos | OD relative `src`; `colorId` null today | **HAVE attach / GAP cache** | [O13](#o13--photos-hashed-path--colorid) |
| **P2** | Per-color bind | `images[].colorId` ∈ that mã’s colors, or `null` | “Add a color above to tag this image.” | `pieces[]` typed; live form often `[]` | All `colorId` **null** (honest) | **HAVE tag UI / GAP honesty** | [O13](#o13--photos-hashed-path--colorid) |
| **H1** | Hold display | Inbox for price; no `$` | P02 / P05 Hold; public `/` matches | Always `staged` ≠ Hold | P02 P05 hold + null $ | **HAVE** | [O8](#o8--hold--price-server-side) keep pairing |
| **H2** | Sold | Retire identity; leave allowlist | No Sold dropdown (correct for 10 live) | on_hand `sold` if rows exist | `hold\|available` only | **HAVE (omit Sold)** | Do not add Sold that recycles mã |
| **S1** | Settings chrome | Blob badge, Back to shop, Test only, noindex | All present. No Settings panel | Kho + CSV only | n/a | **HAVE strip / GAP panel** | [O16](#o16--settings-strip) |
| **S2** | Settings secrets | **Refuse** passwords, Square tokens, Zelle handle | None (correct) | Ask webhook **names** only | n/a | **REFUSE** | Keep none |
| **I1** | Import `catalog.v1` | Button + hard-fail extras | **No Import string** in HTML | CSV restore ≠ shop import | Exporter + validator on PR #18 | **GAP** | [O17](#o17--import-catalogv1) |
| **I2** | Export `catalog.v1` | Dump shop Blob (allowlist, no cost/source) | **No Export** | `/admin` Tải CSV (staff) | Kit export from All | **GAP** | [O18](#o18--export-catalogv1) |
| **X1** | Save receipt | `{ok, ma, blobWritten, catalogSha, revalidated[]}` | **Save {MA}** × 10; no receipt in HTML | Saved card ≠ durable proof | n/a | **GAP** | [O4](#o4--save-ma-receipt) |
| **X2** | Cache bust | `revalidatePath` + two public warms | Public `/` `/m/*` ISR `STALE`/`HIT`; `/admin` `MISS` `no-store` | Intake already `force-dynamic` | n/a | **GAP** | [O5](#o5--revalidatepath)--[O7](#o7--failed-regenerate-must-not-lie) |
| **X3** | Catalog JSON API | `GET /api/admin/catalog` no-store | **404 HIT** (age 6000s this fetch) | `GET /api/submissions` | File on disk | **GAP** | [O19](#o19--get-apiadmincatalog) |
| **X4** | Manual revalidate | `POST /api/admin/revalidate` | **404 HIT** | n/a | n/a | **GAP** | [O20](#o20--post-apiadminrevalidate) |

Live confirmation this run (2026-09-09): `/admin` 200, `cache-control: private, no-cache, no-store`, `x-vercel-cache: MISS`, title `Admin · Sassy Closet`. `/` Featured collection All 10; P02/P05 Hold · Inbox for price; no `$23`; no A03. `/m/A03` 404 (`x-matched-path: /m/[ma]`, prerender). `/api/admin/catalog` and `/api/admin/revalidate` 404 HIT. [[S4]](#s4-live-2026-09-09)

---

## 5. Add

Adding a SKU is **three gates** ([03](./03-tiny-boutique-admin.md) §4): identity → facts → publication. On a **closed** sell-test, publication is already done for ten codes. A new tile is a **contract change**, not a button.

### 5.1 Ready-to-sell need

| Gate | Who | Sell-test rule |
| --- | --- | --- |
| Identity | Stock / Boss in `#shop-decisions` | Assigned A01-style mã. Never `next unused`. |
| Facts | Hub All + real `Photos/{MA}/` | Colors as text; photos that exist; no invented $. |
| Publication | Kit allowlist PR + Origin import | Widen allowlist **on purpose**. Until then, extras **hard-fail**. |

### 5.2 Live sell-test (HAVE + trap)

`/admin` copy 2026-09-09:

> New items get the next unused mã for the letter you pick.  
> Add item · New items start on Hold. Type comes from the letter. Qty is always 1.  
> Each tile shows the next unused mã.

| Letter | Next tile (aria-label) | Kind |
| --- | --- | --- |
| A | **Add A03** · `A · Tops, next A03` | top |
| Q | Q01 Pants | pants |
| V | V01 Skirts | skirt |
| K | K02 Jackets | jacket |
| G | G01 Shoes | shoes |
| B | B01 Bags | bag |
| P | P06 Accessories | accessory |
| H | H02 Hair | hair |
| J | J01 Jewelry | jewelry |
| S | S02 Sets | set |
| O | O01 Other | other |
| D | D01 Dresses | dress |

Those twelve codes are **not** on the allowlist. `/m/A03` is 404. Home text has **zero** `A03`. The trap is the **button**, not the public grid. [[S4]](#s4-live-2026-09-09) [[S7]](#s7-playbook-observed)

Type-from-letter is correct **after** Stock assigns (matches `KIND_TO_TYPE` on PR #18; `P02`/`P05` override to `thermos`). Qty-always-1 and start-on-Hold are correct. The mint is not.

### 5.3 Intake (do not copy)

`POST /api/submissions` → `resolveSaveMa` → empty create mints `nextMa(kind)` ([`store.ts`](../../sassy-closet/lib/store.ts)). That is **hub draft**. Every row is forced `status: "staged"`, `square: "not_square"`. It is **not** a sell-site assignment. [03](./03-tiny-boutique-admin.md) §4.2; [11](./11-vercel-blob-admin-qa.md) §5.

### 5.4 APPLY (Add)

1. Disable or hide Next-grid / **Add A03** (`data-publishable="false"` if the label stays for Stock).
2. Server: create / Save of any mã ∉ allowlist → **400**.
3. `generateStaticParams` = **Blob ∩ allowlist**. Empty placeholder PDPs are a fail.
4. When Boss adds an 11th: Stock assigns → hub All → kit allowlist + USD table change → re-export → import → upload photos. Not a letter tile. [04](./04-next-blob-catalog-arch.md) §9.6.

---

## 6. Edit

Edit = change **facts** without changing **who the piece is**. Rename is §7.

### 6.1 Per-mã fields (live)

Each of the ten tiles on `/admin` (2026-09-09):

| Control | Live | Ready-to-sell rule |
| --- | --- | --- |
| Header | `{MA} · {Type} · $n` or `Hold · Inbox for price` | Type from letter (`P02`/`P05` → Thermos) |
| Status | Hold · Inbox for price **or** Available | Pair with price ([§10](#10-hold)) |
| Price USD | Number box; Hold placeholder `Inbox for price` | Available ⇒ Boss USD; Hold ⇒ empty / ignored |
| Title (EN) / Title (VN) | Inputs | Do not invent if empty; do not copy staff `flag` |
| Description (EN) / Description (VN flavor) | Textareas | Shop Blob owns copy today (kit JSON titles are `""`) |
| Colors | Hex boxes + optional admin note | [§8](#8-colors) |
| Images | Remove / Add URL / Upload | [§9](#9-photos) |
| **Save {MA}** | Explicit, not autosave | Keep explicit; add receipt ([O4](#o4--save-ma-receipt)) |

Recorded EN/VN this fetch (do not “improve” in APPLY):

| Mã | EN description (live) | VN flavor (live) |
| --- | --- | --- |
| A01 | One unique top on hand. Message A01 for real photos and size. | Áo độc bản — một chiếc đang có. |
| S01 | One set on hand. Message S01 for details and photos. | Set đồ — một set đang có. |
| P01 / P03 / P04 | One accessory on hand. Inbox {MA} to buy. | Phụ kiện — một món đang có. |
| P02 / P05 | Thermos on Hold (photo-check). No USD sell price yet — inbox for price. | Bình giữ nhiệt đang Hold — kiểm tra ảnh. |
| K01 | One jacket on hand. Message K01 for size and photos. | Áo khoác — một chiếc đang có. |
| H01 | One hair piece on hand. Inbox H01 to buy. | Tóc / phụ kiện tóc — một món đang có. |
| A02 | One unique top on hand. Message A02 for real photos and size. | Áo độc bản — một chiếc đang có. |

### 6.2 Safe vs unsafe

| Safe to edit | Unsafe to edit quietly |
| --- | --- |
| Titles / descriptions (boutique voice) | mã |
| Hold ↔ Available **when Boss says** | Square token / qty presented as counted |
| Price **to the Boss table value** | P05 `$23` or any off-table USD |
| Image URL / upload on **this** mã | Another piece’s photos; `_placeholder` |
| Admin color note | Invented customer colorway |

### 6.3 Import merge (Edit × Import)

Kit export leaves `titleEn` / descriptions `""` because the live hub has **no title columns**. Re-import **must merge**: take prices / hold / types / image paths from JSON; **keep** shop titles when JSON titles are empty. Overwrite-empty is a silent wipe of the lookbook voice. [04](./04-next-blob-catalog-arch.md) §4.5; [S1](#s1-sell-catalog-contract).

### 6.4 Intake Edit (cite only)

Sửa theo mã → `PATCH /api/submissions/{ma}`. `keep_photos` invalid JSON → `[]` (**silent empty** — [03](./03-tiny-boutique-admin.md) §11.1). Do not port that parse bug to Origin Save.

---

## 7. Rename

Rename is the most dangerous admin op in a tiny closet. Every photo path, caption, Square SKU, Messenger thread, and export row keys off the code. [03](./03-tiny-boutique-admin.md) §6.

### 7.1 Ready-to-sell need (closed allowlist)

**Sell-test does not need a rename box.** The ten codes are the product ids. A rename is “remove old allowlist slot + add new assigned slot” — a kit contract change + `#shop-decisions`, not a text field.

Live `/admin` has **no** Rename / Đổi mã control. That absence is **correct**. Do not “complete” the matrix by adding a mint.

### 7.2 If a field is added later (Origin policy)

| Step | Rule |
| --- | --- |
| 1 | Old mã is the same physical piece |
| 2 | New mã is Boss/Stock-assigned **and** already on the (widened) allowlist |
| 3 | New mã is free (not Sold, not another live row) |
| 4 | Metadata **and** bytes move together, or not at all |
| 5 | Revalidate `/m/{old}` (must 404) and `/m/{new}` |
| 6 | Leave a staff note “was A01” if buyers still DM the old code — **do not** keep two live tiles |

Server: rename to a non-allowlist code → **400**. Rename onto a taken allowlist code → **409** (intake copy: `đã có rồi — không gộp nha`). Never `A01` → `AO001`.

### 7.3 Intake rename (do not copy blindly)

Sửa → **Đổi mã**. Photo caveat: `saveSubmission` writes **new** bytes under `{newMa}/`; `keep_photos` may still point at `{oldMa}/`. After any future shop rename, GET both PDPs + both cover URLs. Never invent replacement JPEGs. [03](./03-tiny-boutique-admin.md) §6.2; [11](./11-vercel-blob-admin-qa.md) §7.

---

## 8. Colors

A color is **not** a new mã. Per-color storage is `images[].colorId`, not `A01-KEM`. [05](./05-ai-product-media.md); [02](./02-pdp-color-size-ux.md).

### 8.1 Two lanes (do not collapse)

| Lane | Who sees it | Source of names | Hex |
| --- | --- | --- | --- |
| **Customer** | `/` `/c/*` `/m/{MA}` | Hub text: `Kem`, `Xanh`, `Chấm bi`, `Hoa`… | **Do not invent.** Do not name swatches on the PDP |
| **Admin** | `/admin` only | Optional boxes for staff | Live palette (below). Gold `#B08968` is **theme** |

Live admin copy: **“Boxes only — no names on the swatches. Optional note is admin-only.”** Keep that sentence. [S4](#s4-live-2026-09-09)

### 8.2 Hub recorded colors (cite, do not invent)

From [11](./11-vercel-blob-admin-qa.md) §2 / PR #18 sample JSON:

| Mã | Recorded color ids | APPLY bind |
| --- | --- | --- |
| A01 | `kem`, `xanh` | Tag only if a human saw the pixels |
| S01 | `kem` | |
| P01 | `hoa` | |
| P02 | `do` | |
| P03 | `den`, `do` | Do not auto-map 001/002/003 |
| P04 | `kem` | |
| P05 | `hong`, `do`, `xanh` | Hold; still no `$23` |
| K01 | *(none)* | `colorId` **null only**. Do not add `den` |
| H01 | *(none)* | `colorId` **null only** |
| A02 | `cham-bi` | Do not rename to `trang` |

`cham-bi` is not an intake chip rename ([`kinds.ts`](../../sassy-closet/lib/kinds.ts) `COLORS` has `caro` / `hoa` / `khac`, not `cham-bi`). Slug the hub word; do not coerce.

### 8.3 Live admin palette (theme chips, 2026-09-09)

Aria-labels on `/admin`: `#F4F0E8` `#111111` `#FFFFFF` `#C4A484` `#5C4033` `#1C2A4A` `#6B6B6B` `#B08968` `#E8D5C4` `#7A8B6F` `#8B3A3A` `#D4C4B0` + Custom color / Custom hex. Default Add-hex placeholder is **`#B08968`** (shop `--gold`). That is **not** `kem` and **not** permission to write `hex` onto `catalog.v1`. [S1](#s1-sell-catalog-contract)

### 8.4 APPLY (Colors)

1. Keep admin hex boxes + “Boxes only.”
2. Persist `colors[].id` / `name` from **hub words** (or existing shop text). Do not emit `hex` on customer JSON unless Boss recorded a real measured swatch.
3. `colorId` on an image must be `null` or ∈ that product’s ids. Fail Save otherwise.
4. PDP: selecting a **text** color filters gallery to that `colorId` ∪ `null`. Empty color → `—`, never another mã’s photos. [02](./02-pdp-color-size-ux.md); [05](./05-ai-product-media.md) bind rule.
5. Do not mint a colorway (`A01` Xanh twin) without a real Xanh photo.

---

## 9. Photos

### 9.1 Ready-to-sell need

| Rule | Why |
| --- | --- |
| Attach only to an **existing** allowlist mã | Media does not lead identity ([05](./05-ai-product-media.md)) |
| Real files only | Skip `_placeholder`, `_probe`, `.keep`, `README` |
| New pathname (or `?v=`) on replace | Blob overwrite + CDN `HIT` can keep old JPEG 60s–1 month ([11](./11-vercel-blob-admin-qa.md) F7) |
| `colorId` null is honest | HQ folders are flat: `Photos/{MA}/001.jpg`, not `kem/001.jpg` |
| Never persist `blob:` object URLs | PR #18 validator rejects `src.startswith("blob:")` |
| Client upload if > 4.5 MB | Vercel server-upload body limit ([playbook 05](./05-nextjs-blob-catalog.md)) |

### 9.2 Live sell-test

- Covers: `/products/{MA}/cover.jpg` for all ten (also in admin `<img>`).
- Controls: **Add URL** (placeholder `https://… or /products/A01/cover.jpg`) · **Upload image** · Remove.
- Copy: “Add a color above to tag this image.”
- Public `/products/A01/cover.jpg` is a **bare** path — [11](./11-vercel-blob-admin-qa.md) recorded CDN `HIT` age 2000+ on 2026-09-09.

OD HQ inventory (PR #18; skip junk):

| Mã | Real files |
| --- | --- |
| A01 | `001.jpg`, `002.jpg` |
| S01 | `001.jpg` |
| P01 | `001.jpg`, `002.jpg` |
| P02 | `001.jpg`, `002.jpg` |
| P03 | `001.jpg`, `002.jpg`, `003.jpg` |
| P04 | `001.jpg`, `002.jpg` |
| P05 | `001.jpg`, `002.jpg`, `003.jpg` |
| K01 | `001.jpeg`, `002.jpeg` |
| H01 | `001.jpeg`, `002.jpeg`, `003.jpeg` |
| A02 | `001.jpeg`, `002.jpeg` |

Those paths are **not** public URLs. Import leaves letter-placeholders until bytes are uploaded. [S1](#s1-sell-catalog-contract)

### 9.3 Intake photos (cite only)

`{ma}/001.jpg` on intake Blob; UI stays `/api/photos/{ma}/{file}`. Hashes for find-by-photo. CSV `photo_link` is a **folder string**, not bytes. Do not treat intake `/admin` CSV as a shop media backup. [`sassy-closet/README.md`](../../sassy-closet/README.md)

### 9.4 APPLY (Photos)

1. Upload → `put` under `shop/products/{MA}/cover-{sha12}.ext` (or `00n-{sha}.ext`) + point catalog `src`.
2. Or keep stable path **and** append `?v={updatedAt}` on every `<img>`.
3. Tag: `{ src, colorId, order: max+1 }` on **this** mã only.
4. Reject `_placeholder` / missing bytes / `blob:` .
5. AI restyle is a **labeled derivative**, never the HQ original ([05](./05-ai-product-media.md)).

---

## 10. Hold

Tiny-boutique **sell-facing** life is three words. `catalog.v1` today encodes only `hold|available`. Sold is Official / Square later — not a recycle button. [03](./03-tiny-boutique-admin.md) §7; [02](./02-pdp-color-size-ux.md) §10.

### 10.1 Pairing (non-negotiable)

| Status | Buyer meaning | Price | Live codes |
| --- | --- | --- | --- |
| **Hold** | Visible; **not** offered at a public $ | `null` / omitted · copy **Inbox for price** | **P02, P05** |
| **Available** | Offered. Messenger CTA ok | Boss USD only | A01 $25 · S01 $28 · P01 $5 · P03 $18 · P04 $13 · K01 $37 · H01 $8 · A02 $22 |
| **Sold** | Identity retired | — | Not on sell-test allowlist |

Hold ≠ Reserved ≠ Orders `Reserved`. Do not invent a 24h countdown. [02](./02-pdp-color-size-ux.md); `#shop-decisions` Hold-extend examples are **Official / inbox**, not this dropdown.

### 10.2 Live (HAVE display)

Home 2026-09-09: `Status: Hold P02 THERMOS Inbox for price` · `Status: Hold P05 THERMOS Inbox for price`. No `$23`. Admin headers match. Price placeholder on Hold tiles: `Inbox for price`.

### 10.3 Dialect trap

| Dialect | Values | Do not type these on `/admin` |
| --- | --- | --- |
| Sell `catalog.v1` | `hold`, `available` | — |
| Intake submission | always `staged` | Not a Hold control |
| Official SoT | `Available\|Reserved\|Sold\|Hold\|…` | Different sheet |
| Wishlist | `candidate\|watching\|skip\|bought` | Not stock |

### 10.4 APPLY (Hold)

Server-side (not just the radio):

- Reject Available + blank price.
- Reject Hold + any USD (including hub **23**).
- After Save: public `/` and `/m/{MA}` must match the pairing after **two** warms ([11](./11-vercel-blob-admin-qa.md) F11 + F5).
- Do not add Sold that leaves the old URL Available.

---

## 11. Settings

A 10-piece closet needs a **merchandiser**, not a PIM. Settings are **shop chrome + storage health**, not roles / tax / locations. [03-tiny-admin-ops](./03-tiny-admin-ops.md)

### 11.1 Live strip (HAVE — keep)

| Control | Live 2026-09-09 | Rule |
| --- | --- | --- |
| Title | `Admin · Sassy Closet` | Keep |
| Banner | **Test only · not in the main nav** | Keep. Do not add `/admin` to the customer nav |
| Nav | **Back to shop** · “Open sell-test editor…” | Keep the two-way link ([playbook README](./README.md)) |
| Storage | **Storage: Vercel Blob** | Must stay durable. Ephemeral `/tmp` is a shredder |
| Catalog count | **Catalog ( 10 )** | Must stay 10 until allowlist widens |
| Qty law | “Qty is always 1.” | Keep |
| Hold law | “New items start on Hold.” | Keep for any *future* assigned mã |
| `robots` | `noindex, nofollow` (site-wide) | Soft-launch. Do not index from this LEARN |
| Auth | None | **Keep none.** No password in code, git, or prompts |

There is **no** Settings panel, no Import, no Export, no Messenger-URL field, no Zelle-handle field (correct — handle stays off the site).

### 11.2 Ready-to-sell Settings strip (APPLY — small)

Add a **single strip** at the top of `/admin` (not a fifth intake tab). Suggested rows:

| Setting | Editable? | Value law |
| --- | --- | --- |
| Storage | read-only badge | `durable (Vercel Blob)` vs fail-closed |
| Catalog sha / updatedAt | read-only | From Blob `get({ useCache: false })` |
| Allowlist | read-only | The ten, that order |
| Facebook Page URL | Boss only | Live: `https://www.facebook.com/profile.php?id=61594312648057` — do not invent |
| Messenger CTA mode | Boss only | Profile today; `m.me?ref={MA}` is [01](./01-messenger-social-commerce.md) APPLY — site still must not Send |
| Word **Zelle** | on/off | Word is allowed. **No** personal name / handle |
| `noindex` | Boss only | Default on until `#shop-decisions` index |
| Import `catalog.v1` | file picker | [§12](#12-import--export) |
| Export `catalog.v1` | download | Allowlist; strip cost/source |
| Revalidate | button | [O20](#o20--post-apiadminrevalidate) |

### 11.3 Must never appear in Settings

- Passwords / Basic Auth / role matrix
- Square access token / Save
- Customer names, Messenger PSIDs, Zelle handle
- Intake Ask webhook **values**
- `BLOB_*` **values** (names only in git — [`KIT.md`](../../excel-kit/KIT.md))
- US size chart as customer default
- “Generate 20 SKUs”
- Shared intake Blob picker

### 11.4 Env (names only)

Sell-test needs its **own** Blob: `BLOB_READ_WRITE_TOKEN` / `BLOB_STORE_ID` / optional `BLOB_ACCESS`. Do not connect the intake store. Official (later) gets a **third**. [04](./04-next-blob-catalog-arch.md) §8.4; [S8](#s8-kit-md)

---

## 12. Import / export

Import is **write**. Default stance: **hard-fail > silent merge**. [03](./03-tiny-boutique-admin.md) §10; [04](./04-next-blob-catalog-arch.md) §9.

### 12.1 Live

No `Import` / `Export` string on `/admin`. No public `GET /api/catalog`. Handoff today: kit JSON + Mini Boss / human upload. That is why this LEARN’s APPLY includes the button — **on Origin**, not a kit fork.

### 12.2 `catalog.v1` envelope (cite)

```json
{
  "schema": "catalog.v1",
  "source": "Documents/Sassy Closet/sassycloset.xlsx",
  "exportedAt": "2026-09-09T01:42:55Z",
  "allowlist": ["A01", "S01", "P01", "P02", "P03", "P04", "P05", "K01", "H01", "A02"],
  "products": [ ]
}
```

Product keys only: `ma`, `titleEn`, `titleVn`, `descriptionEn`, `descriptionVn`, `type`, `status`, `priceUsd`, `qty`, `colors`, `images`. Extra keys (`cost`, `source_link`, names) **fail**. [S1](#s1-sell-catalog-contract)

### 12.3 Import conflict matrix (sell-test)

| Incoming | Existing | Action |
| --- | --- | --- |
| Same mã, newer **price/hold/type/images** | Shop Blob row | Update those fields |
| Same mã, JSON titles `""` | Shop copy filled | **Keep** shop titles ([§6.3](#63-import-merge-edit--import)) |
| Same mã, JSON titles non-empty | Shop copy | Boss pick; default keep shop unless Mini Boss says JSON is SoT for copy |
| Extra mã (`A03`, `Q01`, `AO001`) | — | **Reject file** |
| Missing allowlist mã | — | **Reject file** |
| P05 `priceUsd: 23` | Hold | **Reject** |
| Invented hex / `blob:` src | — | **Reject** |
| Kind-tab dump / intake CSV | — | **Reject** (wrong brain) |
| Image `src` = OD path | Shop | Accept metadata; tiles stay placeholder until upload |

After accept: F2 write + F4 revalidate **all** public paths + two warms. [11](./11-vercel-blob-admin-qa.md) F16.

### 12.4 Export (shop → JSON)

`GET /api/admin/catalog` or an **Export** button. Shape = `catalog.v1`. Still allowlist. Still no cost/source. This is how kit stops scraping HTML forever ([03-tiny-admin-ops](./03-tiny-admin-ops.md); playbook [06](./06-clone-to-official.md)).

Intake `GET /api/export` CSV is **staff backup**, not this file.

### 12.5 Kit commands (human / Mini Boss — this repo, not Origin)

On [PR #18](https://github.com/SkyLanter/Sassy-closet/pull/18) (not `main` @ `ba33024`):

```bash
python3 excel-kit/scripts/export_sell_catalog.py \
  -w "$HOME/OneDrive/Documents/Sassy Closet/sassycloset.xlsx" \
  --photos-dir "$HOME/OneDrive/Documents/Sassy Closet/Photos" \
  -o ./out/sell-catalog.v1.json
python3 excel-kit/scripts/validate_sell_catalog.py ./out/sell-catalog.v1.json
```

This LEARN does **not** run those against live OneDrive and does **not** add the scripts. Missing `-w` must exit 2 — no silent fallback. [S1](#s1-sell-catalog-contract)

---

## 13. Failure modes the matrix is for

Same three clusters as [03](./03-tiny-boutique-admin.md) §11 / [07](./07-failure-modes.md), scoped to **admin verbs**:

| Cluster | Admin symptom | Matrix row |
| --- | --- | --- |
| **Silent save** | Save {MA} 200, Blob old, `/` still $25 after Hold | X1 X2 — [O4](#o4--save-ma-receipt)–[O7](#o7--failed-regenerate-must-not-lie) |
| **Seed drift** | Add A03 / next Q01 / P05 $23 / shared Blob / gold hex as `kem` | A2 C1 I1 — [O1](#o1--kill-next-grid-publish) [O8](#o8--hold--price-server-side) [O12](#o12--colors-text-first) |
| **Duplicate codes** | Rename onto taken mã; `A01`/`AO001` bridge; two Blobs both “A01” | R1 — [O15](#o15--rename-policy) [O21](#o21--two-blob-stores) |

ISR keeps the **last good page** if regenerate throws. Validate **before** `put`. [04](./04-next-blob-catalog-arch.md) §7.5; [Next.js ISR](https://nextjs.org/docs/app/guides/incremental-static-regeneration).

---

## 14. Origin APPLY order

APPLY on **Origin** `sassy-closet-shop` (sell-test or a shop feature branch). **Do not** fork shop code into this kit. **Do not** mutate Excel or intake. **Do not** restyle. Numbers are **dependency order** — do not land O17 before O1/O8, or an import can mint / price-lie.

Sister fix ids from [11](./11-vercel-blob-admin-qa.md) §18 are in parentheses.

### Wave 0 — Stop the bleed (before any new feature)

#### O0 — Look lock (F12)

Paper/blush/gold, Cormorant + Be Vietnam Pro, Messenger / Zelle / `Facebook livestream`, Page `61594312648057`, `Message to buy`, `rounded-full`, admin “Boxes only.” Qty=1. No cart. `--look` stays green if [11](./11-vercel-blob-admin-qa.md) gate is present.

#### O1 — Kill Next-grid publish (F8)

Disable **Add A03** + letter tiles. Save/create ∉ allowlist → **400**. `/m/A03` stays 404. `generateStaticParams` = Blob ∩ allowlist.

**Done when:** clicking every Next tile does nothing public; POST create A03 is 400.

### Wave 1 — Save cannot lie

#### O2 — Catalog JSON consistent read (F1)

`get(catalogPath, { useCache: false })` on admin + RSC catalog reads. Do not wrap Blob URL in `fetch(..., { next: { revalidate: 3600 } })`.

#### O3 — Catalog JSON overwrite write (F2)

`put(..., { addRandomSuffix: false, allowOverwrite: true, contentType: "application/json", cacheControlMaxAge: 0 })`. Remember: Blob **minimum** overwrite cache is still **60s** without O2. [Vercel Blob](https://vercel.com/docs/vercel-blob)

#### O4 — Save {MA} receipt (F3)

Server Action (preferred) or gated `POST /api/admin/save`. Do **not** paint Saved until: validate (allowlist + Hold pairing + reject next-grid) → `put` → confirm `get({ useCache: false })` → `revalidatePath` → return:

```ts
{
  ok: true,
  ma: "A01",
  blobWritten: true,
  catalogSha: "<hex>",
  updatedAt: "<iso>",
  revalidated: ["/", "/c/ao", "/m/A01"],
}
```

On throw: `ok: false`, dirty form stays, **no** Saved toast.

#### O5 — `revalidatePath` signatures (F4)

- `revalidatePath("/")`
- `revalidatePath("/c/[slug]", "page")` **or** literal `/c/ao` (etc.)
- `revalidatePath("/m/[ma]", "page")` **or** literal `/m/${ma}`

`revalidatePath("/m/[ma]")` **without** `"page"` is a miss. [revalidatePath](https://nextjs.org/docs/app/api-reference/functions/revalidatePath)

#### O6 — Router Cache + two warms (F5)

Server Action + `router.refresh()`, or tell the operator to hard-refresh. Regeneration runs on the **next** visit — GET `/m/{MA}` and `/` **twice**. First `STALE` allowed; second must match Blob.

#### O7 — Failed regenerate must not lie (F6)

Validate before `put` so a Hold row cannot throw halfway and leave `$23` on the tile.

#### O8 — Hold ⇔ price server-side (F11)

Reject Available + blank. Reject Hold + any USD. Pairing is the contract, not the dropdown label.

#### O9 — Admin marker (F14)

On `/admin` document: `data-save-contract="blob+revalidate"` **only** when O4+O5 are wired.

#### O10 — `/admin` stays uncached (F10)

Keep `force-dynamic` + `private, no-store` + `x-vercel-cache: MISS`. Already true 2026-09-09 — do not “optimize” admin onto ISR.

**Wave 1 done when:** Hold flip on P05 Preview → Blob null $ → second GET `/` and `/m/P05` show Inbox, no `$23` → restore.

### Wave 2 — Merchandising completeness (the ten)

#### O11 — Edit contract

Keep per-mã Save (not autosave). Bilingual fields stay. Empty kit titles must not wipe shop copy on import (see O17 merge). Do not add qty, cost, or `source_link` to the customer payload.

#### O12 — Colors text-first

Persist hub `id`/`name`. Hex boxes stay admin-only. No invented `hex` on `catalog.v1`. `colorId` must belong to that mã or be `null`.

#### O13 — Photos hashed path + colorId (F7)

Stop silent overwrite of `/products/{MA}/cover.jpg`. Tag uploads to a color or leave `null`. Reject junk prefixes and `blob:` URLs.

#### O14 — Hold display lock

Public copy stays `Hold` + `Inbox for price`. Available stays `$` + Boss table. Do not restyle the Hold chip.

**Wave 2 done when:** the ten still match [§10.1](#101-pairing-non-negotiable); A01 gallery can bind `kem`/`xanh` **or** stay null; cover etag changes after replace.

### Wave 3 — Missing verbs (settings / import / rename policy)

#### O15 — Rename policy

Do **not** add a casual Đổi mã. If a field exists, it 400s unless the new code is already allowlisted and free. Never bridge `A01`↔`AO001`.

#### O16 — Settings strip

[§11.2](#112-ready-to-sell-settings-strip-apply--small). Read-only Blob + sha + allowlist. Optional Page URL / Zelle word / noindex. **No passwords.** Import/Export/Revalidate buttons live here.

#### O17 — Import `catalog.v1` (F16)

`POST /api/admin/catalog/import`. Same rules as `validate_catalog()`. Merge empty titles. Then O3+O5 for **all** public paths.

#### O18 — Export `catalog.v1`

Download or `GET /api/admin/catalog/export`. Allowlist only. No cost/source/names.

#### O19 — `GET /api/admin/catalog` (F9)

`{ products, catalogSha, updatedAt }`, ten in allowlist order. `private, no-store`. After **adding** the route, bust the **cached 404 HIT** on that exact path (this fetch: age 6066s).

#### O20 — `POST /api/admin/revalidate` (F15)

Gated. Marks `/`, `/c/[slug]` `'page'`, `/m/[ma]` `'page'`. GET may 401/405 — **must not 404**. Bust cached 404 after shipping.

**Wave 3 done when:** import of a valid ten-file succeeds; import of `A03` or P05 `23` fails; export round-trips; `/api/admin/catalog` is MISS 200.

### Wave 4 — Isolation + gate

#### O21 — Two Blob stores (F13)

Sell-test Blob ≠ intake `sassy-closet/store.json`. Official (when cloned) = third. A Save that writes the wrong store is silent on the host you are staring at.

#### O22 — Gate green

If [11](./11-vercel-blob-admin-qa.md) scripts are on the branch: `qa_selltest_origin_gate.py` exit **0** on sell-test **and** `qa_origin_save_drill.sh` exit **0** on Preview (A01 title nudge + restore) **and** `--look` still 0.

**Do not** POST a new Production mã to “have something to QA.”

---

## 15. Acceptance (sell-test admin)

Print. Unticked = not ready-to-sell **test**.

### 15.1 Identity

- [ ] Catalog (10) = `A01 S01 P01 P02 P03 P04 P05 K01 H01 A02` in that spirit on `/` and `/admin`
- [ ] `/m/A03` 404 · home has no A03
- [ ] Next-grid cannot publish
- [ ] No `AO001` on shop JSON

### 15.2 Merchandising

- [ ] Available $ match Boss table ([§10.1](#101-pairing-non-negotiable))
- [ ] P02 / P05 Hold · Inbox for price · no `$23`
- [ ] Qty locked 1
- [ ] Customer colors text; admin hex boxes only
- [ ] Photos real or honest empty — no invented files
- [ ] Save {MA} shows receipt; Blob sha matches

### 15.3 Cache / persist

- [ ] `/admin` `no-store` MISS
- [ ] After Save: two warms of `/` + `/m/{MA}` match admin
- [ ] Cover replace changes URL or `?v=` (etag moves)
- [ ] Redeploy does not empty the ten (Blob, not `/tmp`)

### 15.4 Settings / import

- [ ] Test only · Back to shop · Storage: Vercel Blob
- [ ] No password · no Square Save · no FB Send
- [ ] Import rejects extras / P05 23 / invented hex
- [ ] Import merge keeps shop titles when JSON titles are `""`
- [ ] Export is `catalog.v1` without cost/source

### 15.5 Look

- [ ] Messenger · Zelle · Facebook livestream · Page id unchanged
- [ ] Paper / ink / gold / blush · Cormorant + Be Vietnam Pro

---

## 16. What this LEARN never authorizes

- Mutating `excel-kit/**`, `sassy-closet/**`, live Official xlsx, Square, or intake Production
- Forking Origin shop code into this kit repo
- Inventing `A03` / `Q01` / `P06` / `AO001` / `ma=next`
- Publishing P05 at $23
- Inventing hex, titles, photo bytes, or 1drv.ms tokens
- Password wall, cart, Square Save, Facebook Post/Send
- Shared Blob with intake
- Recycle Sold mã; gộp two pieces
- Restyle to intake Allura / `#D82B60` or Shopify Horizon
- US sizes as customer default
- Committing secret env **values**

---

## 17. PASTE INTO ORIGIN AGENT

Copy between the markers. Do not paraphrase the hard stops.

```
BEGIN ORIGIN APPLY — docs/ai-clothing-shop/14-complete-admin-feature-matrix.md
TARGET: sassy-closet-shop (sell-test / shop feature branch). Do NOT edit SkyLanter/Sassy-closet excel-kit or sassy-closet intake.
LOOK: keep paper/ink/gold/blush, Cormorant + Be Vietnam Pro, Messenger, Zelle, Facebook livestream, Page 61594312648057, Boxes only hex. No restyle.

ALLOWLIST ONLY (never mint): A01 S01 P01 P02 P03 P04 P05 K01 H01 A02
HOLD (priceUsd null, Inbox for price): P02 P05
USD: A01=25 S01=28 P01=5 P03=18 P04=13 K01=37 H01=8 A02=22
QTY=1. No cart. No Square Save. No FB Send. No passwords. No $23.

APPLY ORDER (do not skip Wave 0/1):
W0  O0 look lock
    O1 disable Add A03 + Next-grid Q01 V01 K02 G01 B01 P06 H02 J01 S02 O01 D01; Save ∉ allowlist → 400; /m/A03 stays 404
W1  O2 get(catalog, { useCache: false })
    O3 put catalog allowOverwrite, addRandomSuffix false
    O4 Save {MA} receipt {ok, ma, blobWritten, catalogSha, updatedAt, revalidated[]}
    O5 revalidatePath "/" + "/c/[slug]" "page" + "/m/[ma]" "page"
    O6 router.refresh / two public warms
    O7 validate before put (ISR must not keep last-good $)
    O8 Hold ⇔ null price server-side
    O9 data-save-contract="blob+revalidate" only after O4+O5
    O10 /admin stays force-dynamic no-store
W2  O11 edit bilingual; empty JSON titles must not wipe shop copy
    O12 colors: persist text id/name; hex admin-only; colorId ∈ product or null
    O13 photos: hashed path or ?v=; tag color; reject blob: and _placeholder
    O14 Hold copy stays Inbox for price
W3  O15 no casual rename; 400 unless new mã already allowlisted+free; never A01↔AO001
    O16 settings strip: Blob badge, sha, allowlist, Import/Export/Revalidate; no secrets
    O17 POST import catalog.v1 (hard-fail extras / P05 23 / invented hex)
    O18 export catalog.v1 (no cost/source)
    O19 GET /api/admin/catalog no-store (bust cached 404)
    O20 POST /api/admin/revalidate (must not 404)
W4  O21 sell-test Blob ≠ intake Blob
    O22 Preview Save drill + restore; do not mint Production mã

CITE: 14 matrix §4–§14; 11 §18 F1–F16; 04 §6–§9; 03 §4–§11; PR #18 SELL_CATALOG_CONTRACT.md
END ORIGIN APPLY
```

---

## 18. Sister docs (do not duplicate clocks)

| # | File | Job vs this matrix |
| --- | --- | --- |
| 01 | `01-messenger-social-commerce.md` | CTA / `m.me?ref=` — Settings may expose Page URL only |
| 02 | `02-pdp-color-size-ux.md` | Customer **text** colors + gallery sync |
| 03 | `03-tiny-boutique-admin.md` | Ops playbook: add/edit/rename/status brains |
| 04 | `04-next-blob-catalog-arch.md` | ISR, three Blobs, recommended admin API |
| 05 | `05-ai-product-media.md` | Per-color bind; HQ folder law |
| 06 | `06-seo-trust-diaspora-boutique.md` | `noindex` until Boss index |
| 08 | `08-dropship-ops-runbook.md` | Staff clock — not `/admin` |
| 09 | `09-bugcheck-sell-site-checklist.md` | Tick-box QA on live chrome |
| 10 | `10-customer-pleasing-motion-ux.md` | Motion; do not restyle |
| 11 | `11-vercel-blob-admin-qa.md` | Save/cache executable gate + F1–F16 |
| 12 | `12-fb-messenger-dropship-copy.md` | Inbox phrases — site still must not Send |
| **14** | **This file** | **Complete feature matrix + Origin APPLY order** |
| Kit | [PR #18](https://github.com/SkyLanter/Sassy-closet/pull/18) `SELL_CATALOG_CONTRACT.md` | Allowlist + JSON shape |

Playbook twins on `cursor/ai-clothing-shop-playbook-92c6` use a different numbering (`03-tiny-admin-ops.md`, `08-sell-test-observed.md`). Prefer the LEARN-track numbers above when both exist.

---

## 19. Sources

<a id="s1-sell-catalog-contract"></a>

**S1.** `excel-kit/docs/SELL_CATALOG_CONTRACT.md` + `excel-kit/docs/CLONE_TO_OFFICIAL.md` on [PR #18](https://github.com/SkyLanter/Sassy-closet/pull/18) (`cursor/catalog-export-clone-official-5ad2`). `catalog.v1`, allowlist, Hold P02/P05, no invented hex/mã, “Do not modify Origin shop app code from this repo.” Not on `main` at `ba33024`.

<a id="s2-clone-to-official"></a>

**S2.** Same PR `CLONE_TO_OFFICIAL.md` — new Vercel project, own Blob, import when landed, Messenger / Zelle, no A03 mint.

<a id="s3-look-lock"></a>

**S3.** Playbook [README](./README.md) Kelly Ying tokens; [10](./10-customer-pleasing-motion-ux.md) §5; [11](./11-vercel-blob-admin-qa.md) §1.5. Live CSS: `--paper:#fff` `--ink:#111` `--blush:#f3eee8` `--gold:#b08968`.

<a id="s4-live-2026-09-09"></a>

**S4.** Live GET 2026-09-09 this run: https://sassy-closet-shop.vercel.app `/` `/admin` `/m/A03` `/api/admin/catalog` `/api/admin/revalidate`. `/admin`: 200, `private, no-store`, `x-vercel-cache: MISS`, Catalog (10), Add A03 + Next-grid, Save {MA} × 10, Boxes only, default hex `#B08968`, covers `/products/{MA}/cover.jpg`, no Import/Export/Rename/Settings. `/`: All 10, Hold P02/P05 Inbox, no `$23`, no A03, Zelle + Messenger + Facebook livestream. `/m/A03` 404 prerender. Admin APIs 404 HIT age ~6066s.

<a id="s5-schema-py"></a>

**S5.** [`excel-kit/schema.py`](../../excel-kit/schema.py) — `MA_RE` AO001, `SOT_OFFICIAL_STATUS`, `ASK_STOCK_MA`, A01 cutover comment. [`excel-kit/DESIGN_NOTES.md`](../../excel-kit/DESIGN_NOTES.md) — do not mix status dialects.

<a id="s6-intake-mint"></a>

**S6.** [`sassy-closet/lib/mint.ts`](../../sassy-closet/lib/mint.ts) + [`sassy-closet/lib/store.ts`](../../sassy-closet/lib/store.ts) `resolveSaveMa` / `saveSubmission`. Intake mint is draft-only.

<a id="s7-playbook-observed"></a>

**S7.** Playbook [08-sell-test-observed.md](./08-sell-test-observed.md) + [03-tiny-admin-ops.md](./03-tiny-admin-ops.md) — Next-grid trap, Save {MA}, Blob badge, no password.

<a id="s8-kit-md"></a>

**S8.** [`excel-kit/KIT.md`](../../excel-kit/KIT.md) — env **names** only. [`sassy-closet/README.md`](../../sassy-closet/README.md) + [`BOSS.md`](../../sassy-closet/BOSS.md) — intake Kho / CSV / never Square Save.

<a id="s9-intake-admin"></a>

**S9.** [`sassy-closet/app/admin/page.tsx`](../../sassy-closet/app/admin/page.tsx) — Tải CSV + Kho; `force-dynamic`. [`sassy-closet/lib/types.ts`](../../sassy-closet/lib/types.ts) — `status: "staged"`. [`sassy-closet/lib/kinds.ts`](../../sassy-closet/lib/kinds.ts) — letters + VN chips.

<a id="s10-sister-learn"></a>

**S10.** [03](./03-tiny-boutique-admin.md) add/edit/rename/status; [04](./04-next-blob-catalog-arch.md) §6 admin API + §7 ISR; [05](./05-ai-product-media.md) bind rule; [11](./11-vercel-blob-admin-qa.md) §18 F1–F16.

<a id="s11-next-vercel"></a>

**S11.** [Next.js ISR](https://nextjs.org/docs/app/guides/incremental-static-regeneration) · [`revalidatePath`](https://nextjs.org/docs/app/api-reference/functions/revalidatePath) · [Next.js 15 caching](https://nextjs.org/docs/15/app/guides/caching) · [Vercel Blob](https://vercel.com/docs/vercel-blob) · [consistent reads (2026-07-14)](https://vercel.com/changelog/vercel-blob-now-supports-consistent-reads-on-private-storage) · [cache status](https://vercel.com/docs/caching/cache-status).

<a id="s12-slack"></a>

**S12.** Slack `#shop-decisions` (`C0BV3GYC602`) 2026-09-04: yes/no channel; Square Free live; Track stock ON standing rule; bots draft only; Facebook stays the store. Not an `/admin` field spec.

<a id="s13-repo-readme"></a>

**S13.** [`README.md`](../../README.md) — Square Free = on-hand SoT; Official Excel ≠ warehouse; Cloud Agents + Kit; never invent mã.

Granola / Notion had no extra admin-matrix notes this run (Granola unauthorized; Notion welcome page only). Linear had no matching shop issue.

---

## 20. One-page tear sheet

```
SELL-TEST ADMIN = merchandiser for 10 mãs. Not Shopify. Not intake. Not Square.

HAVE (2026-09-09): per-mã Save, Hold/Available, EN/VN, hex boxes,
  URL/upload, Blob badge, Catalog(10), Back to shop, Test only.
GAP: Next-grid mint, Save receipt, revalidate, hashed covers,
  text color ids, import/export, catalog API, settings strip.
REFUSE: A03/Q01/…, $23, passwords, cart, Square Save, FB Send,
  invented hex/photos, A01↔AO001, shared intake Blob, restyle.

ADD     = refuse next unused. 11th mã = Stock + allowlist PR + import.
EDIT    = same mã; Boss $ table; empty JSON titles do not wipe copy.
RENAME  = closed. No box. 400 unless new code already allowlisted.
COLORS  = customer text; admin boxes; colorId ∈ product or null.
PHOTOS  = existing mã; new path or ?v=; no blob: / _placeholder.
HOLD    = null $ + Inbox. P02 P05. Available = Boss USD only.
SETTINGS= Blob/sha/allowlist + Import/Export/Revalidate. No secrets.
IMPORT  = catalog.v1 hard-fail extras. Merge empty titles.

ORIGIN ORDER: O0 look → O1 kill mint → O2–O10 Save/cache/Hold
  → O11–O14 merch → O15–O20 rename/settings/import/API → O21–O22 isolate.

#shop-decisions before Square Save or official go-live.
```

When this page and a dashboard disagree, **this page + the cited file** win until Boss changes the law in `#shop-decisions`.
