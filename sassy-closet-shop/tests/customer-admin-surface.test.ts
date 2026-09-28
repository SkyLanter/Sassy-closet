import assert from "node:assert/strict";
import { readdirSync, readFileSync, statSync } from "node:fs";
import path from "node:path";
import test from "node:test";
import { NextRequest } from "next/server";
import { BOSS_PRICE_LIST } from "../lib/boss-catalog";
import { customerAdminApiClosed, customerAdminProxyDecision } from "../lib/customer-admin-closed";
import { SHOP_REVALIDATE_HEADER, revalidateSecretMatches } from "../lib/revalidate-secret";
import { proxy } from "../proxy";

const SECRET = "surface-test-secret";

function walk(dir: string, acc: string[]): void {
  for (const name of readdirSync(dir)) {
    const full = path.join(dir, name);
    if (statSync(full).isDirectory()) {
      walk(full, acc);
      continue;
    }
    if (/\.(tsx|ts)$/.test(name)) {
      acc.push(full);
    }
  }
}

test("customer shop sources do not mount Shop tools", () => {
  const files: string[] = [];
  walk(path.join(process.cwd(), "app/(shop)"), files);
  walk(path.join(process.cwd(), "components"), files);
  files.push(path.join(process.cwd(), "app/layout.tsx"));
  for (const file of files) {
    const base = path.basename(file);
    if (base === "admin-entry.tsx" || base.startsWith("admin-")) {
      continue;
    }
    const text = readFileSync(file, "utf8");
    assert.equal(text.includes("Shop tools"), false, file);
    assert.equal(text.includes("Công cụ shop"), false, file);
    assert.equal(text.includes("admin-entry"), false, file);
    assert.equal(text.includes("useAdminEntry"), false, file);
  }
  const layout = readFileSync(path.join(process.cwd(), "app/(shop)/layout.tsx"), "utf8");
  assert.equal(layout.includes("AdminEntry"), false);
  const header = readFileSync(path.join(process.cwd(), "components/header.tsx"), "utf8");
  assert.equal(header.includes("holdTimer"), false);
});

test("proxy returns 404 for admin pages and admin APIs except revalidate", () => {
  for (const pathname of [
    "/admin",
    "/admin/new",
    "/admin/edit/A01",
    "/admin/settings",
    "/admin/login",
    "/api/admin/catalog",
    "/api/admin/save",
    "/api/admin/add",
    "/api/admin/rename",
    "/api/admin/remove",
    "/api/admin/hold",
    "/api/admin/settings",
    "/api/admin/catalog/export",
    "/api/admin/catalog/import",
  ]) {
    const response = proxy(new NextRequest(`http://127.0.0.1${pathname}`));
    assert.equal(response.status, 404, pathname);
  }
  assert.equal(customerAdminProxyDecision("/api/admin/revalidate"), "continue");
  const revalidate = proxy(new NextRequest("http://127.0.0.1/api/admin/revalidate", { method: "POST" }));
  assert.notEqual(revalidate.status, 404);
  const home = proxy(new NextRequest("http://127.0.0.1/"));
  assert.notEqual(home.status, 404);
  const product = proxy(new NextRequest("http://127.0.0.1/m/A01"));
  assert.notEqual(product.status, 404);
});

test("shop admin API handlers return 404", async () => {
  const routes = [
    "../app/api/admin/save/route",
    "../app/api/admin/add/route",
    "../app/api/admin/catalog/route",
    "../app/api/admin/rename/route",
    "../app/api/admin/remove/route",
    "../app/api/admin/hold/route",
    "../app/api/admin/settings/route",
    "../app/api/admin/catalog/export/route",
    "../app/api/admin/catalog/import/route",
  ];
  for (const rel of routes) {
    const mod = (await import(rel)) as {
      GET?: () => Promise<Response>;
      POST?: (request: Request) => Promise<Response>;
    };
    if (mod.GET) {
      const response = await mod.GET();
      assert.equal(response.status, 404, `${rel} GET`);
    }
    if (mod.POST) {
      const response = await mod.POST(
        new Request("http://127.0.0.1", {
          method: "POST",
          headers: { "content-type": "application/json" },
          body: "{}",
        }),
      );
      assert.equal(response.status, 404, `${rel} POST`);
    }
  }
  assert.equal(customerAdminApiClosed()?.status, 404);
});

test("revalidate requires the shared secret header", async () => {
  const previous = process.env.SHOP_REVALIDATE_SECRET;
  process.env.SHOP_REVALIDATE_SECRET = SECRET;
  try {
    assert.equal(revalidateSecretMatches(null), false);
    assert.equal(revalidateSecretMatches(""), false);
    assert.equal(revalidateSecretMatches("nope"), false);
    assert.equal(revalidateSecretMatches(SECRET), true);
    const { GET, POST } = await import("../app/api/admin/revalidate/route");
    assert.equal((await GET()).status, 405);
    assert.equal(
      (
        await POST(new Request("http://127.0.0.1/api/admin/revalidate", { method: "POST" }))
      ).status,
      401,
    );
    assert.equal(
      (
        await POST(
          new Request("http://127.0.0.1/api/admin/revalidate", {
            method: "POST",
            headers: { [SHOP_REVALIDATE_HEADER]: "wrong" },
          }),
        )
      ).status,
      401,
    );
    process.env.SHOP_REVALIDATE_SECRET = SECRET;
    const accepted = await POST(
      new Request("http://127.0.0.1/api/admin/revalidate", {
        method: "POST",
        headers: { [SHOP_REVALIDATE_HEADER]: SECRET },
      }),
    );
    assert.equal(accepted.status, 200);
    const acceptedBody = (await accepted.json()) as { ok?: boolean; revalidated?: string[] };
    assert.equal(acceptedBody.ok, true);
    assert.ok(acceptedBody.revalidated?.includes("/"));
    assert.ok(acceptedBody.revalidated?.includes("/m/A01"));
    delete process.env.SHOP_REVALIDATE_SECRET;
    assert.equal(
      (
        await POST(
          new Request("http://127.0.0.1/api/admin/revalidate", {
            method: "POST",
            headers: { [SHOP_REVALIDATE_HEADER]: SECRET },
          }),
        )
      ).status,
      401,
    );
  } finally {
    if (previous === undefined) {
      delete process.env.SHOP_REVALIDATE_SECRET;
    } else {
      process.env.SHOP_REVALIDATE_SECRET = previous;
    }
  }
});

test("intake locked prices match BOSS_PRICE_LIST", () => {
  const text = readFileSync(path.join(process.cwd(), "../sassy-closet/lib/shop-catalog-lock.ts"), "utf8");
  for (const row of BOSS_PRICE_LIST) {
    assert.match(
      text,
      new RegExp(`\\{ ma: "${row.ma}", priceUsd: ${String(row.priceUsd)}, status: "${row.status}" \\}`),
    );
  }
});
