# Sell catalog contract — catalog.v1

Handoff from OneDrive `Documents/Sassy Closet/sassycloset.xlsx` (kit / OD hub) into the **sell-test** shop import JSON. Mini Boss’s Origin agent owns [sassy-closet-shop](https://sassy-closet-shop.vercel.app). This kit only writes JSON + docs. **Do not modify Origin shop app code from this repo.**

Intake (`https://sassy-closet.vercel.app`, folder `sassy-closet/`) stays untouched.

## Hard stops

- Never invent mã, stock, or prices
- Never Square Save
- Never Facebook Post / Send
- Never commit passwords or secret env values
- Never put cost, Taobao `source_link`, or customer names in catalog JSON
- Shop customer colors are **text-only** (name). Do not invent hex
- Messenger-first. The word **Zelle** is OK. No personal name on the site

## Allowlist (first ten only)

These are the only mãs this export may emit. Letter + 2–3 digits (`A01`…`A99`, then `A100`). Letters: `A Q V K G B P H J S O D`.

| Mã | Type | USD | Status |
| --- | --- | --- | --- |
| A01 | top | 25 | available |
| S01 | set | 28 | available |
| P01 | accessory | 5 | available |
| P02 | thermos | — | **hold** |
| P03 | accessory | 18 | available |
| P04 | accessory | 13 | available |
| P05 | thermos | — | **hold** |
| K01 | jacket | 37 | available |
| H01 | hair | 8 | available |
| A02 | top | 22 | available |

`P02` / `P05` stay Hold even when the xlsx `sell_usd` cell has a number (P05 currently shows `23` on All — **do not publish it**). Empty `sell_usd` → Hold.

Scripts **hard-fail** if All has any other mã, a duplicate, a missing allowlist mã, a kind letter that does not match the mã, or a priced row that disagrees with the Boss table above.

## catalog.v1 JSON

```json
{
  "schema": "catalog.v1",
  "source": "Documents/Sassy Closet/sassycloset.xlsx",
  "exportedAt": "2026-09-09T00:00:00Z",
  "allowlist": ["A01", "S01", "P01", "P02", "P03", "P04", "P05", "K01", "H01", "A02"],
  "products": [
    {
      "ma": "A01",
      "titleEn": "",
      "titleVn": "",
      "descriptionEn": "",
      "descriptionVn": "",
      "type": "top",
      "status": "available",
      "priceUsd": 25,
      "qty": 1,
      "colors": [{ "id": "kem", "name": "Kem" }],
      "images": [
        {
          "src": "Documents/Sassy Closet/Photos/A01/001.jpg",
          "colorId": null,
          "order": 1
        }
      ]
    }
  ]
}
```

### Product fields

| Field | Rule |
| --- | --- |
| `ma` | Allowlisted A01-style code. Never mint |
| `titleEn` / `titleVn` | From xlsx if those columns exist. Current hub has **no title columns** — leave empty. Do not invent shop copy |
| `descriptionEn` / `descriptionVn` | Same. Do not copy staff `flag` notes onto the customer site |
| `type` | From mã letter (`A`→`top`, `S`→`set`, `P`→`accessory`, `K`→`jacket`, `H`→`hair`, …). `P02`/`P05` → `thermos` |
| `status` | `hold` or `available` only |
| `priceUsd` | Number on available; **`null` on hold**. qty is always `1` |
| `colors` | `{id, name?, hex?}`. `id` is a slug of the xlsx color word. **No invented hex** |
| `images` | `{src\|url, colorId, order?}`. `src` is the OneDrive relative path when `--photos-dir` is passed. Skip `_placeholder`, `_probe`, `.keep`, `README`. Do not invent Blob URLs |

Shop admin (sell-test) already uses `titleEn`, `titleVn`, `descriptionEn`, `descriptionVn`, `status`, `priceUsd`, `colors[]`, `images[{src,colorId}]`. Import of this file is Origin’s job.

## xlsx column map (`All` sheet)

`sassycloset.xlsx` is the website mirror (see OD `README_sassycloset.txt`). **Read `All` only.** Kind tabs are duplicates — do not merge them (that would double-count).

| xlsx | catalog.v1 | Notes |
| --- | --- | --- |
| `ma` | `product.ma` | Required. Allowlist only |
| `kind` | drives `type` | Must match mã letter |
| `colors` | `colors[].name` | Comma / `;` / `/` split. Text-only |
| `sell_usd` | `priceUsd` + `status` | Empty → Hold. Must match Boss table when set |
| `photo_folder` | image `src` prefix | Default `Documents/Sassy Closet/Photos/{MA}/` |
| `title_en` / `title_vn` | titles | Optional; absent on the live hub |
| `description_en` / `description_vn` | descriptions | Optional; absent on the live hub |
| `source_link` | **omit** | Taobao / e.tb.cn stays on the hub, not the shop JSON |
| `cost` / `currency` | **omit** | Never publish vốn |
| `square` / `status` | **omit** | Hub `status=staged` is not sell `hold\|available` |
| `flag` | **omit** from customer JSON | Staff notes only (`thermos kind hold`, photo checks) |
| `next_desk` | **omit** | |

`Orders` on the same book is out of scope (and must stay empty of customer names in git).

## Photos

```
Documents/Sassy Closet/Photos/{MA}/001.jpg
```

Verified on OD for this allowlist (skip junk):

| Mã | Real files |
| --- | --- |
| A01 | `001.jpg`, `002.jpg` |
| S01 | `001.jpg` |
| P01 | `001.jpg`, `002.jpg` |
| P02 | `001.jpg`, `002.jpg` |
| P03 | `001.jpg`, `002.jpg`, `003.jpg` |
| P04 | `001.jpg`, `002.jpg` |
| P05 | `001.jpg`, `002.jpg`, `003.jpg` |
| K01 | `001.jpeg`, `002.jpeg` |
| H01 | `001.jpeg`, `002.jpeg`, `003.jpeg` |
| A02 | `001.jpeg`, `002.jpeg` |

Those paths are **not** public URLs. Official clone uploads them to that project’s Blob, then rewrites `src` or uses Admin → Upload image. See `CLONE_TO_OFFICIAL.md`.

## Commands

```bash
pip install -r requirements.txt

# Export (needs the OD workbook locally)
python3 excel-kit/scripts/export_sell_catalog.py \
  -w "$HOME/OneDrive/Documents/Sassy Closet/sassycloset.xlsx" \
  --photos-dir "$HOME/OneDrive/Documents/Sassy Closet/Photos" \
  -o ./out/sell-catalog.v1.json

# No write
python3 excel-kit/scripts/export_sell_catalog.py -w path/to/sassycloset.xlsx --dry-run

# Validate
python3 excel-kit/scripts/validate_sell_catalog.py ./out/sell-catalog.v1.json
```

Committed artifact (allowlist only, no invented codes): `out/sell-catalog.v1.json`. Other files under `/out/` stay gitignored. `excel-kit/samples/sell-catalog.v1.json` is the same 10-mã copy for kit-local browsing and must match the committed artifact.

If the workbook is missing, the exporter exits `2` and prints the run steps. It does **not** emit a fake catalog. If `-w` is set and that file is missing, exit `2` — do **not** fall back to OneDrive / env / cwd (a typo must not export a different book).

## Related

- Prompt: `excel-kit/prompts/CATALOG_EXPORT_CLONE_OFFICIAL_2026-09-09.md`
- Official stand-up: `excel-kit/docs/CLONE_TO_OFFICIAL.md`
- Sell-test: https://sassy-closet-shop.vercel.app · `/admin`
- OD hub: `Documents/Sassy Closet/sassycloset.xlsx` + `Photos/{MA}/`
