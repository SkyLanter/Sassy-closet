# 03 — Tiny-boutique admin / inventory ops

**LEARN TRACK (Ultra burn)** · learn → apply · not Shopify enterprise.

This chapter is the admin brain for a **tiny clothing boutique**: add / edit / rename a **SKU (= mã)**, set **Hold / Available / Sold**, keep a **Blob + JSON catalog**, and **export / import** without lying about stock. It maps every move onto **Sassy Closet** as it exists in [SkyLanter/Sassy-closet](https://github.com/SkyLanter/Sassy-closet) on 2026-09-09.

Sibling kit work (do not duplicate here): sell-catalog export + official clone live on open [PR #18](https://github.com/SkyLanter/Sassy-closet/pull/18) (`excel-kit/docs/SELL_CATALOG_CONTRACT.md`, `excel-kit/docs/CLONE_TO_OFFICIAL.md`). This file is the **learn→apply playbook** that PR explicitly left for `docs/ai-clothing-shop/**`.

---

## How to use this playbook

1. Read **§0 Standing law** once. If a later section seems to contradict it, the law wins.
2. Learn the **general boutique pattern** (left column of each table).
3. Apply it on **Sassy Closet** (right column + cited path).
4. Drill **§11 Failure modes** before you touch a live store. Silent save, seed drift, and duplicate codes are the three ways a 10-piece closet becomes a liar.
5. Tick **§12 Apply checklist** after any admin change. Unticked = not done.

This is **not** a Shopify POS manual, not a warehouse WMS, and not permission to mint `A03` because an admin screen says “Next mã.”

---

## 0. Standing law (read first)

| Law | Meaning on a tiny boutique | Sassy Closet mapping |
| --- | --- | --- |
| **SKU = mã** | The human code **is** the stock-keeping unit. One unique piece → one unique code. Sold codes stay retired. | Hub / sell-site: letter + 2–3 digits (`A01`). SoT Excel / Square import: `AO001` style until the A01 handoff. Sources: [`excel-kit/schema.py`](../../excel-kit/schema.py) `MA_RE`; [`sassy-closet/lib/mint.ts`](../../sassy-closet/lib/mint.ts); PR #18 `SELL_MA_RE`. |
| **Never invent mã** | If you do not have a Boss/Stock-assigned code, **stop**. Print ASK STOCK. Do not “helpfully” mint the next number. | Kit scripts require `--ma` or exit 2 ([`append_official_row.py`](../../excel-kit/sot/append_official_row.py)). Sell export **hard-fails** on extra / missing / invented codes ([PR #18](https://github.com/SkyLanter/Sassy-closet/pull/18) `sell_catalog.py`). Intake `nextMa()` exists for **hub drafts only** — it is not a license to publish `A03`. |
| **Sell-site catalog is sell-facing** | The public shop JSON answers “what may a buyer see / message about?” It is **not** a warehouse count. | `catalog.v1` on sell-test ([sassy-closet-shop.vercel.app](https://sassy-closet-shop.vercel.app)) + `/admin`. Allowlist ten mãs. Hold = no public price. Contract: PR #18 `excel-kit/docs/SELL_CATALOG_CONTRACT.md`. |
| **Square Free = on-hand SoT *later*** | When Square is wired, **Square wins every argument about how many pieces exist.** Until then, do **not** invent on-hand qty, storage, or “còn” from a staged row. | Shop law on [`README.md`](../../README.md), [`excel-kit/DESIGN_NOTES.md`](../../excel-kit/DESIGN_NOTES.md), [`excel-kit/square/README.md`](../../excel-kit/square/README.md). Intake card: empty `on_hand` → **Staged only — not on Square On_Hand yet** ([`sassy-closet/lib/on-hand.ts`](../../sassy-closet/lib/on-hand.ts)). |
| **Bots draft only** | Agents / Mini Boss copy captions and inbox text. Owner posts, sends, takes Zelle, taps Square Save. | [`excel-kit/PROMPTS.md`](../../excel-kit/PROMPTS.md); [`sassy-closet/lib/ask-fallback.ts`](../../sassy-closet/lib/ask-fallback.ts) `HARD_STOP`. |
| **No second warehouse** | Excel, JSON, Blob, and the intake site are **indexes / captions / sell copy**. They do not outvote Square on qty. | [`excel-kit/EFFICIENCY.md`](../../excel-kit/EFFICIENCY.md): “Two inventory brains” is listed as expensive. |

**One sentence for agents:** sell-site shows the closet; Square (later) counts the closet; nobody invents a mã to fill a hole.

---

## 1. Why this is not Shopify enterprise

Shopify (and Square for Retail, Lightspeed, etc.) assume:

- thousands of SKUs, variants as first-class stock rows,
- location transfers, purchase orders, cycle counts,
- an app that *is* allowed to mutate inventory,
- SKUs that can be recycled or auto-generated.

A **tiny boutique** (Sassy Closet scale: ~10 live pieces, unique garments, Facebook inbox as the store) fails those assumptions on purpose.

| Enterprise habit | Why it breaks a 10-piece closet | Boutique replacement |
| --- | --- | --- |
| Auto-SKU (`SKU-000123`) | Codes become meaningless; Stock cannot read them off a Dashboard | Human mã: `A01` / `AO001`. Unique piece = unique mã ([`DESIGN_NOTES.md`](../../excel-kit/DESIGN_NOTES.md) § Mã). |
| Variant matrix (S/M/L × 8 colors = 24 qty cells) | Unique piece is **one** row. Fake variants invent stock | One variation row per real size/color **on Square later**. Sell JSON `qty` is always `1` (PR #18). |
| App Save / webhook adjust | A bot “correcting” qty is a second warehouse | No Square Save from site or agents ([`sassy-closet/BOSS.md`](../../sassy-closet/BOSS.md)). |
| Recycle SKU after sell-through | Buyer DMs “còn A01?” six months later; you sold a *different* piece under the same code | Sold mã stays retired ([`ASK_STOCK_MA`](../../excel-kit/schema.py)). |
| Demo / sample catalog in git | Looks like live stock | `clean_sot_demo.py` + kit check “no fake inventory in git” ([`excel-kit/tests/run_checks.py`](../../excel-kit/tests/run_checks.py)). |
| One database for “everything” | Intake photos, vốn, Taobao links, and customer tiles must not share a Blob | **Separate Blobs**: intake ≠ sell-test ≠ official ([PR #18](https://github.com/SkyLanter/Sassy-closet/pull/18) `CLONE_TO_OFFICIAL.md`). |

If a tutorial says “just connect Shopify Admin API,” stop. This track is **admin for a closet that fits in OneDrive + one Blob JSON file.**

---

## 2. Surfaces and sources of truth

Draw this on a sticky note. Mixing two surfaces is how silent save and seed drift start.

```
                    ┌─────────────────────────────────────────┐
                    │  Boss / Stock assign mã                 │
                    │  Slack #shop-decisions                  │
                    └───────────────┬─────────────────────────┘
                                    │
     ┌──────────────────────────────┼──────────────────────────────┐
     ▼                              ▼                              ▼
 INTAKE HUB                    SELL CATALOG                    ON-HAND (later)
 sassy-closet.vercel.app       sassy-closet-shop               Square Free
 GF · Tìm mã · Ask             (test) + official clone         Track stock ON
 status=staged                 catalog.v1 hold\|available      qty is truth
 square=not_square             qty=1 display only              Boss Save only
 Blob: intake store            Blob: shop store                not this repo
     │                              │
     │  sassycloset.xlsx (All)      │  export_sell_catalog.py
     │  Photos/{MA}/                │  validate_sell_catalog.py
     └──────────────┬───────────────┘
                    ▼
         WORKING COPY (not warehouse)
         Sassy_Closet_SoT.xlsx  Official / Wishlist / Orders
         mã index · captions · photo_link
```

### 2.1 Surface table

| Surface | URL / path | Job | Status vocab | May mint mã? | Cited |
| --- | --- | --- | --- | --- | --- |
| **Intake** | https://sassy-closet.vercel.app · repo `sassy-closet/` | GF upload, Sửa theo mã, Tìm mã, Ask | Submission always `staged` / `not_square`. On-hand block `on_hand\|reserved\|sold\|dead` if rows exist | Hub may mint **next draft** `A01`-style on Món mới. **Must not** publish a new sell-site mã | [`sassy-closet/README.md`](../../sassy-closet/README.md), [`sassy-closet/lib/types.ts`](../../sassy-closet/lib/types.ts), [`sassy-closet/lib/store.ts`](../../sassy-closet/lib/store.ts) |
| **OD hub** | `Documents/Sassy Closet/sassycloset.xlsx` sheet **All** + `Photos/{MA}/` | Website mirror / row source for sell JSON | Hub `status=staged` is **not** sell Hold/Available | No | PR #18 `SELL_CATALOG_CONTRACT.md` |
| **Sell-test** | https://sassy-closet-shop.vercel.app · `/admin` | Customer tiles + Messenger CTA | `hold` \| `available` only in `catalog.v1` | **No.** Allowlist only | PR #18 |
| **Official shop** | *new Vercel project* (never intake DNS) | Same app family as sell-test, own Blob | Same | No | PR #18 `CLONE_TO_OFFICIAL.md` |
| **SoT Excel** | `Documents/Sassy Closet/Sassy_Closet_SoT.xlsx` | Working copy / mã index / captions | Official: `Available\|Reserved\|Sold\|Hold\|Damaged\|Donated`. Ma_List: `in_stock\|held\|sold\|archived` | **No.** `--ma` required | [`excel-kit/sot/README.md`](../../excel-kit/sot/README.md), [`schema.py`](../../excel-kit/schema.py) `SOT_OFFICIAL_STATUS` |
| **Square Free** | Square Dashboard Item library | **On-hand SoT later.** Track ON | Square qty + sellable/stockable | **No.** SKU must already be a real mã | [`excel-kit/square/README.md`](../../excel-kit/square/README.md) |

### 2.2 What each brain is allowed to answer

| Question | Ask this brain | Do **not** ask |
| --- | --- | --- |
| “What mã is this piece?” | Stock / Dashboard next-mã **or** the already-assigned code on Official / All / allowlist | Intake “Next A03”, a demo `AO999`, or a bot |
| “May a buyer see this / what’s the $?” | Sell catalog `catalog.v1` (`hold` vs `available`, `priceUsd`) | Hub `sell_usd` alone (P05’s `23` is **not** published — PR #18) |
| “Còn không? How many?” | **Square later.** Today: honest staged-only / Hold · Inbox | Intake staged row, Excel `qty_on_hand`, JSON `qty: 1` |
| “What’s the caption / photo folder?” | Official / hub `photo_link` + `Documents/Sassy Closet/Photos/{MA}/` | Invented Blob URLs, `_placeholder` files |
| “Did Lưu persist?” | Intake `/admin` storage mode **durable** + export CSV **after redeploy** | The Saved card alone |

---

## 3. SKU = mã (identity)

### 3.1 Two alphabets (do not mix in one sheet)

Sassy Closet is mid-handoff. Treat these as **different languages** until Stock finishes the A01 migration noted in [`excel-kit/schema.py`](../../excel-kit/schema.py) (comment: live `parse_ma` stays AO001; A01 is a separate handoff).

| Alphabet | Shape | Used by | Example |
| --- | --- | --- | --- |
| **SoT / Square (legacy)** | `AO\|QU\|VA\|AK\|GI\|PK\|SET` + **3** digits | `Sassy_Closet_SoT.xlsx`, Square import template, `MA_RE`, `append_official_row.py` | `AO001`, `VA012` |
| **Hub / sell-site** | One letter `A Q V D K G B P H J S O` + **2–3** digits (`A01`…`A99`, then `A100`) | Intake `parseHubMa`, sell `SELL_MA_RE`, allowlist | `A01`, `P05`, `S01` |

**Never invent a bridge.** Do not write `AO001` on the sell JSON. Do not write `A01` on a Square import row unless Stock has completed that handoff and the Item SKU **is** `A01`.

Meaning of hub letters (intake [`sassy-closet/lib/kinds.ts`](../../sassy-closet/lib/kinds.ts) + sell `KIND_TO_TYPE` on PR #18):

| Letter | Intake label | Sell `type` |
| --- | --- | --- |
| A | Áo | top |
| Q | Quần | pants |
| V | Váy | skirt |
| D | Đầm / Dress | dress |
| K | Áo khoác | jacket |
| G | Giày | shoes |
| B | Túi | bag |
| P | Phụ kiện | accessory (**P02 / P05 → `thermos`**) |
| H | Tóc | hair |
| J | Trang sức | jewelry |
| S | Set đồ | set |
| O | Khác | other |

SoT prefixes ([`MA_PREFIX_MEANS`](../../excel-kit/schema.py)): `AO` áo, `QU` quần, `VA` váy, `AK` áo khoác, `GI` giày, `PK` phụ kiện, `SET` set.

### 3.2 Identity rules (boutique-generic → Sassy)

1. **Normalize before compare.** Trim + upper. `a01` = `A01`. Intake: `normalizeMa` / `normalizeFindCode`. Kit: `parse_ma` / `normalize_sell_ma`.
2. **Padding is part of the alphabet.** `A01` ≠ `A001` ≠ `AO001`. Reject, do not coerce across alphabets.
3. **Unique piece = unique mã.** Two pink áo are `A01` and `A02`, not `A01` size S/M.
4. **Sold mã stays retired.** Reuse is a **duplicate-code** incident (§11.3), not a cleanup.
5. **Allowlist is a publication gate, not a suggestion.** First ten only: `A01 S01 P01 P02 P03 P04 P05 K01 H01 A02` ([PR #18](https://github.com/SkyLanter/Sassy-closet/pull/18)). Extra mãs on All **hard-fail** export. Missing allowlist mãs **hard-fail**. Gaps are **not** filled with invented rows.

### 3.3 Where the next mã lives (and who may read it)

| Brain | How “next” is computed | Who may use it |
| --- | --- | --- |
| SoT Dashboard | `MAXIFS` on `Official[ma_num]` + prefix, cells **B21:B27** | **Stock reads. Boss assigns.** Scripts print `ASK_STOCK_MA` ([`schema.py`](../../excel-kit/schema.py)). |
| Intake hub | `nextMa(kind, existing)` = max parsed n for that letter + 1 ([`mint.ts`](../../sassy-closet/lib/mint.ts)) | Draft on **Món mới** only. Tests assert it does not invent *extra* mãs beyond that sequence ([`store.test.ts`](../../sassy-closet/tests/store.test.ts), [`ask-and-saved.test.ts`](../../sassy-closet/tests/ask-and-saved.test.ts)). |
| Sell admin “Next mã A03” | UI convenience | **Ignore.** PR #18: “admin next A03 is ignored.” |
| Wishlist | `wish_id` / `#001` photo names — **not** a live mã | Never write `AO001` / `A01` on Wishlist ([`append_wishlist_row.py`](../../excel-kit/sot/append_wishlist_row.py) refuses `--ma`). |

`nextMa("P", ["P01","P02","P05"]) === "P06"` — it **skips the hole** at P03/P04 if those strings are absent from the *intake* list. That is correct for a draft counter and **fatal** if you treat it as Square or sell-site truth. P03 and P04 are already on the sell allowlist.

---

## 4. Add a SKU (create)

### 4.1 Boutique pattern

Adding a SKU is **three gates**, not one form submit:

1. **Identity gate** — Boss/Stock assigned a real mã (or, on intake-only drafts, the hub minted the next letter-number and you **will not** export it until assigned + allowlisted).
2. **Facts gate** — only real fields: photos that exist, colors as text, size Asia+cm, prices Boss approved. Empty is better than invented.
3. **Publication gate** — sell catalog / Square / Facebook are **separate** yeses in `#shop-decisions`.

### 4.2 Sassy Closet — intake create (Món mới)

**UI:** tab **Món mới** → fields → **Lưu & lấy mã** → **Saved · Đã lưu** sheet (big mã, Copy mã / `?ma=` link / caption starter). No Post / Send / Square Save ([`SAVED_CARD_AND_REAL_MINIBOSS_ASK_2026-09-07.md`](../../excel-kit/prompts/SAVED_CARD_AND_REAL_MINIBOSS_ASK_2026-09-07.md), [`SavedCard.tsx`](../../sassy-closet/components/SavedCard.tsx)).

**API:** `POST /api/submissions` multipart ([`app/api/submissions/route.ts`](../../sassy-closet/app/api/submissions/route.ts)) → `saveFromForm` → `saveSubmission`.

**Mã resolution** ([`resolveSaveMa`](../../sassy-closet/lib/store.ts)):

| `new_ma` / kind | Result |
| --- | --- |
| empty on create | `nextMa(kind, existing)` e.g. first Áo → `A01` |
| full code `P10` | formatted; **409** if that mã already exists |
| letter only `P` | next P |
| garbage | 400: “Mã mới: chữ P (ra P kế) hoặc đủ số kiểu P10” |

Every new row is forced:

```ts
status: "staged"
square: "not_square"
photo_link: `Documents/Sassy Closet/Photos/${ma}/`
```

([`saveSubmission`](../../sassy-closet/lib/store.ts).) Tests lock “no invented mã” and “CSV has no qty” ([`store.test.ts`](../../sassy-closet/tests/store.test.ts)).

**Photos:** stored as `{ma}/001.jpg` on disk or Blob. Hashes recorded for find-by-photo. Never invent missing files ([`copyStoreAndPhotos` skips missing bytes](../../sassy-closet/lib/store-backend.ts)).

**Hard stops on create**

- Do not treat Saved card as “it’s on the shop” or “it’s on Square.”
- Do not commit the row to git.
- Do not export `catalog.v1` until the mã is **allowlisted** and Boss priced it.
- Do not copy vốn / Taobao `source_link` onto the customer JSON (PR #18 omit list).

### 4.3 Sassy Closet — Official / Square add (owned piece)

After Boss says the piece is bought/received **and** mã is assigned:

```bash
python3 excel-kit/sot/append_official_row.py -w "$SASSY_SOT" \
  --ma AO001 --name-vi "…" --size "M" --color "đen" --qty 1 --status Available
```

- Missing `--ma` → exit 2 + `ASK_STOCK_MA` ([`append_official_row.py`](../../excel-kit/sot/append_official_row.py)).
- Mã already on the sheet → exit 2: “already on … row N. Do not invent a new mã.”
- `--status` default `Available`; must be in `SOT_OFFICIAL_STATUS`.
- `qty_on_hand` is a **working-copy note**. Script prints: Square still wins; do not Save from the script.

Square import (later, Boss yes in `#shop-decisions`):

- Fresh blank library from Square (live headers win).
- SKU = exact mã. Item Name = `mã` + short name. Variation = Asia size + color.
- `Stockable=Y`. Never put `No` in `New Quantity [Location]` (that **disables** tracking).
- Token blank on create. Headers-only template in git ([`excel-kit/square/README.md`](../../excel-kit/square/README.md), [`validate_import.py`](../../excel-kit/square/validate_import.py)).
- Filled CSV stays off git (`Documents/Sassy Closet/square-drafts/`).

### 4.4 Sassy Closet — sell catalog add

You **do not** add a product by typing JSON. You:

1. Get the mã onto OD hub **All** (Boss/Stock).
2. Get Boss USD (or Hold).
3. Widen the allowlist in kit **on purpose** (code change + `#shop-decisions`) — today the allowlist is closed at ten.
4. Re-run export + validate (PR #18 scripts).
5. Import on sell-test / official `/admin` (Origin shop). Kit does not push Origin.

Until step 3, a new Official row is **not** a shop tile.

---

## 5. Edit a SKU (same identity)

### 5.1 Boutique pattern

Edit = change **facts** without changing **who the piece is**. Rename is a different operation (§6).

Safe to edit: color text, size string, blurbs, cost/sell on the **hub** (vốn never goes to the shop), photos (keep vs replace), Hold↔Available **when Boss says**.

Unsafe to edit quietly: mã, Square token, qty presented as counted, another piece’s photos.

### 5.2 Sassy Closet — intake Sửa theo mã

**UI:** tab **Sửa theo mã** → type mã → **Mở** → edit → **Lưu**. Optional **Đổi mã** field is rename, not edit ([`IntakeApp.tsx`](../../sassy-closet/components/IntakeApp.tsx)). Deep link `/?ma=A01` opens this tab.

**API:** `GET /api/submissions/{ma}` then `PATCH` multipart with `existingMa` set. Missing mã → 404 “Không tìm thấy mã này.”

**Keep-photos:** `keep_photos` JSON list of relative paths. Empty keep + no new files **clears hashes** (intentional wipe, not silent). Invalid JSON → `[]` (**silent empty** — see §11.1).

**Source link:** full Taobao share paste is reduced to the URL only ([`normalizeSourceLink`](../../sassy-closet/lib/source-link.ts), [`source-link.test.ts`](../../sassy-closet/tests/source-link.test.ts)). Empty stays empty — never invent a link.

**Tìm mã card** is read-only: `GET /api/ma/{code}` returns `{ staged, on_hand, staged_only }`. Soft miss: **Không tìm thấy mã**. Empty on-hand does **not** fabricate Square rows ([`FIND_MA_CARD_2026-09-08.md`](../../excel-kit/prompts/FIND_MA_CARD_2026-09-08.md), [`find-ma-card.test.ts`](../../sassy-closet/tests/find-ma-card.test.ts)). Status string `Available` on a raw on-hand object is **dropped** (not in `on_hand|reserved|sold|dead`) — do not treat Excel Official status as intake on-hand status.

### 5.3 Sassy Closet — Official edit

There is **no** “upsert on append.” `append_official_row.py` refuses duplicates. Update the existing row in Excel (or a future dedicated updater). Do not append `AO001` a second time under a new invented code.

### 5.4 Sassy Closet — sell catalog edit

Re-export from **All** after Boss changes price/Hold. Validate. Import again on the shop. Do not hand-edit `out/sell-catalog.v1.json` to “fix” a title — the hub has no title columns; empty titles are honest ([PR #18](https://github.com/SkyLanter/Sassy-closet/pull/18)). Do not copy `flag` notes onto customer description.

Price rule ([`resolve_sell_status_and_price`](https://github.com/SkyLanter/Sassy-closet/blob/cursor/catalog-export-clone-official-5ad2/excel-kit/sell_catalog.py) on PR #18):

- Boss allowlist `None` (P02, P05) → **hold**, `priceUsd=null`. Xlsx `23` on P05 is **ignored** (note), not published.
- Boss has a USD and xlsx empty → available at Boss USD (note).
- Xlsx disagrees with Boss USD → **hard-fail**. Do not invent a compromise price.

---

## 6. Rename a SKU (identity change)

Rename is the most dangerous admin op in a tiny closet. Every photo path, caption, Square SKU, Messenger thread, and export row keys off the code.

### 6.1 Boutique pattern

1. Confirm the **old** mã is the same physical piece.
2. Confirm the **new** mã is Boss/Stock-assigned and **free** (not Sold, not another live row).
3. Rename **metadata and bytes** together, or not at all.
4. Re-export / re-import every published surface.
5. Leave a forwarding note in working copy (`notes`: “was A01”) if buyers still DM the old code. Do **not** create a second live SKU for the old code.

### 6.2 Sassy Closet — intake rename

**UI:** Sửa → **Đổi mã · Change code** (`data-testid="rename-ma"`). Placeholder: `P` or `P10`. Changing **kind** while editing suggests `nextMa(nextKind, knownMas)` into the rename box ([`onKind`](../../sassy-closet/components/IntakeApp.tsx)) — that is a **draft suggestion**, not an assignment.

**API:** PATCH with `new_ma`. `resolveSaveMa`:

- same formatted mã → no-op identity,
- taken mã → **409** `Mã {x} đã có rồi — không gộp nha`,
- kind letter only → next of that kind.

**Photo caveat (apply this, do not ignore it):** `saveSubmission` writes **new** photo bytes under the **new** `{ma}/001.jpg`. Existing `keep_photos` paths still point at the **old** `{oldMa}/001.jpg` unless you rewrite them. After rename, open Tìm mã + `/api/photos/...` for **both** codes. If thumbs 404, re-upload or copy bytes — **never invent** replacement images.

Saved card after rename shows the **new** mã ([Saved card contract](../../excel-kit/prompts/SAVED_CARD_AND_REAL_MINIBOSS_ASK_2026-09-07.md)).

### 6.3 Sassy Closet — Official / Square / sell rename

Kit **does not** auto-rename Official or Square.

- Official: change the `ma` cell **and** `ma_num` / `prefix` / `square_name` / `photo_file` / `photo_link` together. Dashboard next-mã uses `Official[ma_num]`.
- Photos folder: `Photos/AO001/` → `Photos/A01/` (or new SoT name) as a real filesystem move on OneDrive.
- Square later: SKU change is an Item library edit (or re-import with care). **Do not** leave the old SKU sellable.
- Sell JSON: mã is the product id. A rename is “remove old allowlist entry + add new” — today the allowlist is fixed. **Do not** mint a parallel tile.

---

## 7. Status: Hold / Available / Sold

Tiny-boutique **sell-facing** life cycle is three words. Everything else is a **dialect**. Do not mix dialects on one sheet ([`DESIGN_NOTES.md`](../../excel-kit/DESIGN_NOTES.md): “Do not mix the two in one sheet”).

### 7.1 The three sell-facing states

| State | Buyer meaning | Price | On-hand implication |
| --- | --- | --- | --- |
| **Hold** | Visible or inbox-only, **not** offered at a public $. “Inbox for price” / thermos hold / waiting Boss. | `null` / omitted | Does **not** mean counted in Square. |
| **Available** | Offered. Messenger CTA ok. | Boss USD | Still not a warehouse count. `qty=1` on JSON is “this unique piece,” not a cycle count. |
| **Sold** | Identity **retired**. Not for sale. Do not reuse mã. | — | Square later: qty 0 / not sellable. Official `Sold`. Ma_List `sold`. |

`catalog.v1` **today** encodes only `hold|available` ([PR #18](https://github.com/SkyLanter/Sassy-closet/pull/18) validate: `status must be hold|available`). **Sold** is enforced on Official / Ma_List / (later) Square, not by deleting the mã from history. A sold piece should **leave** the public allowlist (or a future `sold` shop status) — do not republish it as Available.

### 7.2 Dialect map (cite before you type a dropdown)

| Dialect | Values | Maps toward Hold / Available / Sold | Source |
| --- | --- | --- | --- |
| **Sell `catalog.v1`** | `hold`, `available` | Direct Hold / Available. No Sold yet | PR #18 `sell_catalog.py` |
| **Official SoT** | `Available`, `Reserved`, `Sold`, `Hold`, `Damaged`, `Donated` | Available→Available; Hold+Reserved→Hold (not for sale / held for someone); Sold→Sold; Damaged/Donated→retired (Ma_List `archived`) | [`SOT_OFFICIAL_STATUS`](../../excel-kit/schema.py), [`OFFICIAL_TO_MA_LIST_STATUS`](../../excel-kit/schema.py) |
| **Ma_List (lean desktop)** | `in_stock`, `held`, `sold`, `archived` | in_stock→Available; held→Hold; sold→Sold; archived→retired | [`MA_LIST_STATUS`](../../excel-kit/schema.py) |
| **Intake submission** | always `staged` | **Not** Hold/Available. Means “hub draft / not Square” | [`types.ts`](../../sassy-closet/lib/types.ts) |
| **Intake on_hand** | `on_hand`, `reserved`, `sold`, `dead` | on_hand≈Available (if Square later says so); reserved≈Hold; sold→Sold; dead→retired | [`ON_HAND_STATUSES`](../../sassy-closet/lib/types.ts) |
| **Wishlist / Candidates** | `candidate`, `watching`, `skip`, `bought` | **Not stock.** `bought` still off Square until Save yes | [`SOT_WISHLIST_STATUS`](../../excel-kit/schema.py), [`GF_CLOTHES_INTAKE.md`](../../excel-kit/prompts/GF_CLOTHES_INTAKE.md) |
| **Orders** | `Inquiry`, `Reserved`, `Paid`, `Shipped`, `Picked up`, `Cancelled` | Order life cycle, **not** SKU life cycle. Reserved order ≠ Official Hold unless Stock says so | [`ORDER_STATUS`](../../excel-kit/schema.py) |
| **Square later** | sellable / stockable / qty | Qty is SoT. `New Quantity='No'` is Track-OFF (illegal here) | [`square/README.md`](../../excel-kit/square/README.md) |

Official → Ma_List ([`OFFICIAL_TO_MA_LIST_STATUS`](../../excel-kit/schema.py)):

```
Available → in_stock
Reserved  → held
Sold      → sold
Hold      → held
Damaged   → archived
Donated   → archived
```

### 7.3 First-ten sell status (Boss table)

Cited from [PR #18](https://github.com/SkyLanter/Sassy-closet/pull/18) `SELL_ALLOWLIST_PRICE_USD`:

| Mã | USD | Sell status |
| --- | --- | --- |
| A01 | 25 | Available |
| S01 | 28 | Available |
| P01 | 5 | Available |
| **P02** | — | **Hold** |
| P03 | 18 | Available |
| P04 | 13 | Available |
| **P05** | — | **Hold** (xlsx `23` must not publish) |
| K01 | 37 | Available |
| H01 | 8 | Available |
| A02 | 22 | Available |

Dashboard working-copy counts (not Square) live in Official `COUNTIF` / `SUMIF` ([`schema.py`](../../excel-kit/schema.py) Dashboard rows 6–8, 11). `dashboard_brief.py` prints **cached** Excel values or tells Boss to copy `B43` — it does not invent counts ([`PROMPTS.md`](../../excel-kit/PROMPTS.md) §5).

### 7.4 Status change playbook

| From → to | Who says yes | What you update | What you do **not** do |
| --- | --- | --- | --- |
| staged → Available (sell) | Boss price + allowlist + `#shop-decisions` | Hub `sell_usd`, re-export JSON, shop import | Invent $; Square Save |
| Available → Hold | Boss | Allowlist price `None` or empty sell + re-export | Leave old $ on the tile |
| Hold → Available | Boss USD | Allowlist + xlsx agree + re-export | Use xlsx 23 on P05 |
| Available → Sold | Sale actually happened (Owner) | Official `Sold`; Ma_List `sold`; Square qty later; **remove or stop selling** on shop | Reuse mã; mint a “new A01” |
| Sold → Available | **Almost never.** New piece = **new mã** | — | Recycle SKU |
| Wishlist bought → Official | Stock mã + Boss | `append_official_row.py --ma`; still off Square until Save yes | Write mã on Wishlist; claim Square stock |

---

## 8. Blob and JSON catalogs

A tiny boutique does **not** need Postgres. It needs **one durable document** (JSON) + **photo bytes**, and it needs to know **which Blob** is which.

### 8.1 Three storage modes (intake)

[`storageMode()`](../../sassy-closet/lib/store-backend.ts):

| Mode | When | Durable? | Failure if you pretend it is production |
| --- | --- | --- | --- |
| **durable** | `BLOB_READ_WRITE_TOKEN` or `BLOB_STORE_ID` set | Yes | — |
| **local** | laptop, no Vercel | Survives restarts in `sassy-closet/data/` (gitignored) or `SASSY_DATA_DIR` | Pushing this folder does not fix Production |
| **ephemeral** | `VERCEL` set, no Blob | **No.** `/tmp/sassy-closet-data` wiped every Production redeploy | Saved card lies; export goes to 0; photos 404 ([`sassy-closet/README.md`](../../sassy-closet/README.md) Durable store) |

**One store, two object kinds** (Hobby-friendly):

| Object | Path | Cache |
| --- | --- | --- |
| Catalog JSON | `sassy-closet/store.json` | `cacheControlMaxAge: 0`, overwrite, no random suffix |
| Photos | `sassy-closet/photos/{ma}/{file}` | cached get |

Env **names** only ([`excel-kit/KIT.md`](../../excel-kit/KIT.md), [`sassy-closet/README.md`](../../sassy-closet/README.md)): `BLOB_READ_WRITE_TOKEN`, `BLOB_STORE_ID`, optional `BLOB_ACCESS` (`private` default).

`GET /api/submissions` returns `storage: { mode, durable, warning? }`. `/admin` prints **Kho**.

### 8.2 Intake `StoreFile` shape

```ts
{
  nextId: number,
  submissions: Submission[],  // mã metadata; status always staged
  fx: { usd_cny, updated },
  on_hand?: Record<ma, OnHandRow[]>  // only if someone stored real rows
}
```

([`store-backend.ts`](../../sassy-closet/lib/store-backend.ts) `StoreFile`.) `on_hand` is **optional**. Missing bag → Tìm mã shows staged-only. **Do not** backfill from staged sizes/colors ([`find-ma-card.test.ts`](../../sassy-closet/tests/find-ma-card.test.ts)).

`parseStore` **refuses** garbage (`{not-json`, `{}` without `submissions`) with “không ghi đè” — a corrupt Blob must not become an empty closet write ([`store.test.ts`](../../sassy-closet/tests/store.test.ts)). A **missing** Blob (404) is treated as empty (`isMissingBlobError`), which is a **different** failure — see silent save.

### 8.3 Sell `catalog.v1` JSON (sell-facing)

Envelope (PR #18):

```json
{
  "schema": "catalog.v1",
  "source": "Documents/Sassy Closet/sassycloset.xlsx",
  "exportedAt": "2026-09-09T00:00:00Z",
  "allowlist": ["A01", "S01", "P01", "P02", "P03", "P04", "P05", "K01", "H01", "A02"],
  "products": [ /* exactly those 10, that order */ ]
}
```

Product fields: `ma`, `titleEn`, `titleVn`, `descriptionEn`, `descriptionVn`, `type`, `status` (`hold|available`), `priceUsd` (number or `null`), `qty` (always 1), `colors[{id,name}]` (no invented hex), `images[{src,colorId,order}]`.

**Omit from customer JSON:** `source_link`, cost/vốn, customer names, hub `status=staged`, `flag`, `next_desk`.

Image `src` is an OneDrive relative path (`Documents/Sassy Closet/Photos/A01/001.jpg`), **not** a public URL. Official clone uploads to **that project’s** Blob, then rewrites src ([`CLONE_TO_OFFICIAL.md`](https://github.com/SkyLanter/Sassy-closet/blob/cursor/catalog-export-clone-official-5ad2/excel-kit/docs/CLONE_TO_OFFICIAL.md)). Skip `_placeholder`, `_probe`, `.keep`, `README`.

### 8.4 Do not share Blobs

| Project | Blob holds | Connect to |
| --- | --- | --- |
| Intake `sassy-closet` | GF submissions + intake photos | Intake Production only |
| Sell-test `sassy-closet-shop` | Sell catalog + shop photos | Sell-test only |
| Official (new) | Official catalog + shop photos | Official only |

[`CLONE_TO_OFFICIAL.md`](https://github.com/SkyLanter/Sassy-closet/blob/cursor/catalog-export-clone-official-5ad2/excel-kit/docs/CLONE_TO_OFFICIAL.md): do not point official at intake Blob; do not steal intake DNS; one-time test→official copy is Origin’s job, allowlist only.

Redeploy proof (intake): Lưu → `/admin` CSV lists mã → Production **Redeploy** → same mã + `/api/photos/{ma}/001.jpg` still 200 ([`sassy-closet/README.md`](../../sassy-closet/README.md)). If this fails, you are in ephemeral mode no matter what the Saved card said.

---

## 9. Export

Export is **read + serialize**. It must not invent rows to look complete.

### 9.1 Intake CSV (hub backup, not shop)

- UI: `/admin` → **Tải CSV** ([`app/admin/page.tsx`](../../sassy-closet/app/admin/page.tsx)).
- API: `GET /api/export` → `exportCsv()` ([`store.ts`](../../sassy-closet/lib/store.ts)).
- Columns: `ma,kind,kind_vi,size,color,color_note,color_pieces,blurb,cost_*,sell_*,source_link,status,square,created_at,updated_at,photo_link`.
- **No qty column** (test assertion). `photo_link` is a **folder path**, not bytes.
- Only rows that survived **Lưu & lấy mã**.

Use: laptop restore, Kit, human backup. **Not** a Square import and **not** `catalog.v1`.

### 9.2 Sell `catalog.v1` (shop handoff)

On [PR #18](https://github.com/SkyLanter/Sassy-closet/pull/18) (not on `main` until merge):

```bash
python3 excel-kit/scripts/export_sell_catalog.py \
  -w "$HOME/OneDrive/Documents/Sassy Closet/sassycloset.xlsx" \
  --photos-dir "$HOME/OneDrive/Documents/Sassy Closet/Photos" \
  -o ./out/sell-catalog.v1.json

python3 excel-kit/scripts/validate_sell_catalog.py ./out/sell-catalog.v1.json
```

Rules baked in:

- Read **All** only. Kind tabs are duplicates — merging would double-count (`CatalogError`: do not invent rows from kind tabs).
- Explicit `-w` that is **missing** exits 2 — **no silent** OneDrive / env / cwd fallback (Bugbot fix; `candidate_catalog_paths`).
- Missing workbook (no `-w`) prints run steps; **no fake catalog**.
- Duplicate mã on All → fail.
- Missing / extra allowlist mã → fail.
- Kind letter must match mã letter.

Committed artifact (that branch): `out/sell-catalog.v1.json` + `excel-kit/samples/sell-catalog.v1.json` (must match). Other `/out/*` stays gitignored.

### 9.3 Square library export (later)

Stock downloads a **fresh blank** (or current) library from Square so location headers match (`Enabled [Sassy Closet]`, `New Quantity [Sassy Closet]`). The repo template is a **reminder**, not the live header set ([`square/README.md`](../../excel-kit/square/README.md)). Never commit a filled export.

### 9.4 Excel / Dashboard export

`dashboard_brief.py` exports **cached** counts. If formulas have not calculated, Boss copies `Dashboard!B43`. Inventing a morning number is a **silent save** of a fake brief.

---

## 10. Import

Import is **write**. Default stance: **hard-fail** > silent merge.

### 10.1 Intake restore (after ephemeral wipe)

Blob + current code **cannot** resurrect mãs `/tmp` already deleted ([`sassy-closet/README.md`](../../sassy-closet/README.md) Restore).

1. **Laptop leftover** `data/submissions.json` + `photos/` → set Blob envs → hit any API once. Migrate copies **only if destination Blob is empty** (`migrateLocalToDurableIfNeeded`). Never invent missing photos.
2. **CSV + re-upload** — fields only. For each real row: Món mới or `POST /api/submissions` with the **same** fields GF had + **real** photo files. Same APIs as Lưu. Do not invent $, qty, or photos.
3. Going forward: `/admin` export after important saves.

### 10.2 Shop import `catalog.v1`

Origin sell-site `/admin` **import catalog.v1** (when landed). Until the button exists, Mini Boss imports on Origin — **do not** fork shop code in this kit repo ([PR #18](https://github.com/SkyLanter/Sassy-closet/pull/18) `CLONE_TO_OFFICIAL.md`).

After import:

- Confirm **exactly** the ten allowlist mãs.
- Hold on P02 / P05; no $23 on P05.
- Upload real photos; tiles stay letter-placeholders until bytes exist.
- `validate_sell_catalog.py` PASS on the JSON you imported.

### 10.3 Square import (later)

`validate_import.py` on a **local** draft: SKU is mã, Stockable Y, Token blank, `New Quantity` is never `No`. Then `#shop-decisions` **yes**, then Owner Save. Success ≠ “Excel is inventory.”

### 10.4 GF packet import

`gf_intake_apply.py`: parse template, never invent fields or mã. `looking` → Wishlist. `bought` without mã → Wishlist `bought` + ASK STOCK. `bought` with Stock mã → Official append. `--dry-run` must not write xlsx ([`GF_CLOTHES_INTAKE.md`](../../excel-kit/prompts/GF_CLOTHES_INTAKE.md)).

### 10.5 Import conflict matrix

| Incoming | Existing | Action |
| --- | --- | --- |
| Same mã, same piece, newer facts | Hub / Blob row | Update in place (PATCH / Official edit) |
| Same mã, **different** piece | Any | **Stop.** Duplicate-code incident |
| New mã not allowlisted | Sell catalog | Do not import to shop |
| New mã not Boss-assigned | Official | ASK STOCK; do not append |
| CSV row, no photos | Production Blob | Import fields only; photos stay missing (honest 404) — do not generate images |
| Kind-tab rows + All rows | Export | Never merge |

---

## 11. Failure modes

These three clusters cause almost every “the site lied” report on a boutique this size.

### 11.1 Silent save

**Definition:** the UI or CLI **looks** like it persisted, but the durable brain did not get the bytes you think — or it persisted to the **wrong** brain.

| Symptom | Actual cause | How to detect | Fix / prevent | Cited |
| --- | --- | --- | --- | --- |
| Saved · Đã lưu shows `A01`, redeploy → export 0, photos 404 | Production wrote `/tmp` (ephemeral). Saved card does not check `storage.durable` | `/admin` Kho line; `GET /api/submissions` → `storage.durable`; redeploy proof | Connect **Private** Blob to Production; Redeploy; verify mã survives | [`sassy-closet/README.md`](../../sassy-closet/README.md), [PR #15](https://github.com/SkyLanter/Sassy-closet/pull/15) |
| `/admin` says durable but catalog empty after “restore” | `get` 404 → `null` → `emptyStore()`; migrate skipped because dest already had `[]` **or** dest had leftovers | Compare laptop JSON count vs `listSubmissions` | Do not treat empty Blob as success; migrate only from a known leftover; never invent rows to fill | [`isMissingBlobError`](../../sassy-closet/lib/store-backend.ts), `migrateLocalToDurableIfNeeded` |
| Edit “saved” but photos vanished | `keep_photos` JSON parse failed → `[]` | Photo count before/after PATCH | Valid JSON array; test keep path ([`form-save.ts`](../../sassy-closet/lib/form-save.ts), [`source-link.test.ts`](../../sassy-closet/tests/source-link.test.ts)) | same |
| Edit “saved” but pieces emptied | `pieces` invalid JSON → `[]` | — | Same silent parse | [`form-save.ts`](../../sassy-closet/lib/form-save.ts) |
| Export CSV “has the item” but restore has no images | CSV `photo_link` is a folder string | Try `/api/photos/{ma}/001.jpg` | Re-upload bytes; CSV is not a media backup | [`exportCsv`](../../sassy-closet/lib/store.ts) |
| Square import “succeeded” but Track is off | `New Quantity [Loc]=No` | Square item Track toggle | `validate_import.py` fails that row | [`validate_import.py`](../../excel-kit/square/validate_import.py) |
| Square qty unchanged | Imported `Current Quantity` (ignored) instead of `New Quantity` | Square on-hand vs CSV | Use `New Quantity [Location]` | [`square/README.md`](../../excel-kit/square/README.md) |
| Catalog export wrote a **different** closet | `-w` typo + fallback to another xlsx | Source path printed on OK line | PR #18: explicit `-w` missing → exit 2, no fallback | `candidate_catalog_paths` |
| Wishlist row has no link and you thought you passed one | URL dropped without `--no-source` | Script contract | Must pass `--source` or `--no-source` | [`append_wishlist_row.py`](../../excel-kit/sot/append_wishlist_row.py) |
| Dry-run Official “looks saved” | `dry-run: not saved` on stdout, file untouched | Read the last lines | Require `saved {path}` | [`append_official_row.py`](../../excel-kit/sot/append_official_row.py) |
| Morning brief numbers feel firm | openpyxl printed stale cache | Excel calculated? | Copy `B43` from open Excel | [`PROMPTS.md`](../../excel-kit/PROMPTS.md) §5 |
| Ask says “còn A01” | Local fallback from **staged** presence | Reply text includes “staged, not Square” | Do not send as stock fact | [`ask-fallback.ts`](../../sassy-closet/lib/ask-fallback.ts) |
| Corrupt `store.json` “fixed itself” to empty | **Must not.** `parseStore` throws không ghi đè | 500 on read | Restore from CSV/laptop; do not PUT `{}` | [`parseStore`](../../sassy-closet/lib/store-backend.ts) |

**Operator habit:** after every important Lưu, download CSV **and** hit one photo URL **and** read Kho. After every catalog export, read the `source:` line and `validate` PASS.

### 11.2 Seed drift

**Definition:** two brains that should describe the same closet **diverged**, usually because a seed, demo, counter, or duplicate sheet was treated as live.

| Drift | How it happens | Tell | Repair |
| --- | --- | --- | --- |
| **Demo seed in Official** | Kit-seeded `demo` / `sample` / `AO999` / `AO000` left in the book | `looks_like_demo_row`; Dashboard counts look like stock | `clean_sot_demo.py` ([`DEMO_ROW_TOKENS`](../../excel-kit/schema.py), [`DESIGN_NOTES.md`](../../excel-kit/DESIGN_NOTES.md)) |
| **Wording seed** | Old cells say “Excel is inventory” | `SQUARE_WORDING_PATCHES` | `clean_sot_demo.py` patches; skip cells that already state Square Free |
| **Alphabet drift** | Agent writes `AO001` on sell JSON or `A01` on Square pre-handoff | Validate / `MA_RE` / `SELL_MA_RE` fail | Keep lanes separate ([`schema.py`](../../excel-kit/schema.py) handoff comment) |
| **Counter drift** | Intake `nextMa` vs Dashboard B21:B27 vs sell allowlist vs admin “Next A03” | Next draft is `A03` while A02 is already sold-facing | **Stock/allowlist win.** Ignore admin next |
| **Hole drift** | `nextMa` skips unused numbers (`P05` present → `P06`) while P03/P04 live on shop | New intake mã collides with allowlist or leaves holes | Do not publish intake next; ASK STOCK |
| **Kind-tab drift** | Export merges Áo + All | Duplicate mã fail (good) or doubled tiles (if someone bypasses) | All sheet only |
| **Price seed drift** | Hub `sell_usd` 23 vs Boss Hold on P05 | Export notes or hard-fail | Allowlist wins; do not publish 23 |
| **Title seed** | Agent invents `titleEn` because hub column is missing | JSON titles non-empty but hub has no such columns | Leave empty; do not invent shop copy |
| **Blob seed** | Official pointed at intake or sell-test Blob | Wrong 10 / GF rows on the shop | New Blob per project |
| **Sample vs live JSON** | `excel-kit/samples/sell-catalog.v1.json` edited by hand | Kit check: sample must match `out/` | Re-export from live All |
| **Photo junk seed** | `_placeholder.jpg` / `_probe` treated as product art | Tile shows junk | Skip prefixes `_` and `.` (PR #18 `SKIP_IMAGE_PREFIXES`) |
| **On-hand seed** | Building Square rows from staged sizes/colors | Tests forbid this | Empty `on_hand` stays empty |
| **Git inventory seed** | Filled Square CSV or live Official rows committed | `check_no_fake_inventory_in_git` | Delete from git; keep on OneDrive |

**Standing cleaners:** `python3 excel-kit/clean_sot_demo.py …` and `python3 excel-kit/tests/run_checks.py`. After any demo seed, phone-safe prompt says to run the cleaner ([`BOUTIQUE_PHONE_SAFE.md`](../../excel-kit/prompts/BOUTIQUE_PHONE_SAFE.md)).

### 11.3 Duplicate codes

**Definition:** two live meanings for one mã, or one piece with two live mãs, or a Sold code brought back.

| Incident | Detector | Required response |
| --- | --- | --- |
| Intake rename onto an existing mã | 409 `đã có rồi — không gộp` | Keep both pieces; pick a **new assigned** mã |
| Official append of existing mã | exit 2 “already on … row N” | Update that row or ASK STOCK — **do not** invent |
| All sheet two rows same mã | `CatalogError: duplicate mã on All sheet` | Dedup on the hub; do not export |
| All + kind tab merged | same, or doubled products | Never merge |
| `a01` vs `A01` vs `A001` vs `AO001` | normalize within **one** alphabet; reject cross-alphabet | Treat as different until Stock maps the handoff |
| Sold mã reused for a new garment | Buyer DMs, Square history, Official `Sold` | **New mã.** Old stays Sold |
| Square SKU ≠ hub mã | validate_import + human diff | Fix Square or hub; do not invent a third code |
| Photo folder `{old}` + JSON `{new}` after rename | 404 / leftover folder | Move bytes; do not upload a random image to “fill” |
| Two Blobs both holding `A01` as different garments | Compare photos + cost + source | Pick the Boss piece; wipe the other **after** backup |
| Wishlist live mã | `append_wishlist_row.py` refuses `--ma` | Bought → Official with assigned mã |

**Gộp (merge) is forbidden** on intake by product copy: “không gộp nha.” Two pieces do not become one SKU because the codes match.

### 11.4 Failure-mode drill (15 minutes)

Do this on Preview / laptop, not as a reason to invent Production data.

1. Save one **fake-shaped** local row with a **real test** photo in `SASSY_DATA_DIR` (not a live mã you do not own). Confirm `submissions.json` + `photos/`.
2. Unset Blob envs, set `VERCEL=1` in a unit test mindset: `storageMode()==="ephemeral"` ([`store.test.ts`](../../sassy-closet/tests/store.test.ts)).
3. Confirm `parseStore("{not-json")` throws không ghi đè.
4. Confirm `sanitizeOnHandRows({qty:99},"A01")` is `[]`.
5. Confirm `maExists` / 409 path in `resolveSaveMa`.
6. On PR #18 branch: `validate_sell_catalog.py` PASS; mentally add `A03` — export must fail.
7. Read `/admin` copy: “Không Post, không Square Save.”

---

## 12. Apply checklist — Sassy Closet

Print. Unticked means the closet may be lying.

### 12.1 Before any admin session

- [ ] I know which surface I am on (intake / hub xlsx / sell-test / official / SoT / Square).
- [ ] I will not invent a mã, $, qty, photo, hex, title, or share token.
- [ ] Square Save and Facebook Post/Send are **off the table** for agents.
- [ ] Secrets stay out of git / PR / chat ([`KIT.md`](../../excel-kit/KIT.md)).

### 12.2 Add

- [ ] Mã is Boss/Stock-assigned **or** this is intake-only draft and will **not** be exported.
- [ ] If Official: `append_official_row.py --ma` succeeded; not a duplicate row.
- [ ] If sell: mã already on allowlist (or allowlist change was an explicit PR + `#shop-decisions`).
- [ ] Photos are real files in `Photos/{MA}/`, not placeholders.
- [ ] Submission/shop status is honest (`staged` vs `hold`/`available`).

### 12.3 Edit

- [ ] Loaded the **same** mã I meant (Tìm mã / Mở).
- [ ] Did not clear `keep_photos` by accident.
- [ ] Did not publish P05 at $23 or any other allowlist violation.
- [ ] Re-exported / re-imported if sell-facing fields changed.

### 12.4 Rename

- [ ] New mã assigned and free (409/duplicate checks).
- [ ] Photo bytes exist under the **new** folder.
- [ ] Official `ma` + `ma_num` + `photo_link` + Square SKU (later) updated together.
- [ ] Old mã not left Available on any public surface.

### 12.5 Status

- [ ] Used the **dialect** of the sheet I am editing (§7.2).
- [ ] Hold ⇒ `priceUsd` null on shop JSON.
- [ ] Sold ⇒ mã retired; not reused; shop tile not Available.
- [ ] Wishlist `bought` ≠ Square on-hand.

### 12.6 Blob / export / import

- [ ] Intake Production: Kho **durable**; redeploy proof done at least once on this project.
- [ ] Official shop has **its own** Blob (never intake).
- [ ] `catalog.v1` validate PASS; source path is the intended xlsx.
- [ ] CSV backup downloaded after important intake saves.
- [ ] Square draft (later) validated; `#shop-decisions` yes before Save.

### 12.7 After go-live (official)

From PR #18 clone checklist (abridged): new Vercel project; Blob connected; exactly ten mãs; prices match Boss table; Hold P02/P05; real photos; Messenger CTA; Zelle word; **no personal name**; intake still GF; no Square Save.

---

## 13. What this track never authorizes

- Shopify (or any enterprise IMS) as the mental model.
- Inventing `A03` / `AO999` / `next` / `ma=next` ([`run_checks.py`](../../excel-kit/tests/run_checks.py) refuses `ma=next`).
- Treating intake Lưu, Excel `qty_on_hand`, or JSON `qty: 1` as Square on-hand.
- Pointing official DNS or Blob at intake.
- Merging kind tabs, gộp-ing two pieces, recycling Sold mãs.
- Committing live Official rows, customer names, Square tokens, filled import CSVs, or secret env **values**.
- Agents tapping Square Save, Facebook Post/Send, or Zelle.
- Inventing titles, hex swatches, photo bytes, or 1drv.ms tokens.
- US sizes quoted to buyers (Asia + cm only).

---

## 14. Source index

Primary law (on `main` unless noted):

| Source | What it proves |
| --- | --- |
| [`README.md`](../../README.md) | Square Free = on-hand SoT; Official Excel ≠ warehouse; never invent mã; Cloud Agents + Kit |
| [`excel-kit/DESIGN_NOTES.md`](../../excel-kit/DESIGN_NOTES.md) | Two Excel layers; mã; status dialects; refuse fake inventory / Shopify |
| [`excel-kit/EFFICIENCY.md`](../../excel-kit/EFFICIENCY.md) | Cost of two inventory brains; daily path |
| [`excel-kit/schema.py`](../../excel-kit/schema.py) | `MA_RE`, `SOT_OFFICIAL_STATUS`, `OFFICIAL_TO_MA_LIST_STATUS`, `ASK_STOCK_MA`, `DEMO_ROW_TOKENS`, Square wording patches, A01 handoff comment |
| [`excel-kit/PROMPTS.md`](../../excel-kit/PROMPTS.md) | Paste-ready agent contracts; Ask Stock; no invent |
| [`excel-kit/square/README.md`](../../excel-kit/square/README.md) + [`validate_import.py`](../../excel-kit/square/validate_import.py) | SKU=mã; Track ON; headers-only in git |
| [`excel-kit/sot/append_official_row.py`](../../excel-kit/sot/append_official_row.py) | `--ma` required; duplicate refuse |
| [`excel-kit/sot/append_wishlist_row.py`](../../excel-kit/sot/append_wishlist_row.py) | No live mã; `--no-source` vs silent drop |
| [`excel-kit/clean_sot_demo.py`](../../excel-kit/clean_sot_demo.py) | Seed drift cleaner |
| [`excel-kit/KIT.md`](../../excel-kit/KIT.md) | Env **names** |
| [`sassy-closet/README.md`](../../sassy-closet/README.md) + [`BOSS.md`](../../sassy-closet/BOSS.md) | Blob durable store; restore; Tìm mã; no Square Save |
| [`sassy-closet/lib/store.ts`](../../sassy-closet/lib/store.ts) + [`store-backend.ts`](../../sassy-closet/lib/store-backend.ts) + [`mint.ts`](../../sassy-closet/lib/mint.ts) + [`form-save.ts`](../../sassy-closet/lib/form-save.ts) + [`on-hand.ts`](../../sassy-closet/lib/on-hand.ts) + [`types.ts`](../../sassy-closet/lib/types.ts) | Add/edit/rename, Blob/JSON, export, staged-only |
| [`sassy-closet/components/IntakeApp.tsx`](../../sassy-closet/components/IntakeApp.tsx) + [`SavedCard.tsx`](../../sassy-closet/components/SavedCard.tsx) | Lưu / rename UX |
| [`sassy-closet/app/admin/page.tsx`](../../sassy-closet/app/admin/page.tsx) | CSV export + Kho |
| [`excel-kit/prompts/FIND_MA_CARD_2026-09-08.md`](../../excel-kit/prompts/FIND_MA_CARD_2026-09-08.md) | Read-only card; never fake Square |
| [`excel-kit/prompts/SAVED_CARD_AND_REAL_MINIBOSS_ASK_2026-09-07.md`](../../excel-kit/prompts/SAVED_CARD_AND_REAL_MINIBOSS_ASK_2026-09-07.md) | Saved sheet; Ask relay |
| [`excel-kit/prompts/GF_CLOTHES_INTAKE.md`](../../excel-kit/prompts/GF_CLOTHES_INTAKE.md) | Packet import; ASK STOCK |
| [PR #15](https://github.com/SkyLanter/Sassy-closet/pull/15) | Durable Blob; missing Blob ≠ crash |
| [PR #18](https://github.com/SkyLanter/Sassy-closet/pull/18) | `catalog.v1`, allowlist, Hold P02/P05, no silent `-w` fallback, `CLONE_TO_OFFICIAL.md` (**open** as of 2026-09-09; paths on `cursor/catalog-export-clone-official-5ad2`) |
| [PR #9](https://github.com/SkyLanter/Sassy-closet/pull/9) / [PR #12](https://github.com/SkyLanter/Sassy-closet/pull/12) | Saved card + Tìm mã |

Granola / Slack / Linear / Notion were queried for this chapter (2026-09-09): no extra meeting notes on tiny-boutique admin. Shop decisions remain Slack `#shop-decisions` as written in kit law.

---

## 15. One-page tear sheet (Ultra burn)

```
SKU = mã. Never invent. Sold stays dead.

Sell catalog  = what buyers may see (hold | available). qty=1 is not a count.
Square Free   = on-hand SoT LATER. Until then: "staged only" / Hold · Inbox.
Excel / Blob  = working copy + captions + photos. Not a second warehouse.

Add    = assigned mã → facts → publication yes (three gates).
Edit   = same mã, real fields, keep_photos valid JSON.
Rename = new assigned mã + move bytes + update every surface. No gộp.

Hold      = no public $. P02 P05 today.
Available = Boss USD table only.
Sold      = retire identity. New piece = new mã.

Export  = All sheet / intake CSV. Hard-fail > pretty JSON.
Import  = allowlist + real photos. Empty is honest.

Silent save  = Saved card /tmp, bad keep_photos, wrong -w, Track=No.
Seed drift   = AO999, next A03, P05=$23, kind tabs, shared Blob.
Duplicate    = 409, Official row exists, All dups, Sold reuse.

#shop-decisions before Square Save or official go-live.
```

When this page and a dashboard disagree, **this page + the cited file** win until Boss changes the law in `#shop-decisions`.
