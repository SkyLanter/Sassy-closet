import { NextResponse } from "next/server";
import { saveFromForm } from "@/lib/form-save";
import { getSubmission } from "@/lib/store";
import { withSharedStore } from "@/lib/with-shared";

export async function GET(
  _request: Request,
  context: { params: Promise<{ ma: string }> },
) {
  const { ma } = await context.params;
  const submission = await withSharedStore(() => getSubmission(ma), "read");
  if (!submission) {
    return NextResponse.json({ error: "Không tìm thấy mã này 🥺" }, { status: 404 });
  }
  return NextResponse.json({
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
    const submission = await withSharedStore(() => saveFromForm(form, ma), "write");
    return NextResponse.json({ submission });
  } catch (error) {
    const status = (error as { status?: number }).status ?? 400;
    return NextResponse.json(
      { error: error instanceof Error ? error.message : "Chưa lưu được, thử lại nha." },
      { status },
    );
  }
}
