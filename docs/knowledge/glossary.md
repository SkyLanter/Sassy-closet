# Glossary

Definitions are paraphrased from the cited file. If the name appears and the file does not define it, the entry says so.

| Term | Meaning | Source |
| --- | --- | --- |
| Boss | The person who says yes or no. Slack `#shop-decisions` is where that yes/no is recorded. The repo does not give a legal name. | `README.md` |
| Mini Boss | Launches Cloud Agents and reviews with Boss. Ask webhook is named `MINIBOSS_ASK_*`. | `README.md`, `excel-kit/KIT.md` |
| Nhung | Name the check scripts use for the intake cost ("Nhung's intake ¥"). Who the person is beyond that is UNKNOWN. | `scripts/too_cheap_check.py`, `scripts/cost_basis_reconcile.py` |
| Luxubu | Named party who must agree with Mini Boss before a Meta QC line counts as pass. Also a local status JSON written from CLI flags. Not defined as the Facebook login. | `scripts/daily_summary_draft.py`, `scripts/luxubu_status_record.py` |
| Muse pack | Local `TODAY.md` plus a pack message. Sections are decisions, caption gaps, and reused codes. Sends nothing. | `scripts/muse_pack_sections.py` |
| mã | The piece code. Two formats: intake/shop `A01`, Official Excel `AO001`. | `scripts/ma_shape.py`, `excel-kit/schema.py` |
| Giá | The price word on a caption. Canonical form is `Giá $NN`. | `scripts/caption_lint.py` |
| Mã line | Caption line 1, canonical `Mã X00`. | `scripts/caption_lint.py` |
| Held / heldIncomplete | Mãs with incomplete Taobao data. Off the public sell catalog. PDP 404. | `data/held.json`, `sassy-closet-shop/lib/held-incomplete.ts` |
| neverList | Second list in `held.json`. Empty on this commit. Same off-catalog treatment. | `data/held.json` |
| hold (status) | A catalog status that still has a public page and asks the customer to inbox for the price. Not the same as heldIncomplete. | `sassy-closet-shop/lib/site-settings.ts` |
| S06 lock | That mã's sell dollar stays 25. | `sassy-closet/lib/publish-guard.ts` |
| Debox | USD added into landed cost. Locked at 7.50 for V, Q, and D. | `sassy-closet/lib/pricing.ts` |
| Landed | CNY / FX + debox, in USD. | `sassy-closet/lib/pricing.ts` |
| Tiered sell | Whole-dollar quote whose margin slides from 35% at $25 to 25% at $45. | `scripts/autolist.py` |
| Flat 25% | `ceil(landed / 0.75)`, plus $2 under $10. | `sassy-closet/lib/pricing.ts` |
| Inbox giá | Caption when the price is blank or the margin is under the 35% floor. | `sassy-closet/lib/pricing.ts` |
| Taobao | Supplier site. Incomplete mãs stay off the sell catalog. | `README.md` |
| e.tb.cn | Taobao share short link. `freshness_check.py` reads the public list price from the `price=` parameter on the Taobao or Tmall item URL embedded in an e.tb.cn bridge page. `intake_shop_link_flags.py` accepts a Taobao item URL or an e.tb.cn share as a valid intake link. | `scripts/freshness_check.py`, `scripts/intake_shop_link_flags.py` |
| Cainiao | China-to-US freight used in the September 2026 margin research docs. Not the live price function. | `sassy-closet-shop/docs/CAINIAO_WEIGHT_SCALE_2026-09-10.md` |
| Square Free | On-hand inventory source of truth. Track stock ON. | `README.md` |
| Official Excel / SoT | `Sassy_Closet_SoT.xlsx`. Working copy, mã index, captions. Not a second inventory. | `excel-kit/schema.py` |
| Kit | The actor that syncs generated workbooks to OneDrive after merge, separate from the Cursor Cloud Agents that change `excel-kit/` code. Runs on the shop machine / OneDrive sync host. How it runs is not in repo. | `README.md`, `excel-kit/sot/FROM_GF_WATCH.md` |
| Hub ten | The allowlist A01, S01, P01–P05, K01, H01, A02. | `sassy-closet-shop/lib/catalog-contract.ts` |
| Blob | Vercel Blob. Intake store and shop catalog are different tokens. | `sassy-closet/docs/SHOP_ADMIN.md` |
| Seed | `sassy-closet-shop/data/products.json`. Fallback catalog, not the live 62-mã set. | `docs/seed-vs-live-mismatch.md` |
| Intake | The Next app in `sassy-closet/`. | `sassy-closet/README.md` |
| Sell shop / sell-test | The Next app in `sassy-closet-shop/`. | `README.md` |
| noindex | `noindex, nofollow, nosnippet` on intake `/api` and `/admin`. | `sassy-closet/lib/intake-direct-link-headers.ts` |
| Open by link | No session and no password on intake routes. | `sassy-closet/lib/shop-admin-gate.ts` |
| Draft only | Agents open pull requests. Boss merges. Bots do not post or Save. | `README.md` |
| PT | `America/Los_Angeles`. | `scripts/freshness_check.py` |
| Flight string | Open PR #220 is titled "Fix midnight QC home prices on RSC flight HTML". Its body says the live home page embeds the catalog in a "Next.js RSC flight string", with quotes escaped. Python sources do not contain `flight` or `__next_f`. On main, `qa_a11y_watery_motion.py` `look_pdp` matches both backslash-escaped and plain `"ma"` / `"priceUsd"`, and only on the held product pages P02 and P05. `midnight_qc.py` `_HOME_PRICE_RE` matches plain quotes in sell-home HTML. | `sassy-closet-shop/docs/ai-clothing-shop/qa/qa_a11y_watery_motion.py`, `scripts/midnight_qc.py`, open PR #220 |
| Piece | A numbered local draft folder used by the bundle scripts. Not the same as a GitHub PR number. | `scripts/bundle_inventory_check.py`, `docs/checkpoints/START-HERE.md` |
| GF | "From GF" intake packets for the Excel kit. Primary path is OneDrive `Documents/Sassy Closet/From GF/`. | `excel-kit/prompts/GF_CLOTHES_INTAKE.md` (wording also in merged PR #3) |
| Zelle | A pay method in the orders sheet, and a word the sell shop shows. | `excel-kit/schema.py` `SOT_PAY` |
| Popular order | JSON list that sorts looks. | `sassy-closet-shop/data/popular-order.json` |
| Q02 | Absent from `data/held.json`. `publishBlock` allows create, mint, and save. Midnight QC and `live_shop_smoke.sh` still expect it off the sell PDP until Boss approves. A 404 there is recorded as observed, and the QC text says it is not a never-list requirement. | `sassy-closet/tests/publish-guard.test.ts`, `scripts/midnight_qc.py`, `scripts/live_shop_smoke.sh` |
