import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import path from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";
import { createElement } from "react";
import { renderToStaticMarkup } from "react-dom/server";
import { ProductPrice } from "../components/product-price";
import { messageReadyAddFields } from "../lib/admin-add";
import { productFromFields, saveProductInCatalog } from "../lib/admin-ops";
import { formatUsd } from "../lib/format";
import { calcPricing, formatUsd2, quoteSellUsd } from "../lib/pricing";
import { saveConfirmLine } from "../lib/save-confirm";
import { s06PriceLockError } from "../lib/sell-contract";
import { productJsonLd } from "../lib/seo";
import type { ShopLook } from "../lib/shop-look";
import type { ProductStatus } from "../lib/types";

const GOLDEN_PATH = path.join(
  path.dirname(fileURLToPath(import.meta.url)),
  "..",
  "..",
  "scripts",
  "testdata",
  "price-characterization.json",
);

type Band = readonly number[];

type Golden = {
  underTenLimit: number;
  underTenBump: number;
  flatBands: Band[];
  flatEdges: Array<{ landed: string; sell: number }>;
  flatInvent: Array<{ landed: string; quotedUsd: number; sellUsd: number }>;
  shopCalc: Array<{
    input: {
      costCny: number | null;
      costUsd: number | null;
      fx: number;
      deboxUsd: number | null;
    };
    costUsd: number | null;
    landedUsd: number | null;
    sellUsd: number | null;
  }>;
  formatUsd: Array<{ amount: number; text: string }>;
  formatUsdThrows: string[];
  formatUsdError: string;
  formatUsd2: Array<{ amount: number | null; text: string }>;
  jsonLdPrices: Array<{ priceUsd: number | null; price: string | null; priceCurrency: string | null }>;
  productPrice: Array<{ priceUsd: number | null; markup: string }>;
  saveConfirm: Array<{ ma: string; status: string; priceUsd: number | null; line: string }>;
  s06PriceLock: Array<{ ma: string; priceUsd: number | null; error: string | null }>;
  saveS06: { rejectPrice: number; rejectError: string; keepPrice: number };
};

const golden = JSON.parse(readFileSync(GOLDEN_PATH, "utf8")) as Golden;

const NON_FINITE: Record<string, number> = {
  NaN: Number.NaN,
  Infinity: Number.POSITIVE_INFINITY,
};

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

function look(priceUsd: number | null): ShopLook {
  return {
    ma: "A01",
    type: "A",
    titleVn: "Áo",
    titleEn: "Top",
    priceUsd,
    colors: [],
    sizes: [],
    images: [],
    descriptionVn: "",
    descriptionEn: "Top",
    measurements: null,
  };
}

function asStatus(status: string): ProductStatus {
  if (status === "hold" || status === "available" || status === "sold") {
    return status;
  }
  throw new Error(`unexpected status ${status}`);
}

test("flat cent grid and the under-ten bump", () => {
  // 6.75 stays $11 and the next cent, 6.76, drops to $10.
  for (let cent = 1; cent <= 8000; cent += 1) {
    const landed = landedString(cent);
    const quote = quoteSellUsd(Number(landed));
    assert.equal(quote.sellUsd, bandSell(golden.flatBands, cent), landed);
    if (quote.quotedUsd < golden.underTenLimit) {
      assert.equal(quote.sellUsd, quote.quotedUsd + golden.underTenBump, landed);
    } else {
      assert.equal(quote.quotedUsd, quote.sellUsd, landed);
    }
  }
});

test("flat edges match quoteSellUsd", () => {
  for (const row of golden.flatEdges) {
    assert.equal(quoteSellUsd(Number(row.landed)).sellUsd, row.sell, row.landed);
  }
});

test("flat quote invents a sell for a non-positive landed cost", () => {
  // A $0 landed cost is not refused: the flat quote turns it into $2.
  for (const row of golden.flatInvent) {
    assert.deepEqual(quoteSellUsd(Number(row.landed)), {
      quotedUsd: row.quotedUsd,
      sellUsd: row.sellUsd,
    });
  }
});

test("shop calculator quotes only with a positive debox", () => {
  // Kind A has no positive debox, and debox 0 is not a quote input, so sell stays null.
  for (const row of golden.shopCalc) {
    const got = calcPricing(row.input);
    assert.equal(got.costUsd, row.costUsd);
    assert.equal(got.landedUsd, row.landedUsd);
    assert.equal(got.sellUsd, row.sellUsd);
  }
});

test("formatUsd", () => {
  for (const row of golden.formatUsd) {
    assert.equal(formatUsd(row.amount), row.text);
  }
  for (const name of golden.formatUsdThrows) {
    const amount = NON_FINITE[name];
    if (amount === undefined) {
      throw new Error(`unknown non-finite label ${name}`);
    }
    assert.throws(() => formatUsd(amount), { message: golden.formatUsdError });
  }
});

test("formatUsd2", () => {
  for (const row of golden.formatUsd2) {
    assert.equal(formatUsd2(row.amount), row.text);
  }
});

test("product json-ld price", () => {
  for (const row of golden.jsonLdPrices) {
    const ld = productJsonLd(look(row.priceUsd));
    const offers: unknown = ld.offers;
    if (typeof offers !== "object" || offers === null) {
      throw new Error("offers missing");
    }
    const offer = offers as Record<string, unknown>;
    if (row.price === null) {
      assert.equal(Object.hasOwn(offer, "price"), false);
      assert.equal(Object.hasOwn(offer, "priceCurrency"), false);
    } else {
      assert.equal(offer.price, row.price);
      assert.equal(offer.priceCurrency, row.priceCurrency);
    }
    assert.equal(JSON.stringify(ld).includes("availability"), false);
  }
});

test("product price markup", () => {
  for (const row of golden.productPrice) {
    const markup = renderToStaticMarkup(createElement(ProductPrice, { product: look(row.priceUsd) }));
    assert.equal(markup, row.markup);
  }
});

test("save confirm line", () => {
  for (const row of golden.saveConfirm) {
    assert.equal(saveConfirmLine(row.ma, asStatus(row.status), row.priceUsd), row.line);
  }
});

test("s06 price lock error", () => {
  for (const row of golden.s06PriceLock) {
    assert.equal(s06PriceLockError(row.ma, row.priceUsd), row.error);
  }
});

test("save keeps S06 at the locked dollar", () => {
  const fields = {
    ...messageReadyAddFields("S"),
    status: "available",
    priceUsd: golden.saveS06.keepPrice,
  };
  const row = productFromFields("S06", fields);
  assert.equal(row.ma, "S06");
  assert.equal(row.type, "S");
  assert.equal(row.status, "available");
  assert.equal(row.priceUsd, golden.saveS06.keepPrice);
  const rejected = saveProductInCatalog([row], "S06", {
    ...fields,
    priceUsd: golden.saveS06.rejectPrice,
  });
  assert.equal(rejected.ok, false);
  if (rejected.ok) {
    assert.fail("S06 price change was saved");
  }
  assert.equal(rejected.error, golden.saveS06.rejectError);
  const saved = saveProductInCatalog([row], "S06", fields);
  assert.equal(saved.ok, true);
  if (!saved.ok) {
    assert.fail(saved.error);
  }
  assert.equal(saved.products[0]?.priceUsd, golden.saveS06.keepPrice);
  assert.equal(saved.products[0]?.ma, "S06");
});
