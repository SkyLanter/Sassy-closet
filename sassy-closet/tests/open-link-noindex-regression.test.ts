import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import test from "node:test";
import { NextRequest } from "next/server";
import { metadata as adminMetadata } from "../app/admin/layout";
import { metadata as shopToolsMetadata } from "../app/admin/shop/layout";
import { GET as exportGet } from "../app/api/export/route";
import { GET as maGet } from "../app/api/ma/[code]/route";
import { GET as oneGet, PATCH as onePatch } from "../app/api/submissions/[ma]/route";
import { GET as listGet, POST as listPost } from "../app/api/submissions/route";
import { INTAKE_LISTING_ROBOTS, isIntakePrivateSurface } from "../lib/intake-direct-link-headers";
import { resetStoreBackendForTests } from "../lib/store-backend";
import { config as intakeMiddlewareConfig, middleware } from "../middleware";

const ROBOTS = "noindex, nofollow, nosnippet";

const OPEN_PATHS = [
  "/api/submissions",
  "/api/submissions/S06",
  "/api/export",
  "/api/ma/S06",
  "/api/ma/A01",
  "/admin",
  "/admin/shop",
];

/**
 * Next matcher `:path*` is zero or more segments, so `/admin/:path*` covers `/admin`.
 * An exact pattern covers only that path.
 */
function matcherCovers(pattern: string, pathname: string): boolean {
  if (pattern.endsWith("/:path*")) {
    const prefix = pattern.slice(0, -"/:path*".length);
    return pathname === prefix || pathname.startsWith(`${prefix}/`);
  }
  return pathname === pattern;
}

function assertOpen(res: Response, name: string, status: number) {
  assert.equal(res.status, status, name);
  assert.notEqual(res.status, 401, name);
  assert.equal(res.headers.get("x-robots-tag"), ROBOTS, name);
  assert.match(res.headers.get("cache-control") ?? "", /no-store/, name);
  assert.equal(res.headers.get("set-cookie"), null, name);
}

function formBody(): FormData {
  const body = new FormData();
  body.set("kind", "A");
  body.set("size", "M");
  return body;
}

test("admin HTML noindex does not depend on the public form layout", () => {
  assert.deepEqual(adminMetadata.robots, INTAKE_LISTING_ROBOTS);
  assert.deepEqual(shopToolsMetadata.robots, INTAKE_LISTING_ROBOTS);
  assert.equal(shopToolsMetadata.title, "Shop tools");
  const root = fs.readFileSync(path.join(process.cwd(), "app/layout.tsx"), "utf8");
  const admin = fs.readFileSync(path.join(process.cwd(), "app/admin/layout.tsx"), "utf8");
  assert.equal(root.includes("INTAKE_LISTING_ROBOTS"), true);
  assert.equal(admin.includes("INTAKE_LISTING_ROBOTS"), true);
  assert.equal(admin.includes('type="password"'), false);
});

test("middleware matcher covers submissions, export, ma, and admin only", () => {
  const patterns = intakeMiddlewareConfig.matcher;
  assert.ok(Array.isArray(patterns));
  for (const pathname of OPEN_PATHS) {
    assert.equal(isIntakePrivateSurface(pathname), true, pathname);
    assert.equal(
      patterns.some((pattern) => matcherCovers(pattern, pathname)),
      true,
      pathname,
    );
    const response = middleware(new NextRequest(`http://127.0.0.1${pathname}`));
    assert.equal(response.status, 200, pathname);
    assert.equal(response.headers.get("x-robots-tag"), ROBOTS, pathname);
  }
  for (const pathname of ["/", "/m/S06"]) {
    assert.equal(isIntakePrivateSurface(pathname), false, pathname);
    assert.equal(
      patterns.some((pattern) => matcherCovers(pattern, pathname)),
      false,
      pathname,
    );
    const response = middleware(new NextRequest(`http://127.0.0.1${pathname}`));
    assert.equal(response.headers.get("x-robots-tag"), null, pathname);
  }
});

test("submission, export, and ma handlers stay open and fully noindex", async () => {
  const tmp = fs.mkdtempSync(path.join(os.tmpdir(), "intake-open-link-"));
  const saved = { ...process.env };
  for (const key of Object.keys(process.env)) {
    if (/BLOB|KV_|VERCEL|ADMIN_/.test(key)) delete process.env[key];
  }
  process.env.SASSY_DATA_DIR = tmp;
  resetStoreBackendForTests();
  try {
    const posted = await listPost(
      new Request("http://127.0.0.1/api/submissions", { method: "POST", body: formBody() }),
    );
    assertOpen(posted, "POST /api/submissions", 200);
    const created = (await posted.json()) as { submission?: { ma?: string } };
    const ma = created.submission?.ma ?? "";
    assert.equal(ma, "A01");

    const patched = await onePatch(
      new Request("http://127.0.0.1/api/submissions/A01", { method: "PATCH", body: formBody() }),
      { params: Promise.resolve({ ma }) },
    );
    assertOpen(patched, "PATCH /api/submissions/A01", 200);

    const listed = await listGet();
    assertOpen(listed, "GET /api/submissions", 200);

    const one = await oneGet(new Request("http://127.0.0.1/api/submissions/A01"), {
      params: Promise.resolve({ ma: "a1" }),
    });
    assertOpen(one, "GET /api/submissions/a1", 200);

    const missingRow = await oneGet(new Request("http://127.0.0.1/api/submissions/S06"), {
      params: Promise.resolve({ ma: "S06" }),
    });
    assertOpen(missingRow, "GET /api/submissions/S06", 404);

    const exported = await exportGet();
    assertOpen(exported, "GET /api/export", 200);
    assert.match(exported.headers.get("content-type") ?? "", /text\/csv/);

    const card = await maGet(new Request("http://127.0.0.1/api/ma/A01"), {
      params: Promise.resolve({ code: "A01" }),
    });
    assertOpen(card, "GET /api/ma/A01", 200);

    const missingCard = await maGet(new Request("http://127.0.0.1/api/ma/S06"), {
      params: Promise.resolve({ code: "S06" }),
    });
    assertOpen(missingCard, "GET /api/ma/S06", 404);

    for (const code of ["%", "A0%"]) {
      const malformed = await maGet(new Request("http://127.0.0.1/api/ma/x"), {
        params: Promise.resolve({ code }),
      });
      assertOpen(malformed, `GET /api/ma/${code}`, 404);
    }
  } finally {
    process.env = saved;
    resetStoreBackendForTests();
    fs.rmSync(tmp, { recursive: true, force: true });
  }
});
