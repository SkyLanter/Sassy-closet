import { NextResponse } from "next/server";
import { saveFromForm } from "@/lib/form-save";
import { intakeCatalog } from "@/lib/kinds";
import { scheduleNewMaWebhookFromRow } from "@/lib/newMaWebhook";
import { requireShopAdmin, shopAdminJson } from "@/lib/shop-admin-http";
import { listSubmissions, storeHealth } from "@/lib/store";

export async function GET(request: Request) {
  const denied = await requireShopAdmin(request);
  if (denied) {
    return denied;
  }
  return shopAdminJson({
    submissions: await listSubmissions(),
    storage: storeHealth(),
    catalog: intakeCatalog(),
  });
}

export async function POST(request: Request) {
  try {
    const form = await request.formData();
    const submission = await saveFromForm(form);
    scheduleNewMaWebhookFromRow("create", submission);
    return NextResponse.json({ submission });
  } catch (error) {
    const status = (error as { status?: number }).status ?? 400;
    return NextResponse.json(
      { error: error instanceof Error ? error.message : "Chưa lưu được, thử lại nha." },
      { status },
    );
  }
}
