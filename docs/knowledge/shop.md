# How the shop works

Sources are the files named in each section. Where the repo does not say something, the section says so.

## What the shop is

The learn-track doc describes Sassy Closet as a Vietnamese / Bay Area Facebook clothing boutique that sells mainly by Taobao dropship, then ships in the US (`sassy-closet-shop/docs/ai-clothing-shop/07-taobao-dropship-boutique.md`). The root README says the Facebook inbox is the store, and Slack `#shop-decisions` is where Boss yes/no lives. Bots draft only. The owner posts on Facebook, sends the message, takes Zelle, and taps Save in Square (`README.md`, `excel-kit/schema.py` `BOTS_DRAFT_ONLY`).

Square Free is the on-hand inventory source of truth. Official Excel is a working copy, a mã index, and captions. It is not a second stock count (`README.md`).

There is no cart. The sell shop is message-first (`sassy-closet-shop/docs/ai-clothing-shop/07-taobao-dropship-boutique.md`, shop copy in `sassy-closet-shop/lib/warehouse-voice.ts`).

Instagram is in the caption and post checkers (`scripts/caption_lint.py`, `scripts/meta_inventory.py`). Those checkers read a saved export. They do not call Meta.

## Two mã systems

Do not mix them.

**Intake and the sell shop** use one uppercase letter plus two digits, such as `S06` or `Q02` (`scripts/ma_shape.py`, `SHAPE_RE`). Kind letters and Vietnamese labels live in `sassy-closet/lib/kinds.ts` and are copied in `excel-kit/schema.py` as `INTAKE_KIND_LABELS`:

| Letter | Label |
| --- | --- |
| A | Áo |
| Q | Quần |
| V | Váy |
| D | Đầm / Dress |
| K | Áo khoác |
| G | Giày / Cao gót |
| B | Túi |
| P | Phụ kiện |
| H | Phụ kiện tóc / Hair accessories |
| J | Trang sức / Jewelry |
| S | Set đồ |
| O | Khác / Other |

Clothing sizes are `2XS` through `2XL`. Shoe sizes on intake for kind `G` are `35`–`41` (`excel-kit/schema.py` `intake_sizes_for_kind`). `scripts/autolist.py` also keeps numeric sizes `33`–`46` for kinds `G` and `O`. Those two size lists are not the same range. Use the file you are editing.

**Official Excel** uses `AO` / `QU` / `VA` / `AK` / `GI` / `PK` / `SET` plus three digits (`excel-kit/schema.py` `MA_RE`). Prefix meanings are in `MA_PREFIX_MEANS` (Áo, Quần, Váy, Áo khoác, Giày, Phụ kiện, Set). The same file says not to invent an Official mã from an intake letter. Bots do not mint the next Official mã. Dashboard cells `B21:B27` are the stock read (`ASK_STOCK_MA`). A Sold mã is not reused.

## Sell-price math

Two calculators exist. They are not the same formula.

**Flat 25%** in `sassy-closet/lib/pricing.ts` `computeAutoPrice` / `sellUsdFromLanded`:

- Landed USD = CNY cost / FX + letter debox.
- Sell = `ceil(landed / 0.75)`.
- If that ceil is under $10, add $2.
- Debox for `V`, `Q`, and `D` is locked at $7.50. Other letters default to $0 unless Boss sets a per-letter value.
- Default FX in that file is `6.723` CNY per USD.
- If the margin is under 35% (`MARGIN_FLOOR`), the caption stays "Inbox giá".

**Tiered quote** in `scripts/autolist.py` and `tieredSellUsd` in `sassy-closet/lib/pricing.ts`, with the same bands in `shared/tiered-pricing.ts`:

- Margin is 35% when the resulting sell is $25 or less.
- Margin is 25% when the resulting sell is $45 or more.
- Between $25 and $45 the margin moves in a straight line.
- Sell is the smallest whole dollar that does not undercut `ceil(landed / (1 - m))`.
- Under $10, add $2.
- `wouldBeLiveUsd` in `shared/tiered-pricing.ts` keeps S06 at $25.

Intake's `intakePriceView` shows $25 for S06 even when the stored sell is blank (`sassy-closet/lib/pricing.ts`). A typed sell under the tiered quote is flagged and still shown.

Dated research sheets are not the live calculator: `sassy-closet-shop/docs/MARGIN_20PCT_2026-09-10.md` (`landed / 0.80`) and `MARGIN_50PCT_CONSERVATIVE_2026-09-10.md` (`landed / 0.50`). They say customer US flat ship is pending Boss (TBD) and is not baked into the product price.

`publishBlock` refuses an S06 sell that is not a whole $25 on any action (create, update, mint, sync), and refuses S06 priced in CNY (`sassy-closet/lib/publish-guard.ts`). An empty sell string is not a lock violation in that function (`wholeDollars` returns null, and the lock only fires when a parsed whole-dollar value is not 25).

## Held items and 404

`data/held.json` on this commit:

- `heldIncomplete`: S14, A24, A25, S15, A26, K02, K03, K04, K05, V04, K06, V05, S16, S17, S18, S19, A27, A28, A29, H02, G01.
- `neverList`: empty.

The shop loads that file in `sassy-closet-shop/lib/held-incomplete.ts`. `isOffLiveSell` is true for either list. `shopVisibleProducts` drops those mãs (`sassy-closet-shop/lib/site-settings.ts`). `getProduct` only searches the visible list, and the product page calls `notFound()` when the mã is missing (`sassy-closet-shop/app/(shop)/m/[ma]/page.tsx`, `sassy-closet-shop/lib/products.ts`). That is the held PDP 404.

`publishBlock` returns `"held"` for a held-incomplete mã and `"never-list"` for a never-list mã. It normalizes the mã first, so padded spellings such as `S014` are caught (`sassy-closet/lib/publish-guard.ts`). The padded-spelling test in `sassy-closet/tests/open-link-health-guards.test.ts` ("held spellings never publish") covers the held list. `neverList` is empty, so no test exercises a real never-list mã.

A catalog `status` of `"hold"` is a different word. `isShopVisibleStatus` still shows `hold` and `available`, and hides `sold`. `asksInboxPrice` is true only for `hold` (`sassy-closet-shop/lib/site-settings.ts`). Do not treat a hold-priced look as a `held.json` row.

Customer `/admin` on the sell shop is 404 (`sassy-closet-shop/proxy.ts` plus `sassy-closet-shop/app/admin/layout.tsx`). Catalog edits for the shop live on the intake app at `/admin/shop` (`sassy-closet/docs/SHOP_ADMIN.md`).

Approved Giá already shown on Facebook and Instagram for some held mãs is a reference file, not a sell price: `data/approved-held-gia.json` (`S15` 30, `A26` 32, `K03` 52, `K04` 101, `K05` 52, `V04` 17). Caption lint uses it (`scripts/caption_lint.py`).

## Taobao

Incomplete Taobao mãs stay off the sell catalog. The README and `SHOP_ADMIN.md` list the same codes as `heldIncomplete`. Shop tools does not add them to Blob.

`scripts/freshness_check.py` treats a short page, a login redirect, or the Chinese access-denied strings as a blocked Taobao page. It reads a public CNY from embedded item JSON, and it unescapes `\u0026` in an item URL before looking for `price=`.

Intake stores `source_link` on the submission. The sell catalog stores `sourceLink` (`sassy-closet-shop/lib/types.ts`). Neither field is a publish switch by itself. The publish block is the held list.

## Nhung's intake

The intake app is `sassy-closet/`. Its README names four tabs: **Món mới**, **Sửa theo mã**, **Tìm mã**, **Hỏi Mini Boss · Ask**. Shop tools are the link `/admin/shop`, not a fifth tab.

Scripts call the intake cost "Nhung's intake" (`scripts/too_cheap_check.py`, `scripts/cost_basis_reconcile.py`, `scripts/daily_shop_check.py`). The repo does not define who Nhung is beyond that name.

The site is open by link. `shopAdminGate` returns `"public"` for every path (`sassy-closet/lib/shop-admin-gate.ts`). `GET /api/shop-catalog/login` redirects to the desk and does not check a password (`sassy-closet/app/api/shop-catalog/login/route.ts`). `requireShopAdmin` does not deny a request with no cookie (`sassy-closet/tests/shop-admin-401-mode.test.ts`).

Search engines: the `X-Robots-Tag: noindex, nofollow, nosnippet` header is set on `/api`, `/api/*`, `/admin`, and `/admin/*` only, by `sassy-closet/middleware.ts` and by the `headers()` rule in `sassy-closet/next.config.ts` (both use `sassy-closet/lib/intake-direct-link-headers.ts`). `/` does not get the header (`isIntakePrivateSurface("/")` is false in `sassy-closet/tests/open-link-health-guards.test.ts`). Every intake HTML page, `/` included, gets a robots meta noindex from the root layout metadata (`sassy-closet/app/layout.tsx`, `INTAKE_LISTING_ROBOTS`). `robots.txt` disallows `/api` and `/admin` (`sassy-closet/docs/SHOP_ADMIN.md`).

Ask stores a question and can relay it to `MINIBOSS_ASK_WEBHOOK_URL`. The reply route is gated by `ASK_REPLY_SECRET`. If the webhook env is missing, the UI shows a local draft (`sassy-closet/README.md`). That secret gates the reply endpoint. It is not a login wall on the intake form.

Durable storage is Vercel Blob pathname `sassy-closet/store.json` plus photo bytes, when `BLOB_READ_WRITE_TOKEN` or `BLOB_STORE_ID` is set. Without Blob, Vercel uses `/tmp`, which a redeploy wipes (`sassy-closet/README.md`, merged PR #15).

Open PRs #188 and #189 would put a cookie in front of cost reads. They were open, not merged, on 2026-11-02. See [pr-history.md](pr-history.md).

## Muse, Luxubu, and Meta

What the repo actually says:

- Caption and inventory tools have no Meta access and do not post (`scripts/caption_lint.py`, `scripts/meta_inventory.py`).
- A flagged post's only action string is `edit original only / Boss decides`. The inventory tool's tests forbid suggesting delete or repost (`scripts/meta_inventory.py`, `scripts/tests/test_meta_inventory.py`).
- A Meta QC pass needs Luxubu and Mini Boss to agree. One side alone is `unchecked` (`scripts/daily_summary_draft.py`).
- `scripts/luxubu_status_record.py` writes a local JSON file from CLI flags. It does not send anything. Times are America/Los_Angeles.
- `scripts/muse_pack_sections.py` appends local sections to a Muse pack (`TODAY.md` and a pack message). It sends nothing. Output is mãs, post ids, and counts.
- Caption rules agents' checkers enforce (`scripts/caption_lint.py`): line 1 is `Mã X00`; the price line is `Giá $NN`; S06 must be $25; a live mã's Giá must match the public dollar; a held mã's Giá must match `data/approved-held-gia.json` when that file has one.
- Size checks are separate read-only scripts (`scripts/size_text.py`, `scripts/size_gap.py`, `scripts/size_repeat.py`). They do not edit Meta.

The README says the owner posts. The code names Luxubu as a dual-confirm person and as a local status record. It does not say Luxubu is the Facebook account that publishes. That identification is **UNKNOWN / not in repo**.

## S06

S06 is not in `heldIncomplete`. It is a live sell mã locked at $25 anywhere the lock is coded: publish guard, intake price view, caption lint (`S06_LOCK = 25.0`), and the smoke script `scripts/live_shop_smoke.sh` (GET `/m/S06` must be 200 and the body must contain `$25`). `docs/seed-vs-live-mismatch.md` says the Oct 22 live snapshot has S06 at $25 and the seed `products.json` does not list S06. `docs/price-drift-boss-decision.md` says hub $25, intake `sell_usd` blank, and the lock stays.
