# Clone-to-official checklist

Goal: take the **sell-test lookbook** (10 allowlist mãs) and stage the same codes on the **Official Excel working copy** — without inventing stock, without Square Save, without fighting Origin `main`.

Sibling agent **Kit: sell catalog export + CLONE_TO_OFFICIAL** already wrote the exporter on `cursor/catalog-export-clone-official-5ad2`:

- Human runbook: `excel-kit/docs/CLONE_TO_OFFICIAL.md`
- Schema: `excel-kit/docs/SELL_CATALOG_CONTRACT.md` (`catalog.v1`)
- Writer: `excel-kit/scripts/export_sell_catalog.py`
- Their validator: `excel-kit/scripts/validate_sell_catalog.py`

This page is the **learn + merge checklist** (how AI shops fail while cloning). Playbook gate (also accepts catalog.v1):

```bash
python3 excel-kit/sot/validate_sell_catalog_export.py path/to/sell-catalog.v1.json
```

Allowlist module: `excel-kit/sell_test_allowlist.py` (same 10 mãs as `sell_catalog.SELL_ALLOWLIST`).

## Why clone at all

Sell-test is a **message-first lookbook**. Official Excel (`Documents/Sassy Closet/Sassy_Closet_SoT.xlsx`) is the desktop **mã index / captions**. Square Free remains on-hand truth. Cloning is “same mã, same story,” not “second warehouse.”

Kit Excel still parses **legacy AO001** (`schema.parse_ma`). Sell-test mãs are **A01**. Do not “fix” `parse_ma` to accept A01 in a drive-by — that is the documented A01 handoff (`schema.py` comment, `bc-43bc86e1`). Until that handoff, Official append for `A01` needs an explicit Boss/Stock path, not a silent rename to `AO001`.

**Never rewrite `A01` → `AO001`.** That is a mã collision.

## Export contract

**Prefer catalog.v1** (sibling): `{ "schema": "catalog.v1", "products": [ ... ] }` with camelCase `titleEn`, `priceUsd`, `status: available|hold`. See `excel-kit/docs/SELL_CATALOG_CONTRACT.md`.

This playbook gate also accepts a flat JSON list or CSV:

| Field | Required | Notes |
| --- | --- | --- |
| `ma` | yes | Exactly one of `A01 S01 P01 P02 P03 P04 P05 K01 H01 A02` |
| `kind` | recommended | Letter `A`/`S`/`P`/`K`/`H` |
| `title_en` / `title_vn` | recommended | Shop admin fields |
| `description_en` / `description_vn` | recommended | Bilingual flavor |
| `status` | recommended | `Available` or `Hold` only |
| `price_usd` | recommended | Empty when `inbox_for_price` |
| `inbox_for_price` | recommended | true for P02, P05 (as of 2026-09-09) |
| `cover` | recommended | URL or `/products/{ma}/cover.jpg` |
| `colors` | recommended | Hex boxes |
| `images` | recommended | `{ src, color_hex, role }` |
| `source` | optional | `sell-test` |

Forbidden in the export:

- Any mã not on the allowlist (A03, Q01, AO001, P06, …).
- Customer names, Messenger PSIDs, Zelle handles.
- Square tokens, Blob tokens, passwords.
- Filled Square import rows.

## Human checklist (Boss / Stock)

1. **Export** from sell-test (sibling CLI or `/admin` download when it exists).
2. **Validate** with `validate_sell_catalog_export.py` (`--strict-complete` default).
3. **Diff mãs** against Official. If Official already has `A01`, **update that row** or stop — do not append a second `A01`.
4. **ASK STOCK** for any desire to add a piece. Do not mint A03.
5. Photos: copy bytes to `Documents/Sassy Closet/Photos/{ma}/`. Excel gets `photo_link` (OneDrive share URL) only. No embeds.
6. Caption fields: shop EN/VN descriptions → Official `name_en` / `name_vi` / notes. Do not invent measurements or qty.
7. Status map:
   - Shop `Available` → Official `Available` (working copy). Square still wins on-hand.
   - Shop `Hold` → Official `Hold`. No USD if inbox-for-price.
8. **#shop-decisions** before anyone taps Square Save.
9. Orders stay off this clone. Facebook inbox remains the store.
10. Do not promote sell-test to Origin `main` as a side effect of the clone.

## Script rules (when the exporter lands)

- `--ma` required per Official append; missing → print ASK STOCK and exit (existing `append_official_row.py` law).
- Refuse `ma=next`, `ma=A03`, `ma=AO001` as a “translation.”
- `--dry-run` prints the mapping and writes nothing.
- Do not call Square APIs.
- Do not POST Messenger.
- Do not open intake `saveSubmission` / `nextMa()`.

## Merge with in-progress work

If a PR already adds `CLONE_TO_OFFICIAL.md` or an exporter:

- Keep their command as the **writer**.
- Keep this checklist as the **law**.
- Import `SELL_TEST_MAS` instead of a second tuple.
- Run the validator in their README / CI.

See [MERGE.md](MERGE.md).
