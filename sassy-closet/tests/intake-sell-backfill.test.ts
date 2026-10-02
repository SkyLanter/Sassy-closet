import assert from "node:assert/strict";
import { execFileSync } from "node:child_process";
import { createHash } from "node:crypto";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { describe, test } from "node:test";
import { fileURLToPath } from "node:url";
import { HELD_INCOMPLETE_MAS } from "../lib/held-incomplete";
import {
  BOSS_CONFIRM_D05_FORM,
  D05_LOCKED_PRICE_USD,
  persistD05IntakeSeed,
  planD05IntakeSeed,
} from "../lib/intake-d05-seed";
import {
  BOSS_CONFIRM_SELL_USD,
  NEVER_LIST_MAS,
  PUBLIC_CATALOG_URL,
  S06_LOCKED_PRICE_USD,
  SELL_USD_BACKFILL,
  persistSellUsdBackfill,
  planSellUsdBackfill,
  resolveBackfillMode,
  sellRewriteBlockReason,
} from "../lib/intake-sell-backfill";
import { isKindCode, type KindCode } from "../lib/kinds";
import { parseBackfillArgs } from "../scripts/intake-sell-backfill";
import type { StoreFile } from "../lib/store-backend";
import type { Submission } from "../lib/types";

const HELD = ["S14", "A24", "A25", "S15", "A26", "K02", "K03", "K04", "K05", "V04"] as const;

const D05_TITLE_VN = "Đầm ren nhún apricot";
const D05_TITLE_EN = "Apricot ruched lace mini dress";
const D05_SOURCE = "https://item.taobao.com/item.htm?id=1039727293632";
const D05_DESCRIPTION = "Đầm ren nhún apricot, hai dây đen, nơ nhỏ.";
const D05_PHOTOS = [
  "https://efsi0jejsfy7j058.public.blob.vercel-storage.com/sassy-closet-shop/products/D05/cover.jpg",
  "https://efsi0jejsfy7j058.public.blob.vercel-storage.com/sassy-closet-shop/products/D05/photo-2.jpg",
  "https://efsi0jejsfy7j058.public.blob.vercel-storage.com/sassy-closet-shop/products/D05/photo-3.jpg",
];

function kindOf(ma: string): KindCode {
  const letter = ma.slice(0, 1);
  return isKindCode(letter) ? letter : "A";
}

function submission(ma: string, sellUsd: string, price = sellUsd): Submission {
  return {
    id: 1,
    ma,
    kind: kindOf(ma),
    size: "S",
    color: "Đen",
    color_note: "",
    pieces: [],
    link: "https://item.taobao.com/item.htm?id=1",
    price,
    cost_cny: "",
    cost_usd: "10",
    cost_currency: "USD",
    sell_cny: "",
    sell_usd: sellUsd,
    sell_currency: "USD",
    blurb: "",
    photo_paths: [`${ma}/001.jpg`],
    photo_hashes: ["abc"],
    status: "staged",
    square: "not_square",
    needs_research: false,
    taobao_snapshot: null,
    auto_price: null,
    created_at: "2026-09-01T00:00:00.000Z",
    updated_at: "2026-09-01T00:00:00.000Z",
    caption_vi: "keep",
    caption_en: "",
    blurb_suggested: "",
    photo_link: `Documents/Sassy Closet/Photos/${ma}/`,
  };
}

function laggingRows(): Submission[] {
  const rows = SELL_USD_BACKFILL.map((spec) => submission(spec.ma, spec.storedSellUsd));
  rows.push(submission("S06", ""));
  rows.push(submission("V03", ""));
  rows.push(submission("A05", "10"));
  rows.push(submission("Q02", "9"));
  for (const ma of HELD) rows.push(submission(ma, "4"));
  return rows;
}

function storeOf(rows: Submission[]): StoreFile {
  return {
    nextId: 80,
    submissions: rows,
    fx: { usd_cny: 6.71, updated: "2026-09-07" },
    on_hand: { A01: [{ size: "M" }] },
  };
}

function prices(overrides: Record<string, number | null> = {}): Map<string, number | null> {
  const map = new Map<string, number | null>();
  for (const spec of SELL_USD_BACKFILL) map.set(spec.ma, spec.blobPriceUsd);
  map.set("S06", S06_LOCKED_PRICE_USD);
  map.set("Q02", 50);
  map.set("K02", 1);
  map.set("D05", D05_LOCKED_PRICE_USD);
  map.set("V03", 21);
  for (const [ma, price] of Object.entries(overrides)) map.set(ma, price);
  return map;
}

function d05Catalog(patch: Record<string, unknown> = {}): unknown {
  return {
    products: [
      {
        ma: "D05",
        type: "D",
        titleVn: D05_TITLE_VN,
        titleEn: D05_TITLE_EN,
        descriptionVn: D05_DESCRIPTION,
        priceUsd: D05_LOCKED_PRICE_USD,
        status: "available",
        sizes: ["L", "S", "M"],
        sourceLink: D05_SOURCE,
        colors: [{ id: "cd0500", name: "Apricot", hex: "#E8C4A0", note: "" }],
        images: D05_PHOTOS.map((src, index) => ({ src, colorId: "cd0500", order: index + 1 })),
        ...patch,
      },
      { ma: "S06", type: "S", priceUsd: S06_LOCKED_PRICE_USD, status: "available" },
      { ma: "Q02", type: "Q", priceUsd: 50, status: "available", titleVn: "never" },
      { ma: "S14", type: "S", priceUsd: 1, status: "available", titleVn: "held" },
    ],
  };
}

describe("intake sell_usd backfill", () => {
  test("locks the 13-row map, S06 at $25, and blocks held mãs and Q02", () => {
    assert.deepEqual(
      SELL_USD_BACKFILL.map((spec) => [spec.ma, spec.storedSellUsd, spec.blobPriceUsd]),
      [
        ["A01", "25", 27],
        ["A02", "22", 23],
        ["A03", "19", 22],
        ["A04", "20", 21],
        ["B01", "41", 46],
        ["B02", "30", 31],
        ["J01", "30", 29],
        ["J02", "35", 40],
        ["K01", "37", 36],
        ["P03", "18", 11],
        ["P04", "13", 10],
        ["P05", "23", 25],
        ["S01", "28", 39],
      ],
    );
    assert.equal(S06_LOCKED_PRICE_USD, 25);
    assert.equal(D05_LOCKED_PRICE_USD, 26);
    assert.deepEqual([...HELD_INCOMPLETE_MAS], [...HELD]);
    assert.deepEqual([...NEVER_LIST_MAS], ["Q02"]);
    assert.equal(PUBLIC_CATALOG_URL.endsWith("/sassy-closet-shop/catalog.v1.json"), true);
    for (const spec of SELL_USD_BACKFILL) {
      assert.equal(sellRewriteBlockReason(spec.ma), null);
    }
    for (const ma of [...HELD, "Q02", "S06"]) {
      assert.ok(sellRewriteBlockReason(ma));
    }
    assert.equal(BOSS_CONFIRM_SELL_USD, "Boss says: apply the 13 intake sell_usd backfill");
    assert.equal(BOSS_CONFIRM_D05_FORM, "Boss says: add the D05 intake form from Blob");
  });

  test("dry-run plans the 13 rewrites and does not persist", async () => {
    const store = storeOf(laggingRows());
    const snapshot = JSON.stringify(store);
    let writes = 0;
    const result = await persistSellUsdBackfill({
      mode: "dry-run",
      confirmation: BOSS_CONFIRM_SELL_USD,
      store,
      catalogPrices: prices(),
      writeStore: () => {
        writes += 1;
        throw new Error("dry-run wrote");
      },
    });
    assert.equal(writes, 0);
    assert.equal(result.persisted, false);
    assert.equal(result.store, store);
    assert.equal(JSON.stringify(store), snapshot);
    assert.equal(result.plan.mode, "dry-run");
    assert.equal(result.plan.applyAllowed, true);
    assert.deepEqual(
      result.plan.changes.map((change) => [change.ma, change.from, change.to]),
      SELL_USD_BACKFILL.map((spec) => [spec.ma, spec.storedSellUsd, String(spec.blobPriceUsd)]),
    );
    assert.equal(result.plan.s06CatalogPriceUsd, 25);
    for (const ma of [...HELD, "Q02", "S06"]) {
      assert.equal(
        result.plan.changes.some((change) => change.ma === ma),
        false,
      );
    }
  });

  test("apply with the Boss phrase rewrites only sell_usd on an in-memory store", async () => {
    const store = storeOf(laggingRows());
    const written: StoreFile[] = [];
    const result = await persistSellUsdBackfill({
      mode: "apply",
      confirmation: BOSS_CONFIRM_SELL_USD,
      store,
      catalogPrices: prices(),
      writeStore: async (next) => {
        written.push(next);
      },
    });
    assert.equal(written.length, 1);
    assert.equal(result.persisted, true);
    assert.equal(result.store.nextId, 80);
    assert.deepEqual(result.store.fx, store.fx);
    assert.equal(result.store.on_hand, store.on_hand);
    assert.equal(result.store.submissions.length, store.submissions.length);
    const byMa = new Map(result.store.submissions.map((row) => [row.ma, row]));
    for (const spec of SELL_USD_BACKFILL) {
      const before = store.submissions.find((row) => row.ma === spec.ma);
      const after = byMa.get(spec.ma);
      assert.ok(before && after);
      assert.equal(after.sell_usd, String(spec.blobPriceUsd));
      assert.equal(after.price, spec.storedSellUsd);
      assert.equal(after.updated_at, before.updated_at);
      assert.equal(after.caption_vi, before.caption_vi);
      assert.notEqual(after, before);
    }
    for (const ma of ["S06", "V03", "A05", "Q02", ...HELD]) {
      const before = store.submissions.find((row) => row.ma === ma);
      const after = byMa.get(ma);
      assert.equal(after, before);
    }
    assert.equal(byMa.get("S06")?.sell_usd, "");
    assert.equal(byMa.get("J01")?.sell_usd, "29");
    assert.equal(byMa.get("P03")?.sell_usd, "11");
  });

  test("the phrase without the apply flag does not persist", async () => {
    assert.equal(resolveBackfillMode(false, BOSS_CONFIRM_SELL_USD, BOSS_CONFIRM_SELL_USD), "dry-run");
    assert.throws(
      () => resolveBackfillMode(true, "apply it", BOSS_CONFIRM_SELL_USD),
      /Boss must say exactly/,
    );
    const store = storeOf(laggingRows());
    let writes = 0;
    await assert.rejects(
      persistSellUsdBackfill({
        mode: "apply",
        confirmation: "Boss says: apply the 13 intake sell_usd backfill please",
        store,
        catalogPrices: prices(),
        writeStore: async () => {
          writes += 1;
        },
      }),
      /Boss confirmation does not match/,
    );
    assert.equal(writes, 0);
    assert.equal(store.submissions.find((row) => row.ma === "A01")?.sell_usd, "25");
  });

  test("S06, held mãs, Q02, and an unexpected stored dollar block the write", async () => {
    const base = storeOf(laggingRows());
    let writes = 0;
    const writeStore = async () => {
      writes += 1;
    };

    const wrongS06 = await persistSellUsdBackfill({
      mode: "dry-run",
      confirmation: "",
      store: base,
      catalogPrices: prices({ S06: 99 }),
      writeStore,
    });
    assert.equal(wrongS06.plan.applyAllowed, false);
    assert.match(wrongS06.plan.blockReason ?? "", /S06/);
    await assert.rejects(
      persistSellUsdBackfill({
        mode: "apply",
        confirmation: BOSS_CONFIRM_SELL_USD,
        store: base,
        catalogPrices: prices({ S06: 99 }),
        writeStore,
      }),
      /S06/,
    );

    const drifted = storeOf(laggingRows().map((row) => (row.ma === "A01" ? { ...row, sell_usd: "99" } : row)));
    const driftedPlan = planSellUsdBackfill(drifted.submissions, prices());
    assert.equal(driftedPlan.applyAllowed, false);
    assert.match(driftedPlan.blockReason ?? "", /A01/);
    await assert.rejects(
      persistSellUsdBackfill({
        mode: "apply",
        confirmation: BOSS_CONFIRM_SELL_USD,
        store: drifted,
        catalogPrices: prices(),
        writeStore,
      }),
      /A01/,
    );

    const dirtyS06 = storeOf(laggingRows().map((row) => (row.ma === "S06" ? { ...row, sell_usd: "30" } : row)));
    await assert.rejects(
      persistSellUsdBackfill({
        mode: "apply",
        confirmation: BOSS_CONFIRM_SELL_USD,
        store: dirtyS06,
        catalogPrices: prices(),
        writeStore,
      }),
      /S06 sell_usd must stay blank or \$25/,
    );
    assert.equal(dirtyS06.submissions.find((row) => row.ma === "S06")?.sell_usd, "30");
    assert.equal(writes, 0);
  });

  test("S06 stored at $25 is left on $25 while the 13 change", async () => {
    const store = storeOf(laggingRows().map((row) => (row.ma === "S06" ? { ...row, sell_usd: "25" } : row)));
    const result = await persistSellUsdBackfill({
      mode: "apply",
      confirmation: BOSS_CONFIRM_SELL_USD,
      store,
      catalogPrices: prices(),
      writeStore: async () => undefined,
    });
    assert.equal(result.store.submissions.find((row) => row.ma === "S06")?.sell_usd, "25");
    assert.equal(result.plan.changes.some((change) => change.ma === "S06"), false);
  });
});

describe("D05 intake seed", () => {
  test("dry-run copies Blob title, $26, photos, and source and does not persist", async () => {
    const store = storeOf(laggingRows());
    let fetches = 0;
    let writes = 0;
    const result = await persistD05IntakeSeed({
      mode: "dry-run",
      confirmation: BOSS_CONFIRM_D05_FORM,
      store,
      catalog: d05Catalog(),
      now: "2026-10-02T00:00:00.000Z",
      fetchPhoto: () => {
        fetches += 1;
        throw new Error("dry-run fetched a photo");
      },
      writePhoto: () => {
        writes += 1;
        throw new Error("dry-run wrote a photo");
      },
      writeStore: () => {
        writes += 1;
        throw new Error("dry-run wrote the store");
      },
    });
    assert.equal(fetches, 0);
    assert.equal(writes, 0);
    assert.equal(result.persisted, false);
    assert.equal(result.store, store);
    assert.equal(result.plan.ok, true);
    assert.equal(result.plan.persisted, false);
    assert.equal(result.plan.titleVn, D05_TITLE_VN);
    assert.equal(result.plan.titleEn, D05_TITLE_EN);
    assert.equal(result.plan.priceUsd, 26);
    assert.equal(result.plan.sellUsd, "26");
    assert.equal(result.plan.sourceLink, D05_SOURCE);
    assert.equal(result.plan.size, "S M L");
    assert.equal(result.plan.color, "");
    assert.equal(result.plan.blurb, D05_TITLE_VN);
    assert.deepEqual(
      result.plan.photos.map((photo) => photo.rel),
      ["D05/001.jpg", "D05/002.jpg", "D05/003.jpg"],
    );
    assert.deepEqual(
      result.plan.photos.map((photo) => photo.src),
      D05_PHOTOS,
    );
    assert.equal(store.submissions.some((row) => row.ma === "D05"), false);
    assert.equal(store.submissions.some((row) => row.ma === "Q02"), true);
  });

  test("apply builds one D05 form and leaves S06, held mãs, and Q02 untouched", async () => {
    const store = storeOf(laggingRows());
    const bytes = Buffer.from("d05-photo");
    const photos: string[] = [];
    const result = await persistD05IntakeSeed({
      mode: "apply",
      confirmation: BOSS_CONFIRM_D05_FORM,
      store,
      catalog: d05Catalog(),
      now: "2026-10-02T00:00:00.000Z",
      fetchPhoto: async () => ({ bytes, contentType: "image/jpeg" }),
      writePhoto: async (rel) => {
        photos.push(rel);
      },
      writeStore: async () => undefined,
    });
    assert.equal(result.persisted, true);
    assert.deepEqual(photos, ["D05/001.jpg", "D05/002.jpg", "D05/003.jpg"]);
    const added = result.store.submissions.filter((row) => row.ma === "D05");
    assert.equal(added.length, 1);
    const d05 = added[0];
    assert.ok(d05);
    assert.equal(d05.kind, "D");
    assert.equal(d05.sell_usd, "26");
    assert.equal(d05.price, "26");
    assert.equal(d05.blurb, D05_TITLE_VN);
    assert.equal(d05.color, "");
    assert.equal(d05.color_note, "");
    assert.equal(d05.cost_usd, "");
    assert.equal(d05.cost_cny, "");
    assert.equal(d05.link, D05_SOURCE);
    assert.equal(d05.size, "S M L");
    assert.deepEqual(d05.pieces, []);
    assert.equal(d05.needs_research, false);
    assert.equal(d05.taobao_snapshot, null);
    assert.equal(d05.auto_price, null);
    assert.equal(d05.status, "staged");
    assert.equal(d05.square, "not_square");
    assert.match(d05.caption_vi, /Đầm ren nhún apricot/);
    assert.match(d05.caption_vi, /\$26/);
    assert.doesNotMatch(d05.caption_vi, /hai dây/);
    assert.doesNotMatch(d05.caption_vi, /Màu /);
    assert.equal(d05.photo_hashes[0], createHash("sha256").update(bytes).digest("hex"));
    assert.equal(result.store.nextId, d05.id + 1);
    for (const before of store.submissions) {
      const after = result.store.submissions.find((row) => row.ma === before.ma);
      assert.equal(after, before);
    }
    assert.equal(result.store.submissions.filter((row) => row.ma === "Q02").length, 1);
    assert.equal(result.store.submissions.find((row) => row.ma === "S06")?.sell_usd, "");
  });

  test("a wrong phrase, a bad price, and an existing D05 do not write", async () => {
    const store = storeOf(laggingRows());
    let fetches = 0;
    const fetchPhoto = async () => {
      fetches += 1;
      return { bytes: Buffer.from("x"), contentType: "image/jpeg" };
    };
    await assert.rejects(
      persistD05IntakeSeed({
        mode: "apply",
        confirmation: BOSS_CONFIRM_SELL_USD,
        store,
        catalog: d05Catalog(),
        now: "2026-10-02T00:00:00.000Z",
        fetchPhoto,
        writePhoto: async () => undefined,
        writeStore: async () => undefined,
      }),
      /Boss confirmation/,
    );
    const priced = planD05IntakeSeed(d05Catalog({ priceUsd: 27 }), []);
    assert.equal(priced.ok, false);
    assert.match(priced.reason ?? "", /\$26/);
    const missing = planD05IntakeSeed({ products: [{ ma: "Q02", priceUsd: 9 }] }, ["Q02", ...HELD]);
    assert.equal(missing.ok, false);
    assert.match(missing.reason ?? "", /D05 is not in the catalog/);
    assert.equal(missing.photos.length, 0);
    const exists = planD05IntakeSeed(d05Catalog(), ["D05"]);
    assert.equal(exists.ok, false);
    assert.match(exists.reason ?? "", /already exists/);
    assert.equal(fetches, 0);
    assert.equal(store.submissions.some((row) => row.ma === "D05"), false);
  });
});

describe("backfill command", () => {
  test("no arguments print the map and do not persist", () => {
    const result = runScript([]);
    assert.equal(result.status, 0);
    assert.match(result.stdout, /mode: dry-run/);
    assert.match(result.stdout, /persisted: false/);
    assert.match(result.stdout, /A01 25 -> 27/);
    assert.match(result.stdout, /S01 28 -> 39/);
    assert.match(result.stdout, /S06 lock: \$25/);
    assert.match(result.stdout, /No intake store was read/);
    assert.doesNotMatch(result.stdout, /persisted: true/);
  });

  test("apply without Blob config refuses and does not create a local store", () => {
    const tmp = fs.mkdtempSync(path.join(os.tmpdir(), "sassy-backfill-"));
    const catalog = path.join(tmp, "catalog.json");
    fs.writeFileSync(catalog, JSON.stringify(catalogDocument()));
    const result = runScript(["--apply-sell", "--catalog", catalog, "--confirm", BOSS_CONFIRM_SELL_USD], tmp);
    assert.notEqual(result.status, 0);
    assert.match(result.stderr, /not configured/);
    assert.equal(fs.existsSync(path.join(tmp, "submissions.json")), false);
    assert.equal(fs.readdirSync(tmp).includes("photos"), false);
    fs.rmSync(tmp, { recursive: true, force: true });
  });

  test("a local dry-run leaves the snapshot file unchanged", () => {
    const tmp = fs.mkdtempSync(path.join(os.tmpdir(), "sassy-backfill-"));
    const storePath = path.join(tmp, "store.json");
    const catalogPath = path.join(tmp, "catalog.json");
    const store = storeOf(laggingRows());
    fs.writeFileSync(storePath, JSON.stringify(store));
    fs.writeFileSync(catalogPath, JSON.stringify(catalogDocument()));
    const before = fs.readFileSync(storePath);
    const result = runScript(["--store", storePath, "--catalog", catalogPath]);
    assert.equal(result.status, 0, result.stderr);
    assert.match(result.stdout, /persisted: false/);
    assert.match(result.stdout, /applyAllowed: true/);
    assert.match(result.stdout, /A01 25->27/);
    assert.deepEqual(fs.readFileSync(storePath), before);
    fs.rmSync(tmp, { recursive: true, force: true });
  });

  test("parser stays on dry-run unless one apply flag and the matching phrase are both present", () => {
    const dry = parseBackfillArgs([], BOSS_CONFIRM_SELL_USD);
    assert.equal(dry.applySell, false);
    assert.equal(resolveBackfillMode(dry.applySell, dry.confirmation, BOSS_CONFIRM_SELL_USD), "dry-run");
    const sell = parseBackfillArgs(["--apply-sell", "--confirm", BOSS_CONFIRM_SELL_USD]);
    assert.equal(resolveBackfillMode(sell.applySell, sell.confirmation, BOSS_CONFIRM_SELL_USD), "apply");
    assert.throws(() => parseBackfillArgs(["--apply-sell", "--apply-d05", "--store", "x.json"]));
    assert.throws(() => parseBackfillArgs(["--dry-run", "--apply-d05"]));
  });
});

function catalogDocument(): unknown {
  const products = [
    ...SELL_USD_BACKFILL.map((spec) => ({
      ma: spec.ma,
      priceUsd: spec.blobPriceUsd,
      status: "available",
    })),
    { ma: "S06", priceUsd: S06_LOCKED_PRICE_USD, status: "available" },
  ];
  return { products };
}

function runScript(args: string[], dataDir?: string): { status: number; stdout: string; stderr: string } {
  const root = fileURLToPath(new URL("..", import.meta.url));
  const script = path.join(root, "scripts", "intake-sell-backfill.ts");
  const env = { ...process.env };
  delete env.BLOB_READ_WRITE_TOKEN;
  delete env.BLOB_STORE_ID;
  delete env.BOSS_CONFIRM;
  delete env.VERCEL;
  if (dataDir) env.SASSY_DATA_DIR = dataDir;
  try {
    const stdout = execFileSync(process.execPath, ["--import", "tsx", script, ...args], {
      cwd: root,
      env,
      encoding: "utf8",
    });
    return { status: 0, stdout, stderr: "" };
  } catch (error) {
    const failed = error as { status?: number; stdout?: string; stderr?: string };
    return {
      status: failed.status ?? 1,
      stdout: failed.stdout ?? "",
      stderr: failed.stderr ?? "",
    };
  }
}
