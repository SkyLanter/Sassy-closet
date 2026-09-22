import { TYPE_LABELS } from "@/lib/catalog";
import { categoryFromSlug } from "@/lib/categories";

export function lookCountLabel(count: number, more = false): string {
  const noun = count === 1 ? "look" : "looks";
  if (more) {
    return `${count} ${noun} nữa · ${count} more ${noun}`;
  }
  return `${count} ${noun}`;
}

export const FEATURED_ALL_ARIA = "Tất cả · All";

export function collectionEmptyCopy(label: string, slug?: string): { title: string; body: string } {
  if (slug === "quan") {
    return {
      title: label,
      body: "Chưa có quần trên lookbook · No pants listed.",
    };
  }
  const type = slug ? categoryFromSlug(slug) : null;
  if (type) {
    const vn = TYPE_LABELS[type].vn.toLocaleLowerCase("vi");
    return {
      title: label,
      body: `Chưa có ${vn} trên lookbook · No ${label.toLowerCase()} listed.`,
    };
  }
  return {
    title: label,
    body: "Chưa có bộ sưu tập trên lookbook · No collections listed.",
  };
}
