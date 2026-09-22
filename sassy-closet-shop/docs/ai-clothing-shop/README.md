# How strong AI-built clothing shops are made

Notes for this sell-test shop. Learn from real boutique / apparel UX and Next persistence docs, then apply only what fits a **Kelly Ying–style unique-piece closet** (Message-first, no cart, no invented mãs).

This is not a Shopify clone brief. Big-store rules (size filters, 150-SKU grids, Stripe checkout) are recorded so we know **what not to fake**.

| Section | File | Applied on this site |
| --- | --- | --- |
| Messenger-first | [01-messenger-social-commerce.md](./01-messenger-social-commerce.md) | `m.me?text=` mã; Hold ≠ Reserved; one how-to line; no cart / ship $ |
| Catalog UX | [01-catalog-ux.md](./01-catalog-ux.md) | Collection piece counts; `aria-current` on category nav; related “more pieces” |
| Tiny-boutique admin | [02-tiny-boutique-admin.md](./02-tiny-boutique-admin.md) | Unsaved-change guard on Add/Edit |
| Admin reliability | [03-tiny-boutique-admin.md](./03-tiny-boutique-admin.md) | Receipt-only success; no seed fallback on corrupt live; unique allowlist mãs |
| PDP color · size | [02-pdp-color-size-ux.md](./02-pdp-color-size-ux.md) | Text-only pills; tagged ∪ untagged gallery; Asia + stored cm; Hold copy |
| Per-color media | [03-per-color-media.md](./03-per-color-media.md) | Gallery live region + lightbox; empty = — |
| AI product media | [05-ai-product-media.md](./05-ai-product-media.md) | Hub slugs on the ten; `colorId` null or on this mã; `order`; Hold stays |
| Message-first trust | [04-message-first-trust.md](./04-message-first-trust.md) | How-to-buy + Meetup & ship (dest in Messenger after confirm; no ship $) |
| SEO · trust · share | [06-seo-trust-diaspora-boutique.md](./06-seo-trust-diaspora-boutique.md) | Per-mã OG; 308 `/m/A01`; robots+sitemap exist; **test stays noindex** |
| Next + Blob arch | [04-next-blob-catalog-arch.md](./04-next-blob-catalog-arch.md) | Kit import; HTTP export/import; no-store shop HTML; Blob ≠ intake |
| Next + Blob | [05-next-blob.md](./05-next-blob.md) | `updatedAt` on catalog.v1; Blob `cacheControlMaxAge: 0` asserted |
| AI-shop failures | [06-ai-shop-failures.md](./06-ai-shop-failures.md) | Health `publicSafety` + copy scan smoke |
| SEO · empty · a11y | [07-seo-empty-a11y.md](./07-seo-empty-a11y.md) | Category ItemList JSON-LD; empty `role=status`; OG images absolute when origin is set |
| Dropship ops rail | [08-dropship-ops-runbook.md](./08-dropship-ops-runbook.md) | Inquiry → Hold → Zelle → Taobao order on shop / how-to-buy; P02/P05 Hold; no invented ship $ |
| Bugcheck QA | [09-bugcheck-sell-site-checklist.md](./09-bugcheck-sell-site-checklist.md) | Change mã uniqueness; Blob Save→revalidate; text colors; P02/P05 Hold |
| Kit-lane #29 APPLY | [29-sell-test-apply.md](./29-sell-test-apply.md) | Next-mã trap tiles off; Blob Save receipt; `m.me?ref=`; 4.5 MB upload cap |
| Customer motion | [10-customer-pleasing-motion-ux.md](./10-customer-pleasing-motion-ux.md) | Official #31 playbook (§18 ORIGIN PASTE) |
| Kit-lane #31 APPLY | [31-motion-apply.md](./31-motion-apply.md) | no-preference loops; covers paint; same-mã VT + lightbox; ≤200ms tabs |
| Admin feature matrix | [14-complete-admin-feature-matrix.md](./14-complete-admin-feature-matrix.md) | Official #32 merchandiser spine (Save/cache/import) |
| Kit-lane #32 APPLY | [32-admin-matrix-apply.md](./32-admin-matrix-apply.md) | Blob receipt + hashed covers + import; **Boss Add A03+ / rename extras** |
| Kit-lane #29 source | [29-AI_CLOTHING_SHOP_APPLY_TO_SELL_TEST.md](./29-AI_CLOTHING_SHOP_APPLY_TO_SELL_TEST.md) | Official apply list (checkboxes for this shop) |
| Dropship boutique law | [07-taobao-dropship-boutique.md](./07-taobao-dropship-boutique.md) | Official #21 playbook (warehouse voice out; Message-first) |
| Kit-lane #21 APPLY | [21-dropship-apply.md](./21-dropship-apply.md) | Seed + status microcopy; Save confirm; on-hand / đang có rejected |
| Messenger copy bank | [12-fb-messenger-dropship-copy.md](./12-fb-messenger-dropship-copy.md) | Official #30 phrase bank (Owner-paste). §9 is the shop clipboard |
| Kit-lane #30 APPLY | [30-copy-apply.md](./30-copy-apply.md) | Short announce A0/A1; per-mã PDP how-to; Hold not-reserved; 1-look rail |
| Kit-lane #34 APPLY | [34-chrome-apply.md](./34-chrome-apply.md) | 1–1.5px gold/ink metal film on header + Message CTA; Featured goo on hairline only |
| Liquid chrome SAFE | [18-visual-fx-liquid-chrome-safe.md](./18-visual-fx-liquid-chrome-safe.md) | LEARN 21 / PR #34 §18 — chrome only, never wreck covers |
| iOS frosted carousel | [16-ios-frosted-carousel-deep.md](./16-ios-frosted-carousel-deep.md) | LEARN 16 / PR #36 §21 — native snap + port mask + sibling frost |
| Kit-lane #36 APPLY | [36-carousel-apply.md](./36-carousel-apply.md) | Native watery roll; `colorId` tagged ∪ null; never borrow another mã |
| FeaturedBoard springs | [20-visual-fx-motion-springs.md](./20-visual-fx-motion-springs.md) | LEARN 20 / PR #37 §19 — `layoutId` spring + Recipe A pour |
| Kit-lane #37 APPLY | [37-springs-apply.md](./37-springs-apply.md) | `springSoft` hairline; `layoutScroll`; 320ms clip tween; `replay={false}` |
| CSS snap / mask / VT | [19-visual-fx-css-snap-mask-vt.md](./19-visual-fx-css-snap-mask-vt.md) | LEARN 19 / PR #38 §22 — named 3/4 frame, directional paper-edge, chrome frost only |
| Kit-lane #38 APPLY | [38-snap-vt-apply.md](./38-snap-vt-apply.md) | Named `product-{THIS mã}` frame; peek mask iff neighbor; lightbox veil; no wrap |
| Apple water glass PDP | [18-visual-fx-apple-water-glass.md](./18-visual-fx-apple-water-glass.md) | LEARN 18 / PR #39 §19 — color → reel roll; frost chrome on peek edges |
| Kit-lane #39 APPLY | [39-water-glass-apply.md](./39-water-glass-apply.md) | Kill same-JPEG remount; tagged/shared scroll; edge frost; APG |
| A11y watery motion | [17-a11y-watery-motion.md](./17-a11y-watery-motion.md) | LEARN 17 / PR #40 §18 — named chips, same-src quiet, reduce-safe hover |
| Kit-lane #40 APPLY | [40-a11y-apply.md](./40-a11y-apply.md) | Color 1/2 or admin names; no fake cover motion; Featured stays tabs |

Intake at `sassy-closet.vercel.app` is a different app. Do not deploy over it.
