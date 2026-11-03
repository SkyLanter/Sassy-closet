import assert from "node:assert/strict";
import { readdirSync, readFileSync } from "node:fs";
import path from "node:path";
import test from "node:test";
import {
  FX_DEFAULT,
  MARGIN_DIVISOR,
  MARGIN_TARGET,
  calcPricing,
  quoteSellUsd,
} from "../lib/pricing";
import {
  S06_LOCK_USD,
  lockedDeboxUsd,
  tieredSellUsd,
  wouldBeLiveUsd,
} from "../../shared/tiered-pricing";

const ROOT = path.join(process.cwd(), "..");
const SNAPSHOT_PATH = path.join(ROOT, "shared", "live-price-snapshot.json");

type SnapshotRow = {
  ma: string;
  kind: string;
  liveUsd: number;
  costCny: string | null;
  costUsd: string | null;
  costSource: string | null;
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

function deboxNumber(kind: string): number {
  return lockedDeboxUsd(kind) === "7.50" ? 7.5 : 0;
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

test("shop flat quote stays ceil(landed / 0.75) and is not the tiered sell", () => {
  assert.equal(MARGIN_TARGET, 0.25);
  assert.equal(MARGIN_DIVISOR, 0.75);
  assert.equal(FX_DEFAULT, 6.723);
  assert.equal(quoteSellUsd(16.25).sellUsd, 22);
  assert.equal(tieredSellUsd("16.25"), 25);
  assert.equal(quoteSellUsd(30).sellUsd, 40);
  assert.equal(tieredSellUsd("30"), 42);
  const source = readFileSync(path.join(process.cwd(), "lib", "pricing.ts"), "utf8");
  assert.equal(source.includes("tiered-pricing"), false);
  assert.equal(source.includes("wouldBeLiveUsd"), false);
  assert.match(source, /ceil\(landedUsd \/ MARGIN_DIVISOR\)/);
  const noDebox = calcPricing({
    costCny: 90.65,
    costUsd: null,
    fx: FX_DEFAULT,
    deboxUsd: null,
  });
  assert.equal(noDebox.sellUsd, null);
  const dress = calcPricing({
    costCny: 127.49,
    costUsd: null,
    fx: FX_DEFAULT,
    deboxUsd: 7.5,
  });
  assert.equal(dress.sellUsd, 36);
});

test("snapshot keeps sell dollars, redacts supplier costs, and S06 stays $25", () => {
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

  for (const row of snapshot.rows) {
    const debox = deboxNumber(row.kind);
    assert.equal(row.deboxUsd, debox === 0 ? "0" : debox.toFixed(2), row.ma);
    assert.equal(row.costCny, null, row.ma);
    assert.equal(row.costUsd, null, row.ma);
    assert.equal(row.costSource, null, row.ma);
    assert.equal(row.landedUsd, null, row.ma);
    assert.equal(Number.isInteger(row.liveUsd) && row.liveUsd > 0, true, row.ma);
    assert.equal(Number.isInteger(row.wouldBeUsd) && row.wouldBeUsd > 0, true, row.ma);
    if (row.ma === "S06") {
      assert.equal(row.applied, false, row.ma);
      assert.equal(row.liveUsd, 25, row.ma);
      assert.equal(row.wouldBeUsd, 25, row.ma);
    } else if (row.flat25Usd == null) {
      assert.equal(row.applied, false, row.ma);
      assert.equal(row.wouldBeUsd, row.liveUsd, row.ma);
    } else {
      assert.equal(row.applied, true, row.ma);
      assert.equal(Number.isInteger(row.flat25Usd) && row.flat25Usd > 0, true, row.ma);
    }
  }

  const s06 = snapshot.rows.find((row) => row.ma === "S06");
  assert.ok(s06);
  assert.equal(s06.liveUsd, 25);
  assert.equal(s06.wouldBeUsd, S06_LOCK_USD);
  assert.equal(s06.applied, false);
  assert.equal(s06.note, "Locked. Shown price stays $25.");
  assert.equal(s06.flat25Usd, 12);
  const locked = wouldBeLiveUsd({
    ma: "S06",
    kind: "S",
    liveUsd: s06.liveUsd,
    costCny: null,
    costUsd: null,
  });
  assert.equal(locked.reason, "locked");
  assert.equal(locked.wouldBeUsd, 25);
  assert.equal(s06.landedUsd, null);
  assert.notEqual(tieredSellUsd("30"), locked.wouldBeUsd);

  const blank = snapshot.rows.find((row) => row.ma === "O04");
  assert.ok(blank);
  assert.equal(blank.wouldBeUsd, blank.liveUsd);
  assert.equal(blank.wouldBeUsd, 12);
  assert.equal(blank.landedUsd, null);
  assert.equal(blank.flat25Usd, null);
  assert.equal(blank.costCny, null);
  assert.equal(blank.costUsd, null);
});

test("sell-site code does not import the tiered quote", () => {
  const moduleSource = readFileSync(path.join(ROOT, "shared", "tiered-pricing.ts"), "utf8");
  assert.equal(moduleSource.includes("held.json"), false);
  assert.equal(moduleSource.includes("products.json"), false);
  assert.equal(moduleSource.includes("fetch("), false);
  for (const dir of ["app", "components", "lib"]) {
    for (const file of walk(path.join(process.cwd(), dir))) {
      const source = readFileSync(file, "utf8");
      assert.equal(source.includes("tiered-pricing"), false, file);
      assert.equal(source.includes("wouldBeLiveUsd"), false, file);
      assert.equal(source.includes("tieredSellUsd"), false, file);
    }
  }
});
