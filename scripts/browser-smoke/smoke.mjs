/**
 * Read-only browser smoke for both sell hosts and intake.
 * GET via Playwright only. No cookies, no forms, no deploy.
 *
 * Usage:
 *   node scripts/browser-smoke/smoke.mjs [--dry-run]
 * Env: SHOP_HOSTS, INTAKE_BASE, HELD_MAS, CHECK_TIMEOUT (seconds, default 20).
 */
import { spawnSync } from "node:child_process";
import path from "node:path";
import { fileURLToPath } from "node:url";
import {
  heldStatusOk,
  noindexPresent,
  originOf,
  plan,
  s06JsonLdOk,
  s06JsonLdPrices,
  visiblePriceOk,
} from "../browser_smoke_checks.mjs";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../..");
const DEFAULT_SHOPS = "https://sassy-closet-shop.vercel.app https://sassycloset.vercel.app";
const DEFAULT_INTAKE = "https://sassy-closet.vercel.app";

function fail(message) {
  console.error(`FAIL ${message}`);
  process.exit(1);
}

function heldList() {
  const ran = spawnSync("python3", ["scripts/browser_smoke_held.py"], {
    cwd: ROOT,
    encoding: "utf8",
    env: process.env,
  });
  if (ran.status !== 0) {
    const detail = (ran.stderr || "").trim().split("\n").pop() || "could not build held list";
    fail(detail);
  }
  return ran.stdout.trim().split(/\s+/).filter(Boolean);
}

function bases(raw, label) {
  const items = String(raw).split(/\s+/).filter(Boolean);
  if (items.length === 0) fail(`${label} is empty`);
  return items.map((item) => {
    try {
      return originOf(item);
    } catch (error) {
      fail(`${label} ${item}: ${error.message}`);
    }
    return "";
  });
}

function argsOk(argv) {
  if (argv.length === 0) return false;
  if (argv.length === 1 && argv[0] === "--dry-run") return true;
  console.error("usage: smoke.mjs [--dry-run]");
  process.exit(2);
}

const dry = argsOk(process.argv.slice(2));
const shops = bases(process.env.SHOP_HOSTS || DEFAULT_SHOPS, "shop");
const intake = bases(process.env.INTAKE_BASE || DEFAULT_INTAKE, "intake")[0];
const held = heldList();
const checks = plan({ shops, intake, held });

if (dry) {
  console.log(`DRY RUN (no browser). shops=[${shops.join(" ")}] intake=${intake}`);
  for (const check of checks) {
    if (check.kind === "s06") console.log(`CHECK GET ${check.url} -> 200, PDP price $25, S06 offer 25, noindex`);
    else if (check.kind === "held") console.log(`CHECK GET ${check.url} -> 404 (held)`);
    else console.log(`CHECK GET ${check.url} -> noindex`);
  }
  process.exit(0);
}

const timeout = Number(process.env.CHECK_TIMEOUT || 20) * 1000;
const { chromium } = await import("playwright");
const browser = await chromium.launch({ headless: true });
const context = await browser.newContext({
  userAgent: "sassy-readonly-browser-smoke/1",
  javaScriptEnabled: false,
});
const page = await context.newPage();
const apiHits = [];
await page.route("**/*", async (route) => {
  const req = route.request();
  let pathname = "";
  try {
    pathname = new URL(req.url()).pathname;
  } catch {
    pathname = "";
  }
  if (req.method() !== "GET" || req.resourceType() !== "document" || pathname.startsWith("/api/")) {
    if (pathname.startsWith("/api/")) apiHits.push(pathname);
    await route.abort();
    return;
  }
  await route.continue();
});
let fails = 0;

function report(ok, label, detail) {
  if (ok) console.log(`PASS  ${label}`);
  else {
    console.log(`FAIL  ${label}  (${detail})`);
    fails += 1;
  }
}

try {
  for (const check of checks) {
    let response;
    try {
      response = await page.goto(check.url, { waitUntil: "domcontentloaded", timeout });
    } catch (error) {
      report(false, check.url, error.name || "navigation error");
      continue;
    }
    const status = response ? response.status() : 0;
    const robots = response ? response.headers()["x-robots-tag"] || "" : "";
    if (check.kind === "held") {
      report(heldStatusOk(status), `${check.url} 404 (held)`, `http ${status}`);
      continue;
    }
    const html = await page.content();
    if (check.kind === "noindex") {
      report(status === 200 && noindexPresent(robots, html), `${check.url} noindex`, `http ${status}`);
      continue;
    }
    const price = (await page.locator(".ky-pdp-price").count())
      ? await page.locator(".ky-pdp-price").first().innerText()
      : "";
    const ld = s06JsonLdPrices(html);
    const ok = status === 200 && visiblePriceOk(price) && s06JsonLdOk(ld) && noindexPresent(robots, html);
    const offers = (ld.prices || []).map((item) => `${item.currency || "none"} ${item.price}`).join(",") || "none";
    const detail = ld.error
      ? `http ${status} ${ld.error}`
      : `http ${status} pdp=${JSON.stringify(price.trim().slice(0, 40))} offer=${offers}`;
    report(ok, `${check.url} S06 $25`, detail);
  }
  if (apiHits.length > 0) {
    report(false, "api requests", `aborted ${apiHits.length}`);
  }
} finally {
  await browser.close();
}

console.log(fails === 0 ? "BROWSER SMOKE: PASS" : `BROWSER SMOKE: FAIL (${fails} fails)`);
process.exit(fails === 0 ? 0 : 1);
