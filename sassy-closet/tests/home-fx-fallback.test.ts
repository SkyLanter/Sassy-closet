import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import test from "node:test";
import { getHomeFx } from "../lib/home-fx";

test("FX read failure -> default display rate, no throw, no secret", async () => {
  const fx = await getHomeFx(async () => {
    throw new Error("Vercel Blob: This store is blocked. vercel_blob_rw_SECRET");
  });
  assert.equal(fx.fallback, true);
  assert.equal(fx.usd_cny, 6.71);
  assert.ok(!fx.label.includes("SECRET"));
});

test("FX success path unchanged", async () => {
  const fx = await getHomeFx(async () => ({ usd_cny: 7.1, updated: "2026-10-01", label: "L" }));
  assert.deepEqual(fx, { usd_cny: 7.1, label: "L", fallback: false });
});

test("HomePage renders the form with default rate when the store is unreadable", async () => {
  const tmp = fs.mkdtempSync(path.join(os.tmpdir(), "intake-233c-"));
  const saved = { ...process.env };
  for (const k of Object.keys(process.env)) if (/BLOB|KV_|VERCEL/.test(k)) delete process.env[k];
  process.env.SASSY_DATA_DIR = tmp;
  fs.writeFileSync(path.join(tmp, "submissions.json"), "{not json");
  const { resetStoreBackendForTests } = await import("../lib/store-backend");
  resetStoreBackendForTests();
  try {
    // tsx compiles JSX in classic mode in tests; Next uses the automatic runtime.
    (globalThis as { React?: unknown }).React = await import("react");
    const { default: HomePage } = await import("../app/page");
    const el = (await HomePage()) as { props: { initialFxRate: number; initialFxLabel: string } };
    assert.equal(el.props.initialFxRate, 6.71);
    assert.match(el.props.initialFxLabel, /mặc định/);
  } finally {
    process.env = saved;
    resetStoreBackendForTests();
    fs.rmSync(tmp, { recursive: true, force: true });
  }
});
