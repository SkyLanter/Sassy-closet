import { IntakeApp } from "@/components/IntakeApp";
import { newMaWebhookConfigured } from "@/lib/newMaWebhook";
import { getHomeFx } from "@/lib/home-fx";

export const dynamic = "force-dynamic";

export default async function HomePage() {
  const fx = await getHomeFx();
  return (
    <IntakeApp
      initialFxRate={fx.usd_cny}
      initialFxLabel={fx.label}
      newMaWebhookOn={newMaWebhookConfigured()}
    />
  );
}
