import { kindLabel } from "./kinds";
import { normalizeFindCode, photoFolder } from "./on-hand";
import { getOnHandRows, getSubmission } from "./store";
import type { MaLookup, MaStaged, OnHandRow, Submission } from "./types";

export function lookupMaCard(raw: string): MaLookup | null {
  const code = normalizeFindCode(raw);
  if (!code) return null;
  const submission = getSubmission(code);
  if (!submission) return null;
  return buildMaLookup(submission, getOnHandRows(submission.ma));
}

export function buildMaLookup(submission: Submission, onHand: OnHandRow[]): MaLookup {
  return {
    code: submission.ma,
    staged: stagedFromSubmission(submission),
    on_hand: onHand,
    staged_only: onHand.length === 0,
  };
}

export function stagedFromSubmission(item: Submission): MaStaged {
  const photo_link = item.photo_link.trim() || photoFolder(item.ma);
  return {
    ma: item.ma,
    kind: item.kind,
    kind_label: kindLabel(item.kind),
    colors: item.color,
    sizes: item.size,
    cost_usd: item.cost_usd,
    cost_cny: item.cost_cny,
    sell_usd: item.sell_usd,
    sell_cny: item.sell_cny,
    source_link: item.link,
    notes: item.color_note,
    color_note: item.color_note,
    blurb: item.blurb,
    photo_paths: item.photo_paths ?? [],
    photo_link,
    status: item.status,
    square: item.square,
    created_at: item.created_at,
    updated_at: item.updated_at,
  };
}
