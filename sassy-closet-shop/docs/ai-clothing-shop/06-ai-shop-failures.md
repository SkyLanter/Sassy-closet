# Common AI-shop failure modes

## What the post-mortems say

1. **Silent success** — checkout or a form shows OK, the write never lands ([CodePup](https://codepup.ai/blog/ai-store-fails-in-production), [Miracuves](https://miracuves.com/blog/silent-checkout-crash-ai-frontend-database-failure/)). We refuse a fake card checkout. Admin Save still must read back.
2. **Invented catalog** — fake SKUs, lorem, “on hand” warehouse, reviews nobody wrote. Checkfix documents AI fake-shops that clone brands and harvest payments ([AI-generated fake shops](https://checkfix.io/en/ai-generated-fake-shops-risk-customers-businesses/)). This closet only uses Boss mãs and never invents `e.tb.cn` links.
3. **Price ≠ payable total** — agents and humans both bail when a hidden ship/tax $ appears ([Idukki / Perplexity](https://idukki.io/blog/perplexity-bought-from-our-store)). Ship is quoted in chat.
4. **Variant collapse** — parent SKU with no color/size id. We sell one mã qty 1; colors are tagged photos, not a fake size run.
5. **Seed vs live split** — the demo catalog keeps serving after Save. One Blob/KV/local document; seed is bootstrap only.
6. **Hardcoded hostnames + password theater** — official clones break; `/admin` grows a fake lock. Portability is `SITE_ID` + catalog.v1 export.

## What we already had

- Hold default, no Square Save, no FB Send, no personal name on the shop.
- Write-then-read, `smoke:link`, contract hostname scan.

## Applied here

- Health `publicSafety`: invented mãs (illegal letters) fail the route.
- `smoke:safety` scans shop/public components for Square, Facebook Send, `ADMIN_PASSWORD`, and the locked personal name.

## Deliberately not applied

- A pretend Stripe success screen “to look like a real store”.
