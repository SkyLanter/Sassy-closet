import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";
import held from "../../data/held.json";
import { emptyFitCm } from "../lib/asia-size";
import { maLetter } from "../lib/ma";
import { pdpDecision } from "../lib/site-settings";
import type { Product, ProductStatus } from "../lib/types";

type FixtureRow = {
  ma: string;
  status: ProductStatus;
  priceUsd: number | null;
};

function loadRows(): FixtureRow[] {
  const raw = JSON.parse(readFileSync(new URL("./fixtures/pdp-catalog.json", import.meta.url), "utf8")) as {
    products: FixtureRow[];
  };
  return raw.products;
}

function product(row: FixtureRow): Product {
  const type = maLetter(row.ma);
  if (type === null) {
    throw new Error(`Invalid mã ${row.ma}`);
  }
  return {
    ma: row.ma,
    type,
    titleVn: row.ma,
    titleEn: row.ma,
    priceUsd: row.priceUsd,
    qty: 1,
    status: row.status,
    colors: [],
    images: [],
    sizes: [],
    fitCm: emptyFitCm(),
    descriptionVn: "",
    descriptionEn: "",
    fulfillment: "dropship",
    sourceLink: null,
  };
}

test("PDP is 404 for every held mã and keeps S06 at $25", () => {
  const rows = loadRows();
  const mas = rows.map((row) => row.ma);
  for (const code of held.heldIncomplete) {
    assert.equal(mas.includes(code), true, code);
  }
  const products = rows.map(product);
  const page = readFileSync(new URL("../app/(shop)/m/[ma]/page.tsx", import.meta.url), "utf8");
  assert.match(page, /if \(!product\) \{\s*notFound\(\);\s*\}/);

  for (const code of held.heldIncomplete) {
    assert.equal(pdpDecision(products, code).status, 404, code);
    assert.equal(pdpDecision(products, code.toLowerCase()).status, 404, code);
  }

  const s06 = pdpDecision(products, "s06");
  assert.equal(s06.status, 200);
  if (s06.status === 200) {
    assert.equal(s06.look.ma, "S06");
    assert.equal(s06.look.priceUsd, 25);
  }

  const a07 = pdpDecision(products, "A07");
  assert.equal(a07.status, 200);
  if (a07.status === 200) assert.equal(a07.look.priceUsd, 26);

  const s10 = pdpDecision(products, "S10");
  assert.equal(s10.status, 200);
  if (s10.status === 200) assert.equal(s10.look.priceUsd, 37);

  const queen = pdpDecision(products, "Q02");
  assert.equal(queen.status, 200);
  if (queen.status === 200) assert.equal(queen.look.priceUsd, null);

  assert.equal(pdpDecision(products, "missing").status, 404);
});
