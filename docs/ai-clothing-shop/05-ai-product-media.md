# 05 — AI product media for clothing shops

Learn track (Ultra burn): fashion product photography and media pipelines that stay honest about **what the garment is**, **which color is in the frame**, and **which mã the file belongs to**.

This lesson is about **attaching** pictures and short motion to pieces the shop already has — not about generating a catalog. If a file cannot be pointed at a real mã + a recorded color (or honestly left unassigned), it does not enter sell-test admin.

**Hard stops (same as the rest of the shop):**

- Never invent a mã.
- Never invent a colorway, a hex swatch, a price, or a qty.
- Never Square Save from a bot, an agent, or a media pipeline.
- Never Facebook Post / Send from a bot. Owner posts from the inbox.
- Never replace a high-quality (HQ) original with an AI derivative and pretend the derivative is the original.
- Never treat Wishlist / intake / “next mã” as permission to mint stock.

Sell-test allowlist for this lesson — **these ten only**:

`A01` · `S01` · `P01` · `P02` · `P03` · `P04` · `P05` · `K01` · `H01` · `A02`

Do not write `A03`, `P06`, `Q01`, `AO001`, or any other code in admin, folders, or JSON. If a new piece arrives, Stock / Boss assigns the mã on the hub first. Media follows. Media does not lead.

---

## 0. What this lesson is for

A clothing shop lives or dies on **color and drape**. Shoppers buy from a grid. If `A01` Kem and `A01` Xanh were lit differently, cropped differently, or generated from a prompt that “improved” the fabric, the grid looks sloppy and returns go up. Ecommerce photography guides treat this as a **returns problem before it is an aesthetic problem**: color that drifts between colorways is the garment the customer does not receive ([On-Model, 2026](https://on-model.com/blog/ecommerce-photography-guide); [Wearview, 2026](https://www.wearview.co/blog/consistent-product-images-guide)).

AI tools (Higgsfield-class product stills, virtual try-on, image-to-video) are useful **after** a real photograph exists. They are dangerous as a **source of product identity**. U.S. law does not need a special “AI photo statute” to punish a misleading garment picture. Section 5 of the FTC Act already bars deceptive acts in commerce. A photorealistic render that shows a sheen, fit, or color the physical piece does not have is a visual claim about the product ([FTC Operation AI Comply, 2024-09-25](https://www.ftc.gov/news-events/news/press-releases/2024/09/ftc-announces-crackdown-deceptive-ai-claims-schemes); fashion-team commentary in [Style3D](https://www.style3d.com/blog/truth-in-advertising-for-ai-product-renders-for-fashion-teams/) and [AI Fashion Law](https://www.aifashionlaw.com/article/ftc)).

This shop also has a **second** law that AI cannot override: **mã discipline**. Intake, Excel, Square drafts, and sell-test all refuse invented codes ([repo `README.md`](../../README.md); [`excel-kit/schema.py`](../../excel-kit/schema.py) `ASK_STOCK_MA`; [`sassy-closet/lib/store.ts`](../../sassy-closet/lib/store.ts) `resolveSaveMa`; sell-catalog allowlist in the kit contract cited in §7 and Sources).

Read this lesson as a pipeline:

```
HQ photograph of the real piece
    → lock lighting + camera for that session
    → one set of views per recorded color (not per imagined color)
    → optional AI restyle / try-on / short motion, tagged as derivative
    → attach file to existing mã + existing colorId (or colorId null)
    → sell-test /admin stores the bind, does not mint a product
```

If any arrow would require inventing a product, stop.

---

## 1. Three surfaces, two mã alphabets, one photo root

Do not mix these. Media bugs in this shop usually start as a **surface mix-up**.

| Surface | URL / path | Mã alphabet | Photo job | This lesson |
| --- | --- | --- | --- | --- |
| Intake (GF) | https://sassy-closet.vercel.app | Letter + 2 digits (`A01`) | Stage photos on a submission. `photo_paths` like `A01/001.jpg`. `pieces[]` exists in types but the live form currently saves `pieces: []` ([`IntakeApp.tsx`](../../sassy-closet/components/IntakeApp.tsx)) | Do not treat intake `/admin` CSV as the sell catalog |
| Sell-test shop | https://sassy-closet-shop.vercel.app · `/admin` | Same A01-style **allowlist of ten** | Customer tiles. catalog.v1 `images[{src, colorId, order}]` | **APPLY target** |
| Official Excel / Square drafts | `Documents/Sassy Closet/Sassy_Closet_SoT.xlsx` | Legacy `AO001` / `PK001` / `SET001` until the A01 handoff ([`schema.py`](../../excel-kit/schema.py) `MA_RE`, comment on A01 cutover) | `photo_link` **text only**. Never embed images | Do not write AO-codes into sell-test |
| HQ disk | `Documents/Sassy Closet/Photos/{MA}/` | Folder name = mã | Bytes of record | Source of truth for files |

Shop law on photos ([`README.md`](../../README.md), [`schema.py` `PHOTO_RULE`](../../excel-kit/schema.py), [`DESIGN_NOTES.md`](../../excel-kit/DESIGN_NOTES.md)):

> Photos live in `Documents/Sassy Closet/Photos/`. Excel stores `photo_link` only — never embed images.

Intake persists bytes on **Vercel Blob** (or local `data/photos/`) under `{ma}/{001}.jpg` and points `photo_link` at the OneDrive folder ([`store.ts`](../../sassy-closet/lib/store.ts) `photo_link: Documents/Sassy Closet/Photos/${ma}/`). Tests refuse to invent extra paths ([`photos.test.ts`](../../sassy-closet/tests/photos.test.ts), [`find-ma-card.test.ts`](../../sassy-closet/tests/find-ma-card.test.ts) “staged photo_paths stay as stored — never invent extra files”).

Sell-test catalog.v1 (kit sell-catalog lane, Boss 2026-09-09) already has the **hook** this lesson fills:

```json
"images": [{ "src": "Documents/Sassy Closet/Photos/A01/001.jpg", "colorId": null, "order": 1 }]
```

Today every exported image is `colorId: null`. That is honest: the HQ folders are **flat** (`001.jpg`, not `kem/001.jpg`), and nobody has verified which file is Kem vs Xanh. APPLY (§8) is how `/admin` should store the bind **without inventing a product or a color**.

Square, when Boss later Saves a library row, can attach a `CatalogImage` to a `CatalogItem` **or** a `CatalogItemVariation`. The first id in `image_ids` is the primary image in POS and Square Online ([Square Catalog API — Upload and Attach Images](https://developer.squareup.com/docs/catalog-api/upload-and-attach-images)). Shop rule for variations is already “Asia size + color” (`M / đen`) and `SKU = mã` ([`excel-kit/square/README.md`](../../excel-kit/square/README.md)). Per-color media belongs on the **variation** (or on sell-test `colorId`), not on a new mã.

---

## 2. Consistent lighting

### 2.1 Why catalogs fail

Shoppers do not inspect one hero. They scan a grid. Frame size, white point, and key-light direction that wander from tile to tile read as “different shops,” then as “different garments” ([On-Model](https://on-model.com/blog/ecommerce-photography-guide); [FrameOnce catalog consistency](https://frameonce.io/blog/catalog-photography); [Pixofix, visual consistency at scale](https://www.pixofix.com/blog/visual-consistency-at-scale-fashion-ecommerce)).

The five variables to lock for a fashion grid ([Wearview](https://www.wearview.co/blog/consistent-product-images-guide)):

| Variable | Lock | Failure this shop must not ship |
| --- | --- | --- |
| Lighting | Same key angle, softness, Kelvin | Window light Tuesday, strobe Friday — Kem looks warm, Xanh looks cold, buyer thinks they are different fabrics |
| Background | One seamless or one scene | Slightly different greys clash in the PLP |
| Framing | Same camera distance, height, aspect | One full-body, next cropped at the hip |
| Color accuracy | Custom white balance + checker | Reds shift; returns |
| Model / stand | Same stand, mannequin, or hanger geometry | AI model changes body and the jacket “fits differently” |

High-volume studios shoot **one composition across all items and colorways**, then change the view — they do not relight between `P03` Đen and `P03` Đỏ ([The Line Studios shot-list guide](https://thelinestudios.nyc/e-commerce-photography-shot-list-guide/)). Fashion ecommerce typically needs **4–6 stills per SKU** (front, back, side or 3/4, detail, texture), not twenty AI variants of the same front.

### 2.2 A locked boutique recipe (write it down, then do not “improve” it)

Higgsfield’s product-photoshoot vocabulary is useful here **as craft language**, not as permission to invent a set. Their own `product-shot` mode defaults to `clean-studio`: seamless white-to-light-grey, soft frontal key, minimal shadow, catalog ratio `1:1` unless the destination implies another ([Higgsfield workflow `product-photoshoot` / `references/product-shot.md`](https://higgsfield.ai) — mode file loaded 2026-09-09). Their photography lexicon forbids vague prompts (“good lighting”) and requires direction, quality, and Kelvin ([`references/photography-vocabulary.md`](https://higgsfield.ai)).

For **this** shop’s HQ stills (phone or camera, real garment), lock one recipe and reuse it for every allowlisted mã in a session:

| Dial | Boutique lock | Why |
| --- | --- | --- |
| Color temperature | **5500K** daylight-balanced (studio standard in the Higgsfield Kelvin table; 5000–5600K in catalog guides) | Auto white balance will make `A01` Kem look peach at 4pm and grey at noon |
| Key | Large soft source, **45° camera-left**, slightly above lens | Classic three-quarter; fabric weave reads; faces (if any) get a nose shadow that is consistent |
| Fill | Bounce camera-right, 1–2 stops under key | Soft falloff, not a second sun |
| Separation | Optional weak hair / rim from three-quarter back | Keeps black garments (`P03` Đen) from melting into a grey sweep |
| Shadow | Soft gradient; contact shadow at the base only | Hard noon sun on one SKU and no shadow on the next breaks the grid |
| Camera | Same height, same distance, same lens-equivalent. Phone: lock AE/AF after a grey card | “Walked two steps closer for the cute one” is how `S01` looks bigger than `A01` |
| Background | One seamless (paper, sheet, or wall) for packshots. Lifestyle is a **second** recipe, not a random bedroom | GF intake photos can be messy; HQ packshots should not inherit that mess |
| File | JPEG/PNG/WebP as the shop already accepts ([`form-save.ts`](../../sassy-closet/lib/form-save.ts) `jpe?g\|png\|webp`). Prefer sRGB | Do not deliver Display-P3 untagged files into Blob and wonder why Kem shifted |

**Do not** change Kelvin to “make Hồng pop” on `P05`. If Hồng looks dull, the garment is dull, or the file is underexposed. Changing the light between colorways is how you invent a product the buyer will not receive.

### 2.3 Session order (real garments)

1. Tape the light stands and the hanger / mannequin feet. Measure key-to-subject once ([FrameOnce](https://frameonce.io/blog/catalog-photography)).
2. Grey card + ColorChecker frame at the start of the session (and again if anything moves). Custom white balance. No auto-WB.
3. Shoot **all recorded colors of one mã** before moving to the next mã. Example: `P03` Đen front → `P03` Đỏ front → then `P03` Đen back → `P03` Đỏ back. That is the Line Studios “moments first” rule applied to a two-color accessory.
4. Then the next mã. Do not interleave `H01` hair pieces into the middle of `A01` unless you are willing to rebuild the stand marks.
5. Shoot 3–5 frames per view; pick one. Do not keep every burst in the HQ folder (see §7).

`P02` and `P05` are **Hold** on sell-test (no public price). Still photograph them if the physical pieces exist — Hold is a **status**, not a reason to skip HQ — but do not invent a $23 tile for `P05` ([sell-catalog contract, Boss 2026-09-09](#sources)).

### 2.4 What AI lighting is allowed to do

| Allowed | Not allowed |
| --- | --- |
| Match an existing HQ still to the locked recipe (same product, same color) | Relight so a cream fabric reads as white, or a wash reads as saturated |
| Even out a messy GF phone snap **of that piece** so it can sit in the grid | Invent a “studio version” of a colorway nobody photographed |
| Lifestyle / campaign stills **labeled as AI** and **not** used as the color-proof hero | Use a dramatic rim-lit render as the only picture of `K01` |

Higgsfield `restyle` is built to change mood/season while **preserving subject, composition, and product appearance** (`references/restyle.md`, quality gate: “no change to product appearance”). If a restyle changes the garment color, it failed the gate. Delete it. Do not attach it to a colorId.

---

## 3. Per-color shots

### 3.1 A color is not a new mã

Shop data model, three layers, same idea:

1. **Intake submission** — one `ma`, `color` as a comma-joined string of chip labels, optional `color_note`, `photo_paths[]` in save order ([`types.ts`](../../sassy-closet/lib/types.ts), [`kinds.ts` `COLORS`](../../sassy-closet/lib/kinds.ts)). `Piece.photos` is an index list into that array, but the live UI currently writes `pieces: []`.
2. **On-hand rows** — `{ size, color, qty_on_hand, status }` per mã. Empty on-hand means **Staged only — not on Square On_Hand yet**. Tests refuse to invent rows from staged colors ([`find-ma-card.test.ts`](../../sassy-closet/tests/find-ma-card.test.ts)).
3. **Sell-test catalog.v1** — `colors: [{ id, name }]` (text only, **no invented hex**) and `images: [{ src, colorId, order }]`. `colorId` must be `null` or an `id` that already exists on **that** product.

Square’s customer-facing analog: one item, many variations, variation name = size + color, SKU stays the mã ([`square/README.md`](../../excel-kit/square/README.md)). Square can attach images to the variation ([Catalog API](https://developer.squareup.com/docs/catalog-api/upload-and-attach-images)). That is “per-color media.” That is **not** “mint `A01-KEM` as a new SKU.”

### 3.2 Recorded colors on the first ten (do not add to this list)

These color **ids** and names come from the live hub export used for catalog.v1 (sample committed on the sell-catalog lane). They are **not** a mood board. If a color is missing here, it is missing on the hub — leave `colorId` null. Do not slug a new id.

| Mã | Kind / sell type | Recorded `colors[].id` | Notes |
| --- | --- | --- | --- |
| `A01` | Áo / top | `kem`, `xanh` | Two colorways. Flat HQ: `001.jpg`, `002.jpg` — **not yet bound** |
| `S01` | Set đồ / set | `kem` | One recorded color. One HQ file: `001.jpg` |
| `P01` | Phụ kiện / accessory | `hoa` | Pattern name, not a hue. Treat `hoa` as the colorId |
| `P02` | Thermos · **hold** | `do` | Hold. Still a real mã. Do not publish a price |
| `P03` | Accessory | `den`, `do` | Two colorways. Three flat files: `001–003.jpg` |
| `P04` | Accessory | `kem` | Two flat files |
| `P05` | Thermos · **hold** | `hong`, `do`, `xanh` | Three recorded colors, three flat files, **all unbound**. Hold |
| `K01` | Áo khoác / jacket | *(none recorded)* | Two `.jpeg` files. **`colorId` stays null** until Boss writes a color on the hub |
| `H01` | Tóc / hair | *(none recorded)* | Three `.jpeg` files. Same rule as `K01` |
| `A02` | Áo / top | `cham-bi` | Pattern (“Chấm bi”), not a chip you invent. Two `.jpeg` files |

Chip vocabulary the intake UI already knows (`den` Đen, `trang` Trắng, `kem` Kem, `xanh` Xanh, `do` Đỏ, `hong` Hồng, `hoa` Hoa, …) lives in [`kinds.ts` `COLORS`](../../sassy-closet/lib/kinds.ts). `cham-bi` is a hub slug, not in that chip list — **keep the hub slug**. Do not rename it to `trang` or `den` because a model “sees” dots on a light ground.

### 3.3 What “one colorway set” means

For a mã that **has** recorded colors, the customer needs to see **that** color in the hero when they tap the chip. Industry default: repeat the **same** views for each colorway (front / back / detail), same lighting ([On-Model](https://on-model.com/blog/ecommerce-photography-guide); [Wearview](https://www.wearview.co/blog/consistent-product-images-guide)).

Worked **non-invention** examples:

- `A01` has Kem and Xanh on the hub. If you only photographed one body in one color, you may attach those files with `colorId: null` (shared gallery) **or** bind them to the color you can prove. You may **not** generate a Xanh twin and call it `A01` Xanh unless the physical Xanh piece was in front of the lens (or a disclosed visualization that is **not** the color-proof hero — see §5 and §6).
- `P05` lists Hồng, Đỏ, Xanh but is Hold. Do not invent three extra mãs (`P06` Hồng…). Do not invent hex `#ff69b4` so the admin swatch looks pretty. Customer colors stay **text** ([CLONE_TO_OFFICIAL / sell-catalog contract](#sources)).
- `K01` and `H01` have HQ files and **empty** `colors[]`. Admin must not invent `den` for the jacket because “jackets are usually black.” Bind nothing. `colorId: null`.

### 3.4 Shot list per recorded color (still)

Minimum useful set for apparel / set / jacket (`A01`, `S01`, `K01`, `A02`):

1. Front hero (packshot, locked recipe).
2. Back or 3/4.
3. Detail (neckline, print, hardware).
4. Texture / fabric macro (no hand in frame if you later cut UGC macros; Higgsfield try-on video forbids hand-on-fabric in those slots).

Minimum for small accessories / hair / thermos (`P01`–`P05`, `H01`):

1. Hero, fill the frame, label/print readable.
2. Second angle or scale (in a hand only if the hand does not hide the color).
3. Optional detail.

Do not pad the set with AI “angle 12 of 12” that was never shot. Empty is honest. Fake volume is a second catalog.

### 3.5 Binding rule (the whole lesson in one sentence)

**A file may join a color only when (a) the mã is allowlisted, (b) the color id already exists on that mã, and (c) a human has seen the pixels and agrees the garment in the frame is that color.**

Otherwise `colorId` stays `null`. Shared / unassigned images are valid. Invented binds are not.

---

## 4. Higgsfield-class tools: what they are good and bad for

“Higgsfield-class” here means: a hosted generate stack with **product-photoshoot**, **virtual try-on stills**, **UGC try-on video**, **Marketing Studio**, and image-to-video models (Kling, Seedance, Genjutsu / motion control, FLUX video, Grok Video, presets). The names below are from Higgsfield’s workflow catalog and `models_explore` as of this writing. Tools move. The **jobs** do not.

Higgsfield’s own product-photoshoot skill is explicit about scope: packshots, lifestyle, closeups, pins, banners, carousels, static ad packs, virtual-model try-on, conceptual CGI, restyle. It **refuses** Amazon-compliance listing sets, video ads, thumbnails, generic portraits, and UGC video (those have sibling workflows). Virtual try-on **requires a source product image** and does **not** remember a model identity between generations (`references/virtual-model-tryout.md`). Restyle **requires** a source and must not change product appearance (`references/restyle.md`).

### 4.1 Good (use, then tag as derivative)

| Job | Tool / mode | Why it is safe *enough* for this shop |
| --- | --- | --- |
| Clean packshot from a real HQ still | `product-photoshoot` → `product-shot` / `clean-studio`; model locked to `nano_banana_pro` + image reference in that workflow | Same product identity; lighting language is specific (45°, Kelvin, shadow behavior) |
| Even a messy phone snap onto the locked recipe | same, or `restyle` with a **neutral studio** aesthetic — not a seasonal palette shift that recolors fabric | Source required; preservation directive |
| Lifestyle / Pinterest / hero banner **around** the real piece | `lifestyle-scene`, `pinterest-pin`, `hero-banner`, `social-carousel` | Campaign, not color-proof. Still reuse the same product reference for every variant (workflow: one identity across the set) |
| On-model lookbook still | `virtual-model-tryout` / `studio-clean` | Product-fidelity directive: “identical to the reference — same color, material, design.” Model is generated **per batch**, not a stored soul. Disclose (see §4.4) |
| Short fabric motion from a locked still | Image-to-video: Kling 3.0 (`start_image`), Seedance 2.0/2.5 (`omni_reference` / start frame; Seedance 2.0 tags include multi-SKU / e-commerce), Grok Video 1.5, FLUX 3 Video | Motion must not change color or cut. Silent or light SFX. Not a fit guarantee |
| UGC-style try-on **draft** for the owner to post | `ugc-try-on-video` (Seedance clips from a board + **product photo** + creator) | Hard garment-consistency lock in that workflow. Owner posts. Disclose synthetic creator / AI video. **Not** a PDP hero |
| Paid-social static from a registered product | Marketing Studio Image / DTC Ads (`product_ids`, brand kit) | Fine for ads **of an allowlisted mã**. Still not a new SKU |
| Upscale / background remove of an HQ file | Dedicated upscale / `remove_bg` style tools | Do not change hue. Keep the HQ original |

### 4.2 Bad (do not attach to a mã as if it were true)

| Job | Why it fails this shop |
| --- | --- |
| Text-only “cream cardigan, boutique lighting” with **no** photo of `A01` | Invents a garment. Workflow allows text-only products; **we do not**, except maybe a moodboard that never touches admin |
| Recolor `A01` Kem → a new “Đỏ” tile | Invents a colorway. Would require a `do` id on `A01` that the hub does not have |
| Virtual try-on as the **only** picture of `K01` | No recorded color, two HQ jpegs. A generated body is not a color bind and is not on-hand proof |
| Amazon / marketplace “main image + infographic + A+” packs | Product-photoshoot skill: out of scope; compliance sets lie easily (badges, fiber claims) |
| Character sheet / Soul identity as “our house model” on every PDP | Virtual-tryout docs: no identity memory; Soul is a different product. A repeating fake person edges into endorsement territory (§4.4) |
| Faceless narrator / explainer / kids / myth workflows | Wrong object. Those make channel videos, not SKUs |
| Website-builder / brand-kit logo work | Wrong object |
| Ad Multiplier on someone else’s 4–30s ad | Edits people/products in **their** clip. Do not steal motion or imply we own that garment |
| Genjutsu / motion-control onto a random dancing video | Fun. Not a catalog source. Fabric will smear |
| Marketing Studio video hooks (“object flies into frame”) as stock proof | 12–15s ads. Fine as ads. Illegal as “this is the piece in the bin” |
| Generating reviews, captions that claim a fit the owner did not measure, or “customers say” | FTC Operation AI Comply includes **Rytr**: a review-generation feature that invented material details. Fake reviews are not a grey area ([FTC 2024-09-25](https://www.ftc.gov/news-events/news/press-releases/2024/09/ftc-announces-crackdown-deceptive-ai-claims-schemes)) |
| Using AI output to **mint** the next mã because `/admin` shows a Next field | Sell-catalog / clone runbook: do not mint `A03` because admin showed it |

### 4.3 Video specifically (good / bad)

| Good | Bad |
| --- | --- |
| 5–15s loop: real still of `S01`, gentle camera push, fabric breathes, color locked | 30s story that “shows” a second color of `S01` |
| Owner-posted UGC try-on draft, disclosed, Messenger/FB — **bots still do not Send** | Auto-posting AI try-on as if GF wore it |
| Silent motion for a Hold piece (`P02`, `P05`) stored in admin, not merchandised as available | Video tile with a price on Hold |
| Start-frame = HQ hero of that color | Start-frame = a stock model in a similar jacket, then labeled `K01` |

Higgsfield `ugc-try-on-video` is unusually strict (garment lock, no mirrors, no hand-on-fabric macros, no CTA tail). Use those constraints even if you shoot real video: they are good catalog hygiene. Still: **video is not on-hand.** Square Free remains inventory SoT ([`README.md`](../../README.md)).

### 4.4 Truth-in-advertising (the legal floor)

- **FTC Act §5** — unfair or deceptive acts in commerce. A picture is a claim. AI is not an exemption. Chair Khan, announcing Operation AI Comply: “Using AI tools to trick, mislead, or defraud people is illegal… there is no AI exemption from the laws on the books” ([FTC press release, 2024-09-25](https://www.ftc.gov/news-events/news/press-releases/2024/09/ftc-announces-crackdown-deceptive-ai-claims-schemes)).
- **Endorsement Guides** (16 C.F.R. Part 255; staff FAQ) — an endorsement must reflect the honest opinion/experience of the endorser; unexpected material connections must be disclosed **clearly and conspicuously**. Disclosures in videos belong **in the video** (visual if the claim is visual; not only in the description; not only behind a link; not only in comments) ([FTC, *Endorsement Guides: What People Are Asking*](https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking)).
- A **synthetic person** who appears to be a real customer or a real reviewer is the dangerous case. Fashion-law commentary treats photoreal product imagery that does not match the shipped garment as classic §5, and synthetic endorsers as Guide territory ([AI Fashion Law](https://www.aifashionlaw.com/article/ftc); [Nightjar 2026 legal guide](https://nightjar.so/blog/ai-product-photography-legal-guide)). Safer PDP pattern: **real HQ hero** + optional “AI visualization — actual product may differ” on derivatives, next to the image, not in a footer.
- **Do not** generate testimonials. Rytr’s “Testimonial & Review” mode is the government exhibit.

This shop’s public sell-test is Messenger-first, Zelle as a **method word**, no personal name on the site ([CLONE_TO_OFFICIAL](#sources)). AI video does not change that. Owner sends the message.

---

## 5. Attach media to SKU / color without inventing products

### 5.1 Identity chain

```
physical piece
  → Stock/Boss mã (allowlist or later assigned)
    → hub row (sassycloset.xlsx All)
      → colors[] text slugs
        → HQ files in Photos/{MA}/
          → catalog.v1 images[].src
            → sell-test Blob after /admin upload
              → (later, Boss-only) Square image_ids on the item or variation
```

Break any link and you have either a **orphan file** (ok, do not show) or a **fake product** (not ok).

Intake already refuses to invent photos: `realPhotoPaths` drops empties; `buildMaLookup` passes `photo_paths` through unchanged; Blob migrate copies only files that exist ([`photos.ts`](../../sassy-closet/lib/photos.ts), [`store-backend.ts`](../../sassy-closet/lib/store-backend.ts) `copyStoreAndPhotos`). Sell-test must be at least that strict.

### 5.2 What admin may do

| Action | Allowed | Forbidden |
| --- | --- | --- |
| Upload a file onto `A01` | Yes, if `A01` exists | Create `A03` to “have a place for this extra cardigan” |
| Set `colorId` to `kem` on an `A01` image | Yes, if `A01.colors` contains `kem` **and** the pixels are Kem | Set `colorId: "do"` on `A01` |
| Leave `colorId` null | Yes — default for every current HQ file | Invent `unassigned` as a color row |
| Add color `cham-bi` to `A02` | Only if the hub already has it (it does) | Add `cham-bi` to `A01` because the print “looks similar” |
| Duplicate an image onto two colors | Only if the same physical photo honestly shows both (almost never) | One file bound to `hong` and `xanh` on `P05` to “save shooting” |
| Store an AI restyle | Yes, as a **derivative** of an existing src, flagged | Overwrite `Photos/A01/001.jpg` |
| Import catalog.v1 | Yes, allowlist only | Import a JSON that contains `Q01` |

### 5.3 Square (later, Boss Save only)

When a variation exists (`M / kem`):

1. Upload the color-proof still with `CreateCatalogImage`.
2. Attach to that **variation’s** `image_ids` (primary = first).
3. Shared detail shots (hardware that does not change by color) may attach to the **item**.

Do not create a new Square item to hold leftover pictures. Do not put `No` in New Quantity (that kills tracking) ([`square/README.md`](../../excel-kit/square/README.md)). Agents still do not Save.

### 5.4 Intake `pieces[]` (future, not a second catalog)

[`types.ts`](../../sassy-closet/lib/types.ts) already has:

```ts
type Piece = { id: string; photos: number[]; suggested: string[]; color: string; note: string };
```

That is an index into `photo_paths`, not a new mã. If intake ever stops saving `pieces: []`, a piece may point at `[0, 1]` meaning “these two files are the Kem body.” Still one `A01`. Do not mint `A01P2`.

---

## 6. HQ photo folder discipline

### 6.1 What exists today (verified on OneDrive for the allowlist)

Contract table (sell-catalog lane). Skip `_placeholder`, `_probe`, `.keep`, `README`. Do not invent Blob URLs. These paths are **not** public.

| Mã | Real HQ files (flat) | Ext |
| --- | --- | --- |
| `A01` | `001`, `002` | `.jpg` |
| `S01` | `001` | `.jpg` |
| `P01` | `001`, `002` | `.jpg` |
| `P02` | `001`, `002` | `.jpg` |
| `P03` | `001`, `002`, `003` | `.jpg` |
| `P04` | `001`, `002` | `.jpg` |
| `P05` | `001`, `002`, `003` | `.jpg` |
| `K01` | `001`, `002` | `.jpeg` |
| `H01` | `001`, `002`, `003` | `.jpeg` |
| `A02` | `001`, `002` | `.jpeg` |

Excel / kit `photo_link` for a site mã is the **folder**:

`Documents/Sassy Closet/Photos/A01/`

([`on-hand.ts` `photoFolder`](../../sassy-closet/lib/on-hand.ts); Official working-copy also has older `AO001.jpg` / `#001.jpg` names for the SoT book — do not rename live Official files from this lesson).

### 6.2 Folder law

1. **One folder per mã.** Name = mã, exact, upper case. No `a01 copy`, no `A01-final-FINAL`.
2. **Flat `001`…`00n` is legal.** It is what we have. `colorId` lives in catalog JSON / admin, not in the filename, until a human creates a color subfolder **and** moves only files that belong there.
3. **Never put two mãs in one folder.** Never put `S01`’s set shot inside `A01` because they were styled together.
4. **Never embed** images in Excel. Builders strip drawings ([`schema.py` `strip_embedded_images`](../../excel-kit/schema.py); [`DESIGN_NOTES.md`](../../excel-kit/DESIGN_NOTES.md)).
5. **From GF** packets stay in `Documents/Sassy Closet/From GF/{date_name}/` until intake apply copies/renames into `Photos/{MA}/` ([`GF_CLOTHES_INTAKE.md`](../../excel-kit/prompts/GF_CLOTHES_INTAKE.md)). Do not point SoT `photo_link` at `From GF/`.
6. **Do not commit live Official photos or customer bytes** to git. Kit seeds may include tiny example `photo.jpg` files under `templates/from_gf/examples/` — those are not stock.
7. **Skip junk.** `_placeholder.jpg` is not a product. Clone runbook: if a folder is only placeholders, skip; never invent a replacement ([CLONE_TO_OFFICIAL](#sources)).
8. **Keep originals.** If you run AI, write derivatives beside, not over:

```
Documents/Sassy Closet/Photos/A01/
  001.jpg                 ← HQ, never overwrite
  002.jpg
  _ai/                    ← optional; not in catalog unless Boss says
    001_restyle_studio.jpg
    001_i2v_05s.mp4
```

9. **Optional color subfolders — only after a verified bind.** Do not create `Photos/A01/kem/` empty “to be ready.” Empty folders become fake inventory in someone’s head.

```
Documents/Sassy Closet/Photos/A01/
  001.jpg                 ← still HQ; colorId null until tagged
  kem/                    ← create only when a Kem-only shoot exists
    001.jpg
  xanh/
    001.jpg
```

Export can then set `src` to `…/A01/kem/001.jpg` and `colorId: "kem"`. Until those files exist, **do not** pretend `A01/001.jpg` is Kem just because it is first on disk.

10. **Extensions stay real.** `K01` and `H01` and `A02` are `.jpeg` on disk. Do not rewrite them to `.jpg` in JSON. Intake `photoContentType` already maps both to `image/jpeg` ([`store-backend.ts`](../../sassy-closet/lib/store-backend.ts)).

### 6.3 Filename grammar (HQ vs intake vs SoT)

| Lane | Pattern | Example |
| --- | --- | --- |
| Sell-test / hub HQ | `{MA}/{nnn}.jpg` or `.jpeg` | `P03/002.jpg` |
| Intake Blob | `{ma}/{nnn}{ext}` minted on save | `A01/001.jpg` |
| SoT Official (legacy) | `{AO}{nnn}.jpg` or `{AO}{nnn}_{k}.jpg` | `AO001.jpg` — **do not emit this into catalog.v1** |
| Wishlist finds | `#001.jpg` | Not sell-test |

`sanitizePhotoRel` strips `..` ([`store-backend.ts`](../../sassy-closet/lib/store-backend.ts)). Do not invent paths like `A01/../S01/001.jpg`.

### 6.4 Who may write which folder

| Writer | Photos/ | From GF/ | sell-test Blob | Intake Blob |
| --- | --- | --- | --- | --- |
| GF | No (unless Boss shared Photos; they should not need it) | **Yes** — primary ([`HOW_TO_UPLOAD.md`](../../excel-kit/templates/from_gf/HOW_TO_UPLOAD.md)) | No | Via site Lưu |
| Boss / Stock | Yes | Yes | Via sell-test `/admin` upload | Via intake |
| Kit export | Read | No | No | No |
| Agents | No live Official rows; no invented files | No | No (Origin owns shop code) | No Production wipe |

---

## 7. APPLY — how sell-test `/admin` should store per-color images

**Scope:** https://sassy-closet-shop.vercel.app/admin (Blob SoT). Mini Boss’s Origin agent owns that app. This repo must not fork shop code ([CLONE_TO_OFFICIAL](#sources)). The following is the **storage contract** admin must obey so a later import / upload cannot invent products.

Intake `/admin` (CSV export only, [`sassy-closet/app/admin/page.tsx`](../../sassy-closet/app/admin/page.tsx)) is **out of scope**. Do not “fix” intake by writing sell-test rows into `submissions.json`.

### 7.1 Allowlist gate (first line of every write)

Admin may create or update image rows only when `product.ma` is one of:

`A01`, `S01`, `P01`, `P02`, `P03`, `P04`, `P05`, `K01`, `H01`, `A02`

Hard-fail (no row, no Blob put, no “we’ll keep it as draft mã”) on anything else — including `a01` that does not normalize to `A01`, `A001`, `AO001`, `A03`, `P06`, `D01`. Normalization is trim + upper + letter + 2–3 digits ([sell-catalog `parse_sell_ma`](#sources)). After normalize, it must still be in the ten.

`P02` and `P05` stay `status: "hold"`, `priceUsd: null`. Uploading a pretty set does not release Hold.

### 7.2 Record shape (catalog.v1, already on the shop)

Per product (fields admin already uses):

```json
{
  "ma": "A01",
  "colors": [
    { "id": "kem", "name": "Kem" },
    { "id": "xanh", "name": "Xanh" }
  ],
  "images": [
    {
      "src": "Documents/Sassy Closet/Photos/A01/001.jpg",
      "colorId": null,
      "order": 1
    }
  ]
}
```

Admin upload should **add** either `src` (OneDrive-relative, for re-export) or `url` (Blob / public URL **after** a real put). Do not invent a `https://…` URL for a file that was never uploaded. Do not invent `hex` on colors.

**Per-color storage is the `colorId` field**, not a new product.

Validation on every image write:

1. `ma` ∈ allowlist.
2. `colorId` is `null` **or** equals `colors[i].id` on **this** product.
3. `src` / `url` points at a file that exists (OD path verified, or Blob 200). If the file is missing, drop the image — do not keep a ghost ([intake migrate already skips missing bytes](../../sassy-closet/lib/store-backend.ts)).
4. `order` is a positive integer. Do not leave holes by inventing `004` when only `001`–`002` exist.
5. Optional admin-only metadata (not required on customer JSON): `role: "hq" | "ai-still" | "ai-video"`, `parentSrc`, `disclosed: true` for AI. Customer PDP should still show HQ first.

### 7.3 What to store **now** for each mã (no invented binds)

Until a human looks at the pixels, **keep `colorId: null`**. That is the current export. It is correct.

| Mã | colors[] to store | images[] to store | Per-color action in admin |
| --- | --- | --- | --- |
| `A01` | `kem`, `xanh` | `001.jpg`, `002.jpg` · order 1–2 · `colorId` null | After visual check: bind 0–n files to `kem` and/or `xanh`. If a file shows both bodies, leave null or split only if they are actually two files |
| `S01` | `kem` | `001.jpg` · order 1 · null or `kem` if the set is Kem | Do not add `xanh` to match `A01` |
| `P01` | `hoa` | `001.jpg`, `002.jpg` | Bind to `hoa` only if both frames are the floral piece. Do not add `hong` |
| `P02` | `do` | `001.jpg`, `002.jpg` | Hold. Bind to `do` only if red is what is in frame. No price |
| `P03` | `den`, `do` | `001.jpg`, `002.jpg`, `003.jpg` | Three files, two colors. **Do not** auto-map 001→đen, 002→đỏ, 003→??? . Null until tagged. Never invent a third color for the leftover file |
| `P04` | `kem` | `001.jpg`, `002.jpg` | Same as `S01` |
| `P05` | `hong`, `do`, `xanh` | `001.jpg`, `002.jpg`, `003.jpg` | Hold. Three colors and three files is a coincidence, **not** a mapping. Null until tagged. Do not mint `P06` |
| `K01` | `[]` | `001.jpeg`, `002.jpeg` | **No colorId except null.** Do not add `den` |
| `H01` | `[]` | `001.jpeg`, `002.jpeg`, `003.jpeg` | **No colorId except null.** Do not add `nau` / `den` for hair |
| `A02` | `cham-bi` | `001.jpeg`, `002.jpeg` | Bind to `cham-bi` after check. Do not rename to `trang` |

Qty stays `1` on the catalog row. That is not a photo count. Do not set `qty: 3` because `H01` has three jpegs.

### 7.4 Admin UX that prevents invention

Implement these as **hard UI constraints** on Origin (spec only here):

1. **Mã picker** = the ten codes. No free-text mã on upload. No “+ New product” that mints.
2. **Color picker** = `colors[]` for the selected mã, plus **Unassigned**. `K01` / `H01` show only Unassigned until the hub grows a color and JSON is re-exported.
3. **Add color** is disabled in admin. Colors enter through `sassycloset.xlsx` → `export_sell_catalog.py`. Admin is not Stock.
4. **Add image** requires an existing mã. Upload writes Blob bytes, then appends `{ url, colorId, order: max+1 }`.
5. **Reorder** changes `order` only. Does not clone rows.
6. **Delete image** removes the bind (and Blob object if unused). Does not delete the mã.
7. **AI upload** path sets `role: "ai-still"` / `"ai-video"` and requires `parent` = an existing HQ image id/src on that same mã. No parent → reject.
8. **Hold badge** on `P02` / `P05` stays visible on the media panel so a pretty gallery does not get published as available.
9. **Customer colors** render as text (`Kem`, `Xanh`, `Chấm bi`). Hex swatches in admin, if Origin already has them, must not be back-filled with guessed hex ([contract: no invented hex](#sources)).

### 7.5 Suggested admin record after a *verified* A01 bind (example only)

This example does **not** claim which of `001`/`002` is Kem. It shows the **shape** after a human tagged file A as Kem and left file B shared:

```json
{
  "ma": "A01",
  "colors": [
    { "id": "kem", "name": "Kem" },
    { "id": "xanh", "name": "Xanh" }
  ],
  "images": [
    {
      "src": "Documents/Sassy Closet/Photos/A01/001.jpg",
      "colorId": "kem",
      "order": 1
    },
    {
      "src": "Documents/Sassy Closet/Photos/A01/002.jpg",
      "colorId": null,
      "order": 2
    }
  ]
}
```

If Xanh has **no** verified file, there is no Xanh hero. The chip still exists (hub said so). The gallery does not lie. That is better than a generated Xanh.

### 7.6 AI derivatives on these ten only

If Boss wants a studio restyle or a 5s motion loop:

| Field | Value |
| --- | --- |
| `ma` | Same as parent (`A01`, not a new code) |
| `colorId` | Same as parent image, or null if parent is null |
| `src` / `url` | New Blob key, e.g. shop prefix `products/A01/ai/001_restyle.jpg` — **not** overwriting `Photos/A01/001.jpg` |
| `role` | `ai-still` or `ai-video` |
| `parentSrc` | `Documents/Sassy Closet/Photos/A01/001.jpg` |
| Customer label | “AI visualization — actual product may differ” next to the asset ([§4.4](#44-truth-in-advertising-the-legal-floor)) |

Do not run try-on video for a color that was never photographed. Do not run try-on for `K01` as a way to “add a color.” Do not generate `P05` as available.

### 7.7 Sync back to HQ (optional, Boss)

When admin has a **better** phone-to-grid still that is still the real piece:

1. Download the Blob original (not a compressed tile).
2. Write it into `Documents/Sassy Closet/Photos/{MA}/` as the next free `00n` — do not reuse `001` if `001` is already the Official hero unless Boss is replacing it on purpose.
3. Re-export catalog.v1 with `--photos-dir`.
4. Do not commit the jpeg to this git repo.

### 7.8 Checklist (print)

- [ ] Only ten mãs in sell-test catalog
- [ ] `P02` / `P05` Hold, no invented $
- [ ] `K01` / `H01` have no invented colors
- [ ] Every `colorId` ∈ that product’s `colors[].id` or is null
- [ ] Every `src` exists on disk or Blob; no placeholders
- [ ] HQ originals not overwritten by AI
- [ ] AI assets disclosed and parented
- [ ] Customer color text matches hub names (`Chấm bi`, not “polka dot #fff”)
- [ ] No `A03` / `P06` / `AO001` anywhere in admin
- [ ] No Square Save, no FB Post/Send
- [ ] `#shop-decisions` before calling the gallery “official”

---

## 8. Worked refusals (so agents do not “help”)

| Request | Refusal |
| --- | --- |
| “Generate `A03` so we can test the grid” | Not in allowlist. Use the ten. |
| “`A01` only has Kem in the photo; invent Xanh” | Leave Xanh chip, `colorId` null, or photograph Xanh. |
| “`K01` looks black; add `den`” | Hub `colors` is empty. Write the color on the hub first. |
| “Map `P05` 001/002/003 to hồng/đỏ/xanh automatically” | Coincidence of counts. Human bind only. |
| “Make a video of `P02` pouring so we can sell it” | Hold. No price. Motion optional, not merchandising. |
| “Soul model wearing a random white top, save as `A02`” | `A02` is Chấm bi. Wrong product. |
| “Put the same lifestyle AI on every mã to fill gaps” | That attaches one invented scene to ten identities. |
| “Excel `AO001` = sell-test `A01`, merge folders” | Two alphabets. Do not merge. A01 handoff is a separate kit job. |

---

## 9. Sources

### Shop / this repo

- [README.md](../../README.md) — Square Free = on-hand SoT; Photos in `Documents/Sassy Closet/Photos/`; never invent mã; bots draft only.
- [excel-kit/schema.py](../../excel-kit/schema.py) — `PHOTO_RULE`, `ASK_STOCK_MA`, `photo_link` last, `photo_filename_for_ma`, A01 cutover comment.
- [excel-kit/DESIGN_NOTES.md](../../excel-kit/DESIGN_NOTES.md) — no embeds; `AO001.jpg` / `#001.jpg` on SoT.
- [excel-kit/square/README.md](../../excel-kit/square/README.md) — SKU = mã; variation = Asia size + color; no Save until `#shop-decisions`.
- [excel-kit/prompts/GF_CLOTHES_INTAKE.md](../../excel-kit/prompts/GF_CLOTHES_INTAKE.md) + [HOW_TO_UPLOAD.md](../../excel-kit/templates/from_gf/HOW_TO_UPLOAD.md) — From GF → Photos rename; do not invent mã; never point SoT at `From GF/`.
- [excel-kit/prompts/FIND_MA_CARD_2026-09-08.md](../../excel-kit/prompts/FIND_MA_CARD_2026-09-08.md) — where stored = `Photos/{ma}/`; never invent qty / $.
- [sassy-closet/lib/kinds.ts](../../sassy-closet/lib/kinds.ts) — kind letters; color chips (`kem`, `xanh`, `hoa`, …).
- [sassy-closet/lib/types.ts](../../sassy-closet/lib/types.ts) — `photo_paths`, `Piece.photos`.
- [sassy-closet/lib/store.ts](../../sassy-closet/lib/store.ts) — `{ma}/{001}.ext`; `photo_link` folder; no invent on mint.
- [sassy-closet/lib/photos.ts](../../sassy-closet/lib/photos.ts) + tests — never invent paths.
- [sassy-closet/app/admin/page.tsx](../../sassy-closet/app/admin/page.tsx) — intake admin is CSV only (not sell-test).
- Sell-catalog lane (Boss 2026-09-09; kit files `excel-kit/docs/SELL_CATALOG_CONTRACT.md`, `CLONE_TO_OFFICIAL.md`, `excel-kit/samples/sell-catalog.v1.json` on the catalog-export branch): allowlist of ten, prices, Hold on `P02`/`P05`, recorded colors, flat HQ file list, `images[].colorId`, sell-test https://sassy-closet-shop.vercel.app/admin.

### Higgsfield-class (loaded 2026-09-09 via MCP)

- Workflow catalog: `product-photoshoot`, `virtual-model-tryout` (mode file), `restyle`, `ugc-try-on-video`, `ugc-product-video`, `ad-multiplier`, `character-sheet`, `thumbnail-generation` — scope lines cited in §4.
- `product-photoshoot` SKILL — one product identity across a set; `nano_banana_pro` + image references; not Amazon-compliance; not UGC video.
- `references/product-shot.md` — `clean-studio`, 5500K-class catalog lighting, 1:1 default, quality gates (recognizable product, plausible shadows, no edge artifacts).
- `references/photography-vocabulary.md` — direction / quality / Kelvin; ban on “good lighting.”
- `references/virtual-model-tryout.md` — no identity memory; product-fidelity directive; `studio-clean` 45° key + 5500K.
- `references/restyle.md` — preserve product appearance; source required.
- `ugc-try-on-video` SKILL — garment consistency lock; product photo required; not a PDP replacement.
- `models_explore` — Marketing Studio Image/Video; Soul 2.0 (fashion editorial, not packshot SoT); Kling 3.0; Seedance 2.0 (multi-SKU / e-commerce tags) and 2.5; Genjutsu motion control; FLUX 3 Video; Grok Video 1.5.

### Lighting / catalog craft

- [Ecommerce Photography: The 2026 Guide — On-Model](https://on-model.com/blog/ecommerce-photography-guide) — grid consistency; colorways as returns; 4–6 images; batch by view.
- [Catalog Photography: 2026 Consistency Guide — FrameOnce](https://frameonce.io/blog/catalog-photography) — tape the lights; 5500K LEDs; custom WB; ColorChecker.
- [Consistent Product Images — Wearview](https://www.wearview.co/blog/consistent-product-images-guide) — five locked variables; same views per colorway.
- [E-Commerce Photography Shot List — The Line Studios](https://thelinestudios.nyc/e-commerce-photography-shot-list-guide/) — shoot one composition across colorways; 4–6 images per SKU.
- [Visual consistency at scale — Pixofix](https://www.pixofix.com/blog/visual-consistency-at-scale-fashion-ecommerce) — numeric locks; canary SKUs before trusting AI post.

### Law / platforms (primary, then commentary)

- [FTC, Operation AI Comply (2024-09-25)](https://www.ftc.gov/news-events/news/press-releases/2024/09/ftc-announces-crackdown-deceptive-ai-claims-schemes) — no AI exemption; Rytr review-generation complaint.
- [FTC, Endorsement Guides: What People Are Asking](https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking) — honest endorsements; clear and conspicuous material-connection disclosures; video disclosures in the video.
- [16 C.F.R. Part 255](https://www.ecfr.gov/current/title-16/chapter-I/subchapter-B/part-255) — Endorsement Guides (2023 revision).
- [Square, Upload and Attach Images](https://developer.squareup.com/docs/catalog-api/upload-and-attach-images) — attach to item or variation; primary = first `image_ids`.
- Commentary (not law): [Style3D, Truth in Advertising for AI Product Renders](https://www.style3d.com/blog/truth-in-advertising-for-ai-product-renders-for-fashion-teams/); [AI Fashion Law, FTC disclosure](https://www.aifashionlaw.com/article/ftc); [Nightjar, Legal Guide to AI Product Photography (2026)](https://nightjar.so/blog/ai-product-photography-legal-guide).

---

## 10. One-page crib

1. Photograph the real piece under **one** 5500K, 45° soft key recipe.
2. Repeat the **same** views for each **recorded** color only.
3. Keep HQ in `Documents/Sassy Closet/Photos/{MA}/` as `001`… — do not overwrite.
4. Sell-test admin stores `{ src, colorId, order }` on an **existing** allowlisted mã.
5. `colorId` is null or a hub slug already on that mã. `K01` / `H01` stay null.
6. AI is a labeled child of an HQ parent. Never a new mã. Never a new color.
7. `P02` / `P05` remain Hold. The other eight keep Boss USD. Qty is not “number of photos.”
8. If you had to invent a code to file the picture, the picture does not get filed.
