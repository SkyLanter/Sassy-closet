import { NextResponse } from "next/server";
import { lookupMaCard } from "@/lib/ma-card";
import { requireShopAdmin } from "@/lib/shop-admin-http";

export const dynamic = "force-dynamic";

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
    return NextResponse.json({ error: "Không tìm thấy mã" }, { status: 404 });
  }
  return NextResponse.json({
    code: card.code,
    staged: card.staged,
    on_hand: card.on_hand,
    staged_only: card.staged_only,
  });
}
