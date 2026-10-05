import assert from "node:assert/strict";
import { createServer, type Server } from "node:http";
import { mkdtempSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import path from "node:path";
import { afterEach, test } from "node:test";
import { NextRequest } from "next/server";
import {
  ADMIN_SESSION_COOKIE,
  ADMIN_SESSION_MAX_AGE_SECONDS,
  adminAuthConfigured,
  createAdminSessionToken,
  passwordMatches,
  verifyAdminSession,
} from "../lib/admin-auth";
import { loginAttemptAllowed, recordLoginFailure, resetLoginBuckets } from "../lib/admin-login-rate";
import { shopAdminGate } from "../lib/shop-admin-gate";
import {
  applyShopCatalogPatch,
  memoryShopCatalogPort,
  saveShopCatalogProduct,
} from "../lib/shop-catalog";
import { SHOP_REVALIDATE_HEADER, readShopRevalidateConfig } from "../lib/shop-revalidate";
import { middleware } from "../middleware";

const PASSWORD = "intake-shop-tools-test";
const SESSION_SECRET = "intake-shop-session-test";
const REVALIDATE_SECRET = "intake-revalidate-test";

const ENV_KEYS = [
  "ADMIN_PASSWORD",
  "ADMIN_SESSION_SECRET",
  "SHOP_BLOB_READ_WRITE_TOKEN",
  "BLOB_READ_WRITE_TOKEN",
  "SHOP_REVALIDATE_SECRET",
  "SHOP_REVALIDATE_URL",
  "SHOP_CATALOG_FILE",
  "VERCEL",
] as const;

const previous: Partial<Record<(typeof ENV_KEYS)[number], string | undefined>> = {};
for (const key of ENV_KEYS) {
  previous[key] = process.env[key];
}

afterEach(() => {
  resetLoginBuckets();
  for (const key of ENV_KEYS) {
    const value = previous[key];
    if (value === undefined) {
      delete process.env[key];
    } else {
      process.env[key] = value;
    }
  }
});

function sampleCatalog(): Record<string, unknown> {
  return {
    schema: "catalog.v1",
    version: 1,
    siteId: "sassy-closet-shop",
    allowlist: ["A01"],
    settings: { announcementLines: ["keep"], facebookPageUrl: "https://example.com/page" },
    products: [
      {
        ma: "A01",
        type: "A",
        titleVn: "Áo len puppy",
        titleEn: "Puppy cardigan",
        priceUsd: 20,
        qty: 1,
        status: "available",
        colors: [{ id: "ca0100", hex: "#F5D76E", name: "Yellow", note: "" }],
        images: [{ src: "/products/A01/cover.jpg", colorId: "ca0100", order: 1 }],
        sizes: ["S", "M"],
        sourceLink: "https://e.tb.cn/example",
        extra: "keep-me",
      },
      {
        ma: "A03",
        type: "A",
        titleVn: "Áo test",
        titleEn: "Test top",
        priceUsd: 12,
        qty: 1,
        status: "available",
        colors: [{ id: "ca0300", hex: "#111111", name: "Black", note: "n" }],
        images: [],
        sizes: ["M"],
      },
    ],
  };
}

function catalogWithS06(
  priceUsd: number | null = 25,
  status: "available" | "hold" | "sold" = "available",
): Record<string, unknown> {
  const catalog = sampleCatalog();
  const products = catalog.products as Record<string, unknown>[];
  products.push({
    ma: "S06",
    type: "S",
    titleVn: "Set S06",
    titleEn: "Set S06",
    priceUsd,
    qty: 1,
    status,
    colors: [{ id: "cs0600", hex: "#ffffff", name: "White", note: "" }],
    images: [],
    sizes: ["M"],
  });
  return catalog;
}

function productRow(
  snapshot: string | null,
  ma: string,
): { ma: string; status: string; priceUsd: number | null; titleEn?: string } | undefined {
  const parsed = JSON.parse(snapshot ?? "{}") as {
    products: { ma: string; status: string; priceUsd: number | null; titleEn?: string }[];
  };
  return parsed.products.find((product) => product.ma === ma);
}

function listen(server: Server): Promise<number> {
  return new Promise((resolve, reject) => {
    server.listen(0, "127.0.0.1", () => {
      const address = server.address();
      if (!address || typeof address === "string") {
        reject(new Error("No port"));
        return;
      }
      resolve(address.port);
    });
  });
}

test("shop tools session is an HttpOnly cookie and fails closed", async () => {
  delete process.env.ADMIN_PASSWORD;
  delete process.env.ADMIN_SESSION_SECRET;
  assert.equal(adminAuthConfigured(), false);
  assert.equal(await passwordMatches(PASSWORD), false);
  assert.equal(await createAdminSessionToken(), null);
  process.env.ADMIN_PASSWORD = PASSWORD;
  process.env.ADMIN_SESSION_SECRET = SESSION_SECRET;
  assert.equal(await passwordMatches("nope"), false);
  assert.equal(await passwordMatches(PASSWORD), true);
  const issued = Date.now();
  const token = await createAdminSessionToken(issued);
  assert.ok(token);
  assert.equal(await verifyAdminSession(token, issued + 1000), true);
  assert.equal(await verifyAdminSession(token, issued + ADMIN_SESSION_MAX_AGE_SECONDS * 1000 + 1), false);
  assert.equal(await verifyAdminSession(`${token}x`, issued + 1000), false);
  assert.equal(token.includes(PASSWORD), false);

  const { POST } = await import("../app/api/shop-catalog/login/route.ts");
  const wrong = await POST(
    new Request("http://127.0.0.1/api/shop-catalog/login", {
      method: "POST",
      headers: { "content-type": "application/json", "x-forwarded-for": "203.0.113.10" },
      body: JSON.stringify({ password: "nope" }),
    }),
  );
  assert.equal(wrong.status, 401);
  const ok = await POST(
    new Request("http://127.0.0.1/api/shop-catalog/login", {
      method: "POST",
      headers: { "content-type": "application/json", "x-forwarded-for": "203.0.113.11" },
      body: JSON.stringify({ password: PASSWORD }),
    }),
  );
  assert.equal(ok.status, 200);
  const setCookie = ok.headers.get("set-cookie") ?? "";
  assert.match(setCookie, new RegExp(`${ADMIN_SESSION_COOKIE}=`));
  assert.match(setCookie, /HttpOnly/i);
  assert.match(setCookie, /Secure/i);
  assert.match(setCookie, /SameSite=Lax/i);
  assert.doesNotMatch(setCookie, /Domain=/i);
  assert.match(setCookie, /Max-Age=2592000/);
});

test("login locks after repeated failures and stays locked when unset", async () => {
  const ip = "203.0.113.12";
  const now = Date.now();
  for (let attempt = 0; attempt < 5; attempt += 1) {
    recordLoginFailure(ip, now);
  }
  const limited = loginAttemptAllowed(ip, now + 1);
  assert.equal(limited.ok, false);

  delete process.env.ADMIN_PASSWORD;
  delete process.env.ADMIN_SESSION_SECRET;
  const { POST } = await import("../app/api/shop-catalog/login/route.ts");
  const locked = await POST(
    new Request("http://127.0.0.1/api/shop-catalog/login", {
      method: "POST",
      headers: { "content-type": "application/json", "x-forwarded-for": "203.0.113.13" },
      body: JSON.stringify({ password: PASSWORD }),
    }),
  );
  assert.equal(locked.status, 503);
});

test("middleware locks shop tools and leaves intake admin export open", async () => {
  process.env.ADMIN_PASSWORD = PASSWORD;
  process.env.ADMIN_SESSION_SECRET = SESSION_SECRET;
  const token = await createAdminSessionToken();
  assert.ok(token);
  const denied = await middleware(new NextRequest("http://127.0.0.1/admin/shop"));
  assert.equal(denied.status, 307);
  assert.match(denied.headers.get("location") ?? "", /\/admin\/shop\/login$/);
  const api = await middleware(new NextRequest("http://127.0.0.1/api/shop-catalog"));
  assert.equal(api.status, 401);
  const csv = await middleware(new NextRequest("http://127.0.0.1/admin"));
  assert.equal(csv.status, 200);
  assert.equal(shopAdminGate("/", false), "public");
  const signed = await middleware(
    new NextRequest("http://127.0.0.1/admin/shop", {
      headers: { cookie: `${ADMIN_SESSION_COOKIE}=${token}` },
    }),
  );
  assert.equal(signed.status, 200);
});

test("catalog save edits an existing mã, writes its USD, and revalidates with the secret", async () => {
  delete process.env.SHOP_BLOB_READ_WRITE_TOKEN;
  delete process.env.BLOB_READ_WRITE_TOKEN;
  delete process.env.VERCEL;
  delete process.env.SHOP_REVALIDATE_SECRET;
  delete process.env.SHOP_REVALIDATE_URL;
  const catalog = sampleCatalog();
  const port = memoryShopCatalogPort(catalog);
  const missing = await saveShopCatalogProduct(port, { ma: "A01", titleEn: "Nope" });
  assert.equal(missing.status, 503);
  assert.match(port.snapshot() ?? "", /Puppy cardigan/);

  let seen = "";
  const server = createServer((request, response) => {
    seen = String(request.headers[SHOP_REVALIDATE_HEADER] ?? "");
    const ok = seen === REVALIDATE_SECRET && request.url === "/api/admin/revalidate";
    response.writeHead(ok ? 200 : 401);
    response.end("{}");
  });
  const portNumber = await listen(server);
  process.env.SHOP_REVALIDATE_SECRET = REVALIDATE_SECRET;
  process.env.SHOP_REVALIDATE_URL = `http://127.0.0.1:${portNumber}/api/admin/revalidate`;
  try {
    const repriced = await saveShopCatalogProduct(port, { ma: "A01", priceUsd: 27 });
    assert.equal(repriced.ok, true);
    assert.match(port.snapshot() ?? "", /"priceUsd": 27/);

    const invented = await saveShopCatalogProduct(port, { ma: "B99", titleEn: "New" });
    assert.equal(invented.status, 400);
    assert.match(invented.error ?? "", /not in the catalog/);

    const saved = await saveShopCatalogProduct(
      port,
      {
        ma: "a01",
        titleEn: "Puppy cardigan edited",
        colors: [{ id: "ca0100", name: "Yellow gold" }],
      },
      { now: "2026-09-28T00:00:00.000Z" },
    );
    assert.equal(saved.ok, true);
    assert.equal(seen, REVALIDATE_SECRET);
    const written = port.snapshot() ?? "";
    assert.match(written, /Puppy cardigan edited/);
    assert.match(written, /"priceUsd": 27/);
    assert.match(written, /https:\/\/e\.tb\.cn\/example/);
    assert.match(written, /keep-me/);
    assert.match(written, /Yellow gold/);
    assert.match(written, /"sizes": \[\s*"S"/);
    assert.equal(written.includes("presentLockedBossPrices"), false);

    const hold = await saveShopCatalogProduct(port, { ma: "A03", status: "hold", priceUsd: 12 });
    assert.equal(hold.ok, true);
    const afterHold = JSON.parse(port.snapshot() ?? "{}") as {
      products: { ma: string; status: string; priceUsd: number | null }[];
    };
    const a03 = afterHold.products.find((product) => product.ma === "A03");
    assert.equal(a03?.status, "hold");
    assert.equal(a03?.priceUsd, null);
  } finally {
    server.close();
  }
});

test("shop tools save refuses to leave S06 anything other than available at $25", async () => {
  const revalidate = async () => {
    throw new Error("revalidate must not run when S06 is refused");
  };
  const port = memoryShopCatalogPort(catalogWithS06());

  const cheaper = await saveShopCatalogProduct(
    port,
    { ma: "s06", status: "available", priceUsd: 19 },
    { revalidate },
  );
  assert.equal(cheaper.ok, false);
  if (!cheaper.ok) {
    assert.equal(cheaper.status, 400);
    assert.equal(cheaper.blobWritten, false);
    assert.equal(cheaper.error, "S06 stays available at $25.");
  }
  assert.equal(productRow(port.snapshot(), "S06")?.status, "available");
  assert.equal(productRow(port.snapshot(), "S06")?.priceUsd, 25);

  const hold = applyShopCatalogPatch(catalogWithS06(), { ma: "S06", status: "hold", priceUsd: 25 }, "t");
  assert.equal(hold.ok, false);
  if (!hold.ok) {
    assert.equal(hold.error, "S06 stays available at $25.");
  }
  const cleared = await saveShopCatalogProduct(port, { ma: "S06", status: "hold", priceUsd: null }, { revalidate });
  assert.equal(cleared.ok, false);
  if (!cleared.ok) {
    assert.equal(cleared.blobWritten, false);
  }
  assert.equal(productRow(port.snapshot(), "S06")?.priceUsd, 25);
  assert.equal(productRow(port.snapshot(), "S06")?.status, "available");

  const sold = applyShopCatalogPatch(catalogWithS06(), { ma: "S06", status: "sold", priceUsd: 25 }, "t");
  assert.equal(sold.ok, false);
  const other = applyShopCatalogPatch(catalogWithS06(), { ma: "S06", priceUsd: 30 }, "t");
  assert.equal(other.ok, false);

  let calls = 0;
  const allow = async () => {
    calls += 1;
    return { ok: true as const };
  };
  const titled = await saveShopCatalogProduct(
    port,
    { ma: "S06", titleEn: "Set S06 renamed" },
    { now: "2026-10-05T00:00:00.000Z", revalidate: allow },
  );
  assert.equal(titled.ok, true);
  assert.equal(calls, 1);
  assert.equal(productRow(port.snapshot(), "S06")?.titleEn, "Set S06 renamed");
  assert.equal(productRow(port.snapshot(), "S06")?.status, "available");
  assert.equal(productRow(port.snapshot(), "S06")?.priceUsd, 25);

  const sameDollar = await saveShopCatalogProduct(
    port,
    { ma: "S06", status: "available", priceUsd: 25 },
    { revalidate: allow },
  );
  assert.equal(sameDollar.ok, true);

  const a01 = await saveShopCatalogProduct(port, { ma: "A01", priceUsd: 27 }, { revalidate: allow });
  assert.equal(a01.ok, true);
  const a03 = await saveShopCatalogProduct(
    port,
    { ma: "A03", status: "hold", priceUsd: 12 },
    { revalidate: allow },
  );
  assert.equal(a03.ok, true);
  assert.equal(productRow(port.snapshot(), "A01")?.priceUsd, 27);
  assert.equal(productRow(port.snapshot(), "A03")?.status, "hold");
  assert.equal(productRow(port.snapshot(), "A03")?.priceUsd, null);
  assert.equal(productRow(port.snapshot(), "S06")?.status, "available");
  assert.equal(productRow(port.snapshot(), "S06")?.priceUsd, 25);

  const drifted = memoryShopCatalogPort(catalogWithS06(19, "available"));
  const titleOnly = await saveShopCatalogProduct(
    drifted,
    { ma: "S06", titleEn: "Should not stick" },
    { revalidate },
  );
  assert.equal(titleOnly.ok, false);
  if (!titleOnly.ok) {
    assert.equal(titleOnly.blobWritten, false);
  }
  assert.match(drifted.snapshot() ?? "", /"priceUsd": 19/);
  assert.equal((drifted.snapshot() ?? "").includes("Should not stick"), false);
  const restored = await saveShopCatalogProduct(
    drifted,
    { ma: "S06", status: "available", priceUsd: 25 },
    { revalidate: allow },
  );
  assert.equal(restored.ok, true);
  assert.equal(productRow(drifted.snapshot(), "S06")?.status, "available");
  assert.equal(productRow(drifted.snapshot(), "S06")?.priceUsd, 25);

  const source = readFileSync(path.join(process.cwd(), "lib/shop-catalog.ts"), "utf8");
  assert.equal(source.includes("HELD_INCOMPLETE"), false);
  assert.equal(source.includes("isHeldIncompleteMa"), false);
  assert.equal(source.includes("presentLockedBossPrices"), false);
  for (const ma of ["S14", "A24", "A25", "S15", "A26", "K02", "K03", "K04", "K05", "V04", "Q02"]) {
    assert.equal(source.includes(`"${ma}"`), false, ma);
  }
});

test("signed-in save route refuses an S06 reprice or hold and leaves the file unchanged", async () => {
  delete process.env.SHOP_BLOB_READ_WRITE_TOKEN;
  delete process.env.BLOB_READ_WRITE_TOKEN;
  delete process.env.VERCEL;
  process.env.ADMIN_PASSWORD = PASSWORD;
  process.env.ADMIN_SESSION_SECRET = SESSION_SECRET;
  process.env.SHOP_REVALIDATE_SECRET = REVALIDATE_SECRET;
  const dir = mkdtempSync(path.join(tmpdir(), "shop-catalog-s06-"));
  const file = path.join(dir, "catalog.v1.json");
  const original = `${JSON.stringify(catalogWithS06(), null, 2)}\n`;
  writeFileSync(file, original);
  process.env.SHOP_CATALOG_FILE = file;
  const token = await createAdminSessionToken();
  assert.ok(token);
  let hits = 0;
  const server = createServer((request, response) => {
    hits += 1;
    assert.equal(request.headers[SHOP_REVALIDATE_HEADER], REVALIDATE_SECRET);
    response.writeHead(200);
    response.end('{"ok":true}');
  });
  const portNumber = await listen(server);
  process.env.SHOP_REVALIDATE_URL = `http://127.0.0.1:${portNumber}/api/admin/revalidate`;
  try {
    const { POST } = await import("../app/api/shop-catalog/save/route.ts");
    const cookie = `${ADMIN_SESSION_COOKIE}=${token}`;
    const saved = await POST(
      new Request("http://127.0.0.1/api/shop-catalog/save", {
        method: "POST",
        headers: { cookie, "content-type": "application/json" },
        body: JSON.stringify({ ma: "S06", status: "available", priceUsd: 19 }),
      }),
    );
    assert.equal(saved.status, 400);
    const body = (await saved.json()) as { ok: boolean; error?: string; blobWritten?: boolean };
    assert.equal(body.ok, false);
    assert.equal(body.error, "S06 stays available at $25.");
    assert.equal(body.blobWritten, false);

    const held = await POST(
      new Request("http://127.0.0.1/api/shop-catalog/save", {
        method: "POST",
        headers: { cookie, "content-type": "application/json" },
        body: JSON.stringify({ ma: "S06", status: "hold" }),
      }),
    );
    assert.equal(held.status, 400);
    assert.equal(readFileSync(file, "utf8"), original);
    assert.equal(hits, 0);
  } finally {
    server.close();
    rmSync(dir, { recursive: true, force: true });
  }
});

test("revalidate URL must be the shop endpoint", () => {
  delete process.env.SHOP_BLOB_READ_WRITE_TOKEN;
  process.env.SHOP_REVALIDATE_SECRET = REVALIDATE_SECRET;
  process.env.SHOP_REVALIDATE_URL = "http://example.com/api/admin/revalidate";
  assert.equal(readShopRevalidateConfig().ok, false);
  process.env.SHOP_REVALIDATE_URL = "https://sassycloset.vercel.app/api/admin/save";
  assert.equal(readShopRevalidateConfig().ok, false);
  process.env.SHOP_REVALIDATE_URL = "https://sassycloset.vercel.app/api/admin/revalidate";
  assert.equal(readShopRevalidateConfig().ok, true);
});

test("signed-in catalog route reads a local file and does not require the intake blob token", async () => {
  delete process.env.SHOP_BLOB_READ_WRITE_TOKEN;
  delete process.env.BLOB_READ_WRITE_TOKEN;
  delete process.env.VERCEL;
  process.env.ADMIN_PASSWORD = PASSWORD;
  process.env.ADMIN_SESSION_SECRET = SESSION_SECRET;
  process.env.SHOP_REVALIDATE_SECRET = REVALIDATE_SECRET;
  const dir = mkdtempSync(path.join(tmpdir(), "shop-catalog-"));
  const file = path.join(dir, "catalog.v1.json");
  writeFileSync(file, `${JSON.stringify(sampleCatalog(), null, 2)}\n`);
  process.env.SHOP_CATALOG_FILE = file;
  const token = await createAdminSessionToken();
  assert.ok(token);
  const cookie = `${ADMIN_SESSION_COOKIE}=${token}`;
  try {
    const { GET } = await import("../app/api/shop-catalog/route.ts");
    const denied = await GET(new Request("http://127.0.0.1/api/shop-catalog"));
    assert.equal(denied.status, 401);
    const listed = await GET(new Request("http://127.0.0.1/api/shop-catalog", { headers: { cookie } }));
    assert.equal(listed.status, 200);
    const body = (await listed.json()) as { products: { ma: string }[] };
    assert.deepEqual(
      body.products.map((product) => product.ma),
      ["A01", "A03"],
    );

    let hits = 0;
    const server = createServer((request, response) => {
      hits += 1;
      assert.equal(request.headers[SHOP_REVALIDATE_HEADER], REVALIDATE_SECRET);
      response.writeHead(200);
      response.end('{"ok":true}');
    });
    const portNumber = await listen(server);
    process.env.SHOP_REVALIDATE_URL = `http://127.0.0.1:${portNumber}/api/admin/revalidate`;
    try {
      const { POST } = await import("../app/api/shop-catalog/save/route.ts");
      const saved = await POST(
        new Request("http://127.0.0.1/api/shop-catalog/save", {
          method: "POST",
          headers: { cookie, "content-type": "application/json" },
          body: JSON.stringify({ ma: "A03", titleEn: "Edited locally" }),
        }),
      );
      assert.equal(saved.status, 200);
      assert.equal(hits, 1);
      const onDisk = readFileSync(file, "utf8");
      assert.match(onDisk, /Edited locally/);
      assert.match(onDisk, /"priceUsd": 20/);
      const patch = applyShopCatalogPatch(sampleCatalog(), { ma: "A01", colors: [{ id: "new", name: "Mint" }] }, "t");
      assert.equal(patch.ok, false);
    } finally {
      server.close();
    }
  } finally {
    rmSync(dir, { recursive: true, force: true });
  }
});

test("intake tabs stay the four GF tabs and shop tools is a separate link", () => {
  const types = readFileSync(path.join(process.cwd(), "lib/types.ts"), "utf8");
  assert.match(types, /export type TabId = "create" \| "edit" \| "find" \| "ask"/);
  const intake = readFileSync(path.join(process.cwd(), "components/IntakeApp.tsx"), "utf8");
  assert.match(intake, /href="\/admin\/shop"/);
  assert.doesNotMatch(intake, /tab-shop/);
  const catalog = readFileSync(path.join(process.cwd(), "lib/shop-catalog.ts"), "utf8");
  assert.equal(catalog.includes("presentLockedBossPrices"), false);
  const store = readFileSync(path.join(process.cwd(), "lib/shop-catalog-store.ts"), "utf8");
  assert.match(store, /SHOP_BLOB_READ_WRITE_TOKEN/);
  assert.equal(store.includes("process.env.BLOB_READ_WRITE_TOKEN"), false);
  assert.match(store, /sassy-closet-shop\/catalog\.v1\.json/);
});
