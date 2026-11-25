import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import path from "node:path";
import { test } from "node:test";
import { fileURLToPath } from "node:url";
import {
  computeAutoPrice,
  intakePriceView,
  landedUsdFromCosts,
  sellPriceFlag,
  sellUsdFromLanded,
  tieredMarginForSell,
  tieredSellUsd as intakeTiered,
} from "../lib/pricing";
import {
  marginForSell,
  tieredSellUsd as sharedTiered,
  wouldBeLiveUsd,
} from "../../shared/tiered-pricing";

const GOLDEN_PATH = path.join(
  path.dirname(fileURLToPath(import.meta.url)),
  "..",
  "..",
  "scripts",
  "testdata",
  "price-characterization.json",
);

type Band = readonly number[];

type Edge = { landed: string; sell: number };

type SellInput = {
  ma: string;
  kind: string;
  sellUsd: string;
  sellCny: string;
  sellCurrency: string;
  costCny: string;
  costUsd: string;
  costCurrency: string;
  fxRate: number;
};

type PriceView = {
  input: SellInput;
  label: string;
  dollars: number | null;
  flag: string;
};

type Golden = {
  tieredBands: Band[];
  flatBands: Band[];
  tieredEdges: Edge[];
  flatEdges: Edge[];
  sharedTieredThrows: string[];
  intakeTieredNulls: Array<number | string>;
  flatInvent: Array<{ landed: string; sellUsd: number }>;
  margins: Array<{ sell: number; text: string }>;
  intakeLanded: Array<{
    kind: string;
    costCny: string;
    costUsd: string;
    costCurrency: string;
    fxRate: number;
    landed: number;
  }>;
  wouldBe: Array<{
    ma: string;
    kind: string;
    liveUsd: number;
    costCny: string;
    costUsd: string | null;
    expected: {
      ma: string;
      liveUsd: number;
      wouldBeUsd: number;
      applied: boolean;
      reason: string;
    };
  }>;
  computeAutoPrice: {
    quoted: {
      input: { costCny: number; fxRate: number; kind: string };
      sellUsd: number;
      deboxUsd: number;
      landedUsd: number;
    };
    nulls: Array<{ costCny: number; fxRate: number; kind: string }>;
  };
  intakeFlagSplit: PriceView & { sellPriceFlag: string };
  intakeBlank: PriceView;
  intakeS06: PriceView;
};

const golden = JSON.parse(readFileSync(GOLDEN_PATH, "utf8")) as Golden;

function landedString(cent: number): string {
  return `${Math.trunc(cent / 100)}.${String(cent % 100).padStart(2, "0")}`;
}

function bandSell(bands: readonly Band[], cent: number): number {
  let sell: number | undefined;
  for (const pair of bands) {
    const start = pair[0];
    const value = pair[1];
    if (start === undefined || value === undefined) {
      throw new Error("golden band is missing a cent or a sell");
    }
    if (cent < start) {
      break;
    }
    sell = value;
  }
  if (sell === undefined) {
    throw new Error(`cent ${cent} is outside the golden bands`);
  }
  return sell;
}

function intakeNullLanded(label: number | string): number {
  if (label === "NaN") {
    return Number.NaN;
  }
  if (label === "Infinity") {
    return Number.POSITIVE_INFINITY;
  }
  if (typeof label === "number") {
    return label;
  }
  throw new Error(`unexpected null landed label ${label}`);
}

function assertPriceView(spec: PriceView): void {
  const view = intakePriceView(spec.input);
  assert.equal(view.label, spec.label);
  assert.equal(view.dollars, spec.dollars);
  assert.equal(view.flag, spec.flag);
}

test("tiered cent grid agrees across the shared quote and intake", () => {
  // 5.85 stays $11 and the next cent, 5.86, drops to $10.
  for (let cent = 1; cent <= 8000; cent += 1) {
    const landed = landedString(cent);
    const sell = bandSell(golden.tieredBands, cent);
    assert.equal(sharedTiered(landed), sell, landed);
    assert.equal(intakeTiered(Number(landed)), sell, landed);
  }
});

test("flat cent grid matches sellUsdFromLanded", () => {
  // 6.75 stays $11 and the next cent, 6.76, drops to $10.
  for (let cent = 1; cent <= 8000; cent += 1) {
    const landed = landedString(cent);
    assert.equal(sellUsdFromLanded(Number(landed)), bandSell(golden.flatBands, cent), landed);
  }
});

test("tiered and flat edges stay split", () => {
  // Tiered and flat quotes are pinned separately. The same landed cost can sell at two different dollars.
  for (const row of golden.tieredEdges) {
    assert.equal(sharedTiered(row.landed), row.sell, row.landed);
    assert.equal(intakeTiered(Number(row.landed)), row.sell, row.landed);
  }
  for (const row of golden.flatEdges) {
    assert.equal(sellUsdFromLanded(Number(row.landed)), row.sell, row.landed);
  }
});

test("shared tiered quote throws on a non-positive landed string", () => {
  for (const landed of golden.sharedTieredThrows) {
    assert.throws(() => {
      sharedTiered(landed);
    });
  }
});

test("intake tiered quote returns null for a non-positive landed number", () => {
  for (const label of golden.intakeTieredNulls) {
    assert.equal(intakeTiered(intakeNullLanded(label)), null);
  }
});

test("flat quote invents a sell for a non-positive landed cost", () => {
  // A $0 landed cost is not refused: the flat quote turns it into $2.
  for (const row of golden.flatInvent) {
    assert.equal(sellUsdFromLanded(Number(row.landed)), row.sellUsd);
  }
});

test("margin text and tiered margin number", () => {
  for (const row of golden.margins) {
    assert.equal(marginForSell(row.sell), row.text);
    assert.equal(tieredMarginForSell(row.sell), Number(row.text));
  }
});

test("landed usd from cny costs", () => {
  for (const row of golden.intakeLanded) {
    assert.equal(
      landedUsdFromCosts({
        kind: row.kind,
        costCny: row.costCny,
        costUsd: row.costUsd,
        costCurrency: row.costCurrency,
        fxRate: row.fxRate,
      }),
      row.landed,
    );
  }
});

test("would-be live dollars", () => {
  for (const row of golden.wouldBe) {
    assert.deepEqual(
      wouldBeLiveUsd({
        ma: row.ma,
        kind: row.kind,
        liveUsd: row.liveUsd,
        costCny: row.costCny,
        costUsd: row.costUsd,
      }),
      row.expected,
    );
  }
});

test("auto price uses the flat quote", () => {
  const quoted = golden.computeAutoPrice.quoted;
  const priced = computeAutoPrice(quoted.input);
  assert.ok(priced);
  assert.equal(priced.landedUsd, quoted.landedUsd);
  assert.equal(priced.deboxUsd, quoted.deboxUsd);
  assert.equal(priced.sellUsd, quoted.sellUsd);
  for (const input of golden.computeAutoPrice.nulls) {
    assert.equal(computeAutoPrice(input), null);
  }
});

test("typed sell flag and intake view disagree under the tiered floor", () => {
  // A typed $9 clears sellPriceFlag and is still under-margin on the tiered intake view.
  const spec = golden.intakeFlagSplit;
  assert.equal(sellPriceFlag(spec.input), spec.sellPriceFlag);
  assertPriceView(spec);
});

test("blank sell without cost stays calculate-later", () => {
  assertPriceView(golden.intakeBlank);
});

test("s06 intake view stays the locked dollar", () => {
  assertPriceView(golden.intakeS06);
});
