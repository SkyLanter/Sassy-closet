import { createHash, createHmac, timingSafeEqual } from "node:crypto";

/**
 * Admin session cookie. httpOnly + Secure + SameSite=Lax, about 30 days.
 * The value is base64url(JSON {v, exp}) + "." + base64url(HMAC).
 * It never contains the password.
 * No Domain attribute: the cookie is host-only, so both
 * sassycloset.vercel.app and sassy-closet-shop.vercel.app can sign in.
 * A session on one host is not sent to the other.
 */
export const ADMIN_SESSION_COOKIE = "sc_admin";

export const ADMIN_SESSION_MAX_AGE_SECONDS = 60 * 60 * 24 * 30;

const SESSION_VERSION = 1;

function readTrimmed(name: "ADMIN_PASSWORD" | "ADMIN_SESSION_SECRET"): string {
  return process.env[name]?.trim() ?? "";
}

/** Both must be non-empty. Missing either locks the desk (fail closed). */
export function adminAuthConfigured(): boolean {
  return readTrimmed("ADMIN_PASSWORD").length > 0 && readTrimmed("ADMIN_SESSION_SECRET").length > 0;
}

/**
 * MAC key is HMAC-SHA256(ADMIN_SESSION_SECRET, ADMIN_PASSWORD).
 * The secret is not derived from the password alone, so a stolen password
 * cannot forge a cookie. Changing either variable signs every browser out.
 */
function macKey(): Buffer | null {
  const secret = readTrimmed("ADMIN_SESSION_SECRET");
  const password = readTrimmed("ADMIN_PASSWORD");
  if (!secret || !password) {
    return null;
  }
  return createHmac("sha256", secret).update(password, "utf8").digest();
}

/**
 * Hash both sides, then compare the digests.
 * PR #60's receiver skipped timingSafeEqual when the buffers differed in
 * length (`length ===` && compare). Equal-length SHA-256 digests always
 * run the compare, including when the raw strings differ in length.
 */
export function constantTimeEqual(left: string, right: string): boolean {
  const leftDigest = createHash("sha256").update(left, "utf8").digest();
  const rightDigest = createHash("sha256").update(right, "utf8").digest();
  return timingSafeEqual(leftDigest, rightDigest);
}

export function passwordMatches(submitted: string): boolean {
  const expected = readTrimmed("ADMIN_PASSWORD");
  if (!adminAuthConfigured() || !expected) {
    return false;
  }
  return constantTimeEqual(submitted, expected);
}

export function createAdminSessionToken(now = Date.now()): string | null {
  const key = macKey();
  if (!key) {
    return null;
  }
  const body = Buffer.from(
    JSON.stringify({ v: SESSION_VERSION, exp: now + ADMIN_SESSION_MAX_AGE_SECONDS * 1000 }),
  ).toString("base64url");
  const mac = createHmac("sha256", key).update(body).digest("base64url");
  return `${body}.${mac}`;
}

export function verifyAdminSession(token: string, now = Date.now()): boolean {
  const key = macKey();
  if (!key || !token) {
    return false;
  }
  const dot = token.indexOf(".");
  if (dot <= 0 || dot !== token.lastIndexOf(".")) {
    return false;
  }
  const body = token.slice(0, dot);
  const mac = token.slice(dot + 1);
  const expected = createHmac("sha256", key).update(body).digest("base64url");
  if (!constantTimeEqual(mac, expected)) {
    return false;
  }
  try {
    const parsed: unknown = JSON.parse(Buffer.from(body, "base64url").toString("utf8"));
    if (!parsed || typeof parsed !== "object") {
      return false;
    }
    const row = parsed as { v?: unknown; exp?: unknown };
    if (row.v !== SESSION_VERSION || typeof row.exp !== "number" || !Number.isFinite(row.exp)) {
      return false;
    }
    return row.exp > now;
  } catch {
    return false;
  }
}

export function adminSessionCookie(token: string): {
  name: string;
  value: string;
  httpOnly: true;
  secure: true;
  sameSite: "lax";
  path: string;
  maxAge: number;
} {
  return {
    name: ADMIN_SESSION_COOKIE,
    value: token,
    httpOnly: true,
    secure: true,
    sameSite: "lax",
    path: "/",
    maxAge: ADMIN_SESSION_MAX_AGE_SECONDS,
  };
}

export function clearedAdminSessionCookie(): {
  name: string;
  value: string;
  httpOnly: true;
  secure: true;
  sameSite: "lax";
  path: string;
  maxAge: number;
} {
  return {
    ...adminSessionCookie(""),
    maxAge: 0,
  };
}
