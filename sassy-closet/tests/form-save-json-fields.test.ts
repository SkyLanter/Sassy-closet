import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { afterEach, beforeEach, describe, test } from "node:test";
import { POST } from "../app/api/submissions/route";
import { saveFromForm } from "../lib/form-save";
import { exportCsv } from "../lib/store";
import { resetStoreBackendForTests } from "../lib/store-backend";

describe("form-save JSON array fields", { concurrency: 1 }, () => {
  let tmp = "";
  const prev: Record<string, string | undefined> = {};

  beforeEach(() => {
    tmp = fs.mkdtempSync(path.join(os.tmpdir(), "form-save-json-"));
    for (const key of Object.keys(process.env)) {
      if (/BLOB|KV_|VERCEL|INTAKE_DATASET/.test(key)) delete process.env[key];
    }
    prev.SASSY_DATA_DIR = process.env.SASSY_DATA_DIR;
    process.env.SASSY_DATA_DIR = tmp;
    resetStoreBackendForTests();
  });

  afterEach(() => {
    if (prev.SASSY_DATA_DIR === undefined) delete process.env.SASSY_DATA_DIR;
    else process.env.SASSY_DATA_DIR = prev.SASSY_DATA_DIR;
    resetStoreBackendForTests();
    fs.rmSync(tmp, { recursive: true, force: true });
  });

  test("rejects keep_photos JSON that is not an array", async () => {
    const form = new FormData();
    form.set("kind", "A");
    form.set("size", "M");
    form.set("keep_photos", "123");
    await assert.rejects(() => saveFromForm(form), /ảnh giữ/);
    const res = await POST(new Request("http://l/", { method: "POST", body: form }));
    assert.equal(res.status, 400);
    const body = (await res.json()) as { error: string };
    assert.match(body.error, /ảnh giữ/);
    assert.doesNotMatch(body.error, /not iterable/i);
  });

  test("rejects pieces JSON that is not an array", async () => {
    const form = new FormData();
    form.set("kind", "A");
    form.set("size", "M");
    form.set("pieces", "{}");
    form.set("keep_photos", "[]");
    await assert.rejects(() => saveFromForm(form), /Danh sách màu/);
  });

  test("drops invalid piece rows so CSV export still works", async () => {
    const form = new FormData();
    form.set("kind", "A");
    form.set("size", "M");
    form.set(
      "pieces",
      JSON.stringify([
        null,
        {
          id: "p1",
          photos: [],
          suggested: ["Đỏ"],
          color: "Đỏ",
          note: "",
        },
      ]),
    );
    form.set("keep_photos", "[]");
    await saveFromForm(form);
    const csv = await exportCsv();
    assert.match(csv, /A\d+,A,/);
  });
});