import { IntakeApp } from "@/components/IntakeApp";
import { getFx } from "@/lib/store";

export const dynamic = "force-dynamic";

export default function HomePage() {
  const fx = getFx();
  return <IntakeApp initialFxRate={fx.usd_cny} initialFxLabel={fx.label} />;
}
