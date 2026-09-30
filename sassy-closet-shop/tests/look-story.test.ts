import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import path from "node:path";
import test from "node:test";
import {
  editorialLine,
  editorialTitle,
  lookStoryIndex,
  lookStoryProgress,
  pickFeatureCards,
  pickLookStory,
} from "../lib/look-story";
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

test("look story keeps popular order, skips covers that are missing, and never invents a mã", () => {
  const looks = [
    look("A05", "A"),
    look("A01", "A", false),
    look("S05", "S"),
    look("S03", "S"),
    look("A06", "A"),
    look("D02", "D"),
  ];
  const story = pickLookStory(looks);
  assert.deepEqual(
    story.map((item) => item.ma),
    ["A05", "S05", "S03", "A06"],
  );
  assert.equal(story.some((item) => item.ma === "Z99"), false);
  assert.equal(pickLookStory([]).length, 0);
});

test("feature cards prefer a look that is not already in the scroll stage", () => {
  const looks = [
    look("A05", "A"),
    look("A01", "A"),
    look("S05", "S"),
    look("S03", "S"),
    look("D02", "D"),
  ];
  const cards = pickFeatureCards(looks, ["A", "S", "D", "P"], ["A05", "S05"]);
  assert.deepEqual(
    cards.map((card) => card.look.ma),
    ["A01", "S03", "D02"],
  );
  assert.equal(cards.some((card) => card.look.ma === "A05"), false);
});

test("feature cards fall back to the stage look when a category has only one cover", () => {
  const looks = [look("D02", "D")];
  const cards = pickFeatureCards(looks, ["D"], ["D02"], 3);
  assert.equal(cards.length, 1);
  assert.equal(cards[0]?.look.ma, "D02");
  assert.equal(cards[0]?.type, "D");
});

test("editorial lines stay on the catalog title and description", () => {
  const item = look("A05", "A");
  assert.equal(editorialTitle(item), "Title A05");
  assert.equal(editorialLine(item), "Copy A05");
  assert.equal(editorialTitle({ ma: "H01", titleEn: "  ", titleVn: "Nơ thỏ" }), "Nơ thỏ");
  assert.equal(editorialLine({ ...item, descriptionEn: "", descriptionVn: "" }), "Tops");
});

test("scroll index holds each look for an equal slice", () => {
  assert.equal(lookStoryProgress(-20, 400), 0);
  assert.equal(lookStoryProgress(0, 0), 0);
  assert.equal(lookStoryProgress(400, 400), 1);
  assert.equal(lookStoryIndex(0, 4), 0);
  assert.equal(lookStoryIndex(0.24, 4), 0);
  assert.equal(lookStoryIndex(0.25, 4), 1);
  assert.equal(lookStoryIndex(0.5, 4), 2);
  assert.equal(lookStoryIndex(0.99, 4), 3);
  assert.equal(lookStoryIndex(1, 4), 3);
  assert.equal(lookStoryIndex(0, 1), 0);
});

test("home keeps the hero, then the scroll stage, then the look grid", () => {
  const home = readFileSync(path.join(process.cwd(), "app/(shop)/(browse)/page.tsx"), "utf8");
  const heroAt = home.indexOf("<HeroEditorial");
  const storyAt = home.indexOf("<HomeEditorial");
  const waveAt = home.indexOf("<ContentWaveHost");
  assert.ok(heroAt >= 0 && storyAt > heroAt && waveAt > storyAt);
  assert.equal(home.includes("CollectionList"), false);
});
