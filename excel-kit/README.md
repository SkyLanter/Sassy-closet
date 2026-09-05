# excel-kit

Builders and prompts for Sassy Closet Excel books. **This GitHub repo is where Cursor Cloud Agents change the kit.** Kit syncs generated `.xlsx` files to OneDrive `Documents/Sassy Closet/`.

Square Free is the on-hand inventory source of truth. The desktop SoT workbook is a working copy / mã index / captions — not a second inventory.

## Layout

```
excel-kit/
  README.md
  EFFICIENCY.md
  DESIGN_NOTES.md
  prompts/BOUTIQUE_DESKTOP_EFFICIENT.md
  prompts/BOUTIQUE_PHONE_SAFE.md
  schema.py
  clean_sot_demo.py
  build_boutique_desktop.py
```

## Shop rules

- **Square Free** = on-hand inventory source of truth. Track stock ON for every item and variation. Wishlist / candidates stay off Square until Boss confirms bought and says Save.
- **Desktop SoT Excel** lives on OneDrive: `Documents/Sassy Closet/Sassy_Closet_SoT.xlsx` (working copy / mã index / captions — **not** second inventory).
- **Photos** live in `Documents/Sassy Closet/Photos/` named `#001.jpg` / `AO001.jpg`. Excel stores `photo_link` only — **never embed images**.
- **Mã** = `AO` / `QU` / `VA` / `AK` / `GI` / `PK` / `SET` + 3 digits. Never invent stock. Never reuse a Sold mã.
- **Bots draft only.** Owner posts, sends, takes Zelle, taps Square Save.
- **Cursor Cloud Agents** build here. **Kit** syncs files to OneDrive.

## Scripts

Needs Python 3.10+ and `openpyxl` (`pip install -r requirements.txt` from the repo root).

```bash
# Desktop Official + Wishlist (empty headers, freeze, AutoFilter, status dropdowns)
python3 excel-kit/build_boutique_desktop.py --out-dir ./out

# Strip demo rows + Square wording patch from a SoT workbook
python3 excel-kit/clean_sot_demo.py path/to/Sassy_Closet_SoT.xlsx -o ./out/Sassy_Closet_SoT_cleaned.xlsx
```

`schema.py` is the shared contract: `MA_LIST`, `ORDERS`, `BOT_ACTIVITY`, `CANDIDATES` (`photo_link` last on Ma_List and Candidates), plus SoT Official / Wishlist / Orders headers for the cleaner.

Do not commit live inventory, customer names, or secrets. Empty data sheets are intentional.

## OneDrive sync targets

| File | Role |
| --- | --- |
| `Documents/Sassy Closet/Sassy_Closet_SoT.xlsx` | Pink stock book (Official / Wishlist / Orders / Dashboard) |
| `Documents/Sassy Closet/Sassy_Closet_Official_desktop.xlsx` | Lean desktop Ma_List / Orders / Bot_Activity |
| `Documents/Sassy Closet/Sassy_Closet_Wishlist_desktop.xlsx` | Lean desktop Candidates |
| `Documents/Sassy Closet/Photos/` | `#001.jpg` / `AO001.jpg` — links only in Excel |
