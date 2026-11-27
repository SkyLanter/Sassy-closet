import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { afterEach, beforeEach, describe, test } from "node:test";
import { resetStoreBackendForTests } from "../lib/store-backend";
import { exportCsv, saveSubmission, type SaveInput } from "../lib/store";

/**
 * A color or note can carry a carriage return or a Unicode line separator
 * from a paste. Those bytes are record breaks for a CSV reader unless the
 * cell is quoted, so one mã was coming back as two rows.
 */
describe("export CSV line breaks", { concurrency: 1 }, () => {
  let tmp = "";
  const prev: Record<string, string | undefined> = {};

  beforeEach(() => {
    tmp = fs.mkdtempSync(path.join(os.tmpdir(), "csv-break-"));
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

  test("a carriage return or Unicode line break stays inside one cell", async () => {
    const hugeNote = `${"Đ".repeat(4000)}\rgiữa\u2028cuối`;
    await saveRow({
      color: "Đỏ\rKem",
      color_note: hugeNote,
      newMa: "A01",
    });
    await saveRow({
      color: "Đỏ",
      color_note: "",
      newMa: "A02",
    });
    await saveRow({
      color: "",
      color_note: "trống",
      newMa: "A03",
    });
    await saveRow({
      color: "Đỏ\u2028Kem",
      color_note: "trên\u2029dưới",
      newMa: "A04",
    });

    const csv = await exportCsv();
    const rows = parseCsv(csv);
    assert.equal(rows.length, 5);
    const byMa = Object.fromEntries(rows.slice(1).map((row) => [row[0], row]));
    const headers = rows[0];
    const colorAt = headers.indexOf("color");
    const noteAt = headers.indexOf("color_note");

    assert.equal(byMa.A01?.[colorAt], "Đỏ\rKem");
    assert.equal(byMa.A01?.[noteAt], hugeNote);
    assert.equal(byMa.A02?.[colorAt], "Đỏ");
    assert.equal(csv.includes('"Đỏ"'), false);
    assert.equal(byMa.A03?.[colorAt], "");
    assert.equal(byMa.A03?.[noteAt], "trống");
    assert.equal(byMa.A04?.[colorAt], "Đỏ\u2028Kem");
    assert.equal(byMa.A04?.[noteAt], "trên\u2029dưới");
  });
});

function saveRow(input: Pick<SaveInput, "color" | "color_note" | "newMa">) {
  return saveSubmission({
    kind: "A",
    size: "M",
    link: "",
    color: input.color,
    color_note: input.color_note,
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
    newMa: input.newMa,
  });
}

/**
 * CR, LF, CRLF, and Unicode line separators end a record when they sit
 * outside quotes. A quoted cell keeps those characters in the value.
 */
function parseCsv(text: string): string[][] {
  const rows: string[][] = [];
  let row: string[] = [];
  let cell = "";
  let quoted = false;
  for (let i = 0; i < text.length; i += 1) {
    const char = text[i] ?? "";
    if (quoted) {
      if (char === '"') {
        if (text[i + 1] === '"') {
          cell += '"';
          i += 1;
        } else {
          quoted = false;
        }
      } else {
        cell += char;
      }
      continue;
    }
    if (char === '"') {
      quoted = true;
      continue;
    }
    if (char === ",") {
      row.push(cell);
      cell = "";
      continue;
    }
    if (char === "\n" || char === "\r" || char === "\u2028" || char === "\u2029") {
      if (char === "\r" && text[i + 1] === "\n") i += 1;
      row.push(cell);
      cell = "";
      if (!(row.length === 1 && row[0] === "")) rows.push(row);
      row = [];
      continue;
    }
    cell += char;
  }
  if (cell !== "" || row.length > 0) {
    row.push(cell);
    rows.push(row);
  }
  return rows;
}
