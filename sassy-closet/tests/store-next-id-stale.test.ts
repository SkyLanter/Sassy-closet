import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { afterEach, beforeEach, test } from "node:test";
import { parseStore, resetStoreBackendForTests } from "../lib/store-backend";
import { hashBytes, listSubmissions, saveSubmission } from "../lib/store";

const STORE_ENV = ["SASSY_DATA_DIR", "VERCEL", "BLOB_READ_WRITE_TOKEN", "BLOB_STORE_ID", "BLOB_ACCESS"] as const;
const prev: Record<string, string | undefined> = {};
let tmp = "";

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
    kind: "A", size: "M", link: "", color, color_note: "", pieces: [],
    ...moneyFields(),
    keep_photos: [] as string[],
    photos: [{ bytes, hash: hashBytes(bytes), ext: ".jpg" }],
    existingMa,
  } as unknown as Parameters<typeof saveSubmission>[0];
}

beforeEach(() => {
  tmp = fs.mkdtempSync(path.join(os.tmpdir(), "sassy-151-"));
  for (const k of STORE_ENV) { prev[k] = process.env[k]; delete process.env[k]; }
  process.env.SASSY_DATA_DIR = tmp;
  resetStoreBackendForTests();
});

afterEach(() => {
  for (const [k, v] of Object.entries(prev)) { if (v === undefined) delete process.env[k]; else process.env[k] = v; }
  resetStoreBackendForTests();
  fs.rmSync(tmp, { recursive: true, force: true });
});

test("a store file without nextId never hands out an id already in use", async () => {
  const first = await saveSubmission(saveInput("Kem"));
  const file = path.join(tmp, "submissions.json");
  const disk = JSON.parse(fs.readFileSync(file, "utf8"));
  delete disk.nextId;
  fs.writeFileSync(file, JSON.stringify(disk));
  resetStoreBackendForTests();

  const second = await saveSubmission(saveInput("Den"));
  assert.notEqual(second.id, first.id, "new row must not reuse an existing id");

  // Updating the first row must not overwrite the second.
  await saveSubmission(saveInput("Trang", first.ma));
  const rows = await listSubmissions();
  assert.equal(rows.length, 2);
  assert.deepEqual(rows.map((r) => r.ma).sort(), [first.ma, second.ma].sort());
});

test("parseStore lifts a stale or invalid nextId above the highest id", () => {
  const rows = [{ id: 4 }, { id: 9 }];
  for (const nextId of [undefined, 1, 9, -3, 2.5, Number.NaN]) {
    const raw = JSON.stringify({ submissions: rows, ...(nextId === undefined ? {} : { nextId }) });
    assert.equal(parseStore(raw).nextId, 10, `nextId ${String(nextId)}`);
  }
  assert.equal(parseStore(JSON.stringify({ submissions: rows, nextId: 15 })).nextId, 15);
  assert.equal(parseStore(JSON.stringify({ submissions: [] })).nextId, 1);
});
