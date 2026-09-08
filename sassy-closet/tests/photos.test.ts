import assert from "node:assert/strict";
import { test } from "node:test";
import { FIND_CARD_THUMB_LIMIT, photoSrc, realPhotoPaths, visiblePhotoPaths } from "../lib/photos";

test("realPhotoPaths never invents images from empty or junk input", () => {
  assert.deepEqual(realPhotoPaths(undefined), []);
  assert.deepEqual(realPhotoPaths(null), []);
  assert.deepEqual(realPhotoPaths({}), []);
  assert.deepEqual(realPhotoPaths(["", "  ", 1, null, "A01/001.jpg"]), ["A01/001.jpg"]);
});

test("photoSrc uses /api/photos for stored paths and keeps existing urls", () => {
  assert.equal(photoSrc("A01/001.jpg"), "/api/photos/A01/001.jpg");
  assert.equal(photoSrc("/api/photos/P05/002.png"), "/api/photos/P05/002.png");
  assert.equal(photoSrc("blob:http://localhost/1"), "blob:http://localhost/1");
  assert.equal(photoSrc(""), "");
});

test("find card row shows at most 3 real photos and reports +N", () => {
  assert.equal(FIND_CARD_THUMB_LIMIT, 3);
  const four = visiblePhotoPaths(["A01/001.jpg", "A01/002.jpg", "A01/003.jpg", "A01/004.jpg"]);
  assert.deepEqual(four.shown, ["A01/001.jpg", "A01/002.jpg", "A01/003.jpg"]);
  assert.equal(four.extra, 1);
  assert.equal(four.all.length, 4);

  const none = visiblePhotoPaths([]);
  assert.deepEqual(none.shown, []);
  assert.equal(none.extra, 0);

  const two = visiblePhotoPaths(["Q02/001.jpg", "Q02/002.jpg"]);
  assert.deepEqual(two.shown, ["Q02/001.jpg", "Q02/002.jpg"]);
  assert.equal(two.extra, 0);
});
