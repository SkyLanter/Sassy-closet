import { NextResponse } from "next/server";
import { fetchTaobaoItem } from "@/lib/taobao";

/**
 * POST /api/taobao-lookup
 * Body: { link: string }
 *
 * Server-side Taobao listing fetch. The browser never fetches Taobao
 * directly (it usually blocks automated requests). Returns the seller
 * SKU colors (Chinese, seller truth), size axes, list ¥ (with a promo
 * note when found), and gallery photos — or a graceful blocked result.
 * Never invents data: fields that are not found are null/empty.
 */
export async function POST(request: Request) {
  let link = "";
  try {
    const body = (await request.json()) as { link?: string };
    link = String(body.link ?? "");
  } catch {
    link = "";
  }
  const result = await fetchTaobaoItem(link);
  if (!result.ok) {
    return NextResponse.json(
      { ok: false, blocked: true, reason: result.reason },
      { status: 200 },
    );
  }
  return NextResponse.json({
    ok: true,
    fetched_at: result.fetchedAt,
    item: result.item,
  });
}
