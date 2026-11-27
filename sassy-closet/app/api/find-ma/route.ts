import { NextResponse } from "next/server";
import { findByPhotoHash, hashBytes } from "@/lib/store";
import { storeUnavailableResponse } from "@/lib/store-unavailable";

function noPhotoResponse(): NextResponse {
  return NextResponse.json(
    { error: "Chưa nhận được ảnh.", error_en: "Send one photo to search." },
    { status: 400 },
  );
}

export async function POST(request: Request) {
  // A direct link answers anyone. A JSON or empty body is not a photo form, and
  // `request.formData()` throws on it before the route can answer, so keep that
  // in the same 400 the missing-photo branch already returns.
  let form: FormData;
  try {
    form = await request.formData();
  } catch {
    return noPhotoResponse();
  }
  const photo = form.get("photo");
  if (!(photo instanceof File)) {
    return noPhotoResponse();
  }
  const bytes = Buffer.from(await photo.arrayBuffer());
  let rows;
  try {
    rows = await findByPhotoHash(hashBytes(bytes));
  } catch (error) {
    return storeUnavailableResponse(error);
  }
  const matches = rows.map((row) => ({
    ma: row.ma,
    kind: row.kind,
    color: row.color,
  }));
  return NextResponse.json({ matches });
}
