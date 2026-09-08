# Sassy Closet shop tooling

GitHub home for the Excel kit. **Cursor Cloud Agents build here. Kit syncs files to OneDrive.**

The shop’s live working copy is **not** this repo. It is:

`Documents/Sassy Closet/Sassy_Closet_SoT.xlsx` on OneDrive

## How Mini Boss launches Agents here

1. Open this repo: [SkyLanter/Sassy-closet](https://github.com/SkyLanter/Sassy-closet).
2. Start a **Cursor Cloud Agent** on `main` (Cursor → Agents, or the Cloud Agent composer pointed at this repo).
3. Paste **one** task from [`excel-kit/PROMPTS.md`](excel-kit/PROMPTS.md) (Official row, Wishlist, Order, morning brief, clean demo, rebuild, Square draft, GF clothes intake).
4. The agent works on a `cursor/…` branch and opens a PR. Mini Boss / Boss review. No Square Save from the agent.
5. After merge, **Kit** syncs built or cleaned `.xlsx` to OneDrive `Documents/Sassy Closet/` (`Sassy_Closet_SoT.xlsx`, optional lean desktop books, `Photos/` stays links-only).
6. Never commit live Official rows, customer names, Square tokens, or a filled import CSV.

Boss yes/no stays in Slack `#shop-decisions`. Facebook inbox is the store.

## Shop rules

- **Square Free = on-hand inventory source of truth.** Track stock ON for every item and variation. Wishlist / candidates stay off Square until Boss confirms bought and says yes to Save.
- **Official Excel** (`Sassy_Closet_SoT.xlsx`) is the ONE desktop working copy / mã index / captions — **not** a second inventory.
- **Photos** live in `Documents/Sassy Closet/Photos/` named `#001.jpg` / `AO001.jpg`. Excel stores `photo_link` only — **never embed images**.
- **Mã** = `AO` / `QU` / `VA` / `AK` / `GI` / `PK` / `SET` + 3 digits. Never invent stock. Never reuse a Sold mã. Ask Stock (Dashboard `B21:B27`).
- **Bots draft only.** The owner posts on Facebook, sends the message, takes Zelle, and taps Save in Square.
- **Cursor Cloud Agents** change kit code in this repo. **Kit** syncs generated workbooks to OneDrive.

## Kit

See [`excel-kit/`](excel-kit/) — schema, SoT CLIs, Square headers, prompts.

```bash
pip install -r requirements.txt
python3 excel-kit/sot/build_sot_desktop.py --out-dir ./out
python3 excel-kit/build_boutique_desktop.py --out-dir ./out
python3 excel-kit/sot/dashboard_brief.py -w ./out/Sassy_Closet_SoT.xlsx
python3 excel-kit/tests/run_checks.py
```

| Path | Job |
| --- | --- |
| `excel-kit/schema.py` | Headers, mã, Dashboard `B43`, Square import columns |
| `excel-kit/sot/` | Append Official / Wishlist / Orders / Bot_Activity; GF intake; morning brief |
| `excel-kit/clean_sot_demo.py` | Demo wipe + Square wording + no embeds |
| `excel-kit/build_boutique_desktop.py` | Lean Official + Wishlist desktop books |
| `excel-kit/square/` | Headers-only import template (Track ON, mã = SKU) |
| `excel-kit/PROMPTS.md` | Paste-ready Cloud Agent prompts |

Prompts also live in `excel-kit/prompts/` (`BOUTIQUE_DESKTOP_EFFICIENT.md`, `BOUTIQUE_PHONE_SAFE.md`, `GF_CLOTHES_INTAKE.md`, `SAVED_CARD_AND_REAL_MINIBOSS_ASK_2026-09-07.md`).

## Intake site

Next.js app in [`sassy-closet/`](sassy-closet/). Vercel Root Directory: `sassy-closet`. Env **names** (no values): `MINIBOSS_ASK_WEBHOOK_URL`, `MINIBOSS_ASK_WEBHOOK_KEY`, `ASK_REPLY_SECRET`, plus Blob (`BLOB_READ_WRITE_TOKEN` / `BLOB_STORE_ID`) so Production redeploys do not wipe mãs — see `excel-kit/KIT.md` and `sassy-closet/README.md`.
