import { lockedBossPrice } from "@/lib/shop-catalog-lock";
import { callShopRevalidate, readShopRevalidateConfig } from "@/lib/shop-revalidate";

export const SHOP_CATALOG_BLOB_PATH = "sassy-closet-shop/catalog.v1.json";
export const SHOP_CATALOG_SITE_ID = "sassy-closet-shop";

export type ShopCatalogStatus = "available" | "hold" | "sold";

export type ShopCatalogColor = {
  id: string;
  name: string;
};

export type ShopCatalogRow = {
  ma: string;
  titleVn: string;
  titleEn: string;
  descriptionVn: string;
  descriptionEn: string;
  priceUsd: number | null;
  status: ShopCatalogStatus;
  locked: boolean;
  shopPriceUsd: number | null;
  colors: ShopCatalogColor[];
};

export type ShopCatalogList =
  | { ok: true; products: ShopCatalogRow[]; updatedAt: string | null; siteId: string }
  | { ok: false; error: string };

export type ShopCatalogPort = {
  read(): Promise<unknown | null>;
  write(body: string): Promise<{ url: string }>;
};

export type ShopCatalogSaveResult =
  | {
      ok: true;
      status: 200;
      ma: string;
      blobWritten: true;
      revalidated: true;
      updatedAt: string;
    }
  | {
      ok: false;
      status: 400 | 404 | 502 | 503;
      error: string;
      blobWritten: boolean;
      ma?: string;
      updatedAt?: string;
    };

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function normalizeMa(ma: string): string {
  return ma.trim().toUpperCase();
}

function isStatus(value: string): value is ShopCatalogStatus {
  return value === "available" || value === "hold" || value === "sold";
}

function readStatus(value: unknown, ma: string): ShopCatalogStatus | string {
  if (typeof value !== "string" || !isStatus(value)) {
    return `Mã ${ma} has an invalid status.`;
  }
  return value;
}

function readPrice(value: unknown, ma: string): number | null | string {
  if (value === null) {
    return null;
  }
  if (typeof value !== "number" || !Number.isFinite(value) || value < 0 || value > 100000) {
    return `Mã ${ma} has an invalid USD price.`;
  }
  const cents = Math.round(value * 100);
  if (Math.abs(value * 100 - cents) > 1e-6) {
    return `Mã ${ma} price must be dollars and cents.`;
  }
  return cents / 100;
}

function pairingError(status: ShopCatalogStatus, priceUsd: number | null, ma: string): string | null {
  switch (status) {
    case "hold":
      return priceUsd === null ? null : `Hold ${ma} cannot have a USD price.`;
    case "available":
      return priceUsd === null ? `Available ${ma} needs a USD price.` : null;
    case "sold":
      return null;
    default: {
      const _exhaustive: never = status;
      return _exhaustive;
    }
  }
}

function readText(value: unknown, label: string, max: number, allowEmpty: boolean): string | null {
  if (typeof value !== "string") {
    return null;
  }
  const trimmed = value.trim();
  if ((!allowEmpty && trimmed.length === 0) || trimmed.length > max) {
    return null;
  }
  return trimmed;
}

function productMa(product: Record<string, unknown>): string {
  return typeof product.ma === "string" ? normalizeMa(product.ma) : "";
}

export function listShopCatalog(document: unknown): ShopCatalogList {
  if (!isRecord(document)) {
    return { ok: false, error: "Shop catalog is not catalog.v1." };
  }
  if (document.schema !== "catalog.v1" || document.version !== 1) {
    return { ok: false, error: "Shop catalog is not catalog.v1." };
  }
  if (document.siteId !== SHOP_CATALOG_SITE_ID) {
    return { ok: false, error: "Catalog siteId is not sassy-closet-shop." };
  }
  if (!Array.isArray(document.products)) {
    return { ok: false, error: "Shop catalog has no products." };
  }
  const products: ShopCatalogRow[] = [];
  const seen = new Set<string>();
  for (const raw of document.products) {
    if (!isRecord(raw)) {
      return { ok: false, error: "Catalog has a product without a mã." };
    }
    const ma = productMa(raw);
    if (!ma) {
      return { ok: false, error: "Catalog has a product without a mã." };
    }
    if (seen.has(ma)) {
      return { ok: false, error: `Catalog has a duplicate mã ${ma}.` };
    }
    seen.add(ma);
    const status = readStatus(raw.status, ma);
    if (typeof status !== "string" || !isStatus(status)) {
      return { ok: false, error: typeof status === "string" ? status : `Mã ${ma} has an invalid status.` };
    }
    const priceUsd = readPrice(raw.priceUsd, ma);
    if (typeof priceUsd === "string") {
      return { ok: false, error: priceUsd };
    }
    if (!Array.isArray(raw.colors)) {
      return { ok: false, error: `Mã ${ma} colors must be an array.` };
    }
    const colors: ShopCatalogColor[] = [];
    for (const color of raw.colors) {
      if (!isRecord(color) || typeof color.id !== "string" || typeof color.name !== "string") {
        return { ok: false, error: `Mã ${ma} has an invalid color.` };
      }
      colors.push({ id: color.id, name: color.name });
    }
    const locked = lockedBossPrice(ma);
    const titleVn = typeof raw.titleVn === "string" ? raw.titleVn : "";
    const titleEn = typeof raw.titleEn === "string" ? raw.titleEn : "";
    const descriptionVn = typeof raw.descriptionVn === "string" ? raw.descriptionVn : "";
    const descriptionEn = typeof raw.descriptionEn === "string" ? raw.descriptionEn : "";
    products.push({
      ma,
      titleVn,
      titleEn,
      descriptionVn,
      descriptionEn,
      priceUsd,
      status,
      locked: Boolean(locked),
      shopPriceUsd: locked ? locked.priceUsd : priceUsd,
      colors,
    });
  }
  const updatedAt = typeof document.updatedAt === "string" ? document.updatedAt : null;
  return { ok: true, products, updatedAt, siteId: SHOP_CATALOG_SITE_ID };
}

export function applyShopCatalogPatch(
  document: unknown,
  patch: unknown,
  nowIso: string,
):
  | { ok: true; document: Record<string, unknown>; json: string; ma: string; updatedAt: string }
  | { ok: false; error: string } {
  const listed = listShopCatalog(document);
  if (!listed.ok) {
    return listed;
  }
  if (!isRecord(patch) || typeof patch.ma !== "string") {
    return { ok: false, error: "Save needs a mã." };
  }
  const ma = normalizeMa(patch.ma);
  if (!ma) {
    return { ok: false, error: "Save needs a mã." };
  }
  const nextDocument = structuredClone(document) as Record<string, unknown>;
  const products = nextDocument.products;
  if (!Array.isArray(products)) {
    return { ok: false, error: "Shop catalog has no products." };
  }
  const product = products.find((row) => isRecord(row) && productMa(row) === ma);
  if (!isRecord(product)) {
    return { ok: false, error: `Mã ${ma} is not in the catalog.` };
  }

  if ("titleVn" in patch) {
    const titleVn = readText(patch.titleVn, "titleVn", 160, false);
    if (titleVn === null) {
      return { ok: false, error: `Mã ${ma} needs a Vietnamese title.` };
    }
    product.titleVn = titleVn;
  }
  if ("titleEn" in patch) {
    const titleEn = readText(patch.titleEn, "titleEn", 160, false);
    if (titleEn === null) {
      return { ok: false, error: `Mã ${ma} needs an English title.` };
    }
    product.titleEn = titleEn;
  }
  if ("descriptionVn" in patch) {
    const descriptionVn = readText(patch.descriptionVn, "descriptionVn", 4000, true);
    if (descriptionVn === null) {
      return { ok: false, error: `Mã ${ma} Vietnamese description is invalid.` };
    }
    product.descriptionVn = descriptionVn;
  }
  if ("descriptionEn" in patch) {
    const descriptionEn = readText(patch.descriptionEn, "descriptionEn", 4000, true);
    if (descriptionEn === null) {
      return { ok: false, error: `Mã ${ma} English description is invalid.` };
    }
    product.descriptionEn = descriptionEn;
  }

  const storedStatus = readStatus(product.status, ma);
  const storedPrice = readPrice(product.priceUsd, ma);
  if (!isStatus(storedStatus) || typeof storedPrice === "string") {
    return { ok: false, error: `Mã ${ma} cannot be saved.` };
  }

  let status = storedStatus;
  let priceUsd = storedPrice;
  const locked = lockedBossPrice(ma);
  if (locked && ("priceUsd" in patch || "status" in patch)) {
    const nextPrice = "priceUsd" in patch ? readPrice(patch.priceUsd, ma) : storedPrice;
    const nextStatus = "status" in patch ? readStatus(patch.status, ma) : storedStatus;
    if (typeof nextPrice === "string") {
      return { ok: false, error: nextPrice };
    }
    if (!isStatus(nextStatus)) {
      return { ok: false, error: nextStatus };
    }
    if (nextPrice !== storedPrice || nextStatus !== storedStatus) {
      return { ok: false, error: `${ma} price and status are locked.` };
    }
  } else {
    if ("status" in patch) {
      const nextStatus = readStatus(patch.status, ma);
      if (!isStatus(nextStatus)) {
        return { ok: false, error: nextStatus };
      }
      status = nextStatus;
    }
    if ("priceUsd" in patch) {
      const nextPrice = readPrice(patch.priceUsd, ma);
      if (typeof nextPrice === "string") {
        return { ok: false, error: nextPrice };
      }
      priceUsd = nextPrice;
    }
    if (status === "hold") {
      priceUsd = null;
    }
    const paired = pairingError(status, priceUsd, ma);
    if (paired) {
      return { ok: false, error: paired };
    }
    product.status = status;
    product.priceUsd = priceUsd;
  }

  if ("colors" in patch) {
    if (!Array.isArray(patch.colors) || !Array.isArray(product.colors)) {
      return { ok: false, error: `Mã ${ma} colors must stay the existing list.` };
    }
    if (patch.colors.length !== product.colors.length) {
      return { ok: false, error: `Mã ${ma} cannot add or remove colors.` };
    }
    const nextColors = [];
    for (let index = 0; index < product.colors.length; index += 1) {
      const current = product.colors[index];
      const incoming = patch.colors[index];
      if (!isRecord(current) || !isRecord(incoming) || incoming.id !== current.id) {
        return { ok: false, error: `Mã ${ma} cannot add or remove colors.` };
      }
      const name = readText(incoming.name, "color", 80, false);
      if (name === null) {
        return { ok: false, error: `Mã ${ma} color name is empty.` };
      }
      nextColors.push({ ...current, name });
    }
    product.colors = nextColors;
  }

  nextDocument.updatedAt = nowIso;
  return {
    ok: true,
    document: nextDocument,
    json: `${JSON.stringify(nextDocument, null, 2)}\n`,
    ma,
    updatedAt: nowIso,
  };
}

export function memoryShopCatalogPort(initial: unknown | null): ShopCatalogPort & { snapshot: () => string | null } {
  let body = initial === null ? null : `${JSON.stringify(initial, null, 2)}\n`;
  return {
    snapshot() {
      return body;
    },
    async read() {
      if (body === null) {
        return null;
      }
      return JSON.parse(body) as unknown;
    },
    async write(next) {
      body = next;
      return { url: "memory://sassy-closet-shop/catalog.v1.json" };
    },
  };
}

export async function saveShopCatalogProduct(
  port: ShopCatalogPort,
  patch: unknown,
  options?: {
    now?: string;
    revalidate?: () => Promise<{ ok: true } | { ok: false; error: string }>;
  },
): Promise<ShopCatalogSaveResult> {
  const current = await port.read();
  if (current === null) {
    return { ok: false, status: 404, error: "Shop catalog is missing.", blobWritten: false };
  }
  const applied = applyShopCatalogPatch(current, patch, options?.now ?? new Date().toISOString());
  if (!applied.ok) {
    return { ok: false, status: 400, error: applied.error, blobWritten: false };
  }
  if (!options?.revalidate) {
    const config = readShopRevalidateConfig();
    if (!config.ok) {
      return { ok: false, status: 503, error: config.error, blobWritten: false };
    }
  }
  await port.write(applied.json);
  const refreshed = await (options?.revalidate ?? (() => callShopRevalidate()))();
  if (!refreshed.ok) {
    return {
      ok: false,
      status: 502,
      error: refreshed.error,
      blobWritten: true,
      ma: applied.ma,
      updatedAt: applied.updatedAt,
    };
  }
  return {
    ok: true,
    status: 200,
    ma: applied.ma,
    blobWritten: true,
    revalidated: true,
    updatedAt: applied.updatedAt,
  };
}
