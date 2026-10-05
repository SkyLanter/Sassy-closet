import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import path from "node:path";
import test from "node:test";
import {
  LOOK_GRID_SIZES,
  RELATED_LOOK_SIZES,
  lookCardFetchPriority,
  nativePhotoSettle,
  revealLookPhoto,
} from "../lib/look-card-photo";

const root = process.cwd();

function read(rel: string): string {
  return readFileSync(path.join(root, rel), "utf8");
}

test("above-the-fold look cards are the only high-priority fetches", () => {
  assert.equal(lookCardFetchPriority(true), "high");
  assert.equal(lookCardFetchPriority(false), "auto");
  assert.equal(lookCardFetchPriority(true, "low"), "low");
  assert.equal(lookCardFetchPriority(false, "high"), "high");
  assert.equal(lookCardFetchPriority(false, "auto"), "auto");
});

test("look-grid and category sizes match the 2/3/4/5 column tracks", () => {
  assert.match(LOOK_GRID_SIZES, /\(max-width: 639px\) calc\(\(100vw - 3\.25rem\) \/ 2\)/);
  assert.match(LOOK_GRID_SIZES, /\(max-width: 1023px\) calc\(\(100vw - 6\.5rem\) \/ 3\)/);
  assert.match(LOOK_GRID_SIZES, /\(max-width: 1279px\) calc\(\(100vw - 7\.75rem\) \/ 4\)/);
  assert.match(LOOK_GRID_SIZES, /calc\(\(min\(100vw, 84rem\) - 9rem\) \/ 5\)$/);
  assert.match(RELATED_LOOK_SIZES, /min\(16\.5rem, calc\(\(100vw - 2\.5rem\) \* 0\.7\)\)/);
  assert.match(RELATED_LOOK_SIZES, /min\(100vw, 80rem\)/);
});

test("look cards wire priority, srcset sizes, blush, and an async decode", () => {
  const photo = read("components/look-photo.tsx");
  const image = read("components/product-image.tsx");
  const grid = read("components/product-grid.tsx");
  const card = read("components/product-card.tsx");
  const board = read("components/featured-board.tsx");
  const css = read("app/globals.css");

  assert.match(photo, /lookCardFetchPriority\(priority, fetchPriority\)/);
  assert.match(photo, /decoding="async"/);
  assert.match(photo, /sizes=\{sizes\}/);
  assert.match(photo, /placeholder="blur"/);
  assert.match(photo, /blurDataURL=\{BLUSH_BLUR\}/);
  assert.equal(photo.includes('fetchPriority ?? "auto"'), false);
  assert.match(photo, /loading=\{priority \? "eager" : "lazy"\}/);
  assert.match(photo, /nativePhotoSettle\(img\)/);
  assert.match(photo, /case "broken"/);
  assert.match(photo, /revealLookPhoto\(/);

  assert.match(image, /LOOK_GRID_SIZES/);
  assert.match(image, /BLUSH_BLUR/);
  assert.match(image, /fadeIn/);
  assert.match(image, /sc-card-photo/);
  assert.match(image, /viewTransitionName: `product-\$\{product\.ma\}`/);
  assert.equal(image.includes("opacity-0"), false);

  assert.match(grid, /LOOK_GRID_SIZES/);
  assert.match(grid, /RELATED_LOOK_SIZES/);
  assert.match(grid, /variant === "compact" \? RELATED_LOOK_SIZES : LOOK_GRID_SIZES/);
  assert.match(grid, /priority=\{index < eagerCount\}/);

  assert.match(card, /aspect-\[3\/4\]/);
  assert.equal(card.includes("onLoad"), false);
  assert.equal(card.includes("img.complete"), false);

  assert.match(board, /eagerCount=\{index === 0 \? 2 : 0\}/);

  assert.match(css, /\.sc-photo\.sc-card-photo\[data-loaded="false"\]/);
  assert.match(css, /\.sc-card-photo,\s*\.sc-card-photo\[data-loaded="false"\]/);
  assert.match(css, /aspect-ratio: 3 \/ 4/);
});

test("a native cover that already finished is ready or broken, never a blank wait", () => {
  assert.equal(
    nativePhotoSettle({ complete: false, naturalWidth: 0, currentSrc: "" }),
    "pending",
  );
  assert.equal(
    nativePhotoSettle({ complete: true, naturalWidth: 0, currentSrc: "" }),
    "pending",
  );
  assert.equal(
    nativePhotoSettle({ complete: true, naturalWidth: 800, currentSrc: "https://cdn.example/a.jpg" }),
    "ready",
  );
  assert.equal(
    nativePhotoSettle({ complete: true, naturalWidth: 0, currentSrc: "https://cdn.example/missing.jpg" }),
    "broken",
  );
});

test("card fades wait for decode, and a decode failure still reveals", async () => {
  const seen: string[] = [];
  revealLookPhoto({ naturalWidth: 0, decode: () => Promise.resolve() }, () => seen.push("empty"), true);
  revealLookPhoto({ naturalWidth: 10 }, () => seen.push("no-decode"), false);
  assert.deepEqual(seen, ["no-decode"]);

  await new Promise<void>((resolve) => {
    revealLookPhoto(
      {
        naturalWidth: 10,
        decode: () => Promise.resolve(),
      },
      () => {
        seen.push("decoded");
        resolve();
      },
      true,
    );
  });
  await new Promise<void>((resolve) => {
    revealLookPhoto(
      {
        naturalWidth: 10,
        decode: () => Promise.reject(new Error("decode")),
      },
      () => {
        seen.push("rejected");
        resolve();
      },
      true,
    );
  });
  assert.deepEqual(seen, ["no-decode", "decoded", "rejected"]);
});
