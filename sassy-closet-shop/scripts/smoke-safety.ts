import { readdirSync, readFileSync, statSync } from "node:fs";
import path from "node:path";
import { PUBLIC_FORBIDDEN_PHRASES, customerStockVoiceHit } from "../lib/public-safety";

const ROOTS = ["app/(shop)", "components", "lib/trust-copy.ts", "lib/seo.ts", "lib/dropship-copy.ts", "lib/site.ts", "lib/shop-look.ts", "lib/share-card.ts"];
const SKIP_DIR = new Set(["admin-colors.tsx"]);
const SKIP_FILE = new Set([
  "admin-colors.tsx",
  "admin-entry.tsx",
  "product-status-badge.tsx",
]);

function fail(message: string): never {
  throw new Error(message);
}

function walk(rel: string, acc: string[]): void {
  const full = path.join(process.cwd(), rel);
  const stat = statSync(full);
  if (stat.isDirectory()) {
    for (const name of readdirSync(full)) {
      if (name.startsWith("admin")) {
        continue;
      }
      walk(path.join(rel, name), acc);
    }
    return;
  }
  if (!/\.(ts|tsx)$/.test(rel)) {
    return;
  }
  if (SKIP_FILE.has(path.basename(rel)) || SKIP_DIR.has(path.basename(rel))) {
    return;
  }
  acc.push(rel);
}

const files: string[] = [];
for (const root of ROOTS) {
  walk(root, files);
}

for (const rel of files) {
  const text = readFileSync(path.join(process.cwd(), rel), "utf8");
  for (const phrase of PUBLIC_FORBIDDEN_PHRASES) {
    if (text.includes(phrase)) {
      fail(`${rel} leaks forbidden public copy: ${phrase}`);
    }
  }
  const stock = customerStockVoiceHit(text);
  if (stock) {
    fail(`${rel} surfaces customer availability copy: ${stock}`);
  }
  if (text.includes("hub-source-links") || text.includes("HUB_SOURCE_LINKS")) {
    fail(`${rel} must not import staff Taobao links`);
  }
}

if (files.length < 8) {
  fail("Safety scan found too few shop files");
}

console.log("public safety ok", { files: files.length });
