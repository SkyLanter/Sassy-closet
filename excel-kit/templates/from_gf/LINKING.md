# From GF OneDrive links (Boss / Kit / Mini Boss)

GF uploads herself to `Documents/Sassy Closet/From GF/`. She needs a **working**
link. Guest Share is still **manual**. Never invent `1drv.ms` / `authkey` tokens.

Shop law unchanged: no Square Save, no invent mã, no live inventory in git.

---

## What failed

Microsoft Graph `item.webUrl` for this personal folder looks like:

```
https://onedrive.live.com?cid=7a74d53e91d4f05f&id=7A74D53E91D4F05F!sae89effd79104c01a63f092754d1c9f9
```

Boss hit that browse URL and it **404s**. Two bugs in the same string:

1. **No slash after `.com`** — it must be `https://onedrive.live.com/?cid=…` (`/?` before the query). Raw `onedrive.live.com?cid=&id=` often 404s.
2. **Unencoded `!` in `id`** — personal resid is `CID!item`. Encode `!` as `%21`.

Do **not** paste Graph `webUrl` to GF (or into Slack) until it has been canonicalized **and** the folder is shared Can edit.

---

## URL patterns (personal OneDrive folders)

Owner-browse (signed-in Boss). Canonical form:

```
https://onedrive.live.com/?cid={cid}&id={CID}%21{item}
```

Worked example (same folder as the failed Graph webUrl):

```
https://onedrive.live.com/?cid=7a74d53e91d4f05f&id=7A74D53E91D4F05F%21sae89effd79104c01a63f092754d1c9f9
```

### Path / GUID alternatives (also have `/?`)

Graph **search** sometimes returns a GUID `id` (from the `{guid}` in eTag) **with** the slash:

```
https://onedrive.live.com/?id={guid}&cid={cid}
```

Example:

```
https://onedrive.live.com/?id=ae89effd-7910-4c01-a63f-092754d1c9f9&cid=7a74d53e91d4f05f
```

`redir` (slash is in the path; still encode `!`):

```
https://onedrive.live.com/redir?resid={CID}%21{item}
```

Signed-in owner path-style (WebDAV host; not a guest share):

```
https://d.docs.live.net/{cid}/Documents/Sassy%20Closet/From%20GF
```

Optional folder hint:

```
https://onedrive.live.com/?cid={cid}&id={CID}%21{item}&ithint=folder
```

Work / school OneDrive (SharePoint) uses a different host — path-based, not `cid=`:

```
https://{tenant}-my.sharepoint.com/personal/{user}/_layouts/15/onedrive.aspx?id=/personal/{user}/Documents/Sassy%20Closet/From%20GF
```

This shop’s From GF folder is **personal** (`driveType=personal`). Prefer the `onedrive.live.com/?` forms above.

---

## Prefer Graph `createLink` (edit) — never invent tokens

When Graph/MSAL credentials **already exist** (none in this repo today):

```
POST https://graph.microsoft.com/v1.0/me/drive/items/{item-id}/createLink
Content-Type: application/json

{"type": "edit", "scope": "anonymous"}
```

Use `link.webUrl` from the JSON (usually `1drv.ms`). That is the GF link.

- `type` must be **`edit`** so GF can drop photos (view-only share is the wrong permission).
- **Never** invent a share token, `authkey`, or fake `1drv.ms` path.
- Do not commit live share URLs or tokens in git.

This kit does **not** ship client secrets, passwords, or MSAL env names. Helper prints the Boss steps and exits 0.

---

## Boss steps (guest share — send this to GF)

Do this once on the real From GF folder:

1. Open **From GF** in OneDrive (browser or app) while signed in. If a pasted URL 404s, run the helper below or use **My files → Documents → Sassy Closet → From GF**.
2. **Share**.
3. Permission **Can edit** (not Can view).
4. **Copy link**.
5. Send **that** copied link to GF (and keep it for Kit). Slack `#shop-intake` is backup if OneDrive is awkward.

GF then follows [`HOW_TO_UPLOAD.md`](./HOW_TO_UPLOAD.md). Looking vs bought still **chưa lên Square**.

---

## Helper (Kit / Mini Boss)

```bash
python3 excel-kit/sot/onedrive_from_gf_link.py --help

# Graph webUrl that 404'd — prints canonical browse + Share steps (exit 0, no secrets)
python3 excel-kit/sot/onedrive_from_gf_link.py \
  --web-url 'https://onedrive.live.com?cid=7a74d53e91d4f05f&id=7A74D53E91D4F05F!sae89effd79104c01a63f092754d1c9f9'

python3 excel-kit/sot/onedrive_from_gf_link.py \
  --cid 7a74d53e91d4f05f \
  --item-id '7A74D53E91D4F05F!sae89effd79104c01a63f092754d1c9f9'
```

Canonical browse is for **Boss signed in**. GF still needs the **Share → Can edit** copy. Watcher notes: [`../../sot/FROM_GF_WATCH.md`](../../sot/FROM_GF_WATCH.md).
