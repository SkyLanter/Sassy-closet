/**
 * Lighthouse-style shop check. No paid services.
 * Run against `next start` (production build), not `next dev`.
 *
 *   npm run build && npm run start -- --hostname 127.0.0.1 --port 4317
 *   SHOP_AUDIT_URL=http://127.0.0.1:4317 npm run audit:shop
 *
 * Test mode stays noindex, so the SEO category is not gated on is-crawlable.
 * S06 is asserted at $25 only when that page is actually served.
 * Held mãs must stay off the shop.
 */
import { readFileSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { launch as launchChrome } from "chrome-launcher";
import lighthouse from "lighthouse";

const shopRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const repoRoot = path.resolve(shopRoot, "..");
const base = (process.env.SHOP_AUDIT_URL || "http://127.0.0.1:4317").replace(/\/$/, "");

const REQUIRED_AUDITS = [
  "document-title",
  "meta-description",
  "viewport",
  "html-has-lang",
  "image-alt",
  "link-text",
  "button-name",
  "heading-order",
  "color-contrast",
  "target-size",
  "font-size",
  "crawlable-anchors",
  "http-status-code",
];

const PAGES = ["/", "/m/A01"];

function fail(message) {
  console.error(`FAIL ${message}`);
  return message;
}

async function fetchText(urlPath) {
  const response = await fetch(`${base}${urlPath}`, { redirect: "manual" });
  const text = await response.text();
  return { status: response.status, text };
}

function heldMas() {
  const held = JSON.parse(readFileSync(path.join(repoRoot, "data/held.json"), "utf8"));
  return [...held.heldIncomplete, ...held.neverList].map((ma) => String(ma).toUpperCase());
}

async function assertCatalog(failures) {
  const home = await fetchText("/");
  if (home.status !== 200) {
    failures.push(fail(`home status ${home.status}`));
    return;
  }
  if (!home.text.includes("sc-price")) {
    failures.push(fail("home is missing prices"));
  }
  if (!home.text.includes('"@type":"WebSite"') && !home.text.includes('"@type": "WebSite"')) {
    failures.push(fail("home is missing WebSite JSON-LD"));
  }
  for (const ma of heldMas()) {
    if (home.text.includes(`/m/${ma}`)) {
      failures.push(fail(`home links held mã ${ma}`));
    }
    const page = await fetchText(`/m/${ma}`);
    if (page.status !== 404) {
      failures.push(fail(`held mã ${ma} is ${page.status}, expected 404`));
    }
  }

  const s06 = await fetchText("/m/S06");
  if (s06.status === 200) {
    const blocks = [...s06.text.matchAll(/<script type="application\/ld\+json">([\s\S]*?)<\/script>/g)];
    const product = blocks
      .map((match) => JSON.parse(match[1]))
      .find((entry) => entry && entry["@type"] === "Product" && entry.sku === "S06");
    const price = product?.offers?.price;
    if (price !== "25.00") {
      failures.push(fail(`S06 JSON-LD price is ${price ?? "missing"}, expected 25.00`));
    }
  } else if (s06.status !== 404) {
    failures.push(fail(`S06 status ${s06.status}`));
  } else {
    console.log("S06 is not in this catalog (404). Price lock stays in admin save.");
  }
}

function auditScore(lhr, id) {
  return lhr.audits[id]?.score;
}

async function assertLighthouse(failures) {
  const chrome = await launchChrome({
    chromeFlags: ["--headless=new", "--no-sandbox", "--disable-gpu", "--disable-dev-shm-usage"],
  });
  try {
    for (const page of PAGES) {
      const url = `${base}${page}`;
      const runner = await lighthouse(url, {
        port: chrome.port,
        logLevel: "error",
        output: "json",
        onlyCategories: ["performance", "accessibility", "best-practices", "seo"],
      });
      const lhr = runner.lhr;
      const scores = Object.fromEntries(
        Object.entries(lhr.categories).map(([key, category]) => [key, category.score]),
      );
      console.log(`${page} scores ${JSON.stringify(scores)}`);
      if ((scores.accessibility ?? 0) < 0.9) {
        failures.push(fail(`${page} accessibility ${scores.accessibility}`));
      }
      if ((scores["best-practices"] ?? 0) < 0.9) {
        failures.push(fail(`${page} best-practices ${scores["best-practices"]}`));
      }
      if ((scores.performance ?? 0) < 0.45) {
        failures.push(fail(`${page} performance ${scores.performance}`));
      }
      for (const id of REQUIRED_AUDITS) {
        const score = auditScore(lhr, id);
        if (score !== 1) {
          const details = lhr.audits[id]?.title ?? id;
          failures.push(fail(`${page} ${id} score ${score} (${details})`));
        }
      }
    }
  } finally {
    await chrome.kill();
  }
}

const failures = [];
await assertCatalog(failures);
await assertLighthouse(failures);
if (failures.length > 0) {
  console.error(`${failures.length} shop audit failure(s)`);
  process.exit(1);
}
console.log("shop audit passed");
