# Next.js + Blob catalog patterns

Sell-test is a Next.js app on Vercel with **Vercel Blob** as the merchandising store (“Storage: Vercel Blob” on `/admin`). Intake in this repo already uses the same idea (`sassy-closet/lib/store-backend.ts`: `store.json` + `photos/` prefix, `put(..., { addRandomSuffix: false, allowOverwrite: true })`).

## Official building blocks

| Need | Source |
| --- | --- |
| Create store, `BLOB_STORE_ID` + OIDC, `BLOB_READ_WRITE_TOKEN` fallback | [Server uploads](https://vercel.com/docs/vercel-blob/server-upload) |
| Private vs public chosen **at create time** | [Private storage](https://vercel.com/docs/vercel-blob/private-storage) |
| Product images can be public URLs; contracts stay private | [How to upload and store files](https://vercel.com/kb/guide/how-to-upload-and-store-files-with-vercel) |
| `next/image` + Blob hostname | [Blob GA](https://vercel.com/blog/vercel-blob-now-generally-available) |
| Server upload body **4.5 MB** — larger files need **client** uploads | Server uploads doc |
| After write: `revalidatePath` | Same + [revalidatePath](https://nextjs.org/docs/app/api-reference/functions/revalidatePath) |
| Home prerender vs admin `force-dynamic` | [Caching guide](https://nextjs.org/docs/app/guides/caching) |

## Pattern that works for a 10-piece closet

```
Blob
  shop/catalog.json          # the 10 allowlist rows (or one JSON per mã)
  shop/products/A01/cover    # bytes; pathname stable
  shop/products/A01/02
public/editorial/*           # brand stills (git) — OK
public/products/*/cover.jpg  # seed fallback ONLY if Blob empty at first boot
```

Rules:

1. **Stable pathnames.** `addRandomSuffix: false` so `/m/A01` does not 404 after every Save. Intake already does this.
2. **Overwrite with allowOverwrite.** Unique piece photos replace in place.
3. **Catalog JSON is the index.** Images are bytes. A CSV export without bytes cannot restore a wipe (intake README already says this).
4. **Public Blob or `/api/photos` proxy.** Pick one. Mixing private Blob + raw `<img src=blob>` without a proxy is a silent broken-image bug.
5. **Do not use `/tmp`.** Intake Production already lost mãs that way (`sassy-closet/README.md`). Same failure if shop admin writes disk on serverless.
6. **Hobby caps.** 1 GB / 10k reads / 2k writes (intake README). Boutique volume fits; a leaky ISR that re-reads Blob on every bot hit will not.

## Caching (this shop, specifically)

Headers on 2026-09-09: `/` is prerendered (`x-nextjs-prerender: 1`); `/admin` is `no-store`.

So:

- Admin Save **must** `revalidatePath('/')`, `revalidatePath('/m/' + ma)`, `revalidatePath('/c/' + slug)`, and tag `catalog` if you use `unstable_cache`.
- `revalidatePath('/blog')` style mistakes: you must pass the **route file** path (`/m/[ma]` + `type: 'page'` or the literal `/m/A01`). Rewrites need the destination path (Next docs).
- Time-based ISR (`revalidate = 60`) without on-demand bust = **Hold price still showing $25** after a Save. That is a silent-save cousin.

## Env (names only — never commit values)

Shop and intake both need Blob **names**:

- `BLOB_READ_WRITE_TOKEN`
- `BLOB_STORE_ID`
- optional `BLOB_ACCESS` (`private` default)

Do **not** share the intake store with the shop unless Boss says so. Two stores beat one `store.json` that intake migrate logic could overwrite. Intake migrate copies local → Blob **only if Blob is empty** — a shop seed written into the same store is seed drift.

## Client vs server upload

Garment photos often exceed 4.5 MB. Follow Vercel: **client upload** for phone photos; server `put` for tiny covers / JSON. Apply list: if admin “Upload image” fails on a 6 MB iPhone shot, that is the 4.5 MB limit, not a “need passwords” problem.
