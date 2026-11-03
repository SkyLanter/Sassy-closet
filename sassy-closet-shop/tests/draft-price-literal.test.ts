import assert from "node:assert/strict";
import test from "node:test";
import { messageReadyAddFields } from "../lib/admin-add";
import { productFromFields, saveProductInCatalog } from "../lib/admin-ops";
import { emptyFitCm } from "../lib/asia-size";
import { parseDraftPrice, validateItemDraft, type ItemDraft } from "../lib/item-draft";
import type { ProductStatus } from "../lib/types";

const PRICED = ["available", "sold"] as const;

const ACCEPTED: ReadonlyArray<readonly [string, number]> = [
  ["0", 0],
  ["40", 40],
  ["40.5", 40.5],
  ["40.50", 40.5],
  ["25", 25],
  ["25.00", 25],
  ["100001", 100001],
];

const REJECTED = [
  "-1",
  "1e2",
  "1E2",
  "0x10",
  "0x19",
  "2.5e1",
  "+40",
  "$40",
  "1,200",
  "2,5",
  "08",
  "40.",
  ".5",
  "NaN",
  "Infinity",
];

function draft(status: ProductStatus, priceInput: string): ItemDraft {
  return {
    titleEn: "Top",
    titleVn: "Top",
    descriptionEn: "",
    descriptionVn: "",
    status,
    priceInput,
    colors: [],
    images: [],
    sizes: [],
    fitCm: emptyFitCm(),
    fulfillment: "dropship",
    sourceLink: "",
  };
}

test("available and sold accept a plain non-negative USD literal", () => {
  for (const status of PRICED) {
    for (const [raw, priceUsd] of ACCEPTED) {
      assert.equal(parseDraftPrice(status, raw), priceUsd, `${status} ${raw}`);
      assert.equal(parseDraftPrice(status, `  ${raw}  `), priceUsd, `${status} padded ${raw}`);
    }
  }
  assert.equal(parseDraftPrice("available", "25"), 25);
  assert.equal(parseDraftPrice("sold", "25.00"), 25);
});

test("exponent, hex, sign, and other non-literals are NaN, including S06 traps", () => {
  for (const status of PRICED) {
    for (const raw of REJECTED) {
      const parsed = parseDraftPrice(status, raw);
      assert.equal(Number.isNaN(parsed), true, `${status} ${raw}`);
    }
  }
  for (const raw of ["2.5e1", "0x19"]) {
    const parsed = parseDraftPrice("available", raw);
    assert.equal(Number.isNaN(parsed), true, raw);
    assert.equal(parsed === 25, false, raw);
    assert.equal(parseDraftPrice("sold", raw) === 25, false, raw);
  }
});

test("blank price is null and hold ignores the text", () => {
  for (const status of PRICED) {
    assert.equal(parseDraftPrice(status, ""), null, status);
    assert.equal(parseDraftPrice(status, "   "), null, status);
  }
  assert.equal(parseDraftPrice("hold", "1e2"), null);
  assert.equal(parseDraftPrice("hold", "40"), null);
  assert.equal(parseDraftPrice("hold", ""), null);
});

test("rejected text keeps the existing price validation messages", () => {
  assert.equal(validateItemDraft(draft("available", "1e2")), "Available items need a USD price.");
  assert.equal(validateItemDraft(draft("available", "")), "Available items need a USD price.");
  assert.equal(
    validateItemDraft(draft("sold", "0x19")),
    "Sold items need a valid USD price or a blank price.",
  );
  assert.equal(validateItemDraft(draft("sold", "")), null);
  assert.equal(validateItemDraft(draft("available", "25")), null);
  assert.equal(validateItemDraft(draft("available", "100001")), null);
  assert.equal(validateItemDraft(draft("sold", "  40.50  ")), null);
});

test("prices above 100000 parse, and an unsafe cent count does not", () => {
  assert.equal(parseDraftPrice("available", "100001"), 100001);
  assert.equal(parseDraftPrice("sold", "100001.5"), 100001.5);

  const maxCents = Number.MAX_SAFE_INTEGER;
  const atLimitWhole = Math.floor(maxCents / 100);
  const atLimit = `${atLimitWhole}.${String(maxCents % 100).padStart(2, "0")}`;
  assert.equal(parseDraftPrice("available", atLimit), maxCents / 100);

  const overCents = maxCents + 1;
  const overLimit = `${Math.floor(overCents / 100)}.${String(overCents % 100).padStart(2, "0")}`;
  assert.equal(Number.isNaN(parseDraftPrice("available", overLimit)), true);
  assert.equal(Number.isNaN(parseDraftPrice("sold", `1${"0".repeat(20)}`)), true);
});

test("a NaN draft price does not overwrite an available A01 row at 40", () => {
  for (const raw of ["1e2", "-1", "0x10"]) {
    const catalog = [
      productFromFields("A01", {
        ...messageReadyAddFields("A"),
        status: "available",
        priceUsd: 40,
      }),
    ];
    const parsed = parseDraftPrice("available", raw);
    assert.equal(Number.isNaN(parsed), true, raw);
    const saved = saveProductInCatalog(catalog, "A01", {
      ...messageReadyAddFields("A"),
      status: "available",
      priceUsd: parsed,
    });
    assert.equal(saved.ok, false, raw);
    assert.equal(catalog[0]?.priceUsd, 40, raw);
  }

  const catalog = [
    productFromFields("A01", {
      ...messageReadyAddFields("A"),
      status: "available",
      priceUsd: 40,
    }),
  ];
  const parsed = parseDraftPrice("available", "40");
  assert.equal(parsed, 40);
  const saved = saveProductInCatalog(catalog, "A01", {
    ...messageReadyAddFields("A"),
    status: "available",
    priceUsd: parsed,
  });
  assert.equal(saved.ok, true, saved.ok ? "" : saved.error);
  if (!saved.ok) {
    return;
  }
  assert.equal(saved.products.find((product) => product.ma === "A01")?.priceUsd, 40);
  assert.equal(catalog[0]?.priceUsd, 40);
});
