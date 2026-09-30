import { assertNever } from "@/lib/kinds";
import type { ShopCatalogList, ShopCatalogStatus } from "@/lib/shop-catalog";

export type DatasetLane = "live" | "held" | "sold";

export type ShopDatasetRow = {
  ma: string;
  status: ShopCatalogStatus;
  priceUsd: number | null;
};

export type DatasetEntry = {
  ma: string;
  lane: DatasetLane;
  priceUsd: number | null;
  inIntake: boolean;
};

export type DatasetView = {
  ready: boolean;
  entries: DatasetEntry[];
  liveCount: number;
  heldMas: string[];
  shopOnlyLive: DatasetEntry[];
};

const MA_CODE = /^[A-Z]\d{2,3}$/;
const BLOB_HOST = /^[a-z0-9-]+$/;

export function formatMaList(mas: readonly string[], limit = 8): string {
  if (mas.length <= limit) return mas.join(", ");
  return `${mas.slice(0, limit).join(", ")} +${String(mas.length - limit)}`;
}

export function datasetLaneLabel(lane: DatasetLane): string {
  switch (lane) {
    case "live":
      return "Live";
    case "held":
      return "Held · chưa xong";
    case "sold":
      return "Sold";
    default:
      return assertNever(lane, "unknown dataset lane");
  }
}

export function rowsFromShopCatalog(list: ShopCatalogList): ShopDatasetRow[] | null {
  if (!list.ok) return null;
  const rows: ShopDatasetRow[] = [];
  for (const product of list.products) {
    const ma = cleanMa(product.ma);
    if (!ma) continue;
    rows.push({ ma, status: product.status, priceUsd: product.priceUsd });
  }
  return rows;
}

/**
 * Public Blob URL for catalog.v1.json, taken from a shop sitemap image host.
 * Returns null unless the host is a public Vercel Blob store.
 */
export function publicCatalogUrlFromSitemap(xml: string): string | null {
  const match = xml.match(/https:\/\/([a-z0-9-]+)\.public\.blob\.vercel-storage\.com\//);
  const store = match?.[1] ?? "";
  if (!store || !BLOB_HOST.test(store)) return null;
  return `https://${store}.public.blob.vercel-storage.com/sassy-closet-shop/catalog.v1.json`;
}

export function isAllowedShopOrigin(origin: string): boolean {
  try {
    const url = new URL(origin);
    return (
      url.protocol === "https:" &&
      (url.hostname === "sassycloset.vercel.app" || url.hostname === "sassy-closet-shop.vercel.app") &&
      url.pathname === "/" &&
      url.search === "" &&
      url.username === "" &&
      url.password === ""
    );
  } catch {
    return false;
  }
}

/**
 * Live = shop catalog status available.
 * Held = catalog hold, or an intake mã that is not in the catalog (not finished, not on the sell site).
 * Sold stays sold. Mãs that are in neither list are not added.
 */
export function buildIntakeDataset(
  intakeMas: readonly string[],
  shop: readonly ShopDatasetRow[] | null,
): DatasetView {
  if (!shop) {
    return { ready: false, entries: [], liveCount: 0, heldMas: [], shopOnlyLive: [] };
  }

  const shopByMa = new Map<string, ShopDatasetRow>();
  for (const row of shop) {
    const ma = cleanMa(row.ma);
    if (!ma || shopByMa.has(ma)) continue;
    shopByMa.set(ma, { ma, status: row.status, priceUsd: row.priceUsd });
  }

  const intakeOrder: string[] = [];
  const seenIntake = new Set<string>();
  for (const raw of intakeMas) {
    const ma = cleanMa(raw);
    if (!ma || seenIntake.has(ma)) continue;
    seenIntake.add(ma);
    intakeOrder.push(ma);
  }

  const entries: DatasetEntry[] = [];
  for (const ma of intakeOrder) {
    const row = shopByMa.get(ma);
    entries.push(entryFor(ma, row, true));
  }

  const shopOnlyLive: DatasetEntry[] = [];
  for (const row of shopByMa.values()) {
    if (seenIntake.has(row.ma)) continue;
    const entry = entryFor(row.ma, row, false);
    entries.push(entry);
    if (entry.lane === "live") shopOnlyLive.push(entry);
  }

  const heldMas = entries.filter((entry) => entry.lane === "held").map((entry) => entry.ma);
  const liveCount = entries.filter((entry) => entry.lane === "live").length;
  return { ready: true, entries, liveCount, heldMas, shopOnlyLive };
}

export function datasetEntryForMa(view: DatasetView, ma: string): DatasetEntry | null {
  const key = cleanMa(ma);
  if (!key) return null;
  return view.entries.find((entry) => entry.ma === key) ?? null;
}

function entryFor(ma: string, row: ShopDatasetRow | undefined, inIntake: boolean): DatasetEntry {
  if (!row) {
    return { ma, lane: "held", priceUsd: null, inIntake };
  }
  return { ma, lane: laneForStatus(row.status), priceUsd: row.priceUsd, inIntake };
}

function laneForStatus(status: ShopCatalogStatus): DatasetLane {
  switch (status) {
    case "available":
      return "live";
    case "hold":
      return "held";
    case "sold":
      return "sold";
    default:
      return assertNever(status, "unknown shop catalog status");
  }
}

function cleanMa(ma: string): string | null {
  const key = ma.trim().toUpperCase();
  return MA_CODE.test(key) ? key : null;
}
