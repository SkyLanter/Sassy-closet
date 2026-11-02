import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { afterEach, beforeEach, describe, test } from "node:test";
import { GET } from "../app/api/export/route";
import { resetStoreBackendForTests } from "../lib/store-backend";
import { exportCsv, getSubmission, listSubmissions, saveSubmission, type SaveInput } from "../lib/store";

const COLOR = "Kem, Xanh";
const NOTE = 'say "hi"\nline';

function saveInput(overrides: Partial<SaveInput> = {}): SaveInput {
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

function parseCsv(text: string): string[][] {
  const source = text.endsWith("\n") ? text.slice(0, -1) : text;
  const rows: string[][] = [];
  let row: string[] = [];
  let cell = "";
  let quoted = false;
  for (let i = 0; i < source.length; i += 1) {
    const ch = source[i] ?? "";
    if (quoted) {
      if (ch === '"') {
        if (source[i + 1] === '"') {
          cell += '"';
          i += 1;
        } else {
          quoted = false;
        }
      } else {
        cell += ch;
      }
      continue;
    }
    if (ch === '"') {
      quoted = true;
      continue;
    }
    if (ch === ",") {
      row.push(cell);
      cell = "";
      continue;
    }
    if (ch === "\n") {
      row.push(cell);
      rows.push(row);
      row = [];
      cell = "";
      continue;
    }
    cell += ch;
  }
  if (cell.length > 0 || row.length > 0) {
    row.push(cell);
    rows.push(row);
  }
  return rows;
}

describe("intake save and export under a legacy mã", { concurrency: 1 }, () => {
  let tmp = "";
  const prev: Record<string, string | undefined> = {};

  beforeEach(() => {
    tmp = fs.mkdtempSync(path.join(os.tmpdir(), "intake-legacy-ma-"));
    for (const key of [
      "SASSY_DATA_DIR",
      "VERCEL",
      "BLOB_READ_WRITE_TOKEN",
      "BLOB_STORE_ID",
      "BLOB_ACCESS",
      "INTAKE_DATASET_SYNC_WEBHOOK_URL",
      "INTAKE_DATASET_SYNC_WEBHOOK_KEY",
    ]) {
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

  test("a padded existing mã updates the one row, and the export keeps commas and newlines inside cells", async () => {
    const created = await saveSubmission(saveInput());
    assert.equal(created.ma, "A01");

    const recolored = await saveSubmission(
      saveInput({
        existingMa: "a1",
        color: COLOR,
      }),
    );
    assert.equal(recolored.id, created.id);
    assert.equal(recolored.ma, "A01");
    assert.equal(recolored.color, COLOR);

    const updated = await saveSubmission(
      saveInput({
        existingMa: "a0001",
        color: COLOR,
        color_note: NOTE,
      }),
    );
    assert.equal(updated.id, created.id);
    assert.equal(updated.ma, "A01");
    assert.equal(updated.color, COLOR);
    assert.equal(updated.color_note, NOTE);

    const listed = await listSubmissions();
    assert.equal(listed.length, 1);
    assert.equal(listed[0]?.ma, "A01");

    for (const spelling of ["A01", "a01", "a1", "a001", "a0001"]) {
      const found = await getSubmission(spelling);
      assert.equal(found?.id, created.id, spelling);
      assert.equal(found?.color, COLOR, spelling);
    }

    const csv = await exportCsv();
    const response = await GET();
    assert.equal(response.status, 200);
    assert.equal(await response.text(), csv);

    const rows = parseCsv(csv);
    assert.equal(rows.length, 2);
    const header = rows[0] ?? [];
    const data = rows[1] ?? [];
    const colorAt = header.indexOf("color");
    const noteAt = header.indexOf("color_note");
    const maAt = header.indexOf("ma");
    assert.ok(colorAt >= 0);
    assert.ok(noteAt >= 0);
    assert.equal(header.length, data.length);
    assert.equal(data[maAt], "A01");
    assert.equal(data[colorAt], COLOR);
    assert.equal(data[noteAt], NOTE);
  });
});
