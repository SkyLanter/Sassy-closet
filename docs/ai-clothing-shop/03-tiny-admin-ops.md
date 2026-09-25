# Tiny admin ops

A 10-piece closet needs a **merchandiser**, not a PIM. Unique-piece studios keep one record that the public site reads ([Art.industries](https://art.industries/) — “write once, read everywhere”; [makers](https://art.industries/makers) — photos, price, location, status). Handmade tools warn that the same unique SKU sold on two channels is an impossible fulfill ([Nventory](https://nventory.io/solutions/industries/handmade-crafts-inventory)).

Sassy already split brains on purpose:

| Brain | Job |
| --- | --- |
| Square Free | On-hand SoT (Track ON). Boss Save only. |
| Official Excel | Working copy / mã index / captions |
| Sell-test `/admin` | Public lookbook fields + Blob images |
| Facebook inbox | The actual store |

Admin must not become a fourth inventory.

## What sell-test admin already gets right

Observed on [sassy-closet-shop.vercel.app/admin](https://sassy-closet-shop.vercel.app/admin):

- Not in the main nav (“Test only”).
- **Back to shop** — admin↔shop link.
- Storage: **Vercel Blob** (durable), not `/tmp`.
- Qty **always 1**.
- New items start **Hold**.
- Fields: EN/VN title, EN/VN description, Available vs Hold · Inbox for price, price USD, hex colors, image URL or upload tagged to a color.
- **Save A01** (explicit button per mã).

## What it gets wrong (apply)

1. **Next-mã tiles invent codes** (A03, Q01, V01, K02, G01, B01, P06, H02, J01, S02, O01, D01). Disable **Add item** minting on sell-test. New mãs are Stock/Boss only. See allowlist.
2. No visible **save result**. If Blob `put` fails, the editor must say so (see silent save).
3. No **export** control. Kit cannot clone Official from HTML scraping forever — sibling export agent + [validator](../../excel-kit/sot/validate_sell_catalog_export.py).
4. Admin is public (no password). **Keep it that way** (hard stop: no passwords). Mitigate with `noindex`, obscurity of `/admin`, and “test only” — not Basic Auth.

## Tiny-admin checklist (keep it tiny)

Must have:

- Edit the 10 allowlist rows.
- Hold / Available / Inbox for price.
- Per-color hex + tag images.
- Upload or URL → Blob.
- Explicit Save + toast/error.
- Back to shop + (optional) discreet shop→admin link in footer for Boss, still off the main nav.
- Storage badge: durable Blob vs ephemeral.

Must not have:

- Customer PII, order desk, Zelle capture.
- Square Save, stock counts other than 1.
- Role/password matrix.
- Bulk “generate 20 SKUs.”
- Intake tabs (those live on `sassy-closet.vercel.app`).

## After each Save

Call `revalidatePath` for `/`, `/m/{ma}`, `/c/{slug}`, `/admin` so the prerendered grid does not keep the old price ([Next.js `revalidatePath`](https://nextjs.org/docs/app/api-reference/functions/revalidatePath), [caching guide](https://nextjs.org/docs/app/guides/caching)). Admin is already `no-store`; the **storefront** is the stale one.
