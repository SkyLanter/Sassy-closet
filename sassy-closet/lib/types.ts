import type { KindCode } from "./kinds";

export type Piece = {
  id: string;
  photos: number[];
  suggested: string[];
  color: string;
  note: string;
};

export type Submission = {
  id: number;
  ma: string;
  kind: KindCode;
  size: string;
  color: string;
  color_note: string;
  pieces: Piece[];
  link: string;
  price: string;
  cost_cny: string;
  cost_usd: string;
  cost_currency: string;
  sell_cny: string;
  sell_usd: string;
  sell_currency: string;
  blurb: string;
  photo_paths: string[];
  photo_hashes: string[];
  status: "staged";
  square: "not_square";
  created_at: string;
  updated_at: string;
  caption_vi: string;
  caption_en: string;
  blurb_suggested: string;
  photo_link: string;
};

export type AskStatus = "waiting" | "ready" | "error";

export type AskRecord = {
  id: string;
  question: string;
  status: AskStatus;
  answer: string;
  copies: AskCopy[];
  source: "relay" | "local";
  offline: boolean;
  created_at: string;
  updated_at: string;
};

export type AskCopy = {
  id: string;
  label: string;
  text: string;
};

export type TabId = "create" | "edit" | "find" | "ask";

export const ON_HAND_STATUSES = ["on_hand", "reserved", "sold", "dead"] as const;

export type OnHandStatus = (typeof ON_HAND_STATUSES)[number];

export type OnHandRow = {
  size: string;
  color: string;
  qty_on_hand: number | null;
  status: OnHandStatus | "";
  storage_location: string;
  notes: string;
  where_stored: string;
};

export type MaStaged = {
  ma: string;
  kind: KindCode;
  kind_label: string;
  colors: string;
  sizes: string;
  cost_usd: string;
  cost_cny: string;
  sell_usd: string;
  sell_cny: string;
  source_link: string;
  notes: string;
  color_note: string;
  blurb: string;
  photo_paths: string[];
  photo_link: string;
  status: Submission["status"];
  square: Submission["square"];
  created_at: string;
  updated_at: string;
};

export type MaLookup = {
  code: string;
  staged: MaStaged;
  on_hand: OnHandRow[];
  staged_only: boolean;
};
