"use client";

import { useMemo, useState, type FormEvent } from "react";
import type { ShopCatalogList, ShopCatalogRow, ShopCatalogStatus } from "@/lib/shop-catalog";

type SaveReceipt = {
  ok?: boolean;
  error?: string;
  blobWritten?: boolean;
  revalidated?: boolean;
  ma?: string;
};

export function ShopCatalogDesk({ initial }: { initial: ShopCatalogList }) {
  const [products, setProducts] = useState<ShopCatalogRow[]>(initial.ok ? initial.products : []);
  const [selectedMa, setSelectedMa] = useState(initial.ok ? (initial.products[0]?.ma ?? "") : "");
  const [busy, setBusy] = useState(false);
  const [notice, setNotice] = useState<string | null>(null);
  const selected = useMemo(
    () => products.find((product) => product.ma === selectedMa) ?? null,
    [products, selectedMa],
  );

  async function onSave(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!selected) {
      return;
    }
    const form = new FormData(event.currentTarget);
    const colors = selected.colors.map((color) => ({
      id: color.id,
      name: String(form.get(`color-${color.id}`) ?? ""),
    }));
    const patch: Record<string, unknown> = {
      ma: selected.ma,
      titleVn: String(form.get("titleVn") ?? ""),
      titleEn: String(form.get("titleEn") ?? ""),
      descriptionVn: String(form.get("descriptionVn") ?? ""),
      descriptionEn: String(form.get("descriptionEn") ?? ""),
      colors,
    };
    const status = String(form.get("status") ?? selected.status);
    patch.status = status;
    if (status === "hold") {
      patch.priceUsd = null;
    } else {
      const raw = String(form.get("priceUsd") ?? "").trim();
      patch.priceUsd = raw === "" ? null : Number(raw);
    }
    setBusy(true);
    setNotice(null);
    try {
      const response = await fetch("/api/shop-catalog/save", {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify(patch),
      });
      const receipt = (await response.json()) as SaveReceipt;
      if (!response.ok || !receipt.ok) {
        const wrote = receipt.blobWritten ? " Blob was written." : "";
        setNotice(`${receipt.error || "Save failed."}${wrote}`);
        return;
      }
      setNotice(`Saved ${receipt.ma}. Shop catalog updated and revalidated.`);
      const refreshed = await fetch("/api/shop-catalog");
      const body = (await refreshed.json()) as ShopCatalogList & { ok?: boolean };
      if (refreshed.ok && body.ok && body.products) {
        setProducts(body.products);
      }
    } catch {
      setNotice("Save could not reach the server.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <main className="mx-auto max-w-lg px-4 py-8 text-[#5c3d48]">
      <p className="text-[11px] font-semibold uppercase tracking-[0.16em] text-[#a85d74]">Intake · Shop tools</p>
      <div className="mt-1 flex items-start justify-between gap-3">
        <h1 className="text-[21px] font-semibold text-[#3c2a2e]">Shop catalog</h1>
        <form action="/api/shop-catalog/logout" method="post">
          <button
            type="submit"
            className="inline-flex min-h-11 items-center rounded-full px-3 text-sm font-semibold text-[#5c3d48] ring-1 ring-[#eadfdc]"
          >
            Sign out
          </button>
        </form>
      </div>
      <p className="mt-2 text-[13.5px] leading-relaxed text-[#7d5360]">
        Edits the sell catalog in Blob <span className="font-semibold">sassy-closet-shop/catalog.v1.json</span>, then
        asks the shop to revalidate. Available USD is the catalog price.
      </p>
      <p className="mt-3 text-sm">
        <a className="underline-offset-2 hover:underline" href="/">
          Back to intake
        </a>
        <span className="mx-1">·</span>
        <a className="underline-offset-2 hover:underline" href="/admin">
          Kit export CSV
        </a>
      </p>
      {!initial.ok ? (
        <p role="alert" className="mt-6 text-sm text-[#9b2c2c]">
          {initial.error}
        </p>
      ) : null}
      {initial.ok && products.length === 0 ? <p className="mt-6 text-sm">No products in the shop catalog.</p> : null}
      {initial.ok && products.length > 0 ? (
        <div className="mt-6 grid gap-4">
          <label className="grid gap-1 text-sm">
            <span className="font-semibold text-[#3c2a2e]">Mã</span>
            <select
              className="min-h-11 rounded-2xl bg-white px-3 ring-1 ring-[#eadfdc]"
              value={selectedMa}
              onChange={(event) => {
                setSelectedMa(event.target.value);
                setNotice(null);
              }}
            >
              {products.map((product) => (
                <option key={product.ma} value={product.ma}>
                  {product.ma} · {product.titleEn || product.titleVn}
                </option>
              ))}
            </select>
          </label>
          {selected ? <Editor key={selected.ma} product={selected} busy={busy} onSave={onSave} /> : null}
        </div>
      ) : null}
      {notice ? (
        <p role="status" className="mt-4 text-sm text-[#3c2a2e]">
          {notice}
        </p>
      ) : null}
    </main>
  );
}

function Editor({
  product,
  busy,
  onSave,
}: {
  product: ShopCatalogRow;
  busy: boolean;
  onSave: (event: FormEvent<HTMLFormElement>) => void;
}) {
  return (
    <form className="grid gap-3" onSubmit={onSave}>
      <Field label="Title VN" name="titleVn" defaultValue={product.titleVn} />
      <Field label="Title EN" name="titleEn" defaultValue={product.titleEn} />
      <Area label="Description VN" name="descriptionVn" defaultValue={product.descriptionVn} />
      <Area label="Description EN" name="descriptionEn" defaultValue={product.descriptionEn} />
      <UnlockedPrice product={product} />
      {product.colors.length > 0 ? (
        <fieldset className="grid gap-2">
          <legend className="text-sm font-semibold text-[#3c2a2e]">Colors</legend>
          {product.colors.map((color) => (
            <label key={color.id} className="grid gap-1 text-sm">
              <span className="text-[#7d5360]">{color.id}</span>
              <input
                name={`color-${color.id}`}
                defaultValue={color.name}
                className="min-h-11 rounded-2xl bg-white px-3 ring-1 ring-[#eadfdc]"
              />
            </label>
          ))}
        </fieldset>
      ) : (
        <p className="text-sm text-[#7d5360]">No colors on this mã.</p>
      )}
      <button
        type="submit"
        disabled={busy}
        className="inline-flex min-h-11 items-center justify-center rounded-full bg-primary px-5 font-bold text-primary-foreground disabled:opacity-60"
      >
        {busy ? "Saving…" : "Save to shop"}
      </button>
    </form>
  );
}

function UnlockedPrice({ product }: { product: ShopCatalogRow }) {
  return (
    <div className="grid gap-3">
      <label className="grid gap-1 text-sm">
        <span className="font-semibold text-[#3c2a2e]">Status</span>
        <select
          name="status"
          defaultValue={product.status}
          className="min-h-11 rounded-2xl bg-white px-3 ring-1 ring-[#eadfdc]"
        >
          {(["available", "hold", "sold"] as const satisfies readonly ShopCatalogStatus[]).map((status) => (
            <option key={status} value={status}>
              {status}
            </option>
          ))}
        </select>
      </label>
      <Field
        label="Price USD"
        name="priceUsd"
        defaultValue={product.priceUsd === null ? "" : String(product.priceUsd)}
      />
    </div>
  );
}

function Field({ label, name, defaultValue }: { label: string; name: string; defaultValue: string }) {
  return (
    <label className="grid gap-1 text-sm">
      <span className="font-semibold text-[#3c2a2e]">{label}</span>
      <input
        name={name}
        defaultValue={defaultValue}
        className="min-h-11 rounded-2xl bg-white px-3 ring-1 ring-[#eadfdc]"
      />
    </label>
  );
}

function Area({ label, name, defaultValue }: { label: string; name: string; defaultValue: string }) {
  return (
    <label className="grid gap-1 text-sm">
      <span className="font-semibold text-[#3c2a2e]">{label}</span>
      <textarea
        name={name}
        defaultValue={defaultValue}
        rows={3}
        className="rounded-2xl bg-white px-3 py-2 ring-1 ring-[#eadfdc]"
      />
    </label>
  );
}
