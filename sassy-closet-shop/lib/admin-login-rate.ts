/**
 * Basic per-instance login throttle. Vercel may run more than one instance,
 * so this is not a global lock — failed attempts also wait LOGIN_FAILURE_DELAY_MS.
 */

export const LOGIN_FAILURE_DELAY_MS = 800;

const WINDOW_MS = 10 * 60 * 1000;
const LOCK_MS = 10 * 60 * 1000;
const MAX_FAILURES = 5;

type Bucket = {
  failures: number;
  windowStart: number;
  lockedUntil: number;
};

const buckets = new Map<string, Bucket>();

export function resetLoginBuckets(): void {
  buckets.clear();
}

export function clientAddress(request: Request): string {
  const forwarded = request.headers.get("x-forwarded-for");
  if (forwarded) {
    const first = forwarded.split(",")[0]?.trim() ?? "";
    if (first) {
      return first.slice(0, 80);
    }
  }
  const real = request.headers.get("x-real-ip")?.trim() ?? "";
  if (real) {
    return real.slice(0, 80);
  }
  return "unknown";
}

function prune(now: number): void {
  if (buckets.size < 500) {
    return;
  }
  for (const [ip, bucket] of buckets) {
    const expired = bucket.lockedUntil <= now && now - bucket.windowStart > WINDOW_MS;
    if (expired) {
      buckets.delete(ip);
    }
  }
}

export function loginAttemptAllowed(
  ip: string,
  now: number,
): { ok: true } | { ok: false; retryAfterSeconds: number } {
  prune(now);
  const bucket = buckets.get(ip);
  if (!bucket) {
    return { ok: true };
  }
  if (bucket.lockedUntil > now) {
    return {
      ok: false,
      retryAfterSeconds: Math.max(1, Math.ceil((bucket.lockedUntil - now) / 1000)),
    };
  }
  if (now - bucket.windowStart > WINDOW_MS) {
    buckets.delete(ip);
  }
  return { ok: true };
}

export function recordLoginFailure(ip: string, now: number): void {
  const existing = buckets.get(ip);
  if (!existing || now - existing.windowStart > WINDOW_MS) {
    buckets.set(ip, { failures: 1, windowStart: now, lockedUntil: 0 });
    return;
  }
  existing.failures += 1;
  if (existing.failures >= MAX_FAILURES) {
    existing.lockedUntil = now + LOCK_MS;
  }
}

export function recordLoginSuccess(ip: string): void {
  buckets.delete(ip);
}

export function waitForLoginFailure(): Promise<void> {
  return new Promise((resolve) => {
    setTimeout(resolve, LOGIN_FAILURE_DELAY_MS);
  });
}
