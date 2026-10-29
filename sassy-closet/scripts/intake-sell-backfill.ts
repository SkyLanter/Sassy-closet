/**
 * Dry-run by default. Does not read or write the durable intake store unless
 * `--apply-sell` or `--apply-d05` is set and BOSS_CONFIRM is the exact phrase.
 *
 * Dry-run:
 *   npm run intake:sell-backfill
 *   npm run intake:sell-backfill -- --store snapshot.json --catalog catalog.v1.json
 *
 * Live sell_usd rewrite (13 mãs, sell_usd only), after Boss says the phrase:
 *   BOSS_CONFIRM='Boss says: apply the 13 intake sell_usd backfill' \
 *     npm run intake:sell-backfill -- --apply-sell --catalog catalog.v1.json
 *
 * Live D05 form, after Boss says that phrase:
 *   BOSS_CONFIRM='Boss says: add the D05 intake form from Blob' \
 *     npm run intake:sell-backfill -- --apply-d05 --catalog catalog.v1.json
 *
 * Apply reads the durable intake Blob. It does not write the sell catalog,
 * Square, or Meta. `--store` is dry-run only.
 */
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { assertNever } from "../lib/kinds";
import {
  BOSS_CONFIRM_D05_FORM,
  D05_LOCKED_PRICE_USD,
  persistD05IntakeSeed,
  planD05IntakeSeed,
} from "../lib/intake-d05-seed";
import {
  BOSS_CONFIRM_SELL_USD,
  PUBLIC_CATALOG_URL,
  S06_LOCKED_PRICE_USD,
  SELL_USD_BACKFILL,
  catalogPriceIndex,
  persistSellUsdBackfill,
  planSellUsdBackfill,
  resolveBackfillMode,
} from "../lib/intake-sell-backfill";
import { photoContentType, activeBackend, blobConfigured, type StoreFile } from "../lib/store-backend";

type Invocation = {
  applySell: boolean;
  applyD05: boolean;
  confirmation: string;
  storePath: string;
  catalogPath: string;
};

export function parseBackfillArgs(argv: readonly string[], envConfirm = ""): Invocation {
  let applySell = false;
  let applyD05 = false;
  let sawDryRun = false;
  let confirmation = envConfirm;
  let storePath = "";
  let catalogPath = "";
  for (let i = 0; i < argv.length; i += 1) {
    const arg = argv[i] ?? "";
    if (arg === "--apply-sell") applySell = true;
    else if (arg === "--apply-d05") applyD05 = true;
    else if (arg === "--dry-run") sawDryRun = true;
    else if (arg === "--store") storePath = argv[++i] ?? "";
    else if (arg === "--catalog") catalogPath = argv[++i] ?? "";
    else if (arg === "--confirm") confirmation = argv[++i] ?? "";
    else throw new Error(`Unknown argument ${arg}`);
  }
  if (sawDryRun && (applySell || applyD05)) {
    throw new Error("--dry-run cannot be combined with an apply flag.");
  }
  if ((applySell || applyD05) && storePath) {
    throw new Error("--store is for dry-run only. Apply reads the durable intake store.");
  }
  return { applySell, applyD05, confirmation: confirmation.trim(), storePath, catalogPath };
}

async function main(): Promise<void> {
  const invocation = parseBackfillArgs(process.argv.slice(2), process.env.BOSS_CONFIRM ?? "");
  if (invocation.applySell && invocation.applyD05) {
    throw new Error("Run the sell_usd backfill and the D05 form as two commands.");
  }
  const sellMode = resolveBackfillMode(
    invocation.applySell,
    invocation.confirmation,
    BOSS_CONFIRM_SELL_USD,
  );
  const d05Mode = resolveBackfillMode(invocation.applyD05, invocation.confirmation, BOSS_CONFIRM_D05_FORM);

  switch (sellMode) {
    case "dry-run":
      if (d05Mode === "dry-run") {
        runDry(invocation);
        return;
      }
      if (d05Mode === "apply") {
        await runD05Apply(invocation);
        return;
      }
      return assertNever(d05Mode, "unknown backfill mode");
    case "apply":
      if (d05Mode !== "dry-run") {
        throw new Error("Run the sell_usd backfill and the D05 form as two commands.");
      }
      await runSellApply(invocation);
      return;
    default:
      return assertNever(sellMode, "unknown backfill mode");
  }
}

function runDry(invocation: Invocation): void {
  console.log("mode: dry-run");
  console.log("persisted: false");
  console.log(`S06 lock: $${String(S06_LOCKED_PRICE_USD)}`);
  console.log(`D05 seed price: $${String(D05_LOCKED_PRICE_USD)}`);
  console.log("sell_usd map:");
  for (const spec of SELL_USD_BACKFILL) {
    console.log(`${spec.ma} ${spec.storedSellUsd} -> ${String(spec.blobPriceUsd)}`);
  }
  console.log(`Boss sell_usd phrase: ${BOSS_CONFIRM_SELL_USD}`);
  console.log(`Boss D05 phrase: ${BOSS_CONFIRM_D05_FORM}`);
  console.log(`Catalog file (read-only SoT): ${PUBLIC_CATALOG_URL}`);

  if (!invocation.storePath && !invocation.catalogPath) {
    console.log("No intake store was read. No Blob write.");
    return;
  }
  if (!invocation.storePath || !invocation.catalogPath) {
    throw new Error("Dry-run against rows needs both --store and --catalog. Neither file is written.");
  }
  const store = readStoreFile(invocation.storePath);
  const catalog = readJson(invocation.catalogPath);
  const prices = catalogPriceIndex(catalog);
  const plan = planSellUsdBackfill(store.submissions, prices);
  const d05 = planD05IntakeSeed(
    catalog,
    store.submissions.map((row) => row.ma),
  );
  const s06Catalog = plan.s06CatalogPriceUsd === null ? "missing" : `$${String(plan.s06CatalogPriceUsd)}`;
  console.log(`applyAllowed: ${String(plan.applyAllowed)}`);
  console.log(`blockReason: ${plan.blockReason ?? ""}`);
  console.log(`S06 catalog: ${s06Catalog}`);
  const changeLine = plan.applyAllowed
    ? plan.changes.map((change) => `${change.ma} ${change.from}->${change.to}`).join(", ")
    : "";
  console.log(`changes: ${changeLine}`);
  console.log(`D05 form: ${d05.ok ? "ready" : "blocked"}`);
  console.log(`D05 reason: ${d05.reason ?? ""}`);
  console.log("D05 persisted: false");
  console.log("persisted: false");
}

async function runSellApply(invocation: Invocation): Promise<void> {
  const { store, prices, backend } = await openDurable(invocation.catalogPath);
  const result = await persistSellUsdBackfill({
    mode: "apply",
    confirmation: invocation.confirmation,
    store,
    catalogPrices: prices,
    writeStore: (next) => backend.writeStore(next),
  });
  console.log(`persisted: ${String(result.persisted)}`);
  console.log(`changes: ${result.plan.changes.map((change) => change.ma).join(", ")}`);
}

async function runD05Apply(invocation: Invocation): Promise<void> {
  const { store, catalog, backend } = await openDurable(invocation.catalogPath);
  const result = await persistD05IntakeSeed({
    mode: "apply",
    confirmation: invocation.confirmation,
    store,
    catalog,
    now: new Date().toISOString(),
    fetchPhoto: fetchBlobPhoto,
    writePhoto: (rel, bytes, contentType) => backend.writePhoto(rel, bytes, contentType),
    writeStore: (next) => backend.writeStore(next),
  });
  console.log(`persisted: ${String(result.persisted)}`);
  console.log(`D05 photos: ${String(result.plan.photos.length)}`);
}

async function openDurable(catalogPath: string): Promise<{
  store: StoreFile;
  catalog: unknown;
  prices: Map<string, number | null>;
  backend: ReturnType<typeof activeBackend>;
}> {
  if (!catalogPath) {
    throw new Error("Apply needs --catalog pointing at a downloaded catalog.v1.json.");
  }
  if (!blobConfigured()) {
    throw new Error("Durable intake Blob is not configured. Refusing to write.");
  }
  const catalog = readJson(catalogPath);
  const prices = catalogPriceIndex(catalog);
  const backend = activeBackend();
  if (backend.kind !== "blob") {
    throw new Error("Refusing to write a local intake store.");
  }
  const store = await backend.readStore();
  if (!store) throw new Error("Durable intake store is empty. Refusing to write.");
  return { store, catalog, prices, backend };
}

export async function fetchBlobPhoto(url: string): Promise<{ bytes: Buffer; contentType: string }> {
  const parsed = new URL(url);
  if (parsed.protocol !== "https:" || !parsed.hostname.endsWith(".public.blob.vercel-storage.com")) {
    throw new Error("D05 photo URL is not public Blob.");
  }
  const response = await fetch(parsed, { redirect: "error" });
  if (!response.ok) throw new Error(`D05 photo fetch failed (${String(response.status)}).`);
  const bytes = Buffer.from(await response.arrayBuffer());
  const contentType = response.headers.get("content-type") || photoContentType(parsed.pathname);
  return { bytes, contentType };
}

function readStoreFile(filePath: string): StoreFile {
  const parsed = readJson(filePath);
  if (!isRecord(parsed) || !Array.isArray(parsed.submissions)) {
    throw new Error("Store JSON has no submissions array.");
  }
  return parsed as StoreFile;
}

function readJson(filePath: string): unknown {
  const text = fs.readFileSync(path.resolve(filePath), "utf8");
  return JSON.parse(text) as unknown;
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

const isDirect = process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url);
if (isDirect) {
  main().catch((error: unknown) => {
    const message = error instanceof Error ? error.message : "Backfill failed.";
    console.error(message);
    process.exitCode = 1;
  });
}
