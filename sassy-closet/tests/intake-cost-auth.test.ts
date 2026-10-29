import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { afterEach, beforeEach, describe, test } from "node:test";
import { NextRequest } from "next/server";
import { GET as exportGet } from "../app/api/export/route";
import { GET as cardGet } from "../app/api/ma/[code]/route";
import { GET as readGet, PATCH as patchMa } from "../app/api/submissions/[ma]/route";
import { GET as listGet, POST as createPost } from "../app/api/submissions/route";
import { ADMIN_SESSION_COOKIE, createAdminSessionToken } from "../lib/admin-auth";
import { intakeCatalog } from "../lib/kinds";
import { lookupMaCard } from "../lib/ma-card";
import { isIntakeCostReadApi, shopAdminGate } from "../lib/shop-admin-gate";
import { exportCsv, getSubmission, listSubmissions, saveSubmission, storeHealth } from "../lib/store";
import { resetStoreBackendForTests } from "../lib/store-backend";
import type { Submission } from "../lib/types";
import { config as middlewareConfig, middleware } from "../middleware";

const PASSWORD = "intake-shop-tools-test";
const SESSION_SECRET = "intake-shop-session-test";

const ENV_KEYS = [
  "ADMIN_PASSWORD",
  "ADMIN_SESSION_SECRET",
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

const yuan = ["3", "3", ".", "3"].join("");
const dollars = ["4", ".", "5", "0"].join("");
const sourceLink = ["https://", ["shop", "example", "test"].join("."), "/item/", ["6", "6"].join("")].join("");
const COST_MARKERS = [yuan, dollars, sourceLink, "cost_cny", "cost_usd", "source_link"];

const previous: Partial<Record<(typeof ENV_KEYS)[number], string | undefined>> = {};
for (const key of ENV_KEYS) {
  previous[key] = process.env[key];
}

describe("intake cost reads require the shop admin cookie", { concurrency: 1 }, () => {
  let tmp = "";
  let token = "";
  let saved: Submission;

  beforeEach(async () => {
    tmp = fs.mkdtempSync(path.join(os.tmpdir(), "sassy-cost-auth-"));
    for (const key of ENV_KEYS) {
      delete process.env[key];
    }
    process.env.SASSY_DATA_DIR = tmp;
    process.env.ADMIN_PASSWORD = PASSWORD;
    process.env.ADMIN_SESSION_SECRET = SESSION_SECRET;
    resetStoreBackendForTests();
    const issued = await createAdminSessionToken();
    assert.ok(issued);
    token = issued;
    saved = await saveSubmission({
      kind: "A",
      size: "M",
      link: sourceLink,
      color: "Kem",
      color_note: "",
      pieces: [],
      cost_usd: dollars,
      cost_cny: yuan,
      cost_currency: "USD",
      sell_usd: "",
      sell_cny: "",
      sell_currency: "USD",
      keep_photos: [],
      photos: [],
      needs_research: false,
      taobao_snapshot: null,
      auto_price: null,
    });
  });

  afterEach(() => {
    for (const key of ENV_KEYS) {
      const value = previous[key];
      if (value === undefined) delete process.env[key];
      else process.env[key] = value;
    }
    resetStoreBackendForTests();
    fs.rmSync(tmp, { recursive: true, force: true });
  });

  test("gate list locks cost GETs and leaves submission writes public", () => {
    assert.equal(isIntakeCostReadApi("/api/export"), true);
    assert.equal(isIntakeCostReadApi("/api/submissions"), true);
    assert.equal(isIntakeCostReadApi("/api/submissions/A01"), true);
    assert.equal(isIntakeCostReadApi("/api/ma/A01"), true);
    assert.equal(isIntakeCostReadApi("/api/ma"), false);
    assert.equal(isIntakeCostReadApi("/api/find-ma"), false);
    assert.equal(isIntakeCostReadApi("/api/listing-status"), false);
    assert.equal(isIntakeCostReadApi("/api/shop-catalog"), false);
    assert.equal(shopAdminGate("/api/export", false), "deny");
    assert.equal(shopAdminGate("/api/export", true), "allow");
    assert.equal(shopAdminGate("/api/submissions", false, "GET"), "deny");
    assert.equal(shopAdminGate("/api/submissions", false, "POST"), "public");
    assert.equal(shopAdminGate("/api/submissions/A01", false, "PATCH"), "public");
    assert.equal(shopAdminGate("/api/ma/A01", false, "GET"), "deny");
    assert.equal(shopAdminGate("/api/ma/A01", true, "GET"), "allow");
    assert.equal(shopAdminGate("/admin", false), "public");
    assert.equal(shopAdminGate("/", false), "public");
    const matchers = [...middlewareConfig.matcher];
    assert.ok(matchers.includes("/api/export"));
    assert.ok(matchers.includes("/api/submissions"));
    assert.ok(matchers.includes("/api/submissions/:path*"));
    assert.ok(matchers.includes("/api/ma/:path*"));
  });

  test("unsigned GETs are 401 and omit cost and source fields", async () => {
    const requests = [
      exportGet(open("http://127.0.0.1/api/export")),
      exportGet(new Request("http://127.0.0.1/api/export", { headers: { cookie: `${ADMIN_SESSION_COOKIE}=nope` } })),
      listGet(open("http://127.0.0.1/api/submissions")),
      readGet(open(`http://127.0.0.1/api/submissions/${saved.ma}`), { params: Promise.resolve({ ma: saved.ma }) }),
      cardGet(open(`http://127.0.0.1/api/ma/${saved.ma}`), { params: Promise.resolve({ code: saved.ma }) }),
      cardGet(open("http://127.0.0.1/api/ma/Z99"), { params: Promise.resolve({ code: "Z99" }) }),
    ];
    for (const pending of requests) {
      await assertClosed(await pending);
    }

    delete process.env.ADMIN_PASSWORD;
    delete process.env.ADMIN_SESSION_SECRET;
    await assertClosed(await exportGet(withSession("http://127.0.0.1/api/export")));
  });

  test("signed GETs keep today's response shape, including cost and source fields", async () => {
    const csvResponse = await exportGet(withSession("http://127.0.0.1/api/export"));
    assert.equal(csvResponse.status, 200);
    assert.match(csvResponse.headers.get("content-type") ?? "", /text\/csv/);
    const csv = await csvResponse.text();
    assert.equal(csv, await exportCsv());
    assert.match(csv, /^ma,/);
    assert.match(csv, /cost_cny/);
    assert.match(csv, /cost_usd/);
    assert.match(csv, /source_link/);
    assert.ok(csv.includes(yuan));
    assert.ok(csv.includes(dollars));
    assert.ok(csv.includes(sourceLink));

    const listedResponse = await listGet(withSession("http://127.0.0.1/api/submissions"));
    assert.equal(listedResponse.status, 200);
    const listed = (await listedResponse.json()) as {
      submissions: Submission[];
      storage: ReturnType<typeof storeHealth>;
      catalog: ReturnType<typeof intakeCatalog>;
    };
    assert.deepEqual(listed, {
      submissions: await listSubmissions(),
      storage: storeHealth(),
      catalog: intakeCatalog(),
    });
    assert.equal(listed.submissions[0]?.ma, saved.ma);
    assert.equal(listed.submissions[0]?.cost_cny, yuan);
    assert.equal(listed.submissions[0]?.cost_usd, dollars);
    assert.equal(listed.submissions[0]?.link, sourceLink);

    const readResponse = await readGet(withSession(`http://127.0.0.1/api/submissions/${saved.ma}`), {
      params: Promise.resolve({ ma: saved.ma.toLowerCase() }),
    });
    assert.equal(readResponse.status, 200);
    const read = (await readResponse.json()) as { ma: string; caption_vi: string; submission: Submission };
    const stored = await getSubmission(saved.ma);
    assert.ok(stored);
    assert.deepEqual(read, {
      ma: stored.ma,
      caption_vi: stored.caption_vi,
      submission: stored,
    });
    assert.equal(read.submission.cost_cny, yuan);
    assert.equal(read.submission.link, sourceLink);

    const cardResponse = await cardGet(withSession(`http://127.0.0.1/api/ma/${saved.ma}`), {
      params: Promise.resolve({ code: saved.ma }),
    });
    assert.equal(cardResponse.status, 200);
    const card = (await cardResponse.json()) as {
      code: string;
      staged: { cost_cny: string; cost_usd: string; source_link: string };
      on_hand: unknown[];
      staged_only: boolean;
    };
    const lookedUp = await lookupMaCard(saved.ma);
    assert.ok(lookedUp);
    assert.deepEqual(card, {
      code: lookedUp.code,
      staged: lookedUp.staged,
      on_hand: lookedUp.on_hand,
      staged_only: lookedUp.staged_only,
    });
    assert.equal(card.staged.cost_cny, yuan);
    assert.equal(card.staged.cost_usd, dollars);
    assert.equal(card.staged.source_link, sourceLink);

    const missing = await readGet(withSession("http://127.0.0.1/api/submissions/Z99"), {
      params: Promise.resolve({ ma: "Z99" }),
    });
    assert.equal(missing.status, 404);
    const missingCard = await cardGet(withSession("http://127.0.0.1/api/ma/Z99"), {
      params: Promise.resolve({ code: "Z99" }),
    });
    assert.equal(missingCard.status, 404);
  });

  test("POST and PATCH still save without the admin cookie", async () => {
    const createdResponse = await createPost(formRequest("POST", "/api/submissions", {}));
    assert.equal(createdResponse.status, 200);
    const created = (await createdResponse.json()) as { submission: { ma: string } };
    assert.equal(created.submission.ma, "A02");

    const patchedResponse = await patchMa(formRequest("PATCH", `/api/submissions/${saved.ma}`, { color: "Xanh" }), {
      params: Promise.resolve({ ma: saved.ma }),
    });
    assert.equal(patchedResponse.status, 200);
    const patched = (await patchedResponse.json()) as { submission: { ma: string; color: string } };
    assert.equal(patched.submission.ma, saved.ma);
    assert.equal(patched.submission.color, "Xanh");
    assert.equal((await getSubmission(saved.ma))?.color, "Xanh");
  });

  test("middleware returns 401 for unsigned cost GETs and lets writes through", async () => {
    const denied = await middleware(new NextRequest("http://127.0.0.1/api/export"));
    await assertClosed(denied);
    const listDenied = await middleware(new NextRequest("http://127.0.0.1/api/submissions"));
    await assertClosed(listDenied);
    const readDenied = await middleware(new NextRequest(`http://127.0.0.1/api/submissions/${saved.ma}`));
    await assertClosed(readDenied);
    const cardDenied = await middleware(new NextRequest(`http://127.0.0.1/api/ma/${saved.ma}`));
    await assertClosed(cardDenied);

    const signed = await middleware(
      new NextRequest("http://127.0.0.1/api/export", { headers: { cookie: `${ADMIN_SESSION_COOKIE}=${token}` } }),
    );
    assert.equal(signed.status, 200);
    const post = await middleware(new NextRequest("http://127.0.0.1/api/submissions", { method: "POST" }));
    assert.equal(post.status, 200);
    const patch = await middleware(
      new NextRequest(`http://127.0.0.1/api/submissions/${saved.ma}`, { method: "PATCH" }),
    );
    assert.equal(patch.status, 200);
    const page = await middleware(new NextRequest("http://127.0.0.1/admin"));
    assert.equal(page.status, 200);
  });

  function withSession(url: string): Request {
    return new Request(url, { headers: { cookie: `${ADMIN_SESSION_COOKIE}=${token}` } });
  }
});

function open(url: string): Request {
  return new Request(url);
}

async function assertClosed(response: Response): Promise<void> {
  assert.equal(response.status, 401);
  const text = await response.text();
  assert.deepEqual(JSON.parse(text), { ok: false, error: "Unauthorized." });
  for (const marker of COST_MARKERS) {
    assert.equal(text.includes(marker), false, marker);
  }
}

function formRequest(method: "POST" | "PATCH", pathname: string, fields: Record<string, string>): Request {
  const form = new FormData();
  form.set("kind", "A");
  form.set("size", "M");
  form.set("color", "Kem");
  form.set("color_note", "");
  form.set("link", "");
  form.set("pieces", "[]");
  form.set("keep_photos", "[]");
  for (const [key, value] of Object.entries(fields)) form.set(key, value);
  return new Request(`http://127.0.0.1${pathname}`, { method, body: form });
}
