import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import path from "node:path";
import test from "node:test";

function read(rel: string): string {
  return readFileSync(path.join(process.cwd(), rel), "utf8");
}

test("root layout mounts Web Analytics and Speed Insights", () => {
  const layout = read("app/layout.tsx");
  assert.match(layout, /import \{ Analytics \} from "@vercel\/analytics\/next"/);
  assert.match(layout, /import \{ SpeedInsights \} from "@vercel\/speed-insights\/next"/);
  assert.match(layout, /<Analytics \/>/);
  assert.match(layout, /<SpeedInsights \/>/);
});

test("product page records product_view with the mã", () => {
  const page = read("app/(shop)/m/[ma]/page.tsx");
  const event = read("components/product-view-event.tsx");
  assert.match(page, /<ProductViewEvent ma=\{product\.ma\} \/>/);
  assert.match(event, /from "@vercel\/analytics"/);
  assert.match(event, /track\("product_view", \{ ma \}\)/);
});

test("messenger click records messenger_cta only when a mã is set", () => {
  const cta = read("components/messenger-cta.tsx");
  const header = read("components/header.tsx");
  const footer = read("components/footer.tsx");
  assert.match(cta, /from "@vercel\/analytics"/);
  assert.match(cta, /if \(!ma\) \{\s*return;\s*\}/);
  assert.match(cta, /track\("messenger_cta", \{ ma \}\)/);
  assert.match(cta, /target="_blank"/);
  assert.match(cta, /rel="noopener noreferrer"/);
  assert.equal(cta.includes("preventDefault"), false);
  assert.match(header, /<MessengerCta variant="header"/);
  assert.equal(header.includes("<MessengerCta") && header.includes("ma="), false);
  assert.match(footer, /<MessengerCta variant="ghost" \/>/);
  assert.equal(footer.includes("ma="), false);
});

test("header search submit records a trimmed query and skips blanks", () => {
  const search = read("components/header-search.tsx");
  assert.match(search, /from "@vercel\/analytics"/);
  assert.match(search, /searchSubmitQuery\(value\)/);
  assert.match(search, /track\("search_submit", \{ query \}\)/);
  assert.match(search, /if \(query\)/);
});
