# Sassy Closet — 50% GM sell floors, conservative inbound (2026-09-10)

**Audience:** Boss. Mini Boss surfaces this sheet only.  
**Scope:** docs on Origin `main`. **No** live catalog Save, **no** product JSON change, **no** Square, **no** Facebook Post/Send, **no** passwords, **no** buy/cart/checkout.  
**Sell-test:** https://sassy-closet-shop.vercel.app  
**Mãs:** the same 11. No invented mã or stock.

Companion CSV: [`docs/MARGIN_50PCT_CONSERVATIVE_2026-09-10.csv`](./MARGIN_50PCT_CONSERVATIVE_2026-09-10.csv).  
Inbound method: [`docs/CAINIAO_INBOUND_CONSERVATIVE_2026-09-10.md`](./CAINIAO_INBOUND_CONSERVATIVE_2026-09-10.md).  
Rounding engine: `scripts/margin_50pct_conservative_20260910.py` (Python `Decimal` **ROUND_HALF_UP**).

**Boss override (2026-09-10):** prior sea inbound **~$2.52/mã** (3.0 kg equal-share) is **too cheap**. This sheet uses the **expensive** default: **4.0 kg** App-linear sea, **weight-weighted**, **never below the 0.5 kg sea step**. Floor locked: **50% GM** ⇒ `sell = landed / 0.50`.

**This sheet does not use ¥158÷11 or $2.52.** Customer US flat ship = **TBD** — column present, **empty**, not in sell.

---

## Hard stops (this file)

- Margin = **product sell vs landed product cost only**. Customer US flat ship is **pending Boss** — not invented, not baked into sell.  
- Do **not** treat `sell_50pct_*` as an official catalog price. Do not Save Square. Do not write `data/products.json`.  
- P02 / P05 stay **Inbox for price** on the live shop. Snapshot P05 `$23` is **Excel/staff, not live**. Shop law: P05 is never official `$23`.  
- Live A03 is **Hold / Inbox**. Snapshot `$19` is compare-only.  
- **Live list ¥ overrides catalog cost** on K01 / H01 / A02 / P05 (Boss default if silent = use live list as payable). Other mãs keep prior `cost_cny` / FX.

---

## FX

Source: [open.er-api.com USD→CNY](https://open.er-api.com/v6/latest/USD)  
`1 USD = 6.725515 CNY` · timestamp **Thu, 10 Sep 2026 00:02:31 +0000** (re-fetched 2026-09-10; no fresher print).

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

## Inbound (conservative — more expensive than $2.52)

Full method + sources: [inbound memo](./CAINIAO_INBOUND_CONSERVATIVE_2026-09-10.md). App-linear is **illustrative** (one App point).

| 11-mã haul | Billable | Sea 含税 box | Air 含税 box | Per-mã sea used here |
| --- | ---: | ---: | ---: | --- |
| Prior SoT (UNDERSTATE) | 3.0 kg | ¥186.10 ($27.67) | ¥441.70 ($65.67) | equal **$2.52** |
| 4.0 kg equal (compare) | 4.0 kg | ¥248.14 ($36.89) | ¥588.93 ($87.57) | equal **$3.35** |
| **Default** | **4.0 kg** | ¥248.14 ($36.89) | ¥588.93 ($87.57) | **wt + 0.5 kg floor:** A **$5.07** · S **$6.34** · K **$9.15** · P/H **$4.61** |
| Sensitivity | 5.0 kg | ¥310.17 ($46.12) | ¥736.16 ($109.46) | A $6.34 · S $7.92 · K $11.44 · P/H $4.61 |

Default inbound for “what should we sell at” = **sea**. Air is the speed alternative. Item-only is the Taobao floor (no inbound).

Landed columns add the **full-precision** inbound USD to the **full-precision** item USD, then round HALF_UP to 2 decimals. Sells from the **rounded** landed cell.

The 0.5 kg sea floor lifts six P/H rows. Planning inbound **sums to $58.37**, not the $36.89 box. Clothes still pay their heavier 4 kg wt-share (not equal $3.35).

---

## Formulas (locked — do not mix)

**50% gross margin on sell** (only GM formula on this sheet):

```
(sell − landed) / sell = 0.50
sell_50pct = landed / 0.50
```

That is a **100% markup on landed cost**. It is **not** “times 1.50”. It is **not** the old 20% GM (`landed / 0.80`).

| Landed scenario | Meaning |
| --- | --- |
| Item-only | Taobao / live-list cost USD used |
| **+Sea (default)** | item + **4.0 kg wt-share, floored at $4.61** |
| +Air | item + **4.0 kg air wt-share, floored at $10.95** |
| +Sea 5 kg | item + 5.0 kg wt-share, same $4.61 floor |
| Old 3.0 kg equal | compare-only ($2.52) — not used for the floor |
| Customer US flat | **TBD** — CSV column empty; not in sell |

```
delta_vs_current_sea = current_sell_usd − sell_50pct_sea
```

- **Positive** = current sell **above** the 50% GM sea floor (**OVER**).  
- **Negative** = current sell **below** that floor (**UNDER**).  
- Empty = no snapshot sell (do not invent).

US customer ship, meetup, Zelle fees, and extra duty-on-top-of-tax-incl are **out of this margin**.

---

## Assumptions

| # | Locked |
| --- | --- |
| 1 | 11 mãs only. No new SKUs. |
| 2 | Default inbound = **sea, App-linear illustrative, 4.0 kg, weight-weighted, 0.5 kg sea floor**. |
| 3 | Grams model: A 360 / S 450 / K 650 / P 80 / H 40. Not 过机. Drinkware extra is in the **4.0 kg box**, not the split. |
| 4 | K01 H01 A02 P05 use **live list ¥** as payable. |
| 5 | `current_sell_usd` = snapshot (P05 `23`, A03 `19`). Live Blob may be Inbox. |
| 6 | Live catalog 2026-09-10: sha `986334693c8fc6c3585ecbe3de1af0be47c1a723a515d8cf0e96ea5a776199e2`, `updatedAt` `2026-09-10T07:58:43.366Z`. P02 / P05 / A03 Hold. |
| 7 | No US customer flat ship in sell. |
| 8 | Docs only. Official sell prices stay as they are on the shop. |

---

## All 11 mãs (USD, 2 decimals)

**Bold** = default: **50% GM on conservative sea-landed**.

| mã | cost ¥ | USD used | inbound sea | inbound air | landed item | **landed sea** | landed air | sell 50% item | **sell 50% sea** | sell 50% air | current | Δ vs sea 50% |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| A01 | 90.65 | 13.48 | 5.07 | 12.03 | 13.48 | **18.55** | 25.51 | 26.96 | **37.10** | 51.02 | 25.00 | **−12.10** |
| P01 | 7.18 | 1.07 | 4.61 | 10.95 | 1.07 | **5.68** | 12.01 | 2.14 | **11.36** | 24.02 | 5.00 | **−6.36** |
| S01 | 114.07 | 16.96 | 6.34 | 15.04 | 16.96 | **23.30** | 32.00 | 33.92 | **46.60** | 64.00 | 28.00 | **−18.60** |
| P02 | 63.00 | 9.37 | 4.61 | 10.95 | 9.37 | **13.98** | 20.31 | 18.74 | **27.96** | 40.62 | — | — |
| P05 | **109.90** | 16.34 | 4.61 | 10.95 | 16.34 | **20.95** | 27.29 | 32.68 | **41.90** | 54.58 | 23.00 | **−18.90** |
| P03 | 31.00 | 4.61 | 4.61 | 10.95 | 4.61 | **9.22** | 15.56 | 9.22 | **18.44** | 31.12 | 18.00 | **−0.44** |
| P04 | 15.90 | 2.36 | 4.61 | 10.95 | 2.36 | **6.98** | 13.31 | 4.72 | **13.96** | 26.62 | 13.00 | **−0.96** |
| K01 | **125.00** | 18.59 | 9.15 | 21.72 | 18.59 | **27.74** | 40.31 | 37.18 | **55.48** | 80.62 | 37.00 | **−18.48** |
| H01 | **17.90** | 2.66 | 4.61 | 10.95 | 2.66 | **7.27** | 13.61 | 5.32 | **14.54** | 27.22 | 8.00 | **−6.54** |
| A02 | **85.90** | 12.77 | 5.07 | 12.03 | 12.77 | **17.84** | 24.80 | 25.54 | **35.68** | 49.60 | 22.00 | **−13.68** |
| A03 | 59.00 | 8.77 | 5.07 | 12.03 | 8.77 | **13.84** | 20.80 | 17.54 | **27.68** | 41.60 | 19.00 | **−8.68** |

**Every snapshot-priced mã is UNDER** the conservative sea 50% GM floor. P02 has no current sell — do not invent one.

P01 current **$5** is **below** conservative sea landed **$5.68** (current GM vs sea landed **−13.6%**). That row loses money on this inbound before any 50% target.

P05 snapshot `$23` vs sea 50% **$41.90**. Live P05 is Inbox — do not Save `$23`. Flag only.

### Sensitivity (sea 50% GM)

| mã | **4.0 kg default** | 5.0 kg | old 3.0 kg equal $2.52 inbound | 4.0 kg equal $3.35 inbound |
| --- | ---: | ---: | ---: | ---: |
| A01 | **37.10** | 39.64 | 31.98 | 33.66 |
| P01 | **11.36** | 11.36 | 7.16 | 8.84 |
| S01 | **46.60** | 49.76 | 38.96 | 40.62 |
| P02 | **27.96** | 27.96 | 23.76 | 25.44 |
| P05 | **41.90** | 41.90 | 37.72 | 39.38 |
| P03 | **18.44** | 18.44 | 14.24 | 15.92 |
| P04 | **13.96** | 13.96 | 9.76 | 11.44 |
| K01 | **55.48** | 60.06 | 42.20 | 43.88 |
| H01 | **14.54** | 14.54 | 10.36 | 12.04 |
| A02 | **35.68** | 38.22 | 30.58 | 32.26 |
| A03 | **27.68** | 30.22 | 22.58 | 24.26 |

Old-equal and 4 kg-equal sells above are `round(round(item + that_share, 2) / 0.50, 2)` for compare only. **Do not** plan from those columns. P/H 5 kg floors stay at $4.61 (0.5 kg step still binds), so those 50% sells match the 4 kg default.

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
| A01 | FX_CONFLICT catalog_cost_usd 13.51 vs used 13.48 (prefer CNY/6.725515); live sell 25.00 available; **UNDER_SEA −12.10** (current GM vs sea landed 25.8%) |
| P01 | FX matches catalog cost_usd at 2dp; live sell 5.00 available; **UNDER_SEA −6.36** (current GM vs sea landed **−13.6%** — sell below landed) |
| S01 | FX_CONFLICT catalog_cost_usd 17.00 vs used 16.96 (prefer CNY/6.725515); live sell 28.00 available; **UNDER_SEA −18.60** (current GM vs sea landed 16.8%) |
| P02 | FX_CONFLICT catalog_cost_usd 9.39 vs used 9.37; NO_CURRENT_SELL; live Hold/Inbox; do not invent $ |
| P05 | **LIVE_LIST ¥109.90** (was ¥75; short-link meta ¥98.90 unused); SNAPSHOT_SELL 23.00 not live; **UNDER_SEA −18.90** (current GM vs sea landed 8.9%); shop law: P05 never official $23 |
| P03 | FX_CONFLICT catalog_cost_usd 4.62 vs used 4.61; live sell 18.00 available; **UNDER_SEA −0.44** (current GM vs sea landed 48.8%) |
| P04 | FX_CONFLICT catalog_cost_usd 2.37 vs used 2.36; live sell 13.00 available; **UNDER_SEA −0.96** (current GM vs sea landed 46.3%) |
| K01 | **LIVE_LIST ¥125** (was USD_ONLY ~¥103 / $15.32); used 18.59; live sell 37.00 available; **UNDER_SEA −18.48** (current GM vs sea landed 25.0%) |
| H01 | **LIVE_LIST ¥17.90** (was USD_ONLY ~¥13.45 / $2.00); used 2.66; live sell 8.00 available; **UNDER_SEA −6.54** (current GM vs sea landed 9.1%) |
| A02 | **LIVE_LIST ¥85.90** (was ¥71); used 12.77; live sell 22.00 available; **UNDER_SEA −13.68** (current GM vs sea landed 18.9%) |
| A03 | FX_CONFLICT catalog_cost_usd 8.79 vs used 8.77; SNAPSHOT_SELL 19.00 not live; live Hold; **UNDER_SEA −8.68** (current GM vs sea landed 27.2%) |

---

## Under / over vs current sell (sea 50% GM, conservative inbound)

**All 10 snapshot-priced mãs are UNDER.** Zero OVER. P02 has no current sell.

### Most under vs sea 50% GM (largest −Δ)

| Rank | mã | current | sea 50% GM | Δ | current GM vs sea landed | Live |
| ---: | --- | ---: | ---: | ---: | ---: | --- |
| 1 | P05 | 23.00 | 41.90 | **−18.90** | 8.9% | hold Inbox |
| 2 | S01 | 28.00 | 46.60 | **−18.60** | 16.8% | available $28 |
| 3 | K01 | 37.00 | 55.48 | **−18.48** | 25.0% | available $37 |
| 4 | A02 | 22.00 | 35.68 | **−13.68** | 18.9% | available $22 |
| 5 | A01 | 25.00 | 37.10 | **−12.10** | 25.8% | available $25 |
| 6 | A03 | 19.00 | 27.68 | **−8.68** | 27.2% | hold Inbox |
| 7 | H01 | 8.00 | 14.54 | **−6.54** | 9.1% | available $8 |
| 8 | P01 | 5.00 | 11.36 | **−6.36** | **−13.6%** | available $5 |
| 9 | P04 | 13.00 | 13.96 | **−0.96** | 46.3% | available $13 |
| 10 | P03 | 18.00 | 18.44 | **−0.44** | 48.8% | available $18 |

**Top under among live Available:** **S01 −$18.60** · **K01 −$18.48** · **A02 −$13.68**.

**Closest to the 50% floor (still under):** **P03** −$0.44 (current GM 48.8%) · **P04** −$0.96 (46.3%).

**P02** sea 50% GM ask would be **$27.96** if Boss wants a printed USD later. Do not invent.

**Money-losing on conservative sea landed (sell &lt; landed):** **P01** $5 vs landed $5.68.

---

## Before / after vs the old 20% · $2.52 sheet

Same item USD. Only inbound + GM target changed.

| mã | old inbound | old 20% GM sea | **new inbound** | **new 50% GM sea** | current |
| --- | ---: | ---: | ---: | ---: | ---: |
| A01 | 2.52 | 19.99 | **5.07** | **37.10** | 25 |
| P01 | 2.52 | 4.48 | **4.61** | **11.36** | 5 |
| S01 | 2.52 | 24.35 | **6.34** | **46.60** | 28 |
| P02 | 2.52 | 14.85 | **4.61** | **27.96** | — |
| P05 | 2.52 | 23.58 | **4.61** | **41.90** | 23 |
| P03 | 2.52 | 8.90 | **4.61** | **18.44** | 18 |
| P04 | 2.52 | 6.10 | **4.61** | **13.96** | 13 |
| K01 | 2.52 | 26.38 | **9.15** | **55.48** | 37 |
| H01 | 2.52 | 6.48 | **4.61** | **14.54** | 8 |
| A02 | 2.52 | 19.11 | **5.07** | **35.68** | 22 |
| A03 | 2.52 | 14.11 | **5.07** | **27.68** | 19 |

The old 20% sheet had **one** snapshot under (P05 −$0.58) and every live Available **over**. This 50% + expensive inbound sheet flips that: **10/10 priced rows under**. That is the override working as asked — not a catalog change.

---

## Open questions (Boss)

1. **Need Boss App quote at 4–5 kg** on the same 含税 SKUs — retires “illustrative” on the ¥/kg.  
2. **Customer flat ship $** — still pending. Not in sell.  
3. **P05 / A03** — snapshot vs live Inbox. Sheet compares snapshot; live Blob is null. Do not Save.  
4. **Warehouse grams** / drinkware 拆盒 — keep 4.0 kg until 过机.  
5. Confirm live list ¥ on K01 / H01 / A02 / P05 are the payable numbers (this sheet assumes yes).  
6. Duty true-up on 含税.  
7. Whether **P01 $5** stays a traffic SKU even though conservative landed is $5.68.

---

## What this is not

- Not a catalog price change.  
- Not a customer-facing ship rate.  
- Not a Square / Facebook action.  
- Not a buy on Taobao.

---

## DONE

- Files: `docs/MARGIN_50PCT_CONSERVATIVE_2026-09-10.md`, `docs/MARGIN_50PCT_CONSERVATIVE_2026-09-10.csv` on Origin `main`.  
- Inbound default: **4.0 kg · wt + $4.61 floor** (not $2.52). Air column published; product floor stays sea.  
- Live list overrides: K01 ¥125 · H01 ¥17.90 · A02 ¥85.90 · P05 ¥109.90.  
- FX 6.725515. 11/11 mãs. 0 × `NEED_LIVE_TB`.  
- **UNDER:** all 10 priced mãs. **Top under (live):** S01 −$18.60, K01 −$18.48, A02 −$13.68. **Closest under:** P03 −$0.44. **Sell &lt; landed:** P01.  
- Default inbound for Cap/Money: [conservative inbound memo](./CAINIAO_INBOUND_CONSERVATIVE_2026-09-10.md).  
- Open Q: **need Boss App quote at 4–5 kg.**  
- Live catalog read-only. Product JSON **not** edited.  
- Sheet commit SHA: `9736129532452b42120ad388a9428ba024ae69c6`. Origin `main` SHA after merge.
