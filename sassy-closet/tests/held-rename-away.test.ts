import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { afterEach, beforeEach, describe, test } from "node:test";
import { HELD_INCOMPLETE_MAS } from "../lib/held-incomplete";
import { getSubmission, listSubmissions, saveSubmission, type SaveInput } from "../lib/store";
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

describe("rename cannot leave a held mã or an off-lock S06", { concurrency: 1 }, () => {
  let tmp = "";
  const prev: Record<string, string | undefined> = {};

  beforeEach(() => {
    tmp = fs.mkdtempSync(path.join(os.tmpdir(), "sassy-held-rename-"));
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

  test("a held row stays held when the save names a free mã", async () => {
    const held = HELD_INCOMPLETE_MAS[0];
    assert.ok(held);
    await saveSubmission(blank());
    const file = path.join(tmp, "submissions.json");
    const store = JSON.parse(fs.readFileSync(file, "utf8")) as {
      submissions: { ma: string; kind: string }[];
    };
    store.submissions[0].ma = held;
    store.submissions[0].kind = held[0] ?? "A";
    fs.writeFileSync(file, JSON.stringify(store));

    await assert.rejects(
      () => saveSubmission(blank({ kind: held[0], existingMa: held, newMa: "A77" })),
      new RegExp(`Không lưu ${held} \\(held\\)`),
    );
    const rows = await listSubmissions();
    assert.deepEqual(rows.map((row) => row.ma), [held]);
    assert.equal(await getSubmission("A77"), null);
    assert.equal((await getSubmission(held))?.ma, held);
  });

  test("S06 cannot move to another mã at a different dollar", async () => {
    const locked = await saveSubmission(blank({ kind: "S", newMa: "S06", sell_usd: "25" }));
    assert.equal(locked.ma, "S06");
    assert.equal(locked.sell_usd, "25");

    await assert.rejects(
      () => saveSubmission(blank({ kind: "S", existingMa: "S06", newMa: "S07", sell_usd: "40" })),
      /Không lưu S06 \(s06-lock\)/,
    );
    const stayed = await getSubmission("S06");
    assert.equal(stayed?.sell_usd, "25");
    assert.equal(await getSubmission("S07"), null);
  });

  test("S06 can move when the locked dollar stays", async () => {
    await saveSubmission(blank({ kind: "S", newMa: "S06", sellUsd: "25" }));
    const moved = await saveSubmission(
      blank({ kind: "S", existingMa: "S06", newMa: "S07", sell_usd: "25" }),
    );
    assert.equal(moved.ma, "S07");
    assert.equal(moved.sell_usd, "25");
    assert.equal(await getSubmission("S06"), null);
  });

  test("a normal mã still renames", async () => {
    await saveSubmission(blank());
    const moved = await saveSubmission(blank({ existingMa: "A01", newMa: "A09" }));
    assert.equal(moved.ma, "A09");
    assert.equal(await getSubmission("A01"), null);
  });
});

function blank(overrides: Partial<SaveInput> = {}): SaveInput {
  return {
    kind: "A",
    size: "M",
    link: "",
    color: "Kem",
    color_note: "",
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
    ...overrides,
  };
}
