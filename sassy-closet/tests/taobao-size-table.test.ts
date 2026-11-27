import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import path from "node:path";
import { test } from "node:test";
import { parseTaobaoHtml } from "../lib/taobao";

const FIXTURES = path.join(process.cwd(), "../scripts/tests/fixtures/taobao");
const PAD = " ".repeat(2100);

function page(name: string): string {
  return readFileSync(path.join(FIXTURES, name), "utf8");
}

test("a seller size table is captured as Asia letters and cm stays off", () => {
  const item = parseTaobaoHtml(page("sku-size-table.html"), "1");
  assert.equal(item.listCny, "88.00");
  assert.deepEqual(item.sizeAxes, [{ name: "尺码", values: ["S", "M", "L"] }]);
  const values = item.sizeAxes.flatMap((axis) => axis.values);
  assert.equal(values.includes("84"), false);
  assert.equal(values.includes("88"), false);
  assert.equal(values.includes("92"), false);

  const column = `<table><tr><th>尺码</th><th>胸围</th></tr><tr><td><span>S</span></td><td>84</td></tr><tr><td>M</td><td>88</td></tr><tr><td>L</td><td>92</td></tr></table>${PAD}`;
  assert.deepEqual(parseTaobaoHtml(column, "1").sizeAxes, [{ name: "尺码", values: ["S", "M", "L"] }]);

  const english = `<table><tr><td>Size</td><td>S</td><td>M</td></tr></table>${PAD}`;
  assert.deepEqual(parseTaobaoHtml(english, "1").sizeAxes, [{ name: "Size", values: ["S", "M"] }]);

  const colors = `<table><tr><td>颜色</td><td>杏色</td><td>黑色</td></tr></table>${PAD}`;
  assert.deepEqual(parseTaobaoHtml(colors, "1").sizeAxes, []);
  assert.deepEqual(parseTaobaoHtml(page("bridge-list.html"), "1").sizeAxes, []);
});

test("a SKU size axis wins over a size table", () => {
  const sku =
    '{"pid":"1627207","name":"颜色分类","values":[{"name":"杏色"},{"name":"黑色"}]},' +
    '{"pid":"20509","name":"尺码","values":[{"name":"S"},{"name":"M"},{"name":"L"}]}';
  const both = `${sku}<table><tr><td>尺码</td><td>XL</td></tr></table>${PAD}`;
  const item = parseTaobaoHtml(both, "1");
  assert.deepEqual(item.colors, ["杏色", "黑色"]);
  assert.deepEqual(item.sizeAxes, [{ name: "尺码", values: ["S", "M", "L"] }]);
});
