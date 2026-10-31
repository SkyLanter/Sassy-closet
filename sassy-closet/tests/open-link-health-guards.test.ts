import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import test from "node:test";
import { NextRequest } from "next/server";
import { HELD_INCOMPLETE_MAS } from "../lib/held-incomplete";
import { intakeHealthReport } from "../lib/intake-health";
import { isIntakePrivateSurface } from "../lib/intake-direct-link-headers";
import { publishBlock } from "../lib/publish-guard";
import { intakePriceView } from "../lib/pricing";
import { config as intakeMiddlewareConfig, middleware } from "../middleware";
import robots from "../app/robots";

const OPEN_ROUTES = [
  "app/api/submissions/route.ts",
  "app/api/submissions/[ma]/route.ts",
  "app/api/export/route.ts",
  "app/api/ma/[code]/route.ts",
  "app/api/health/route.ts",
  "app/admin/page.tsx",
  "app/admin/shop/page.tsx",
];

function walk(dir: string, acc: string[]): void {
  for (const name of fs.readdirSync(dir)) {
    const full = path.join(dir, name);
    if (fs.statSync(full).isDirectory()) {
      walk(full, acc);
      continue;
    }
    if (name.endsWith(".tsx") || name.endsWith(".ts")) {
      acc.push(full);
    }
  }
}

test("api and admin stay noindex and out of the sitemap and nav", () => {
  for (const pathname of [
    "/api/submissions",
    "/api/submissions/S06",
    "/api/export",
    "/api/ma/S06",
    "/api/health",
    "/admin",
    "/admin/shop",
  ]) {
    assert.equal(isIntakePrivateSurface(pathname), true, pathname);
  }
  assert.equal(isIntakePrivateSurface("/"), false);
  const rules = robots();
  const rule = Array.isArray(rules.rules) ? rules.rules[0] : rules.rules;
  const disallow = JSON.stringify(rule?.disallow ?? "");
  assert.match(disallow, /\/api/);
  assert.match(disallow, /\/admin/);
  assert.notEqual(rule?.disallow, "/");
  assert.equal(rules.sitemap, undefined);
  assert.equal(fs.existsSync(path.join(process.cwd(), "app/sitemap.ts")), false);
  const header = fs.readFileSync(path.join(process.cwd(), "components/BrandHeader.tsx"), "utf8");
  assert.equal(header.includes("/admin"), false);
  assert.equal(header.includes("/api/"), false);
});

test("open data routes have no password field and no 401", () => {
  for (const rel of OPEN_ROUTES) {
    const text = fs.readFileSync(path.join(process.cwd(), rel), "utf8");
    assert.equal(text.includes("401"), false, rel);
    assert.equal(/type\s*=\s*["']password["']/.test(text), false, rel);
  }
  const files: string[] = [];
  walk(path.join(process.cwd(), "app"), files);
  walk(path.join(process.cwd(), "components"), files);
  for (const file of files) {
    const text = fs.readFileSync(file, "utf8");
    assert.equal(/type\s*=\s*["']password["']/.test(text), false, file);
    assert.equal(/name\s*=\s*["']password["']/.test(text), false, file);
  }
  const desk = fs.readFileSync(path.join(process.cwd(), "docs/SHOP_ADMIN.md"), "utf8");
  assert.equal(desk.includes("## Password"), false);
  assert.match(desk, /Open by link/);
  const form = fs.readFileSync(path.join(process.cwd(), "components/IntakeApp.tsx"), "utf8");
  assert.match(form, /Giá bán \/ sell \(tuỳ chọn\)/);
  assert.match(form, /Giá bán không bắt buộc/);
  const sellAt = form.indexOf('data-testid="sell-usd"');
  assert.ok(sellAt > 0);
  assert.equal(form.slice(sellAt, sellAt + 500).includes("required"), false);
  const card = fs.readFileSync(path.join(process.cwd(), "lib/ma-card.ts"), "utf8");
  assert.match(card, /cost_cny: item\.cost_cny/);
  assert.match(card, /source_link: item\.link/);
});

test("S06 stays $25 for short and padded spellings, and a blank sell stays allowed", () => {
  for (const ma of ["S06", "S6", "s006", " S006 "]) {
    const view = intakePriceView({
      ma,
      kind: "S",
      sellUsd: "40",
      sellCny: "",
      sellCurrency: "USD",
      costCny: "",
      costUsd: "",
      costCurrency: "USD",
      fxRate: 1,
    });
    assert.equal(view.dollars, 25, ma);
    assert.equal(view.label, "$25", ma);
    assert.equal(publishBlock({ action: "update", ma, sellUsd: "40" }), "s06-lock", ma);
    assert.equal(publishBlock({ action: "update", ma, sellUsd: "" }), null, ma);
    assert.equal(publishBlock({ action: "update", ma, sellUsd: "25" }), null, ma);
  }
});

test("held spellings never publish", () => {
  const held = HELD_INCOMPLETE_MAS[0];
  assert.ok(held);
  const padded = `${held[0]}0${held.slice(1)}`;
  for (const ma of [held, padded, padded.toLowerCase()]) {
    assert.equal(publishBlock({ action: "create", ma, sellUsd: "25" }), "held", ma);
    assert.equal(publishBlock({ action: "sync", ma, sellUsd: "" }), "held", ma);
  }
});

test("middleware matcher covers every api and admin path", () => {
  assert.deepEqual(intakeMiddlewareConfig.matcher, ["/api/:path*", "/admin", "/admin/:path*"]);
});

test("middleware and health stay open and noindex without secrets", async () => {
  for (const pathname of ["/api/submissions", "/api/export", "/api/ma/S06", "/api/health", "/admin", "/admin/shop"]) {
    const response = middleware(new NextRequest(`http://127.0.0.1${pathname}`));
    assert.equal(response.status, 200, pathname);
    assert.match(response.headers.get("x-robots-tag") ?? "", /noindex,\s*nofollow,\s*nosnippet/i, pathname);
  }
  const home = middleware(new NextRequest("http://127.0.0.1/"));
  assert.equal(home.headers.get("x-robots-tag"), null);

  const saved: Record<string, string | undefined> = {};
  for (const key of Object.keys(process.env)) {
    if (/BLOB|KV_|VERCEL|TOKEN|SECRET|ADMIN_/i.test(key)) {
      saved[key] = process.env[key];
      delete process.env[key];
    }
  }
  const tmp = fs.mkdtempSync(path.join(os.tmpdir(), "intake-health-"));
  process.env.SASSY_DATA_DIR = tmp;
  const { resetStoreBackendForTests } = await import("../lib/store-backend");
  resetStoreBackendForTests();
  try {
    const report = intakeHealthReport();
    assert.equal(report.ok, true);
    assert.equal(report.reading, "local");
    assert.equal(report.blob.configured, false);
    assert.equal(JSON.stringify(report).includes("token"), false);

    const health = await import("../app/api/health/route");
    const healthResponse = health.GET();
    assert.equal(healthResponse.status, 200);
    assert.notEqual(healthResponse.status, 401);
    assert.match(healthResponse.headers.get("x-robots-tag") ?? "", /noindex,\s*nofollow,\s*nosnippet/i);
    const healthBody = (await healthResponse.json()) as { reading?: string; submissions?: unknown };
    assert.equal(healthBody.reading, "local");
    assert.equal("submissions" in healthBody, false);

    const submissions = await import("../app/api/submissions/route");
    const listed = await submissions.GET();
    assert.equal(listed.status, 200);
    assert.notEqual(listed.status, 401);
    assert.match(listed.headers.get("x-robots-tag") ?? "", /noindex/i);

    const exported = await import("../app/api/export/route");
    const csv = await exported.GET();
    assert.equal(csv.status, 200);
    assert.notEqual(csv.status, 401);

    const ma = await import("../app/api/ma/[code]/route");
    const missing = await ma.GET(new Request("http://127.0.0.1/api/ma/S06"), {
      params: Promise.resolve({ code: "S06" }),
    });
    assert.equal(missing.status, 404);
    assert.notEqual(missing.status, 401);
    assert.match(missing.headers.get("x-robots-tag") ?? "", /noindex/i);
  } finally {
    for (const [key, value] of Object.entries(saved)) {
      if (value === undefined) {
        delete process.env[key];
      } else {
        process.env[key] = value;
      }
    }
    delete process.env.SASSY_DATA_DIR;
    resetStoreBackendForTests();
    fs.rmSync(tmp, { recursive: true, force: true });
  }
});
