# Kit watcher — From GF (thin)

No daemon ships in this repo. **Kit** (on the shop machine / OneDrive sync host) scans periodically.

**PRIMARY inbox:** `Documents/Sassy Closet/From GF/`  
GF uploads herself via Boss’s **Share → Can edit** link (not Graph `item.webUrl`). Slack `#shop-intake` / Boss-paste / email are backups. Do not watch Messenger. Do not watch Dial Bot.

**Links:** raw `https://onedrive.live.com?cid=&id=` (no `/?` after `.com`, unencoded `!`) often **404s** — that is the Graph webUrl shape Boss hit. Canonical patterns + helper: [`../templates/from_gf/LINKING.md`](../templates/from_gf/LINKING.md). Kit:

```bash
python3 excel-kit/sot/onedrive_from_gf_link.py --web-url 'https://onedrive.live.com?cid=…&id=…'
```

Guest share stays manual. Prefer Graph `createLink` type=edit when credentials already exist; this repo has none — never invent `1drv.ms` tokens.

## What to scan

Every 5–15 minutes (or on OneDrive change):

1. List folders under `Documents/Sassy Closet/From GF/`.
2. Skip: `HOW_TO_UPLOAD.md`, `LINKING.md`, root `INTAKE_TEMPLATE.txt`, `examples/`, `_applied/`, `_error/`, files that are not packets.
3. A **packet** is a folder with `INTAKE_TEMPLATE.txt` and/or `note.txt`, plus optional photos (`.jpg` / `.jpeg` / `.png` / `.webp` / `.heic`).
4. Skip a packet if it already has `_applied.txt` or lives under `_applied/`.

## What to run

```bash
python3 excel-kit/sot/gf_intake_apply.py \
  --from-gf "$PACKET" \
  -w "$SASSY_SOT" \
  --photos-out "$HOME/OneDrive/Documents/Sassy Closet/Photos"
```

Use `--dry-run` first if Kit wants a parse-only pass. Dry-run must not write the xlsx and must not copy photos.

On success:

- Copy the printed **Boss → GF** draft to Boss (Slack DM or `#shop-intake` as backup). Boss confirms to GF.
- If the CLI printed **ASK STOCK**, ping Stock (Dashboard `B21:B27`). Do not mint mã.
- Move or stamp the packet (`_applied.txt` + date) so the next scan skips it.
- Paste OneDrive **Photos/** share URLs into `photo_link` when ready. Never point SoT at `From GF/`.

On exit 2: leave the packet, write `_error.txt` with stderr, notify Mini Boss. Do not invent fields.

## Never

- Square Save, Facebook post, Zelle
- Invent mã
- Treat Wishlist `bought` as on-hand
- `#shop-decisions` is still required before Boss taps Save in Square
