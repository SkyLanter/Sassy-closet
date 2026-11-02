# Pull request history

Fetched read-only from GitHub on 2026-11-02 for `SkyLanter/Sassy-closet`, PRs **#1 through #247**. No numbers are missing in that range. This file is a snapshot of those PR records. It is not a live query, and an open PR is not shop law until it is merged.

Counts at fetch time: 116 merged, 125 open, 6 closed without merge.

The one-line note is the first prose sentence of the PR body, taken mechanically. A leading heading such as "Summary", "TL;DR", or "What changed" is run into the sentence, list bullets and some Markdown are dropped, and a long sentence is cut off mid-word, sometimes with no `...`. Read the PR body itself before relying on a note. When the body has no prose, the note says UNKNOWN. Titles are the PR titles. Do not treat a title as a description of what `main` contains unless the state is MERGED.

## Landmarks that are on main

These are merged PRs whose bodies were read while writing this knowledge base. The notes here are paraphrased summaries. The table below is the full index.

| PR | What the body says |
| --- | --- |
| #1 | Seeds the Excel kit so Cloud Agents can build desktop books here and Kit can sync them to OneDrive. |
| #2 | Adds SoT append CLIs, a headers-only Square import template, the morning brief, and kit checks. |
| #9 | Adds the intake app: Saved card after Lưu, and the Mini Boss Ask relay. |
| #12 | Adds the Tìm mã code box and full info card on top of #9. |
| #15 | Moves intake mã JSON and photo bytes to Vercel Blob so a Production redeploy does not wipe `/tmp`. |
| #203 | Combines 45 visual-neutral script and test PRs. Does not change the shop or intake UI, prices, or `data/held.json`. |
| #204 | Brings fix-needed script checks onto main and points them at the current held list and S06 copy. |
| #205 | Keeps intake and shop health open by link, noindex, S06 at $25, and held PDPs 404. |
| #206 | Stops a false FAIL when intake defines `tieredSellUsd` locally instead of importing `shared/tiered-pricing.ts`. |
| #207 | Nulls `costCny`, `costUsd`, `costSource`, and `landedUsd` in `shared/live-price-snapshot.json`. That removes 117 of about 260 privacy-scan hits against old base `eb8a143`. The other hits (mostly Taobao/1688 test fixtures) were left in place. |

## Open drafts that disagree with current main

These were open on 2026-11-02. They are not merged. Current code wins until Boss merges them.

| PR | Conflict with main |
| --- | --- |
| #188, #189 | Would require a shop-admin cookie on intake cost reads (`/api/export`, `/api/submissions`, `/api/ma`). Main keeps those routes open by link (`sassy-closet/docs/SHOP_ADMIN.md`, `sassy-closet/lib/shop-admin-gate.ts`). |
| #215 | Would make `scripts/hard_recheck.sh` default its diff base to the merge-base with `main` when `eb8a143` is missing. Main still prefers `eb8a143`, then the root commit. This clone has no `eb8a143`. |
| #220 | Would teach midnight QC to read escaped Next.js flight quotes. Main's home-price regex still requires plain quotes (`scripts/midnight_qc.py`). |

## Merged, then reversed by later merges

- #74 put shop admin on intake "behind a password", and #194 (merge commit `10141e4`, 2026-10-29 19:07 UTC) made `/api/export`, `/api/submissions`, and `/api/ma/*` require a shop-admin session. Later merges the same day removed those gates: #196 (21:02 UTC), #200 (21:37 UTC), and #201 (21:50 UTC), per `git log` on `main`. Main has no intake login now (`sassy-closet/lib/shop-admin-gate.ts`, `sassy-closet/lib/shop-admin-http.ts`).
- Some merged PR bodies still say "Draft only. Do not merge." (for example #12, #14, #84, #193, #204). The body was written while the PR was a draft. The MERGED state is what counts.

## Closed without merge

#63 UI/UX pass: home, catalog, product pages, search, admin, #71 Lock the shop desk so customers cannot reach admin, #93 Add gentle boutique motion on the sell shop, #94 Redirect the old hair category slug to /c/toc, #96 Restore iOS status bar to black-translucent, #97 Name the mã on product share descriptions

## Full index

| # | State | Date | Title | Body, first sentence |
| --- | --- | --- | --- | --- |
| 1 | MERGED | 2026-09-05 | Seed excel-kit shop tooling | Seeds the Sassy Closet Excel kit into this repo so Cursor Cloud Agents can build desktop books here and Kit can sync them to OneDrive. |
| 2 | MERGED | 2026-09-05 | SoT automation suite: append CLIs, Square template, morning brief | Production-ready expansion of `excel-kit/` for the ONE desktop workbook `Sassy_Closet_SoT.xlsx`. |
| 3 | MERGED | 2026-09-05 | GF clothes intake: From GF packets → Photos + Wishlist/Official staging | Kit-only GF clothes intake. Contract: `excel-kit/prompts/GF_CLOTHES_INTAKE.md`. |
| 4 | MERGED | 2026-09-06 | Fix From GF OneDrive browse URLs (Graph webUrl 404 shape) | Boss’s Graph `item.webUrl` for personal OneDrive **From GF** looks like `https://onedrive.live.com?cid=…&id=…` (no slash after `.com`, raw `!` in `id`) and **404s**. |
| 5 | MERGED | 2026-09-06 | Restore schema exports for append_official_row --help | Why Local bugcheck failed with `ImportError` on `from schema import OFFICIAL_TO_MA_LIST_STATUS` (and siblings). |
| 6 | OPEN | — | Tighten Màu auto-detect (garment vs studio back) | What changed Client-side color detect (`sassy-closet/lib/colors-client.ts`) now: 1. |
| 7 | OPEN | — | Plain Sassy_Closet_Data.xlsx — cute Excel retired | Boss 2026-09-07 ~10:24 PM PT: Excel is now a **thin floor tracker for teammates**, still plain and openable on OneDrive + Excel. |
| 8 | OPEN | — | sassycloset hub — All + category sheets, kit.sh save | Boss 2026-09-07 ~10:33 PM PT + path clarification: keep the existing OneDrive shop folder. |
| 9 | MERGED | 2026-09-08 | Saved card popup + real Mini Boss Ask relay | Boss 2026-09-07 ~10:53 PM PT. Spec: `excel-kit/prompts/SAVED_CARD_AND_REAL_MINIBOSS_ASK_2026-09-07.md`. |
| 10 | OPEN | — | Square.xlsx + Finance.xlsx — empty bought tracker and tax book | Boss 2026-09-07 ~11:30 PM PT: two plain books for `Documents/Sassy Closet/`. |
| 11 | OPEN | — | Square.xlsx + Finance.xlsx — bought tracker and tax-ready books | Boss 2026-09-07 ~11:30 PM PT: two plain books for OneDrive `Documents/Sassy Closet/`. |
| 12 | MERGED | 2026-09-08 | Tìm mã find-by-code box + full info card (keep photo detect) | Boss check before merge. **Do not merge. Do not touch Production** (`sassy-closet.vercel.app`). |
| 13 | OPEN | — | Fix Bugbot issues from saved-card Ask (size, Sửa, rename, shared store) | TL;DR Fixes all six Bugbot notes from #9 on the already-merged saved-card / Mini Boss Ask work. |
| 14 | MERGED | 2026-09-08 | Photo lightbox + Tìm mã 3-up photo row | Boss check before merge. **Do not merge. Do not touch Production** (`sassy-closet.vercel.app`). |
| 15 | MERGED | 2026-09-08 | Durable Vercel Blob store — stop Production redeploy wipes | Production at https://sassy-closet.vercel.app was writing mã metadata and photo bytes to serverless `/tmp`. |
| 16 | MERGED | 2026-09-08 | Extract Taobao URL only from a full share paste | Outcome When GF pastes a **full Chinese Taobao share blob** (wrapper text + URL) into Link shop / Taobao, Save/Mint and Sửa PATCH store **URL only** (e.g. |
| 17 | MERGED | 2026-09-09 | Add mã D (Đầm / Dress) and restore intake CNY↔USD convert | TL;DR Intake now has a **D = Đầm / Dress** chip that mints `D01…`. |
| 18 | OPEN | — | Kit: sell catalog.v1 export + CLONE_TO_OFFICIAL | TL;DR Kit-only lane: export the **10 known mãs** from OneDrive `sassycloset.xlsx` into sell-site **catalog.v1** JSON, validate allowlist + prices, and give Boss a runbook to stand up official from sell-test. |
| 19 | OPEN | — | Learn-track 02: Fashion PDP color/size UX (sell-test) | Adds `docs/ai-clothing-shop/02-pdp-color-size-ux.md` — a long, source-cited learn-track note for a small-shop fashion PDP. |
| 20 | OPEN | — | Learn track: tiny-boutique admin / inventory ops playbook | TL;DR Adds the LEARN TRACK (Ultra burn) playbook **`docs/ai-clothing-shop/03-tiny-boutique-admin.md`**: tiny-boutique admin (not Shopify enterprise) for add / edit / rename **SKU = mã**, **Hold / Available / Sold**, Blob |
| 21 | OPEN | — | Learn 07: Taobao dropship boutique law + sell-site APPLY | TL;DR Adds `docs/ai-clothing-shop/07-taobao-dropship-boutique.md` — the dropship-first operating law for Sassy Closet (VN / Bay Area Facebook + US ship). |
| 22 | OPEN | — | LEARN 01: Messenger-first social-commerce playbook | Adds `docs/ai-clothing-shop/01-messenger-social-commerce.md` — a sourced playbook for unique-piece clothing shops that discover on Facebook/Instagram and close in Messenger (no cart). |
| 23 | OPEN | — | Learn track: AI product media + sell-test per-color storage | Learn-track lesson `docs/ai-clothing-shop/05-ai-product-media.md` for AI fashion product photography and media pipelines. |
| 24 | OPEN | — | Learn: Next+Blob catalog.v1 architecture (ISR, admin, clone) | TL;DR LEARN TRACK apply playbook for the headless clothing catalog: versioned **`catalog.v1`**, intake vs Origin admin APIs, ISR/Blob cache pitfalls, sell-test vs official isolation, and the xlsx → JSON → Blob handoff. |
| 25 | OPEN | — | Learn track 06: SEO, trust, and conversion for diaspora boutiques | Adds `docs/ai-clothing-shop/06-seo-trust-diaspora-boutique.md` — the Ultra-burn learn note for **SEO, trust, and conversion** on a VN / Bay Area / US-ship Messenger closet. |
| 26 | OPEN | — | LEARN 08: Taobao dropship ops runbook (Inbox Desk + Buy Research) | TL;DR Adds `docs/ai-clothing-shop/08-dropship-ops-runbook.md` — the **day-to-day hands** playbook after sibling PR #19 (PDP) and PR #21 (dropship **law**). |
| 27 | OPEN | — | Learn 09: sell-site bugcheck QA checklist (live shop map) | Adds `docs/ai-clothing-shop/09-bugcheck-sell-site-checklist.md` — a long, source-cited LEARN TRACK QA book for the AI-built Taobao-dropship sell-test at https://sassy-closet-shop.vercel.app. |
| 28 | OPEN | — | Learn 11: sell-test Origin gate + admin/Blob fix list (Kelly Ying look stays) | TL;DR LEARN now **improves sell-test**: Origin `sassy-closet-shop` gets an executable fail-until-green QA harness and a numbered admin/Blob APPLY list so **Save cannot stay silent** and **public HTML/covers cannot drift**. |
| 29 | OPEN | — | AI clothing-shop playbook + sell-test apply list | Kit-lane learn notes for how AI-built clothing shops are actually assembled, mapped onto the live sell-test shop. |
| 30 | OPEN | — | LEARN 12: FB Messenger dropship VN+EN phrase bank | Adds `docs/ai-clothing-shop/12-fb-messenger-dropship-copy.md` — a cited **phrase bank** (VN first, then EN) for a Taobao dropship boutique that closes in Messenger. |
| 31 | OPEN | — | Learn 10: customer-pleasing motion UX (Kelly Ying lookbook) | Adds `docs/ai-clothing-shop/10-customer-pleasing-motion-ux.md` — LEARN TRACK for boutique motion on the sell-test lookbook. |
| 32 | OPEN | — | Learn 14: complete admin feature matrix (sell-test Origin APPLY) | Adds `docs/ai-clothing-shop/14-complete-admin-feature-matrix.md` — LEARN TRACK for a ready-to-sell **test** boutique merchandiser. |
| 33 | OPEN | — | Learn 13: watery / liquid tab + slide motion (Kelly Ying lookbook) | Adds `docs/ai-clothing-shop/13-watery-tab-slide-motion.md` — LEARN TRACK for **premium watery tab + grid pour** on the sell-test lookbook. |
| 34 | OPEN | — | Learn 21: liquid chrome FX — chrome only, never wreck covers | Adds `docs/ai-clothing-shop/21-visual-fx-liquid-chrome-safe.md` — LEARN TRACK for **shader-light liquid chrome** on the sell-test lookbook. |
| 35 | OPEN | — | Learn 15: Apple watery color/carousel peek (Kelly Ying PDP) | Adds `docs/ai-clothing-shop/15-apple-watery-color-peek.md` — LEARN TRACK (Fast OFF) for **Apple-style watery see-through color chips + peeking gallery roll** on fashion PDPs. |
| 36 | OPEN | — | Learn 16: iOS frosted carousel + colorId watery roll | Adds `docs/ai-clothing-shop/16-ios-frosted-carousel-deep.md` — LEARN TRACK (Fast OFF) for an **Apple-style color carousel** translated to the sell-test lookbook: neighbor **peeks**, **scroll-snap** watery roll, frosted * |
| 37 | OPEN | — | Learn 20: visual FX motion springs (FeaturedBoard watery tabs) | Adds `docs/ai-clothing-shop/20-visual-fx-motion-springs.md` — LEARN TRACK (Fast OFF) for **Framer Motion / Motion One `layoutId`, shared element, and spring pours** on the sell-test lookbook. |
| 38 | OPEN | — | Learn 19: CSS snap / mask / backdrop / VT for watery PDP slides | Adds `docs/ai-clothing-shop/19-visual-fx-css-snap-mask-vt.md` — LEARN TRACK (Fast **off**) for **watery rolling slides** on the sell-test fashion PDP. |
| 39 | OPEN | — | Learn 18: Apple color carousel + frosted edge peeks (Kelly Ying lookbook) | Adds `docs/ai-clothing-shop/18-visual-fx-apple-water-glass.md` — LEARN TRACK for **Apple-grammar PDP gallery FX** on the sell-test lookbook: color → gallery **roll**, **frosted glass edge peeks**, watery/native-snap transitions. |
| 40 | OPEN | — | Learn 17: a11y + reduced-motion for watery/frosted carousels (Kelly Ying lock) | Adds `docs/ai-clothing-shop/17-a11y-watery-motion.md` — LEARN TRACK for **accessibility + reduced-motion** on watery/frosted **galleries**, without flattening the boutique. |
| 41 | OPEN | — | Learn: Next+Blob catalog.v1 architecture + intake Blob cache APPLY | TL;DR Continuation of the Next+Blob catalog LEARN track. |
| 42 | MERGED | 2026-09-23 | Intake webhook → dataset sync | TL;DR After a successful GF intake **create** or **update** (Món mới / Sửa theo mã, including rename), the **server** POSTs a small JSON event to the Grok Bot routine `intake-dataset-sync-webhook`. |
| 43 | OPEN | — | Finance.xlsx + Square.xlsx — empty tax-ready books for OneDrive | Boss 2026-09-15: stand up Finance.xlsx (and Square.xlsx) for Cap/Money tracking and accountant-friendly tax filing. |
| 44 | OPEN | — | LEARN: Taobao how-it-works + Cainiao China→US weight scale | TL;DR DRAFT-only Buy Research LEARN playbooks under `docs/scout/`. |
| 45 | OPEN | — | Docs: website codebase map (intake + sell-test handoff) | TL;DR Docs only. Adds `docs/CODEBASE_MAP.md` so the next CloudAgent can work the **websites** without guessing. |
| 46 | OPEN | — | Restore FINANCE_* schema exports so kit.sh books works | Hub sync overwrote `excel-kit/schema.py` and dropped `FINANCE_*` / Square book constants. |
| 47 | OPEN | — | LEARN draft: 38-mã Taobao deep dive (2026-09-15) | Draft-only Buy Research / LEARN notes. **No 旺旺, cart, or buy.** No invented ¥. |
| 48 | MERGED | 2026-09-23 | Intake G shoe sizes 35–41 + H/J accessory labels | Intake kinds stay the catalog Excel / dataset / Ask webhook sync from. |
| 49 | OPEN | — | Restore FINANCE_* schema + San Jose 10% tax-ready Finance.xlsx | Hub/site restores dropped `FINANCE_*` exports from `schema.py`, which broke `excel-kit/build_square_finance.py` (`ImportError: FINANCE_CHANNEL`). |
| 50 | MERGED | 2026-09-22 | Land sell shop under sassy-closet-shop (GitHub source of truth) | Summary Lands the live sell-shop app in this repo as `sassy-closet-shop/`, next to intake (`sassy-closet/`) and `excel-kit/`. |
| 51 | MERGED | 2026-09-23 | Meta Popular refresh 2026-09-22 | Replaces `sassy-closet-shop/data/popular-order.json` with the Sep 22 Meta FB+IG equal rank-position blend. |
| 52 | MERGED | 2026-09-23 | Remove redirect URLs from sitemap | Removes /how-to-buy and /meetup-ship from the sitemap — both routes currently redirect to /, so they should not be listed as crawlable pages. |
| 53 | MERGED | 2026-09-23 | Intake automation: Taobao link prefill + auto-price calculator | Automation upgrade for the intake site (sassy-closet), so new-clothes intake needs less manual work. |
| 54 | MERGED | 2026-09-23 | Admin workflow automation: intake import + price calculator + pipeline tracker | Automation upgrade for the sell-site admin (Sell ops), sassy-closet-shop. |
| 55 | OPEN | — | [DRAFT] Admin UI polish: needs-attention chips, badges, sorting, sticky filters, Save & next | Branch: `admin-ui-polish-2026-09-23` → `main` (3 commits, rebased on origin/main) What this does: Layers admin catalog UX improvements on top of current main (post-#54), keeping every #54 feature intact (Intake/Pipeline |
| 56 | OPEN | — | [DRAFT] Workflow hardening: intake carry-through, price locks, stale-color fix, accessories one-size, sync dedupe draft | Branch: `workflow-hardening-2026-09-23` → `main` (3 commits) What this does: Hardens the intake→pricing→records workflow: provenance carry-through for intake auto-price/Taobao snapshots, Boss price locks, a stale-closure |
| 57 | MERGED | 2026-09-27 | Fix LayoutProps type error and clean ESLint config | Small standalone fix (Mini Boss PR order #1). |
| 58 | MERGED | 2026-09-27 | Blob-first photo migration: external covers (Catbox/Alicdn) to Vercel Blob | Adds lib/photo-migrate.ts, scripts/migrate-covers-to-blob.ts (dry-run by default; --live performs Blob writes), tests/photo-migrate.test.ts (7 passing). |
| 59 | MERGED | 2026-09-27 | Add needs_research pipeline stage | Restores the needs_research stage between intake and researched in lib/pipeline.ts PIPELINE_STAGE_IDS, with matching null entry in emptyStages(). |
| 60 | OPEN | — | Stage-only intake receiver: POST /api/intake/receive | Authenticated stage-only receiver for girlfriend intake submissions. |
| 61 | OPEN | — | Refresh listings: A17–A22, S10 as hold/Inbox-price tabs | Seven new public-field-only listings per Mini Boss BOTH-ok direction. |
| 62 | OPEN | — | Fix smoke tests and Boss price corrections | Restores 20 Boss-authorized prices (+$1 bump from 2026-09-21) and fixes stale smoke test expectations. |
| 63 | CLOSED | 2026-10-01 | UI/UX pass: home, catalog, product pages, search, admin | Full UI/UX pass on the Sassy Closet sell site. |
| 64 | MERGED | 2026-09-27 | Meta Popular refresh 2026-09-25 | Replaces `sassy-closet-shop/data/popular-order.json` with the Sep 25 Meta FB+IG equal rank-position blend. |
| 65 | MERGED | 2026-09-27 | Soften the shop lookbook: blush paper, even cards, search empty state | Summary Customer shop polish for https://sassy-closet-shop.vercel.app (`sassy-closet-shop/`). |
| 66 | MERGED | 2026-09-27 | Calm the intake UI: blush tokens, tabs, confirm, and toasts | Summary GF intake polish for https://sassy-closet.vercel.app (`sassy-closet/`). |
| 67 | MERGED | 2026-09-27 | Clear the stuck home search, show the search field, and fix Looks Popular | Search field (Boss) The header search was a transparent pill with a 1px gold hairline, so it disappeared on the frosted bar over the hero and over the blush page. |
| 68 | MERGED | 2026-09-27 | fix: commit product photos so GitHub deploys keep them | Summary Commit the sell-site product photos into `sassy-closet-shop/public/products/` (114 files in 40 mã folders). |
| 69 | MERGED | 2026-09-27 | Remove seller overlays from product photos | Summary Brand wordmarks and cute character stickers stay. |
| 70 | MERGED | 2026-09-27 | Keep the phone buy bar solid without covering the color label | Phone buy bar On a phone product page the buy-bar title wrapped to two lines (`PUPPY CARDIGAN`, `BUTTER PUPPY CARDIGAN`, `PUPPY ZIP JACKET`). |
| 71 | CLOSED | 2026-09-28 | Lock the shop desk so customers cannot reach admin | Customer URL Customers use https://sassycloset.vercel.app. |
| 72 | MERGED | 2026-09-27 | Erase leftover watermark lines on J01 necklace photos | The ABAO轻珠宝 removal on the J01 necklace left a thin bright band on the background. |
| 73 | MERGED | 2026-09-28 | Publish new-shipping prices for the 10 locked mãs | Summary Boss yes (2026-09-27 23:37 UTC): draft the new-shipping prices for all 10 locked mãs, including removing the P05 $23 rule. |
| 74 | MERGED | 2026-09-28 | Move shop admin onto the intake app behind a password | This draft supersedes unmerged PR #71 (`cursor/admin-session-lock-21ce`). |
| 75 | MERGED | 2026-09-28 | Polish the shop look without changing the brand | Same blush shop, just cleaner. A returning shopper should still recognize Sassy Closet: same light-pink page, same colors, same Be Vietnam Pro and Cormorant fonts, same “Sassy Closet” wordmark, and the same D02 front/back cover. |
| 76 | MERGED | 2026-09-28 | Intake: non-blocking new-mã webhook (+ optional Live/Held badge) | What changed When Nhung taps Lưu (a new mã or an edit), the save returns as fast as it does today. |
| 77 | MERGED | 2026-09-28 | Polish shop motion and phone details on the blush look | Stacked draft on `cursor/shop-ui-polish-6643` (PR #75). |
| 78 | MERGED | 2026-09-28 | Clean leftover promo text and duplicate shop photos | Draft only. Mini Boss reviews the sheets with Boss before merge. |
| 79 | MERGED | 2026-09-28 | Meta Popular 3-day refresh 2026-09-28 | Looks tab Popular sort now follows the Meta-blended mã order from the 2026-09-28 refresh. |
| 80 | MERGED | 2026-09-28 | [stacked on #77] Shop r3: photo share cards, accent-free search, faster PDP photo | Outcome Share cards now use the real look photo and the catalog price, in the blush paper look with Cormorant and Be Vietnam Pro. |
| 81 | MERGED | 2026-09-28 | Shop visual r4: calmer cards, first-screen products, cleaner PDP (same style) | Same Sassy Closet. Calmer phone shop: products start higher, cards share one rhythm, the product page puts the title and the buy bar in one glance, and the chrome — including every Messenger link — is a blush liquid glass that sits off t... |
| 82 | MERGED | 2026-09-28 | Switch sell margin to 25% and add shop analytics | Boss approved a store-wide switch from 30% to 25% margin on 2026-09-28. |
| 83 | MERGED | 2026-09-28 | Add Vercel Web Analytics and Speed Insights to the shop | Summary Adds Vercel Web Analytics and Speed Insights to the customer shop (`sassy-closet-shop` only). |
| 84 | MERGED | 2026-09-29 | Shop polish r5: colors in first screen, readable glass, faster grids, clearer Messenger ask | Draft only. Do not merge. Do not deploy to production. |
| 85 | MERGED | 2026-09-29 | Shop: restore r4 see-through header glass (keep r5 buy bar) | The top panel is see-through and lightly blurred again, like the last version. |
| 86 | OPEN | — | Blush scroll stage and floating shop pill | Draft only. Do not merge. This does not change the live catalog, prices, or product rows, and it does not deploy production. |
| 87 | OPEN | — | Restore intake cream shell and match live Blob prices — stage sell_usd backfill and D05 form | Draft only. Do not merge. This does not write the live sell Blob, production intake records, Square, or Meta. |
| 88 | MERGED | 2026-09-30 | Publish Blob catalog USD for the hub ten | What changed Customer shop reads were replacing the hub ten (`A01`, `A02`, `S01`, `P01`–`P05`, `K01`, `H01`) with a hard-coded Boss list (`A01` $24, `A02` $20, and the rest of the old flat 25% prices). |
| 89 | MERGED | 2026-10-05 | Refuse seed when Blob catalog JSON cannot be parsed | Before A live Blob catalog that was not valid JSON threw `SyntaxError`. |
| 90 | OPEN | — | Midnight QC 2026-10-01 data and sell-site proof | Midnight QC 2026-10-01 Overall: PASS** (0 FAIL). |
| 91 | MERGED | 2026-10-01 | Meta Popular 3-day refresh 2026-10-01 | Looks tab Popular sort now follows the Meta-blended mã order from the 2026-10-01 refresh. |
| 92 | MERGED | 2026-10-01 | List all six held incomplete mãs | Before Docs and config that name unfinished Taobao mãs did not list the standing never-publish set. |
| 93 | CLOSED | 2026-10-02 | Add gentle boutique motion on the sell shop | Summary Tasteful motion on the sell shop only (`sassy-closet-shop`). |
| 94 | CLOSED | 2026-10-02 | Redirect the old hair category slug to /c/toc | Summary The sell shop already treats `/c/toc` as Hair. |
| 95 | OPEN | — | Make look-card photos settle without a stuck blank well | Summary Look-card photos on the sell shop (`sassy-closet-shop`) keep a stable blush well and fade the photo in when it is ready. |
| 96 | CLOSED | 2026-10-02 | Restore iOS status bar to black-translucent | Summary `npm run smoke:seo` fails early because `rootSeo()` in `sassy-closet-shop/lib/seo.ts` sets `appleWebApp.statusBarStyle` to `default`, while the smoke requires `black-translucent` over the ink ticker. |
| 97 | CLOSED | 2026-10-02 | Name the mã on product share descriptions | Why `npm run smoke:seo` asserts that the A01 share description names the mã and the garment, and never says Taobao. |
| 98 | OPEN | — | Keep live $25 on share cards and finish smoke SEO | Summary One sell-shop draft for the safe smoke SEO fixes, plus the stale hair-slug redirect. |
| 99 | OPEN | — | LEARN: Taobao sea-shipping China→US for held mãs | TL;DR Draft LEARN only. One new file: `docs/scout/taobao-cainiao-sea-hub-fields.md`. |
| 100 | MERGED | 2026-10-05 | Hold K03 K04 K05 V04 on main (draft) | Summary `HELD_INCOMPLETE_MAS` on `main` was still six mãs. |
| 101 | OPEN | — | Meta Popular 3-day refresh 2026-10-13 | Looks Popular now uses the 2026-10-13 Meta blend. |
| 102 | MERGED | 2026-10-05 | Keep live hub prices and check before write | What changed `apply-hub-live.ts` kept a live hub-ten dollar only when the seed price was strictly lower. |
| 103 | MERGED | 2026-10-05 | Keep stored Blob catalog titles on read and save | Summary `overlayCustomerStockVoice` replaced every known-seed title and description with seed copy on live read. |
| 104 | OPEN | — | Refuse shop-tools saves that move S06 off $25 | Summary A signed-in intake shop-tools save (`POST /api/shop-catalog/save` → `saveShopCatalogProduct`) could change S06 to another dollar or to Hold, which stores `priceUsd: null`. |
| 105 | OPEN | — | Hold K06 with the incomplete mãs | Boss already decided K06 stays off the sell catalog. |
| 106 | OPEN | — | Hold V05 with the incomplete mãs | Why Boss is holding V05 off the sell catalog. |
| 107 | MERGED | 2026-10-11 | Dataset freshness, tiered quotes, and one held list | Summary Draft only. This does not merge, and it does not mark the PR ready. |
| 108 | MERGED | 2026-10-12 | Let the next queen mã be Q02 | Q02 never had clothes, so it is no longer a never-list code. |
| 109 | OPEN | — | Hold S16 with the incomplete mãs | S16 is a new intake form (id 74, created 2026-10-12T19:21:24.743Z). |
| 110 | OPEN | — | Hold A27, A28, S17, S18, and S19 with the incomplete mãs | These five intake forms are incomplete Taobao holds. |
| 111 | MERGED | 2026-10-30 | Refuse shop-tools saves that leave S06 sold | Summary 104 refused any intake shop-tools save that would leave S06 anything other than available at $25. |
| 112 | MERGED | 2026-10-30 | Map live hub Official USD from row-1 sell_usd | Summary `scripts/freshness_check.py` skipped the hub Official sheet with `Official sheet is missing ma or list_price`. |
| 113 | MERGED | 2026-10-30 | Add a read-only desk status command | Summary Adds `scripts/desk_status.py`, a read-only desk status command. |
| 114 | OPEN | — | Hold a new intake mã when Taobao is incomplete or the ¥ drifted | Summary Adds `scripts/held_sync.py`. Given a local intake fixture and a held file, it appends a new intake mã when Taobao data has no size, no photo, or no public ¥, or when the intake ¥ differs from that public ¥. |
| 115 | OPEN | — | Add a read-only Vietnamese caption linter | Summary Adds a fixture-only Vietnamese caption linter at `scripts/caption_lint.py`. |
| 116 | OPEN | — | Add fixture tests for PDP 404, catalog freshness, corrupt Blob, and Add | Draft only. Tests and two small test hooks. |
| 117 | OPEN | — | Add a read-only intake cost-drift check | Summary Adds a read-only check that compares fixture intake ¥ with parsed or public Taobao ¥. |
| 118 | OPEN | — | Explain intake save errors and warn on a blank ¥ | Summary The intake form now tells Nhung, in plain Vietnamese, why a mã was not saved. |
| 119 | OPEN | — | Refresh intake restore onto current main | Draft only. Do not merge. This refreshes #87 without closing it. |
| 120 | MERGED | 2026-10-30 | Suggest one complementary piece for each catalog letter | Summary Adds `suggestOutfitBundle` as a new shop helper. |
| 121 | OPEN | — | Block a reused mã and suggest the next free code | Summary Saving a mã that is already on the sell catalog is rejected. |
| 122 | MERGED | 2026-10-30 | Show what live prices would become under the tiered margin | Draft only. Live prices stay as they are. |
| 123 | OPEN | — | Show stored sizes on the sell product page | Summary Adds a small size guide on the sell product page. |
| 124 | MERGED | 2026-10-30 | Harden Taobao parser with offline fixtures | Summary Offline Taobao HTML fixtures harden the freshness parser. |
| 125 | OPEN | — | Add a read-only midnight QC script | Draft only. Do not merge. Do not mark ready. |
| 126 | MERGED | 2026-10-30 | Report blank or unusable intake photo fields | Summary Adds `scripts/intake_photo_flags.py`, a read-only check for intake rows whose photo fields are blank or unusable. |
| 127 | OPEN | — | Add a read-only restock note for sold catalog mãs | Summary Adds `scripts/restock_note.py`, a read-only command that lists catalog mãs whose status is sold and writes a markdown restock note. |
| 128 | MERGED | 2026-10-30 | Flag catalog titles that match another mã | Summary `scripts/title_overlap.py` is a read-only report. |
| 129 | OPEN | — | Polish the sell shop for phones, access, and a local Lighthouse check | Draft only. Do not merge. Phone shoppers see the look name and price before the photo, so the buy bar no longer covers the title. |
| 130 | OPEN | — | Report catalog fixture mã and price diffs | Summary Adds a read-only script that compares two local `catalog.v1` JSON fixtures and prints added mãs, removed mãs, and price changes. |
| 131 | MERGED | 2026-10-30 | Preview a packing slip from a fixture order | Summary Adds a local packing-slip preview from a fixture order (`scripts/packing_slip.py`). |
| 132 | MERGED | 2026-10-30 | Flag size text that has no number | Summary Read-only check for catalog and intake size text that has no number. |
| 133 | MERGED | 2026-10-30 | Flag catalog rows with a blank color | Summary Adds a read-only check, `scripts/color_flags.py`, that flags catalog rows with a blank color. |
| 134 | MERGED | 2026-10-30 | Drop held mãs from a fixture popular list | Summary Add a read-only check that a popular-piece list omits held mãs. |
| 135 | MERGED | 2026-10-30 | Flag messy Giá price formats in caption fixtures | Summary Adds a read-only check for messy USD amounts on caption Giá lines. |
| 136 | MERGED | 2026-10-30 | Flag catalog rows with a blank title | Summary Adds a read-only script, `scripts/blank_titles.py`, that flags a catalog row when `titleEn` or `titleVn` is missing, null, empty, whitespace, or not a string. |
| 137 | MERGED | 2026-10-30 | List catalog mãs with more than one color | Summary Adds a read-only script, `scripts/multi_color.py`, that lists catalog mãs whose stored color list already has more than one entry. |
| 138 | MERGED | 2026-10-30 | Flag intake shop links that are not Taobao item or e.tb.cn shares | Summary Adds a read-only check that flags intake shop links which are not a Taobao item URL or an `e.tb.cn` share link. |
| 139 | MERGED | 2026-10-30 | Flag a catalog mã whose photo list repeats a URL | Summary Adds `scripts/duplicate_photo_urls.py`, a read-only check that flags a catalog mã whose photo list contains the same stored URL twice. |
| 140 | MERGED | 2026-10-30 | Flag catalog rows whose letter does not match the type | Summary `scripts/letter_type.py` is a read-only report. |
| 141 | OPEN | — | Report added and removed mãs between held-list fixtures | Summary Adds a read-only script that compares two local held-list JSON fixtures and prints mãs added to `heldIncomplete` and mãs removed from it. |
| 142 | MERGED | 2026-10-30 | Flag catalog mãs with fewer than 2 photos | Summary Adds a read-only check, `scripts/catalog_photo_count.py`, that flags catalog mãs with fewer than 2 photos. |
| 143 | MERGED | 2026-10-30 | Flag intake rows saved more than 7 days ago and still off the catalog | Summary Adds a read-only script, `scripts/intake_stale_flags.py`, that flags intake rows whose saved date is older than 7 days and whose mã is still absent from a catalog fixture. |
| 144 | OPEN | — | Omit held mãs from shop search | Summary Shop search still returned held mãs when those rows were in the list it searched. |
| 145 | MERGED | 2026-10-30 | Flag catalog statuses other than available, sold, or held | Summary Adds `scripts/catalog_status.py`, a read-only check that flags a catalog status other than available, sold, or held. |
| 146 | MERGED | 2026-10-30 | Flag a fixture order when the same mã appears twice | Summary Adds a read-only check (`scripts/order_line_flags.py`) that flags a fixture order when the same mã appears twice. |
| 147 | OPEN | — | Count the next free mã per letter from fixtures | Summary Adds a read-only counter that prints the next free mã for each letter in a fixture. |
| 148 | MERGED | 2026-10-30 | Flag catalog titles that are only the mã | Summary Adds a read-only script, `scripts/ma_only_titles.py`, that flags a fixture catalog row when `titleEn` or `titleVn` is only that row's mã. |
| 149 | MERGED | 2026-10-30 | Flag fixture captions whose Giá dollars differ from the catalog price | Summary Adds a read-only check for fixture captions whose Giá dollars differ from that mã's catalog price. |
| 150 | MERGED | 2026-10-30 | Count fixture catalog mãs by color name | Summary Adds a read-only count, `scripts/color_counts.py`, that reports how many fixture catalog mãs use each stored color name. |
| 151 | OPEN | — | Flag a size list that skips a step | Summary Read-only check for a size list that skips a clothing step. |
| 152 | MERGED | 2026-10-30 | Flag a photo URL filed under a different mã | Summary Adds `scripts/photo_path_ma.py`, a read-only check that flags a fixture photo URL whose `/products/{mã}/` folder differs from the row mã. |
| 153 | MERGED | 2026-10-30 | Flag a fixture mã whose letter is outside the known set | Summary Adds a read-only check that flags a fixture mã whose letter sits outside the shop's known letters: A, B, D, G, H, J, K, O, P, Q, S, V. |
| 154 | MERGED | 2026-10-30 | Flag catalog rows with no sell price | Summary Adds a read-only script, `scripts/missing_sell_price.py`, that flags a fixture catalog row when `priceUsd` is missing, null, or blank. |
| 155 | OPEN | — | Flag a held mã marked available in a catalog fixture | Summary Adds `scripts/held_available.py`, a read-only check that flags a mã on a held-list fixture when a catalog fixture still marks it available. |
| 156 | MERGED | 2026-10-30 | Flag a catalog photo src that is not a site path | Summary Adds `scripts/photo_src_paths.py`, a read-only check that flags a fixture photo src which is not a site path. |
| 157 | MERGED | 2026-10-30 | Flag a fixture color that has a hex and a blank name | Summary Adds a read-only check, `scripts/hex_blank_name.py`, that flags a fixture color which has a hex and a blank name. |
| 158 | MERGED | 2026-10-30 | Flag hold or held rows missing from the held list | Summary Read-only check for a fixture catalog row whose status is `hold` or `held` when that mã is absent from a fixture held list. |
| 159 | MERGED | 2026-10-30 | Flag fixture shop links that use http rather than https | Summary Adds a read-only check that flags a fixture shop link whose scheme is `http` rather than `https`. |
| 160 | MERGED | 2026-10-30 | Flag intake rows with a missing or unreadable saved date | Summary Add a read-only checker, `scripts/intake_saved_date_flags.py`, that flags a fixture intake row when its saved date is missing or unreadable. |
| 161 | OPEN | — | Omit held mãs from the shop category grid | Summary The shop category grid and the home looks list still listed held mãs when those rows were in the list they rendered. |
| 162 | MERGED | 2026-10-30 | Flag a fixture popular list when the same mã appears twice | Summary Add a read-only check that flags a fixture popular list when the same mã appears twice. |
| 163 | MERGED | 2026-10-30 | Flag a fixture order line whose price differs from the catalog | Summary Adds a read-only check (`scripts/order_price_mismatch.py`) that flags a fixture order line whose price differs from that mã's fixture catalog price. |
| 164 | MERGED | 2026-10-30 | Flag a fixture popular mã absent from the catalog | Summary Adds a read-only script, `scripts/popular_missing.py`, that flags a popular mã when that mã is absent from a catalog fixture. |
| 165 | OPEN | — | Skip unpublished intake mãs when counting the next free code | Summary Adds a read-only counter that prints the next free mã for each letter from a fixture. |
| 166 | MERGED | 2026-10-30 | Flag fixture captions with two Giá lines | Summary Adds a read-only check that flags a fixture caption with two or more Giá lines. |
| 167 | MERGED | 2026-10-30 | Flag a fixture mã that is sold and also held | Summary Read-only check for a fixture catalog row whose status is `sold` when that mã is also on a fixture held list. |
| 168 | MERGED | 2026-10-30 | Flag fixture color names that differ only by case | Summary Adds a read-only check, `scripts/color_case_flags.py`, that flags fixture color names which match except for case, such as `Pink` and `pink`. |
| 169 | OPEN | — | Flag a held mã that still has a sell price | Summary Adds `scripts/held_sell_price.py`, a read-only check that flags a mã on a held-list fixture when a catalog fixture still has a sell price for it. |
| 170 | OPEN | — | Flag a size list that repeats a size | Summary Read-only check for a fixture size list that repeats a size. |
| 171 | MERGED | 2026-10-30 | Flag a sell price that is not a whole dollar | Summary Adds a read-only script, `scripts/non_whole_dollar.py`, that flags a fixture sell price which is not a whole dollar, such as 25.50. |
| 172 | MERGED | 2026-10-30 | Flag a fixture popular entry when the mã is blank | Summary Add a read-only check that flags a fixture popular entry whose mã is blank. |
| 173 | MERGED | 2026-10-30 | Flag fixture photo paths with no image extension | Summary Add `scripts/photo_path_ext.py`, a read-only fixture check. |
| 174 | OPEN | — | Flag a fixture order line with a blank mã | Summary Adds a read-only check (`scripts/order_blank_ma.py`) that flags a fixture order line whose mã is missing, null, empty, or whitespace. |
| 175 | MERGED | 2026-10-30 | Flag a fixture catalog row with a blank mã | Summary Adds a read-only script, `scripts/blank_catalog_ma.py`, that flags a fixture catalog row when `ma` is missing, null, empty, whitespace-only, or not a string. |
| 176 | MERGED | 2026-10-30 | Flag a fixture mã that is not one letter plus two digits | Summary Adds a read-only check that flags a fixture mã which is not one uppercase letter plus two digits. |
| 177 | MERGED | 2026-10-30 | Flag fixture shop links that contain a space or a newline | Summary Adds a read-only check that flags a fixture shop link containing a space or a newline. |
| 178 | OPEN | — | Flag fixture intake mãs already in the catalog | Summary `scripts/intake_catalog_overlap.py` reads a fixture intake file and a fixture catalog. |
| 179 | MERGED | 2026-10-30 | Flag a fixture Giá line with no digit | Summary Adds a read-only check that flags a fixture Giá line with no digit. |
| 180 | MERGED | 2026-10-30 | Flag a fixture hex that is not # plus 3 or 6 digits | Summary Adds a read-only check, `scripts/hex_shape.py`, that flags a fixture hex which is not `#` plus 3 or 6 hex digits. |
| 181 | MERGED | 2026-10-30 | Flag intake saved dates after the fixture as-of date | Summary Add a read-only checker that flags a fixture intake saved date when it is after the as-of date stored in that fixture. |
| 182 | MERGED | 2026-10-30 | Flag a fixture popular price that differs from the catalog price | Summary Adds a read-only script, `scripts/popular_price_mismatch.py`, that flags a fixture popular price when it differs from that mã's fixture catalog price. |
| 183 | OPEN | — | Flag a held-list entry that is not one letter plus two digits | Summary Adds a read-only check that flags a held-list fixture entry that is not one letter plus two digits. |
| 184 | MERGED | 2026-10-30 | Flag a fixture sell price of zero | Summary Adds a read-only script, `scripts/zero_sell_price.py`, that flags a fixture catalog row when the sell price is 0. |
| 185 | OPEN | — | Flag an unknown size token | Summary Read-only check for a fixture size token outside S, M, L, XL, XXL, XS, and a plain number. |
| 186 | MERGED | 2026-10-30 | Skip Vercel deploys for cursor/* branches | Stops automatic Vercel deployments for agent branches named `cursor/*` on both apps. |
| 187 | OPEN | — | Hold the missing incomplete mãs | Draft only. Do not merge. `origin/main` `data/held.json` was missing A27, A28, A29, G01, H02, S16, S17, S18, and S19 from `heldIncomplete`. |
| 188 | OPEN | — | draft: require admin login on intake cost APIs (export/submissions/ma) | Summary Unsigned intake reads were returning Nhung’s costs and Taobao source links. |
| 189 | OPEN | — | Draft: gate intake cost reads behind shop admin | Routes covered `requireShopAdmin` now runs before these reads return a body: `GET /api/export` `GET /api/submissions` `GET /api/submissions/[ma]` `GET /api/ma/[code]` No session returns 401 `{ ok: false, error: "Unauthor |
| 190 | OPEN | — | Lock S06 at $25 on shop add and rename | Draft only. Do not merge. Why Shop save already refused every S06 dollar other than $25. |
| 191 | OPEN | — | Align auto-list config so Q02 stays listable | Draft only. Do not merge. This does not write Blob, intake, Meta, or a sell price. |
| 192 | OPEN | — | Hold the nine intake mãs missing from the live catalog | Draft only. Do not merge. This does not write Blob, intake, Meta, or a sell price. |
| 193 | MERGED | 2026-10-30 | Report public sell-price drift without changing prices | Draft only. Do not merge. This does not write Blob, intake, Meta, or any sell price. |
| 194 | MERGED | 2026-10-29 | Safe-frame merge: privacy gates + held gap + S06 lock (no visual frame change) | Deploy warning Set the shop-admin login on the intake Vercel project BEFORE this deploy, or Nhung cannot save.** `/api/export`, `/api/submissions`, and `/api/ma/*` now require the same shop-admin session as the shop tools. |
| 195 | OPEN | — | Give auto-list a public mã index with no costs | Draft — do not merge or deploy The service-token idea is dropped. |
| 196 | MERGED | 2026-10-29 | Open intake data links without a login | Direct links to intake data return 200 with no `Authorization` header and no cookie. |
| 197 | MERGED | 2026-10-29 | Add nosnippet on open intake data links | Boss asked to ship direct-link intake data `GET /api/submissions`, `GET /api/export`, `GET /api/ma/*`, and `GET /api/submissions/ ` stay open with no login and no service token. |
| 198 | MERGED | 2026-10-29 | Keep intake sell price optional | Nhung can save an intake row without typing a sell price, and the form does not ask her to apply an auto-calculated one. |
| 199 | MERGED | 2026-10-29 | Let intake save without an automatic sell price | What Nhung sees The auto-price box is optional. |
| 200 | MERGED | 2026-10-29 | Remove the intake password wall | No login `/admin`, `/admin/shop`, Shop tools, `/api/submissions` (read and save), `/api/export`, `/api/ma/*`, and `/api/shop-catalog` open with the link. |
| 201 | MERGED | 2026-10-29 | Remove the intake password | Anyone with the link can open and edit intake. |
| 202 | MERGED | 2026-10-29 | Show calculated sell prices on intake rows | Why so many said “Tính giá sau” 67 of 84 live rows have an empty sell field. |
| 203 | MERGED | 2026-10-30 | Safe combined: 45 visual-neutral script/test PRs (hard-checked) | Combines 45 hard-checked safe PRs that only add/improve behind-the-scenes scripts and tests (no shop/intake app UI). |
| 204 | MERGED | 2026-10-31 | Harden scripts/tests: fix 12 fix-needed failure modes (held.json, S06, pins) | Draft only. Do not merge. Brings the fix-needed script checks onto main `339e77b` and fixes why they failed there. |
| 205 | MERGED | 2026-10-31 | Harden intake/shop health: open-by-link, noindex, S06$25, held 404 | Will change Intake `/api/*` and `/admin*` stay open by link (no 401, no password form) and send `X-Robots-Tag: noindex, nofollow, nosnippet`. |
| 206 | MERGED | 2026-10-31 | Fix intake tiered-price-diff false FAIL (local tieredSellUsd) | Why main fails today On main `339e77b`, intake `npm test` fails one test: `sassy-closet/tests/tiered-price-diff.test.ts` — "sell-site code does not import the tiered quote". |
| 207 | MERGED | 2026-10-31 | Scrub cost fields from shared/live-price-snapshot.json (privacy) | Why privacy hard_recheck fails on main today `scripts/hard_recheck.sh` runs `privacy_scan.py --git-diff` against old base `eb8a143` (not against the previous commit). |
| 208 | OPEN | — | Harden intake FX and shop health noindex after POST-207 | Why this one PR After #205, intake data routes and shop `/api/health` are open by link and noindex, and the public shop health body is only `blob.configured` plus `blob.readable`. |
| 209 | OPEN | — | Harden intake open-by-link/noindex regressions (post-#208) | Why this one PR After #205, `/api/submissions`, `/api/export`, `/api/ma/*`, and `/admin` are open by link. |
| 210 | OPEN | — | Hold a pickup with no usable landed cost even when Boss approved | Bug:** In `scripts/pickup.py` `plan_pickups`, an intake row with a blank or garbled ¥ and no landed_usd quotes as `no-price`. |
| 211 | OPEN | — | Match the JS mã key in Python: drop a BOM, ASCII digits only | Bug:** Python `held_policy.norm_ma` disagreed with JS `canonicalMaSpelling` on (1) UTF-8 BOM — a held mã in a CSV first cell missed the held gate and could be quoted for listing (same for S06 $25 lock); (2) fullwidth dig |
| 212 | OPEN | — | Live smoke: check S06's own JSON-LD offer is $25, not any $25 on the page | Bug:** Live shop smoke for S06 passed if "$25" appeared anywhere on `/m/S06`. |
| 213 | OPEN | — | Host health: held PDP must also 404 under alternate spellings | Bug:** Daily `host_health_check` only asserted held S19 returns 404 at exact `/m/S19`. |
| 214 | OPEN | — | Too-cheap: S06 missing from live catalog or off $25 is LOCK_DRIFT | Bug:** `too_cheap_check` reported QUIET_OK when S06 was absent from the live catalog (no lock row at all), and its outcome still said QUIET_OK even with S06 lock-drift off $25. |
| 215 | OPEN | — | hard_recheck: default base = merge-base with main (fix false FAIL on fresh clones) | What happened On a fresh clone of `main`, `eb8a143` is not in history. |
| 216 | OPEN | — | hard_recheck: parse Node spec-reporter test counts (ℹ tests N) | Summary On modern Node, the spec reporter prints test counts as `ℹ tests 218` (and the same shape for pass, fail, and skipped). |
| 217 | OPEN | — | Combined safe bundle #208-#216 (do not merge without Boss) | Why one draft Draft PRs #208 through #216 are each one commit on current `main`. |
| 218 | OPEN | — | Fail closed when Blob is down, and drop held folders from other mãs | What changed Two customer-facing holes, both invisible on the current live catalog. |
| 219 | OPEN | — | Keep a blank intake sell blank and parse pasted yen safely | Why A blank sell box was still posted as a calculated dollar, so a later bot treated that price as typed. |
| 220 | OPEN | — | Fix midnight QC home prices on RSC flight HTML | Midnight QC reads sell-home HTML to compare catalog prices with Blob. |
| 221 | OPEN | — | Guard shop workflows against wrong days, stale intake, and silent holds | Why Five local workflows could look successful while using the wrong shop day, an old intake file, or a crashed heartbeat. |
| 222 | OPEN | — | Keep held-sheet landed digits aligned with the printed quote | What changed The Boss held-price sheet stored landed cost at 4 decimal places and printed 2. |
| 223 | OPEN | — | Add a read-only workflow status report | What this does `scripts/workflow_status.py` prints one plain status report for the Sassy Closet workflows. |
| 224 | OPEN | — | Keep open Boss decisions the digest and streak were dropping | The Boss digest and the cost-recheck streak were dropping or stretching open decisions. |
| 225 | OPEN | — | Draft: one branch for the safe shop fixes (#217–#224) | Draft only One branch for Boss to review. |
| 226 | OPEN | — | Read the flat midnight QC summary in the daily draft | The daily draft still read an old midnight QC file: `counts`, `fails`, `warns`, `pass2.agrees`, and `s06.blob`. |
| 227 | OPEN | — | Show the shop-draft proposal in the daily summary | The shop-draft runner wrote the held-price sheet under the day's report folder, then ran the daily summary without telling it where that file was. |
| 228 | OPEN | — | Recognize padded and short caption mãs before the price check | The caption linter only accepted a mã with exactly two digits. |
| 229 | OPEN | — | Compare padded caption mãs with the catalog price | `caption_price_mismatch.py` only took a two-digit mã. |
| 230 | OPEN | — | Keep a bad live price from dropping the cost-basis report | `cost_basis_reconcile.py` read a live catalog only as a products list, and only when every price was already a finite number. |
| 231 | OPEN | — | Do not serve a held folder from another mã's image URL | A live mã's public image URL could return a held folder's bytes when the catalog src pointed at that folder. |
| 232 | OPEN | — | Run the hard recheck on pull requests | Pull requests install both apps and run `scripts/hard_recheck.sh --json --base origin/main`. |
| 233 | OPEN | — | Draft: read-only parity check for pricing, mã, and sizes | Summary Draft only. This adds a read-only parity checker for pricing, mã spelling, size rules, and the committed catalogs. |
| 234 | OPEN | — | Read padded QC-note mãs as the shop key | QC notes named a post or Reel with a two-digit mã capture. |
| 235 | OPEN | — | Prefix CSV formula starters in the intake export | Intake CSV export wrote a color or note that starts with `=`, `+`, `-`, `@`, a tab, or a carriage return as a bare spreadsheet cell. |
| 236 | OPEN | — | Draft: keep a trailing .0 on in-window EU shoe sizes | Summary Shop `parseAsiaSizes` turned `40.0` into `400` and dropped the size. |
| 237 | OPEN | — | Compare caption Giá with a padded or lowercase price key | `caption_gap_watch.py` only kept a price key that was already a clean mã, and only a value that was already a number. |
| 238 | OPEN | — | Read on-hand rows stored under a variant mã key | `GET /api/ma/{code}` found the staged row for `a01`, `A001`, or `S006`, then looked up Square on-hand only under the canonical key. |
| 239 | OPEN | — | Add an on-demand read-only browser smoke | On-demand Playwright smoke for both sell hosts and intake. |
| 240 | OPEN | — | Draft: note that shop pricing prefers the yen cost | Summary The checker now records a Boss note when shop `calcPricing` and intake disagree on which cost field to use. |
| 241 | OPEN | — | Keep sold and hold rows out of the intake live price | `intake_gaps.py` treated a catalog row as the live shop price unless the status was hidden, draft, or deleted. |
| 242 | OPEN | — | Return 503 when an intake save cannot read the store | `GET` routes already answer a corrupt or unreadable intake store with 503 and a fixed Vietnamese message. |
| 243 | OPEN | — | Draft: keep EU sizes when importing a G submission | Summary Shop intake import kept only Asia letters, so a G row sized `40.0 35,36` lost every size. |
| 244 | OPEN | — | Check every live S06 row in the daily snapshot | The reduced daily shop check stopped at the first live S06. |
| 245 | OPEN | — | Return 503 when a share card cannot read the catalog | `GET /share/m/{mã}` and `GET /share/c/{slug}` already 404 when the mã or category is missing. |
| 246 | OPEN | — | Add a read-only draft merge-readiness report | Read-only list of open draft pull requests. |
| 247 | OPEN | — | Draft: keep an in-window trailing .0 on intake shoe chips | Summary Intake `keepSizesForKind` treated `40.0` as a different chip from `40` and dropped it. |

Missing numbers: none.

