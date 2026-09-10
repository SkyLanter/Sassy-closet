import { NextResponse } from "next/server";
import { INTAKE_PHOTO_CACHE_CONTROL } from "@/lib/store-backend";
import { readPhoto } from "@/lib/store";

export async function GET(
  _request: Request,
  context: { params: Promise<{ path: string[] }> },
) {
  const { path } = await context.params;
  const photo = await readPhoto(path.join("/"));
  if (!photo) {
    return NextResponse.json({ error: "Không thấy ảnh." }, { status: 404 });
  }
  return new NextResponse(new Uint8Array(photo.bytes), {
    headers: {
      "content-type": photo.type,
      "cache-control": INTAKE_PHOTO_CACHE_CONTROL,
    },
  });
}
