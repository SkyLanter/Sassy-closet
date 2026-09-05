# Efficiency

How the shop stays fast without a second inventory brain or bloated workbooks.

## Standing rules (do not “optimize” these away)

- **Square Free = on-hand inventory source of truth.** Excel never wins an argument with Square about how many pieces exist.
- **Desktop SoT** (`Documents/Sassy Closet/Sassy_Closet_SoT.xlsx`) is the working copy / mã index / captions — not a second inventory.
- **Photos** stay in `Documents/Sassy Closet/Photos/` as `#001.jpg` / `AO001.jpg`. Excel stores `photo_link` only. Embedded pictures explode file size, break phone Excel, and go stale.
- **Mã** = `AO` / `QU` / `VA` / `AK` / `GI` / `PK` / `SET` + 3 digits. Never invent stock to “fill the sheet.”
- **Bots draft only.** Owner posts, sends, takes Zelle, taps Square Save.
- **Cursor Cloud Agents** change code in this repo. **Kit** syncs built files to OneDrive. Do not hand-edit a copy and forget to sync.

## What is expensive

| Cost | Why it hurts | Do this instead |
| --- | --- | --- |
| Embedded images | 5–20 MB books, iOS Excel hangs, OneDrive preview lies | `photo_link` URL |
| 200 prefilled empty rows | Phone scroll tax, fake “stock,” broken tables | Header + short blank runway (desktop builder uses 40) |
| Two inventory brains | Square vs Excel fights; Guide says còn wrong | Square on-hand; Excel captions / mã / photo index |
| Freeze that hides columns | Phone cannot type size / price | Freeze **header row only** — see `prompts/BOUTIQUE_PHONE_SAFE.md` |
| Rebuilding SoT for a caption tweak | Loses Boss typing | Edit the live OneDrive file; rebuild only from `BOT PROMPT` |
| Demo / sample rows left in Official | Looks like live stock | `clean_sot_demo.py` |

## Fast daily path

1. **In-hand piece** → Square Save (Boss yes) with Track stock ON → one Official / Ma_List row → mã Boss assigned → photo in `Photos/` → paste share URL in `photo_link`.
2. **Hunt** → one Candidates / Wishlist row. Off Square until bought.
3. **Inbox** → Guide drafts from Official `ma` + `size` + `status`. Owner sends.
4. **Morning brief** → Dashboard (SoT) or empty desktop filters — not a new workbook.

## Desktop vs phone

- **Desktop Official + Wishlist** (`build_boutique_desktop.py`): AutoFilter arrows, frozen header, status dropdowns, lean columns. Built for a computer.
- **Phone:** use SoT with header-row freeze only, yellow input cells, no sheet protection, no tiles, no embeds. Prompt: `prompts/BOUTIQUE_PHONE_SAFE.md`.
- Do not ship “cute phone” books that embed stickers or lock columns.

## Kit / agent efficiency

- Import `schema.py`. Do not retype headers.
- `photo_link` stays last on Ma_List and Candidates.
- Run `py_compile` on every `.py` you touch.
- Prefer patching wording / clearing demo rows (`clean_sot_demo.py`) over a full SoT rebuild.
- After a good desktop build, Kit copies the two `.xlsx` files to OneDrive. This repo stays code + prompts.
