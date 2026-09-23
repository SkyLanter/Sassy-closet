# Origin APPLY — PR #28 §18 F1–F16

Sell-test Save cannot look green while Blob or public HTML stays old. Kelly Ying look stays.

| ID | Landed |
| --- | --- |
| F1 | Catalog `get({ useCache: false })` on every Blob read |
| F2 | Overwrite `put` + `cacheControlMaxAge: 0` — not enough without F1 |
| F3 | Save success only after write + read-back + receipt `{ ok, blobWritten, catalogSha, revalidated }` |
| F4 | `revalidatePath("/m/[ma]", "page")` and `/c/[slug]` `"page"` |
| F5–F6 | Two public warms; validate Hold/price before put |
| F7 | Shop covers are `/products/{MA}/cover.jpg?v=` — never in-place `cover.jpg` overwrite |
| F8 | Add next mã (A03+) Saves to Blob and appears on shop; Official `AO001` still 400 |
| F9 | `GET /api/admin/catalog` private no-store + `catalogSha` |
| F10 | `/admin` stays `force-dynamic` + no-store |
| F11 | Hold ⇔ `priceUsd` null; P02/P05 never $23 |
| F12 | Look lock — paper/blush/gold, Messenger, Zelle, Facebook livestream, Message to buy |
| F13 | Sell-test Blob prefix `{SITE_ID}/` — not intake `store.json` |
| F14 | `/admin` `data-save-contract="blob+revalidate"` |
| F15 | `POST /api/admin/revalidate` (GET is 405, never 404) |
| F16 | Import rejects extras / P05 $23, then F2+F4 |

Gate: `python3 docs/ai-clothing-shop/qa/qa_selltest_origin_gate.py`  
Preview Save drill: `SHOP=… ADMIN_TOKEN=open docs/ai-clothing-shop/qa/qa_origin_save_drill.sh` (admin is open; any token string works as a header).
