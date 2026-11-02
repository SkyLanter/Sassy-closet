import assert from "node:assert/strict";
import fs from "node:fs";
import { createRequire } from "node:module";
import os from "node:os";
import path from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";
import { HELD_INCOMPLETE_MAS } from "../lib/held-incomplete";
import { invalidateLiveCatalogMemo } from "../lib/catalog-store";

const shopRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const require = createRequire(import.meta.url);
const { workAsyncStorage } = require(
  path.join(shopRoot, "node_modules/next/dist/server/app-render/work-async-storage.external.js"),
) as {
  workAsyncStorage: { run: <T>(store: { forceStatic: true; route: string }, fn: () => T) => T };
};

/** connection() bails out of a static shell. Tests are not a Next request. */
function inRequest<T>(fn: () => Promise<T>): Promise<T> {
  return workAsyncStorage.run({ forceStatic: true, route: "/share" }, fn);
}

function saveEnv(): NodeJS.ProcessEnv {
  return { ...process.env };
}

function stripLiveStores() {
  for (const key of Object.keys(process.env)) {
    if (/BLOB|KV_|VERCEL/.test(key)) delete process.env[key];
  }
}

async function withShopCwd(fn: () => Promise<void>) {
  const cwd = process.cwd();
  const saved = saveEnv();
  stripLiveStores();
  process.chdir(shopRoot);
  invalidateLiveCatalogMemo();
  try {
    await fn();
  } finally {
    invalidateLiveCatalogMemo();
    process.chdir(cwd);
    process.env = saved;
  }
}

test("a corrupt catalog does not paint the home card on a product or category share URL", async () => {
  const tmp = fs.mkdtempSync(path.join(os.tmpdir(), "share-unavailable-"));
  const cwd = process.cwd();
  const saved = saveEnv();
  stripLiveStores();
  try {
    fs.mkdirSync(path.join(tmp, "data"), { recursive: true });
    fs.writeFileSync(path.join(tmp, "data", "live-catalog.json"), "{");
    process.chdir(tmp);
    invalidateLiveCatalogMemo();
    const product = await import("../app/share/m/[ma]/route");
    const category = await import("../app/share/c/[slug]/route");
    const productRes = await inRequest(() =>
      product.GET(new Request("https://example.invalid/share/m/A01"), {
        params: Promise.resolve({ ma: "A01" }),
      }),
    );
    const categoryRes = await inRequest(() =>
      category.GET(new Request("https://example.invalid/share/c/ao"), {
        params: Promise.resolve({ slug: "ao" }),
      }),
    );
    for (const res of [productRes, categoryRes]) {
      assert.equal(res.status, 503);
      assert.match(res.headers.get("content-type") ?? "", /text\/plain/);
      assert.match(res.headers.get("cache-control") ?? "", /no-store/);
      const text = await res.text();
      assert.equal(text, "Share card unavailable");
      assert.equal(text.startsWith("\xff\xd8"), false);
    }
  } finally {
    invalidateLiveCatalogMemo();
    process.chdir(cwd);
    process.env = saved;
    fs.rmSync(tmp, { recursive: true, force: true });
  }
});

test("a held mã and an unknown category share URL 404 and are not stored", async () => {
  const held = HELD_INCOMPLETE_MAS[0];
  assert.ok(held);
  await withShopCwd(async () => {
    const product = await import("../app/share/m/[ma]/route");
    const category = await import("../app/share/c/[slug]/route");
    const heldRes = await inRequest(() =>
      product.GET(new Request(`https://example.invalid/share/m/${held}`), {
        params: Promise.resolve({ ma: held }),
      }),
    );
    const missingRes = await inRequest(() =>
      category.GET(new Request("https://example.invalid/share/c/not-a-rack"), {
        params: Promise.resolve({ slug: "not-a-rack" }),
      }),
    );
    for (const res of [heldRes, missingRes]) {
      assert.equal(res.status, 404);
      assert.equal(await res.text(), "Not found");
      assert.match(res.headers.get("cache-control") ?? "", /no-store/);
    }
  });
});

test("a listed mã still gets its own jpeg share card", async () => {
  await withShopCwd(async () => {
    const product = await import("../app/share/m/[ma]/route");
    const res = await inRequest(() =>
      product.GET(new Request("https://example.invalid/share/m/A01"), {
        params: Promise.resolve({ ma: "A01" }),
      }),
    );
    assert.equal(res.status, 200);
    assert.match(res.headers.get("content-type") ?? "", /image\/jpeg/);
    const bytes = new Uint8Array(await res.arrayBuffer());
    assert.equal(bytes[0], 0xff);
    assert.equal(bytes[1], 0xd8);
  });
});
