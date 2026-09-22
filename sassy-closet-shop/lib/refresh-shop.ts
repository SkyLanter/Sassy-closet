import { revalidatePath, revalidateTag } from "next/cache";
import { after } from "next/server";
import { KNOWN_SEED_MAS } from "@/lib/catalog-contract";
import { TYPE_SLUGS } from "@/lib/categories";
import { CATALOG_CACHE_TAG } from "@/lib/catalog-tag";
import { MA_LETTERS, maLetter, normalizeMa } from "@/lib/ma";

function uniqueMas(mas: string[]): string[] {
  const seen = new Set<string>();
  const out: string[] = [];
  for (const raw of mas) {
    const ma = normalizeMa(raw);
    if (!ma || seen.has(ma)) {
      continue;
    }
    seen.add(ma);
    out.push(ma);
  }
  return out;
}

function categoryPathForMa(ma: string): string | null {
  const letter = maLetter(ma);
  if (!letter) {
    return null;
  }
  return `/c/${TYPE_SLUGS[letter]}`;
}

export function publicPathsForMas(mas: string[]): string[] {
  const paths = new Set<string>(["/", "/how-to-buy", "/meetup-ship"]);
  for (const ma of uniqueMas(mas)) {
    const category = categoryPathForMa(ma);
    if (category) {
      paths.add(category);
    }
    paths.add(`/m/${ma}`);
    paths.add(`/share/m/${ma}`);
  }
  return [...paths];
}

function shopWarmOrigin(): string | null {
  const configured =
    process.env.NEXT_PUBLIC_SHOP_URL?.trim() ||
    process.env.SHOP_ORIGIN?.trim() ||
    process.env.SHOP_WARM_ORIGIN?.trim();
  if (configured) {
    return configured.replace(/\/$/, "");
  }
  const vercel = process.env.VERCEL_PROJECT_PRODUCTION_URL?.trim() || process.env.VERCEL_URL?.trim();
  if (vercel) {
    return vercel.startsWith("http") ? vercel.replace(/\/$/, "") : `https://${vercel.replace(/\/$/, "")}`;
  }
  if (process.env.VERCEL !== "1") {
    return "http://127.0.0.1:43147";
  }
  return null;
}

/** Two public warms so the first ISR STALE does not keep a wrong price. */
export async function warmShopPaths(paths: string[]): Promise<void> {
  const origin = shopWarmOrigin();
  if (!origin) {
    return;
  }
  const publicPaths = paths.filter(
    (path) =>
      path === "/" ||
      path === "/how-to-buy" ||
      path === "/meetup-ship" ||
      path.startsWith("/m/") ||
      path.startsWith("/c/"),
  );
  for (let round = 0; round < 2; round += 1) {
    await Promise.all(
      publicPaths.map(async (path) => {
        try {
          await fetch(`${origin}${path}`, {
            cache: "no-store",
            headers: {
              "User-Agent": "SassyCloset-Warm/1.0",
              "Cache-Control": "no-cache",
              Pragma: "no-cache",
            },
          });
        } catch {
          // Warm is best-effort — receipt still requires revalidatePath to have run.
        }
      }),
    );
  }
}

function markShopStale(targets: string[]): void {
  revalidateTag(CATALOG_CACHE_TAG, "max");
  revalidatePath("/", "layout");
  revalidatePath("/", "page");
  revalidatePath("/c/[slug]", "page");
  revalidatePath("/m/[ma]", "page");
  revalidatePath("/share/m/[ma]");
  revalidatePath("/share/c/[slug]");
  revalidatePath("/how-to-buy");
  revalidatePath("/meetup-ship");
  revalidatePath("/c", "layout");
  revalidatePath("/m", "layout");
  for (const letter of MA_LETTERS) {
    revalidatePath(`/c/${TYPE_SLUGS[letter]}`, "page");
  }
  for (const ma of new Set([...targets, ...KNOWN_SEED_MAS])) {
    revalidatePath(`/m/${ma}`, "page");
  }
}

function markAdminStale(targets: string[]): void {
  revalidatePath("/admin", "layout");
  revalidatePath("/admin", "page");
  revalidatePath("/admin/new");
  revalidatePath("/admin/settings");
  revalidatePath("/api/admin/catalog");
  revalidatePath("/api/admin/add");
  revalidatePath("/api/admin/revalidate");
  revalidatePath("/api/admin/save");
  revalidatePath("/api/admin/rename");
  revalidatePath("/api/admin/remove");
  revalidatePath("/api/admin/settings");
  revalidatePath("/api/admin/hold");
  revalidatePath("/api/admin/catalog/import");
  for (const ma of new Set([...targets, ...KNOWN_SEED_MAS])) {
    revalidatePath(`/admin/edit/${ma}`);
  }
}

function runAfterResponse(task: () => Promise<void> | void): void {
  const run = () => {
    void Promise.resolve(task()).catch((error) => {
      console.error("Post-save shop follow-up failed.", error);
    });
  };
  try {
    after(run);
  } catch {
    run();
  }
}

/**
 * Drop shop views of the live catalog after a write.
 * Admin / current-page revalidate + warm run AFTER the response so a Server
 * Action on /admin/new cannot die behind RSC #441.
 * Dynamic segments must pass `"page"` — `revalidatePath("/m/[ma]")` alone is a miss.
 */
export async function refreshShop(...mas: string[]): Promise<string[]> {
  const targets = uniqueMas(mas.length > 0 ? mas : [...KNOWN_SEED_MAS]);
  const publicPaths = publicPathsForMas(targets);
  try {
    markShopStale(targets);
  } catch (error) {
    console.error("Shop revalidate after write failed.", error);
  }
  runAfterResponse(async () => {
    try {
      markAdminStale(targets);
    } catch (error) {
      console.error("Admin revalidate after write failed.", error);
    }
    await warmShopPaths(publicPaths);
  });
  return publicPaths;
}
