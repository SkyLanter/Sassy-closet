# 05 — AI product media (APPLY on sell-test)

Learn note from Official [PR #23](https://github.com/SkyLanter/Sassy-closet/pull/23). Applied on this sell-test `/admin` only. **Do not write Excel, OneDrive Photos/, or intake.**

Media **attaches** to a piece the shop already has. It does not mint stock.

## Hard stops

- Never invent a mã from a photo pipeline.
- Never invent a colorway, a hex for the customer, a price, or a qty.
- `colorId` is `null` **or** a slug already on **that** mã.
- `P02` / `P05` stay Hold. A pretty gallery does not release $23.
- HQ folders stay flat (`001.jpg`). Do not copy OneDrive paths onto the shop. Shop `src` stays `/products/{MA}/cover.jpg` (or a Blob upload URL).

## Recorded hub slugs (the ten)

| Mã | Slugs | Notes |
| --- | --- | --- |
| A01 | `kem`, `xanh` | Two colorways. Cover stays `colorId` null until tagged |
| S01 | `kem` | Do not add `xanh` to match A01 |
| P01 | `hoa` | Pattern name, not a hue |
| P02 | `do` | **Hold** |
| P03 | `den`, `do` | Do not auto-map file order to colors |
| P04 | `kem` | |
| P05 | `hong`, `do`, `xanh` | **Hold**. Three colors + three files is a coincidence, not a mapping |
| K01 | *(none)* | `colorId` stays null. Do not invent `den` |
| H01 | *(none)* | `colorId` stays null |
| A02 | `cham-bi` | Keep the hub slug. Do not rename to `trang` |

Admin on these ten: tag photos to a recorded slug, or leave null. Do not Add/Remove color rows.

Boss Add (A03+) is a separate path. Extra mãs may use generated `c…` ids. Media still cannot invent a hub slug that is not on that piece.

## Record shape

```json
"images": [{ "src": "/products/A01/cover.jpg", "colorId": null, "order": 1 }]
```

`order` is 1…n after Save. Reorder changes `order` only.

## Shop

Gallery is tagged ∪ untagged **this mã**. Empty = `—`. Paper/gold lightbox + motion stay. Message-first. Dropship.

## Not applied

Higgsfield generation, writing `Documents/Sassy Closet/Photos/`, Square image attach, intake CSV, auto-binding P05 001/002/003.
