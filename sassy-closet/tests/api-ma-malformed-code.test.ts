import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import test from "node:test";
import { adminRequest } from "./admin-request";

// Next already decodes [code]; a second decodeURIComponent throws URIError on a
// literal "%" (request /api/ma/%25), turning a lookup miss into a 500.
test("/api/ma/[code] answers 404, not a throw, for a code containing %", async () => {
  const tmp = fs.mkdtempSync(path.join(os.tmpdir(), "intake-170-"));
  const saved = { ...process.env };
  for (const k of Object.keys(process.env)) if (/BLOB|KV_|VERCEL/.test(k)) delete process.env[k];
  process.env.SASSY_DATA_DIR = tmp;
  try {
    const { resetStoreBackendForTests } = await import("../lib/store-backend");
    resetStoreBackendForTests();
    const { GET } = await import("../app/api/ma/[code]/route");
    for (const code of ["%", "A0%", "%E0%A4%A"]) {
      const res = await GET(await adminRequest("http://localhost/api/ma/x"), {
        params: Promise.resolve({ code }),
      });
      assert.equal(res.status, 404, code);
    }
  } finally {
    process.env = saved;
    fs.rmSync(tmp, { recursive: true, force: true });
  }
});
