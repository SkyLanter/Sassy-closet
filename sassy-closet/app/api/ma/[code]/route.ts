import { NextResponse } from "next/server";
import { lookupMaCard } from "@/lib/ma-card";
import { withSharedStore } from "@/lib/with-shared";

export async function GET(
  _request: Request,
  context: { params: Promise<{ code: string }> },
) {
  const { code } = await context.params;
  const card = await withSharedStore(
    () => lookupMaCard(decodeURIComponent(code ?? "")),
    "read",
  );
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
