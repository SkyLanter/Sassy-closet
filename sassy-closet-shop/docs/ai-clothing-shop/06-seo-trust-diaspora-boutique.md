# 06 — SEO / trust APPLY (sell-test)

Official lesson: [PR #25](https://github.com/SkyLanter/Sassy-closet/pull/25) (`docs/ai-clothing-shop/06-seo-trust-diaspora-boutique.md` on Official, head `d557016`).

This sell-test **applies customer-facing trust + share polish** and **does not flip public index**. Test HTML stays `noindex, nofollow` until Boss says otherwise.

## Applied

- Unique home / category / per-mã titles and descriptions. Hold = Inbox for price. Available USD only when real. No “on hand” / “đang có” warehouse voice.
- `og:title` `og:description` `og:image` `og:url` `og:type` + Twitter `summary_large_image`. Share cards are 1200×630 (`/opengraph-image`, `/share/m/{MA}`, `/share/c/{slug}`) — blush / ink / gold, mã + kind + price-or-Hold. No personal name, no ship $.
- Self-canonical when a shop origin is resolvable (`NEXT_PUBLIC_SHOP_URL` or Vercel host). Never hardcode a shop hostname in the data layer.
- `/m/a01` → **308** `/m/A01` (and `/m/a01/opengraph-image`). Category slugs lowercase.
- `robots.txt` exists: allow `/`, disallow `/admin/` `/api/`. **Do not Disallow `/`** — hide is page-level noindex.
- `sitemap.xml` lists `/`, `/how-to-buy`, `/meetup-ship`, `/c/*`, uppercase `/m/{MA}` when an origin exists.
- Announcement (h-8, rotating): livestream · meetup or US-quote ship · Message / Zelle after confirm. No `$`.
- How-to-buy + Meetup & ship pages and footer links. Dest sent **in Messenger after confirm**. Zelle is a rail word only.
- Fulfill sentence under Message to buy (PDP + mobile bar).
- Organization + Product JSON-LD. No `shippingRate` / `shippingDetails`. Dropship available stays `PreOrder`, not fake `InStock`.
- Admin layout stays explicit `noindex` even if the shop later goes official.

## Deliberately not applied

- `robots: { index: true }` on the test shop.
- Invented flat ship $, Zelle dest, meetup street pin, or Thang Tien Huynh.
- `hreflang` split. EN chrome / VN soul on one URL.
- Indexing intake (`sassy-closet.vercel.app`).
