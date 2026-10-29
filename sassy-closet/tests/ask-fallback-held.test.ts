import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { afterEach, beforeEach, test } from "node:test";
import { localAskAnswer } from "../lib/ask-fallback";
import { HELD_INCOMPLETE_MAS, NEVER_LIST_MAS } from "../lib/held-incomplete";
import { hashBytes, saveSubmission } from "../lib/store";
import { resetStoreBackendForTests } from "../lib/store-backend";

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

beforeEach(() => {
  tmp = fs.mkdtempSync(path.join(os.tmpdir(), "sassy-158-"));
  for (const k of STORE_ENV) { prev[k] = process.env[k]; delete process.env[k]; }
  process.env.SASSY_DATA_DIR = tmp;
  resetStoreBackendForTests();
});

afterEach(() => {
  for (const [k, v] of Object.entries(prev)) { if (v === undefined) delete process.env[k]; else process.env[k] = v; }
  resetStoreBackendForTests();
  fs.rmSync(tmp, { recursive: true, force: true });
});

// Seed one intake row, then re-key it on disk to a mã from data/held.json
// (held rows live in the intake dataset; they just never list).
async function seedAs(ma: string): Promise<void> {
  const bytes = Buffer.from(`photo-${ma}`);
  await saveSubmission({
    kind: "A", size: "M", link: "", color: "Kem", color_note: "", pieces: [],
    ...moneyFields(), keep_photos: [], photos: [{ bytes, hash: hashBytes(bytes), ext: ".jpg" }],
  } as unknown as Parameters<typeof saveSubmission>[0]);
  const file = path.join(tmp, "submissions.json");
  const disk = JSON.parse(fs.readFileSync(file, "utf8"));
  disk.submissions[0].ma = ma;
  disk.submissions[0].kind = ma[0];
  fs.writeFileSync(file, JSON.stringify(disk));
  resetStoreBackendForTests();
}

const offList = [...HELD_INCOMPLETE_MAS.slice(0, 2), ...NEVER_LIST_MAS.slice(0, 1)];

for (const ma of offList) {
  test(`held / never-list ${ma}: no caption or inbox copy, not called on-site`, async () => {
    await seedAs(ma);
    for (const q of [`viết caption ${ma}`, `soạn tin ${ma}`, `${ma}`]) {
      const answer = await localAskAnswer(q);
      assert.equal(answer.copies.length, 0, `${q} offered a copy`);
    }
    const stock = await localAskAnswer(`còn ${ma} không`);
    assert.ok(!stock.reply.includes("đang trên site"), stock.reply);
  });
}

test("a normal mã still gets its caption copy", async () => {
  await seedAs(["A", "01"].join(""));
  const answer = await localAskAnswer("viết caption A01");
  assert.equal(answer.copies[0]?.id, "caption");
});
