type NamedLook = {
  ma: string;
  titleEn: string;
  titleVn: string;
  descriptionEn?: string;
  descriptionVn?: string;
};

export function displayName(product: NamedLook): string {
  return (product.titleEn.trim() || product.titleVn.trim() || product.ma).toUpperCase();
}

export function displayTitle(product: NamedLook): string {
  return `${product.ma}. ${displayName(product)}`;
}

/** English product copy for metadata and the primary description. */
export function displayDescription(product: NamedLook): string {
  return (product.descriptionEn ?? "").trim() || (product.descriptionVn ?? "").trim();
}

/** Optional short Vietnamese flavor line. Never used for nav, CTAs, or metadata. */
export function flavorVn(product: NamedLook): string | null {
  const vn = (product.descriptionVn ?? "").trim();
  const en = (product.descriptionEn ?? "").trim();
  if (!vn || vn === en) {
    return null;
  }
  return vn;
}
