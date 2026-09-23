import type { Metadata } from "next";
import { categoryCopy, categorySlug } from "@/lib/categories";
import { coverSrc } from "@/lib/product-media";
import { SITE } from "@/lib/site";
import { siteMode } from "@/lib/site-runtime";
import { resolvableShopOrigin } from "@/lib/shop-origin";
import {
  categoryShareDescription,
  HOME_DESCRIPTION,
  HOME_OG_TITLE,
  HOME_TITLE,
  productOgAlt,
  productShareDescription,
  productShareTitle,
} from "@/lib/trust-copy";
import type { MaLetter } from "@/lib/ma";
import type { ShopLook } from "@/lib/shop-look";

export function shopRobots(): Metadata["robots"] {
  return siteMode() === "official"
    ? { index: true, follow: true }
    : { index: false, follow: false };
}

export function shopOrigin(): string {
  return resolvableShopOrigin();
}

export function shopCanonical(path = "/"): string | undefined {
  const origin = shopOrigin();
  if (!origin) {
    return undefined;
  }
  if (path === "/") {
    return origin;
  }
  return `${origin}${path.startsWith("/") ? path : `/${path}`}`;
}

export function absoluteMedia(src: string): string {
  if (src.startsWith("http://") || src.startsWith("https://")) {
    return src;
  }
  const origin = shopOrigin();
  if (!origin) {
    return src;
  }
  return `${origin}${src.startsWith("/") ? src : `/${src}`}`;
}

function shareImage(path: string, alt: string): NonNullable<Metadata["openGraph"]>["images"] {
  return [
    {
      url: shopCanonical(path) ?? path,
      width: 1200,
      height: 630,
      alt,
    },
  ];
}

export function rootSeo(): Metadata {
  const origin = shopOrigin();
  const canonical = shopCanonical("/");
  const images = shareImage("/opengraph-image", "Sassy Closet lookbook");
  return {
    metadataBase: origin ? new URL(origin) : undefined,
    title: {
      default: HOME_TITLE,
      template: `%s · ${SITE.name}`,
    },
    description: HOME_DESCRIPTION,
    robots: shopRobots(),
    alternates: canonical ? { canonical } : undefined,
    openGraph: {
      type: "website",
      locale: "en_US",
      siteName: SITE.name,
      title: HOME_OG_TITLE,
      description: HOME_DESCRIPTION,
      url: canonical,
      images,
    },
    twitter: {
      card: "summary_large_image",
      title: HOME_OG_TITLE,
      description: HOME_DESCRIPTION,
      images: images,
    },
    appleWebApp: {
      statusBarStyle: "black-translucent",
      title: SITE.name,
    },
    other: {
      "format-detection": "telephone=no, date=no, address=no, email=no",
    },
  };
}

export function productSeo(product: ShopLook): Metadata {
  const title = productShareTitle(product);
  const description = productShareDescription(product);
  const canonical = shopCanonical(`/m/${product.ma}`);
  const images = shareImage(`/share/m/${product.ma}`, productOgAlt(product));
  return {
    title,
    description,
    robots: shopRobots(),
    alternates: canonical ? { canonical } : undefined,
    openGraph: {
      type: "website",
      locale: "en_US",
      siteName: SITE.name,
      title,
      description,
      url: canonical,
      images,
    },
    twitter: {
      card: "summary_large_image",
      title,
      description,
      images,
    },
  };
}

export function categorySeo(type: MaLetter): Metadata {
  const { label } = categoryCopy(type);
  const slug = categorySlug(type);
  const description = categoryShareDescription(type);
  const canonical = shopCanonical(`/c/${slug}`);
  const ogTitle = `${label} · ${SITE.name}`;
  const images = shareImage(`/share/c/${slug}`, ogTitle);
  return {
    title: label,
    description,
    robots: shopRobots(),
    alternates: canonical ? { canonical } : undefined,
    openGraph: {
      type: "website",
      locale: "en_US",
      siteName: SITE.name,
      title: ogTitle,
      description,
      url: canonical,
      images,
    },
    twitter: {
      card: "summary_large_image",
      title: ogTitle,
      description,
      images,
    },
  };
}

export function trustPageSeo(title: string, description: string, path: string): Metadata {
  const canonical = shopCanonical(path);
  const images = shareImage("/opengraph-image", `${title} · ${SITE.name}`);
  return {
    title,
    description,
    robots: shopRobots(),
    alternates: canonical ? { canonical } : undefined,
    openGraph: {
      type: "website",
      locale: "en_US",
      siteName: SITE.name,
      title,
      description,
      url: canonical,
      images,
    },
    twitter: {
      card: "summary_large_image",
      title,
      description,
      images,
    },
  };
}

export function categoryJsonLd(
  label: string,
  slug: string,
  products: ShopLook[],
): Record<string, unknown> {
  const canonical = shopCanonical(`/c/${slug}`);
  const itemListElement = products.map((product, index) => {
    const item: Record<string, unknown> = {
      "@type": "ListItem",
      position: index + 1,
      name: productShareTitle(product),
    };
    const url = shopCanonical(`/m/${product.ma}`);
    if (url) {
      item.url = url;
    }
    return item;
  });
  const jsonLd: Record<string, unknown> = {
    "@context": "https://schema.org",
    "@type": "ItemList",
    name: `${label} · ${SITE.name}`,
    numberOfItems: products.length,
    itemListElement,
  };
  if (canonical) {
    jsonLd.url = canonical;
  }
  return jsonLd;
}

export function productJsonLd(product: ShopLook): Record<string, unknown> {
  const canonical = shopCanonical(`/m/${product.ma}`);
  const cover = coverSrc(product);
  const offer: Record<string, unknown> = {
    "@type": "Offer",
    url: canonical,
  };
  if (product.priceUsd !== null) {
    offer.priceCurrency = "USD";
    offer.price = product.priceUsd.toFixed(2);
  }
  const jsonLd: Record<string, unknown> = {
    "@context": "https://schema.org",
    "@type": "Product",
    name: productShareTitle(product),
    description: productShareDescription(product),
    sku: product.ma,
    inLanguage: "en",
    brand: {
      "@type": "Brand",
      name: SITE.name,
    },
    image: cover ? [absoluteMedia(cover)] : undefined,
    offers: offer,
  };
  if (canonical) {
    jsonLd.url = canonical;
  }
  return jsonLd;
}

export function organizationJsonLd(facebookPageUrl: string): Record<string, unknown> {
  const canonical = shopCanonical("/");
  const jsonLd: Record<string, unknown> = {
    "@context": "https://schema.org",
    "@type": "Organization",
    name: SITE.name,
    sameAs: [facebookPageUrl],
  };
  if (canonical) {
    jsonLd.url = canonical;
  }
  const logo = shopCanonical("/opengraph-image");
  if (logo) {
    jsonLd.logo = logo;
  }
  return jsonLd;
}
