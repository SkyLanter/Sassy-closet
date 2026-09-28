import { IntakeApp } from "@/components/IntakeApp";
import { newMaWebhookUrlConfigured } from "@/lib/newMaWebhook";
import { getFx } from "@/lib/store";

export const dynamic = "force-dynamic";

export default async function HomePage() {
  const fx = await getFx();
  return (
    <IntakeApp
      initialFxRate={fx.usd_cny}
      initialFxLabel={fx.label}
      newMaWebhookOn={newMaWebhookUrlConfigured()}
    />
  );
}
