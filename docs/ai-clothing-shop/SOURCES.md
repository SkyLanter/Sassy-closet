# Sources

URLs used in this playbook. Snapshot date: **2026-09-09**. Prefer the live page over a paraphrase.

## Sell-test (first-party)

| URL | Used for |
| --- | --- |
| https://sassy-closet-shop.vercel.app/ | Featured collection, 10-piece grid, filters, Messenger / Zelle footer |
| https://sassy-closet-shop.vercel.app/admin | Tiny admin, Blob, next-mã tiles, per-color hex + image tag |
| https://sassy-closet-shop.vercel.app/m/A01 | PDP: unique piece, no cart, `$25`, Message A01 |
| https://sassy-closet-shop.vercel.app/m/P02 | Hold · Inbox for price (thermos) |
| https://sassy-closet-shop.vercel.app/c/ao | Tops category (A01, A02) |
| https://sassy-closet-shop.vercel.app/c/set | Sets (S01) |
| https://sassy-closet-shop.vercel.app/c/phu-kien | Accessories (P01–P05) |
| https://sassy-closet-shop.vercel.app/c/ao-khoac | Jackets (K01) |
| https://sassy-closet-shop.vercel.app/c/toc | Hair (H01) |
| https://www.facebook.com/profile.php?id=61594312648057 | Current shop Messenger / livestream target |
| https://sassy-closet.vercel.app | Intake (do not restyle shop to match; do not edit) |

## Boutique catalog UX

| URL | Used for |
| --- | --- |
| https://depict.ai/resources/blog/10-best-practices-for-fashion-store-product-grid-design | Fashion grid: filters with counts, 44px targets, hover/second image, scroll model |
| https://craftshift.com/shopify-product-grid-color-swatches-ux/ | Swatches under image, 4–6 max, 44px hit, light-color border, a11y name |
| https://suplex.design/blog/product-listing-page-best-practices | PLP columns (desktop 3–4, mobile 2), visual-first fashion cards |

## Message-first / social commerce

| URL | Used for |
| --- | --- |
| https://developers.facebook.com/docs/messenger-platform/discovery/m-me-links/ | `m.me/{PAGE}?ref=` — open a thread; `ref` is context, not a Send |
| https://developers.facebook.com/documentation/business-messaging/messenger-platform/discovery/m-me-links | Same, current Business Messaging copy |
| https://developers.facebook.com/docs/messenger-platform/reference/webhook-events/messaging_referrals/ | `ref` payload when a thread already exists |
| https://developers.facebook.com/docs/messenger-platform/send-messages/template/product/ | Product template — **do not wire Send API** (hard stop) |
| https://developers.facebook.com/docs/facebook-business-extension/fbe/guides/catalog/ | Meta catalog as optional *inbox* aid, not site checkout |
| https://developers.facebook.com/docs/commerce-platform/catalog/feed/ | Feed replace vs `update_only` (seed-drift cousin) |
| https://tailortalk.ai/ | Fashion DMs as the real store (pattern, not a vendor pick) |
| https://sellthread.com/ | Stay-in-chat browse (pattern). Sassy stays human inbox + Zelle. |

## Tiny admin / unique pieces

| URL | Used for |
| --- | --- |
| https://art.industries/ | One record per unique work; site reads the archive |
| https://art.industries/makers | Piece inventory: photos, price, location, Available / reserved / sold |
| https://nventory.io/solutions/industries/handmade-crafts-inventory | One-of-a-kind oversell across channels |
| https://stockria.com/features/inventory-tracking | Maker SKU + custom fields (size/color) — contrast with qty=1 boutique |

## Per-color media

| URL | Used for |
| --- | --- |
| https://help.shopify.com/en/manual/products/product-media/add-images-variants | One assigned image per variant; extra shots live on the product gallery |
| https://help.shopify.com/en/manual/products/variants/add-variants | Option × value = variant; SKU is unique |
| https://shopifytheme.blog/multiple-variant-images-in-shopify/ | Color galleries need extra mapping (metafield / filter), not one JPEG |

## Next.js + Blob

| URL | Used for |
| --- | --- |
| https://vercel.com/docs/vercel-blob/server-upload | `put()`, 4.5 MB server limit, `revalidatePath` after upload |
| https://vercel.com/docs/vercel-blob/private-storage | Private vs public store; access chosen at create time |
| https://vercel.com/kb/guide/how-to-upload-and-store-files-with-vercel | Public URLs for product photos; private for internal docs |
| https://vercel.com/blog/vercel-blob-now-generally-available | Blob + `next/image` |
| https://nextjs.org/docs/app/guides/caching | `force-dynamic`, `force-cache`, tags, ISR |
| https://nextjs.org/docs/app/api-reference/functions/revalidatePath | Bust `/`, `/m/[ma]`, `/c/[slug]` after admin save |

## Failure modes (AI shops)

| URL | Used for |
| --- | --- |
| https://meetanshi.ai/blog/audited-50-vibe-coded-ecommerce-apps/ | Silent payment/order; missing error paths |
| https://meetanshi.ai/blog/bolt-new-ecommerce-problems/ | Seed/auth that works locally and dies in prod |
| https://www.vibefix.co/blog/cursor-bolt-lovable-when-ai-apps-break | Silent catch; env-only-in-`.env` |
| https://dev.to/ndabene/vibe-coding-in-e-commerce-why-80-of-ai-generated-modules-will-never-make-it-to-production-4p6m | Display hooks without delete/update hooks (phantom SKUs) |
| https://johal.in/war-story-ai-hallucinations-broke-our-black-friday | LLM-minted codes — validate against a pre-approved set |

## This repo (kit law)

| Path | Used for |
| --- | --- |
| `README.md` | Kit vs OneDrive SoT; bots draft only |
| `sassy-closet/README.md` | Blob durable store; `/tmp` wipe; export as backup |
| `sassy-closet/BOSS.md` | Four intake tabs; no Square Save |
| `excel-kit/DESIGN_NOTES.md` | Square = on-hand; Official = working copy |
| `excel-kit/PROMPTS.md` | Existing Cloud Agent contracts |
