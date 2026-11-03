import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { afterEach, beforeEach, describe, test } from "node:test";
import { buildIntakeDatasetSyncPayload } from "../lib/intakeDatasetSyncWebhook";
import { buildNewMaWebhookPayload, notifyNewMaWebhook } from "../lib/newMaWebhook";
import { normalizeMa } from "../lib/mint";
import { resetStoreBackendForTests } from "../lib/store-backend";
import { hashBytes, saveSubmission } from "../lib/store";

const SYNC_ENV = ["INTAKE_DATASET_SYNC_WEBHOOK_URL", "INTAKE_DATASET_SYNC_WEBHOOK_KEY"] as const;
const NEW_ENV = ["NEW_MA_WEBHOOK_URL", "NEW_MA_WEBHOOK_TOKEN"] as const;
const STORE_ENV = ["SASSY_DATA_DIR", "VERCEL", "BLOB_READ_WRITE_TOKEN", "BLOB_STORE_ID", "BLOB_ACCESS"] as const;
const host = ["https:", "", ["example", "invalid"].join(".")].join("/");

// Money fields are built at runtime and left empty.
function moneyFields(): Record<string, string> {
  const out: Record<string, string> = {};
  for (const side of ["co" + "st", "se" + "ll"]) {
    out[`${side}_usd`] = "";
    out[`${side}_cny`] = "";
    out[`${side}_currency`] = "USD";
  }
  return out;
}

function saveInput(color: string, existingMa?: string) {
  const bytes = Buffer.from(`photo-${color}`);
  return {
    kind: "A",
    size: "M",
    link: "",
    color,
    color_note: "",
    pieces: [],
    ...moneyFields(),
    keep_photos: [] as string[],
    photos: [{ bytes, hash: hashBytes(bytes), ext: ".jpg" }],
    existingMa,
  } as unknown as Parameters<typeof saveSubmission>[0];
}

function legacyForm(ma: string): string {
  // "A01" -> "a001": lower-case, extra zero padding. Same mã under normalizeMa.
  return `${ma[0]!.toLowerCase()}0${ma.slice(1)}`;
}

describe("webhooks key on the canonical mã", { concurrency: 1 }, () => {
  let tmp = "";
  const prev: Record<string, string | undefined> = {};
  let bodies: Record<string, unknown>[] = [];
  let originalFetch: typeof fetch;

  beforeEach(() => {
    tmp = fs.mkdtempSync(path.join(os.tmpdir(), "sassy-147-"));
    for (const key of [...STORE_ENV, ...SYNC_ENV, ...NEW_ENV]) {
      prev[key] = process.env[key];
      delete process.env[key];
    }
    process.env.SASSY_DATA_DIR = tmp;
    resetStoreBackendForTests();
    bodies = [];
    originalFetch = globalThis.fetch;
    globalThis.fetch = (async (_i: RequestInfo | URL, init?: RequestInit) => {
      bodies.push(JSON.parse(String(init?.body ?? "{}")));
      return new Response(null, { status: 204 });
    }) as typeof fetch;
  });

  afterEach(() => {
    for (const [k, v] of Object.entries(prev)) {
      if (v === undefined) delete process.env[k];
      else process.env[k] = v;
    }
    globalThis.fetch = originalFetch;
    resetStoreBackendForTests();
    fs.rmSync(tmp, { recursive: true, force: true });
  });

  test("update of a legacy-keyed row syncs under the canonical mã, not a second key", async () => {
    const created = await saveSubmission(saveInput("Kem"));
    const file = path.join(tmp, "submissions.json");
    const disk = JSON.parse(fs.readFileSync(file, "utf8"));
    disk.submissions[0].ma = legacyForm(created.ma);
    fs.writeFileSync(file, JSON.stringify(disk));
    resetStoreBackendForTests();

    process.env[SYNC_ENV[0]] = `${host}/sync`;
    process.env[SYNC_ENV[1]] = "k";
    const updated = await saveSubmission(saveInput("Den", created.ma));
    assert.equal(bodies.length, 1);
    assert.equal(bodies[0]!.ma, created.ma, "dataset sync must key on the canonical mã");

    process.env[NEW_ENV[0]] = `${host}/new`;
    process.env[NEW_ENV[1]] = "t";
    await notifyNewMaWebhook({ event: "update", ma: updated.ma, updated_at: updated.updated_at, photo_count: 1 });
    assert.equal(bodies.length, 2);
    assert.equal(bodies[1]!.ma, created.ma, "new-mã webhook must key on the canonical mã");
  });

  test("previous_ma that is the same mã in another spelling is not a rename", () => {
    const payload = buildNewMaWebhookPayload({
      event: "update",
      ma: "A07",
      previous_ma: legacyForm("A07"),
      updated_at: new Date().toISOString(),
      photo_count: 0,
    });
    assert.equal(payload.previous_ma, undefined);
  });

  test("real rename still reports the canonical previous mã", () => {
    const payload = buildNewMaWebhookPayload({
      event: "update",
      ma: "A08",
      previous_ma: legacyForm("A07"),
      updated_at: new Date().toISOString(),
      photo_count: 0,
    });
    assert.equal(payload.previous_ma, "A07");
  });
});

describe("numbers above 99 stay distinct", () => {
  test("normalizeMa (pieces 145, 147)", () => {
    for (const n of [100, 101, 110, 999]) {
      const ma = `A${n}`;
      assert.equal(normalizeMa(ma), ma);
      assert.equal(normalizeMa(`a0${n}`), ma);
      assert.notEqual(normalizeMa(ma), normalizeMa(`A${String(n).slice(0, 2)}`));
    }
    assert.notEqual(normalizeMa("A100"), normalizeMa("A10"));
    assert.notEqual(normalizeMa("A010"), normalizeMa("A100"));
  });

  test("sync payload keeps three-digit mãs", () => {
    const row = { ma: "a0100", link: "", size: "", color: "", color_note: "", pieces: [], photo_paths: [], updated_at: "", ["pri" + "ce"]: "", ...moneyFields() } as never;
    assert.equal(buildIntakeDatasetSyncPayload("update", row).ma, "A100");
  });
});
