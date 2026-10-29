import { NextResponse } from "next/server";
import { requireShopAdmin } from "@/lib/shop-admin-http";
import { saveFromForm } from "@/lib/form-save";
import { intakeDirectJson, withIntakeDirectLinkHeaders } from "@/lib/intake-direct-link";
import { intakeCatalog } from "@/lib/kinds";
import { scheduleNewMaWebhookFromRow } from "@/lib/newMaWebhook";
import { listSubmissions, storeHealth } from "@/lib/store";
import { storeUnavailableResponse } from "@/lib/store-unavailable";

// Direct link, no session. Writes stay on the shop-admin session. noindex, not in nav.
export async function GET() {
  let submissions;
  try {
    submissions = await listSubmissions();
  } catch (error) {
    return withIntakeDirectLinkHeaders(storeUnavailableResponse(error));
  }
  return intakeDirectJson({
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
    return withIntakeDirectLinkHeaders(NextResponse.json({ submission }));
  } catch (error) {
    const status = (error as { status?: number }).status ?? 400;
    return withIntakeDirectLinkHeaders(
      NextResponse.json(
        { error: error instanceof Error ? error.message : "Chưa lưu được, thử lại nha." },
        { status },
      ),
    );
  }
}
