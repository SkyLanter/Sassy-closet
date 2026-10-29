import { requireShopAdmin, shopAdminJson } from "@/lib/shop-admin-http";
import { lookupMaCard } from "@/lib/ma-card";

export async function GET(
  request: Request,
  context: { params: Promise<{ code: string }> },
) {
  const denied = await requireShopAdmin(request);
  if (denied) {
    return denied;
  }
  const { code } = await context.params;
  const card = await lookupMaCard(decodeURIComponent(code ?? ""));
  if (!card) {
    return shopAdminJson({ error: "Không tìm thấy mã" }, 404);
  }
  return shopAdminJson({
    code: card.code,
    staged: card.staged,
    on_hand: card.on_hand,
    staged_only: card.staged_only,
  });
}
