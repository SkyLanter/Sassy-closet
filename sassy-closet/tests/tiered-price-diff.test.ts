import assert from "node:assert/strict";
import { readdirSync, readFileSync } from "node:fs";
import path from "node:path";
import { test } from "node:test";
import {
  DEFAULT_FX,
  TARGET_MARGIN,
  computeAutoPrice,
  deboxFor,
  sellUsdFromLanded,
} from "../lib/pricing";
import {
  S06_LOCK_USD,
  marginForSell,
  tieredSellUsd,
  wouldBeLiveUsd,
} from "../../shared/tiered-pricing";

const ROOT = path.join(process.cwd(), "..");
const SNAPSHOT_PATH = path.join(ROOT, "shared", "live-price-snapshot.json");

type CostSource = "cny" | "usd" | null;

type SnapshotRow = {
  ma: string;
  kind: string;
  liveUsd: number;
  costCny: string | null;
  costUsd: string | null;
  costSource: CostSource;
  deboxUsd: string;
  landedUsd: string | null;
  flat25Usd: number | null;
  wouldBeUsd: number;
  applied: boolean;
  note: string;
};

type Snapshot = {
  readOnly: boolean;
  writesCatalog: boolean;
  blobSha256: string;
  liveCount: number;
  fx: string;
  rows: SnapshotRow[];
};

function loadSnapshot(): Snapshot {
  const parsed: unknown = JSON.parse(readFileSync(SNAPSHOT_PATH, "utf8"));
  if (typeof parsed !== "object" || parsed === null) {
    throw new Error("snapshot must be an object");
  }
  const value = parsed as Snapshot;
  if (!Array.isArray(value.rows)) throw new Error("snapshot rows must be a list");
  return value;
}

function positive(raw: string | null): number | null {
  if (raw == null) return null;
  const text = raw.trim();
  if (!/^\d+(?:\.\d+)?$/.test(text)) return null;
  const amount = Number(text);
  if (!Number.isFinite(amount) || amount <= 0) return null;
  return amount;
}

function walk(dir: string): string[] {
  const found: string[] = [];
  for (const entry of readdirSync(dir, { withFileTypes: true })) {
    if (entry.name === "node_modules" || entry.name === ".next") continue;
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) {
      found.push(...walk(full));
    } else if (entry.isFile() && /\.(ts|tsx)$/.test(entry.name)) {
      found.push(full);
    }
  }
  return found;
}

const INTAKE_PRICING = "lib/pricing.ts";

function sellSiteRelativePath(file: string): string {
  return path.relative(process.cwd(), file).split(path.sep).join("/");
}

function countTieredSellUsdDefinitions(source: string): number {
  const patterns = [
    /(?:^|\n)\s*(?:export\s+(?:default\s+)?)?(?:async\s+)?function\s+tieredSellUsd\b\s*\(/g,
    /(?:^|\n)\s*(?:export\s+)?(?:const|let|var)\s+tieredSellUsd\b\s*=/g,
  ];
  let count = 0;
  for (const pattern of patterns) {
    count += source.match(pattern)?.length ?? 0;
  }
  return count;
}

function resolvesToIntakePricing(fromRel: string, specifier: string): boolean {
  if (specifier === "@/lib/pricing" || specifier === "@/lib/pricing.ts") return true;
  if (specifier === "lib/pricing" || specifier === "lib/pricing.ts") return true;
  if (!specifier.startsWith(".")) return false;
  const resolved = path.posix.normalize(path.posix.join(path.posix.dirname(fromRel), specifier));
  return resolved === "lib/pricing" || resolved === "lib/pricing.ts";
}

function importsTieredSellUsdFromPricing(fromRel: string, source: string): boolean {
  const pattern = /(?:import|export)\s+(?:type\s+)?([\s\S]*?)\s+from\s+["']([^"']+)["']/g;
  for (const match of source.matchAll(pattern)) {
    const clause = match[1] ?? "";
    const specifier = match[2] ?? "";
    if (!resolvesToIntakePricing(fromRel, specifier)) continue;
    if (/\btieredSellUsd\b/.test(clause)) return true;
  }
  return false;
}

/**
 * `lib/pricing.ts` defines `tieredSellUsd` itself. That local function is the
 * sell-site quote, not an import of `shared/tiered-pricing.ts`. Other files may
 * import it from `lib/pricing`. A second definition is a divergent copy.
 */
function sellSiteTieredQuoteProblem(relPath: string, source: string): string | null {
  const rel = relPath.split("\\").join("/");
  if (source.includes("tiered-pricing")) return "imports the shared tiered quote";
  if (source.includes("wouldBeLiveUsd")) return "references wouldBeLiveUsd";
  const definitions = countTieredSellUsdDefinitions(source);
  const mentions = source.includes("tieredSellUsd");
  if (rel === INTAKE_PRICING) {
    if (definitions > 1) return "divergent tieredSellUsd copies in lib/pricing.ts";
    if (definitions === 1) return null;
    if (mentions) return "lib/pricing.ts mentions tieredSellUsd without a local definition";
    return null;
  }
  if (definitions > 0) return "divergent tieredSellUsd; import the quote from lib/pricing.ts";
  if (mentions && !importsTieredSellUsdFromPricing(rel, source)) {
    return "mentions tieredSellUsd without importing it from lib/pricing.ts";
  }
  return null;
}

test("tiered bands match the autolist fixed points", () => {
  assert.equal(marginForSell(25), "0.35");
  assert.equal(marginForSell(9), "0.35");
  assert.equal(marginForSell(45), "0.25");
  assert.equal(marginForSell(60), "0.25");
  assert.equal(marginForSell(35), "0.3");
  assert.equal(tieredSellUsd("16.25"), 25);
  assert.equal(tieredSellUsd("33.75"), 45);
  assert.equal(tieredSellUsd("3.9"), 8);
  assert.equal(tieredSellUsd("24.5"), 35);
  assert.equal(tieredSellUsd("16.26"), 26);
  assert.equal(tieredSellUsd("19.50"), 30);
  assert.equal(tieredSellUsd("30"), 42);
  assert.equal(tieredSellUsd("33"), 45);
  assert.equal(tieredSellUsd("19.51"), 30);
  assert.equal(tieredSellUsd("19.58"), 30);
  assert.throws(() => tieredSellUsd("0"), /refusing to invent/);
});

test("intake calculator stays on flat 25% and does not quote the tiered sell", () => {
  assert.equal(TARGET_MARGIN, 0.25);
  assert.equal(DEFAULT_FX, 6.723);
  assert.equal(sellUsdFromLanded(16.25), 22);
  assert.equal(tieredSellUsd("16.25"), 25);
  assert.equal(sellUsdFromLanded(30), 40);
  assert.equal(tieredSellUsd("30"), 42);
  const source = readFileSync(path.join(process.cwd(), "lib", "pricing.ts"), "utf8");
  assert.equal(source.includes("tiered-pricing"), false);
  assert.equal(source.includes("wouldBeLiveUsd"), false);
  assert.match(source, /MARGIN_DIVISOR = 1 - TARGET_MARGIN/);
  const puppy = computeAutoPrice({ costCny: 90.65, fxRate: DEFAULT_FX, kind: "A" });
  assert.ok(puppy);
  assert.equal(puppy.sellUsd, 18);
  const tiered = wouldBeLiveUsd({
    ma: "A01",
    kind: "A",
    liveUsd: 27,
    costCny: "90.65",
    costUsd: "13.51",
  });
  assert.equal(tiered.liveUsd, 27);
  assert.equal(tiered.wouldBeUsd, 21);
  assert.notEqual(puppy.sellUsd, tiered.wouldBeUsd);
});

test("each live catalog price would become the tiered quote, and S06 stays $25", () => {
  const snapshot = loadSnapshot();
  assert.equal(snapshot.readOnly, true);
  assert.equal(snapshot.writesCatalog, false);
  assert.equal(snapshot.fx, "6.723");
  assert.equal(snapshot.liveCount, 62);
  assert.equal(
    snapshot.blobSha256,
    "5a61d106e697a781c3c829f2c1d9c11aeec41670b13627cfc1a72c3f99fa4ed3",
  );
  assert.equal(snapshot.rows.length, 62);

  const seen = new Set<string>();
  for (const row of snapshot.rows) {
    assert.equal(seen.has(row.ma), false, row.ma);
    seen.add(row.ma);
    const debox = deboxFor(row.kind);
    assert.equal(row.deboxUsd, debox === 0 ? "0" : debox.toFixed(2), row.ma);
    const cny = positive(row.costCny);
    const usd = positive(row.costUsd);
    const landed = cny != null ? cny / DEFAULT_FX + debox : usd != null ? usd + debox : null;
    if (landed == null) {
      assert.equal(row.flat25Usd, null, row.ma);
    } else {
      assert.equal(sellUsdFromLanded(landed), row.flat25Usd, row.ma);
    }

    const got = wouldBeLiveUsd({
      ma: row.ma,
      kind: row.kind,
      liveUsd: row.liveUsd,
      costCny: row.costCny,
      costUsd: row.costUsd,
    });
    assert.equal(got.liveUsd, row.liveUsd, row.ma);
    assert.equal(got.wouldBeUsd, row.wouldBeUsd, row.ma);
    assert.equal(got.applied, row.applied, row.ma);
    if (row.landedUsd != null && row.applied) {
      assert.equal(tieredSellUsd(row.landedUsd), row.wouldBeUsd, row.ma);
    }
  }

  const s06 = snapshot.rows.find((row) => row.ma === "S06");
  assert.ok(s06);
  assert.equal(s06.liveUsd, 25);
  assert.equal(s06.wouldBeUsd, S06_LOCK_USD);
  assert.equal(s06.applied, false);
  assert.equal(s06.note, "Locked. Shown price stays $25.");
  const locked = wouldBeLiveUsd({
    ma: "s06",
    kind: "S",
    liveUsd: s06.liveUsd,
    costCny: s06.costCny,
    costUsd: s06.costUsd,
  });
  assert.equal(locked.reason, "locked");
  assert.equal(locked.wouldBeUsd, 25);
  assert.ok(s06.landedUsd);
  assert.notEqual(tieredSellUsd(s06.landedUsd), locked.wouldBeUsd);

  const blank = snapshot.rows.find((row) => row.ma === "O04");
  assert.ok(blank);
  assert.equal(blank.liveUsd, 12);
  assert.equal(blank.wouldBeUsd, 12);
  assert.equal(blank.applied, false);
  assert.equal(blank.landedUsd, null);
});

test("sell-site code does not import the tiered quote", () => {
  const moduleSource = readFileSync(path.join(ROOT, "shared", "tiered-pricing.ts"), "utf8");
  assert.equal(moduleSource.includes("held.json"), false);
  assert.equal(moduleSource.includes("products.json"), false);
  assert.equal(moduleSource.includes("fetch("), false);
  assert.equal(moduleSource.includes("writeFile"), false);
  let sawPricing = false;
  for (const dir of ["app", "components", "lib"]) {
    for (const file of walk(path.join(process.cwd(), dir))) {
      const rel = sellSiteRelativePath(file);
      if (rel === INTAKE_PRICING) sawPricing = true;
      const source = readFileSync(file, "utf8");
      const problem = sellSiteTieredQuoteProblem(rel, source);
      assert.equal(problem, null, `${rel}: ${problem ?? ""}`);
    }
  }
  assert.equal(sawPricing, true);
});

test("local tieredSellUsd in lib/pricing.ts is not a sell-site quote failure", () => {
  const source = readFileSync(path.join(process.cwd(), "lib", "pricing.ts"), "utf8");
  assert.equal(countTieredSellUsdDefinitions(source), 1);
  assert.equal(source.includes("tieredSellUsd"), true);
  assert.equal(source.includes("tiered-pricing"), false);
  assert.equal(source.includes("wouldBeLiveUsd"), false);
  assert.equal(sellSiteTieredQuoteProblem(INTAKE_PRICING, source), null);
});

test("a second tieredSellUsd definition stays a divergent copy", () => {
  const copy = "export function tieredSellUsd(landedUsd: number): number | null {\n  return 1;\n}\n";
  assert.equal(sellSiteTieredQuoteProblem(INTAKE_PRICING, copy), null);
  assert.equal(
    sellSiteTieredQuoteProblem("lib/quote.ts", copy),
    "divergent tieredSellUsd; import the quote from lib/pricing.ts",
  );
  assert.equal(
    sellSiteTieredQuoteProblem("components/Row.tsx", copy),
    "divergent tieredSellUsd; import the quote from lib/pricing.ts",
  );
  const alias = "export const tieredSellUsd = (landedUsd: number) => 1;\n";
  assert.equal(
    sellSiteTieredQuoteProblem("app/page.tsx", alias),
    "divergent tieredSellUsd; import the quote from lib/pricing.ts",
  );
  assert.equal(
    sellSiteTieredQuoteProblem(INTAKE_PRICING, `${copy}\n${copy}`),
    "divergent tieredSellUsd copies in lib/pricing.ts",
  );
});

test("other sell-site files share tieredSellUsd by importing lib/pricing", () => {
  const shared = 'import {\n  tieredSellUsd,\n} from "@/lib/pricing";\nexport const n = tieredSellUsd(16.25);\n';
  assert.equal(sellSiteTieredQuoteProblem("components/Row.tsx", shared), null);
  const relative = 'import { tieredSellUsd } from "../lib/pricing";\nexport const n = tieredSellUsd(16.25);\n';
  assert.equal(sellSiteTieredQuoteProblem("components/Row.tsx", relative), null);
  const reexport = 'export { tieredSellUsd } from "@/lib/pricing";\n';
  assert.equal(sellSiteTieredQuoteProblem("components/Row.tsx", reexport), null);
  const otherPricing = 'import { tieredSellUsd } from "./pricing";\nexport const n = tieredSellUsd(16.25);\n';
  assert.equal(
    sellSiteTieredQuoteProblem("components/Row.tsx", otherPricing),
    "mentions tieredSellUsd without importing it from lib/pricing.ts",
  );
  const bare = "export const n = tieredSellUsd(16.25);\n";
  assert.equal(
    sellSiteTieredQuoteProblem("components/Row.tsx", bare),
    "mentions tieredSellUsd without importing it from lib/pricing.ts",
  );
  const sharedModule = 'import { tieredSellUsd } from "../../shared/tiered-pricing";\n';
  assert.equal(sellSiteTieredQuoteProblem("components/Row.tsx", sharedModule), "imports the shared tiered quote");
  assert.equal(sellSiteTieredQuoteProblem(INTAKE_PRICING, sharedModule), "imports the shared tiered quote");
});

test("a local tieredSellUsd definition still cannot pull in the shared quote", () => {
  const definedAndImported = [
    "export function tieredSellUsd(landedUsd: number): number | null {",
    "  return 1;",
    "}",
    "const other = wouldBeLiveUsd;",
    "",
  ].join("\n");
  assert.equal(sellSiteTieredQuoteProblem(INTAKE_PRICING, definedAndImported), "references wouldBeLiveUsd");
  const definedAndModule = [
    'import { marginForSell } from "../../shared/tiered-pricing";',
    "export function tieredSellUsd(landedUsd: number): number | null {",
    "  return marginForSell(1) ? 1 : 1;",
    "}",
    "",
  ].join("\n");
  assert.equal(sellSiteTieredQuoteProblem(INTAKE_PRICING, definedAndModule), "imports the shared tiered quote");
  assert.equal(
    sellSiteTieredQuoteProblem("app/page.tsx", "export const n = wouldBeLiveUsd;\n"),
    "references wouldBeLiveUsd",
  );
});
