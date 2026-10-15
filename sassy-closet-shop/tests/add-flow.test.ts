import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";
import { mergeAddFields, messageReadyAddFields } from "../lib/admin-add";
import { addProductToCatalog } from "../lib/admin-ops";
import { isOffLiveSell } from "../lib/held-incomplete";
import type { Product } from "../lib/types";

type FixtureRow = { ma: string; priceUsd: number };

function loadRows(): FixtureRow[] {
  const raw = JSON.parse(readFileSync(new URL("./fixtures/add-catalog.json", import.meta.url), "utf8")) as {
    rows: FixtureRow[];
  };
  return raw.rows;
}

function catalogFrom(rows: FixtureRow[]): Product[] {
  return rows.map((row) => ({ ma: row.ma, priceUsd: row.priceUsd }) as Product);
}

function heldBytes(): Buffer {
  return readFileSync(new URL("../../data/held.json", import.meta.url));
}

test("Add mints the next free mã on hold and leaves S06 at $25", () => {
  const beforeHeld = heldBytes();
  const rows = loadRows();
  const catalog = catalogFrom(rows);
  const snapshot = catalog.map((product) => ({ ma: product.ma, priceUsd: product.priceUsd }));

  const added = addProductToCatalog(catalog, "Q", mergeAddFields("Q", messageReadyAddFields("Q")));
  assert.equal(added.ok, true);
  if (added.ok) {
    assert.equal(added.ma, "Q02");
    const queen = added.products.find((product) => product.ma === "Q02");
    assert.equal(queen?.status, "hold");
    assert.equal(queen?.priceUsd, null);
    const s06 = added.products.find((product) => product.ma === "S06");
    assert.equal(s06?.priceUsd, 25);
    assert.equal(added.products.some((product) => isOffLiveSell(product.ma)), false);
  }
  assert.deepEqual(
    catalog.map((product) => ({ ma: product.ma, priceUsd: product.priceUsd })),
    snapshot,
  );
  assert.ok(heldBytes().equals(beforeHeld));
});

test("Add refuses the next held mã for K, V, and S", () => {
  const beforeHeld = heldBytes();
  const rows = loadRows();
  const cases: Array<{ letter: "K" | "V" | "S"; minted: string }> = [
    { letter: "K", minted: "K02" },
    { letter: "V", minted: "V04" },
    { letter: "S", minted: "S14" },
  ];
  for (const item of cases) {
    const catalog = catalogFrom(rows);
    const saved = addProductToCatalog(catalog, item.letter, messageReadyAddFields(item.letter));
    assert.equal(saved.ok, false, item.letter);
    if (!saved.ok) assert.match(saved.error, new RegExp(`Cannot mint ${item.minted}`));
    assert.equal(catalog.find((product) => product.ma === "S06")?.priceUsd, 25);
    assert.equal(catalog.length, rows.length);
  }
  assert.ok(heldBytes().equals(beforeHeld));
});

test("Add of a free letter does not reprice S06", () => {
  const rows = loadRows();
  const catalog = catalogFrom(rows);
  const fields = mergeAddFields("D", {
    status: "available",
    priceUsd: 40,
    titleEn: "Dress",
    titleVn: "Đầm",
  });
  const added = addProductToCatalog(catalog, "D", fields);
  assert.equal(added.ok, true);
  if (added.ok) {
    assert.equal(added.ma, "D01");
    assert.equal(added.products.find((product) => product.ma === "D01")?.priceUsd, 40);
    assert.equal(added.products.find((product) => product.ma === "S06")?.priceUsd, 25);
    assert.equal(added.products.some((product) => isOffLiveSell(product.ma)), false);
  }
  assert.equal(catalog.find((product) => product.ma === "S06")?.priceUsd, 25);
});
