import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import test, { afterEach, beforeEach, describe } from "node:test";
import { GET } from "../app/api/export/route";
import { saveFromForm } from "../lib/form-save";
import { buildIntakeDatasetSyncPayload } from "../lib/intakeDatasetSyncWebhook";
import { exportCsv, saveSubmission } from "../lib/store";
import { resetStoreBackendForTests } from "../lib/store-backend";

const STORE_ENV = [
  "SASSY_DATA_DIR",
  "VERCEL",
  "BLOB_READ_WRITE_TOKEN",
  "BLOB_STORE_ID",
  "BLOB_ACCESS",
  "INTAKE_DATASET_SYNC_WEBHOOK_URL",
  "INTAKE_DATASET_SYNC_WEBHOOK_KEY",
  "NEW_MA_WEBHOOK_URL",
  "NEW_MA_WEBHOOK_TOKEN",
] as const;

test("IntakeApp save() posts the typed sell and does not invent a calculated price", () => {
  const src = fs.readFileSync(path.join(process.cwd(), "components", "IntakeApp.tsx"), "utf8");
  const start = src.indexOf("async function save(");
  const end = src.indexOf("async function onSaveClick(", start);
  assert.ok(start >= 0, "IntakeApp save() not found");
  assert.ok(end > start, "slice save() before onSaveClick so later intakePriceView is not flagged");
  const save = src.slice(start, end);
  assert.equal(save.includes("fillCalculated"), false);
  assert.equal(save.includes("priced.dollars"), false);
  assert.equal(save.includes("intakePriceView"), false);
  assert.match(save, /form\.set\(\s*"sell_usd",\s*sellUsd\s*\)/);
});

describe("export CSV edges", { concurrency: 1 }, () => {
  let tmp = "";
  const prev: Record<string, string | undefined> = {};

  beforeEach(() => {
    tmp = fs.mkdtempSync(path.join(os.tmpdir(), "sassy-csv-"));
    for (const key of STORE_ENV) {
      prev[key] = process.env[key];
      delete process.env[key];
    }
    process.env.SASSY_DATA_DIR = tmp;
    resetStoreBackendForTests();
  });

  afterEach(() => {
    for (const key of STORE_ENV) {
      if (prev[key] === undefined) delete process.env[key];
      else process.env[key] = prev[key];
    }
    resetStoreBackendForTests();
    fs.rmSync(tmp, { recursive: true, force: true });
  });

  test("a color_note with a comma and a bare CR stays one quoted row", async () => {
    const note = "shop, red\rblue";
    const bareCr = "kem\rdo";
    const saved = await saveSubmission({
      kind: "A",
      size: "",
      link: "",
      color: bareCr,
      color_note: note,
      pieces: [],
      cost_usd: "",
      cost_cny: "",
      cost_currency: "USD",
      sell_usd: "",
      sell_cny: "",
      sell_currency: "USD",
      keep_photos: [],
      photos: [],
      needs_research: false,
      taobao_snapshot: null,
      auto_price: null,
    });
    const csv = await exportCsv();
    assert.equal(csv.startsWith("\uFEFF"), false);
    assert.equal(csv.startsWith("ma,"), true);
    const rows = csv.split("\n").filter((line) => line.length > 0);
    assert.equal(rows.length, 2);
    assert.match(rows[0] ?? "", /^ma,/);
    assert.match(rows[1] ?? "", new RegExp(saved.ma));
    assert.ok((rows[1] ?? "").includes("\r"));
    assert.match(rows[1] ?? "", /"shop, red\rblue"/);
    assert.match(rows[1] ?? "", /"kem\rdo"/);
  });

  test("odd pieces and keep_photos JSON do not throw and only string photos are kept", async () => {
    const emptyPieces = await saveFromForm(form({ pieces: "null", color: "Kem" }));
    assert.deepEqual(emptyPieces.pieces, []);

    const mixedPieces = await saveFromForm(
      form({ pieces: JSON.stringify([null, { color: "Đỏ" }]), color: "Đỏ" }),
    );
    assert.deepEqual(mixedPieces.pieces, [{ color: "Đỏ" }]);

    const nestedPieces = await saveFromForm(
      form({ pieces: JSON.stringify([["red"], { color: "Đỏ" }]), color: "Đỏ" }),
    );
    assert.deepEqual(nestedPieces.pieces, [{ color: "Đỏ" }]);
    const synced = buildIntakeDatasetSyncPayload("create", {
      ...nestedPieces,
      pieces: [["red"], { color: "Đỏ" }] as unknown as typeof nestedPieces.pieces,
    });
    assert.deepEqual(synced.colors, ["Đỏ"]);

    const emptyKeep = await saveFromForm(form({ keep_photos: "{}" }));
    assert.deepEqual(emptyKeep.photo_paths, []);

    const mixedKeep = await saveFromForm(
      form({
        keep_photos: JSON.stringify(["pix/a.jpg", 1, null, { a: 1 }, "pix/b.jpg"]),
      }),
    );
    assert.deepEqual(mixedKeep.photo_paths, ["pix/a.jpg", "pix/b.jpg"]);
    for (const rel of mixedKeep.photo_paths) assert.equal(typeof rel, "string");

    const csv = await exportCsv();
    assert.equal(csv.startsWith("ma,"), true);
    assert.match(csv, new RegExp(emptyPieces.ma));
    assert.match(csv, new RegExp(mixedPieces.ma));
    assert.match(csv, /Đỏ/);
    assert.match(csv, new RegExp(emptyKeep.ma));
    assert.match(csv, new RegExp(mixedKeep.ma));
  });

  test("a stored row with pieces null exports and does not 503", async () => {
    fs.writeFileSync(
      path.join(tmp, "submissions.json"),
      JSON.stringify({
        nextId: 2,
        fx: { usd_cny: 6.71, updated: "2026-09-07" },
        submissions: [
          {
            id: 1,
            ma: "B02",
            kind: "B",
            size: "",
            color: "",
            color_note: "",
            pieces: null,
            link: "",
            price: "",
            cost_cny: "",
            cost_usd: "",
            cost_currency: "USD",
            sell_cny: "",
            sell_usd: "",
            sell_currency: "USD",
            blurb: "",
            photo_paths: [],
            photo_hashes: [],
            status: "staged",
            square: "not_square",
            needs_research: false,
            taobao_snapshot: null,
            auto_price: null,
            created_at: "2026-11-02T00:00:00.000Z",
            updated_at: "2026-11-02T00:00:00.000Z",
            caption_vi: "",
            caption_en: "",
            blurb_suggested: "",
            photo_link: "",
          },
        ],
      }),
    );
    resetStoreBackendForTests();
    const csv = await exportCsv();
    assert.equal(csv.startsWith("\uFEFF"), false);
    assert.equal(csv.startsWith("ma,"), true);
    assert.match(csv, /B02/);

    const res = await GET();
    assert.equal(res.status, 200);
    const body = await res.text();
    assert.equal(body.startsWith("ma,"), true);
    assert.match(body, /B02/);
  });
});

function form(overrides: Record<string, string> = {}): FormData {
  const body = new FormData();
  const defaults: Record<string, string> = {
    kind: "A",
    size: "",
    link: "",
    color: "",
    color_note: "",
    pieces: "[]",
    cost_usd: "",
    cost_cny: "",
    cost_currency: "USD",
    sell_usd: "",
    sell_cny: "",
    sell_currency: "USD",
    keep_photos: "[]",
  };
  for (const [key, value] of Object.entries({ ...defaults, ...overrides })) {
    body.set(key, value);
  }
  return body;
}
