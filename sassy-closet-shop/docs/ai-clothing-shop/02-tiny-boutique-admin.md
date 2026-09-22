# Tiny-boutique admin

## What strong shops do

Shopify’s own merchandising model for color-split products is **parent listing + child identity**, edited from a product row, with a “view product page” escape hatch ([Combined listings help](https://help.shopify.com/en/manual/products/combined-listings-app), [dev combined listings](https://shopify.dev/docs/apps/build/product-merchandising/combined-listings)). The admin is not a second catalog. The storefront reads what the merchant just saved.

CodePup’s production post-mortem of AI-built stores names **silent form failure** as the third most common outage: the UI says saved, nothing is persisted ([AI store fails at 2am](https://codepup.ai/blog/ai-store-fails-in-production)). Miracuves calls the same pattern a “silent checkout crash” when success chrome is not backed by a write ([silent checkout crash](https://miracuves.com/blog/silent-checkout-crash-ai-frontend-database-failure/)). For a boutique admin that *is* the catalog, leaving Add/Edit without a prompt is the same class of bug.

SKU uniqueness is non-negotiable. Combined listings still give each child its own URL/handle. We use mã uniqueness + allowed letters instead of inventing handles.

## What we already had

- Catalog row → `/admin/edit/[ma]`, Preview PDP, sticky Save, toasts, write-then-read-back.
- Hold default on Add. Rename uniqueness.
- No password theater. No Square Save.

## Applied here

- Dirty-state guard: `beforeunload` + confirm on “Back to catalog” when the draft differs from the last successful load/save.

## Deliberately not applied

- Draft/publish workflow (two catalogs). This shop is one live document.
- Inventory counts, barcode, compare-at price.
