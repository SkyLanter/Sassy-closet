import { NextResponse } from "next/server";
import { saveFromForm } from "@/lib/form-save";
import { intakeDirectJson, withIntakeDirectLinkHeaders } from "@/lib/intake-direct-link";
import { normalizeMa } from "@/lib/mint";
import { scheduleNewMaWebhookFromRow } from "@/lib/newMaWebhook";
import { getSubmission } from "@/lib/store";
import { intakeWriteErrorResponse, storeUnavailableResponse } from "@/lib/store-unavailable";

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
  let form: FormData;
  try {
    form = await request.formData();
  } catch {
    return withIntakeDirectLinkHeaders(
      NextResponse.json({ error: "Chưa lưu được, thử lại nha." }, { status: 400 }),
    );
  }
  try {
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
    return withIntakeDirectLinkHeaders(intakeWriteErrorResponse(error));
  }
}
