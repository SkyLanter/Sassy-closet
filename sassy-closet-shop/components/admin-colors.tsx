"use client";

import { useState } from "react";
import { ColorSwatch, ColorSwatchEmpty } from "@/components/color-swatch";
import { mergeColorAssets } from "@/lib/catalog-merge";
import { COLOR_PRESETS, createColorId, normalizeHex, suggestedColorName } from "@/lib/colors";
import { hubColorLocked, nextImageOrder, recordedHubSlugs } from "@/lib/hub-colors";
import { assignSlideColor, moveLinkedSlide } from "@/lib/image-order";
import { imagesTaggedToColor } from "@/lib/product-media";
import { isAllowedImageSrc } from "@/lib/product-parse";
import type { ProductColor, ProductImageAsset } from "@/lib/types";

export function AdminColorEditor({
  ma,
  colors,
  images,
  canUpload,
  onColorsChange,
  onImagesChange,
  onUpload,
  onNotice,
}: {
  ma: string;
  colors: ProductColor[];
  images: ProductImageAsset[];
  canUpload: boolean;
  onColorsChange: (colors: ProductColor[]) => void;
  onImagesChange: (images: ProductImageAsset[]) => void;
  onUpload: (file: File, colorId: string) => void;
  onNotice?: (tone: "ok" | "error", text: string) => void;
}) {
  const locked = hubColorLocked(ma);
  const recorded = recordedHubSlugs(ma);
  const [custom, setCustom] = useState("#111111");
  const [customName, setCustomName] = useState("Black");
  const [mergeFrom, setMergeFrom] = useState("");
  const [mergeInto, setMergeInto] = useState("");

  function pickPreset(hex: string, name: string) {
    setCustom(hex);
    setCustomName(name);
  }

  function addColor() {
    if (locked) {
      onNotice?.(
        "error",
        recorded.length === 0
          ? `${ma} has no recorded hub color. Photos stay untagged (colorId null). Do not invent den.`
          : `${ma} already has recorded hub colors (${recorded.join(", ")}). Do not invent another colorway.`,
      );
      return;
    }
    const hex = normalizeHex(custom);
    if (!hex) {
      onNotice?.("error", "Color hex is invalid. Use #111111 or a swatch box.");
      return;
    }
    if (colors.some((color) => color.hex === hex)) {
      onNotice?.("error", `That hex is already on this item (${hex}).`);
      return;
    }
    const label = customName.trim() || suggestedColorName(hex);
    if (!label) {
      onNotice?.("error", "Give the color a name. The shop shows names, not boxes.");
      return;
    }
    onColorsChange([...colors, { id: createColorId(), hex, name: label, note: "" }]);
  }

  function updateColor(id: string, patch: Partial<ProductColor>) {
    onColorsChange(colors.map((color) => (color.id === id ? { ...color, ...patch } : color)));
  }

  function removeColor(id: string) {
    if (locked) {
      onNotice?.("error", `Keep recorded hub colors on ${ma}. Untag the photo instead.`);
      return;
    }
    onColorsChange(colors.filter((color) => color.id !== id));
    onImagesChange(
      images.map((image) => (image.colorId === id ? { ...image, colorId: null } : image)),
    );
  }

  function addUrlToColor(colorId: string, src: string) {
    const trimmed = src.trim();
    if (!trimmed) {
      onNotice?.("error", "Paste an image URL before attaching.");
      return false;
    }
    if (!isAllowedImageSrc(trimmed)) {
      onNotice?.("error", "Use an http(s) URL or a site path like /products/A01/cover.jpg.");
      return false;
    }
    onImagesChange([...images, { src: trimmed, colorId, order: nextImageOrder(images) }]);
    return true;
  }

  function removeImage(src: string, colorId: string) {
    onImagesChange(
      images.filter((image) => !(image.src === src && image.colorId === colorId)),
    );
  }

  return (
    <section className="space-y-4">
      <div>
        <h3 className="text-xs uppercase tracking-[0.14em] text-muted">Colors</h3>
        <p className="mt-1 text-sm text-muted">
          {locked
            ? recorded.length === 0
              ? `${ma} has no recorded hub color. Tag photos as unassigned (colorId null). Do not invent den.`
              : `${ma} colors are hub slugs (${recorded.join(", ")}). Tag a photo to a slug already on this mã, or leave null. Do not invent a colorway.`
            : "Swatch boxes pick a hex for you. Press Add color to attach it. Each color needs a name (shop is text-only). Link gallery slides to a color (image.colorId) so the shop reel rolls to those photos."}
        </p>
      </div>
      {locked ? null : (
      <>
      <div className="flex flex-wrap gap-2">
        {COLOR_PRESETS.map((preset) => (
          <ColorSwatch
            key={preset.hex}
            hex={preset.hex}
            size="lg"
            title={preset.name}
            selected={normalizeHex(custom) === preset.hex}
            onClick={() => pickPreset(preset.hex, preset.name)}
          />
        ))}
      </div>
      <div className="flex flex-wrap items-end gap-2">
        <label className="text-xs uppercase tracking-[0.12em] text-muted">
          Swatch
          <input
            type="color"
            value={normalizeHex(custom) ?? "#111111"}
            onChange={(event) => {
              const hex = normalizeHex(event.target.value) ?? event.target.value;
              setCustom(hex);
              const suggested = suggestedColorName(hex);
              if (suggested) {
                setCustomName(suggested);
              }
            }}
            aria-label="Custom color"
            className="mt-1 block h-9 w-9 cursor-pointer rounded-sm border border-line bg-paper p-0"
          />
        </label>
        <label className="text-xs uppercase tracking-[0.12em] text-muted">
          Hex
          <input
            value={custom}
            onChange={(event) => setCustom(event.target.value)}
            placeholder="#111111"
            aria-label="Custom hex"
            className="mt-1 block w-28 rounded-lg border border-line bg-paper px-2 py-1.5 font-sans text-sm normal-case tabular-nums tracking-normal text-ink outline-none focus:border-gold"
          />
        </label>
        <label className="text-xs uppercase tracking-[0.12em] text-muted">
          Name
          <input
            value={customName}
            onChange={(event) => setCustomName(event.target.value)}
            placeholder="Black"
            aria-label="Custom color name"
            className="mt-1 block w-36 rounded-lg border border-line bg-paper px-2 py-1.5 text-sm normal-case tracking-normal text-ink outline-none focus:border-gold"
          />
        </label>
        <button
          type="button"
          data-testid="admin-add-color"
          className="rounded-full bg-ink px-3 py-1.5 text-xs uppercase tracking-[0.12em] text-paper"
          onClick={addColor}
        >
          Add color
        </button>
      </div>
      </>
      )}
      {colors.length > 1 && !locked ? (
        <div className="flex flex-wrap items-end gap-2 rounded-xl border border-line px-3 py-3">
          <label className="text-xs uppercase tracking-[0.12em] text-muted">
            Merge from
            <select
              value={mergeFrom}
              onChange={(event) => setMergeFrom(event.target.value)}
              className="mt-1 block min-w-[8rem] rounded-lg border border-line bg-paper px-2 py-1.5 text-sm normal-case tracking-normal text-ink"
            >
              <option value="">Pick color</option>
              {colors.map((color) => (
                <option key={color.id} value={color.id}>
                  {color.name || color.hex}
                </option>
              ))}
            </select>
          </label>
          <label className="text-xs uppercase tracking-[0.12em] text-muted">
            Into
            <select
              value={mergeInto}
              onChange={(event) => setMergeInto(event.target.value)}
              className="mt-1 block min-w-[8rem] rounded-lg border border-line bg-paper px-2 py-1.5 text-sm normal-case tracking-normal text-ink"
            >
              <option value="">Keep color</option>
              {colors.map((color) => (
                <option key={color.id} value={color.id}>
                  {color.name || color.hex}
                </option>
              ))}
            </select>
          </label>
          <button
            type="button"
            data-testid="admin-merge-colors"
            className="rounded-full border border-line px-3 py-1.5 text-xs uppercase tracking-[0.12em] text-ink"
            onClick={() => {
              try {
                const next = mergeColorAssets(colors, images, mergeInto, mergeFrom);
                onColorsChange(next.colors);
                onImagesChange(next.images);
                setMergeFrom("");
                setMergeInto("");
                onNotice?.("ok", "Colors merged. Photos moved to the kept name.");
              } catch (error) {
                onNotice?.("error", error instanceof Error ? error.message : "Color merge failed");
              }
            }}
          >
            Merge colors
          </button>
        </div>
      ) : null}
      {colors.length === 0 ? (
        <p className="text-sm text-muted">
          {locked
            ? `${ma} has no recorded hub color. Leave every photo colorId null.`
            : "No colors yet. Skip if the piece is one look."}
        </p>
      ) : (
        <ul className="space-y-4">
          {colors.map((color) => (
            <ColorCard
              key={color.id}
              color={color}
              images={images}
              canUpload={canUpload}
              locked={locked}
              onUpdate={(patch) => updateColor(color.id, patch)}
              onRemove={() => removeColor(color.id)}
              onAddUrl={(src) => addUrlToColor(color.id, src)}
              onRemovePhoto={(src) => removeImage(src, color.id)}
              onImagesChange={onImagesChange}
              onUpload={(file) => onUpload(file, color.id)}
            />
          ))}
        </ul>
      )}
    </section>
  );
}

function ColorCard({
  color,
  images,
  canUpload,
  locked,
  onUpdate,
  onRemove,
  onAddUrl,
  onRemovePhoto,
  onImagesChange,
  onUpload,
}: {
  color: ProductColor;
  images: ProductImageAsset[];
  canUpload: boolean;
  locked: boolean;
  onUpdate: (patch: Partial<ProductColor>) => void;
  onRemove: () => void;
  onAddUrl: (src: string) => boolean;
  onRemovePhoto: (src: string) => void;
  onImagesChange: (images: ProductImageAsset[]) => void;
  onUpload: (file: File) => void;
}) {
  const [url, setUrl] = useState("");
  const [hexDraft, setHexDraft] = useState(color.hex);
  const photos = imagesTaggedToColor(images, color.id);
  const unassigned = images.filter((image) => image.colorId === null && image.src.trim());

  return (
    <li className="rounded-2xl border border-line p-4">
      <div className="flex flex-wrap items-start gap-3">
        <ColorSwatch hex={color.hex} size="lg" title={color.name} />
        <div className="grid min-w-0 flex-1 gap-3 sm:grid-cols-2">
          <label className="text-xs uppercase tracking-[0.12em] text-muted">
            Name / label
            {locked ? (
              <p className="mt-1 rounded-lg border border-line bg-blush px-3 py-2 text-sm normal-case tracking-normal text-ink">
                {color.name}
              </p>
            ) : (
              <input
                value={color.name}
                onChange={(event) => onUpdate({ name: event.target.value })}
                placeholder="Black / Đen"
                className="mt-1 w-full rounded-lg border border-line bg-paper px-3 py-2 text-sm normal-case tracking-normal text-ink outline-none focus:border-gold"
              />
            )}
          </label>
          <label className="text-xs uppercase tracking-[0.12em] text-muted">
            Note
            <input
              value={color.note}
              onChange={(event) => onUpdate({ note: event.target.value })}
              placeholder="Hoa / Caro — shown under the shop name"
              className="mt-1 w-full rounded-lg border border-line bg-paper px-3 py-2 text-sm normal-case tracking-normal text-ink outline-none focus:border-gold"
            />
          </label>
          <label className="text-xs uppercase tracking-[0.12em] text-muted">
            Hex
            {locked ? (
              <p className="mt-1 rounded-lg border border-line bg-blush px-3 py-2 font-sans text-sm tabular-nums text-ink">
                {color.hex}
              </p>
            ) : (
              <div className="mt-1 flex gap-2">
                <input
                  type="color"
                  value={normalizeHex(color.hex) ?? "#111111"}
                  onChange={(event) => {
                    const hex = normalizeHex(event.target.value);
                    if (hex) {
                      setHexDraft(hex);
                      onUpdate({ hex });
                    }
                  }}
                  aria-label={`Hex for ${color.name || "color"}`}
                  className="h-10 w-10 cursor-pointer rounded-sm border border-line bg-paper p-0"
                />
                <input
                  value={hexDraft}
                  onChange={(event) => {
                    setHexDraft(event.target.value);
                    const hex = normalizeHex(event.target.value);
                    if (hex) {
                      onUpdate({ hex });
                    }
                  }}
                  className="min-w-0 flex-1 rounded-lg border border-line bg-paper px-3 py-2 font-sans text-sm tabular-nums text-ink outline-none focus:border-gold"
                />
              </div>
            )}
          </label>
        </div>
        {locked ? (
          <p
            className="rounded-full border border-line px-2.5 py-1 text-[11px] uppercase tracking-[0.12em] text-muted"
            data-testid="admin-hub-slug"
          >
            {color.id}
          </p>
        ) : (
          <button
            type="button"
            className="text-xs uppercase tracking-[0.12em] text-muted hover:text-ink"
            onClick={onRemove}
          >
            Remove color
          </button>
        )}
      </div>
      <p className="mt-4 text-xs uppercase tracking-[0.14em] text-muted">
        Slides linked to this color (image.colorId)
      </p>
      <ul className="mt-2 flex flex-wrap gap-3">
        {photos.map((photo, index) => (
          <li key={`${color.id}-${photo.src}-${index}`} className="relative">
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img src={photo.src} alt="" className="h-20 w-16 rounded-md object-cover" />
            {photo.src.startsWith("blob:") ? (
              <span className="absolute inset-x-0 top-0 bg-ink/70 py-0.5 text-center text-[8px] uppercase tracking-[0.1em] text-paper">
                Uploading
              </span>
            ) : null}
            <div className="absolute inset-x-0 bottom-0 flex flex-col">
              <span className="flex">
                <button
                  type="button"
                  data-testid="admin-slide-up"
                  disabled={index === 0}
                  className="flex-1 bg-ink/70 py-0.5 text-[8px] uppercase tracking-[0.08em] text-paper disabled:opacity-40"
                  onClick={() => onImagesChange(moveLinkedSlide(images, color.id, index, -1))}
                >
                  Up
                </button>
                <button
                  type="button"
                  data-testid="admin-slide-down"
                  disabled={index === photos.length - 1}
                  className="flex-1 bg-ink/70 py-0.5 text-[8px] uppercase tracking-[0.08em] text-paper disabled:opacity-40"
                  onClick={() => onImagesChange(moveLinkedSlide(images, color.id, index, 1))}
                >
                  Down
                </button>
              </span>
              <button
                type="button"
                data-testid="admin-unlink-slide"
                className="bg-ink/80 py-0.5 text-[8px] uppercase tracking-[0.1em] text-paper"
                onClick={() => onImagesChange(assignSlideColor(images, photo.src, null, color.id))}
              >
                Unlink
              </button>
              <button
                type="button"
                className="bg-ink py-0.5 text-[8px] uppercase tracking-[0.1em] text-paper"
                onClick={() => onRemovePhoto(photo.src)}
              >
                Remove
              </button>
            </div>
          </li>
        ))}
        {photos.length === 0 ? (
          <li className="flex h-20 w-28 items-center justify-center rounded-md border border-dashed border-line px-2 text-center text-[11px] text-gold-deep">
            Link a slide, or attach a URL
          </li>
        ) : null}
      </ul>
      {unassigned.length > 0 ? (
        <div className="mt-3">
          <p className="text-[11px] uppercase tracking-[0.12em] text-muted">
            Unassigned slides — link to this color
          </p>
          <ul className="mt-2 flex flex-wrap gap-2">
            {unassigned.map((photo, index) => (
              <li key={`unassigned-${photo.src}-${index}`} className="relative">
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img src={photo.src} alt="" className="h-16 w-12 rounded-md object-cover" />
                <button
                  type="button"
                  data-testid="admin-link-slide"
                  className="absolute inset-x-0 bottom-0 bg-ink/75 py-0.5 text-[8px] uppercase tracking-[0.1em] text-paper"
                  onClick={() => onImagesChange(assignSlideColor(images, photo.src, color.id, null))}
                >
                  Link
                </button>
              </li>
            ))}
          </ul>
        </div>
      ) : null}
      <div className="mt-3 flex flex-wrap items-center gap-2">
        {canUpload ? (
          <label className="cursor-pointer rounded-full border border-line px-3 py-1.5 text-xs uppercase tracking-[0.12em] text-ink hover:border-gold">
            Upload photo
            <input
              type="file"
              accept="image/*"
              className="sr-only"
              onChange={(event) => {
                const file = event.target.files?.[0];
                if (file) {
                  onUpload(file);
                }
                event.target.value = "";
              }}
            />
          </label>
        ) : (
          <span className="text-xs text-muted">Paste a URL — uploads need Blob</span>
        )}
        <input
          value={url}
          onChange={(event) => setUrl(event.target.value)}
          placeholder="https://… or /products/A01/cover.jpg"
          className="min-w-[12rem] flex-1 rounded-lg border border-line bg-paper px-3 py-1.5 text-sm text-ink outline-none focus:border-gold"
        />
        <button
          type="button"
          className="rounded-full border border-line px-3 py-1.5 text-xs uppercase tracking-[0.12em] text-ink hover:border-gold"
          onClick={() => {
            if (onAddUrl(url)) {
              setUrl("");
            }
          }}
        >
          Attach URL
        </button>
      </div>
    </li>
  );
}

export function AdminImageColorTag({
  colors,
  colorId,
  onChange,
}: {
  colors: ProductColor[];
  colorId: string | null;
  onChange: (colorId: string | null) => void;
}) {
  if (colors.length === 0) {
    return (
      <p className="text-[11px] text-muted" data-testid="admin-color-tag-empty">
        Unassigned · colorId null. Do not invent a slug.
      </p>
    );
  }
  return (
    <div className="flex flex-wrap items-center gap-2" data-testid="admin-image-color-tag">
      <span className="inline-flex items-center gap-1.5">
        <ColorSwatchEmpty selected={colorId === null} size="sm" onClick={() => onChange(null)} />
        <button
          type="button"
          data-testid="admin-color-unassigned"
          className={`text-[11px] uppercase tracking-[0.12em] ${
            colorId === null ? "text-ink" : "text-muted hover:text-ink"
          }`}
          onClick={() => onChange(null)}
        >
          Unassigned
        </button>
      </span>
      {colors.map((color) => (
        <span key={color.id} className="inline-flex items-center gap-1">
          <ColorSwatch
            hex={color.hex}
            size="sm"
            selected={colorId === color.id}
            title={`${color.name} · ${color.id}`}
            onClick={() => onChange(color.id)}
          />
          <button
            type="button"
            data-color-id={color.id}
            className={`text-[11px] ${colorId === color.id ? "text-ink" : "text-muted hover:text-ink"}`}
            onClick={() => onChange(color.id)}
          >
            {color.name} · {color.id}
          </button>
        </span>
      ))}
    </div>
  );
}
