# Apply playbook → sell-test shop

Target: **https://sassy-closet-shop.vercel.app**  
Repo for *these notes*: SkyLanter/Sassy-closet (kit lane).  
Origin sell-site **`main` is off-limits.** Apply on the sell-test project / a shop feature branch only.

Playbook: `docs/ai-clothing-shop/` (sourced URLs).  
Allowlist: `excel-kit/sell_test_allowlist.py`.

## Hard stops (every item)

- Never invent mã. Only **A01 S01 P01 P02 P03 P04 P05 K01 H01 A02**.
- Intake (`sassy-closet/` + `sassy-closet.vercel.app`) **untouched**.
- No Square Save.
- No Facebook Send / Post.
- No passwords.

## Preserve (do not “clean up”)

1. **Kelly Ying design** — paper `#fff` / ink `#111` / blush `#f3eee8` / gold `#b08968` / gold-deep `#8c6a4e` / line `#ececec` / muted `#6b6b6b`. Body **Be Vietnam Pro**. Display **Cormorant Garamond**. Not intake Allura / rose `#D82B60`.
2. **Fancy motion** — `announce-fade` (4.2s), `shimmer-slide` (1.3s), `cta-flash` on `.cta-shine:hover`, `site-header` view-transition, `--duration-enter:.21s` `--duration-exit:.15s` `--duration-move:.4s`. Keep `prefers-reduced-motion` kill switch.
3. **Admin ↔ shop link** — `/admin` stays off the main nav (“Test only”) but keeps **Back to shop** / Open sell-test editor. Do not orphan admin. A discreet shop→admin affordance for Boss is OK; do not put Admin in the primary chips (Tops / Sets / …).
4. **Message-first** — “Message to buy. No cart.” Unique piece, qty 1. Zelle is footer copy only.
5. **Hold · Inbox for price** on **P02** and **P05** (no USD on the card).
6. **Bilingual** EN title/description + VN flavor.
7. **`noindex, nofollow`** until Boss says launch.
8. **Vercel Blob** as catalog storage (already on `/admin`).
9. **Per-color hex boxes** — no names on storefront swatches; admin note stays admin-only.
10. Facebook Page stay: `https://www.facebook.com/profile.php?id=61594312648057` (or `m.me` for that Page). Do not swap in a random Page.

## Concrete apply list

Do these on sell-test. Check each box only when the live URL proves it.

### A. Mã lock (collision)

- [ ] Remove or disable **Add item / next-mã tiles** (A03, Q01, V01, K02, G01, B01, P06, H02, J01, S02, O01, D01).
- [ ] Create/update of any mã outside the allowlist returns **4xx** and does not write Blob.
- [ ] `/m/A03` stays not-found. Grid count stays **10**.
- [ ] Do not alias `A01` ↔ `AO001`.

### B. Silent save

- [ ] Keep per-row **Save {mã}** (no blur autosave).
- [ ] Success toast + failure toast (show Blob / validation error).
- [ ] After success: `revalidatePath` `/`, `/m/{ma}`, `/c/{slug}` so prerendered home updates. Source: https://nextjs.org/docs/app/api-reference/functions/revalidatePath
- [ ] Save A01 → hard refresh `/m/A01` shows the new title (manual proof).
- [ ] Uploads > 4.5 MB use **client** Blob upload, not a silent drop. Source: https://vercel.com/docs/vercel-blob/server-upload

### C. Seed drift

- [ ] Git seed / `public/products/*/cover.jpg` must **not** overwrite a non-empty Blob catalog on deploy.
- [ ] Empty Blob: may load the 10 allowlist covers once; never invent extra mãs while seeding.
- [ ] Filter counts are computed from Blob rows, not hardcoded “Accessories 5”.
- [ ] Add **Export JSON/CSV** on `/admin` (or use the kit CLI already on `cursor/catalog-export-clone-official-5ad2`).
- [ ] Gate with **both** (after that PR merges):

```bash
python3 excel-kit/scripts/validate_sell_catalog.py ./out/sell-catalog.v1.json
python3 excel-kit/sot/validate_sell_catalog_export.py ./out/sell-catalog.v1.json
```

- [ ] Merge with sibling catalog-export / CLONE_TO_OFFICIAL — do not start a second writer. See `docs/ai-clothing-shop/MERGE.md` and `excel-kit/docs/CLONE_TO_OFFICIAL.md` (sibling).

### D. Message-first (still no Send)

- [ ] Each card + PDP CTA opens Messenger / Page with **mã in context**.
- [ ] Prefer `https://m.me/<page>?ref=A01` (allowlist mã only). Source: https://developers.facebook.com/docs/messenger-platform/discovery/m-me-links/
- [ ] If `m.me` is not ready, keep the current profile URL but put **A01** in the visible button label (already: “Message A01 →”).
- [ ] Network tab: no `POST graph.facebook.com/.../messages`.
- [ ] Hold CTAs never show a fake dollar.

### E. Per-color media

- [ ] Admin: add hex → tag image → Save.
- [ ] PDP: swatch changes the gallery to images tagged with that hex.
- [ ] Light hex has a border on paper. No color *names* on shopper swatches.
- [ ] Do not mint `A01-RED` as a new mã.
- [ ] Cover path stays `/products/{MA}/cover.jpg` or a stable Blob pathname.

### F. Tiny admin

- [ ] Qty stays 1. New pieces (if Boss ever adds one) start Hold — but sell-test must not mint the mã.
- [ ] Storage badge: durable Blob vs ephemeral `/tmp`.
- [ ] No Square controls. No Send. No password dialog.
- [ ] Admin↔shop link survives CSS/nav refactors.

### G. Kelly Ying + motion (regression)

- [ ] Home still has editorial tiles + Featured collection, not a stripped inventory table.
- [ ] Cormorant display headings, Be Vietnam UI, gold/ink buttons.
- [ ] Announce / shimmer / CTA shine still run (and still disable under reduced motion).
- [ ] Header view-transition not removed “for performance” without Boss yes.

### H. Clone-to-Official (kit, after export)

- [ ] Export contains **exactly** the 10 mãs (validator `--strict-complete`).
- [ ] Official mapping is dry-run first. Existing Official `A01` → update or stop, never a second row.
- [ ] Photos → `Documents/Sassy Closet/Photos/{ma}/` + `photo_link` only.
- [ ] ASK STOCK before any mã not on the allowlist.
- [ ] `#shop-decisions` before Square Save. This apply list does **not** Save.
- [ ] Do not change `schema.parse_ma` to treat `A01` as `AO001` in passing.

### I. Out of scope (reject if a shop PR sneaks them in)

- Intake tab changes, Saved card, Mini Boss Ask, From GF.
- Origin shop `main` restyle / cart / SEO index.
- Shopify, Stripe checkout, Square widget.
- Customer PII in git.
- “Helpful” extra SKUs for empty categories (Pants Q01, Dresses D01, …).

## Verify (live URLs)

| Check | URL |
| --- | --- |
| Grid 10 | https://sassy-closet-shop.vercel.app/ |
| Tops A01 A02 | https://sassy-closet-shop.vercel.app/c/ao |
| Hold thermos | https://sassy-closet-shop.vercel.app/m/P02 |
| Available top | https://sassy-closet-shop.vercel.app/m/A01 |
| Admin + Blob + Save | https://sassy-closet-shop.vercel.app/admin |
| Invented mã dead | https://sassy-closet-shop.vercel.app/m/A03 |

## Paste block (Cloud Agent on a **shop** repo — not this kit, not Origin main)

```
Apply excel-kit/prompts/AI_CLOTHING_SHOP_APPLY_TO_SELL_TEST.md to the Sassy Closet SELL-TEST shop
https://sassy-closet-shop.vercel.app only.

Preserve Kelly Ying design (paper/ink/gold, Be Vietnam + Cormorant) + fancy motion
+ admin↔shop link. Message-first, no cart.

HARD STOPS: never invent mã (only A01 S01 P01–P05 K01 H01 A02).
Intake untouched. No Square Save. No FB Send. No passwords.
Do not fight Origin shop main.

If catalog export / CLONE_TO_OFFICIAL is in progress, merge — import
excel-kit/sell_test_allowlist.py and run validate_sell_catalog_export.py.
```
