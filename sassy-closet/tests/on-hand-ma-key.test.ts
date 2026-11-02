import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { afterEach, beforeEach, test } from "node:test";
import { GET } from "../app/api/ma/[code]/route";
import { lookupMaCard } from "../lib/ma-card";
import { saveSubmission } from "../lib/store";
import { resetStoreBackendForTests } from "../lib/store-backend";

const ENV_KEYS = [
  "SASSY_DATA_DIR",
  "VERCEL",
  "BLOB_READ_WRITE_TOKEN",
  "BLOB_STORE_ID",
  "BLOB_ACCESS",
  "INTAKE_DATASET_SYNC_WEBHOOK_URL",
  "INTAKE_DATASET_SYNC_WEBHOOK_KEY",
] as const;

let tmp = "";
const prev: Record<string, string | undefined> = {};

beforeEach(() => {
  tmp = fs.mkdtempSync(path.join(os.tmpdir(), "on-hand-key-"));
  for (const key of ENV_KEYS) {
    prev[key] = process.env[key];
    delete process.env[key];
  }
  process.env.SASSY_DATA_DIR = tmp;
  resetStoreBackendForTests();
});

afterEach(() => {
  for (const key of ENV_KEYS) {
    const value = prev[key];
    if (value === undefined) delete process.env[key];
    else process.env[key] = value;
  }
  resetStoreBackendForTests();
  fs.rmSync(tmp, { recursive: true, force: true });
});

function blankMoney(): Record<string, string> {
  return {
    cost_usd: "",
    cost_cny: "",
    cost_currency: "USD",
    sell_usd: "",
    sell_cny: "",
    sell_currency: "USD",
  };
}

async function savePlain(kind: "A" | "S", extra: { newMa?: string; color: string; size: string }) {
  await saveSubmission({
    kind,
    size: extra.size,
    link: "",
    color: extra.color,
    color_note: "",
    pieces: [],
    ...blankMoney(),
    keep_photos: [],
    photos: [],
    needs_research: false,
    taobao_snapshot: null,
    auto_price: null,
    newMa: extra.newMa,
  });
}

function writeOnHand(onHand: Record<string, unknown>) {
  const diskPath = path.join(tmp, "submissions.json");
  const disk = JSON.parse(fs.readFileSync(diskPath, "utf8")) as { on_hand?: unknown };
  disk.on_hand = onHand;
  fs.writeFileSync(diskPath, JSON.stringify(disk));
  resetStoreBackendForTests();
}

async function maBody(code: string): Promise<{
  code: string;
  staged_only: boolean;
  on_hand: { size: string; qty_on_hand: number | null }[];
}> {
  const response = await GET(new Request(`http://localhost/api/ma/${code}`), {
    params: Promise.resolve({ code }),
  });
  assert.equal(response.status, 200);
  return (await response.json()) as {
    code: string;
    staged_only: boolean;
    on_hand: { size: string; qty_on_hand: number | null }[];
  };
}

test("GET /api/ma reads on-hand rows stored under a lowercase or padded key", async () => {
  await savePlain("A", { color: "Kem", size: "M" });
  await savePlain("S", { color: "Den", size: "S", newMa: "S06" });
  writeOnHand({
    a01: [{ size: "M", color: "Kem", qty_on_hand: 1, status: "on_hand" }],
    S006: [{ size: "S", color: "Den", qty_on_hand: 2, status: "reserved" }],
    B02: [{ size: "L", color: "Do", qty_on_hand: 9, status: "on_hand" }],
  });

  const a01 = await maBody("a01");
  assert.equal(a01.code, "A01");
  assert.equal(a01.staged_only, false);
  assert.equal(a01.on_hand.length, 1);
  assert.equal(a01.on_hand[0]?.size, "M");
  assert.equal(a01.on_hand[0]?.qty_on_hand, 1);

  const s06 = await maBody("S006");
  assert.equal(s06.code, "S06");
  assert.equal(s06.staged_only, false);
  assert.equal(s06.on_hand.length, 1);
  assert.equal(s06.on_hand[0]?.size, "S");
  assert.equal(s06.on_hand[0]?.qty_on_hand, 2);

  const card = await lookupMaCard("A01");
  assert.equal(card?.on_hand.length, 1);
  assert.equal(card?.staged_only, false);
});

test("an empty canonical on-hand bucket wins over an alias and aliases are not summed", async () => {
  await savePlain("A", { color: "Kem", size: "M" });
  writeOnHand({
    A01: [],
    a01: [{ size: "M", color: "Kem", qty_on_hand: 4, status: "on_hand" }],
    A001: [{ size: "L", color: "Kem", qty_on_hand: 5, status: "sold" }],
  });

  const exact = await maBody("A01");
  assert.equal(exact.staged_only, true);
  assert.deepEqual(exact.on_hand, []);

  writeOnHand({
    A001: [{ size: "L", color: "Kem", qty_on_hand: 5, status: "sold" }],
    a01: [{ size: "M", color: "Kem", qty_on_hand: 4, status: "on_hand" }],
  });
  const alias = await maBody("A001");
  assert.equal(alias.code, "A01");
  assert.equal(alias.on_hand.length, 1);
  assert.equal(alias.on_hand[0]?.qty_on_hand, 4);
});
