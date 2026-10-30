# Public sell-price drift (draft)

Observed 2026-10-29T06:40:27Z. Live dollars are the public catalog. Intake dollars are non-blank public `sell_usd` values. This file records the comparison. It does not change Blob, intake, Meta, or any fixture price.

S06 stays **$25**. The live observation is $25.

## Boss confirm

Do not copy intake dollars onto the live site, and do not copy live dollars onto intake, until Boss picks a side. Largest intake gaps: S01 live $39 vs intake $28, P03 live $11 vs intake $18.

Intake sell already matches live for: A05 $25, A06 $23, H01 $8, P01 $5.

## Intake sell vs live

| Mã | Fixture | Live | Gap |
| --- | ---: | ---: | ---: |
| A01 | $25 | $27 | $2 |
| A02 | $22 | $23 | $1 |
| A03 | $19 | $22 | $3 |
| A04 | $20 | $21 | $1 |
| B01 | $41 | $46 | $5 |
| B02 | $30 | $31 | $1 |
| J01 | $30 | $29 | $1 |
| J02 | $35 | $40 | $5 |
| K01 | $37 | $36 | $1 |
| P03 | $18 | $11 | $7 |
| P04 | $13 | $10 | $3 |
| P05 | $23 | $25 | $2 |
| S01 | $28 | $39 | $11 |

## Catalog seed (`sassy-closet-shop/data/products.json`) vs live

| Mã | Fixture | Live | Gap |
| --- | ---: | ---: | ---: |
| A03 | $25 | $22 | $3 |
| A04 | $23 | $21 | $2 |
| A05 | $28 | $25 | $3 |
| A06 | $26 | $23 | $3 |
| A07 | $28 | $26 | $2 |
| A08 | $32 | $29 | $3 |
| A09 | $28 | $26 | $2 |
| A10 | $31 | $29 | $2 |
| A11 | $29 | $27 | $2 |
| A12 | $32 | $29 | $3 |
| A13 | $27 | $25 | $2 |
| A14 | $26 | $24 | $2 |
| A15 | $27 | $25 | $2 |
| B01 | $45 | $46 | $1 |
| B02 | $25 | $31 | $6 |
| D01 | $46 | $40 | $6 |
| D02 | $46 | $40 | $6 |
| D03 | $34 | $31 | $3 |
| J01 | $32 | $29 | $3 |
| J02 | $46 | $40 | $6 |
| O01 | $21 | $22 | $1 |
| O02 | $21 | $24 | $3 |
| O03 | $6 | $7 | $1 |
| O05 | $14 | $15 | $1 |
| Q01 | $30 | $28 | $2 |
| S02 | $28 | $25 | $3 |
| S03 | $29 | $26 | $3 |
| S04 | $48 | $41 | $7 |

## README hub-ten table vs live

| Mã | Fixture | Live | Gap |
| --- | ---: | ---: | ---: |
| A01 | $25 | $27 | $2 |
| A02 | $21 | $23 | $2 |
| P02 | $24 | $25 | $1 |
| P03 | $10 | $11 | $1 |
| P04 | $9 | $10 | $1 |
| P05 | $23 | $25 | $2 |

## `preserve_live_prices` vs live

Both Taobao seed copies are read. Only the public dollar map is compared.

| Mã | Fixture | Live | Gap |
| --- | ---: | ---: | ---: |
| A01 | $25 | $27 | $2 |
| P03 | $18 | $11 | $7 |

## `CATALOG_USD` in the boss price lock vs live

No dollar differences.

## S06 and other checks

- S06 stays $25 on the live observation. No checked fixture stores another S06 dollar.

Live mãs with no catalog-seed row: A16, A17, A18, A19, A20, A21, A22, A23, D04, D05, S05, S06, S07, S08, S09, S10, S11, S12, S13, V01, V02, V03.

Rendered pages checked against the same live dollars:

- `https://sassycloset.vercel.app/m/A03` A03 $22
- `https://sassycloset.vercel.app/m/P03` P03 $11
- `https://sassycloset.vercel.app/m/S01` S01 $39
- `https://sassycloset.vercel.app/m/S06` S06 $25
- `https://sassy-closet-shop.vercel.app/m/P03` P03 $11
- `https://sassy-closet-shop.vercel.app/m/S01` S01 $39
