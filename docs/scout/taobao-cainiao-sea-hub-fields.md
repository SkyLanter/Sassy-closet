# Taobao + Cainiao sea path — hub fields for held mãs (LEARN)

**Access / write date:** 2026-10-02 · **DRAFT ONLY** · Browse / GET · **Never 旺旺 / cart / checkout / buy** · **Never invent a ship $** · **No Blob write · no price change · no publishing held mãs**

**Why this file exists:** held and new mãs need a place to store *inputs* a later sea quote would use. This note names those hub fields. It does **not** price any mã.

**Rate SoT stays elsewhere.** Billable math, the 0.5 kg ladder, the 2026-09-09 App sample, the stale 2025 tax-incl unit card, fuel, and the sea ETA samples are already in [PR #44](https://github.com/SkyLanter/Sassy-closet/pull/44) `docs/scout/cainiao-weight-scale.md`. Company comparison (Cainiao parcel sea vs agents that floor at 12–21 kg) is already in `sassy-closet-shop/docs/china-us-best-ship-rate-20260909.md`. **This file does not reprint those ¥ tables and does not assign a dollar to any mã.**

---

## Hard stops

- No per-mã ship dollar. No customer flat rate. No live Blob price.
- No credentials. A Taobao or Cainiao login wall is a **Boss unlock**, not something this note stores.
- Held mãs stay off the sell catalog. This file does not mint mãs and does not add columns in code.

---

## 1) What a 2026-10-02 re-check changed

Public pages opened today still match the 2026-09-15 LEARN. Nothing here replaces that ladder.

| Check | Result 2026-10-02 | vs PR #44 |
| --- | --- | --- |
| `calculator.cainiao.us/static/js/calculator_en.js` | HTTP 200. `Last-Modified: Sun, 13 Oct 2024 21:00:57 GMT` | **Same stamp** #44 already cited. Formula not re-derived here. |
| [cainiao101](https://www.cainiao.us/p/cainiao101) | Page stamp **2026-03-31**. Economy Sea **32–43 business days**. 0.5 kg steps. Warehouse may repack at 合单. | **Same guide** #44 citation #9. |
| Tax-incl sea card [cainiao.us](https://www.cainiao.us/p/air-shipping-tax-inclusive-line) / [cainiaobuy twin](https://www.cainiaobuy.com/p/air-shipping-tax-inclusive-line) | Still the **2025-07-23** card: two **kg bands** (0–21.5 with a first weight, 21.51–65 with no first). | **Same STALE card** #44 already flagged against the live App sample. Not a new table. |
| [Expected-delivery samples](https://quaily.com/usave/p/cainiao-expected-delivery-time) | Sea **~25 days** (no inspection) / **~37 days** (inspection). Page is a 2024 trace, not a 2026 SLA. | **Same samples** #44 citation #10. |
| Web search 2026-10-02 | No newer **full US tax-incl weight table** than that 2025 card + the 2026-09-09 App sample + the Apr 2026 fuel card already in #44. | No new ¥. |

**Weight bands (structure only — ¥ stay in #44):**

1. **Billing step** is **0.5 kg** after `max(actual, L×W×H cm / 6000)`. Soft apparel that is vacuumed or laid flat usually bills on **actual**. A gift box or shoe box flips the same piece onto **volume**.
2. **One jacket or one dress is not the billed object.** Cainiao bills the **合单** (the merged export parcel). A solo piece still rounds **up** to the next 0.5 kg step. Do not freeze one haul’s total onto every mã.
3. **Tax-incl sea card bands** (stale 2025 page, still up): **0–21.5 kg** and **21.51–65 kg**. A closet haul of tops, dresses, and jackets sits in the **first** band. The second band is not this shop’s parcel.
4. **Wrong band:** agent / LCL sea lines that start at **12–21 kg** (already called out in the 2026-09-09 best-rate note). Those are not the product for a 0.5–3 kg apparel 合单.

**Timelines (already sourced — not a new promise):**

- Plan sea as **about a month**, using the published **32–43 business day** Economy Sea line, with the older door samples **~25 / ~37 calendar days** as illustrations of inspection vs not.
- A **2024-09-15** coupon-blog post says pay 合单 by **14:00 Friday China time** to catch a **Wednesday** sailing ([cainiao.us fastest-order note](https://www.cainiao.us/p/cainiao-consolidated-shipping-fastest-order-time)). That is a staff anecdote on a promo site, **not** an official schedule and **not** in #44. Do not quote it to a customer as a ship-by date.
- Air is the speed alternative only. This file does not re-price it.

---

## 2) How the sea path actually moves (so we know which fields exist when)

Sourced from [cainiao101](https://www.cainiao.us/p/cainiao101) (stamp 2026-03-31, fetched 2026-10-02) and the consolidation overview dated **2026-09-14** ([quaily Cainiao cost/time guide](https://quaily.com/cainiaopromocode/p/shipping-from-china-to-usa-cainiao-cost-time-complete-guide)). Same shape as the 2026-09-09 best-rate note: domestic to a China warehouse, then one export.

```
GF paste (link, size, color, soft vs box)
        │
        ▼
Boss buys on Taobao later  →  seller ships domestic to the
Cainiao warehouse address from the App (“Go Consolidation”)
        │
        ▼
Warehouse intake may record: status, weight, dimensions,
package number, seller
        │
        ▼
App tab “To Merge”  →  Boss picks sea  →  App shows Weight fee
        │
        ▼
Pay 合单  →  export  →  US last mile (FedEx / UPS or similar)
```

**Two ids that are easy to mix up** (not in #44). Tracking note, body updated through **2026-03-31**, fetched **2026-10-02**: [how to track](https://www.cainiao.us/p/how-to-track-cainiao-consolidated-shipping-us).

| Code | What it is | Hub use |
| --- | --- | --- |
| **LP…** logistics number | The number to track. Boss’s 2026-09-09 shots already used `LP…` ids. | Store **after** the parcel exists. |
| **HS** | Route label for **tax-included sea** (“Hanshui Sea”). **Not** a US tracking number. | Lane tag only, after Boss picks sea. |
| **HA** | Route label for **tax-included air**. | Not the default for soft clothes. |

US last-mile tracking may be **missing inside the App** on the tax-incl lines (same page: local numbers stopped showing after the 2025 tax-incl change). Leave last-mile blank until a real carrier number exists.

---

## 3) Hub fields to capture

Sell `Product` today (`sassy-closet-shop/lib/types.ts`) stores `sourceLink`, `fulfillment`, size, color, and price. It has **no** weight, dims, or logistics number. GF intake (`excel-kit/templates/from_gf/INTAKE_TEMPLATE.txt`) stores `source`, size, color, `price_original`, `notes`. It has **no** weight or box flag.

**Do not add these columns in this PR.** Capture them in staff notes / a later schema pass. Blank means unknown. Never fill a blank with a guessed gram or a guessed dollar.

### 3a) GF can fill now (before any parcel)

| Field | Ask | Rule |
| --- | --- | --- |
| `source` | Taobao / shop URL | Keep the short link. Same normalize as `source-link.ts`. Empty if she has none — do not invent a URL. |
| kind letter | Áo / Váy / Áo khoác / Set / … | The letter is a **planning** hint only. #44’s kind-gram rows are **estimate / open**, not a scale weight. |
| `size` | Asia size + cm | SKU match. |
| `color` | As she says | SKU match. |
| `packed` | soft polybag **or** box (shoe box, gift box, hanger) | This is the vol risk. A jacket in a box is not “soft actual.” |
| seller grams | only if the page **shows** a 重量 | Planning note. **Not** billable kg. Often behind the login wall — leave blank. |
| 现货 / 预售 | only if the page **shows** it | Clock **before** sea days start. #44: world PDP hid this on the opened mãs. Leave blank. |
| `price_original` + currency | item ask she saw or paid | **Item** cost. Not ship. |

### 3b) Only the warehouse / App can fill (leave blank until then)

| Field | When it becomes real |
| --- | --- |
| inbound status | Parcel shows under **To Merge**, or it does not. |
| actual grams | Warehouse scale. |
| L, W, H cm | Warehouse measure. |
| billable kg | App **Weight fee**, else the #44 formula. App wins when both exist. |
| domestic tracking | After the seller ships to the warehouse. |
| `LP…` logistics number | After intake. |
| lane | `HS` once Boss picks sea. Not a tracking number. |
| App sea total | Boss’s Cainiao checkout for **that** 合单. **Haul** cost. Do not divide it onto mãs and do not write it as the customer ship $. |

### 3c) What not to store

- A customer-facing US ship dollar.
- A yen copied off the stale 2025 card onto one mã.
- `HS` in the tracking field.
- Credentials, warehouse personal addresses, or a reconstructed 淘口令.

---

## 4) Held set this note is for

Ship column is **blank on purpose**. No row was weighed for this pass. No row is a price.

| mã | Why it is in this note | In `HELD_INCOMPLETE_MAS` on main (2026-10-02) | Ship $ |
| --- | --- | --- | --- |
| **K03** | Newer held context (jacket letter → soft, unless GF says it is boxed) | **No.** Not in this checkout. Do not mint. | blank |
| **K04** | same | **No.** | blank |
| **K05** | same | **No.** | blank |
| **V04** | Newer held context (dress letter → soft, unless boxed) | **No.** | blank |
| **S14** | Older held incomplete. Off the sell catalog. | **Yes** | blank |
| **A24** | same | **Yes** | blank |
| **A25** | same | **Yes** | blank |
| **S15** | same | **Yes** | blank |
| **A26** | same | **Yes** | blank |
| **K02** | Older held incomplete. Jacket letter. Off the sell catalog. | **Yes** | blank |

`HELD_INCOMPLETE_MAS` in `sassy-closet/lib/held-incomplete.ts` is only **S14, A24, A25, S15, A26, K02**. Shop tools do not add that set to Blob. **K03 K04 K05 V04** are named here as the newer held motivation. They are not published by this note.

For every row above, the useful GF ask is the same: short link, Asia size + cm, color, soft vs box, and item ask **if she already has it**. Grams, dims, `LP…`, and any sea total stay blank until a warehouse shot exists.

---

## 5) Boss unlock (no credentials)

Logged-out research still cannot see seller **重量**, item **运费 / 包邮**, or **现货 / 预售** on the desktop item page. PR #44 (2026-09-15) already showed `item.taobao.com` as a login wall and world PDP as the public surface that **omits** those three. This pass did **not** log in and did **not** re-open those PDPs.

Boss unlock, when someone needs those fields **before** a parcel exists:

1. Taobao (Boss’s own session) for 重量 / 运费 / 现货 on the held links.
2. Cainiao App for a live **To Merge** weight. Public cards are not that checkout.

Do not paste passwords into git, Slack, or this file.

---

## 6) Citations

| # | Source | Used for | Date |
| --- | --- | --- | --- |
| 1 | PR #44 `docs/scout/cainiao-weight-scale.md` | Rate ladder, billable formula, App sample, ETAs already written | written 2026-09-15 · still open |
| 2 | `calculator_en.js` response header | Unchanged `Last-Modified` | fetched **2026-10-02** |
| 3 | https://www.cainiao.us/p/cainiao101 | App steps, Economy Sea 32–43 bd, 0.5 kg, repack | stamp 2026-03-31 · fetched **2026-10-02** |
| 4 | https://www.cainiao.us/p/air-shipping-tax-inclusive-line and cainiaobuy twin | Stale band **shape** only (0–21.5 / 21.51–65). ¥ not copied here. | page 2025-07-23 · search **2026-10-02** |
| 5 | https://quaily.com/cainiaopromocode/p/shipping-from-china-to-usa-cainiao-cost-time-complete-guide | Warehouse may record status, weight, dimensions, package number, seller | page **2026-09-14** · fetched **2026-10-02** |
| 6 | https://www.cainiao.us/p/how-to-track-cainiao-consolidated-shipping-us | **HS** ≠ tracking; track **LP…** | updated thru 2026-03-31 · fetched **2026-10-02** |
| 7 | https://www.cainiao.us/p/cainiao-consolidated-shipping-fastest-order-time | Friday 14:00 CST anecdote. **Not** an SLA. | page **2024-09-15** · fetched **2026-10-02** |
| 8 | `sassy-closet/lib/held-incomplete.ts` | Older six mãs off catalog | main **2026-10-02** |

No 旺旺 · no cart · no buy · no invented ship $.
