import type { AsiaSizeLetter, FitCm, ShopSize } from "./asia-size";
import type { Fulfillment } from "./fulfillment";
import type { MaLetter } from "./ma";

export type { AsiaSizeLetter, FitCm, Fulfillment, ShopSize };

export type ProductStatus = "available" | "hold" | "sold";

export type ProductColor = {
  id: string;
  hex: string;
  name: string;
  note: string;
};

export type ProductImageAsset = {
  src: string;
  colorId: string | null;
  order: number;
};

export type Product = {
  ma: string;
  type: MaLetter;
  titleVn: string;
  titleEn: string;
  priceUsd: number | null;
  qty: 1;
  status: ProductStatus;
  colors: ProductColor[];
  images: ProductImageAsset[];
  sizes: ShopSize[];
  fitCm: FitCm;
  descriptionVn: string;
  descriptionEn: string;
  fulfillment: Fulfillment;
  sourceLink: string | null;
  /** Optional Meta popular rank overlay — not persisted in catalog Blob. */
  fbRank?: number;
  fbViews?: number;
  fbEngagement?: number;
  fbPosts?: number;
};

export type SiteSettings = {
  announcementLines: string[];
  facebookPageUrl: string;
};

export type CatalogDocument = {
  schema: "catalog.v1";
  version: 1;
  siteId: string;
  products: Product[];
  settings: SiteSettings;
  updatedAt?: string;
};
