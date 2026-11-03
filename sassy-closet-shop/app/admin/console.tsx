"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { CatalogList } from "@/app/admin/catalog-list";
import { FormAlert } from "@/app/admin/fields";
import { IntakeImportPanel } from "@/app/admin/intake-import";
import { ItemForm } from "@/app/admin/item-form";
import { PipelineTracker } from "@/app/admin/pipeline-tracker";
import { SettingsPanel } from "@/app/admin/settings-panel";
import {
  persistAdminToast,
  takePersistedAdminToast,
  ToastHost,
  type AdminToast,
} from "@/app/admin/toasts";
import { KNOWN_SEED_MAS, catalogBlobPath } from "@/lib/catalog-contract";
import type { SiteRuntimeInfo } from "@/lib/site-runtime";
import type { CatalogStorageInfo } from "@/lib/storage-info";
import type { PipelineDocument } from "@/lib/pipeline";
import type { Product, SiteSettings } from "@/lib/types";

export type AdminMode = "list" | "add" | "edit" | "settings" | "intake" | "pipeline";

function backendLabel(backend: CatalogStorageInfo["backend"]): string {
  switch (backend) {
    case "blob":
      return "Vercel Blob";
    case "kv":
      return "Vercel KV";
    case "local":
      return "Local file (data/live-catalog.json)";
    case "seed":
      return "Seed JSON (bootstrap only)";
    default: {
      const _exhaustive: never = backend;
      return _exhaustive;
    }
  }
}

function storageLabel(storage: CatalogStorageInfo): string {
  const write = backendLabel(storage.backend);
  if (!storage.reading || storage.reading === storage.backend) {
    return `${write} · shop and admin share this catalog`;
  }
  return `${write} writes · shop is still reading ${backendLabel(storage.reading)}`;
}

function navClass(active: boolean): string {
  return `inline-flex min-h-11 shrink-0 touch-manipulation items-center text-left ${active ? "text-ink" : "text-muted hover:text-ink"}`;
}

export function AdminConsole({
  initialProducts,
  initialSettings,
  storage,
  site,
  pipeline,
  mode,
  editMa,
  notice,
}: {
  initialProducts: Product[];
  initialSettings: SiteSettings;
  storage: CatalogStorageInfo;
  site: SiteRuntimeInfo;
  pipeline: PipelineDocument;
  mode: AdminMode;
  editMa?: string;
  notice?: string;
}) {
  const router = useRouter();
  const [products, setProducts] = useState(initialProducts);
  const [settings, setSettings] = useState(initialSettings);
  const [toasts, setToasts] = useState<AdminToast[]>([]);

  useEffect(() => {
    setProducts(initialProducts);
    setSettings(initialSettings);
  }, [initialProducts, initialSettings]);

  const pushToast = useCallback((tone: AdminToast["tone"], text: string) => {
    persistAdminToast(tone, text);
    const id = `${Date.now()}-${Math.random().toString(16).slice(2)}`;
    setToasts((current) => [...current, { id, tone, text }]);
    window.setTimeout(() => {
      setToasts((current) => current.filter((toast) => toast.id !== id));
    }, 9000);
  }, []);

  useEffect(() => {
    const persisted = takePersistedAdminToast();
    if (!persisted) {
      return;
    }
    const id = `${Date.now()}-${Math.random().toString(16).slice(2)}`;
    setToasts((current) => [...current, { id, ...persisted }]);
    window.setTimeout(() => {
      setToasts((current) => current.filter((toast) => toast.id !== id));
    }, 9000);
  }, []);

  useEffect(() => {
    if (!storage.canWrite) {
      pushToast(
        "error",
        "Storage is not configured. Add will fail until BLOB_READ_WRITE_TOKEN (or KV) is set on Vercel.",
      );
    }
  }, [pushToast, storage.canWrite]);

  function sync(nextProducts: Product[], nextSettings: SiteSettings) {
    setProducts(nextProducts);
    setSettings(nextSettings);
    router.refresh();
  }

  const editing = mode === "edit" && editMa ? products.find((item) => item.ma === editMa) : undefined;

  return (
    <div className="relative">
      <ToastHost
        toasts={toasts}
        onDismiss={(id) => setToasts((current) => current.filter((toast) => toast.id !== id))}
      />
      <header className="border-b border-line pb-6">
        <div className="flex flex-wrap items-end justify-between gap-4">
          <div>
            <p className="text-[11px] uppercase tracking-[0.18em] text-muted">
              Test only · {site.mode === "official" ? "Official" : "Sell-test"} · {site.id} · not in
              the main nav
            </p>
            <h1 className="mt-2 font-display text-4xl text-ink sm:text-5xl">Sell ops</h1>
          </div>
          <Link href="/" className="inline-flex min-h-8 items-center text-sm text-muted hover:text-ink">
            Back to shop
          </Link>
        </div>
        <p className="mt-3 max-w-2xl text-sm text-muted">
          Storage: {storageLabel(storage)}. Vercel Blob is the live shop catalog store
          {storage.backend === "blob" ? "." : " (this session is a local/KV stand-in)."}
          {storage.canWrite ? "" : " Add and Save will error until a store is attached."}
          {storage.canUpload ? "" : " Image uploads need Blob; URL paste still works."}
        </p>
        <p className="mt-2 max-w-2xl text-sm text-muted">
          Boxes only — no names on the swatches. The shop shows color names. Hub allowlist{" "}
          {KNOWN_SEED_MAS.join(" ")} · {products.length} mãs live · Blob key {catalogBlobPath(site.id)}{" "}
          (never intake store.json). Boss Add assigns the next unused letter-code on Save — unused
          codes are not shop tiles until the receipt. Change mã is on the catalog and on Edit —
          unused codes only, hub ten stay. Save is Blob write + revalidate + two warms — receipt or
          error, never silent.
        </p>
        {storage.reading === "seed" && storage.canWrite ? (
          <p className="mt-2 max-w-2xl text-sm text-gold-deep">
            Shop is still on seed until the first Save lands in the live store. After Save, shop and
            admin must show the same mãs.
          </p>
        ) : null}
      </header>

      <div className="lg:grid lg:grid-cols-[12.5rem_minmax(0,1fr)] lg:gap-10">
        <nav
          className="mt-6 flex gap-6 overflow-x-auto tab-scroll text-[11px] font-medium uppercase tracking-[0.18em] lg:mt-8 lg:flex-col lg:gap-3 lg:overflow-visible"
          aria-label="Admin"
        >
          <Link href="/admin" className={navClass(mode === "list")}>
            Catalog
          </Link>
          <Link href="/admin/intake" className={navClass(mode === "intake")}>
            Intake
          </Link>
          <Link href="/admin/new" className={navClass(mode === "add")}>
            Add mã
          </Link>
          <Link href="/admin/pipeline" className={navClass(mode === "pipeline")}>
            Pipeline
          </Link>
          <Link
            href={editMa ? `/admin/edit/${editMa}` : "/admin"}
            className={navClass(mode === "edit")}
          >
            Edit item
          </Link>
          <Link href="/admin/settings" className={navClass(mode === "settings")}>
            Site settings
          </Link>
        </nav>

        <div className="py-8">
          {mode === "settings" ? (
            <SettingsPanel
              initial={settings}
              canWrite={storage.canWrite}
              site={site}
              onToast={pushToast}
              onSaved={sync}
            />
          ) : mode === "intake" ? (
            <IntakeImportPanel products={products} canWrite={storage.canWrite} onToast={pushToast} />
          ) : mode === "pipeline" ? (
            <PipelineTracker
              products={products}
              initial={pipeline}
              canWrite={storage.canWrite}
              onToast={pushToast}
            />
          ) : mode === "add" ? (
            <ItemForm
              mode="add"
              products={products}
              storage={storage}
              onToast={pushToast}
              onCancel={() => router.push("/admin")}
              onCatalog={(nextProducts, nextSettings, options) => {
                if (options?.nextMa) {
                  router.replace(`/admin/edit/${options.nextMa}?added=1`);
                  return;
                }
                setProducts(nextProducts);
                setSettings(nextSettings);
              }}
            />
          ) : mode === "edit" && editing ? (
            <ItemForm
              key={editing.ma}
              mode="edit"
              product={editing}
              products={products}
              storage={storage}
              notice={notice}
              onToast={pushToast}
              onCancel={() => router.push("/admin")}
              onCatalog={(nextProducts, nextSettings, options) => {
                setProducts(nextProducts);
                setSettings(nextSettings);
                if (options?.removed) {
                  router.replace(`/admin?removed=${encodeURIComponent(editing.ma)}`);
                  return;
                }
                if (options?.renamedTo && options.renamedTo !== editing.ma) {
                  router.replace(
                    `/admin/edit/${options.renamedTo}?renamedFrom=${encodeURIComponent(editing.ma)}`,
                  );
                }
              }}
            />
          ) : mode === "edit" ? (
            <p className="text-sm text-gold-deep">
              Mã {editMa} is not in the catalog.{" "}
              <Link href="/admin" className="underline">
                Back to catalog
              </Link>
            </p>
          ) : (
            <div className="space-y-4">
              {notice ? <FormAlert tone="ok" text={notice} /> : null}
              <CatalogList
                products={products}
                pipeline={pipeline}
                canWrite={storage.canWrite}
                onAdd={() => router.push("/admin/new")}
                onEdit={(ma) => router.push(`/admin/edit/${ma}`)}
                onHeld={sync}
                onToast={pushToast}
              />
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
