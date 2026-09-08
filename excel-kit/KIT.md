# Kit

Cute / pink / emoji / phone Excel is **retired** (Boss 2026-09-07).

Boss opens one plain book: `Sassy_Closet_Data.xlsx` — Inventory, Candidates, Orders. English headers, no merged title art, no embeds.

| Role | What |
| --- | --- |
| Website `https://sassy-closet.vercel.app` | GF input |
| `Sassy_Closet_Data.xlsx` | Boss simple mirror / edit buffer |
| Square Free | On-hand inventory truth. Excel is not. |

```bash
# From repo root — fetch live /api/export and write the plain book
python3 excel-kit/build_plain_data.py --out-dir ./out
./excel-kit/kit.sh pull    # same as: kit.sh plain
```

`kit.sh pull` / `kit.sh plain` land `Sassy_Closet_Data.xlsx` (not the old blush Wishlist desktop book). They copy into OneDrive `Documents/Sassy Closet/` only when that folder already exists. They do **not** delete other Boss OneDrive files.

Contract: `prompts/PLAIN_DATA_EXCEL.md`. Photos: `PHOTOS.md`.
