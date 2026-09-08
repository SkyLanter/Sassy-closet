import { hydrateSharedStore, persistSharedStore } from "./shared-persist";

export async function withSharedStore<T>(
  fn: () => T | Promise<T>,
  mode: "read" | "write",
): Promise<T> {
  await hydrateSharedStore();
  const result = await fn();
  if (mode === "write") await persistSharedStore();
  return result;
}
