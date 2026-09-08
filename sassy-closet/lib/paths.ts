import fs from "node:fs";
import path from "node:path";

export function dataRoot(): string {
  if (process.env.SASSY_DATA_DIR) return process.env.SASSY_DATA_DIR;
  if (process.env.VERCEL) return path.join("/tmp", "sassy-closet-data");
  return path.join(process.cwd(), "data");
}

export function ensureDataDirs(): string {
  const root = dataRoot();
  fs.mkdirSync(path.join(root, "photos"), { recursive: true });
  return root;
}
