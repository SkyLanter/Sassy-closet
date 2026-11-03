import { blobConfigured, storageMode, type StorageMode } from "./store-backend";

export type IntakeReading = "blob" | "local" | "ephemeral";

export type IntakeHealthReport = {
  ok: true;
  reading: IntakeReading;
  blob: {
    configured: boolean;
  };
};

/**
 * Intake has no seed catalog. Blob is detectable from env presence only.
 * This report has no token, path, cost, or shop link.
 */
export function intakeHealthReport(): IntakeHealthReport {
  return {
    ok: true,
    reading: readingFor(storageMode()),
    blob: { configured: blobConfigured() },
  };
}

function readingFor(mode: StorageMode): IntakeReading {
  switch (mode) {
    case "durable":
      return "blob";
    case "local":
      return "local";
    case "ephemeral":
      return "ephemeral";
    default: {
      const neverMode: never = mode;
      throw new Error(`unknown storage mode ${String(neverMode)}`);
    }
  }
}
