# Sassy Closet shop tooling

GitHub home for the Excel kit. **Cursor Cloud Agents build here. Kit syncs files to OneDrive.**

The shop’s live working copy is **not** this repo. It is:

`Documents/Sassy Closet/Sassy_Closet_Track.xlsx` on OneDrive

Cute / pink / emoji / phone Excel is **retired**. Website `https://sassy-closet.vercel.app` is GF intake. The plain workbook is a floor tracker for teammates. Square Free stays on-hand inventory truth.

## How Mini Boss launches Agents here

1. Open this repo: [SkyLanter/Sassy-closet](https://github.com/SkyLanter/Sassy-closet).
2. Start a **Cursor Cloud Agent** on `main` (Cursor → Agents, or the Cloud Agent composer pointed at this repo).
3. Paste **one** task from [`excel-kit/PROMPTS.md`](excel-kit/PROMPTS.md) (plain data rebuild, Official row, Wishlist, Order, morning brief, clean demo, Square draft, GF clothes intake).
4. The agent works on a `cursor/…` branch and opens a PR. Mini Boss / Boss review. No Square Save from the agent.
5. After merge, **Kit** syncs the floor tracker to OneDrive `Documents/Sassy Closet/Sassy_Closet_Track.xlsx` (`kit.sh pull`). `Photos/{MA}/` stays links-only. Do not delete other OneDrive files blindly.
6. Never commit live Official rows, customer names, Square tokens, or a filled import CSV.

Boss yes/no stays in Slack `#shop-decisions`. Facebook inbox is the store.

## Shop rules

- **Square Free = on-hand inventory source of truth.** Track stock ON for every item and variation. Wishlist / candidates stay off Square until Boss confirms bought and says yes to Save.
- **Plain Excel** (`Sassy_Closet_Track.xlsx`) is the teammate floor tracker — **not** a second inventory.
- **Photos** live in `Documents/Sassy Closet/Photos/{MA}/`. Excel stores `photo_link` only — **never embed images**.
- **Live mã** = letter + growing digits (`A01`…`A99` then `A100+`). Never invent stock. A02 was renamed to P02 (not P05).
- **Bots draft only.** The owner posts on Facebook, sends the message, takes Zelle, and taps Save in Square.
- **Cursor Cloud Agents** change kit code in this repo. **Kit** syncs generated workbooks to OneDrive.

## Kit

See [`excel-kit/`](excel-kit/) — schema, SoT CLIs, Square headers, prompts.

```bash
pip install -r requirements.txt
python3 excel-kit/build_floor_track.py --out-dir ./out
./excel-kit/kit.sh pull
python3 excel-kit/tests/run_checks.py
```

| Path | Job |
| --- | --- |
| `excel-kit/build_floor_track.py` | Live `/api/export` → `Sassy_Closet_Track.xlsx` |
| `excel-kit/kit.sh` | `pull` / `plain` lands the Boss book (not cute Wishlist) |
| `excel-kit/schema.py` | Headers, mã, Dashboard `B43`, Square import columns |
| `excel-kit/sot/` | Legacy SoT append CLIs; GF intake; morning brief |
| `excel-kit/clean_sot_demo.py` | Demo wipe + Square wording + no embeds |
| `excel-kit/square/` | Headers-only import template (Track ON, mã = SKU) |
| `excel-kit/PROMPTS.md` | Paste-ready Cloud Agent prompts |

Prompts also live in `excel-kit/prompts/BOUTIQUE_DESKTOP_EFFICIENT.md`, `BOUTIQUE_PHONE_SAFE.md`, and `GF_CLOTHES_INTAKE.md`.
