import { NextResponse } from "next/server";
import { requireShopAdmin } from "@/lib/shop-admin-http";
import { lookupMaCard } from "@/lib/ma-card";
import { storeUnavailableResponse } from "@/lib/store-unavailable";

export async function GET(
  request: Request,
  context: { params: Promise<{ code: string }> },
) {
  const denied = await requireShopAdmin(request);
  if (denied) return denied;
  const { code } = await context.params;
  let decoded = code ?? "";
  try {
    decoded = decodeURIComponent(decoded);
  } catch {
    // Next already decoded the param; a literal "%" stays as-is (lookup miss → 404).
  }
  let card;
  try {
    card = await lookupMaCard(decoded);
  } catch (error) {
    return storeUnavailableResponse(error);
  }
  if (!card) {
    return NextResponse.json({ error: "Không tìm thấy mã" }, { status: 404 });
  }
  return NextResponse.json({
    code: card.code,
    staged: card.staged,
    on_hand: card.on_hand,
    staged_only: card.staged_only,
  });
}
