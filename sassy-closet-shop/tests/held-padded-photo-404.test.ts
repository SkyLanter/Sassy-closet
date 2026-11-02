import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import test from "node:test";
import { GET } from "../app/products/[ma]/[file]/route";
import { HELD_INCOMPLETE_MAS, isOffLiveSell } from "../lib/held-incomplete";

function padMa(ma: string): string {
  return `${ma[0]}0${ma.slice(1)}`;
}

test("held photo URLs 404 for padded and short spellings even when the file is on disk", async () => {
  const held = HELD_INCOMPLETE_MAS[0];
  assert.ok(held);
  assert.match(held, /^[A-Z]\d{2}$/);
  const padded = padMa(held);
  const live = "Q02";
  assert.equal(isOffLiveSell(live), false);
  assert.equal(isOffLiveSell(padded), true);
  assert.equal(isOffLiveSell(held.toLowerCase()), true);

  const tmp = fs.mkdtempSync(path.join(os.tmpdir(), "shop-held-photo-"));
  const cwd = process.cwd();
  const bytes = {
    held: `held-${held}`,
    padded: `padded-${padded}`,
    live: `live-${live}`,
  };
  try {
    for (const [ma, body] of [
      [held, bytes.held],
      [padded, bytes.padded],
      [live, bytes.live],
    ] as const) {
      const dir = path.join(tmp, "public", "products", ma);
      fs.mkdirSync(dir, { recursive: true });
      fs.writeFileSync(path.join(dir, "cover.jpg"), body);
    }
    process.chdir(tmp);

    const call = (ma: string) =>
      GET(new Request(`https://example.invalid/products/${ma}/cover.jpg`), {
        params: Promise.resolve({ ma, file: "cover.jpg" }),
      });

    const blocked = [
      held,
      held.toLowerCase(),
      padded,
      padded.toLowerCase(),
    ];
    for (const ma of blocked) {
      const response = await call(ma);
      assert.equal(response.status, 404, ma);
      assert.equal(await response.text(), "Not found", ma);
      assert.match(response.headers.get("cache-control") ?? "", /no-store/, ma);
    }

    const open = await call(live.toLowerCase());
    assert.equal(open.status, 200);
    assert.equal(open.headers.get("content-type"), "image/jpeg");
    assert.equal(Buffer.from(await open.arrayBuffer()).toString(), bytes.live);
  } finally {
    process.chdir(cwd);
    fs.rmSync(tmp, { recursive: true, force: true });
  }
});
