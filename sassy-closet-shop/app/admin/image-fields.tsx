"use client";

import { AdminImageColorTag } from "@/components/admin-colors";
import { nextImageOrder, stampImageOrders } from "@/lib/hub-colors";
import { reorderImages } from "@/lib/image-order";
import type { ItemDraft } from "@/lib/item-draft";
import type { ProductColor, ProductImageAsset } from "@/lib/types";

export function ImageFields({
  ma,
  draft,
  canUpload,
  onChange,
  onUpload,
}: {
  ma: string;
  draft: ItemDraft;
  canUpload: boolean;
  onChange: (next: ItemDraft) => void;
  onUpload: (file: File) => void;
}) {
  function setImages(images: ProductImageAsset[]) {
    onChange({
      ...draft,
      images: stampImageOrders(images.length > 0 ? images : [{ src: "", colorId: null, order: 1 }]),
    });
  }

  function move(index: number, direction: -1 | 1) {
    setImages(reorderImages(draft.images, index, direction));
  }

  return (
    <section className="space-y-3" data-upload-limit="4.5mb-server-action">
      <div>
        <h3 className="text-xs uppercase tracking-[0.14em] text-muted">All images</h3>
        <p className="mt-1 text-sm text-muted">
          Upload or paste a URL. Tag each photo to a color (or none). Use arrows to reorder — first
          image is the cover. Uploads cap at 4.5 MB each — compress the JPEG first if it fails.
        </p>
      </div>
      {draft.images.map((image, index) => (
        <div key={`${ma}-img-${index}`} className="flex items-start gap-3">
          <div className="relative h-20 w-14 shrink-0 overflow-hidden rounded-md border border-dashed border-line bg-blush">
            {image.src.trim() ? (
              // eslint-disable-next-line @next/next/no-img-element
              <img src={image.src} alt="" className="h-full w-full object-cover" />
            ) : (
              <span className="flex h-full items-center justify-center text-[9px] uppercase tracking-[0.12em] text-muted">
                —
              </span>
            )}
            {image.src.startsWith("blob:") ? (
              <span className="absolute inset-x-0 bottom-0 bg-ink/70 py-0.5 text-center text-[8px] uppercase tracking-[0.1em] text-paper">
                Uploading
              </span>
            ) : null}
          </div>
          <div className="min-w-0 flex-1 space-y-2">
            <p className="text-[10px] uppercase tracking-[0.14em] text-muted">
              {index === 0 ? "Cover" : `Photo ${index + 1}`} · order {image.order || index + 1}
            </p>
            <input
              value={image.src}
              onChange={(event) => {
                const images = draft.images.slice();
                images[index] = { ...image, src: event.target.value };
                setImages(images);
              }}
              placeholder="https://… or /products/A01/cover.jpg"
              className="w-full rounded-lg border border-line bg-paper px-3 py-2 text-sm text-ink outline-none focus:border-gold"
            />
            <AdminImageColorTag
              colors={draft.colors}
              colorId={image.colorId}
              onChange={(colorId) => {
                const images = draft.images.slice();
                images[index] = { ...image, colorId };
                setImages(images);
              }}
            />
            <div className="flex flex-wrap gap-3">
              <button
                type="button"
                className="text-xs uppercase tracking-[0.12em] text-muted hover:text-ink disabled:opacity-30"
                disabled={index === 0}
                onClick={() => move(index, -1)}
              >
                Up
              </button>
              <button
                type="button"
                className="text-xs uppercase tracking-[0.12em] text-muted hover:text-ink disabled:opacity-30"
                disabled={index === draft.images.length - 1}
                onClick={() => move(index, 1)}
              >
                Down
              </button>
              <button
                type="button"
                className="text-xs uppercase tracking-[0.12em] text-muted hover:text-ink"
                onClick={() => {
                  const images = draft.images.filter((_, itemIndex) => itemIndex !== index);
                  setImages(images);
                }}
              >
                Remove
              </button>
            </div>
          </div>
        </div>
      ))}
      <div className="flex flex-wrap items-center gap-3">
        <button
          type="button"
          className="rounded-full border border-line px-3 py-1.5 text-xs uppercase tracking-[0.12em] text-ink hover:border-gold"
          onClick={() =>
            setImages([
              ...draft.images,
              { src: "", colorId: null, order: nextImageOrder(draft.images) },
            ])
          }
        >
          Add URL
        </button>
        {canUpload ? (
          <label className="cursor-pointer rounded-full border border-line px-3 py-1.5 text-xs uppercase tracking-[0.12em] text-ink hover:border-gold">
            Upload image
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
      </div>
    </section>
  );
}

export function applyColorsToDraft(draft: ItemDraft, colors: ProductColor[]): ItemDraft {
  const ids = new Set(colors.map((color) => color.id));
  return {
    ...draft,
    colors,
    images: draft.images.map((image) => ({
      ...image,
      colorId: image.colorId && ids.has(image.colorId) ? image.colorId : null,
    })),
  };
}
