# Admin access

Customers never get the shop desk. `/admin` and `/api/admin` stay locked until both of these environment variables are set on the Vercel project **sassy-closet-shop** (Production, and Preview if you want to sign in on a preview):

- `ADMIN_PASSWORD`
- `ADMIN_SESSION_SECRET`

Vercel → that project → Settings → Environment Variables. Paste the values there. Do not put them in git, chat, or this file. There is no default password. If either name is missing or blank, the desk stays locked.

## Sign in

1. Open `/admin/login` on the shop (production: `https://sassy-closet-shop.vercel.app/admin/login`).
2. Enter the password.
3. The browser keeps a cookie for about 30 days.
4. Use **Sign out** on any admin page when you are done.

A wrong password does not open the desk. After 5 failed tries from the same IP within 10 minutes, that IP has to wait 10 minutes. Each failure also waits briefly. The counter lives in one server instance, so a fresh Vercel instance starts over. The wait still applies on every failure.

## Session cookie

- Name: `sc_admin`
- httpOnly, Secure, SameSite=Lax, Path=/, Max-Age 30 days
- Body is a version and an expiry. It is signed with HMAC-SHA256.
- The MAC key is `HMAC-SHA256(ADMIN_SESSION_SECRET, ADMIN_PASSWORD)`. Changing either variable signs every browser out. The secret is not derived from the password alone, so the password by itself cannot forge a cookie.

Password checks hash both sides with SHA-256 and then `timingSafeEqual`. That avoids the length short-circuit in unmerged PR #60 (`length` check before `timingSafeEqual` on the intake receiver). This shop does not add that receiver.

## What customers still see

Home, `/m/<mã>`, search, category tabs, Messenger, and photos are unchanged and do not ask for this cookie. The gold dot and the logo long-press render only when the cookie is valid. Logged-out HTML does not include them.

## Girlfriend intake

The intake app (`sassy-closet`, https://sassy-closet.vercel.app) does not call this shop. Nhung’s saves stay on the intake app’s own routes (`/api/submissions`, `/api/photos`, `/api/ma`, `/api/find-ma`, `/api/ask`).

The optional dataset-sync webhook is configured only on the **intake** project:

- `INTAKE_DATASET_SYNC_WEBHOOK_URL`
- `INTAKE_DATASET_SYNC_WEBHOOK_KEY`

This shop does not read those names. If that URL points somewhere else, this change does not alter it. Unmerged PR #60 proposed `POST /api/intake/receive` with `INTAKE_RECEIVE_KEY`. That route is not on `main`, and this change does not add it.

After you sign in, the desk can still read the intake site’s public `GET /api/submissions`. Host override, if the intake app moves: `INTAKE_SITE_URL`.

## Revalidate scripts

There is no cron on this shop. `scripts/apply-dataset-fix-batch1.ts` and `scripts/apply-price-bump-20.ts` POST `/api/admin/revalidate` with no token. They now get **401** until the request sends the `sc_admin` cookie from a signed-in browser. Do not add a fallback password.

`GET /api/health`, product photos, and share-card routes stay public.

## Search engines

`robots.txt` disallows `/admin` and `/admin/`. Admin responses send `noindex, nofollow` (page metadata and `X-Robots-Tag`).

## Surfaces this lock covers

Pages (logged out → redirect to `/admin/login`, except the login page itself):

- `/admin`
- `/admin/new`
- `/admin/edit/<mã>`
- `/admin/settings`
- `/admin/intake`
- `/admin/pipeline`

APIs (logged out → 401, except sign-in):

- `GET /api/admin/catalog`
- `GET` and `POST /api/admin/catalog/export`
- `GET` and `POST /api/admin/catalog/import`
- `GET` and `POST /api/admin/add`
- `GET` and `POST /api/admin/save`
- `GET` and `POST /api/admin/rename`
- `GET` and `POST /api/admin/remove`
- `GET` and `POST /api/admin/settings`
- `GET` and `POST /api/admin/hold`
- `GET` and `POST /api/admin/revalidate`
- `POST /api/admin/logout` (401 when logged out; the response still clears a bad cookie)
- `POST /api/admin/login` is the sign-in route. `GET` there is 405.

Server actions in `app/admin/actions.ts` (save, add, rename, remove, settings, export, import, bulk hold, photo upload, intake pull, pipeline) also require the session. A server-action POST without the cookie is 401.

Hidden toggles that used to be public, now session-only:

- Floating button “Công cụ shop · Shop tools” (gold dot)
- Logo long-press (about 700ms) opening that same sheet

There is no `?admin=` query switch and no localStorage admin flag. Customer `sessionStorage` for the ship-address draft is unchanged.
