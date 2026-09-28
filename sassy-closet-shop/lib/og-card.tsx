import { readFile } from "node:fs/promises";
import path from "node:path";
import { ImageResponse } from "next/og";
import type { ShareCardModel } from "@/lib/share-card";
import type { SharePhoto } from "@/lib/share-photo";

export const SHARE_CARD_SIZE = { width: 1200, height: 630 } as const;

const PAPER = "#fdece6";
const INK = "#111111";
const GOLD = "#b08968";
const GOLD_DEEP = "#8c6a4e";
const PHOTO_WIDTH = 472;

type OgFont = {
  name: string;
  data: Buffer;
  weight: 400 | 500 | 600;
  style: "normal";
};

let fontsPromise: Promise<OgFont[]> | null = null;

function loadOgFonts(): Promise<OgFont[]> {
  if (!fontsPromise) {
    const dir = path.join(process.cwd(), "assets/og-fonts");
    fontsPromise = Promise.all([
      readFile(path.join(dir, "CormorantGaramond-SemiBold.ttf")),
      readFile(path.join(dir, "BeVietnamPro-Regular.ttf")),
      readFile(path.join(dir, "BeVietnamPro-Medium.ttf")),
    ])
      .then(([cormorant, regular, medium]) => [
        { name: "Cormorant Garamond", data: cormorant, weight: 600 as const, style: "normal" as const },
        { name: "Be Vietnam Pro", data: regular, weight: 400 as const, style: "normal" as const },
        { name: "Be Vietnam Pro", data: medium, weight: 500 as const, style: "normal" as const },
      ])
      .catch((error: unknown) => {
        fontsPromise = null;
        throw error;
      });
  }
  return fontsPromise;
}

function titleSize(title: string, withPhoto: boolean): number {
  if (title.length > 46) {
    return withPhoto ? 40 : 48;
  }
  if (title.length > 28) {
    return withPhoto ? 52 : 64;
  }
  if (title.length > 18) {
    return withPhoto ? 60 : 72;
  }
  return withPhoto ? 72 : 88;
}

function photoDataUrl(photo: SharePhoto): string {
  return `data:${photo.mime};base64,${Buffer.from(photo.data).toString("base64")}`;
}

function CardCopy({ model, withPhoto }: { model: ShareCardModel; withPhoto: boolean }) {
  const textWidth = withPhoto ? 600 : 1040;
  return (
    <div
      style={{
        display: "flex",
        flexDirection: "column",
        justifyContent: "space-between",
        width: withPhoto ? 1200 - PHOTO_WIDTH - 8 : 1200,
        height: "100%",
        padding: withPhoto ? "52px 56px 44px" : "64px 80px",
        background: PAPER,
      }}
    >
      <div style={{ display: "flex", flexDirection: "column" }}>
        <div
          style={{
            display: "flex",
            fontFamily: "Be Vietnam Pro",
            fontWeight: 500,
            fontSize: 18,
            letterSpacing: "0.32em",
            color: GOLD_DEEP,
          }}
        >
          {model.kicker}
        </div>
        <div
          style={{
            display: "flex",
            width: 64,
            height: 2,
            marginTop: 18,
            background: GOLD,
          }}
        />
        {model.eyebrow ? (
          <div
            style={{
              display: "flex",
              marginTop: 28,
              fontFamily: "Be Vietnam Pro",
              fontWeight: 500,
              fontSize: 26,
              letterSpacing: "0.16em",
              color: GOLD,
            }}
          >
            {model.eyebrow}
          </div>
        ) : null}
        <div
          style={{
            display: "flex",
            width: textWidth,
            marginTop: model.eyebrow ? 12 : 28,
            fontFamily: "Cormorant Garamond",
            fontWeight: 600,
            fontSize: titleSize(model.title, withPhoto),
            lineHeight: 1.02,
            color: INK,
          }}
        >
          {model.title}
        </div>
        {model.detail ? (
          <div
            style={{
              display: "flex",
              marginTop: 22,
              fontFamily: "Be Vietnam Pro",
              fontWeight: 500,
              fontSize: 34,
              color: INK,
            }}
          >
            {model.detail}
          </div>
        ) : null}
      </div>
      <div
        style={{
          display: "flex",
          borderTop: `1px solid ${GOLD}`,
          paddingTop: 22,
          fontFamily: "Be Vietnam Pro",
          fontWeight: 400,
          fontSize: 22,
          letterSpacing: "0.04em",
          color: GOLD_DEEP,
        }}
      >
        {model.cta}
      </div>
    </div>
  );
}

async function paintShareCard(model: ShareCardModel): Promise<ImageResponse> {
  const fonts = await loadOgFonts();
  const photo = model.photo;
  return new ImageResponse(
    (
      <div
        style={{
          width: "100%",
          height: "100%",
          display: "flex",
          flexDirection: "row",
          background: PAPER,
        }}
      >
        {photo ? (
          <div style={{ display: "flex", width: PHOTO_WIDTH, height: SHARE_CARD_SIZE.height }}>
            {/* Satori paints <img>; next/image is not available in ImageResponse. */}
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img
              src={photoDataUrl(photo)}
              width={PHOTO_WIDTH}
              height={SHARE_CARD_SIZE.height}
              alt=""
              style={{
                width: PHOTO_WIDTH,
                height: SHARE_CARD_SIZE.height,
                objectFit: "cover",
                objectPosition: "top",
              }}
            />
          </div>
        ) : null}
        {photo ? <div style={{ display: "flex", width: 8, height: "100%", background: GOLD }} /> : null}
        <CardCopy model={model} withPhoto={Boolean(photo)} />
      </div>
    ),
    {
      width: SHARE_CARD_SIZE.width,
      height: SHARE_CARD_SIZE.height,
      fonts,
    },
  );
}

const BLUSH_PNG = Buffer.from(
  "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg==",
  "base64",
);

export async function renderShareCard(model: ShareCardModel): Promise<Response> {
  try {
    return await paintShareCard(model);
  } catch (error) {
    console.error("share card paint failed", error instanceof Error ? error.message : "error");
    if (model.photo) {
      try {
        return await paintShareCard({ ...model, photo: null });
      } catch (fallbackError) {
        console.error(
          "share card text fallback failed",
          fallbackError instanceof Error ? fallbackError.message : "error",
        );
      }
    }
    return new Response(BLUSH_PNG, {
      status: 200,
      headers: { "content-type": "image/png", "cache-control": "no-store" },
    });
  }
}
