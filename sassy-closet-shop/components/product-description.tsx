import { displayDescription, flavorVn } from "@/lib/copy";
import type { ShopLook } from "@/lib/shop-look";

export function ProductDescription({ product }: { product: ShopLook }) {
  const english = displayDescription(product);
  const vietnamese = flavorVn(product);
  if (!english && !vietnamese) {
    return null;
  }

  return (
    <div className="mt-5 max-w-prose space-y-2">
      {english ? (
        <p className="text-[13px] leading-relaxed text-pretty text-muted [orphans:2] [widows:2]" translate="no">{english}</p>
      ) : null}
      {vietnamese ? (
        <p lang="vi" className="text-[13px] leading-relaxed text-pretty text-muted [orphans:2] [widows:2]" translate="no">
          {vietnamese}
        </p>
      ) : null}
    </div>
  );
}
