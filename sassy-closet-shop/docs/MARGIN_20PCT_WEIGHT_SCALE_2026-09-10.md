# Sassy Closet — 20% margin sell floors, weight-scaled inbound (2026-09-10)

> **SUPERSEDED for Cap / Money watch (Boss override 2026-09-10).** 20% GM + 3.0 kg equal **$2.52** inbound is **too cheap**. Use [`docs/MARGIN_50PCT_CONSERVATIVE_2026-09-10.md`](./MARGIN_50PCT_CONSERVATIVE_2026-09-10.md) (`sell = landed / 0.50`, expensive inbound).

**Audience:** Boss. Mini Boss surfaces this sheet only.  
**Scope:** docs on Origin `main`. **No** live catalog Save, **no** product JSON change, **no** Square, **no** Facebook Post/Send, **no** passwords, **no** buy/cart/checkout.  
**Sell-test:** https://sassy-closet-shop.vercel.app  
**Mãs:** the same 11. No invented mã or stock.

Companion CSV: [`docs/MARGIN_20PCT_WEIGHT_SCALE_2026-09-10.csv`](./MARGIN_20PCT_WEIGHT_SCALE_2026-09-10.csv).  
Inbound: [`docs/CAINIAO_WEIGHT_SCALE_2026-09-10.md`](./CAINIAO_WEIGHT_SCALE_2026-09-10.md) (mirrors Buy Research scout SoT).

**This sheet does not use ¥158 ÷ 11.** Inbound is the scout-locked **3.0 kg** soft 11-mã haul on **App-linear illustrative** sea (`158/2.547` ¥/kg): **¥186.10 ($27.67)** total → **¥16.92 / $2.52 per mã**. Air: **¥441.70 ($65.67)** → **$5.97 per mã**.

Default inbound for “what should we sell at” = **sea**. Air is the speed alternative. Item-only is the Taobao floor. App-linear is **illustrative** (one App point).

---

## Hard stops (this file)

- Margin = **product sell vs landed product cost only**. Customer US flat ship is **pending Boss** — not invented, not baked into sell.  
- Do **not** treat `sell_20pct_*` as an official catalog price. Do not Save Square. Do not write `data/products.json`.  
- P02 / P05 stay **Inbox for price** on the live shop. Snapshot P05 `$23` is **Excel/staff, not live**. Shop law: P05 is never official `$23`.  
- Live A03 is **Hold / Inbox**. Snapshot `$19` is compare-only.  
- **Live list ¥ overrides catalog cost** on K01 / H01 / A02 / P05 (Boss default if silent = use live list as payable). Other mãs keep prior `cost_cny` / FX.

---

## FX

Source: [open.er-api.com USD→CNY](https://open.er-api.com/v6/latest/USD)  
`1 USD = 6.725515 CNY` · timestamp **Thu, 10 Sep 2026 00:02:31 +0000**.

```
usd = cny / 6.725515
```

### Cost USD used

1. **Live list override** (this pass): K01 ¥125 · H01 ¥17.90 · A02 ¥85.90 · P05 ¥109.90.  
   P05 short-link meta ¥98.90 is **not** used.  
2. Else if `cost_cny` present → `cost_usd_used = cny / 6.725515` (prefer CNY).  
3. Else if only `cost_usd` → use it (none left after this pass).  
4. If both empty → `NEED_LIVE_TB`. **None of the 11.**

| mã | Prior cost | **This pass** | Flag |
| --- | --- | --- | --- |
| K01 | USD_ONLY $15.32 → back-calc ¥103.03 | **¥125** | LIVE_LIST |
| H01 | USD_ONLY $2.00 → back-calc ¥13.45 | **¥17.90** | LIVE_LIST |
| A02 | ¥71 | **¥85.90** | LIVE_LIST |
| P05 | ¥75 | **¥109.90** | LIVE_LIST (meta ¥98.90 unused) |
| A01 P01 S01 P02 P03 P04 A03 | prior catalog ¥ | unchanged | catalog / FX |

---

## Inbound (weight-scaled — not ¥158÷11)

Scout method. Full sources in the weight-scale memo.

| 11-mã haul | Billable | Sea 含税 total | Air 含税 total | Equal share / 11 |
| --- | ---: | ---: | ---: | ---: |
| **Soft 11 (default, scout)** | **3.0 kg** | **¥186.10 ($27.67)** | **¥441.70 ($65.67)** | sea **¥16.92 / $2.52** · air **$5.97** |
| Retired equal-split | (ignored kg) | ¥158.00 ($23.49) | ¥375.00 ($55.76) | sea ¥14.36 / $2.14 |

Landed columns add the **full-precision** equal share (`(158/2.547)×3/11/FX`) to the **full-precision** item USD, then round HALF_UP to 2 decimals.

**How ¥ grows:** 1-piece box ¥31 sea; 11-mã box **¥186** sea; 20-piece box ¥341 sea. ¥158 is the App print at **2.547 kg**, not this clothes haul.

### Sensitivity — if the 合单 were 5 or 20 pieces

Same item USD; inbound share = that haul’s **total / N** (App-linear).

| Haul | Billable | Sea total | Equal share | vs 11-mã $2.52 |
| --- | ---: | ---: | ---: | ---: |
| N=5 mixed | 2.0 kg | ¥124.07 ($18.45) | **$3.69** | +$1.17 |
| N=11 soft | 3.0 kg | ¥186.10 ($27.67) | **$2.52** | default |
| N=20 mixed | 5.5 kg | ¥341.19 ($50.73) | **$2.54** | +$0.02 (linear ≈ same per mã) |

App-linear has no first-weight bump, so N=20 per-mã ≈ N=11. The **totals** still grow (¥186 → ¥341).

**Optional weight-weighted** (letter grams / 2,620 g of the same ¥186.10): K01 **$6.86** · H01 **$0.42** · P** **$0.84**.

---

## Formulas (locked — do not mix)

**20% gross margin on sell** (primary):

```
(sell − landed) / sell = 0.20
sell_20pct_margin = landed / 0.80
```

That is a **25% markup on landed cost**. It is **not** “times 1.20”.

**20% markup** (alternate column only — sea):

```
sell_20pct_markup_sea = landed_sea * 1.20
```

| Landed scenario | Meaning |
| --- | --- |
| Item-only | Taobao / live-list cost USD used |
| +Sea share (default) | item + $2.52 — **3.0 kg App-linear sea** |
| +Air share | item + $5.97 — **3.0 kg App-linear air** |
| Sea N=5 / N=20 | item + that haul’s equal share |
| Sea old ¥158/11 | compare-only (retired) |
| Sea weight-weighted | item + $27.67 × (g / 2620) |

```
delta_vs_current_sea = current_sell_usd − sell_20pct_margin_sea
```

- **Positive** = current sell **above** the 20% GM sea target.  
- **Negative** = current sell **below** that target.  
- Empty = no snapshot sell (do not invent).

Rounding: Python `Decimal` **ROUND_HALF_UP** to 2 decimals. Sells from the **rounded** landed cell.

US customer ship, meetup, Zelle fees, and extra duty-on-top-of-tax-incl are **out of this margin**.

---

## Assumptions

| # | Locked |
| --- | --- |
| 1 | 11 mãs only. No new SKUs. |
| 2 | Default inbound = **sea, App-linear illustrative, 3.0 kg, equal share ¥16.92**. |
| 3 | Grams model: A 360 / S 450 / K 650 / P 80 / H 40. Not 过机. |
| 4 | K01 H01 A02 P05 use **live list ¥** as payable. |
| 5 | `current_sell_usd` = snapshot (P05 `23`, A03 `19`). Live Blob may be Inbox. |
| 6 | Live catalog 2026-09-10: sha `986334693c8fc6c3585ecbe3de1af0be47c1a723a515d8cf0e96ea5a776199e2`. P02 / P05 / A03 Hold. |
| 7 | No US customer flat ship in sell. |
| 8 | Docs only. Official sell prices stay as they are on the shop. |

---

## All 11 mãs (USD, 2 decimals)

**Bold** = default: **20% GM on 3.0 kg sea-landed**.  
`sell_20pct_markup_sea` is the **1.20×** alternate.

| mã | cost ¥ | USD used | landed item | landed sea | landed air | sell 20% GM item | **sell 20% GM sea** | sell 20% GM air | sell 20% markup sea | current | Δ vs sea GM |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| A01 | 90.65 | 13.48 | 13.48 | 15.99 | 19.45 | 16.85 | **19.99** | 24.31 | 19.19 | 25.00 | 5.01 |
| P01 | 7.18 | 1.07 | 1.07 | 3.58 | 7.04 | 1.34 | **4.48** | 8.80 | 4.30 | 5.00 | 0.52 |
| S01 | 114.07 | 16.96 | 16.96 | 19.48 | 22.93 | 21.20 | **24.35** | 28.66 | 23.38 | 28.00 | 3.65 |
| P02 | 63.00 | 9.37 | 9.37 | 11.88 | 15.34 | 11.71 | **14.85** | 19.18 | 14.26 | — | — |
| P05 | **109.90** | 16.34 | 16.34 | 18.86 | 22.31 | 20.43 | **23.58** | 27.89 | 22.63 | 23.00 | **−0.58** |
| P03 | 31.00 | 4.61 | 4.61 | 7.12 | 10.58 | 5.76 | **8.90** | 13.23 | 8.54 | 18.00 | 9.10 |
| P04 | 15.90 | 2.36 | 2.36 | 4.88 | 8.33 | 2.95 | **6.10** | 10.41 | 5.86 | 13.00 | 6.90 |
| K01 | **125.00** | 18.59 | 18.59 | 21.10 | 24.56 | 23.24 | **26.38** | 30.70 | 25.32 | 37.00 | 10.62 |
| H01 | **17.90** | 2.66 | 2.66 | 5.18 | 8.63 | 3.33 | **6.48** | 10.79 | 6.22 | 8.00 | 1.52 |
| A02 | **85.90** | 12.77 | 12.77 | 15.29 | 18.74 | 15.96 | **19.11** | 23.43 | 18.35 | 22.00 | 2.89 |
| A03 | 59.00 | 8.77 | 8.77 | 11.29 | 14.74 | 10.96 | **14.11** | 18.43 | 13.55 | 19.00 | 4.89 |

P05 snapshot `$23` is **under** the new sea 20% GM floor (**$23.58**). Live P05 is Inbox — do not Save `$23`. Flag only.

### Sensitivity (sea 20% GM only)

| mã | **11 @ 3.0 kg** | N=5 (2.0 kg) | N=20 (5.5 kg) | old ¥158/11 | wt-share 3.0 kg |
| --- | ---: | ---: | ---: | ---: | ---: |
| A01 | **19.99** | 21.46 | 20.03 | 19.51 | 21.60 |
| P01 | **4.48** | 5.95 | 4.50 | 4.00 | 2.39 |
| S01 | **24.35** | 25.81 | 24.38 | 23.88 | 27.14 |
| P02 | **14.85** | 16.33 | 14.88 | 14.38 | 12.76 |
| P05 | **23.58** | 25.04 | 23.60 | 23.10 | 21.49 |
| P03 | **8.90** | 10.38 | 8.94 | 8.44 | 6.81 |
| P04 | **6.10** | 7.56 | 6.13 | 5.63 | 4.01 |
| K01 | **26.38** | 27.85 | 26.40 | 25.90 | 31.81 |
| H01 | **6.48** | 7.94 | 6.50 | 6.00 | 3.85 |
| A02 | **19.11** | 20.58 | 19.14 | 18.64 | 20.71 |
| A03 | **14.11** | 15.58 | 14.14 | 13.64 | 15.71 |

### Staff Taobao links (not for the shopper)

| mã | source_link |
| --- | --- |
| A01 | https://e.tb.cn/h.8KCQeaHH3dz1iSl?tk=WeuOTTBXHOu |
| P01 | https://e.tb.cn/h.8LUkbrVGhE4Yurr?tk=RYgXTTzkt8b |
| S01 | https://e.tb.cn/h.8KBBS0G8a3NQqtg?tk=YcEnTTALzCr |
| P02 | https://e.tb.cn/h.8KU3zzXBR4OB9me?tk=kcDJT6G7z4p |
| P05 | https://e.tb.cn/h.8pbIxrTW0mbK1Wk?tk=oDgIT6GKXrw |
| P03 | https://e.tb.cn/h.8KKzBinMRDOZhNO?tk=nf9vThVDZ31 |
| P04 | https://e.tb.cn/h.8LYfu0T52xNPoOD?tk=sfeoT6uLsAa |
| K01 | https://e.tb.cn/h.8LLjHT2R8bUOvIz?tk=cgigThRIuvf |
| H01 | https://e.tb.cn/h.8KE7trcDe92yo2O?tk=fkqzThRw8Yn |
| A02 | https://e.tb.cn/h.8JSyU68ajHWyf52?tk=rSynThj54Ks |
| A03 | https://e.tb.cn/h.8p9N3n8BxBY4aEN?tk=OurQTSg7ai8 |

### FX / live flags

| mã | Notes |
| --- | --- |
| A01 | FX_CONFLICT catalog_cost_usd 13.51 vs used 13.48 (prefer CNY/6.725515); live sell 25.00 available; OVER_SEA +5.01 (current GM vs sea landed 36.0%) |
| P01 | FX matches catalog cost_usd at 2dp; live sell 5.00 available; OVER_SEA +0.52 (current GM vs sea landed 28.4%) |
| S01 | FX_CONFLICT catalog_cost_usd 17.00 vs used 16.96 (prefer CNY/6.725515); live sell 28.00 available; OVER_SEA +3.65 (current GM vs sea landed 30.4%) |
| P02 | FX_CONFLICT catalog_cost_usd 9.39 vs used 9.37; NO_CURRENT_SELL; live Hold/Inbox; do not invent $ |
| P05 | **LIVE_LIST ¥109.90** (was ¥75; short-link meta ¥98.90 unused); SNAPSHOT_SELL 23.00 not live; **UNDER_SEA −0.58** (current GM vs sea landed 18.0%); shop law: P05 never official $23 |
| P03 | FX_CONFLICT catalog_cost_usd 4.62 vs used 4.61; live sell 18.00 available; OVER_SEA +9.10 (current GM vs sea landed 60.4%) |
| P04 | FX_CONFLICT catalog_cost_usd 2.37 vs used 2.36; live sell 13.00 available; OVER_SEA +6.90 (current GM vs sea landed 62.5%) |
| K01 | **LIVE_LIST ¥125** (was USD_ONLY ~¥103 / $15.32); used 18.59; live sell 37.00 available; OVER_SEA +10.62 (current GM vs sea landed 43.0%) |
| H01 | **LIVE_LIST ¥17.90** (was USD_ONLY ~¥13.45 / $2.00); used 2.66; live sell 8.00 available; OVER_SEA +1.52 (current GM vs sea landed 35.2%) |
| A02 | **LIVE_LIST ¥85.90** (was ¥71); used 12.77; live sell 22.00 available; OVER_SEA +2.89 (current GM vs sea landed 30.5%) |
| A03 | FX_CONFLICT catalog_cost_usd 8.79 vs used 8.77; SNAPSHOT_SELL 19.00 not live; live Hold; OVER_SEA +4.89 (current GM vs sea landed 40.6%) |

---

## Under / over vs current sell (sea 20% GM, 3.0 kg share)

**One snapshot row is under:** **P05** `$23` vs sea GM **$23.58** (Δ **−0.58**, GM 18.0% on sea-landed). Live P05 is Inbox. Do not Save.

All **live Available** priced mãs still clear 20% on 3.0 kg sea-landed product (customer ship excluded).

### Most over vs sea 20% GM (largest +Δ)

| Rank | mã | current | sea 20% GM | Δ | current GM vs sea landed | Live |
| ---: | --- | ---: | ---: | ---: | ---: | --- |
| 1 | K01 | 37.00 | 26.38 | +10.62 | 43.0% | available $37 |
| 2 | P03 | 18.00 | 8.90 | +9.10 | 60.4% | available $18 |
| 3 | P04 | 13.00 | 6.10 | +6.90 | 62.5% | available $13 |
| 4 | A01 | 25.00 | 19.99 | +5.01 | 36.0% | available $25 |
| 5 | A03 | 19.00 | 14.11 | +4.89 | 40.6% | hold Inbox |
| 6 | S01 | 28.00 | 24.35 | +3.65 | 30.4% | available $28 |
| 7 | A02 | 22.00 | 19.11 | +2.89 | 30.5% | available $22 |
| 8 | H01 | 8.00 | 6.48 | +1.52 | 35.2% | available $8 |
| 9 | P01 | 5.00 | 4.48 | +0.52 | 28.4% | available $5 |
| — | P05 | 23.00 | 23.58 | **−0.58** | **18.0%** | hold Inbox |

**Top over (live Available):** **K01** +$10.62 · **P03** +$9.10 · **P04** +$6.90.

### Under vs sea 20% GM

**P05** (snapshot only). **P02** has no current sell — sea 20% GM ask would be **$14.85** if Boss wants a printed USD later. Do not invent.

**Closest to the 20% floor among live Available:**

| mã | current | sea landed | current GM | sea 20% GM | Δ |
| --- | ---: | ---: | ---: | ---: | ---: |
| P01 | 5.00 | 3.58 | 28.4% | 4.48 | +0.52 |
| S01 | 28.00 | 19.48 | 30.4% | 24.35 | +3.65 |
| A02 | 22.00 | 15.29 | 30.5% | 19.11 | +2.89 |

A02 thinned after the live-list bump (¥71 → ¥85.90). P01 is still the thinnest live mã.

---

## Open questions (Boss)

1. **Customer flat ship $** — still pending. Not in sell.  
2. **App quote at a second kg** — retires “illustrative” on the ¥/kg.  
3. **P05** — snapshot $23 is under the new floor. Live is Inbox. Do not Save.  
4. **Warehouse grams** / drinkware 拆盒 — 3.0 vs 4.0 kg step.  
5. Confirm live list ¥ on K01 / H01 / A02 / P05 are the payable numbers (this sheet assumes yes).  
6. Duty true-up on 含税.

---

## What this is not

- Not a catalog price change.  
- Not a customer-facing ship rate.  
- Not a Square / Facebook action.  
- Not a buy on Taobao.

---

## DONE

- Files: `docs/MARGIN_20PCT_WEIGHT_SCALE_2026-09-10.md`, `docs/MARGIN_20PCT_WEIGHT_SCALE_2026-09-10.csv` on Origin `main`.  
- Inbound: **3.0 kg · ¥186.10 sea · ¥16.92/mã** (App-linear illustrative). Not ¥158÷11.  
- Live list overrides: K01 ¥125 · H01 ¥17.90 · A02 ¥85.90 · P05 ¥109.90.  
- FX 6.725515. 11/11 mãs. 0 × `NEED_LIVE_TB`.  
- **Top over:** K01 +$10.62, P03 +$9.10, P04 +$6.90. **Under:** P05 snapshot −$0.58 (Inbox). Thinnest live: **P01**.  
- Default inbound: **海运含税, App-linear, 3.0 kg** ([weight-scale memo](./CAINIAO_WEIGHT_SCALE_2026-09-10.md)).  
- Open Qs: flat ship, second App kg, P05 floor, warehouse grams.  
- Live catalog read-only. Product JSON **not** edited.  
- Sheet commit SHA: `5fcd582f4d9e3d6f79290865142ec557733d9ab4`. Origin `main` SHA after merge.
