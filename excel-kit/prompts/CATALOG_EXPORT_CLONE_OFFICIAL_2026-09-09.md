# Catalog export Excel/OD → sell-site JSON + CLONE_TO_OFFICIAL

Boss 2026-09-09. Paste into a **Cursor Cloud Agent** on `https://github.com/SkyLanter/Sassy-closet` (kit). **Do not** push to or fight Origin main of sassy-closet-shop. Mini Boss’s Origin agent owns the live shop.

## Outcome

1. Scripts + docs under `excel-kit/` that export **REAL** catalog rows from `sassycloset.xlsx` into sell-site import JSON (`catalog.v1`).
2. `CLONE_TO_OFFICIAL.md` Boss can use later to stand up official sell site from the test shop.
3. Sample JSON for the **10 known mãs only** — never invent mãs.

## Context

- Sell-test live: https://sassy-closet-shop.vercel.app (Blob SoT; open `/admin`)
- Intake UNTOUCHED: https://sassy-closet.vercel.app
- OD hub: `Documents/Sassy Closet/sassycloset.xlsx` + `Photos/{MA}/`
- Allowlist ONLY: A01 S01 P01 P02 P03 P04 P05 K01 H01 A02
- Prices USD: A01 25 · S01 28 · P01 5 · P02 Hold · P03 18 · P04 13 · P05 Hold · K01 37 · H01 8 · A02 22
- Mã: letter + 2–3 digits. Letters A/Q/V/K/G/B/P/H/J/S/O/D. Do not mint new numbers.
- Target catalog shape: product (`mã`, `titleEn`/`titleVn`, `descriptionEn`/`descriptionVn`, `type`, `status` hold|available, `priceUsd`|null, `qty=1`); `colors[{id,name?,hex?}]`; `images[{src|url,colorId|null,order?}]`. Shop customer colors = text-only; Messenger-first; Zelle method word OK; no personal name.

## Deliverables

1. `excel-kit/docs/SELL_CATALOG_CONTRACT.md` — catalog.v1 schema + xlsx column map
2. `excel-kit/scripts/export_sell_catalog.py` — xlsx → `out/sell-catalog.v1.json`; hard-fail on non-allowlist / invent; Hold when price empty
3. `out/sell-catalog.v1.json` if local xlsx exists; else document run steps
4. `excel-kit/docs/CLONE_TO_OFFICIAL.md` — new Vercel project (never intake), Blob migrate/import, env, Messenger, checklist
5. `excel-kit/scripts/validate_sell_catalog.py` — schema + allowlist
6. Link from `KIT.md` / `PROMPTS.md`; save this brief under `excel-kit/prompts/CATALOG_EXPORT_CLONE_OFFICIAL_2026-09-09.md` if missing

## Hard stops

No invent mã/stock/prices · no Square Save · no FB Post/Send · no passwords · intake untouched · do not modify Origin sell-site app code

## Success

Docs readable · scripts run or dry-run documented · JSON allowlist-only · validate PASS · open PR on this repo · report PR URL + sha + paths

## Kit commands (after this lands)

```
python3 excel-kit/scripts/export_sell_catalog.py \
  -w "$HOME/OneDrive/Documents/Sassy Closet/sassycloset.xlsx" \
  --photos-dir "$HOME/OneDrive/Documents/Sassy Closet/Photos" \
  -o ./out/sell-catalog.v1.json
python3 excel-kit/scripts/validate_sell_catalog.py ./out/sell-catalog.v1.json
python3 excel-kit/tests/run_checks.py
```

Repo-root `/out/` is gitignored. Committed sample: `excel-kit/samples/sell-catalog.v1.json`.
