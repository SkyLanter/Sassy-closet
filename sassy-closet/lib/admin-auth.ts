const ADMIN_PASSWORD = "ADMIN_PASSWORD";
const ADMIN_SESSION_SECRET = "ADMIN_SESSION_SECRET";

/** Host-only session cookie for shop tools on the intake site. */
export const ADMIN_SESSION_COOKIE = "sc_admin";

export const ADMIN_SESSION_MAX_AGE_SECONDS = 60 * 60 * 24 * 30;

const SESSION_VERSION = 1;

function readTrimmed(name: typeof ADMIN_PASSWORD | typeof ADMIN_SESSION_SECRET): string {
  return process.env[name]?.trim() ?? "";
}

/** Both must be non-empty. Missing either locks shop tools. There is no default password. */
export function adminAuthConfigured(): boolean {
  return readTrimmed(ADMIN_PASSWORD).length > 0 && readTrimmed(ADMIN_SESSION_SECRET).length > 0;
}

function bytesToBase64Url(bytes: Uint8Array): string {
  let binary = "";
  for (const byte of bytes) {
    binary += String.fromCharCode(byte);
  }
  return btoa(binary).replaceAll("+", "-").replaceAll("/", "_").replace(/=+$/u, "");
}

function base64UrlToBytes(value: string): Uint8Array | null {
  if (!/^[A-Za-z0-9_-]+$/u.test(value)) {
    return null;
  }
  const padded = value + "=".repeat((4 - (value.length % 4)) % 4);
  const binary = atob(padded.replaceAll("-", "+").replaceAll("_", "/"));
  const bytes = new Uint8Array(binary.length);
  for (let index = 0; index < binary.length; index += 1) {
    bytes[index] = binary.charCodeAt(index);
  }
  return bytes;
}

async function sha256(value: string): Promise<Uint8Array> {
  const digest = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(value));
  return new Uint8Array(digest);
}

function constantTimeEqualBytes(left: Uint8Array, right: Uint8Array): boolean {
  if (left.length !== right.length) {
    return false;
  }
  let diff = 0;
  for (let index = 0; index < left.length; index += 1) {
    diff |= (left[index] ?? 0) ^ (right[index] ?? 0);
  }
  return diff === 0;
}

/** Hash both sides, then compare the digests, including when the raw strings differ in length. */
export async function constantTimeEqual(left: string, right: string): Promise<boolean> {
  const leftDigest = await sha256(left);
  const rightDigest = await sha256(right);
  return constantTimeEqualBytes(leftDigest, rightDigest);
}

async function hmacSha256(keyBytes: Uint8Array, data: string): Promise<Uint8Array> {
  const keyCopy = new Uint8Array(keyBytes);
  const key = await crypto.subtle.importKey("raw", keyCopy, { name: "HMAC", hash: "SHA-256" }, false, ["sign"]);
  const signature = await crypto.subtle.sign("HMAC", key, new TextEncoder().encode(data));
  return new Uint8Array(signature);
}

/**
 * MAC key is HMAC-SHA256(ADMIN_SESSION_SECRET, ADMIN_PASSWORD).
 * Changing either variable signs every browser out.
 */
async function macKey(): Promise<Uint8Array | null> {
  const secret = readTrimmed(ADMIN_SESSION_SECRET);
  const password = readTrimmed(ADMIN_PASSWORD);
  if (!secret || !password) {
    return null;
  }
  return hmacSha256(new TextEncoder().encode(secret), password);
}

export async function passwordMatches(submitted: string): Promise<boolean> {
  const expected = readTrimmed(ADMIN_PASSWORD);
  if (!adminAuthConfigured() || !expected) {
    return false;
  }
  return constantTimeEqual(submitted, expected);
}

export async function createAdminSessionToken(now = Date.now()): Promise<string | null> {
  const key = await macKey();
  if (!key) {
    return null;
  }
  const body = bytesToBase64Url(
    new TextEncoder().encode(JSON.stringify({ v: SESSION_VERSION, exp: now + ADMIN_SESSION_MAX_AGE_SECONDS * 1000 })),
  );
  const mac = bytesToBase64Url(await hmacSha256(key, body));
  return `${body}.${mac}`;
}

export async function verifyAdminSession(token: string, now = Date.now()): Promise<boolean> {
  const key = await macKey();
  if (!key || !token) {
    return false;
  }
  const dot = token.indexOf(".");
  if (dot <= 0 || dot !== token.lastIndexOf(".")) {
    return false;
  }
  const body = token.slice(0, dot);
  const mac = token.slice(dot + 1);
  const expected = bytesToBase64Url(await hmacSha256(key, body));
  if (!(await constantTimeEqual(mac, expected))) {
    return false;
  }
  const raw = base64UrlToBytes(body);
  if (!raw) {
    return false;
  }
  try {
    const parsed: unknown = JSON.parse(new TextDecoder().decode(raw));
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

export function readCookie(header: string | null, name: string): string {
  if (!header) {
    return "";
  }
  for (const part of header.split(";")) {
    const trimmed = part.trim();
    const eq = trimmed.indexOf("=");
    if (eq <= 0) {
      continue;
    }
    if (trimmed.slice(0, eq) !== name) {
      continue;
    }
    return decodeURIComponent(trimmed.slice(eq + 1));
  }
  return "";
}

export async function requestHasAdminSession(request: Request): Promise<boolean> {
  return verifyAdminSession(readCookie(request.headers.get("cookie"), ADMIN_SESSION_COOKIE));
}
