import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { afterEach, beforeEach, test } from "node:test";
import { resetStoreBackendForTests } from "../lib/store-backend";
import { hashBytes, listSubmissions, saveSubmission } from "../lib/store";
import type { SaveInput } from "../lib/store";

const ENV = [
  "SASSY_DATA_DIR",
  "VERCEL",
  "BLOB_READ_WRITE_TOKEN",
  "BLOB_STORE_ID",
  "BLOB_ACCESS",
  "INTAKE_DATASET_SYNC_WEBHOOK_URL",
  "INTAKE_DATASET_SYNC_WEBHOOK_KEY",
] as const;

const prev: Record<string, string | undefined> = {};
let tmp = "";

beforeEach(() => {
  tmp = fs.mkdtempSync(path.join(os.tmpdir(), "sassy-atomic-"));
  for (const key of ENV) {
    prev[key] = process.env[key];
    delete process.env[key];
  }
  process.env.SASSY_DATA_DIR = tmp;
  resetStoreBackendForTests();
});

afterEach(() => {
  for (const [key, value] of Object.entries(prev)) {
    if (value === undefined) delete process.env[key];
    else process.env[key] = value;
  }
  resetStoreBackendForTests();
  fs.rmSync(tmp, { recursive: true, force: true });
});

test("a store write that dies mid-file leaves the previous closet readable", async () => {
  await saveSubmission(input("Kem"));
  const original = fs.writeFileSync;
  fs.writeFileSync = ((file: fs.PathOrFileDescriptor, data: string | NodeJS.ArrayBufferView, ...rest: unknown[]) => {
    if (String(file).includes("submissions.json")) {
      original(file, "{");
      throw Object.assign(new Error("ENOSPC"), { code: "ENOSPC" });
    }
    return original(file, data, ...(rest as []));
  }) as typeof fs.writeFileSync;
  try {
    await assert.rejects(saveSubmission(input("Đen")));
  } finally {
    fs.writeFileSync = original;
  }
  const rows = await listSubmissions();
  assert.equal(rows.length, 1);
  assert.equal(rows[0].ma, "A01");
  assert.equal(rows[0].color, "Kem");
  const raw = fs.readFileSync(path.join(tmp, "submissions.json"), "utf8");
  const disk = JSON.parse(raw) as { submissions: { color: string }[] };
  assert.equal(disk.submissions[0].color, "Kem");
});

function input(color: string): SaveInput {
  const bytes = Buffer.from(`photo-${color}`);
  return {
    kind: "A",
    size: "M",
    link: "",
    color,
    color_note: "",
    pieces: [],
    cost_usd: "",
    cost_cny: "",
    cost_currency: "USD",
    sell_usd: "",
    sell_cny: "",
    sell_currency: "USD",
    keep_photos: [],
    photos: [{ bytes, hash: hashBytes(bytes), ext: ".jpg" }],
    needs_research: false,
    taobao_snapshot: null,
    auto_price: null,
  };
}
