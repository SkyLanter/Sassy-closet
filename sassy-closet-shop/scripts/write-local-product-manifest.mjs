import { readdirSync, writeFileSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const productsDir = path.join(root, "public", "products");
const entries = [];

for (const ma of readdirSync(productsDir, { withFileTypes: true })) {
  if (!ma.isDirectory() || ma.name.startsWith(".")) {
    continue;
  }
  const folder = path.join(productsDir, ma.name);
  for (const file of readdirSync(folder, { withFileTypes: true })) {
    if (!file.isFile() || file.name.startsWith(".")) {
      continue;
    }
    entries.push(`${ma.name}/${file.name}`);
  }
}

entries.sort((left, right) => left.localeCompare(right));
writeFileSync(path.join(root, "data", "local-product-files.json"), `${JSON.stringify(entries, null, 2)}\n`);
