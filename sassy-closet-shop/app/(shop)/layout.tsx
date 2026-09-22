import type { ReactNode } from "react";
import { headers } from "next/headers";
import { AdminEntryProvider } from "@/components/admin-entry";
import { AnnouncementBar } from "@/components/announcement-bar";
import { CatalogMediaVersionProvider } from "@/components/catalog-media-version";
import { Footer } from "@/components/footer";
import { Header } from "@/components/header";
import { MessengerDeviceProvider } from "@/components/messenger-device";
import { ShopPdpScroll } from "@/components/shop-pdp-scroll";
import { ShopSearchProvider } from "@/components/shop-search";
import { SiteSettingsProvider } from "@/components/site-settings";
import { SkipToLooks } from "@/components/skip-to-looks";
import { catalogShaOf } from "@/lib/catalog-sha";
import { decodeShopSearchHeader, SHOP_SEARCH_HEADER, toLookSearchItems } from "@/lib/look-search";
import { isMessengerAppDevice } from "@/lib/messenger";
import { getCatalogDocument, getCatalogTypes } from "@/lib/products";
import { shopVisibleLooks } from "@/lib/site-settings";

export const dynamic = "force-dynamic";
export const revalidate = 0;

export default async function ShopLayout({ children }: { children: ReactNode }) {
  const types = await getCatalogTypes();
  const document = await getCatalogDocument();
  const looks = toLookSearchItems(shopVisibleLooks(document.products));
  const settings = document.settings;
  const mediaVersion = document.updatedAt ?? catalogShaOf(document);
  const requestHeaders = await headers();
  const isAppDevice = isMessengerAppDevice(
    requestHeaders.get("user-agent") ?? "",
    0,
    requestHeaders.get("sec-ch-ua-mobile") ?? "",
  );

  return (
    <SiteSettingsProvider settings={settings}>
      <MessengerDeviceProvider isAppDevice={isAppDevice}>
      <CatalogMediaVersionProvider version={mediaVersion}>
        <AdminEntryProvider>
        <ShopSearchProvider
          looks={looks}
          initialQuery={decodeShopSearchHeader(requestHeaders.get(SHOP_SEARCH_HEADER))}
        >
        <SkipToLooks />
        <ShopPdpScroll />
        <div className="relative sticky top-0 z-50" data-testid="shop-chrome">
          <AnnouncementBar lines={settings.announcementLines} />
          <Header types={types} />
        </div>
        <main
          id="main"
          tabIndex={-1}
          className="flex-1 scroll-mt-[calc(env(safe-area-inset-top,0px)+8.25rem)] outline-none sm:scroll-mt-[calc(env(safe-area-inset-top,0px)+8.75rem)]"
        >
          {children}
        </main>
        <Footer />
        </ShopSearchProvider>
        </AdminEntryProvider>
      </CatalogMediaVersionProvider>
      </MessengerDeviceProvider>
    </SiteSettingsProvider>
  );
}
