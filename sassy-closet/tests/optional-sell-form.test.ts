import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import test from "node:test";

test("intake form keeps sell optional and leaves auto-calc off the save path", () => {
  const src = fs.readFileSync(path.join(process.cwd(), "components/IntakeApp.tsx"), "utf8");
  assert.match(src, /data-testid="sell-price"/);
  assert.match(src, /data-testid="sell-optional"/);
  assert.match(src, /Để trống vẫn lưu/);
  assert.equal(src.includes('data-testid="price-panel"'), false);
  assert.equal(src.includes('data-testid="price-use"'), false);
  assert.equal(src.includes("Dùng giá"), false);
  assert.equal(src.includes("Tính giá tự động"), false);
  assert.equal(src.includes("Thiếu giá"), false);
  assert.match(src, /disabled=\{props\.busy \|\| !props\.canSave\}/);
  assert.equal(/sellUsd/.test(src.slice(src.indexOf("data-testid=\"save-mint\""), src.indexOf("data-testid=\"save-mint\"") + 180)), false);
});
