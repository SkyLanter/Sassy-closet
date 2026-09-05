# Prompt — boutique desktop (efficient)

Paste this when a Cursor Cloud Agent or Kit should rebuild the **desktop** Official + Wishlist books. Do not use this to remake `Sassy_Closet_SoT.xlsx` unless Boss also pasted the SoT `BOT PROMPT`.

```
Build desktop Official + Wishlist for Sassy Closet with excel-kit.

RUN
  python3 excel-kit/build_boutique_desktop.py --out-dir ./out
  python3 -m py_compile excel-kit/schema.py excel-kit/build_boutique_desktop.py excel-kit/clean_sot_demo.py

CONTRACT (import excel-kit/schema.py — do not retype)
- Official: How_to_use, Ma_List, Orders, Bot_Activity
- Wishlist: How_to_use, Candidates
- MA_LIST / ORDERS / BOT_ACTIVITY / CANDIDATES headers exactly as schema.py
- photo_link LAST on Ma_List and Candidates
- Freeze header row (A2). AutoFilter on the pink header.
- Status dropdowns: Ma_List in_stock/held/sold/archived; Orders Inquiry/Reserved/Paid/Shipped/Picked up/Cancelled; Candidates candidate/watching/skip/bought + Type list
- Zero embedded images. photo_link = OneDrive share URL text/hyperlink only
- Zero live inventory rows. Zero customer PII. Empty data is correct
- Pink blush headers (F7C6D5), ink 4A3038, Calibri. No sheet protection

SHOP LAW
- Square Free = on-hand inventory source of truth
- Desktop SoT Excel: Documents/Sassy Closet/Sassy_Closet_SoT.xlsx (working copy / mã index / captions — NOT second inventory)
- Photos: Documents/Sassy Closet/Photos/ named #001.jpg / AO001.jpg
- Mã: AO/QU/VA/AK/GI/PK/SET + 3 digits. Never invent stock
- Bots draft only. Owner posts / sends / Zelle / Square Save
- Cursor Cloud Agents build in this GitHub repo. Kit syncs .xlsx to OneDrive:
    Documents/Sassy Closet/Sassy_Closet_Official_desktop.xlsx
    Documents/Sassy Closet/Sassy_Closet_Wishlist_desktop.xlsx

EFFICIENCY
- Reuse schema.py helpers (style_header_row, add_list_dropdown, strip_workbook_images)
- Do not prefill 200 empty rows. Do not add sticker sheets. Do not freeze column E
- If you only need to strip demo rows or fix Square wording, run clean_sot_demo.py instead of a rebuild
- Prefer committing useful Python over empty stubs

STOP
Do not Save in Square. Do not post. Do not invent AO999. Sync is Kit’s job after the files verify.
```
