import { ImageResponse } from "next/og";

export const size = { width: 180, height: 180 };
export const contentType = "image/png";

export default function AppleIcon() {
  return new ImageResponse(
    (
      <div
        style={{
          width: "100%",
          height: "100%",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          background: "#F6F1EB",
          borderRadius: 40,
        }}
      >
        <div
          style={{
            width: 148,
            height: 148,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            borderRadius: 28,
            border: "3px solid #B08968",
            color: "#8C6A4E",
            fontSize: 64,
            fontFamily: "Georgia, serif",
            letterSpacing: "0.04em",
          }}
        >
          SC
        </div>
      </div>
    ),
    { ...size },
  );
}
