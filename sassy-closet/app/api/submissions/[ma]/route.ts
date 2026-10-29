import { NextResponse } from "next/server";
import { saveFromForm } from "@/lib/form-save";
import { intakeDirectJson, withIntakeDirectLinkHeaders } from "@/lib/intake-direct-link";
import { normalizeMa } from "@/lib/mint";
import { scheduleNewMaWebhookFromRow } from "@/lib/newMaWebhook";
import { getSubmission } from "@/lib/store";
import { storeUnavailableResponse } from "@/lib/store-unavailable";

export async function GET(
  _request: Request,
  context: { params: Promise<{ ma: string }> },
) {
  const { ma } = await context.params;
  let submission;
  try {
    submission = await getSubmission(ma);
  } catch (error) {
    return withIntakeDirectLinkHeaders(storeUnavailableResponse(error));
  }
  if (!submission) {
    return intakeDirectJson({ error: "Không tìm thấy mã này 🥺" }, 404);
  }
  return intakeDirectJson({
    ma: submission.ma,
    caption_vi: submission.caption_vi,
    submission,
  });
}

export async function PATCH(
  request: Request,
  context: { params: Promise<{ ma: string }> },
) {
  const { ma } = await context.params;
  try {
    const form = await request.formData();
    const submission = await saveFromForm(form, ma);
    const urlMa = normalizeMa(ma);
    const savedMa = normalizeMa(submission.ma);
    scheduleNewMaWebhookFromRow(
      "update",
      submission,
      urlMa !== savedMa ? urlMa : undefined,
    );
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
