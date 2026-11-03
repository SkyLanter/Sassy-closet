/**
 * Compare mã + price pairs embedded in two shop HTML responses.
 * Does not write the catalog. Prints a unified diff. Exit 1 when they differ.
 *
 *   node scripts/diff-shop-prices.mjs https://sassy-closet-shop.vercel.app https://preview.example
 */
const leftUrl = process.argv[2];
const rightUrl = process.argv[3];

if (!leftUrl || !rightUrl) {
  console.error("Usage: node scripts/diff-shop-prices.mjs <production-url> <preview-url>");
  process.exit(2);
}

function readPrice(chunk) {
  const match = chunk.match(/priceUsd\\?":(null|-?\d+(?:\.\d+)?)/);
  if (!match) {
    return undefined;
  }
  return match[1] === "null" ? null : Number(match[1]);
}

function pairsFromHtml(html) {
  const found = new Map();
  const re = /\\?"ma\\?":\\?"([A-Z][0-9]{1,3})\\?"/g;
  for (const match of html.matchAll(re)) {
    const ma = match[1];
    if (found.has(ma)) {
      continue;
    }
    const chunk = html.slice(match.index, match.index + 700);
    const price = readPrice(chunk);
    if (price !== undefined) {
      found.set(ma, price);
    }
  }
  return found;
}

async function load(url) {
  const response = await fetch(url, { redirect: "follow" });
  if (!response.ok) {
    throw new Error(`${url} returned ${response.status}`);
  }
  const html = await response.text();
  return pairsFromHtml(html);
}

const [left, right] = await Promise.all([load(leftUrl), load(rightUrl)]);
const mas = [...new Set([...left.keys(), ...right.keys()])].sort();
const lines = [];
let diffs = 0;

for (const ma of mas) {
  const a = left.has(ma) ? left.get(ma) : "missing";
  const b = right.has(ma) ? right.get(ma) : "missing";
  const same = a === b;
  if (!same) {
    diffs += 1;
  }
  lines.push(`${same ? " " : "!"} ${ma}  production=${a}  preview=${b}`);
}

console.log(`production ${leftUrl}  ${left.size} mãs`);
console.log(`preview    ${rightUrl}  ${right.size} mãs`);
console.log(lines.join("\n"));
console.log(diffs === 0 ? "prices match" : `${diffs} price or mã differences`);
process.exit(diffs === 0 ? 0 : 1);
