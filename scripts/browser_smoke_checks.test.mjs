import assert from "node:assert/strict";
import test from "node:test";
import {
  heldStatusOk,
  noindexPresent,
  originOf,
  plan,
  s06JsonLdOk,
  s06JsonLdPrices,
  visiblePriceOk,
} from "./browser_smoke_checks.mjs";

const S06_LD_SKU = (sku, price, currency = "USD") =>
  `<script type="application/ld+json">${JSON.stringify({
    "@context": "https://schema.org",
    "@type": "Product",
    sku,
    offers: { "@type": "Offer", priceCurrency: currency, price },
  })}</script>`;

const S06_LD = (price) => S06_LD_SKU("S06", price, "USD");

test("visible PDP price is only $25", () => {
  assert.equal(visiblePriceOk("$25"), true);
  assert.equal(visiblePriceOk(" $25.00 "), true);
  assert.equal(visiblePriceOk("$16"), false);
  assert.equal(visiblePriceOk("$250"), false);
  assert.equal(visiblePriceOk("was $25"), false);
  assert.equal(visiblePriceOk(""), false);
});

test("json-ld uses the S06 offer, not another $25", () => {
  const html = `${S06_LD("25.00")}<p>$16</p><script type="application/ld+json">${JSON.stringify({
    "@type": "Product",
    sku: "A01",
    offers: { price: "25.00" },
  })}</script>`;
  const parsed = s06JsonLdPrices(html);
  assert.deepEqual(parsed.prices, [{ price: "25.00", currency: "USD" }]);
  assert.equal(s06JsonLdOk(parsed), true);
  assert.equal(s06JsonLdOk(s06JsonLdPrices(S06_LD_SKU("S006", "25.00", "USD"))), true);
  assert.equal(s06JsonLdOk(s06JsonLdPrices(S06_LD_SKU("S6", "25.00", "USD"))), true);
  assert.equal(s06JsonLdOk(s06JsonLdPrices(S06_LD_SKU("S06", "25.00", "EUR"))), false);
  assert.equal(s06JsonLdOk(s06JsonLdPrices(S06_LD_SKU("S06", "25.00", ""))), false);
  assert.equal(s06JsonLdOk(s06JsonLdPrices(S06_LD("16.00"))), false);
  assert.equal(s06JsonLdOk(s06JsonLdPrices("<p>$25</p>")), false);
  assert.equal(s06JsonLdOk(s06JsonLdPrices(`${S06_LD("25.00")}${S06_LD("25.00")}`)), false);
});

test("json-ld inside @graph and a broken script fails closed", () => {
  const html = `<script type="application/ld+json">${JSON.stringify({
    "@graph": [{ "@type": "Product", sku: "S06", offers: [{ price: 25, priceCurrency: "USD" }] }],
  })}</script>`;
  assert.equal(s06JsonLdOk(s06JsonLdPrices(html)), true);
  const broken = `<script type="application/ld+json">{</script>${S06_LD("25.00")}`;
  assert.equal(s06JsonLdPrices(broken).error, "json-ld parse failed");
});

test("noindex from header or robots meta, either attribute order", () => {
  assert.equal(noindexPresent("noindex, nofollow", ""), true);
  assert.equal(noindexPresent("", '<meta name="robots" content="noindex, nofollow">'), true);
  assert.equal(noindexPresent("", "<meta content='noindex, nofollow, nosnippet' name='robots'>"), true);
  assert.equal(noindexPresent("", '<meta name="robots" content="index, follow">'), false);
  assert.equal(noindexPresent("", "<meta name=\"description\" content=\"noindex\">"), false);
  assert.equal(noindexPresent("", ""), false);
});

test("held page must be http 404", () => {
  assert.equal(heldStatusOk(404), true);
  assert.equal(heldStatusOk(200), false);
  assert.equal(heldStatusOk(0), false);
});

test("plan covers both shops, held mãs, S06, and intake", () => {
  const checks = plan({
    shops: ["https://shop.example", "https://other.example/"],
    intake: "https://intake.example",
    held: ["K03"],
  });
  const urls = checks.map((item) => `${item.kind} ${item.url}`);
  assert.deepEqual(urls, [
    "noindex https://shop.example/",
    "s06 https://shop.example/m/S06",
    "held https://shop.example/m/K03",
    "noindex https://other.example/",
    "s06 https://other.example/m/S06",
    "held https://other.example/m/K03",
    "noindex https://intake.example/",
  ]);
});

test("origins stay http(s)", () => {
  assert.equal(originOf("https://sassy-closet-shop.vercel.app/m/S06"), "https://sassy-closet-shop.vercel.app");
  assert.throws(() => originOf("file:///tmp/x"), /unsupported scheme/);
});
