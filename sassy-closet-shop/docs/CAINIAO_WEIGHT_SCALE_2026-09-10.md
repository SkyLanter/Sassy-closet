# Sassy Closet — Cainiao China→US weight ladder (2026-09-10)

> **SUPERSEDED for Cap / Money watch (Boss override 2026-09-10).** This 3.0 kg equal-share lock (**~$2.52/mã**) is **UNDERSTATE**. Use [`docs/CAINIAO_INBOUND_CONSERVATIVE_2026-09-10.md`](./CAINIAO_INBOUND_CONSERVATIVE_2026-09-10.md) + [`docs/MARGIN_50PCT_CONSERVATIVE_2026-09-10.md`](./MARGIN_50PCT_CONSERVATIVE_2026-09-10.md). Keep this file as the scout method history.

**Audience:** Boss. Mini Boss surfaces this file only.  
**Scope:** docs on Origin `main`. **No** live catalog Save, **no** product JSON change, **no** Square, **no** Facebook Post/Send, **no** passwords, **no** buy / cart / checkout / 旺旺.  
**Sell-test:** https://sassy-closet-shop.vercel.app  
**Companion:** [`docs/MARGIN_20PCT_WEIGHT_SCALE_2026-09-10.md`](./MARGIN_20PCT_WEIGHT_SCALE_2026-09-10.md) + [`.csv`](./MARGIN_20PCT_WEIGHT_SCALE_2026-09-10.csv).

**SoT:** Buy Research scout `sassy-closet/scout/cainiao-weight-scale-20260910.md` (kept on the Buy Research box). This Origin memo **mirrors that locked method**. Prefer scout / App-linear over stale public cards.

This memo **stops ¥158÷11**. Shipping is a function of **billable kg**. A 3.0 kg soft 11-mã haul is **¥186.1 sea**, not ¥158, so equal share is **¥16.92/mã**, not ¥14.36.

---

## Locked inbound method

1. **Billable kg** = `max(actual kg, L×W×H cm / 6000)`, then **round up 0.5 kg**.  
2. **Live App anchor** (2026-09-09, first-party checkout): **2.547 kg** billable → sea tax-incl **¥158+** · air tax-incl **¥375+**.  
   Cite: Boss App; [`docs/china-us-best-ship-rate-20260909.md`](./china-us-best-ship-rate-20260909.md) @ `5886c4eb07f9d414c4b08af0be6605a5a5cd9ca3`.  
3. **App-linear (illustrative — default for research / margin until a second App kg):**  
   `¥62.03/kg sea` = `158 / 2.547`  
   `¥147.23/kg air` = `375 / 2.547`  
   `total = billable_kg × ¥/kg` (full precision `158/2.547` and `375/2.547`, then display).  
   **Label: illustrative.** One live point; not a published unit card.  
4. **Soft 11-mã haul** ≈ **3.0 kg** billable → sea ≈ **¥186.1** → equal share ≈ **¥16.92/mã**.  
5. **Default MARGIN column = sea.** Air is the speed column.  
6. Customer US flat ship = **TBD**. Not in these totals. Not in sell.

**Do not** use 2025 marketing cards (¥47 / ¥57 / 0.5 kg, sea first ¥52.35) as checkout or as the margin inbound. They stay below, marked **STALE vs App**.

---

## How ¥ grows as piece count / kg grows

**Total inbound ¥ rises with billable kg.** App-linear has **no first-weight bump** (unlike the 2025 sea card). If kg grows with N, per-mã share stays in a band; the **box** still gets more expensive.

| Mixed soft haul | Model billable | Sea 含税 (App-linear, illustrative) | Air 含税 (App-linear, illustrative) | Sea per-mã (total/N) |
| --- | ---: | ---: | ---: | ---: |
| N=1 (one A-class garment) | **0.5 kg** | **¥31.02** ($4.61) | **¥73.62** ($10.95) | **$4.61** |
| N=5 (A+S+K+P+H) | **2.0 kg** | **¥124.07** ($18.45) | **¥294.46** ($43.78) | **$3.69** |
| **N=11 soft (locked)** | **3.0 kg** | **¥186.10** ($27.67) | **¥441.70** ($65.67) | **¥16.92 / $2.52** |
| N=20 (≈2× letter mix) | **5.5 kg** | **¥341.19** ($50.73) | **¥809.78** ($120.40) | **$2.54** |

Read the **total** column:

- 1 piece → **¥31** sea (0.5 kg step × ¥62.03/kg).  
- 11 soft pieces → **¥186** sea.  
- 20 pieces → **¥341** sea.  
- **¥158 is the App quote at 2.547 kg**, not a constant, and **not** the 3.0 kg clothes box.  
- **¥158÷11 = ¥14.36 is retired.** The 3.0 kg clothes share is **¥16.92**.

A 20-piece box is **more ¥** than an 11-piece box. A 1-piece order is **not** ¥14.

**Default for future sheets:** look up billable kg → `kg × 158/2.547` sea (illustrative) → share = total/N. Replace the ¥/kg when Boss pastes a **second App kg**. **Never freeze ¥158.**

---

## Hard stops

- Every research ¥ has a URL or the Boss App quote and an access date.  
- **App** = live checkout authority. **App-linear** = illustrative scale from that one point. **Marketing card** = 2025 cainiao.us posts, **STALE vs App**. **Calculator JS** = non-tax freight, JS `Last-Modified: 2024-10-13`.  
- Customer US flat ship is **pending Boss**.  
- Soft-clothes grams are a **model**, not warehouse 过机重量. No invented mã or stock.  
- Do not buy, cart, or checkout. Do not Save Square. Do not write `data/products.json`.

---

## FX

Source: [open.er-api.com USD→CNY](https://open.er-api.com/v6/latest/USD)  
`1 USD = 6.725515 CNY` · timestamp **Thu, 10 Sep 2026 00:02:31 +0000**.

```
usd = cny / 6.725515
```

¥158 → **$23.49**. ¥375 → **$55.76**. ¥186.10 → **$27.67**. ¥16.92 → **$2.52**.

---

## Billing rules

Chargeable kg = **max(actual kg, volumetric kg)**.  
Volumetric kg = **(L × W × H cm) / 6000**.  
Then **round up to the next 0.5 kg**.

| Rule | Source | Accessed | Mark |
| --- | --- | --- | --- |
| `chargeable = max(actual, L×W×H/6000)` | [calculator.cainiao.us](https://calculator.cainiao.us/) `static/js/calculator.js` | 2026-09-10 | Calculator (guide site). No ZIP. |
| Round up 0.5 kg | Same JS: `Math.ceil(weight * 2) / 2` | 2026-09-10 | Calculator. |
| 0.5 kg increments | [cainiao.us Cainiao 101](https://www.cainiao.us/p/cainiao101) (2024-09-25 / stamp 2026-03-31) | 2026-09-10 | Guide. |
| Live App printed **2.547 kg** | Boss App 2026-09-09 | 2026-09-09 | **App.** |
| Reject / 大件 | JS: reject longest ≥ 240 cm / girth ≥ 327 / kg ≥ 65; 大件 +¥200 if kg > 21.5 or longest > 120 or girth > 265 | 2026-09-10 | Calculator. Closet hauls stay 小件. |

No ZIP on the public calculator. Bay Area uses the US country card. AK / HI commonly excluded ([Extrabux](https://www.extrabux.com/chs/guide/8720714), 2026-09-10).

---

## Billable-kg ladder

### A. App-linear 含税 (illustrative) — use for landed / sell floors

Anchor: App **¥158 sea / ¥375 air @ 2.547 kg** (2026-09-09).

```
sea_cny = billable_kg × (158 / 2.547)    # ≈ ¥62.03 / kg
air_cny = billable_kg × (375 / 2.547)    # ≈ ¥147.23 / kg
```

At **2.547 kg** this reproduces the App totals exactly. At other kg it is **illustrative** until a second App quote.

| Billable kg | **Sea App-linear ¥** | Sea $ | **Air App-linear ¥** | Air $ |
| ---: | ---: | ---: | ---: | ---: |
| 0.5 | **31.02** | 4.61 | **73.62** | 10.95 |
| 1.0 | **62.03** | 9.22 | **147.23** | 21.89 |
| 2.0 | **124.07** | 18.45 | **294.46** | 43.78 |
| 2.5 | **155.08** | 23.06 | **368.08** | 54.73 |
| **2.547 (App)** | **158.00** | 23.49 | **375.00** | 55.76 |
| **3.0 (11-mã soft)** | **186.10** | 27.67 | **441.70** | 65.67 |
| 5.0 | **310.17** | 46.12 | **736.16** | 109.46 |
| 5.5 | **341.19** | 50.73 | **809.78** | 120.40 |
| 8.0 | **496.27** | 73.79 | **1177.86** | 175.13 |

### B. 2025 marketing cards — STALE vs App (do not sell from this)

| Lane | Unit card | Page | Dated | Accessed |
| --- | --- | --- | --- | --- |
| 海运含税 0–21.5 kg | first ¥52.35 / 0.5 kg + ¥15.4 / 0.5 kg add’l | [cainiao.us tax-incl line](https://www.cainiao.us/p/air-shipping-tax-inclusive-line) | 2025-07-23 | 2026-09-10 |
| 普货经济空运含税 | ¥47 / 0.5 kg | same + [US air launch](https://www.cainiao.us/p/us-air-shipping-with-tax-included-is-here) | 2025-08-23 | 2026-09-10 |
| 普货标准空运含税 | ¥57 / 0.5 kg | same | 2025-08-23 | 2026-09-10 |

Derived 3.0 kg: card sea **¥129.35** · Eco **¥282** · Fast **¥342**. App-linear at 3.0 kg is **¥186.1 / ¥441.7**. Cards **under-shoot**. Not used for margin.

### C. Calculator / Cainiao 101 — NON-TAX (do not sell from this)

[calculator.cainiao.us/static/js/calculator.js](https://calculator.cainiao.us/static/js/calculator.js) · `Last-Modified: 2024-10-13` · accessed 2026-09-10. Matches [Cainiao 101](https://www.cainiao.us/p/cainiao101) 5.751 kg sample (¥171 / ¥426 / ¥516 at the 6.0 kg step). Non-tax US lines also precollect **65% of declare** ([tariff notice](https://www.cainiao.us/p/us-tariff-policy-impact-on-cainiao-logistics-2025), 2025-05-20). **Not 含税.**

| Billable kg | Calc sea ¥ | Calc air eco ¥ | Calc air std ¥ |
| ---: | ---: | ---: | ---: |
| 0.5 | 66.00 | 71.00 | 86.00 |
| 3.0 | 108.00 | 213.00 | 258.00 |
| 6.0 | 171.00 | 426.00 | 516.00 |

`USAVE` still advertised. Unknown whether ¥158 / ¥375 already includes it. **Do not bake 10% into the ladder.**

---

## Soft-clothes model (flat-pack, not shoe boxes)

The 2026-09-09 App sample was **actual ~1.09 kg → billable 2.547 kg** (shoe box vol). A closet 合单 that 拆盒 / 真空 is **actual-weight**.

**Scout lock:** the 11-mã soft haul is treated as **3.0 kg billable** for inbound. That is the number the margin sheet uses.

### Proposed actual grams by kind (model, not 过机)

| Kind | What | Model g | Folded pack cm³ | Vol kg |
| --- | --- | ---: | ---: | ---: |
| A / Q / V | clothes — knit / light dress | **360** | 1,500 | 0.250 |
| S | dress / set | **450** | 2,080 | 0.347 |
| K | zip jacket (heavier) | **650** | 3,430 | 0.572 |
| P / J | light accessory | **80** | 500 | 0.083 |
| H | hair | **40** | 180 | 0.030 |

Gram tables: [FINDS](https://repfindsarchive.com/blog/shipping-haul-weight-calculator) (2026-03), [Indetexx](https://www.indetexx.com/how-much-is-a-kg-of-clothes-garments-weight-guide/) (accessed 2026-09-10), [Shopify](https://www.shopify.com/blog/how-much-does-shirt-weigh) (2026-04-23).

Carton: +80 g + 15 g×N. Void ×1.15 on packed cm³.

**Catalog note (not a new mã):** P02 / P03 / P05 are drinkware. If 拆盒 ~320 g each, the 11-mã actual can near **3.6 kg → 4.0 kg step** (App-linear sea ≈ **¥248**). Scout still locks research at **3.0 kg** until warehouse 过机. 4.0 kg is a sensitivity, not the default.

---

## Worked hauls

`actual = (Σ item g + 80 + 15N) / 1000`  
`vol = (Σ packed cm³ × 1.15) / 6000`  
`bill = ceil_half(max(actual, vol))`  
¥ = **App-linear illustrative**.

### N=1 — one A (360 g + 95 g pack)

Actual 0.455 · vol 0.288 · **bill 0.5 kg** · sea **¥31.02** · air **¥73.62**.

### N=5 — A+S+K+P+H (1,580 g + 155 g)

Actual 1.735 · vol 1.474 · **bill 2.0 kg** · sea **¥124.07** ($18.45) · share **$3.69** · air **¥294.46**.

### N=11 — letter mix (scout lock)

3A+S+K+5P+H = 2,620 g + 245 g pack → actual **2.865 kg** · vol 2.432 · **bill 3.0 kg**.  
Sea **¥186.10 ($27.67)** · equal share **¥16.92 / $2.52**.  
Air **¥441.70 ($65.67)** · equal share **¥40.15 / $5.97**.

### N=20 — 6A+2S+2K+8P+2H (5,080 g + 380 g)

Actual 5.460 · vol 4.673 · **bill 5.5 kg** · sea **¥341.19 ($50.73)** · share **$2.54**.

---

## Per-mã share on the locked 11-mã 3.0 kg haul

**Primary:** `share = ¥186.10 / 11 = ¥16.92` ($2.52). Same dollars on every mã.

**Optional weight-weighted** (letter grams / 2,620 g, same ¥186.10 total):

| mã | Model g | Sea wt-share $ | vs equal $2.52 |
| --- | ---: | ---: | ---: |
| K01 | 650 | 6.86 | +4.34 |
| S01 | 450 | 4.75 | +2.23 |
| A01 / A02 / A03 | 360 | 3.80 | +1.28 |
| P** | 80 | 0.84 | −1.68 |
| H01 | 40 | 0.42 | −2.10 |

---

## Why ¥158÷11 is retired

| | Retired | This memo (scout) |
| --- | --- | --- |
| Total sea | Always ¥158 (one shoe-box App sample) | **kg × ¥62.03** (illustrative) |
| 11-mã clothes box | ¥158 / 11 = ¥14.36 | **3.0 kg → ¥186.1 / 11 = ¥16.92** |
| 1-piece | under-charged | 0.5 kg × ¥62.03 |
| 20-piece | under-charged | 5.5 kg × ¥62.03 |

**More clothes = more ship cost** = the **parcel bill**, not “each extra tee adds ¥14.”

---

## Recommended default (future sheets)

1. **Lane:** Cainiao App **海运含税**. Air only if the customer cannot wait ~1 month.  
2. **kg:** warehouse 计费重 after 拆盒 / 真空. Until then, **3.0 kg** for the 11-mã soft haul (scout).  
3. **¥:** App-linear illustrative (`158/2.547` sea, `375/2.547` air). Replace when a second App kg lands.  
4. **Share:** total/N. Weight-weighted is a staff split only.  
5. **Do not** use 2025 ¥47/¥57 cards. **Do not** freeze ¥158 or ¥14.36.  
6. **Do not** invent customer US flat ship into sell.

---

## Open questions (Boss)

1. **App quote at a second kg** (1 kg and 5 kg on the same 含税 SKUs) — retires “illustrative.”  
2. Did 2.547 kg **bill as 2.547 or ceil to 3.0**? This memo uses **printed 2.547** as the ¥/kg divisor (scout).  
3. **Warehouse 过机 g** — especially K01 and P02/P03/P05. Drinkware can tip 3.0 → 4.0 kg.  
4. **`USAVE` already in ¥158 / ¥375?**  
5. **Customer US flat ship $** — still pending.  
6. **Duty true-up** on 含税 — product claim is one payment; CBP is not a guarantee.

---

## What this is not

- Not a catalog price change.  
- Not a customer-facing ship rate.  
- Not a Square / Facebook / Taobao buy.  
- Not a live App screenshot at 0.5 / 1 / 5 / 8 kg (those are the ask).

---

## DONE

- File: `docs/CAINIAO_WEIGHT_SCALE_2026-09-10.md` on Origin `main`.  
- Method: **App-linear illustrative** (scout SoT). Ladder 0.5 / 1 / 2 / 3 / 5 / 8 kg. Stale cards demoted.  
- Soft 11-mã = **3.0 kg · ¥186.1 sea · ¥16.92/mã** (not ¥14.36).  
- Statement: **total ¥ grows with kg.** ¥158 is the 2.547 kg App point, not a constant.  
- Default inbound: **海运含税, App-linear, 3.0 kg for the 11.**  
- Open Q: **need Boss App quote at a second kg.**  
- FX 6.725515 (2026-09-10 00:02:31 +0000). Product JSON **not** edited.  
- Sheet commit SHA: `5fcd582f4d9e3d6f79290865142ec557733d9ab4`. Origin `main` SHA after merge.
