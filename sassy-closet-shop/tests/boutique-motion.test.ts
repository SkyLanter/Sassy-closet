import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import path from "node:path";
import test from "node:test";

const root = process.cwd();

function read(rel: string): string {
  return readFileSync(path.join(root, rel), "utf8");
}

test("look cards scale and fade in only after they enter the viewport", () => {
  const css = read("app/globals.css");
  const card = read("components/product-card.tsx");
  const noPreference = css.split("@media (prefers-reduced-motion: no-preference)")[1] ?? "";
  assert.equal(card.includes('className="sc-rise'), true);
  assert.equal(card.includes('el.dataset.rise = "pending"'), true);
  assert.equal(card.includes('el.dataset.rise = "shown"'), true);
  assert.equal(card.includes("if (!el || reduced)"), true);
  assert.match(noPreference, /\.sc-rise\[data-rise="pending"\][\s\S]*opacity:\s*0/);
  assert.match(noPreference, /\.sc-rise\[data-rise="pending"\][\s\S]*scale\(0\.965\)/);
  assert.match(noPreference, /\.sc-rise\[data-rise="shown"\][\s\S]*animation:\s*sc-rise/);
  assert.match(css, /@keyframes sc-rise\s*\{[\s\S]*opacity:\s*0[\s\S]*scale\(0\.965\)[\s\S]*opacity:\s*1/);
});

test("category tabs, PDP price, and header nav have one quiet entrance each", () => {
  const css = read("app/globals.css");
  const noPreference = css.split("@media (prefers-reduced-motion: no-preference)")[1] ?? "";
  const featured = read("components/featured-board.tsx");
  const header = read("components/header.tsx");
  const look = read("components/product-look.tsx");
  assert.equal(featured.includes("sc-tab-pop"), true);
  assert.equal(header.includes("sc-nav-reveal"), true);
  assert.equal(look.includes("sc-price-in"), true);
  assert.match(noPreference, /\.sc-tab-pop\s*\{[\s\S]*animation:\s*sc-tab-pop/);
  assert.match(noPreference, /\.sc-price-in\s*\{[\s\S]*animation:\s*sc-price-in/);
  assert.match(noPreference, /\.sc-nav-reveal\s*\{[\s\S]*animation:\s*sc-nav-reveal/);
  assert.equal(css.includes("sc-glass-pop"), true);
});

test("reduced motion keeps the new boutique entrances fully visible", () => {
  const css = read("app/globals.css");
  const reduce = css.split("@media (prefers-reduced-motion: reduce)")[1] ?? "";
  for (const name of [".sc-rise", ".sc-tab-pop", ".sc-price-in", ".sc-nav-reveal"]) {
    assert.equal(reduce.includes(name), true, name);
  }
  assert.match(reduce, /\.sc-rise\[data-rise="pending"\][\s\S]*opacity:\s*1 !important/);
  assert.match(reduce, /\.sc-nav-reveal\s*\{[\s\S]*transform:\s*none !important/);
});
