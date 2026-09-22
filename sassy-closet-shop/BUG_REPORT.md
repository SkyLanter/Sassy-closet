# Sell shop bug check — 2026-09-21

Shop only: [https://sassy-closet-shop.vercel.app](https://sassy-closet-shop.vercel.app). Intake [https://sassy-closet.vercel.app](https://sassy-closet.vercel.app) was not changed. No new mã, brand, size, color, stock, or ship price. No Square save, no Facebook/Instagram post, no Blob write, no margin or hold change.

Land commit: `44e4cc0e88958993c3d0ed559fe373c61497ffcc` on `cursor/sell-shop-bugfix-676e`. Deploy the branch tip.

Local proof: `npm run build` (Next.js 16.3.4) passed. `npm run smoke:search`, `smoke:pdp`, `smoke:bugcheck`, `smoke:fb-rank`, `smoke:dropship`, `smoke:media`, `smoke:motion`, and `smoke:seo` passed. Production server `next start` on this branch returns real 404s (below). Dev: [http://127.0.0.1:43127](http://127.0.0.1:43127).

## Fixed

| Finding | What was wrong | Where |
| --- | --- | --- |
| Header search ignored `/?q=` on first paint | The field started empty and only copied the URL in an effect, so a shared search link looked blank and the grid was already filtered. | `lib/look-search.ts` (`x-sassy-q` encode/decode), `proxy.ts`, `components/shop-search.tsx`, `app/(shop)/layout.tsx`, `components/header-search.tsx` |
| Leaving home wiped the query | Any path other than `/` forced the draft to `""`, so a search typed in the header disappeared on a look or category. | `components/header-search.tsx` (`UrlQueryReader`) |
| Category tab ignored the search | With a needle set, Looks still showed every match and left the highlighted tab's count unfiltered. | `components/featured-board.tsx` |
| Suggestion sheet covered the category tabs | The old sheet was frosted glass, absolutely placed over the tab row. | `components/header.tsx`, `components/header-search.tsx` (`.shop-search-sheet` after the nav), `app/globals.css` |
| Unknown `/c/*` and `/m/*` were HTTP 200 | `app/(shop)/loading.tsx` wrapped those pages in a Suspense boundary, so `notFound()` rendered the empty state but the status stayed 200. | Home skeleton moved to `app/(shop)/(browse)/loading.tsx`. Category and product pages stay under `app/(shop)/layout.tsx` and now return **404** with the shop header. `app/(shop)/c/[slug]/page.tsx` calls `notFound()` from metadata. `app/not-found.tsx` title is `Not found · Sassy Closet`. |
| Search field focus ring was removed | `outline-none` dropped the gold keyboard ring. | `components/header-search.tsx` |
| Category grid did not follow the header query | A search kept in the header still listed every look on `/c/*`. | `components/looks-catalog.tsx` |
| 均码 could be mistaken for a letter | Customer sizes must stay Asia letters only. | `scripts/smoke-pdp.ts` (guard). Chip component was already honest. |

Checked in the browser on this branch (390×844 and 1280×800):

- `/?q=puppy` paints `value="puppy"` and filters Looks. `/?q=zzzznotfound` keeps that text and shows “Không thấy mã hoặc tên đó · No look matches that search.”
- Dresses tab under `puppy` reads “Đầm · Dresses, 0 looks” and “Không có trong mục này · Nothing in this tab matches.”
- Suggestion sheet is opaque paper (`rgb(250, 247, 244)`, no backdrop blur) and starts 1px under the tab row.
- `/c/ao` is left-aligned “Tops”, Popular is the active sort, and the only search field is the header.
- `/c/tops` and `/m/ZZNOPE` are HTTP 404, title “Not found · Sassy Closet”, shop header still on the page.
- `/c/phu-kien-toc` is 308 to `/c/toc`.
- Phone buy bar does not cover the footer Message control at the end of the page (about 60px clear on a 390×844 PDP). Gallery photo fills its frame (no hole) at 844px and 700px tall.
- iPhone user agent: Message is `fb-messenger://user-thread/61594312648057` with no `target`. Desktop: `https://m.me/61594312648057` in the same tab.
- No page JavaScript errors on those flows.

## Deferred

- **Live Messenger opens a new tab.** Production HTML uses `target="_blank"` and `data-messenger-scheme="web-newtab"` even for an iPhone. This branch does not copy that. Shop smoke forbids `target="_blank"` on Message because it opens a blank Safari tab and blocks the app scheme. After `vercel --prod`, desktop Message is same-tab `m.me`, and phones open the Messenger app. Separate “Open on web” stays `https://m.me/61594312648057`.
- **Live category pages are an older layout** (centered title, a second search field, featured-pour). This branch’s `/c/*` matches home: Looks catalog, Popular sort, header search only. That is the alignment, not a new template.
- **English slugs such as `/c/tops` are not categories.** Real slugs stay Vietnamese (`ao`, `quan`, `vay`, `dam`, `ao-khoac`, `giay`, `tui`, `phu-kien`, `toc`, `trang-suc`, `set`, `khac`). Only `phu-kien-toc` redirects.
- **Paths that are not a shop route** (for example `/this-does-not-exist`) 404 from the root not-found page, without the shop header. Unknown categories and mãs keep the header.
- **Seed `data/products.json` has no size letters**, so a local PDP does not render size chips. Live A01 is S / M / L. Chips still show only stored letters `2XS XS S M L XL 2XL`. 均码 stays an empty size list. No letters were invented.
- **`metadataBase` warning** during build (Open Graph images fall back to localhost) is pre-existing. Not part of this pass.
- **No production deploy from this environment.** Vercel is not logged in here. Blob catalog was not read for writes and was not wiped.

## Spot-check after deploy

- [https://sassy-closet-shop.vercel.app/](https://sassy-closet-shop.vercel.app/)
- [https://sassy-closet-shop.vercel.app/?q=puppy](https://sassy-closet-shop.vercel.app/?q=puppy)
- [https://sassy-closet-shop.vercel.app/?q=zzzznotfound](https://sassy-closet-shop.vercel.app/?q=zzzznotfound)
- [https://sassy-closet-shop.vercel.app/c/ao](https://sassy-closet-shop.vercel.app/c/ao)
- [https://sassy-closet-shop.vercel.app/c/vay](https://sassy-closet-shop.vercel.app/c/vay)
- [https://sassy-closet-shop.vercel.app/c/tops](https://sassy-closet-shop.vercel.app/c/tops) (expect 404, shop header, “Không tìm thấy”)
- [https://sassy-closet-shop.vercel.app/c/phu-kien-toc](https://sassy-closet-shop.vercel.app/c/phu-kien-toc) (expect 308 to `/c/toc`)
- [https://sassy-closet-shop.vercel.app/m/A01](https://sassy-closet-shop.vercel.app/m/A01) (sizes S M L)
- [https://sassy-closet-shop.vercel.app/m/V03](https://sassy-closet-shop.vercel.app/m/V03)
- [https://sassy-closet-shop.vercel.app/m/D05](https://sassy-closet-shop.vercel.app/m/D05)
- [https://sassy-closet-shop.vercel.app/m/H01](https://sassy-closet-shop.vercel.app/m/H01) (Pink, Blue, Wine; no invented size letter)
- [https://sassy-closet-shop.vercel.app/m/ZZNOPE](https://sassy-closet-shop.vercel.app/m/ZZNOPE) (expect 404)
