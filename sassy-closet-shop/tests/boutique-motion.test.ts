import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import path from "node:path";
import test from "node:test";

function read(rel: string): string {
  return readFileSync(path.join(process.cwd(), rel), "utf8");
}

test("look cards scale and fade in only after they enter the viewport", () => {
  const css = read("app/globals.css");
  const card = read("components/product-card.tsx");
  assert.equal(card.includes('className="sc-rise'), true);
  assert.equal(card.includes('el.dataset.rise = "pending"'), true);
  assert.equal(card.includes('el.dataset.rise = "shown"'), true);
  assert.equal(card.includes("if (!el || reduced)"), true);
  assert.equal(card.includes("new IntersectionObserver"), true);
  assert.equal(card.includes("onload"), false);
  assert.equal(card.includes("sc-card-plate"), true);
  assert.equal(
    css.includes(`.sc-rise[data-rise="pending"] {
    opacity: 0;
    transform: translateY(10px) scale(0.975);
  }`),
    true,
  );
  assert.equal(css.includes("will-change: transform, opacity;"), true);
  assert.equal(css.includes("animation: sc-rise 380ms var(--sc-ease) both;"), true);
  assert.equal(css.includes(".sc-card-plate"), true);
  assert.match(css, /\.sc-rise \.sc-photo\[data-loaded="false"\][\s\S]*?transform:\s*none/);
  assert.match(
    css,
    /@keyframes sc-rise\s*\{[\s\S]*opacity:\s*0[\s\S]*scale\(0\.975\)[\s\S]*opacity:\s*1/,
  );
});

test("category tabs, PDP price, and header nav have one quiet entrance each", () => {
  const css = read("app/globals.css");
  const featured = read("components/featured-board.tsx");
  const header = read("components/header.tsx");
  const look = read("components/product-look.tsx");
  assert.equal(featured.includes("sc-tab-pop"), true);
  assert.equal(header.includes("sc-nav-reveal"), true);
  assert.equal(look.includes("sc-price-in"), true);
  assert.equal(css.includes("animation: sc-tab-pop 280ms var(--sc-ease) both;"), true);
  assert.equal(css.includes("animation: sc-price-in 420ms var(--sc-ease) both;"), true);
  assert.equal(css.includes("animation: sc-nav-reveal 440ms var(--sc-ease) both;"), true);
  const entrance = css.split("@media (prefers-reduced-motion: no-preference)").at(-1) ?? "";
  assert.equal(entrance.includes("animation: sc-tab-pop"), true);
  assert.equal(entrance.includes("animation: sc-price-in"), true);
  assert.equal(entrance.includes("animation: sc-nav-reveal"), true);
  assert.equal(entrance.includes("animation: sc-rise"), true);
});

test("reduced motion keeps the new boutique entrances fully visible", () => {
  const css = read("app/globals.css");
  const reduce = css.split("@media (prefers-reduced-motion: reduce)")[1] ?? "";
  for (const name of [".sc-rise", ".sc-tab-pop", ".sc-price-in", ".sc-nav-reveal"]) {
    assert.equal(reduce.includes(`${name},`) || reduce.includes(`${name} {`), true, name);
    assert.equal(reduce.includes("animation: none !important"), true);
  }
  assert.match(reduce, /\.sc-rise\[data-rise="pending"\][\s\S]*opacity:\s*1 !important/);
  assert.match(reduce, /\.sc-nav-reveal\s*\{[\s\S]*transform:\s*none !important/);
});
