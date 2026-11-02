import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import path from "node:path";
import test from "node:test";
import { editorialTitle, pickFeatureCards } from "../lib/home-features";
import type { MaLetter } from "../lib/ma";
import type { ShopLook } from "../lib/shop-look";

function look(ma: string, type: MaLetter, image = true): ShopLook {
  return {
    ma,
    type,
    titleVn: `VN ${ma}`,
    titleEn: `Title ${ma}`,
    priceUsd: 12,
    colors: [],
    sizes: [],
    images: image ? [{ src: `/products/${ma}/cover.jpg`, colorId: null, order: 1 }] : [],
    descriptionVn: "",
    descriptionEn: `Copy ${ma}`,
    measurements: null,
  };
}

test("feature cards take the first covered look of each category and never invent a mã", () => {
  const looks = [
    look("A05", "A"),
    look("A01", "A"),
    look("S05", "S", false),
    look("S03", "S"),
    look("D02", "D"),
    look("P02", "P"),
  ];
  const cards = pickFeatureCards(looks, ["A", "S", "D", "P"]);
  assert.deepEqual(
    cards.map((card) => card.look.ma),
    ["A05", "S03", "D02"],
  );
  assert.equal(cards.some((card) => card.look.ma === "Z99"), false);
  assert.equal(pickFeatureCards([], ["A"]).length, 0);
});

test("feature cards skip a category that has no cover", () => {
  const looks = [look("D02", "D")];
  const cards = pickFeatureCards(looks, ["A", "D"]);
  assert.equal(cards.length, 1);
  assert.equal(cards[0]?.look.ma, "D02");
  assert.equal(cards[0]?.type, "D");
});

test("editorial titles stay on the catalog title", () => {
  const item = look("A05", "A");
  assert.equal(editorialTitle(item), "Title A05");
  assert.equal(editorialTitle({ ma: "H01", titleEn: "  ", titleVn: "Nơ thỏ" }), "Nơ thỏ");
  assert.equal(editorialTitle({ ma: "H02", titleEn: "", titleVn: "" }), "H02");
});

test("home keeps the hero, then category plates, then the look grid", () => {
  const home = readFileSync(path.join(process.cwd(), "app/(shop)/(browse)/page.tsx"), "utf8");
  const editorial = readFileSync(path.join(process.cwd(), "components/home-editorial.tsx"), "utf8");
  const heroAt = home.indexOf("<HeroEditorial");
  const platesAt = home.indexOf("<HomeEditorial");
  const waveAt = home.indexOf("<ContentWaveHost");
  assert.ok(heroAt >= 0 && platesAt > heroAt && waveAt > platesAt);
  assert.equal(home.includes("CollectionList"), false);
  assert.equal(home.includes("look-story"), false);
  assert.equal(editorial.includes("LookStory"), false);
  assert.equal(editorial.includes("look-story"), false);
});
