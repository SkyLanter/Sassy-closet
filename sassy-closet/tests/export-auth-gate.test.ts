import assert from "node:assert/strict";
import { randomBytes } from "node:crypto";
import { mkdtempSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import path from "node:path";
import { afterEach, test } from "node:test";
import { NextRequest } from "next/server";
import { GET as getExport } from "../app/api/export/route";
import { GET as getKinds } from "../app/api/kinds/route";
import { GET as getListingStatus } from "../app/api/listing-status/route";
import { GET as getMa } from "../app/api/ma/[code]/route";
import { GET as getShopCatalog } from "../app/api/shop-catalog/route";
import { GET as getSubmission } from "../app/api/submissions/[ma]/route";
import { GET as getSubmissions } from "../app/api/submissions/route";
import { ADMIN_SESSION_COOKIE, createAdminSessionToken } from "../lib/admin-auth";
import { shopAdminGate } from "../lib/shop-admin-gate";
import { listShopCatalog } from "../lib/shop-catalog";
import { resetStoreBackendForTests } from "../lib/store-backend";
import { saveSubmission } from "../lib/store";
import { middleware } from "../middleware";

const PASSWORD = "intake-export-gate-test";
const SESSION_SECRET = "intake-export-session-test";

const COST_FIELD_NAMES = ["cost_cny", "cost_usd", "source_link", "sourceLink"] as const;

const ENV_KEYS = [
  "ADMIN_PASSWORD",
  "ADMIN_SESSION_SECRET",
  "BLOB_ACCESS",
  "BLOB_READ_WRITE_TOKEN",
  "BLOB_STORE_ID",
  "INTAKE_DATASET_SYNC_WEBHOOK_KEY",
  "INTAKE_DATASET_SYNC_WEBHOOK_URL",
  "LISTING_STATUS_URL",
  "SASSY_DATA_DIR",
  "SHOP_BLOB_READ_WRITE_TOKEN",
  "SHOP_CATALOG_FILE",
  "VERCEL",
] as const;

const previous: Partial<Record<(typeof ENV_KEYS)[number], string | undefined>> = {};
for (const key of ENV_KEYS) {
  previous[key] = process.env[key];
}

let tempDir = "";

afterEach(() => {
  resetStoreBackendForTests();
  if (tempDir) {
    rmSync(tempDir, { recursive: true, force: true });
    tempDir = "";
  }
  for (const key of ENV_KEYS) {
    const value = previous[key];
    if (value === undefined) {
      delete process.env[key];
    } else {
      process.env[key] = value;
    }
  }
});

function isolateStore(): void {
  for (const key of ENV_KEYS) {
    delete process.env[key];
  }
  tempDir = mkdtempSync(path.join(tmpdir(), "export-auth-gate-"));
  process.env.SASSY_DATA_DIR = tempDir;
  resetStoreBackendForTests();
}

function leakedCost(text: string, secrets: readonly string[]): string | null {
  for (const name of COST_FIELD_NAMES) {
    if (text.includes(name)) {
      return name;
    }
  }
  for (const secret of secrets) {
    if (secret.length > 0 && text.includes(secret)) {
      return "seed";
    }
  }
  return null;
}

function assertIncludes(text: string, needle: string, label: string): void {
  assert.equal(text.includes(needle), true, label);
}

async function readText(response: Response): Promise<string> {
  return response.text();
}

test("unauthenticated cost reads are refused and a shop session can still read them", async () => {
  isolateStore();
  const token = randomBytes(8).toString("hex");
  const costUsd = `u${token}`;
  const costCny = `c${token}`;
  const sourceLink = `https://example.test/ref-${token}`;
  const secrets = [costUsd, costCny, sourceLink];

  const saved = await saveSubmission({
    kind: "P",
    size: "M",
    link: sourceLink,
    color: "Kem",
    color_note: "",
    pieces: [],
    cost_usd: costUsd,
    cost_cny: costCny,
    cost_currency: "USD",
    sell_usd: "28",
    sell_cny: "",
    sell_currency: "USD",
    keep_photos: [],
    photos: [],
    needs_research: false,
    taobao_snapshot: null,
    auto_price: null,
  });

  const maParams = { params: Promise.resolve({ ma: saved.ma }) };
  const codeParams = { params: Promise.resolve({ code: saved.ma }) };
  const anonReads = [
    getExport(new Request("http://127.0.0.1/api/export")),
    getSubmissions(new Request("http://127.0.0.1/api/submissions")),
    getSubmission(new Request(`http://127.0.0.1/api/submissions/${saved.ma}`), maParams),
    getMa(new Request(`http://127.0.0.1/api/ma/${saved.ma}`), codeParams),
  ];
  for (const pending of anonReads) {
    const response = await pending;
    const text = await readText(response);
    assert.equal(response.status, 401);
    assert.equal(leakedCost(text, secrets), null);
    assert.match(response.headers.get("cache-control") ?? "", /no-store/);
    const body = JSON.parse(text) as { ok?: boolean; error?: string };
    assert.equal(body.ok, false);
    assert.equal(body.error, "Unauthorized.");
  }

  delete process.env.ADMIN_PASSWORD;
  delete process.env.ADMIN_SESSION_SECRET;
  const locked = await getExport(new Request("http://127.0.0.1/api/export"));
  assert.equal(locked.status, 401);
  assert.equal(leakedCost(await readText(locked), secrets), null);

  process.env.ADMIN_PASSWORD = PASSWORD;
  process.env.ADMIN_SESSION_SECRET = SESSION_SECRET;
  const session = await createAdminSessionToken();
  assert.ok(session);
  const headers = { cookie: `${ADMIN_SESSION_COOKIE}=${session}` };
  const csv = await getExport(new Request("http://127.0.0.1/api/export", { headers }));
  const csvText = await readText(csv);
  assert.equal(csv.status, 200);
  for (const name of ["cost_cny", "cost_usd", "source_link"] as const) {
    assertIncludes(csvText, name, name);
  }
  for (const secret of secrets) {
    assertIncludes(csvText, secret, "admin export");
  }

  const listed = await getSubmissions(new Request("http://127.0.0.1/api/submissions", { headers }));
  const listedText = await readText(listed);
  assert.equal(listed.status, 200);
  assertIncludes(listedText, "cost_cny", "cost_cny");
  assertIncludes(listedText, "cost_usd", "cost_usd");
  assertIncludes(listedText, costUsd, "admin list");
  assertIncludes(listedText, costCny, "admin list");
  assertIncludes(listedText, sourceLink, "admin list");

  const one = await getSubmission(
    new Request(`http://127.0.0.1/api/submissions/${saved.ma}`, { headers }),
    maParams,
  );
  const oneText = await readText(one);
  assert.equal(one.status, 200);
  assertIncludes(oneText, "cost_cny", "cost_cny");
  assertIncludes(oneText, "cost_usd", "cost_usd");
  assertIncludes(oneText, costUsd, "admin submission");
  assertIncludes(oneText, costCny, "admin submission");
  assertIncludes(oneText, sourceLink, "admin submission");

  const card = await getMa(new Request(`http://127.0.0.1/api/ma/${saved.ma}`, { headers }), codeParams);
  const cardText = await readText(card);
  assert.equal(card.status, 200);
  assertIncludes(cardText, "cost_cny", "cost_cny");
  assertIncludes(cardText, "cost_usd", "cost_usd");
  assertIncludes(cardText, "source_link", "source_link");
  for (const secret of secrets) {
    assertIncludes(cardText, secret, "admin card");
  }

  const missing = await getMa(new Request("http://127.0.0.1/api/ma/P99", { headers }), {
    params: Promise.resolve({ code: "P99" }),
  });
  const missingText = await readText(missing);
  assert.equal(missing.status, 404);
  assert.equal(leakedCost(missingText, secrets), null);

  const anonymousMissing = await getSubmission(new Request("http://127.0.0.1/api/submissions/P99"), {
    params: Promise.resolve({ ma: "P99" }),
  });
  assert.equal(anonymousMissing.status, 401);
  assert.equal(leakedCost(await readText(anonymousMissing), secrets), null);
});

test("public shop and intake reads of non-sensitive fields stay open", async () => {
  isolateStore();
  delete process.env.LISTING_STATUS_URL;
  const kinds = await getKinds();
  const kindsText = await readText(kinds);
  assert.equal(kinds.status, 200);
  assert.equal(leakedCost(kindsText, []), null);
  assert.match(kindsText, /"catalog"/);

  const listing = await getListingStatus();
  const listingText = await readText(listing);
  assert.equal(listing.status, 200);
  assert.equal(leakedCost(listingText, []), null);
  const listingBody = JSON.parse(listingText) as { enabled?: boolean };
  assert.equal(listingBody.enabled, false);

  const shop = await getShopCatalog(new Request("http://127.0.0.1/api/shop-catalog"));
  assert.equal(shop.status, 401);
  assert.equal(leakedCost(await readText(shop), []), null);

  const hiddenSupplier = `https://example.test/catalog-${randomBytes(4).toString("hex")}`;
  const listed = listShopCatalog({
    schema: "catalog.v1",
    version: 1,
    siteId: "sassy-closet-shop",
    products: [
      {
        ma: "P01",
        titleVn: "Túi",
        titleEn: "Bag",
        priceUsd: 28,
        status: "available",
        colors: [{ id: "cp0100", name: "Kem" }],
        sourceLink: hiddenSupplier,
      },
    ],
  });
  assert.equal(listed.ok, true);
  if (listed.ok) {
    const row = listed.products[0];
    assert.equal(row?.ma, "P01");
    assert.equal(row?.priceUsd, 28);
    assert.equal("sourceLink" in (row ?? {}), false);
    assert.equal(leakedCost(JSON.stringify(listed.products), [hiddenSupplier]), null);
  }

  assert.equal(shopAdminGate("/api/export", false), "public");
  assert.equal(shopAdminGate("/api/submissions", false), "public");
  assert.equal(shopAdminGate("/api/ma/P01", false), "public");
  assert.equal(shopAdminGate("/", false), "public");
  assert.equal(shopAdminGate("/api/shop-catalog", false), "deny");

  process.env.ADMIN_PASSWORD = PASSWORD;
  process.env.ADMIN_SESSION_SECRET = SESSION_SECRET;
  const passed = await middleware(new NextRequest("http://127.0.0.1/api/kinds"));
  assert.equal(passed.status, 200);
  const shopDenied = await middleware(new NextRequest("http://127.0.0.1/api/shop-catalog"));
  assert.equal(shopDenied.status, 401);
});
