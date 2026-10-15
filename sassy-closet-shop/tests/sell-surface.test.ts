import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import path from "node:path";
import test from "node:test";
import { breadcrumbJsonLd, homeCatalogJsonLd, websiteJsonLd } from "../lib/seo";
import type { ShopLook } from "../lib/shop-look";

const root = process.cwd();

function read(relative: string): string {
  return readFileSync(path.join(root, relative), "utf8");
}

test("viewport stays device-width and the blush theme, without unused font weights", () => {
  const layout = read("app/layout.tsx");
  assert.match(layout, /width: "device-width"/);
  assert.match(layout, /initialScale: 1/);
  assert.match(layout, /themeColor: "#fdece6"/);
  assert.equal(layout.includes('"300"'), false);
  assert.equal(layout.includes('"700"'), false);
});

test("shop type floor and phone name lead stay in the stylesheet", () => {
  const css = read("app/globals.css");
  assert.match(css, /\.text-\\\[11px\\\]/);
  assert.match(css, /font-size: 0\.75rem/);
  assert.match(css, /\.ky-scroll-more/);
  assert.match(css, /\.ky-chip-rail > \.ky-scroll-more/);
  assert.match(read("components/color-name-chips.tsx"), /ky-chip-rail/);
  assert.match(css, /\.ky-pdp-media \.ky-gallery-frame/);
  const look = read("components/product-look.tsx");
  assert.match(look, /ky-pdp-lead/);
  assert.match(look, /aria-label="Breadcrumb"/);
  assert.match(look, /aria-current="page"/);
});

test("search and breadcrumb markup do not invent a price", () => {
  const previous = process.env.NEXT_PUBLIC_SHOP_URL;
  process.env.NEXT_PUBLIC_SHOP_URL = "https://shop.example";
  try {
    const site = websiteJsonLd();
    const siteJson = JSON.stringify(site);
    assert.equal(site["@type"], "WebSite");
    assert.match(siteJson, /search_term_string/);
    assert.equal(siteJson.includes("$"), false);
    assert.equal(siteJson.includes("price"), false);

    const crumbs = breadcrumbJsonLd([
      { name: "Sassy Closet", path: "/" },
      { name: "Sets", path: "/c/set" },
      { name: "S06", path: "/m/S06" },
    ]);
    const crumbJson = JSON.stringify(crumbs);
    assert.match(crumbJson, /BreadcrumbList/);
    assert.match(crumbJson, /https:\/\/shop\.example\/m\/S06/);
    assert.equal(crumbJson.includes("$"), false);
    assert.equal(crumbJson.includes("25"), false);

    const look: ShopLook = {
      ma: "A01",
      type: "A",
      titleEn: "Puppy cardigan",
      titleVn: "Áo",
      priceUsd: 28,
      colors: [],
      images: [],
      sizes: [],
      descriptionEn: "Soft cardigan",
      descriptionVn: "",
      measurements: null,
    };
    const listJson = JSON.stringify(homeCatalogJsonLd([look]));
    assert.match(listJson, /ItemList/);
    assert.match(listJson, /A01 · Puppy cardigan/);
    assert.equal(listJson.includes("28"), false);
    assert.equal(listJson.includes("price"), false);
    assert.equal(listJson.includes("$"), false);
  } finally {
    if (previous === undefined) {
      delete process.env.NEXT_PUBLIC_SHOP_URL;
    } else {
      process.env.NEXT_PUBLIC_SHOP_URL = previous;
    }
  }
});

test("S06 price lock and the local lighthouse audit stay in place", () => {
  const ops = read("lib/admin-ops.ts");
  assert.match(ops, /ma === "S06" && input\.priceUsd !== 25/);
  const audit = read("scripts/audit-shop.mjs");
  assert.match(audit, /lighthouse/);
  assert.match(audit, /held\.json/);
  assert.match(audit, /25\.00/);
  assert.match(audit, /color-contrast/);
  assert.match(audit, /font-size/);
  assert.match(audit, /target-size/);
});
