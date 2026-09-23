import { ImageResponse } from "next/og";

export const SHARE_CARD_SIZE = { width: 1200, height: 630 } as const;

export function shareCard(opts: {
  kicker: string;
  title: string;
  subtitle: string;
  footer: string;
}): ImageResponse {
  return new ImageResponse(
    (
      <div
        style={{
          width: "100%",
          height: "100%",
          display: "flex",
          flexDirection: "column",
          justifyContent: "space-between",
          background: "linear-gradient(160deg, #f3eee8 0%, #ffffff 55%, #efe6dc 100%)",
          padding: "72px 80px",
          color: "#111111",
        }}
      >
        <div style={{ display: "flex", flexDirection: "column", gap: 18 }}>
          <div
            style={{
              display: "flex",
              fontSize: 22,
              letterSpacing: "0.42em",
              textTransform: "uppercase",
              color: "#8c6a4e",
              fontWeight: 600,
            }}
          >
            {opts.kicker}
          </div>
          <div
            style={{
              display: "flex",
              fontSize: 92,
              lineHeight: 0.95,
              fontFamily: "Georgia, 'Times New Roman', serif",
              fontWeight: 600,
            }}
          >
            {opts.title}
          </div>
          <div
            style={{
              display: "flex",
              fontSize: 36,
              color: "#6b6b6b",
              letterSpacing: "0.04em",
            }}
          >
            {opts.subtitle}
          </div>
        </div>
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "flex-end",
            borderTop: "1px solid #d8c4b0",
            paddingTop: 28,
            fontSize: 24,
            color: "#8c6a4e",
            letterSpacing: "0.08em",
          }}
        >
          <span>{opts.footer}</span>
          <span>Message</span>
        </div>
      </div>
    ),
    { width: SHARE_CARD_SIZE.width, height: SHARE_CARD_SIZE.height },
  );
}
