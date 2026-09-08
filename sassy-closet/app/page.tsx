import { IntakeApp } from "@/components/IntakeApp";
import { getFx } from "@/lib/store";
import { withSharedStore } from "@/lib/with-shared";

export const dynamic = "force-dynamic";

export default async function HomePage() {
  const fx = await withSharedStore(() => getFx(), "read");
  return <IntakeApp initialFxRate={fx.usd_cny} initialFxLabel={fx.label} />;
}
