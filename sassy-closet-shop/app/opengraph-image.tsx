import { shareCard } from "@/lib/og-card";
import { FULFILL_LINE_SHORT } from "@/lib/trust-copy";

export const alt = "Sassy Closet lookbook";
export const size = { width: 1200, height: 630 };
export const contentType = "image/png";

export default function OpengraphImage() {
  return shareCard({
    kicker: "Sassy Closet",
    title: "Sassy Closet",
    subtitle: FULFILL_LINE_SHORT,
    footer: "Message on Messenger",
  });
}
