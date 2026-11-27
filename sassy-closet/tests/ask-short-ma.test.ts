import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { afterEach, beforeEach, test } from "node:test";
import { localAskAnswer } from "../lib/ask-fallback";
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
  tmp = fs.mkdtempSync(path.join(os.tmpdir(), "sassy-ask-short-"));
  for (const key of STORE_ENV) {
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

async function seedAs(ma: string): Promise<void> {
  const bytes = Buffer.from(`photo-${ma}`);
  await saveSubmission({
    kind: "A",
    size: "M",
    link: "",
    color: "Kem",
    color_note: "",
    pieces: [],
    ...moneyFields(),
    keep_photos: [],
    photos: [{ bytes, hash: hashBytes(bytes), ext: ".jpg" }],
  } as unknown as Parameters<typeof saveSubmission>[0]);
  const file = path.join(tmp, "submissions.json");
  const disk = JSON.parse(fs.readFileSync(file, "utf8")) as {
    submissions: { ma: string; kind: string }[];
  };
  disk.submissions[0].ma = ma;
  disk.submissions[0].kind = ma[0] ?? "A";
  fs.writeFileSync(file, JSON.stringify(disk));
  resetStoreBackendForTests();
}

test("a one-digit ask finds the canonical intake row", async () => {
  await seedAs("A01");
  const answer = await localAskAnswer("còn A1 không");
  assert.match(answer.reply, /A01/);
  assert.match(answer.reply, /đang trên site/);
});

test("a one-digit ask for a held mã does not offer a caption", async () => {
  await seedAs("K02");
  const stock = await localAskAnswer("còn K2 không");
  assert.match(stock.reply, /held/);
  assert.equal(stock.copies.length, 0);
  assert.equal(stock.reply.includes("đang trên site"), false);
  const caption = await localAskAnswer("viết caption K2");
  assert.equal(caption.copies.length, 0);
  assert.match(caption.reply, /held/);
});

test("a longer mã is not trimmed to a shorter one", async () => {
  await seedAs("A01");
  const answer = await localAskAnswer("còn A10 không");
  assert.match(answer.reply, /Không thấy A10/);
  assert.equal(answer.reply.includes("A01 đang trên site"), false);
});
