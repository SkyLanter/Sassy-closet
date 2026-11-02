import { NextResponse } from "next/server";
import { saveFromForm } from "@/lib/form-save";
import { intakeDirectJson, withIntakeDirectLinkHeaders } from "@/lib/intake-direct-link";
import { intakeCatalog } from "@/lib/kinds";
import { scheduleNewMaWebhookFromRow } from "@/lib/newMaWebhook";
import { listSubmissions, storeHealth } from "@/lib/store";
import { intakeWriteErrorResponse, storeUnavailableResponse } from "@/lib/store-unavailable";

// Direct link, no session, reads and writes. noindex, not in nav.
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
  let form: FormData;
  try {
    form = await request.formData();
  } catch {
    return withIntakeDirectLinkHeaders(
      NextResponse.json({ error: "Chưa lưu được, thử lại nha." }, { status: 400 }),
    );
  }
  try {
    const submission = await saveFromForm(form);
    scheduleNewMaWebhookFromRow("create", submission);
    return withIntakeDirectLinkHeaders(NextResponse.json({ submission }));
  } catch (error) {
    return withIntakeDirectLinkHeaders(intakeWriteErrorResponse(error));
  }
}
