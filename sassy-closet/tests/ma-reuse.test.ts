import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { afterEach, test } from "node:test";
import { intakeSaveFailure } from "../lib/form-save";
import { isHeldIncompleteMa, NEVER_LIST_MAS } from "../lib/held-incomplete";
import { liveListingMas } from "../lib/listing-status";
import { nextMa, suggestNextMa } from "../lib/mint";
import { publishBlock } from "../lib/publish-guard";
import { hashBytes, listSubmissions, saveSubmission } from "../lib/store";
import { resetStoreBackendForTests } from "../lib/store-backend";

const ENV_KEYS = [
  "SASSY_DATA_DIR",
  "SHOP_CATALOG_FILE",
  "SHOP_BLOB_READ_WRITE_TOKEN",
  "BLOB_READ_WRITE_TOKEN",
  "BLOB_STORE_ID",
  "VERCEL",
  "INTAKE_DATASET_SYNC_WEBHOOK_URL",
  "INTAKE_DATASET_SYNC_WEBHOOK_KEY",
  "NEW_MA_WEBHOOK_URL",
  "NEW_MA_WEBHOOK_TOKEN",
] as const;

const prev: Record<string, string | undefined> = {};
const heldPath = path.join(process.cwd(), "..", "data", "held.json");

afterEach(() => {
  for (const key of ENV_KEYS) {
    if (prev[key] === undefined) delete process.env[key];
    else process.env[key] = prev[key];
  }
  resetStoreBackendForTests();
});

test("saving a reused D05 is blocked and the next D is suggested", async () => {
  const heldBefore = fs.readFileSync(heldPath, "utf8");
  const tmp = fs.mkdtempSync(path.join(os.tmpdir(), "sassy-d05-"));
  const catalog = writeCatalog(tmp, [
    product("D05", 26, "Apricot ruched lace mini dress", "Apricot"),
    product("S06", 25, "Washed distressed overalls", "Blue"),
  ]);
  const catalogBefore = fs.readFileSync(catalog, "utf8");
  const calls: string[] = [];
  rememberEnv();
  process.env.SASSY_DATA_DIR = tmp;
  process.env.SHOP_CATALOG_FILE = catalog;
  delete process.env.SHOP_BLOB_READ_WRITE_TOKEN;
  delete process.env.BLOB_READ_WRITE_TOKEN;
  delete process.env.BLOB_STORE_ID;
  delete process.env.VERCEL;
  delete process.env.INTAKE_DATASET_SYNC_WEBHOOK_URL;
  delete process.env.INTAKE_DATASET_SYNC_WEBHOOK_KEY;
  delete process.env.NEW_MA_WEBHOOK_URL;
  delete process.env.NEW_MA_WEBHOOK_TOKEN;
  resetStoreBackendForTests();
  const original = globalThis.fetch;
  globalThis.fetch = (async (url: string | URL | Request) => {
    calls.push(String(url));
    throw new Error("no live write");
  }) as typeof fetch;
  try {
    await assert.rejects(
      () => saveSubmission(blankSave({ kind: "D", newMa: "D05", color: "Đen" })),
      (error: unknown) => {
        assert.ok(error instanceof Error);
        assert.match(error.message, /Không lưu D05 \(reused\)/);
        assert.match(error.message, /Mã kế: D06/);
        assert.equal((error as { suggestion?: string }).suggestion, "D06");
        assert.equal((error as { status?: number }).status, 409);
        return true;
      },
    );
    assert.deepEqual(await listSubmissions(), []);
    assert.equal(fs.existsSync(path.join(tmp, "photos", "D05")), false);

    const minted = await saveSubmission(blankSave({ kind: "D", newMa: "D", color: "Đen" }));
    assert.equal(minted.ma, "D06");
    assert.equal(minted.color, "Đen");
    assert.equal(minted.status, "staged");
    const rows = await listSubmissions();
    assert.deepEqual(rows.map((row) => row.ma), ["D06"]);
    assert.equal(fs.existsSync(path.join(tmp, "photos", "D05")), false);

    await assert.rejects(
      () => saveSubmission(blankSave({ kind: "S", newMa: "S06", sellUsd: "25" })),
      /reused/,
    );
    assert.deepEqual((await listSubmissions()).map((row) => row.ma), ["D06"]);
  } finally {
    globalThis.fetch = original;
  }
  assert.deepEqual(calls, []);
  assert.equal(fs.readFileSync(catalog, "utf8"), catalogBefore);
  assert.match(catalogBefore, /Apricot ruched lace mini dress/);
  assert.match(catalogBefore, /"priceUsd": 26/);
  assert.match(catalogBefore, /"ma": "S06"/);
  assert.match(catalogBefore, /"priceUsd": 25/);
  assert.equal(fs.readFileSync(heldPath, "utf8"), heldBefore);
  fs.rmSync(tmp, { recursive: true, force: true });
});

test("editing the same live mã does not write the catalog", async () => {
  const heldBefore = fs.readFileSync(heldPath, "utf8");
  const tmp = fs.mkdtempSync(path.join(os.tmpdir(), "sassy-d05-edit-"));
  const catalog = writeCatalog(tmp, [
    product("D05", 26, "Apricot ruched lace mini dress", "Apricot"),
    product("S06", 25, "Washed distressed overalls", "Blue"),
  ]);
  const catalogBefore = fs.readFileSync(catalog, "utf8");
  rememberEnv();
  process.env.SASSY_DATA_DIR = tmp;
  process.env.SHOP_CATALOG_FILE = catalog;
  delete process.env.SHOP_BLOB_READ_WRITE_TOKEN;
  delete process.env.BLOB_READ_WRITE_TOKEN;
  delete process.env.BLOB_STORE_ID;
  resetStoreBackendForTests();
  fs.writeFileSync(
    path.join(tmp, "submissions.json"),
    JSON.stringify({
      nextId: 2,
      submissions: [
        {
          id: 1,
          ma: "D05",
          kind: "D",
          size: "",
          color: "Đen",
          color_note: "",
          pieces: [],
          link: "",
          price: "",
          cost_cny: "127.49",
          cost_usd: "",
          cost_currency: "CNY",
          sell_cny: "",
          sell_usd: "",
          sell_currency: "USD",
          blurb: "",
          photo_paths: [],
          photo_hashes: [],
          status: "staged",
          square: "not_square",
          created_at: "2026-10-12T19:29:09.359Z",
          updated_at: "2026-10-12T19:29:09.359Z",
          caption_vi: "",
          caption_en: "",
          blurb_suggested: "",
          photo_link: "",
          needs_research: false,
          taobao_snapshot: null,
          auto_price: null,
        },
      ],
      fx: { usd_cny: 6.71, updated: "2026-09-07" },
    }),
  );
  const updated = await saveSubmission(blankSave({ kind: "D", existingMa: "D05", color: "Đen" }));
  assert.equal(updated.ma, "D05");
  assert.equal(updated.color, "Đen");
  assert.equal(fs.readFileSync(catalog, "utf8"), catalogBefore);
  assert.equal(fs.readFileSync(heldPath, "utf8"), heldBefore);
  await assert.rejects(
    () => saveSubmission(blankSave({ kind: "D", newMa: "d05", color: "Đen" })),
    (error: unknown) => {
      assert.ok(error instanceof Error);
      assert.match(error.message, /reused/);
      assert.equal((error as { suggestion?: string }).suggestion, "D06");
      return true;
    },
  );
  assert.deepEqual((await listSubmissions()).map((row) => row.ma), ["D05"]);
  assert.equal(fs.readFileSync(catalog, "utf8"), catalogBefore);
  fs.rmSync(tmp, { recursive: true, force: true });
});

test("next S suggestion skips a fixture held list and is not S14, S15, or S16", async () => {
  const heldBefore = fs.readFileSync(heldPath, "utf8");
  const fixtureHeld = ["S14", "S15", "S16"];
  assert.equal(fixtureHeld.includes("Q02"), false);
  assert.equal(NEVER_LIST_MAS.includes("Q02"), false);
  assert.equal(suggestNextMa("Q", ["Q01"], fixtureHeld), "Q02");
  assert.equal(nextMa("Q", ["Q01"]), "Q02");
  const nextS = suggestNextMa("S", ["S06", "S13"], fixtureHeld);
  assert.equal(nextS, "S17");
  assert.notEqual(nextS, "S14");
  assert.notEqual(nextS, "S15");
  assert.notEqual(nextS, "S16");
  assert.equal(publishBlock({ action: "update", ma: "S06", sellUsd: "25" }), null);
  assert.equal(publishBlock({ action: "update", ma: "S06", sellUsd: "30" }), "s06-lock");

  const tmp = fs.mkdtempSync(path.join(os.tmpdir(), "sassy-held-s-"));
  const catalog = writeCatalog(tmp, [
    product("S06", 25, "Washed distressed overalls", "Blue"),
    product("S13", 26, "Fixture set", "Green"),
    product("Q01", 20, "Fixture pants", "Navy"),
  ]);
  const catalogBefore = fs.readFileSync(catalog, "utf8");
  const calls: string[] = [];
  rememberEnv();
  process.env.SASSY_DATA_DIR = tmp;
  process.env.SHOP_CATALOG_FILE = catalog;
  delete process.env.SHOP_BLOB_READ_WRITE_TOKEN;
  delete process.env.BLOB_READ_WRITE_TOKEN;
  delete process.env.BLOB_STORE_ID;
  delete process.env.VERCEL;
  delete process.env.INTAKE_DATASET_SYNC_WEBHOOK_URL;
  delete process.env.INTAKE_DATASET_SYNC_WEBHOOK_KEY;
  delete process.env.NEW_MA_WEBHOOK_URL;
  delete process.env.NEW_MA_WEBHOOK_TOKEN;
  resetStoreBackendForTests();
  const original = globalThis.fetch;
  globalThis.fetch = (async (url: string | URL | Request) => {
    calls.push(String(url));
    throw new Error("no live write");
  }) as typeof fetch;
  try {
    await assert.rejects(
      () => saveSubmission(blankSave({ kind: "S", newMa: "S13", heldMas: fixtureHeld })),
      (error: unknown) => {
        assert.ok(error instanceof Error);
        assert.match(error.message, /Không lưu S13 \(reused\)/);
        assert.match(error.message, /Mã kế: S17/);
        assert.equal((error as { suggestion?: string }).suggestion, "S17");
        for (const blocked of ["S14", "S15", "S16"]) {
          assert.notEqual((error as { suggestion?: string }).suggestion, blocked);
        }
        return true;
      },
    );
    await assert.rejects(
      () => saveSubmission(blankSave({ kind: "Q", newMa: "Q01", heldMas: fixtureHeld })),
      (error: unknown) => {
        assert.ok(error instanceof Error);
        assert.equal((error as { suggestion?: string }).suggestion, "Q02");
        return true;
      },
    );
    assert.deepEqual(await listSubmissions(), []);
  } finally {
    globalThis.fetch = original;
  }
  assert.deepEqual(calls, []);
  assert.equal(fs.readFileSync(catalog, "utf8"), catalogBefore);
  assert.match(catalogBefore, /"ma": "S06"/);
  assert.match(catalogBefore, /"priceUsd": 25/);
  assert.equal(fs.readFileSync(heldPath, "utf8"), heldBefore);
  fs.rmSync(tmp, { recursive: true, force: true });
});

test("a reused Q suggests Q02 and Q02 is not on the never-list", async () => {
  const heldBefore = fs.readFileSync(heldPath, "utf8");
  const held = JSON.parse(heldBefore) as { neverList: string[] };
  assert.equal(held.neverList.includes("Q02"), false);
  assert.equal(NEVER_LIST_MAS.includes("Q02"), false);
  assert.equal(isHeldIncompleteMa("Q02"), false);
  assert.equal(nextMa("Q", ["Q01"]), "Q02");
  assert.equal(publishBlock({ action: "create", ma: "Q02" }), null);
  assert.equal(publishBlock({ action: "mint", ma: "Q02" }), null);
  assert.equal(publishBlock({ action: "update", ma: "S06", sellUsd: "25" }), null);
  assert.equal(publishBlock({ action: "update", ma: "S06", sellUsd: "30" }), "s06-lock");

  const tmp = fs.mkdtempSync(path.join(os.tmpdir(), "sassy-q02-"));
  const catalog = writeCatalog(tmp, [
    product("Q01", 20, "Fixture pants", "Black"),
    product("S06", 25, "Washed distressed overalls", "Blue"),
  ]);
  const catalogBefore = fs.readFileSync(catalog, "utf8");
  const calls: string[] = [];
  rememberEnv();
  process.env.SASSY_DATA_DIR = tmp;
  process.env.SHOP_CATALOG_FILE = catalog;
  delete process.env.SHOP_BLOB_READ_WRITE_TOKEN;
  delete process.env.BLOB_READ_WRITE_TOKEN;
  delete process.env.BLOB_STORE_ID;
  delete process.env.INTAKE_DATASET_SYNC_WEBHOOK_URL;
  delete process.env.NEW_MA_WEBHOOK_URL;
  resetStoreBackendForTests();
  const original = globalThis.fetch;
  globalThis.fetch = (async (url: string | URL | Request) => {
    calls.push(String(url));
    throw new Error("no live write");
  }) as typeof fetch;
  try {
    await assert.rejects(
      () => saveSubmission(blankSave({ kind: "Q", newMa: "Q01" })),
      (error: unknown) => {
        assert.ok(error instanceof Error);
        assert.match(error.message, /Không lưu Q01 \(reused\)/);
        assert.match(error.message, /Mã kế: Q02/);
        assert.equal((error as { suggestion?: string }).suggestion, "Q02");
        return true;
      },
    );
    assert.deepEqual(await listSubmissions(), []);
    const minted = await saveSubmission(blankSave({ kind: "Q", newMa: "Q" }));
    assert.equal(minted.ma, "Q02");
    assert.equal(minted.status, "staged");
    assert.deepEqual((await listSubmissions()).map((row) => row.ma), ["Q02"]);
  } finally {
    globalThis.fetch = original;
  }
  assert.deepEqual(calls, []);
  assert.equal(fs.readFileSync(catalog, "utf8"), catalogBefore);
  assert.match(catalogBefore, /"ma": "S06"/);
  assert.match(catalogBefore, /"priceUsd": 25/);
  assert.equal(fs.readFileSync(heldPath, "utf8"), heldBefore);
  const failure = intakeSaveFailure(
    Object.assign(new Error("Không lưu D05 (reused). Mã kế: D06."), { status: 409, suggestion: "D06" }),
  );
  assert.equal(failure.status, 409);
  assert.equal(failure.body.suggestion, "D06");
  assert.deepEqual(
    liveListingMas({
      D05: { state: "live", priceUsd: 26, reasons: [], todo: [] },
      Q02: { state: "pending", reasons: [], todo: [] },
      S06: { state: "live", priceUsd: 25, reasons: [], todo: [] },
    }),
    ["D05", "S06"],
  );
  const source = fs.readFileSync(path.join(process.cwd(), "lib", "live-mas.ts"), "utf8");
  assert.equal(source.includes(".write("), false);
  assert.equal(source.includes("put("), false);
  fs.rmSync(tmp, { recursive: true, force: true });
});

function rememberEnv(): void {
  for (const key of ENV_KEYS) prev[key] = process.env[key];
}

function writeCatalog(dir: string, products: Record<string, unknown>[]): string {
  const file = path.join(dir, "catalog.v1.json");
  fs.writeFileSync(
    file,
    JSON.stringify(
      {
        schema: "catalog.v1",
        version: 1,
        siteId: "sassy-closet-shop",
        products,
      },
      null,
      2,
    ),
  );
  return file;
}

function product(ma: string, priceUsd: number, titleEn: string, color: string): Record<string, unknown> {
  return {
    ma,
    type: ma.slice(0, 1),
    titleVn: titleEn,
    titleEn,
    priceUsd,
    qty: 1,
    status: "available",
    colors: [{ id: `${ma.toLowerCase()}00`, hex: "#E8C4A0", name: color, note: "" }],
    images: [],
    sizes: ["S"],
  };
}

function blankSave(
  overrides: {
    kind?: string;
    newMa?: string;
    existingMa?: string;
    sellUsd?: string;
    color?: string;
    heldMas?: readonly string[];
  } = {},
) {
  const bytes = Buffer.from("photo");
  return {
    kind: overrides.kind ?? "A",
    size: "S",
    link: "",
    color: overrides.color ?? "",
    color_note: "",
    pieces: [],
    cost_usd: "",
    cost_cny: "80",
    cost_currency: "CNY",
    sell_usd: overrides.sellUsd ?? "",
    sell_cny: "",
    sell_currency: "USD",
    keep_photos: [] as string[],
    photos: [{ bytes, hash: hashBytes(bytes), ext: ".jpg" }],
    existingMa: overrides.existingMa,
    newMa: overrides.newMa,
    heldMas: overrides.heldMas,
    needs_research: false,
    taobao_snapshot: null,
    auto_price: null,
  };
}
