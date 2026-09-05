# Sassy Closet shop tooling

GitHub home for the Excel kit. **Cursor Cloud Agents build here. Kit syncs files to OneDrive.**

The shop’s live working copy is **not** this repo. It is:

`Documents/Sassy Closet/Sassy_Closet_SoT.xlsx` on OneDrive

## Shop rules

- **Square Free = on-hand inventory source of truth.** Track stock ON for every item and variation. Wishlist / candidates stay off Square until Boss confirms bought and says yes to Save.
- **Desktop SoT Excel** lives on OneDrive: `Documents/Sassy Closet/Sassy_Closet_SoT.xlsx`. It is the working copy / mã index / captions — **not** a second inventory.
- **Photos** live in `Documents/Sassy Closet/Photos/` named `#001.jpg` / `AO001.jpg`. Excel stores `photo_link` only — **never embed images**.
- **Mã** = `AO` / `QU` / `VA` / `AK` / `GI` / `PK` / `SET` + 3 digits. Never invent stock. Never reuse a Sold mã.
- **Bots draft only.** The owner posts on Facebook, sends the message, takes Zelle, and taps Save in Square.
- **Cursor Cloud Agents** change kit code in this repo. **Kit** syncs generated workbooks to OneDrive.

Facebook inbox is the store. `#shop-decisions` is Boss yes/no. This repo is builders + prompts — no live stock, no customer PII, no secrets.

## Kit

See [`excel-kit/`](excel-kit/) (`README.md`, `EFFICIENCY.md`, `DESIGN_NOTES.md`, prompts, and the openpyxl scripts).

```bash
pip install -r requirements.txt
python3 excel-kit/build_boutique_desktop.py --out-dir ./out
python3 excel-kit/clean_sot_demo.py path/to/Sassy_Closet_SoT.xlsx -o ./out/SoT_cleaned.xlsx
```

| Script | Job |
| --- | --- |
| `excel-kit/schema.py` | `MA_LIST` / `ORDERS` / `BOT_ACTIVITY` / `CANDIDATES` (`photo_link` last on Ma_List + Candidates) |
| `excel-kit/build_boutique_desktop.py` | Official + Wishlist desktop books: freeze, AutoFilter, status dropdowns, no embeds |
| `excel-kit/clean_sot_demo.py` | Clear demo rows; Square wording patch; strip embedded pictures |

Prompts for agents: `excel-kit/prompts/BOUTIQUE_DESKTOP_EFFICIENT.md`, `excel-kit/prompts/BOUTIQUE_PHONE_SAFE.md`.
