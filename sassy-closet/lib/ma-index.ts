import type { Submission } from "./types";

/**
 * Public mã list for the auto-list runner.
 * Whitelist only: identity fields. Money, supplier links, captions, and notes stay off.
 */
export type MaIndexItem = {
  ma: string;
  kind: Submission["kind"];
  size: string;
  color: string;
  status: Submission["status"];
  photo_count: number;
  created_at: string;
  updated_at: string;
};

export const MA_INDEX_KEYS = [
  "ma",
  "kind",
  "size",
  "color",
  "status",
  "photo_count",
  "created_at",
  "updated_at",
] as const;

export function toMaIndexItem(row: Submission): MaIndexItem {
  const photos = Array.isArray(row.photo_paths) ? row.photo_paths.length : 0;
  return {
    ma: row.ma,
    kind: row.kind,
    size: row.size,
    color: row.color,
    status: row.status,
    photo_count: photos,
    created_at: row.created_at,
    updated_at: row.updated_at,
  };
}

export function maIndexPayload(rows: readonly Submission[]): { items: MaIndexItem[] } {
  return { items: rows.map(toMaIndexItem) };
}
