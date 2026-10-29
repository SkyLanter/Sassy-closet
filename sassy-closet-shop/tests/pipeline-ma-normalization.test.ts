import assert from "node:assert/strict";
import test from "node:test";
import { getPipelineRow, parsePipelineDocument, setPipelineStage } from "../lib/pipeline";

const ma = ["A", "03"].join("");
const variants = [ma[0] + "0" + ma.slice(1), ` ${ma} `, ma.toLowerCase(), (ma[0] + "0" + ma.slice(1)).toLowerCase()];

test("pipeline rows are found and updated under padded/spaced/lower mã spellings", () => {
  for (const stored of [ma, ...variants]) {
    const doc = parsePipelineDocument({ rows: [{ ma: stored, stages: {} }] }, "site");
    assert.equal(doc.rows[0]?.ma, ma, `stored ${JSON.stringify(stored)}`);
    for (const asked of variants) {
      assert.ok(getPipelineRow(doc, asked), `asked ${JSON.stringify(asked)}`);
      const next = setPipelineStage(doc, asked, "intake", true);
      assert.equal(next.rows.length, 1, `no duplicate row for ${JSON.stringify(asked)}`);
    }
  }
});
