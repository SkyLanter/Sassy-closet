import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { afterEach, beforeEach, test } from "node:test";
import { POST } from "../app/api/submissions/route.ts";
import { GET, PATCH } from "../app/api/submissions/[ma]/route.ts";
import { costCnyWarning, explainIntakeFailure } from "../lib/intake-errors";
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
  "NEW_MA_WEBHOOK_URL",
  "NEW_MA_WEBHOOK_TOKEN",
] as const;

const prev: Partial<Record<(typeof ENV_KEYS)[number], string | undefined>> = {};
let tmp = "";

beforeEach(() => {
  tmp = fs.mkdtempSync(path.join(os.tmpdir(), "sassy-intake-errors-"));
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

test("blank ¥ warns and a real number does not", () => {
  const blank = costCnyWarning("  ");
  assert.equal(blank?.kind, "blank");
  assert.match(blank?.text ?? "", /Chưa có giá ¥/);
  assert.match(blank?.text ?? "", /Vẫn lưu được/);
  assert.equal(costCnyWarning("87.23"), null);
  const garbled = costCnyWarning("127;145");
  assert.equal(garbled?.kind, "garbled");
  assert.match(garbled?.text ?? "", /87\.23/);
  assert.match(garbled?.text ?? "", /Vẫn lưu được/);
});

test("block codes become a reason and a next-code sentence is left alone", () => {
  const held = explainIntakeFailure("Không lưu K06 (held).");
  assert.match(held, /Chưa lưu được K06/);
  assert.match(held, /đang được giữ lại/);
  assert.match(held, /Không có gì được ghi/);
  assert.doesNotMatch(held, /\(held\)|K07/);
  assert.equal(explainIntakeFailure(held), held);

  const minted = explainIntakeFailure("Không mint V05 (held).");
  assert.match(minted, /Chưa lấy được mã mới V05/);
  assert.doesNotMatch(minted, /V06|mã kế/);

  assert.match(explainIntakeFailure("Không lưu Q02 (never-list)."), /không được dùng/);
  const locked = explainIntakeFailure("Không lưu S06 (s06-lock).");
  assert.match(locked, /\$25 hoặc để trống/);
  assert.match(locked, /không được ghi/);
  assert.match(explainIntakeFailure("Không lưu A01 (reused)."), /không gộp vào mã cũ/);
  assert.doesNotMatch(explainIntakeFailure("Không lưu A01 (duplicate)."), /A02/);

  const suggested = "Mã A01 đã có rồi — không gộp nha 💕 Mã trống tiếp là A02.";
  assert.equal(explainIntakeFailure(suggested), suggested);
  assert.equal(explainIntakeFailure(""), "Chưa lưu được mã. Không có gì được ghi. Thử lại.");
  assert.equal(
    explainIntakeFailure("Không tìm thấy mã này 🥺"),
    "Không tìm thấy mã này. Kiểm tra chữ và số rồi mở lại.",
  );
});

test("store still throws the block code and the route explains it without writing", async () => {
  await assert.rejects(
    () =>
      saveSubmission({
        kind: "K",
        size: "",
        link: "",
        color: "",
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
        newMa: "K06",
        needs_research: false,
        taobao_snapshot: null,
        auto_price: null,
      }),
    /Không lưu K06 \(held\)\./,
  );

  const form = new FormData();
  form.set("kind", "K");
  form.set("new_ma", "K06");
  form.set("cost_cny", "");
  const response = await POST(
    new Request("http://127.0.0.1/api/submissions", { method: "POST", body: form }),
  );
  assert.equal(response.status, 409);
  const body = (await response.json()) as { error?: string };
  assert.match(body.error ?? "", /Chưa lưu được K06/);
  assert.match(body.error ?? "", /Không có gì được ghi/);
  assert.doesNotMatch(body.error ?? "", /\(held\)/);
  assert.equal(fs.existsSync(path.join(tmp, "submissions.json")), false);
});

test("S06 off $25 is explained and a blank ¥ row can still be saved", async () => {
  const locked = new FormData();
  locked.set("kind", "S");
  locked.set("new_ma", "S06");
  locked.set("sell_usd", "30");
  const refused = await POST(
    new Request("http://127.0.0.1/api/submissions", { method: "POST", body: locked }),
  );
  assert.equal(refused.status, 409);
  const refusedBody = (await refused.json()) as { error?: string };
  assert.match(refusedBody.error ?? "", /\$25 hoặc để trống/);
  assert.equal(fs.existsSync(path.join(tmp, "submissions.json")), false);

  const open = new FormData();
  open.set("kind", "A");
  open.set("new_ma", "A90");
  open.set("cost_cny", "");
  open.set("sell_usd", "");
  const saved = await POST(
    new Request("http://127.0.0.1/api/submissions", { method: "POST", body: open }),
  );
  assert.equal(saved.status, 200);
  const savedBody = (await saved.json()) as { submission?: { ma: string; cost_cny: string; sell_usd: string } };
  assert.equal(savedBody.submission?.ma, "A90");
  assert.equal(savedBody.submission?.cost_cny, "");
  assert.equal(savedBody.submission?.sell_usd, "");

  const missing = await GET(new Request("http://127.0.0.1/api/submissions/Z99"), {
    params: Promise.resolve({ ma: "Z99" }),
  });
  assert.equal(missing.status, 404);
  const missingBody = (await missing.json()) as { error?: string };
  assert.equal(missingBody.error, "Không tìm thấy mã này. Kiểm tra chữ và số rồi mở lại.");

  const patch = new FormData();
  patch.set("kind", "A");
  patch.set("new_ma", "K06");
  const renamed = await PATCH(new Request("http://127.0.0.1/api/submissions/A90", { method: "PATCH", body: patch }), {
    params: Promise.resolve({ ma: "A90" }),
  });
  assert.equal(renamed.status, 409);
  const renamedBody = (await renamed.json()) as { error?: string };
  assert.match(renamedBody.error ?? "", /Chưa lưu được K06/);
  const rows = JSON.parse(fs.readFileSync(path.join(tmp, "submissions.json"), "utf8")) as {
    submissions: { ma: string; sell_usd: string }[];
  };
  assert.deepEqual(
    rows.submissions.map((row) => row.ma),
    ["A90"],
  );
  assert.equal(rows.submissions[0]?.sell_usd, "");
});
