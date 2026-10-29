import { constantTimeEqual } from "@/lib/admin-auth";

/** Vercel intake project only. Never NEXT_PUBLIC_, never committed. */
export const INTAKE_PIPELINE_SECRET_ENV = "INTAKE_PIPELINE_SECRET";

/** Below this length the bearer is ignored and the route stays 401. */
export const INTAKE_PIPELINE_SECRET_MIN_LENGTH = 24;

/** Above this length the bearer is ignored, so a huge header is not hashed. */
export const INTAKE_PIPELINE_SECRET_MAX_LENGTH = 256;

/**
 * Printable ASCII, no spaces or controls, so the value is one header token.
 * `openssl rand -hex 32` fits.
 */
export function pipelineSecretUsable(value: string): boolean {
  if (value.length < INTAKE_PIPELINE_SECRET_MIN_LENGTH) return false;
  if (value.length > INTAKE_PIPELINE_SECRET_MAX_LENGTH) return false;
  for (let index = 0; index < value.length; index += 1) {
    const code = value.charCodeAt(index);
    if (code < 0x21 || code > 0x7e) return false;
  }
  return true;
}

export function readPipelineSecret(): string {
  return process.env[INTAKE_PIPELINE_SECRET_ENV]?.trim() ?? "";
}

/** `Authorization: Bearer <token>` only. Query strings and other headers are ignored. */
export function readPipelineBearer(request: Request): string {
  const raw = (request.headers.get("authorization") ?? "").trim();
  const match = /^Bearer\s+(\S+)$/iu.exec(raw);
  return match?.[1] ?? "";
}

/**
 * True only for a configured secret and a matching bearer.
 * Unset, short, or oversized secrets fail closed.
 */
export async function pipelineBearerOk(request: Request): Promise<boolean> {
  const expected = readPipelineSecret();
  if (!pipelineSecretUsable(expected)) return false;
  const provided = readPipelineBearer(request);
  if (!pipelineSecretUsable(provided)) return false;
  return constantTimeEqual(provided, expected);
}
