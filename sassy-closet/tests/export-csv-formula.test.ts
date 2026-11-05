import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { afterEach, beforeEach, test } from "node:test";
import { exportCsv, saveSubmission } from "../lib/store";
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
  tmp = fs.mkdtempSync(path.join(os.tmpdir(), "csv-formula-"));
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

function parseLine(line: string): string[] {
  const cells: string[] = [];
  let index = 0;
  while (index < line.length) {
    if (line[index] === '"') {
      let value = "";
      index += 1;
      while (index < line.length) {
        if (line[index] === '"') {
          if (line[index + 1] === '"') {
            value += '"';
            index += 2;
            continue;
          }
          index += 1;
          break;
        }
        value += line[index] ?? "";
        index += 1;
      }
      cells.push(value);
      if (line[index] === ",") index += 1;
      continue;
    }
    const comma = line.indexOf(",", index);
    const end = comma === -1 ? line.length : comma;
    cells.push(line.slice(index, end));
    index = comma === -1 ? line.length : comma + 1;
  }
  return cells;
}

function rowByMa(csv: string, ma: string): Record<string, string> {
  const lines = csv.trimEnd().split("\n");
  const headers = parseLine(lines[0] ?? "");
  const match = lines.slice(1).map(parseLine).find((cells) => cells[0] === ma);
  assert.ok(match, `missing ${ma}`);
  return Object.fromEntries(headers.map((header, index) => [header, match[index] ?? ""]));
}

test("CSV export keeps formula-like cells as text and leaves plain cells alone", async () => {
  await saveSubmission({
    kind: "A",
    size: "M",
    link: "",
    color: "=1+1",
    color_note: "+note",
    pieces: [],
    ...blankMoney(),
    keep_photos: [],
    photos: [],
    needs_research: false,
    taobao_snapshot: null,
    auto_price: null,
  });
  await saveSubmission({
    kind: "A",
    size: "S",
    link: "",
    color: "plain",
    color_note: "@handle",
    pieces: [],
    ...blankMoney(),
    keep_photos: [],
    photos: [],
    needs_research: false,
    taobao_snapshot: null,
    auto_price: null,
  });
  const diskPath = path.join(tmp, "submissions.json");
  const disk = JSON.parse(fs.readFileSync(diskPath, "utf8")) as {
    submissions: { ma: string; color: string }[];
  };
  const stored = disk.submissions.find((item) => item.ma === "A02");
  assert.ok(stored);
  stored.color = "\t=1+1";
  fs.writeFileSync(diskPath, JSON.stringify(disk));
  resetStoreBackendForTests();
  await saveSubmission({
    kind: "A",
    size: "L",
    link: "",
    color: "Kem",
    color_note: "red, blue",
    pieces: [],
    ...blankMoney(),
    keep_photos: [],
    photos: [],
    needs_research: false,
    taobao_snapshot: null,
    auto_price: null,
  });

  const csv = await exportCsv();
  const formula = rowByMa(csv, "A01");
  const tabbed = rowByMa(csv, "A02");
  const plain = rowByMa(csv, "A03");

  assert.equal(formula.color, "'=1+1");
  assert.equal(formula.color_note, "'+note");
  assert.equal(formula.ma, "A01");
  assert.equal(tabbed.color, "'\t=1+1");
  assert.equal(tabbed.color_note, "'@handle");
  assert.equal(plain.color, "Kem");
  assert.equal(plain.color_note, "red, blue");
  assert.equal(plain.size, "L");
  assert.match(csv, /"'=1\+1"/);
  assert.doesNotMatch(csv, /(^|,)=1\+1(,|\n)/);
  assert.doesNotMatch(csv, /(^|,)\+note(,|\n)/);
});
