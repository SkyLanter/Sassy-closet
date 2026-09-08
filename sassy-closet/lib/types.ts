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
