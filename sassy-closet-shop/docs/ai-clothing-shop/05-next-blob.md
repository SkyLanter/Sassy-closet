# Next.js + Vercel Blob catalogs

## What strong shops do

Vercel Blob caches **public blobs up to a month** unless you set `cacheControlMaxAge` ([Vercel Blob](https://vercel.com/docs/vercel-blob)). Their upload guide is explicit: **treat blobs as immutable**; overwriting the same path leaves stale CDN copies for up to ~60s. Product photos should use `addRandomSuffix: true`. A **single mutable catalog JSON** is the documented exception — set a short `cacheControlMaxAge` and re-read after write ([How to upload and store files](https://vercel.com/kb/guide/how-to-upload-and-store-files-with-vercel)).

Next.js 16 `revalidateTag(tag, "max")` marks tagged data stale; the next visit refreshes ([revalidateTag](https://nextjs.org/docs/app/api-reference/functions/revalidateTag)). For sell-ops, we also `revalidatePath` the shop + admin routes and force-dynamic HTML so Add/Edit is not racing a static shell.

Prefix the pathname with `SITE_ID`. Official and test can share an account without clobbering `{id}/catalog.v1.json`.

## What we already had

- Catalog JSON: `allowOverwrite: true`, `cacheControlMaxAge: 0`, read-after-write.
- Images: `addRandomSuffix: true` under `{SITE_ID}/products/{ma}`.
- `refreshShop` → `revalidateTag(..., "max")` + path busts.

## Applied here

- Catalog document may carry `updatedAt` (ISO). Writes stamp it. Health reports it.
- Contract smoke asserts the Blob put uses `cacheControlMaxAge: 0` (no month-long stale catalog).
- Reads use Blob `get(pathname, { useCache: false })` first. Save verifies via that path (or the put URL), not list-only. List is paginated fallback.

## Deliberately not applied

- Random suffix on `catalog.v1.json` (the official handoff path must stay stable).
- Inventing a shop hostname when `NEXT_PUBLIC_SHOP_URL` is empty.
