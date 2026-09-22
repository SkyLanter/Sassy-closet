"use client";

import { useMemo, useState } from "react";
import Link from "next/link";
import { MaMark } from "@/components/ma-mark";
import { postAdminHold } from "@/lib/admin-client-save";
import { publicSaveErrorMessage, opaquePostSaveMessage } from "@/lib/opaque-rsc-error";
import { ProductStatusBadge } from "@/components/product-status-badge";
import { letterPickerOptions, TYPE_LABELS } from "@/lib/catalog";
import { isKnownSeedMa } from "@/lib/catalog-contract";
import { inspectCatalogIntegrity } from "@/lib/catalog-integrity";
import { formatUsd } from "@/lib/format";
import { isCompleteSaveReceipt, saveReceiptLine, silentSaveError } from "@/lib/save-receipt";
import type { MaLetter } from "@/lib/ma";
import { coverSrc } from "@/lib/product-media";
import type { Product, ProductStatus, SiteSettings } from "@/lib/types";

type StatusFilter = "all" | ProductStatus;

function PriceCell({ product }: { product: Product }) {
  switch (product.status) {
    case "hold":
      return <span className="text-muted">Hold</span>;
    case "available":
    case "sold":
      return <span>{product.priceUsd === null ? "—" : formatUsd(product.priceUsd)}</span>;
    default: {
      const _exhaustive: never = product.status;
      return _exhaustive;
    }
  }
}

export function CatalogList({
  products,
  onAdd,
  onEdit,
  canWrite,
  onHeld,
  onToast,
}: {
  products: Product[];
  onAdd: () => void;
  onEdit: (ma: string) => void;
  canWrite: boolean;
  onHeld: (products: Product[], settings: SiteSettings) => void;
  onToast: (tone: "ok" | "error", text: string) => void;
}) {
  const [busy, setBusy] = useState(false);
  const [query, setQuery] = useState("");
  const [typeFilter, setTypeFilter] = useState<MaLetter | "all">("all");
  const [statusFilter, setStatusFilter] = useState<StatusFilter>("all");
  const [fulfillmentFilter, setFulfillmentFilter] = useState<"all" | "dropship" | "on_hand">("all");
  const [selected, setSelected] = useState<string[]>([]);
  const letters = letterPickerOptions();
  const integrity = useMemo(() => inspectCatalogIntegrity(products), [products]);

  const visible = useMemo(() => {
    const needle = query.trim().toLowerCase();
    return products.filter((product) => {
      if (typeFilter !== "all" && product.type !== typeFilter) {
        return false;
      }
      if (statusFilter !== "all" && product.status !== statusFilter) {
        return false;
      }
      if (fulfillmentFilter !== "all" && product.fulfillment !== fulfillmentFilter) {
        return false;
      }
      if (!needle) {
        return true;
      }
      const hay = `${product.ma} ${product.titleEn} ${product.titleVn} ${product.colors
        .map((color) => `${color.name} ${color.hex}`)
        .join(" ")}`.toLowerCase();
      return hay.includes(needle);
    });
  }, [fulfillmentFilter, products, query, statusFilter, typeFilter]);

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <h2 className="font-display text-3xl text-ink">
            Catalog · 10 hub
            {products.length > 10 ? ` + ${products.length - 10} extra` : ""}
          </h2>
          <p className="mt-1 text-sm text-muted">
            Ten hub mãs stay. {products.length} in store · {visible.length} shown. Change mã is on
            each row (extras only — uniqueness required). Sold / Gone stay in admin and leave the
            shop. Boss Add writes the live catalog; unused letter-codes are not shop tiles. Shop
            tiles are hold | available only.
          </p>
        </div>
        <div className="flex flex-wrap gap-2">
          <button
            type="button"
            data-testid="admin-bulk-hold"
            disabled={busy || !canWrite || selected.length === 0}
            onClick={() => {
              void (async () => {
                const holding = [...selected];
                setBusy(true);
                try {
                  const result = await postAdminHold(holding);
                  if (!result.ok) {
                    onToast("error", result.error);
                    return;
                  }
                  if (!isCompleteSaveReceipt(result) || !result.products || !result.settings) {
                    onToast("error", silentSaveError());
                    return;
                  }
                  setSelected([]);
                  onHeld(result.products, result.settings);
                  onToast(
                    "ok",
                    `Hold ${holding.length} mãs · Inbox for price · ${saveReceiptLine(result)}`,
                  );
                } catch (error) {
                  onToast("error", publicSaveErrorMessage(error, opaquePostSaveMessage()));
                } finally {
                  setBusy(false);
                }
              })();
            }}
            className="min-h-11 rounded-full border border-line px-4 py-2.5 text-sm text-ink disabled:opacity-40"
          >
            Hold selected{selected.length ? ` (${selected.length})` : ""}
          </button>
          <button
            type="button"
            data-testid="admin-add-open"
            onClick={onAdd}
            className="min-h-11 rounded-full bg-ink px-5 py-2.5 text-sm text-paper"
          >
            Add mã
          </button>
        </div>
      </div>
      {integrity.missingAllowlist.length > 0 ? (
        <p className="rounded-xl border border-gold-deep/40 bg-blush px-4 py-3 text-sm text-gold-deep" role="alert">
          Missing allowlist mãs: {integrity.missingAllowlist.join(", ")}. Do not invent replacements.
        </p>
      ) : null}
      {integrity.extras.length > 0 ? (
        <p className="rounded-xl border border-gold-deep/40 bg-blush px-4 py-3 text-sm text-gold-deep" role="alert">
          Extra mãs beyond the hub ten: {integrity.extras.join(", ")}. They Save and appear on the
          shop. Remove leftover test mãs if they are not a real piece.
        </p>
      ) : null}
      {integrity.duplicates.length > 0 ? (
        <p className="rounded-xl border border-gold-deep/40 bg-blush px-4 py-3 text-sm text-gold-deep" role="alert">
          Duplicate mãs: {integrity.duplicates.join(", ")}. Do not gộp.
        </p>
      ) : null}
      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
        <label className="block text-xs uppercase tracking-[0.14em] text-muted">
          Search
          <input
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="A01, thermos…"
            className="mt-1 w-full rounded-lg border border-line bg-paper px-3 py-2 text-sm normal-case tracking-normal text-ink outline-none focus:border-gold"
          />
        </label>
        <label className="block text-xs uppercase tracking-[0.14em] text-muted">
          Type
          <select
            value={typeFilter}
            onChange={(event) => {
              const value = event.target.value;
              if (value === "all") {
                setTypeFilter("all");
                return;
              }
              const match = letters.find((option) => option.letter === value);
              if (match) {
                setTypeFilter(match.letter);
              }
            }}
            className="mt-1 w-full rounded-lg border border-line bg-paper px-3 py-2 text-sm normal-case tracking-normal text-ink outline-none focus:border-gold"
          >
            <option value="all">All types</option>
            {letters.map((option) => (
              <option key={option.letter} value={option.letter}>
                {option.label}
              </option>
            ))}
          </select>
        </label>
        <label className="block text-xs uppercase tracking-[0.14em] text-muted">
          Status
          <select
            value={statusFilter}
            onChange={(event) => {
              const value = event.target.value;
              if (value === "all" || value === "available" || value === "hold" || value === "sold") {
                setStatusFilter(value);
              }
            }}
            className="mt-1 w-full rounded-lg border border-line bg-paper px-3 py-2 text-sm normal-case tracking-normal text-ink outline-none focus:border-gold"
          >
            <option value="all">All statuses</option>
            <option value="hold">Hold · Inbox for price</option>
            <option value="available">Available</option>
            <option value="sold">Sold / Gone</option>
          </select>
        </label>
        <label className="block text-xs uppercase tracking-[0.14em] text-muted">
          Fulfillment
          <select
            value={fulfillmentFilter}
            onChange={(event) => {
              const value = event.target.value;
              if (value === "all" || value === "dropship" || value === "on_hand") {
                setFulfillmentFilter(value);
              }
            }}
            className="mt-1 w-full rounded-lg border border-line bg-paper px-3 py-2 text-sm normal-case tracking-normal text-ink outline-none focus:border-gold"
          >
            <option value="all">All fulfillment</option>
            <option value="dropship">Dropship · Taobao</option>
            <option value="on_hand">On hand · received</option>
          </select>
        </label>
      </div>

      {visible.length === 0 ? (
        <p
          role="status"
          className="rounded-2xl border border-dashed border-line px-4 py-10 text-center text-sm text-muted"
        >
          No items match this search.
        </p>
      ) : (
        <div className="overflow-x-auto rounded-2xl border border-line">
          <table className="min-w-full text-left text-sm">
            <thead className="border-b border-line bg-blush/50 text-[11px] uppercase tracking-[0.14em] text-muted">
              <tr>
                <th className="px-3 py-3 font-medium">
                  <input
                    type="checkbox"
                    aria-label="Select all shown"
                    checked={visible.length > 0 && visible.every((product) => selected.includes(product.ma))}
                    onChange={(event) => {
                      if (event.target.checked) {
                        setSelected(visible.map((product) => product.ma));
                        return;
                      }
                      setSelected([]);
                    }}
                  />
                </th>
                <th className="px-3 py-3 font-medium"> </th>
                <th className="px-4 py-3 font-medium">Mã</th>
                <th className="px-4 py-3 font-medium">Title</th>
                <th className="px-4 py-3 font-medium">Status</th>
                <th className="px-4 py-3 font-medium">Price</th>
                <th className="hidden px-4 py-3 font-medium lg:table-cell">Source</th>
                <th className="hidden px-4 py-3 font-medium md:table-cell">Colors</th>
                <th className="hidden px-4 py-3 font-medium sm:table-cell">Images</th>
                <th className="px-4 py-3 font-medium"> </th>
              </tr>
            </thead>
            <tbody>
              {visible.map((product) => {
                const thumb = coverSrc(product);
                const imageCount = product.images.filter((image) => image.src.trim()).length;
                return (
                <tr
                  key={product.ma}
                  className="cursor-pointer border-b border-line last:border-0 hover:bg-blush/40"
                  onClick={() => onEdit(product.ma)}
                >
                  <td className="px-3 py-2" onClick={(event) => event.stopPropagation()}>
                    <input
                      type="checkbox"
                      aria-label={`Select ${product.ma}`}
                      checked={selected.includes(product.ma)}
                      onChange={(event) => {
                        setSelected((current) =>
                          event.target.checked
                            ? [...current, product.ma]
                            : current.filter((ma) => ma !== product.ma),
                        );
                      }}
                    />
                  </td>
                  <td className="px-3 py-2">
                    {thumb ? (
                      // eslint-disable-next-line @next/next/no-img-element
                      <img
                        src={thumb}
                        alt=""
                        className="h-14 w-11 rounded-sm object-cover"
                      />
                    ) : (
                      <div className="h-14 w-11 rounded-sm bg-blush" />
                    )}
                  </td>
                  <td className="px-4 py-3">
                    <MaMark ma={product.ma} className="text-[13px] tracking-[0.12em]" />
                  </td>
                  <td className="px-4 py-3">
                    <p className="text-ink">{product.titleEn}</p>
                    {product.titleVn && product.titleVn !== product.titleEn ? (
                      <p className="text-[12px] text-muted">{product.titleVn}</p>
                    ) : null}
                    <p className="mt-0.5 text-[11px] text-muted sm:hidden">
                      {TYPE_LABELS[product.type].nav}
                    </p>
                  </td>
                  <td className="px-4 py-3">
                    <ProductStatusBadge product={product} audience="admin" />
                  </td>
                  <td className="px-4 py-3 tabular-nums text-ink">
                    <PriceCell product={product} />
                  </td>
                  <td className="hidden px-4 py-3 text-[11px] uppercase tracking-[0.12em] text-muted lg:table-cell">
                    {product.fulfillment === "on_hand" ? "On hand" : "Dropship"}
                    {product.sourceLink ? " · link" : ""}
                  </td>
                  <td className="hidden px-4 py-3 md:table-cell">
                    {product.colors.length === 0 ? (
                      <span className="text-muted">—</span>
                    ) : (
                      <span className="flex flex-wrap items-center gap-2">
                        {product.colors.map((color) => (
                          <span key={color.id} className="inline-flex items-center gap-1.5">
                            <span
                              className="inline-block h-4 w-4 shrink-0 rounded-sm border border-black/20"
                              style={{ backgroundColor: color.hex }}
                              title={color.name || color.hex}
                            />
                            <span className="text-[11px] text-muted">{color.name || color.hex}</span>
                          </span>
                        ))}
                      </span>
                    )}
                  </td>
                  <td className="hidden px-4 py-3 tabular-nums text-muted sm:table-cell">
                    {imageCount}
                  </td>
                  <td className="px-4 py-3 text-right">
                    <div className="flex flex-wrap justify-end gap-3">
                      <button
                        type="button"
                        data-testid={`admin-edit-${product.ma}`}
                        className="inline-flex min-h-8 items-center text-xs uppercase tracking-[0.12em] text-ink hover:text-gold-deep"
                        onClick={(event) => {
                          event.stopPropagation();
                          onEdit(product.ma);
                        }}
                      >
                        Edit
                      </button>
                      {isKnownSeedMa(product.ma) ? (
                        <span className="text-xs uppercase tracking-[0.12em] text-muted">Hub mã stays</span>
                      ) : (
                        <Link
                          href={`/admin/edit/${product.ma}#ma`}
                          data-testid={`admin-rename-open-${product.ma}`}
                          className="inline-flex min-h-8 items-center text-xs uppercase tracking-[0.12em] text-gold-deep hover:text-ink"
                          onClick={(event) => event.stopPropagation()}
                        >
                          Change mã
                        </Link>
                      )}
                      {product.status !== "sold" ? (
                        <Link
                          href={`/m/${product.ma}`}
                          target="_blank"
                          className="inline-flex min-h-8 items-center text-xs uppercase tracking-[0.12em] text-muted hover:text-ink"
                          onClick={(event) => event.stopPropagation()}
                        >
                          Preview
                        </Link>
                      ) : (
                        <span className="text-xs uppercase tracking-[0.12em] text-muted">Hidden</span>
                      )}
                    </div>
                  </td>
                </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
