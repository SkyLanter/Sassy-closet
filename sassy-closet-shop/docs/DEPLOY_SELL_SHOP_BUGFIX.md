# Deploy note — sell shop bugfix

**Branch:** `cursor/sell-shop-bugfix-676e`  
**Bugfix commit:** `44e4cc0e88958993c3d0ed559fe373c61497ffcc`  
**Deploy the branch tip** (this note may sit one commit after that SHA).  
**Base:** `origin/cursor/sell-site-bugcheck-d648` (`fd2d4bc`, H01 colors, size chips, sheen, buy-bar space) plus the opaque header search sheet.  
**Intended production:** [https://sassy-closet-shop.vercel.app](https://sassy-closet-shop.vercel.app) (Vercel project `sassy-closet-shop` only)  
**Do not deploy over intake:** [https://sassy-closet.vercel.app](https://sassy-closet.vercel.app)

Catalog Blob was not written. No new mã, price, size, color, or ship amount. Margin formula and holds are unchanged. No Square. No Facebook or Instagram post.

## What changes on the live shop

- Header search keeps `/?q=` on first paint and keeps the typed query when you open a look.
- Looks category tabs filter inside the current search. A tab with no match says so.
- Suggestion list is opaque paper and sits under the category tabs.
- Unknown `/c/{slug}` and `/m/{ma}` respond **404** (shop header stays). `/c/phu-kien-toc` still 308s to `/c/toc`.
- `/c/*` uses the same Looks catalog as home (Popular sort, no second search box).
- Message stays the repo contract: desktop `https://m.me/61594312648057` in the **same tab**; phone `fb-messenger://user-thread/61594312648057`. Live production currently uses `target="_blank"` / `web-newtab`. This deploy **stops** that new-tab behavior.

## APPLY (Mini Boss)

From a checkout of `cursor/sell-shop-bugfix-676e`, linked only to project `sassy-closet-shop`:

```bash
git fetch origin cursor/sell-shop-bugfix-676e
git checkout cursor/sell-shop-bugfix-676e
npm ci
npm run build
npx vercel --prod --yes
```

`npm run build` already passed on this branch before the land note. Do not point the deploy at the intake project.

Spot-check list is in `BUG_REPORT.md`.
