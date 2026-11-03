import { intakeDirectJson } from "@/lib/intake-direct-link";
import { intakeHealthReport } from "@/lib/intake-health";

export const dynamic = "force-dynamic";

/** Open by link. Reading only: blob, local disk, or ephemeral tmp. */
export function GET() {
  return intakeDirectJson(intakeHealthReport());
}
