# Tìm mã find-by-code box + full info card — Boss 2026-09-08 ~12:00 AM PT

Site job for https://sassy-closet.vercel.app. **Existing four tabs only.** Do not add another top-level tab. Stack on Saved card + Ask (PR #9).

Shop law (unchanged): no Post / Send / Square Save. Never invent mã, qty, $, or storage. Bots draft only. Facebook inbox is the store. Square Free = on-hand SoT.

## Tìm mã · Find tab — two boxes, both stay

1. **Code find box** (new) — type / paste mã (e.g. A01), Enter or **Tìm**.
2. **Color detect / find-by-photo box** (existing) — drop or choose a saved photo. Do **not** remove or replace this UX.

Place the code box **above** (phone) or beside (wide) the photo box.

## Full info card — NO new tab

Valid mã → modal / bottom sheet (same Done / ✕ close pattern as **Saved · Đã lưu**).

Intake / staged from the **site store** (never invent):

- Big mã
- kind, colors, sizes
- cost / sell **if present**
- source_link
- notes
- photo thumbs if any
- **Copy mã**
- **Copy link** — `/?ma=…` (Sửa)
- **Copy caption starter** — mã on line 1
- optional **Open in Sửa**

On-hand block:

- per size + color: `qty_on_hand` + status `on_hand | reserved | sold | dead`
- where stored = `Documents/Sassy Closet/Photos/{ma}/` (+ `storage_location` / notes if in the model)

Missing data = empty / **—** / **Staged only — not on Square On_Hand yet**.

## API

Read-only `GET /api/ma/{code}`:

- normalize trim + upper
- `{ staged, on_hand, staged_only }`
- 404 → UI soft **Không tìm thấy mã**
- `on_hand` is only rows actually stored. Empty array if the app has no Square / Official on-hand. **Do not fake Square Free counts.**

## Hard stops

- No invent mã / qty / $ / storage
- No Square Save
- No Facebook Post / Send
- No secrets in repo
- No Production promote
- No wipe live store
- Keep Saved · Đã lưu + Ask working
- Keep find-by-photo / color detect

## Success

- Code box + photo box both present on Tìm mã
- Valid mã opens the full card sheet
- Empty on-hand is honest staged-only
- `npm test` / `typecheck` / `build` pass
- Boss checks Preview / PR before merge. Do not merge. Do not touch Production.
