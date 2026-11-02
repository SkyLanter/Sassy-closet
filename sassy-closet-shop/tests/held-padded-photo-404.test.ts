import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import test from "node:test";
import { GET } from "../app/products/[ma]/[file]/route";
import { HELD_INCOMPLETE_MAS, isOffLiveSell } from "../lib/held-incomplete";

function padMa(ma: string, zeros: number): string {
  return `${ma[0]}${"0".repeat(zeros)}${ma.slice(1)}`;
}

test("held photo URLs 404 for other mãs, extra zeros, and photo files when the file is on disk", async () => {
  const heldCodes = [HELD_INCOMPLETE_MAS[0], HELD_INCOMPLETE_MAS[1]];
  assert.equal(heldCodes.length, 2);
  for (const held of heldCodes) {
    assert.ok(held);
    assert.match(held, /^[A-Z]\d{2}$/);
  }
  assert.notEqual(heldCodes[0]![0], heldCodes[1]![0]);

  const live = "Q02";
  assert.equal(isOffLiveSell(live), false);
  const files = ["cover.jpg", "photo-1.jpg"] as const;
  const spellings = heldCodes.flatMap((held) => {
    const code = held!;
    return [code, code.toLowerCase(), padMa(code, 1), padMa(code, 1).toLowerCase(), padMa(code, 2), padMa(code, 2).toLowerCase()];
  });
  for (const spelling of spellings) {
    assert.equal(isOffLiveSell(spelling), true, spelling);
  }

  const tmp = fs.mkdtempSync(path.join(os.tmpdir(), "shop-held-photo-"));
  const cwd = process.cwd();
  const liveBytes = {
    "cover.jpg": `live-${live}-cover`,
    "photo-1.jpg": `live-${live}-photo`,
  };
  try {
    const write = (ma: string, file: string, body: string) => {
      const dir = path.join(tmp, "public", "products", ma);
      fs.mkdirSync(dir, { recursive: true });
      fs.writeFileSync(path.join(dir, file), body);
    };
    for (const spelling of spellings) {
      for (const file of files) {
        write(spelling, file, `held-${spelling}-${file}`);
      }
    }
    for (const file of files) {
      write(live, file, liveBytes[file]);
    }
    process.chdir(tmp);

    const call = (ma: string, file: string) =>
      GET(new Request(`https://example.invalid/products/${ma}/${file}`), {
        params: Promise.resolve({ ma, file }),
      });

    for (const spelling of spellings) {
      for (const file of files) {
        const response = await call(spelling, file);
        const label = `${spelling}/${file}`;
        assert.equal(response.status, 404, label);
        assert.equal(await response.text(), "Not found", label);
        assert.match(response.headers.get("cache-control") ?? "", /no-store/, label);
      }
    }

    for (const file of files) {
      const response = await call(live.toLowerCase(), file);
      assert.equal(response.status, 200, file);
      assert.equal(response.headers.get("content-type"), "image/jpeg", file);
      assert.equal(Buffer.from(await response.arrayBuffer()).toString(), liveBytes[file], file);
    }
  } finally {
    process.chdir(cwd);
    fs.rmSync(tmp, { recursive: true, force: true });
  }
});
