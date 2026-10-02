import { assertNever } from "./kinds";
import { isHeldIncompleteMa } from "./held-incomplete";
import { normalizeMa } from "./mint";
import type { StoreFile } from "./store-backend";

/**
 * Dry-run by default. A live rewrite runs only when mode is "apply" and
 * `confirmation` is exactly `BOSS_CONFIRM_SELL_USD`. This module does not
 * call Blob, Square, or Meta by itself.
 *
 * The 13-row rewrite changes `sell_usd` only. `price` and every other field
 * stay as stored. S06, held incomplete mãs, and Q02 are not in the map.
 */

export const BOSS_CONFIRM_SELL_USD = "Boss says: apply the 13 intake sell_usd backfill";

export const PUBLIC_CATALOG_URL =
  "https://efsi0jejsfy7j058.public.blob.vercel-storage.com/sassy-closet-shop/catalog.v1.json";

export const S06_LOCKED_PRICE_USD = 25;

export const NEVER_LIST_MAS = ["Q02"] as const;

export const SELL_USD_BACKFILL = [
  { ma: "A01", storedSellUsd: "25", blobPriceUsd: 27 },
  { ma: "A02", storedSellUsd: "22", blobPriceUsd: 23 },
  { ma: "A03", storedSellUsd: "19", blobPriceUsd: 22 },
  { ma: "A04", storedSellUsd: "20", blobPriceUsd: 21 },
  { ma: "B01", storedSellUsd: "41", blobPriceUsd: 46 },
  { ma: "B02", storedSellUsd: "30", blobPriceUsd: 31 },
  { ma: "J01", storedSellUsd: "30", blobPriceUsd: 29 },
  { ma: "J02", storedSellUsd: "35", blobPriceUsd: 40 },
  { ma: "K01", storedSellUsd: "37", blobPriceUsd: 36 },
  { ma: "P03", storedSellUsd: "18", blobPriceUsd: 11 },
  { ma: "P04", storedSellUsd: "13", blobPriceUsd: 10 },
  { ma: "P05", storedSellUsd: "23", blobPriceUsd: 25 },
  { ma: "S01", storedSellUsd: "28", blobPriceUsd: 39 },
] as const;

export type SellUsdBackfillSpec = (typeof SELL_USD_BACKFILL)[number];

export type BackfillMode = "dry-run" | "apply";

export type SellUsdChange = {
  ma: string;
  from: string;
  to: string;
};

export type SellUsdRowDecision =
  | { ma: string; action: "change"; from: string; to: string }
  | { ma: string; action: "unchanged"; sellUsd: string }
  | { ma: string; action: "refuse"; reason: string };

export type SellUsdPlan = {
  mode: "dry-run";
  rows: SellUsdRowDecision[];
  changes: SellUsdChange[];
  applyAllowed: boolean;
  blockReason: string | null;
  s06CatalogPriceUsd: number | null;
  blockedPresent: string[];
};

type SellRow = {
  ma: string;
  sell_usd: string;
};

export function resolveBackfillMode(
  flagApply: boolean,
  confirmation: string,
  expectedPhrase: string,
): BackfillMode {
  if (!flagApply) return "dry-run";
  if (confirmation !== expectedPhrase) {
    throw new Error(`Live write refused. Boss must say exactly: ${expectedPhrase}`);
  }
  return "apply";
}

export function sellRewriteBlockReason(ma: string): string | null {
  const key = normalizeMa(ma);
  if (isHeldIncompleteMa(key)) return `${key} is held incomplete and is never published`;
  if ((NEVER_LIST_MAS as readonly string[]).includes(key)) return `${key} is never listed`;
  if (key === "S06") return "S06 stays $25 and is not in the sell_usd backfill";
  return null;
}

export function catalogPriceIndex(doc: unknown): Map<string, number | null> {
  if (!isRecord(doc) || !Array.isArray(doc.products)) {
    throw new Error("Catalog JSON has no products array.");
  }
  const map = new Map<string, number | null>();
  for (const raw of doc.products) {
    if (!isRecord(raw) || typeof raw.ma !== "string") continue;
    const ma = normalizeMa(raw.ma);
    if (!ma) continue;
    if (map.has(ma)) throw new Error(`Duplicate catalog mã ${ma}.`);
    map.set(ma, readCatalogPrice(raw.priceUsd, ma));
  }
  return map;
}

export function planSellUsdBackfill(
  submissions: readonly SellRow[],
  catalogPrices: ReadonlyMap<string, number | null>,
): SellUsdPlan {
  const blockedPresent = blockedMasPresent(submissions);
  const s06CatalogPriceUsd = catalogPrices.has("S06") ? catalogPrices.get("S06") ?? null : null;
  const duplicate = duplicateMa(submissions);
  if (duplicate) {
    return emptyPlan(s06CatalogPriceUsd, blockedPresent, `Duplicate intake mã ${duplicate}.`);
  }

  const byMa = indexByMa(submissions);
  const rows: SellUsdRowDecision[] = [];
  for (const spec of SELL_USD_BACKFILL) {
    const blocked = sellRewriteBlockReason(spec.ma);
    if (blocked) {
      rows.push({ ma: spec.ma, action: "refuse", reason: blocked });
      continue;
    }
    rows.push(decideRow(spec, byMa.get(spec.ma), catalogPrices.get(spec.ma)));
  }

  const changes = rows.flatMap((row) =>
    row.action === "change" ? [{ ma: row.ma, from: row.from, to: row.to }] : [],
  );
  const blockReason = planBlockReason(rows, s06CatalogPriceUsd, changes.length);
  return {
    mode: "dry-run",
    rows,
    changes,
    applyAllowed: blockReason === null,
    blockReason,
    s06CatalogPriceUsd,
    blockedPresent,
  };
}

export function storeWithSellUsdChanges(store: StoreFile, plan: SellUsdPlan): StoreFile {
  if (!plan.applyAllowed || plan.blockReason) {
    throw new Error(plan.blockReason ?? "Sell_usd backfill is not allowed.");
  }
  const changeByMa = new Map(plan.changes.map((change) => [change.ma, change]));
  const submissions = store.submissions.map((row) => {
    const key = normalizeMa(row.ma);
    if (sellRewriteBlockReason(key) || !changeByMa.has(key)) return row;
    const change = changeByMa.get(key);
    if (!change || row.sell_usd.trim() !== change.from) {
      throw new Error(`Stored sell_usd for ${key} is not ${change?.from ?? "?"}.`);
    }
    return { ...row, sell_usd: change.to };
  });
  const next: StoreFile = { ...store, submissions };
  assertSellUsdWriteSafe(store, next, plan);
  return next;
}

export async function persistSellUsdBackfill(input: {
  mode: BackfillMode;
  confirmation: string;
  store: StoreFile;
  catalogPrices: ReadonlyMap<string, number | null>;
  writeStore: (store: StoreFile) => Promise<void>;
}): Promise<{ persisted: boolean; plan: SellUsdPlan; store: StoreFile }> {
  const plan = planSellUsdBackfill(input.store.submissions, input.catalogPrices);
  switch (input.mode) {
    case "dry-run":
      return { persisted: false, plan, store: input.store };
    case "apply": {
      if (input.confirmation !== BOSS_CONFIRM_SELL_USD) {
        throw new Error("Live write refused. Boss confirmation does not match.");
      }
      if (!plan.applyAllowed || plan.blockReason) {
        throw new Error(plan.blockReason ?? "Sell_usd backfill is not allowed.");
      }
      const next = storeWithSellUsdChanges(input.store, plan);
      await input.writeStore(next);
      return { persisted: true, plan, store: next };
    }
    default:
      return assertNever(input.mode, "unknown backfill mode");
  }
}

function decideRow(
  spec: SellUsdBackfillSpec,
  row: SellRow | undefined,
  catalogPrice: number | null | undefined,
): SellUsdRowDecision {
  if (!row) return { ma: spec.ma, action: "refuse", reason: `${spec.ma} has no intake form.` };
  if (typeof row.sell_usd !== "string") {
    return { ma: spec.ma, action: "refuse", reason: `${spec.ma} sell_usd is not a string.` };
  }
  if (catalogPrice === undefined) {
    return { ma: spec.ma, action: "refuse", reason: `${spec.ma} is missing from the catalog.` };
  }
  if (catalogPrice !== spec.blobPriceUsd) {
    return {
      ma: spec.ma,
      action: "refuse",
      reason: `${spec.ma} catalog price is ${String(catalogPrice)} and the locked Blob price is ${String(spec.blobPriceUsd)}.`,
    };
  }
  const stored = row.sell_usd.trim();
  const target = String(spec.blobPriceUsd);
  if (stored === target) return { ma: spec.ma, action: "unchanged", sellUsd: stored };
  if (stored !== spec.storedSellUsd) {
    return {
      ma: spec.ma,
      action: "refuse",
      reason: `${spec.ma} stored sell_usd is ${stored || "(blank)"} and the expected lag is ${spec.storedSellUsd}.`,
    };
  }
  return { ma: spec.ma, action: "change", from: spec.storedSellUsd, to: target };
}

function planBlockReason(
  rows: readonly SellUsdRowDecision[],
  s06CatalogPriceUsd: number | null,
  changeCount: number,
): string | null {
  if (s06CatalogPriceUsd !== S06_LOCKED_PRICE_USD) {
    return "S06 catalog price must be $25 before any sell_usd write.";
  }
  for (const row of rows) {
    switch (row.action) {
      case "change":
      case "unchanged":
        break;
      case "refuse":
        return row.reason;
      default:
        return assertNever(row, "unknown sell_usd row decision");
    }
  }
  if (changeCount === 0) return "No sell_usd rows need a rewrite.";
  return null;
}

function assertSellUsdWriteSafe(before: StoreFile, after: StoreFile, plan: SellUsdPlan): void {
  if (plan.s06CatalogPriceUsd !== S06_LOCKED_PRICE_USD) {
    throw new Error("S06 catalog price must be $25.");
  }
  if (before.submissions.length !== after.submissions.length) {
    throw new Error("Sell_usd backfill changed the intake row count.");
  }
  const changeByMa = new Map(plan.changes.map((change) => [change.ma, change]));
  for (let i = 0; i < before.submissions.length; i += 1) {
    const prev = before.submissions[i];
    const next = after.submissions[i];
    if (!prev || !next) throw new Error("Sell_usd backfill dropped a row.");
    if (prev.ma !== next.ma) throw new Error(`Sell_usd backfill moved mã ${prev.ma}.`);
    const key = normalizeMa(prev.ma);
    const blocked = sellRewriteBlockReason(key);
    const change = changeByMa.get(key);
    if (blocked || !change) {
      if (prev !== next) throw new Error(`${key} was rewritten.`);
      continue;
    }
    if (next.sell_usd !== change.to || prev.sell_usd.trim() !== change.from) {
      throw new Error(`${key} sell_usd rewrite does not match the locked map.`);
    }
    if (!sameExceptSellUsd(prev, next)) {
      throw new Error(`${key} changed a field other than sell_usd.`);
    }
  }
  const s06 = after.submissions.find((row) => normalizeMa(row.ma) === "S06");
  if (s06 && s06.sell_usd.trim() !== "" && s06.sell_usd.trim() !== String(S06_LOCKED_PRICE_USD)) {
    throw new Error("S06 sell_usd must stay blank or $25.");
  }
  for (const ma of NEVER_LIST_MAS) {
    const prev = before.submissions.find((row) => normalizeMa(row.ma) === ma);
    const next = after.submissions.find((row) => normalizeMa(row.ma) === ma);
    if (prev !== next) throw new Error(`${ma} was rewritten.`);
  }
}

function sameExceptSellUsd(before: { sell_usd: string }, after: { sell_usd: string }): boolean {
  const { sell_usd: previousSell, ...previousRest } = before;
  const { sell_usd: nextSell, ...nextRest } = after;
  void previousSell;
  void nextSell;
  return JSON.stringify(previousRest) === JSON.stringify(nextRest);
}

function emptyPlan(
  s06CatalogPriceUsd: number | null,
  blockedPresent: string[],
  blockReason: string,
): SellUsdPlan {
  return {
    mode: "dry-run",
    rows: [],
    changes: [],
    applyAllowed: false,
    blockReason,
    s06CatalogPriceUsd,
    blockedPresent,
  };
}

function blockedMasPresent(submissions: readonly SellRow[]): string[] {
  const found: string[] = [];
  for (const row of submissions) {
    const key = normalizeMa(row.ma);
    if (sellRewriteBlockReason(key)) found.push(key);
  }
  return found;
}

function duplicateMa(submissions: readonly SellRow[]): string | null {
  const seen = new Set<string>();
  for (const row of submissions) {
    const key = normalizeMa(row.ma);
    if (seen.has(key)) return key;
    seen.add(key);
  }
  return null;
}

function indexByMa<T extends SellRow>(rows: readonly T[]): Map<string, T> {
  const map = new Map<string, T>();
  for (const row of rows) map.set(normalizeMa(row.ma), row);
  return map;
}

function readCatalogPrice(value: unknown, ma: string): number | null {
  if (value === null) return null;
  if (typeof value !== "number" || !Number.isFinite(value)) {
    throw new Error(`Catalog price for ${ma} is not a number.`);
  }
  return value;
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}
