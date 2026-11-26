import assert from "node:assert/strict";
import { existsSync, readFileSync } from "node:fs";
import path from "node:path";
import test from "node:test";
import { NextRequest } from "next/server";
import { isSeedAssetPath } from "../lib/customer-seed-closed";
import { proxy } from "../proxy";

const SEED_REL = path.join("public", "data", "taobao_confirm_seed.json");
const ROBOTS_HEADER = /noindex,\s*nofollow,\s*nosnippet/i;

/**
 * `public/data/taobao_confirm_seed.json` ships in `public/`, so Next served it as
 * a 200 for anyone who asked. It is the Taobao supplier seed (links, shops, CNY
 * supplier prices), and customer HTML strips `sourceLink` precisely because that
 * data is not for shoppers. The shop has no `/data` route, so the prefix must 404.
 */
test("the shop does not serve the supplier seed under /data", async () => {
  const seedPath = path.join(process.cwd(), SEED_REL);
  assert.equal(existsSync(seedPath), true, "the seed file is still the repo fixture");
  const seed = JSON.parse(readFileSync(seedPath, "utf8")) as { items?: unknown[] };
  assert.ok((seed.items?.length ?? 0) > 0, "the seed really holds supplier rows");

  const response = proxy(new NextRequest("http://127.0.0.1/data/taobao_confirm_seed.json"));
  assert.equal(response.status, 404);
  assert.match(response.headers.get("x-robots-tag") ?? "", ROBOTS_HEADER);
  assert.match(response.headers.get("cache-control") ?? "", /no-store/);
  assert.equal(await response.text(), "Not found");
});

test("every spelling of the seed folder is closed", () => {
  for (const pathname of [
    "/data",
    "/data/",
    "/data/taobao_confirm_seed.json",
    "/data/taobao_confirm_seed.json?x=1",
    "/%64ata/taobao_confirm_seed.json",
    "/DATA/taobao_confirm_seed.json",
    "/data/./taobao_confirm_seed.json",
    "/data//taobao_confirm_seed.json",
    "/x/../data/taobao_confirm_seed.json",
  ]) {
    assert.equal(isSeedAssetPath(pathname), true, pathname);
    assert.equal(
      proxy(new NextRequest(new URL(pathname, "http://127.0.0.1"))).status,
      404,
      pathname,
    );
  }
});

test("the lookbook and other public files still load", () => {
  for (const pathname of ["/", "/m/A01", "/c/ao", "/sitemap.xml", "/robots.txt"]) {
    assert.equal(isSeedAssetPath(pathname), false, pathname);
    assert.notEqual(
      proxy(new NextRequest(`http://127.0.0.1${pathname}`)).status,
      404,
      pathname,
    );
  }
  assert.equal(isSeedAssetPath("/database/thing.json"), false);
  assert.equal(isSeedAssetPath("/datax"), false);
});
