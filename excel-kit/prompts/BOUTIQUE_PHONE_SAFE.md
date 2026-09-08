# Prompt — boutique phone-safe

> **Retired 2026-09-07.** Cute / pink / emoji / phone Excel is retired. Boss daily book is the plain `Sassy_Closet_Data.xlsx` (`build_plain_data.py`). See `PLAIN_DATA_EXCEL.md`.

Paste this when anyone rebuilds a book that must open in **Excel iOS / OneDrive mobile**. Desktop AutoFilter books are allowed to be richer; phone books must stay typeable.

```
Phone-safe Sassy Closet Excel. Microsoft Excel / OneDrive only. Not Google Sheets.

MUST
- Freeze HEADER ROW ONLY (freeze A2 or Official header row 5). Never freeze a column (no freeze at E). A thumb must reach size, price, status
- No sheet protection. No locked cells. Yellow = type. White = formula
- No embedded images, stickers, or phone tiles. photo_link URL only
- Photos live in Documents/Sassy Closet/Photos/ as #001.jpg / AO001.jpg
- AutoFilter + short tables. Do not prefill 200 empty rows (~25 Official rows max at SoT build, and those must not be fake stock — empty is better)
- Arial or Calibri. Cute pink (deep rose headers, blush rows). File must feel open, not “preview only”
- Customer-facing fit = Asia size + cm. Never quote US sizes to buyers

SHOP LAW
- Square Free = on-hand inventory source of truth
- Documents/Sassy Closet/Sassy_Closet_SoT.xlsx = working copy / mã index / captions — NOT second inventory
- Mã AO/QU/VA/AK/GI/PK/SET + 3 digits. Never invent stock
- Bots draft only. Owner posts, sends, takes Zelle, taps Square Save
- Cursor Cloud Agents build in GitHub. Kit syncs to OneDrive

IF YOU ARE EDITING THE SOT BOOK
Sheets: START HERE, TOMORROW, BOT PROMPT, Lists, Official, Wishlist, Orders, Dashboard
Official header row 4, data from row 5. Dropdowns from Lists. Next mã = Dashboard MAXIFS — Stock reads it, bots do not mint mã
After any demo seed, run: python3 excel-kit/clean_sot_demo.py Sassy_Closet_SoT.xlsx

IF YOU ARE EDITING DESKTOP BOOKS
Use excel-kit/build_boutique_desktop.py and prompts/BOUTIQUE_DESKTOP_EFFICIENT.md
Still no embeds. Freeze header only so the same file is not hostile on a phone

STOP
Chat preview is not Excel. Owner downloads / Open in app. Do not Save in Square from this prompt.
```
