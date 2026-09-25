# Failure modes AI clothing shops hit

Three failures Boss named — **silent save**, **seed drift**, **mã collision** — plus the ones every vibe-coded store repeats.

## 1. Silent save

**What it looks like:** Admin shows the new title, you refresh `/m/A01`, old copy is still there. Or Save “works” and Blob never got the JSON.

**Why AI shops do this**

- Empty `catch {}` — [VibeFix: silent failures](https://www.vibefix.co/blog/cursor-bolt-lovable-when-ai-apps-break).
- Write to `/tmp` on Vercel; next deploy is empty. This repo already burned that on intake (`sassy-closet/README.md`).
- Server Action returns 200 after a failed `put`.
- Storefront is **prerendered**; Save updates Blob but nobody calls `revalidatePath` ([caching guide](https://nextjs.org/docs/app/guides/caching)). Sell-test `/` is prerendered today.
- Client upload > 4.5 MB silently dropped ([Blob server upload](https://vercel.com/docs/vercel-blob/server-upload)).
- “Autosave on blur” with no toast — looks saved, request aborted on navigate.

**Sassy apply**

- Keep **explicit Save {mã}**. No blur-save.
- Toast **Đã lưu** / **Lưu lỗi** with the Blob error text.
- After OK: revalidate `/`, `/m/{ma}`, `/c/{slug}`.
- `/admin` storage line must say durable vs ephemeral.
- Never treat a 200 HTML navigation as proof the JSON landed — read-back the mã.

## 2. Seed drift

**What it looks like:** Git `products.json` has 10 pieces; Blob has 8; the grid still says All **10**. Or a deploy resets Blob from seed and P02’s Hold note disappears.

**Why**

- Prisma/JSON seed runs on every deploy and **replaces** production ([Bolt ecommerce problems](https://meetanshi.ai/blog/bolt-new-ecommerce-problems/) — local vs prod config).
- Meta-style **full replace** feeds delete anything not in the file ([Catalog feed](https://developers.facebook.com/docs/commerce-platform/catalog/feed/) `update_only=false`).
- Intake `migrateLocalToDurableIfNeeded` copies local → Blob **only if Blob is empty**. A “helpful” empty seed write makes the next migrate look like a restore.
- Filter counts hardcoded (`Accessories 5`) instead of `items.length`.
- Two Blob stores (preview vs production) with different seeds.

**Sassy apply**

- Seed is a **fallback when Blob has zero allowlist rows**, never an overwrite.
- Export after important Saves (intake already: “`/admin` export is the backup”).
- Validator `--strict-complete` fails if any of the 10 mãs are missing.
- Do not commit live Official rows or a filled Square CSV as a “seed.”
- Preview deploys must not point at Production Blob unless Boss says so.

## 3. Mã collision

**What it looks like:** Two pieces claim `A01`. Or the agent “helps” by minting `A03`. Or Excel `AO001` is treated as shop `A01`.

**Why**

- `nextMa()` / “next unused mã” tiles. Sell-test admin **already shows A03, Q01, V01, …**.
- LLM-generated codes. [Black Friday war story](https://johal.in/war-story-ai-hallucinations-broke-our-black-friday): never let a model mint a token; check a **pre-approved set**.
- Display hooks without delete/update hooks → phantom SKUs ([DEV: vibe-coding ecommerce](https://dev.to/ndabene/vibe-coding-in-e-commerce-why-80-of-ai-generated-modules-will-never-make-it-to-production-4p6m)).
- Unique-piece sold on two channels ([Nventory](https://nventory.io/solutions/industries/handmade-crafts-inventory)).
- Intake `saveSubmission` will mint `A03` if you POST kind `A` without `new_ma`. That is why **intake stays untouched** and shop must not call it.

**Sassy apply**

- Allowlist is closed: `A01 S01 P01–P05 K01 H01 A02`.
- `refuse_invented_ma()` on every export / clone / admin create.
- Disable **Add A03** on sell-test.
- Never alias `A01` ↔ `AO001`.
- Sold / retired mãs stay retired (kit law). Do not recycle P02 if it later sells.
- 409 on duplicate, same spirit as intake: “Mã đã có rồi — không gộp.”

## 4. Other AI-shop classics (do not import)

| Failure | Source | Sassy response |
| --- | --- | --- |
| Payment charged, no order | [Meetanshi 50-app audit](https://meetanshi.ai/blog/audited-50-vibe-coded-ecommerce-apps/) | No cart. Zelle + inbox stay human. |
| Auth that works on localhost | [Bolt problems](https://meetanshi.ai/blog/bolt-new-ecommerce-problems/) | No passwords to misconfigure. |
| Env in `.env` only, not Vercel | VibeFix | Document **names** in `KIT.md`; never paste values. |
| Fetch entire catalog on every PDP | Meetanshi / Bolt | 10 rows — still cache + revalidate; don’t add Shopify-scale joins. |
| Fake checkout to look “done” | Common v0/Lovable demo | Message-first. No Stripe decorative button. |

## Quick test (sell-test)

1. `/` shows exactly the 10 allowlist mãs — no A03.
2. `/m/A03` stays not-found.
3. Save A01 title → hard refresh `/m/A01` shows the new title (not silent).
4. Redeploy → A01 cover still 200 (not seed wipe).
5. Export → validator OK.
6. Message CTA does not call Send API (network tab: no `graph.facebook.com/.../messages`).
