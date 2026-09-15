# Cainiao billable-kg + China → US playbook (DRAFT ONLY — Buy Research)

**Access / write date:** 2026-09-15 · **Never buy / never cart / never 旺旺 / no passwords / no invented customer flat ship $**

**Hard rule:** every ¥ has a URL, a Boss App shot, or an **illustrative** / **estimate** / **STALE** flag. No invented customer US ship $. No invented App checkout.

**Floor SoT:** this scout path (`docs/scout/cainiao-weight-scale.md`). Refresh of the 2026-09-10 weight-scale draft + 2026-09-09 US-rates draft. Prefer **this file** if they diverge.

**Boss override (why this file exists):** equal `¥158÷N` freezes one **2.547 kg** shoe+pajama App sample across every haul. More soft clothes → more billable kg → more inbound. **Scale by billable kg.** Prefer **sea tax-incl**.

**Dest context:** San Jose / Bay Area **951xx** is still **country-flat United States** on every public card opened this pass (no ZIP field).

---

## 0) How Boss should quote soft-clothes parcels

1. **Default lane:** sea tax-incl (App “and up”). Air = speed alt only.
2. **Billable first:** `chargeable = max(actual_kg, L×W×H_cm / 6000)`, then round **up to 0.5 kg**. Soft tops usually win on **actual** if vacuum / flat. Boxes (shoes, drinkware gift boxes, bag stuffing) flip to **vol**.
3. **Do not** write `¥158÷11 ≈ ¥14.36` (or `$2.14`) on every mã for every haul size. That number is the **2026-09-09** App sea total for **one** 2.547 kg merge, split equally. It is not a unit card.
4. **Do** estimate haul billable kg, then:
   - look up **total inbound ¥** from the live App, or from **column A** (illustrative ¥/kg from that same App sample) when the App is closed;
   - **per-mã share = total ÷ N** (equal), **or** weight-weighted by kind grams if Boss wants A vs P fairness.
5. When App shows a real 合单 **Weight fee**, **App wins**. Replace the estimate.
6. **Prefer sea** for clothing / bags / jewelry hauls that can wait. Live 2026-09-09 sample: sea **¥158+** vs air **¥375+** at the same 2.547 kg (~**¥217** cheaper; still “and up”).
7. **Drinkware / shoe boxes** (P02-class 保温杯, G giày) are not “soft.” Quote them on their own billable kg, or strip boxes at warehouse before merge.
8. **Never invent** a customer-facing US flat ship $. This file is China→US 集运 **cost context** only.

---

## 1) Live vs stale (2026-09-15 refresh)

| Rank | Source | What it is | Freshness this pass |
| --- | --- | --- | --- |
| **1 PRIMARY** | Boss Cainiao App shots **2026-09-09** | Same 2 parcels → billable **2.547 kg** → Sea tax-incl **¥158+** / Air tax-incl **¥375+** | **LIVE App** — **not re-shot 2026-09-15**. Still the only tax-incl checkout sample. |
| **2 NEW public card** | https://www.cainiao.us/p/price-update-us-au-uk-zh (and EN twin) | US fuel from **2026-04-01**: air **¥5 / 0.5kg** · sea **¥2 / kg** | Page **2026-03-31**. **Fetched 2026-09-15** (this URL **404’d** on the 2026-09-09 pass). |
| **3** | `calculator.cainiao.us/static/js/calculator_en.js` | Non–tax-incl Eco / Std / Sea; **vol/6000**; **0.5 kg ceil**; large-item **¥200** | **Re-fetched 2026-09-15** — same formulas as 2026-09-10. **Different product** (not 含税). |
| **4 STALE card** | Tax-incl unit cards Jul/Aug **2025** | Air Eco **¥47** / Fast **¥57** per 0.5kg; Sea first **¥52.35** + **¥15.4**/0.5kg | Pages still dated **2025-07-23** / **2025-08-23**. **Re-fetched 2026-09-15.** **STALE vs live App** at ~2.5 kg. |
| — | 2026 promo “from” floors | Air from **¥30** / Sea from **¥9** per 500g; new user 1 kg free | https://www.cainiao.us/p/cainiao-coupon-usave — title “2026年8月最新”; body “Last updated: March 31, 2026”; HTML touch **2026-08-31**. **Floors only — not a ladder.** |
| — | cainiao101 sample | 5.751 kg → Sea **¥171** / Eco air **¥426** / Std air **¥516** | Guide updated thru **2026-03-31**. **Not** tax-incl; **not** the App sample. |

**Do not mix lanes.** Tax-incl App / 2025 含税 cards ≠ calculator.js non-tax ≠ promo floors ≠ AliExpress Super Economy.

**Fuel vs App:** the 2026-09-09 App totals are **“and up”** on that day. This file does **not** add ¥5/0.5kg or ¥2/kg on top of **¥158+ / ¥375+** (double-count risk). Fuel is a **published add-on card** for planning when you are on a **pre-April unit table**. How the App rounded fuel on 2026-09-09 is **unknown**.

**WebSearch 2026-09-15:** no newer **full 2026 US tax-incl weight table** than the Jul/Aug 2025 cards + the live App sample + the Apr 2026 **fuel** card. Malaysia got a 2026-07-22 table — **wrong country**, excluded.

---

## 2) Billable weight (sourced)

```
volume_kg     = L × W × H  (cm)  /  6000
chargeable    = max(actual_kg, volume_kg)
billable_step = ceil(chargeable × 2) / 2     # 0.5 kg steps
```

Confirmed:

- Calculator JS (fetched **2026-09-15** and 2026-09-10): `volumeWeight = (length * width * height) / 6000`; `finalWeight = Math.max(volumeWeight, weight)`; `roundedWeight = Math.ceil(weight * 2) / 2`.
- Boss App **2026-09-09:** shoes 0.72 kg / 30×25×14 ≈ **1.75** vol + pajamas 0.371 kg / 33×29×5 ≈ **0.80** vol → sum **≈2.55** → App **Weight fee 2.547 kg**. Per-parcel max(actual, vol), **not** sum of actuals (~1.09 kg).

Reject / large (JS, non-tax tool only): reject if length ≥240 cm or girth ≥327 cm or weight ≥65 kg. Large-item **¥200** if weight >21.5 kg or length >120 cm or girth >265 cm (USAVE path in JS waives it). **Not** copied into tax-incl App totals.

---

## 3) Sea vs air (tax-incl)

| Lane | What to use | Live sample @ 2.547 kg (App 2026-09-09) | STALE 普货 card (re-fetched 2026-09-15) | ETA (sourced help — **not** on the App shots) |
| --- | --- | ---: | --- | --- |
| **Sea tax-incl** | **Default** for soft clothes | **¥158.00 and up** | First **¥52.35**/0.5kg + **¥15.4**/0.5kg (0–21.5 kg) | Guide samples **~25 d** (no inspection) / **~37 d** (inspection); cainiao101 Economy Sea **32–43 business days** |
| **Air tax-incl** | Speed alt | **¥375.00 and up** | Eco **¥47**/0.5kg · Fast **¥57**/0.5kg (no first-weight on 普货) | Fast-Air 普货 **7–9 wd** · Eco-Air 普货 **10–12 wd** (Aug 2025 launch post) |

Implied on **that haul only** (illustrative, not an official card):

`¥158 / 2.547 ≈ **¥62.03 / kg**` sea · `¥375 / 2.547 ≈ **¥147.23 / kg**` air  
→ ≈ **¥31.02 / 0.5 kg** sea · ≈ **¥73.62 / 0.5 kg** air.

**Sanity vs stale cards at ~2.5 kg:** sea card ≈ **¥113.95** · air Eco **¥235** · Fast **¥285** — all **below** live App **¥158 / ¥375**. **Do not plan a real merge from Aug’25 cards alone.**

Clothing bags are usually **普货**, not 敏货 (food etc.). Sensitive first-weights on the 2025 card (Eco first ¥120 / Fast first ¥130) are **out of scope** unless the SKU is food-class.

---

## 4) Side-by-side ladder

| Billable kg | **A) Live App linear (illustrative)** Sea ¥ | **A) Live App linear** Air ¥ | **B) STALE tax-incl card** Sea ¥ | **B) STALE** Air Eco ¥ | **B) STALE** Air Fast ¥ | **C) calc.js non-tax** Sea ¥ | **C) calc.js** Air Eco ¥ |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 0.5 | ≈31.0 | ≈73.6 | **52.35** | **47** | **57** | 66 | 71 |
| 1.0 | ≈62.0 | ≈147.2 | **67.75** | **94** | **114** | 66 | 71 |
| 2.0 | ≈124.1 | ≈294.5 | **98.55** | **188** | **228** | 87 | 142 |
| 2.547 | **158+** (App) | **375+** (App) | ≈114.0 @2.5 | 235 @2.5 | 285 @2.5 | — | — |
| 3.0 | ≈186.1 | ≈441.7 | **129.35** | **282** | **342** | 108 | 213 |
| 5.0 | ≈310.2 | ≈736.2 | **190.95** | **470** | **570** | 150 | 355 |
| 8.0 | ≈496.3 | ≈1177.9 | **283.35** | **752** | **912** | 213 | 568 |

**How each column is computed**

- **A (preferred planning when App closed):** `kg × (158/2.547)` sea · `kg × (375/2.547)` air. **Illustrative** — one live point. First-weight / fuel / remote may break linearity (especially **&lt;1 kg**, where A sea ≈31 **&lt;** card first ¥52.35). Still “and up.”
- **B (STALE official-looking unit cards):**
  - Sea ≤21.5 kg: first **¥52.35**/0.5kg + **¥15.4**/0.5kg add’l ([cainiao.us](https://www.cainiao.us/p/air-shipping-tax-inclusive-line) / [cainiaobuy twin](https://www.cainiaobuy.com/p/air-shipping-tax-inclusive-line), page **2025-07-23**, accessed **2026-09-15**).
  - Air 普货 no first: Eco **¥47**/0.5kg · Fast **¥57**/0.5kg ([us-air-shipping-with-tax-included-is-here](https://www.cainiao.us/p/us-air-shipping-with-tax-included-is-here), **2025-08-23**, accessed **2026-09-15**).
- **C (calc.js, non-tax):** sea `66 + max(0, round0.5−1)×21` (≤21.5 kg); air Eco `71 + ceil((round0.5−1)×2)×35.5` — JS re-fetched **2026-09-15**. **Not** tax-incl.

**MARGIN default:** column **A sea** for haul totals when billable kg is estimated; replace with App checkout when open. Keep B as cross-check. Never present A as “official card.”

Optional FX context only (not a customer quote): `1 USD = 6.725199 CNY` (open.er-api.com, **Tue, 15 Sep 2026 00:02:31 UTC**). 2026-09-10 sheet used 6.725515. Aug 2025 air-card page printed **7.17**. **Do not invent** a shop $ from these.

---

## 5) Soft-clothes billable-kg model

Catalog kinds (`sassy-closet/lib/kinds.ts`): A Áo · Q Quần · V Váy · D Đầm · K Áo khoác · B Túi · H Tóc · J Trang sức · P Phụ kiện · S Set · G Giày · O Khác.

| Kind | Typical actual (g) | Assumed flat dims (cm) | Vol kg (/6000) | Chargeable ≈ | Bill step | Cite / flag |
| --- | ---: | --- | ---: | ---: | ---: | --- |
| **A** áo / top | **200–450** (use **300**) | 30×25×3 | 0.375 | **0.375** | 0.5 | Agent tables (2026-09-10 search). Page fetch was blocked → **estimate / open**. Not re-weighed 2026-09-15. |
| **Q** quần | **200–650** (use **450**) | 35×28×4 | 0.653 | **0.653** | 1.0 | same — **estimate / open** |
| **V / D** váy · đầm | **300–1000** (use **450**) | 35×28×4 | 0.653 | **0.653** | 1.0 | same — **estimate / open** |
| **K** sweater / jacket | sweater **500–900** / jacket **500–1200** (use **600**) | 35×30×6 | 1.05 | **1.05** | 1.5 | **estimate / open** |
| **B** bag | **650–1100** (use **800**) | 40×30×12 | 2.40 | **2.40** | 2.5 | boxes inflate further — **estimate / open** |
| **S** set | mid soft **~500** | 35×28×5 | 0.817 | **0.817** | 1.0 | **estimate / open** |
| **P / H / J** tiny | **50–150** (P **100** / H·J **80**) | 20×15×2 | ≤0.10 | **≈actual** | 0.5 | **estimate / open**. **P thermos is not this row** — see P02 主图 (gift box + 800ml cup). |
| **G** giày | (out of soft model) | shoe box often **vol-driven** | — | live shoe 0.72 act → **~1.75** vol | — | Boss shot 30×25×14 — **sourced 2026-09-09** |

**Shop habit:** vacuum / remove boxes before merge, or volumetric owns the bill (live shoe box ~2.4× actual). P02-class 保温杯 ships like a **box**, not like a scrunchie.

**Open:** still no soft-only App merge (no shoe box) on file. Kind grams are not scale-weighed Sassy SKUs.

---

## 6) Scenarios (planning — estimates flagged)

FX is optional context only. **Customer US flat ship not invented.**

Method: **A live linear** as primary planning ¥, **B STALE** in parentheses. Billable kg = estimate / open unless noted.

### 6a) Stop `¥158÷N`

The **2026-09-09** App sea total **¥158+** belongs to **2.547 kg** (shoes+pajamas). Dividing by 11 (or any N) **does not** scale when the next haul is 3 kg, 4 kg, or 8 kg of clothes.

| If haul bills | A sea total | Equal share if N=11 | vs frozen ¥14.36 |
| ---: | ---: | ---: | --- |
| 2.547 kg (the sample) | **¥158+** | ≈¥14.4 | same haul only |
| 3.0 kg | ≈¥186.1 | ≈¥16.9 | ~18% higher |
| 4.0 kg | ≈¥248.1 | ≈¥22.6 | do not use ¥14 |

### 6b) Historical **11-mã** mix (MARGIN_20PCT_2026-09-10)

**3×A · 5×P · 1×S · 1×K · 1×H**. Live export **2026-09-15** has **more** mãs (A12+, B, J, D, O). Do not pretend the shop is still 11 rows.

| Piece of model | Value | Flag |
| --- | --- | --- |
| Sum estimated actual | ≈ **2.58 kg** | estimate |
| Optimistic one soft merge (~40×30×15) | vol **3.0** → bill **3.0** | estimate / open |
| **Planning billable used** | **3.0 kg** mid | replace with App Weight fee |

| Lane | Total @ 3.0 kg (A) | Total @ 3.0 (B STALE) | Equal /11 (A) |
| --- | ---: | ---: | ---: |
| **Sea tax-incl** | **≈¥186.1** | ¥129.35 | **≈¥16.9** |
| **Air tax-incl** | **≈¥441.7** | Eco ¥282 / Fast ¥342 | **≈¥40.2** |

Optional weight-weighted sea (A @ 3.0 kg = ¥186.1), mid grams as weights — **all estimate / open**:

| Kind | N | Mid g | Sea ¥ share (A) | vs equal ¥16.9 |
| --- | ---: | ---: | ---: | --- |
| A | 3 | 300 | ≈**¥21.6** each | heavier |
| P | 5 | 100 | ≈**¥7.2** each | lighter — **invalid if those P are 保温杯** |
| S | 1 | 500 | ≈**¥36.1** | heavier |
| K | 1 | 600 | ≈**¥43.3** | heavier |
| H | 1 | 80 | ≈**¥5.8** | lighter |

### 6c) **1** soft top (A-like)

Est. chargeable ≈0.375 → bill **0.5 kg**. Sea A ≈**¥31.0** · B card **¥52.35** (first-weight — prefer **card or App** for tiny parcels). Air A ≈**¥73.6** · B Eco **¥47** / Fast **¥57**. Per-mã = total.

### 6d) **5** soft pieces

Assume ~0.40 kg/pc → bill **2.0 kg**. Sea A ≈**¥124.1** (B ¥98.55) → equal ≈**¥24.8**. Air A ≈**¥294.5**.

### 6e) **20** soft pieces

Assume ~0.35 kg/pc → bill **7.0 kg**. Sea A `7×(158/2.547)≈¥434.2` (B sea 52.35+13×15.4 = **¥252.55**) → equal ≈**¥21.7**. Air A ≈**¥1030.6**.

**Pattern:** equal per-mã sea (A) moves with **billable kg / N**, not with a frozen ¥14. Denser J/H pull per-mã down; bulky K/B and **boxed drinkware** pull it up. **Never lock ¥158÷N.**

---

## 7) Live App sample (Boss screenshots) — 2026-09-09 PT

**Source:** Cainiao Consolidation App · tax-inclusive lines (Boss phone).  
**Shots (not in this git tree):** `scout/shots/cainiao-live-air-taxincl-20260909.jpeg` · `cainiao-live-sea-taxincl-20260909.jpeg` (attached 2026-09-09 write-up).  
**Never buy / never To Merge click by bots.**

| Item | Logistics No | Actual wt | Dims (cm) | Vol L×W×H/6000 |
| --- | --- | ---: | --- | ---: |
| Shoes | `LP00841222790229` | 0.72 kg | 30×25×14 | ≈1.75 kg |
| Pajamas | `LP00840799461457` | 0.371 kg | 33×29×5 | ≈0.80 kg |
| **App Weight fee** | | **≈1.091 kg actual** | | **2.547 kg** |

| Line (App label) | Shown total |
| --- | ---: |
| **Air** tax-included | **¥375.00 and up** |
| **Sea** tax-included (On-Time / special line) | **¥158.00 and up** |
| Delta (sea cheaper) | **≈¥217** |

Dest ZIP was **not** on the shot. Public cards remain United States country-flat. **951xx remote fee: no official Cainiao $ found.**

---

## 8) Fuel surcharge card (was 404 on 2026-09-09)

Fetched **2026-09-15**: https://www.cainiao.us/p/price-update-us-au-uk-zh · EN https://www.cainiao.us/p/price-update-us-au-uk  
Page date **2026-03-31**. Effective **2026-04-01 00:00** 合单.

| Country | Air surcharge | Sea surcharge |
| --- | --- | --- |
| **United States** | **¥5 / 0.5kg** | **¥2 / kg** |
| Australia | ¥6 / 0.5kg | Econ ¥5 / kg |
| UK | ¥6 / 0.5kg | — |

This playbook **does not** invent how many 0.5 kg steps the App used on the 2.547 kg shot, and **does not** add these ¥ on top of **¥158+ / ¥375+**.

---

## 9) What we still do not have

- Soft-goods-only App merge (no shoe box) vs the 2.547 kg sample
- ZIP-visible App quote **95125** vs AK/HI/remote
- Whether Apr 2026 fuel changed the **¥47/¥57** unit card (card HTML still 2025-08-23)
- Official per-state / zone $ table — **none found** (2026-09-09 and 2026-09-15)
- Taobao item-page 官方物流/跨境直邮 vs 集运 on a live clothing SKU (out of scope this LEARN — no 下单)
- Customer US last-mile $ (Inbox “báo phí ship”) — Boss-only

`gpn.cainiao.com/logisticsPlanQuery` still returns 暂无线路 without UI origin/dest. Taobao `pcs.i56.taobao.com/.../shipCalculator` is login/UI — **no live $ this pass**.

---

## 10) Citations (URLs + dates)

| # | Source | Used for | Date |
| --- | --- | --- | --- |
| 1 | Boss App shots (2026-09-09 write-up) | Sea **¥158+** / Air **¥375+** @ 2.547 kg | shot **2026-09-09** · cited **2026-09-15** |
| 2 | https://calculator.cainiao.us/static/js/calculator_en.js | Non-tax formulas; /6000; 0.5 ceil; ¥200 large | fetched **2026-09-15** (same as 2026-09-10) |
| 3 | https://www.cainiao.us/p/air-shipping-tax-inclusive-line | **STALE** sea/air tax-incl first/add ¥ | page 2025-07-23 · access **2026-09-15** |
| 4 | https://www.cainiaobuy.com/p/air-shipping-tax-inclusive-line | EN twin of #3 | 2025-07-23 · access **2026-09-15** |
| 5 | https://www.cainiao.us/p/us-air-shipping-with-tax-included-is-here | **STALE** air Eco ¥47 / Fast ¥57 /0.5kg + air ETA | page 2025-08-23 · access **2026-09-15** |
| 6 | https://www.cainiao.us/p/price-update-us-au-uk-zh | US fuel air ¥5/0.5kg · sea ¥2/kg | page 2026-03-31 · access **2026-09-15** |
| 7 | https://www.cainiao.us/p/price-update-us-au-uk | EN twin of #6 | 2026-03-31 · access **2026-09-15** |
| 8 | https://www.cainiao.us/p/cainiao-coupon-usave | Promo floors ¥30/¥9 per 500g | updated 2026-03-31 / title Aug 2026 · access **2026-09-15** |
| 9 | https://www.cainiao.us/p/cainiao101 | Method names; 5.751 kg ¥171/426/516; sea 32–43 bd | thru 2026-03-31 · access **2026-09-15** |
| 10 | https://www.cainiao.us/p/cainiao-expected-delivery-time | Sea door-to-door samples ~25d / ~37d | page 2024-08-17 · access **2026-09-15** |
| 11 | https://www.cainiao.us/ | Index still lists the Apr 1 fuel notice (now clickable as #6) | access **2026-09-15** |
| 12 | https://open.er-api.com/v6/latest/USD | Optional USD context 6.725199 CNY | **2026-09-15** 00:02 UTC |
| 13 | Attached `cainiao-weight-scale-20260910.md` + `cainiao-us-ship-rates-20260909.md` | Prior LIVE App write-up + stale-card math | 2026-09-09 / 2026-09-10 |

---

## Group TLDR

**Cainiao 9/15:** stop `¥158÷N`. Billable = max(act, LWH/6000), 0.5kg steps. Live App **2026-09-09** 2.547kg → sea **¥158+** / air **¥375+** ≈ **¥62/kg** sea · **¥147/kg** air (**illustrative**). **STALE** 2025 cards (sea first ¥52.35+¥15.4/0.5; air ¥47/¥57) **understate** that App sample. **NEW** public fuel card (fetched 2026-09-15, page 2026-03-31): US air **¥5/0.5kg** · sea **¥2/kg** — do not stack on the App totals. Soft clothes: **prefer sea**, scale by **billable kg**. P-letter 保温杯 is a box, not a 100g accessory.

No 旺旺 · no cart · no buy · no invented ¥.
