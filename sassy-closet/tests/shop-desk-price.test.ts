import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import path from "node:path";
import { test } from "node:test";
import { memoryShopCatalogPort, saveShopCatalogProduct } from "../lib/shop-catalog";
import { parseShopDeskPrice } from "../lib/shop-desk-price";

const ACCEPTED: ReadonlyArray<readonly [string, number]> = [
  ["0", 0],
  ["40", 40],
  ["40.5", 40.5],
  ["40.50", 40.5],
  ["100000", 100000],
];

const REJECTED = ["$40", "1,200", "40 usd", "40.", "1e2", "0x10", "+40", "-1", "100001", "NaN", "Infinity"];

test("blank desk price clears and plain USD literals stay exact cents", () => {
  assert.deepEqual(parseShopDeskPrice("", "A01"), { ok: true, priceUsd: null });
  assert.deepEqual(parseShopDeskPrice("   ", "A01"), { ok: true, priceUsd: null });
  for (const [raw, priceUsd] of ACCEPTED) {
    assert.deepEqual(parseShopDeskPrice(raw, "A01"), { ok: true, priceUsd }, raw);
    assert.deepEqual(parseShopDeskPrice(`  ${raw}  `, "A01"), { ok: true, priceUsd }, raw);
  }
});

test("garbage USD text is an error and is not turned into null or a number", () => {
  for (const raw of REJECTED) {
    const parsed = parseShopDeskPrice(raw, "A01");
    assert.deepEqual(parsed, { ok: false, error: "Mã A01 has an invalid USD price." }, raw);
    assert.equal("priceUsd" in parsed, false, raw);
  }
});

test("S06 accepts 25 and refuses $25 without coercing it to null", () => {
  assert.deepEqual(parseShopDeskPrice("25", "S06"), { ok: true, priceUsd: 25 });
  const marked = parseShopDeskPrice("$25", "S06");
  assert.deepEqual(marked, { ok: false, error: "Mã S06 has an invalid USD price." });
  assert.notDeepEqual(marked, { ok: true, priceUsd: null });
  assert.equal("priceUsd" in marked, false);
});

test("Number of a dollar sign is null in JSON, and the desk parser does not yield a price", () => {
  const poisoned = JSON.stringify({ priceUsd: Number("$40") });
  assert.equal(poisoned.includes("null"), true);
  const parsed = parseShopDeskPrice("$40", "A01");
  assert.equal(parsed.ok, false);
  if (parsed.ok) {
    assert.fail(`rejected $40 must not be used as a price (${String(parsed.priceUsd)})`);
  }
  assert.equal(parsed.error, "Mã A01 has an invalid USD price.");
});

test("shop desk parses USD through parseShopDeskPrice and does not Number(raw)", () => {
  const source = readFileSync(path.join(process.cwd(), "components/ShopCatalogDesk.tsx"), "utf8");
  assert.equal(source.includes("parseShopDeskPrice"), true);
  assert.equal(source.includes("Number(raw)"), false);
  assert.match(source, /status === "hold"/);
  assert.match(source, /patch\.priceUsd = null/);
});

test("a sold row at 40 stays 40 when the parser accepts 40, and rejected text is not saved", async () => {
  const port = memoryShopCatalogPort({
    schema: "catalog.v1",
    version: 1,
    siteId: "sassy-closet-shop",
    products: [
      {
        ma: "A01",
        titleVn: "Ao",
        titleEn: "Top",
        priceUsd: 40,
        status: "sold",
        colors: [],
      },
    ],
  });
  const accepted = parseShopDeskPrice("40", "A01");
  assert.equal(accepted.ok, true);
  if (!accepted.ok) {
    assert.fail("plain 40 must parse");
    return;
  }
  const saved = await saveShopCatalogProduct(
    port,
    { ma: "A01", status: "sold", priceUsd: accepted.priceUsd },
    { now: "2026-11-03T00:00:00.000Z", revalidate: async () => ({ ok: true }) },
  );
  assert.equal(saved.ok, true);
  const snapshot = JSON.parse(port.snapshot() ?? "{}") as {
    products: { ma: string; priceUsd: number | null; status: string }[];
  };
  assert.equal(snapshot.products.find((product) => product.ma === "A01")?.priceUsd, 40);
  assert.equal(snapshot.products.find((product) => product.ma === "A01")?.status, "sold");

  for (const raw of ["$40", "1,200", "$25"]) {
    const rejected = parseShopDeskPrice(raw, "A01");
    assert.equal(rejected.ok, false, raw);
    if (rejected.ok) {
      await saveShopCatalogProduct(
        port,
        { ma: "A01", status: "sold", priceUsd: rejected.priceUsd },
        { now: "2026-11-03T00:00:00.000Z", revalidate: async () => ({ ok: true }) },
      );
    }
  }
  const after = JSON.parse(port.snapshot() ?? "{}") as {
    products: { ma: string; priceUsd: number | null }[];
  };
  assert.equal(after.products.find((product) => product.ma === "A01")?.priceUsd, 40);
});
