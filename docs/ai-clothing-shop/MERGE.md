# Merge with catalog export / CLONE_TO_OFFICIAL

Do **not** abandon export work. Do **not** open a second Official / catalog.v1 writer.

## Sibling already in progress

Agent **Kit: sell catalog export + CLONE_TO_OFFICIAL**  
`bc-8eb42dad-c793-4dc5-92b1-c63df4375ad2`  
Branch: `cursor/catalog-export-clone-official-5ad2`

That branch (as of 2026-09-09) already has the **writer**:

| Path | Job |
| --- | --- |
| `excel-kit/sell_catalog.py` | catalog.v1 model + `SELL_ALLOWLIST` (same 10 mãs) |
| `excel-kit/scripts/export_sell_catalog.py` | `sassycloset.xlsx` → `out/sell-catalog.v1.json` |
| `excel-kit/scripts/validate_sell_catalog.py` | Schema + allowlist + Boss USD table |
| `excel-kit/docs/SELL_CATALOG_CONTRACT.md` | Field map (camelCase `priceUsd`, `titleEn`, …) |
| `excel-kit/docs/CLONE_TO_OFFICIAL.md` | New Vercel project (never intake), Blob, Messenger |
| `excel-kit/prompts/CATALOG_EXPORT_CLONE_OFFICIAL_2026-09-09.md` | Paste brief |
| `excel-kit/samples/sell-catalog.v1.json` + `out/sell-catalog.v1.json` | Allowlist-only artifact |

**This playbook PR does not copy those files.** When that PR merges, keep them. Use them as the exporter.

## What this PR owns

| Path | Job |
| --- | --- |
| `docs/ai-clothing-shop/` | Sourced learn playbook + live sell-test notes |
| `excel-kit/prompts/AI_CLOTHING_SHOP_APPLY_TO_SELL_TEST.md` | Concrete apply list for the live shop |
| `excel-kit/sell_test_allowlist.py` | Same 10 mãs + Boss USD table (import-friendly) |
| `excel-kit/sot/validate_sell_catalog_export.py` | Extra gate: also accepts catalog.v1 `products[]` |

After both land:

```bash
# Sibling writer (xlsx → catalog.v1)
python3 excel-kit/scripts/export_sell_catalog.py \
  -w "$HOME/OneDrive/Documents/Sassy Closet/sassycloset.xlsx" \
  --photos-dir "$HOME/OneDrive/Documents/Sassy Closet/Photos" \
  -o ./out/sell-catalog.v1.json
python3 excel-kit/scripts/validate_sell_catalog.py ./out/sell-catalog.v1.json

# Playbook gate (same file — allowlist / Hold / no A03)
python3 excel-kit/sot/validate_sell_catalog_export.py ./out/sell-catalog.v1.json
```

Prefer **one** allowlist constant long-term: `sell_catalog.SELL_ALLOWLIST` or `sell_test_allowlist.SELL_TEST_MAS` (they must stay equal). Do not grow a third tuple.

## Expected merge conflicts

Both PRs touch `README.md`, `excel-kit/README.md`, `excel-kit/KIT.md`, `excel-kit/PROMPTS.md`, `excel-kit/tests/run_checks.py`.

Resolve by **keeping both** sections:

- Their prompt **16 / catalog export** block **and** this playbook’s prompt **15**.
- Their `check_*` for catalog.v1 **and** `check_sell_catalog_export`.
- Both KIT.md bullets.

If filenames collide, merge the files — do not delete theirs or ours.

## What this playbook will not do

- Will not replace `export_sell_catalog.py`.
- Will not `append_official_row` for the 10 pieces.
- Will not call Square or POST Messenger Send.
- Will not add A03 / Q01 / D01.
- Will not change intake `sassy-closet/`.
- Will not fight Origin shop `main`.
