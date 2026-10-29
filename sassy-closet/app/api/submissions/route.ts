import { NextResponse } from "next/server";
import { requireShopAdmin } from "@/lib/shop-admin-http";
import { saveFromForm } from "@/lib/form-save";
import { intakeCatalog } from "@/lib/kinds";
import { scheduleNewMaWebhookFromRow } from "@/lib/newMaWebhook";
import { listSubmissions, storeHealth } from "@/lib/store";
import { storeUnavailableResponse } from "@/lib/store-unavailable";

// Rows carry costs + source links: admin session required (piece 240b).
export async function GET(request: Request) {
  const denied = await requireShopAdmin(request);
  if (denied) return denied;
  let submissions;
  try {
    submissions = await listSubmissions();
  } catch (error) {
    return storeUnavailableResponse(error);
  }
  return NextResponse.json({
    submissions,
    storage: storeHealth(),
    catalog: intakeCatalog(),
  });
}

export async function POST(request: Request) {
  const denied = await requireShopAdmin(request);
  if (denied) return denied;
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
