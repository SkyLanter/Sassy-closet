/** Production Server Action / RSC failures become React #441 with no useful message. */

export function isOpaqueRscError(error: unknown): boolean {
  const message = error instanceof Error ? error.message : String(error ?? "");
  return /Server Components render|#441|react\.dev\/errors\/441|omitted in production builds|digest property is included/i.test(
    message,
  );
}

export function opaquePostSaveMessage(): string {
  return "The catalog may already be saved. Open Catalog and look for the new mã — do not Save again until you check.";
}

export function publicSaveErrorMessage(error: unknown, fallback: string): string {
  if (isOpaqueRscError(error)) {
    return fallback;
  }
  if (error instanceof Error && error.message.trim()) {
    return error.message;
  }
  return fallback;
}
