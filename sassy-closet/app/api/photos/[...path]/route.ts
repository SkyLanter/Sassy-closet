import { NextResponse } from "next/server";
import { readPhoto } from "@/lib/store";
import { withSharedStore } from "@/lib/with-shared";

export async function GET(
  _request: Request,
  context: { params: Promise<{ path: string[] }> },
) {
  const { path } = await context.params;
  const photo = await withSharedStore(() => readPhoto(path.join("/")), "read");
  if (!photo) {
    return NextResponse.json({ error: "Không thấy ảnh." }, { status: 404 });
  }
  return new NextResponse(new Uint8Array(photo.bytes), {
    headers: { "content-type": photo.type },
  });
}
